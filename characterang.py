#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
motion_rig.py — 글씨랑 캐릭터 모션 엔진(무료·자동화).

원리: 스틱 캐릭터의 '정체성'은 머리(얼굴+머리카락)에 있고 팔다리는 얇은 선이다.
 → 원본 컷아웃에서 **머리 부품**을 잘라 그대로 쓰고(원본 얼굴 유지),
   **팔·다리·손·발**은 관절(anim_poses)에 맞춰 선/도형으로 그린다.
 → 어떤 포즈도 즉시 생성, 시간축 보간으로 모션 완성. DB의 어떤 캐릭터든 재사용.

DB:
  anim_characters(char_key, base_image, ...)  — 캐릭터 원본
  anim_char_parts(char_key, part, file_path, ax, ay)  — 잘라낸 부품(머리 등)+부착점
  anim_poses(pose_name, joints_json)          — 포즈=관절좌표
  anim_sequences(seq_name, beats_json)        — 모션=포즈 시퀀스

API:
  extract_head(char_key, base_png)   — 머리 부품 추출→저장+DB등록
  render(char_key, joints, H=520)    — 포즈(관절)로 캐릭터 1장 렌더(RGBA)
  render_pose_name(char_key, name)   — 등록된 포즈명으로 렌더
검증:  python motion_rig.py           # 여러 포즈 시트
"""
import os, sys, json, math, sqlite3
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")
INK = (28, 24, 22, 255)
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass


def _con():
    c = sqlite3.connect(DB); return c


def ensure_tables():
    c = _con()
    c.execute("""CREATE TABLE IF NOT EXISTS anim_char_parts(
        id INTEGER PRIMARY KEY, char_key TEXT, part TEXT, file_path TEXT,
        ax REAL, ay REAL, updated_at TEXT, UNIQUE(char_key,part))""")
    c.commit(); c.close()


# ---------- 머리 부품 추출(깨끗한 머리 = 표정 지움) ----------
def _clean_face(head_rgba):
    """머리 내부의 baked 눈코입(어두운 마크)을 지워 깨끗한 흰 얼굴로. 주황머리·외곽선은 보존."""
    from scipy import ndimage
    arr = np.array(head_rgba).astype(np.int16)
    r, g, b, al = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
    solid = al > 60
    # 내부(외곽선 제외): 실루엣을 침식
    inner = ndimage.binary_erosion(solid, iterations=max(3, head_rgba.width // 22))
    dark = (r < 130) & (g < 130) & (b < 130)         # 눈·입(어두움)
    orange = (r > 150) & (g > 70) & (g < 190) & (b < 130)   # 머리카락(보존)
    remove = inner & dark & (~orange)
    out = np.array(head_rgba)
    out[remove] = [252, 250, 247, 255]               # 흰 얼굴로 덮음
    return Image.fromarray(out, "RGBA")


def extract_head(char_key, base_png, head_frac=0.34):
    """원본 상단(머리+머리카락)을 잘라 **깨끗한 머리**(표정 제거)로 저장. 얼굴은 render가 그림."""
    ensure_tables()
    im = Image.open(base_png).convert("RGBA")
    a = np.array(im)[:, :, 3]
    h, w = a.shape
    cut = int(h * head_frac)
    head = im.crop((0, 0, w, cut))
    ha = np.array(head)[:, :, 3]
    xs = np.where(ha.sum(axis=0) > 0)[0]
    if len(xs):
        head = head.crop((max(0, xs[0]-4), 0, min(w, xs[-1]+4), cut))
    try:
        head = _clean_face(head)
    except Exception as e:
        print("  (표정 제거 스킵:", str(e)[:40], ")")
    outdir = os.path.join(ROOT, "assets", "graphics", "parts")
    os.makedirs(outdir, exist_ok=True)
    # 원본(AI 얼굴 살림) = 정면용, 깨끗(얼굴 제거) = 옆모습용
    front = im.crop((0, 0, w, cut))
    fa = np.array(front)[:, :, 3]; fxs = np.where(fa.sum(axis=0) > 0)[0]
    if len(fxs): front = front.crop((max(0, fxs[0]-4), 0, min(w, fxs[-1]+4), cut))
    of = os.path.join(outdir, f"{char_key}_head_front.png"); front.save(of)
    oc = os.path.join(outdir, f"{char_key}_head_clean.png"); head.save(oc)
    c = _con()
    c.execute("DELETE FROM anim_char_parts WHERE char_key=? AND part IN ('head_front','head_clean')", (char_key,))
    for part, path in [("head_front", of), ("head_clean", oc)]:
        fp = os.path.relpath(path, ROOT).replace(os.sep, "/")
        c.execute("INSERT INTO anim_char_parts(char_key,part,file_path,ax,ay,updated_at) VALUES (?,?,?,?,?,datetime('now'))",
                  (char_key, part, fp, head.width/2, head.height-2))
    c.commit(); c.close()
    print(f"  head_front(AI얼굴) + head_clean(옆모습용) 저장")
    return of


# ---------- 진짜 옆모습(프로필) 머리 그리기: 코·눈 하나·귀 하나 ----------
WHITE = (252, 250, 247, 255)
ORANGE = (232, 126, 58, 255)
def draw_profile_head(img, cx, cy, r, facing="right", expr="neutral"):
    """옆모습 머리 — 라인만(원본 졸라걸 선화). 코는 윤곽에 통합, 눈 하나·눈썹·입·귀 선."""
    d = ImageDraw.Draw(img)
    s = 1 if facing == "right" else -1
    ow = max(2, int(r*0.09))
    # 머리 실루엣(프로필): 원 + 앞쪽 코 돌출 폴리곤. 흰 채움 + 선 윤곽.
    sil = []
    for i in range(49):
        a = -math.pi/2 + 2*math.pi*i/48
        rr = r
        da = abs(a)                                   # a=0 → 앞(오른쪽) 코
        if da < math.radians(24): rr = r*(1.0 + 0.18*(1-da/math.radians(24)))
        sil.append((cx + s*rr*math.cos(a), cy + rr*math.sin(a)))
    d.polygon(sil, fill=WHITE)
    d.line(sil+[sil[0]], fill=INK, width=ow, joint="curve")
    # 머리묶음(뒤) — 라인
    br = r*0.58; bx = cx - s*r*0.66; by = cy - r*0.66
    d.ellipse([bx-br, by-br, bx+br, by+br], fill=ORANGE, outline=INK, width=ow)
    # 앞머리 한 가닥(이마→코 위) 라인
    d.line([(cx - s*r*0.2, cy-r*0.95),(cx + s*r*0.75, cy-r*0.35)], fill=INK, width=max(2,int(r*0.05)))
    # 눈 하나
    ex = cx + s*r*0.40; ey = cy - r*0.08; er = max(2, r*0.11)
    d.ellipse([ex-er, ey-er, ex+er, ey+er], fill=INK)
    # 눈썹(선)
    d.line([(ex-s*r*0.05, ey-r*0.30),(ex+s*r*0.22, ey-r*0.26)], fill=INK, width=max(2,int(r*0.055)))
    # 입(표정, 코 아래 앞쪽) — 선
    mx = cx + s*r*0.62; my = cy + r*0.44
    if expr == "happy":
        d.line([(mx-s*r*0.18, my-r*0.02),(mx, my+r*0.10),(mx+s*r*0.14, my-r*0.02)], fill=INK, width=max(2,int(r*0.07)), joint="curve")
    elif expr in ("talk","surprised"):
        rr=r*0.10; d.ellipse([mx-rr, my-rr, mx+rr, my+rr], outline=INK, width=max(2,int(r*0.07)))
    else:
        d.line([(mx-s*r*0.12, my),(mx+s*r*0.10, my)], fill=INK, width=max(2,int(r*0.07)))
    # 귀 하나(뒤쪽) — 작은 반원 선
    ear_x = cx - s*r*0.20; ear_y = cy + r*0.05; err = r*0.14
    a0, a1 = (270, 90) if s>0 else (90, 270)
    d.arc([ear_x-err, ear_y-err, ear_x+err, ear_y+err], a0, a1, fill=INK, width=ow)


# ---------- 얼굴 그리기(정면/옆모습 + 표정) ----------
def draw_face_on(img, cx, cy, r, facing="front", expr="neutral"):
    """깨끗한 머리 위에 눈·코·입을 그림. facing=front/right, expr=neutral/happy/talk/think."""
    d = ImageDraw.Draw(img)
    ex = r * 0.34; ey = cy - r * 0.10
    er = max(2, r * 0.11)
    fo = {"front": 0.0, "right": 0.34, "left": -0.34}.get(facing, 0.0)
    cxf = cx + r * fo
    # 눈
    if facing == "front":
        eyes = [(cxf - ex, ey), (cxf + ex, ey)]
    else:
        s = 1 if facing == "right" else -1
        eyes = [(cxf + s * ex * 0.15, ey), (cxf + s * ex * 0.62, ey)]
    for (x, y) in eyes:
        d.ellipse([x-er, y-er, x+er, y+er], fill=INK)
    # 코(옆모습이면 튀어나온 코, 정면이면 작은 점/선)
    if facing != "front":
        s = 1 if facing == "right" else -1
        nx = cxf + s * r * 0.72
        d.line([(cxf + s*r*0.5, cy+r*0.10), (nx, cy+r*0.18), (cxf + s*r*0.5, cy+r*0.26)], fill=INK, width=max(2, int(r*0.06)))
    else:
        d.ellipse([cxf-er*0.5, cy+r*0.12-er*0.5, cxf+er*0.5, cy+r*0.12+er*0.5], fill=INK)
    # 입(표정)
    my = cy + r * 0.42; mw = r * 0.30
    if expr == "happy":
        seg = [(cxf-mw+r*fo*0, my), (cxf, my+r*0.16), (cxf+mw, my)]
        d.line(seg, fill=INK, width=max(2, int(r*0.09)), joint="curve")
    elif expr in ("talk", "surprised"):
        rr = r*0.14; d.ellipse([cxf-rr, my-rr, cxf+rr, my+rr], outline=INK, width=max(2,int(r*0.09)))
    elif expr == "think":
        d.line([(cxf-mw*0.6, my), (cxf+mw*0.2, my-r*0.05)], fill=INK, width=max(2,int(r*0.08)))
    else:
        d.line([(cxf-mw*0.6, my), (cxf+mw*0.6, my)], fill=INK, width=max(2, int(r*0.08)))


# ---------- 포즈 렌더 ----------
def has_part(char_key, part):
    c = _con()
    r = c.execute("SELECT 1 FROM anim_char_parts WHERE char_key=? AND part=?", (char_key, part)).fetchone()
    c.close()
    return r is not None


_PARTS = {}
def head_part(char_key, part="head_front"):
    key = (char_key, part)
    if key not in _PARTS:
        c = _con()
        r = c.execute("SELECT file_path,ax,ay FROM anim_char_parts WHERE char_key=? AND part=?", (char_key, part)).fetchone()
        if not r:  # 폴백: 아무 머리
            r = c.execute("SELECT file_path,ax,ay FROM anim_char_parts WHERE char_key=? AND part LIKE 'head%'", (char_key,)).fetchone()
        c.close()
        _PARTS[key] = (Image.open(os.path.join(ROOT, r[0])).convert("RGBA"), r[1], r[2]) if r else None
    return _PARTS[key]


# ---------- 모션: 키프레임 보간(연속 프레임 생성) ----------
def lerp_pose(A, B, t):
    """두 포즈(관절 dict) 사이 보간 → 중간 프레임."""
    return {k: (A[k][0]*(1-t) + B[k][0]*t, A[k][1]*(1-t) + B[k][1]*t) for k in A}


def motion_frames(char_key, keyframes, n, H=520, expr="neutral"):
    """keyframes=[(joints, turn), ...] 를 부드럽게 이어 n프레임(연속 동작).
    turn도 함께 보간 → 몸 회전(일어서기/앉기/돌기)까지 매끄럽게. keyframes 원소가 joints만이면 turn=0."""
    kf = [(k if isinstance(k, tuple) else (k, 0.0)) for k in keyframes]
    frames = []
    segs = len(kf) - 1
    for i in range(n):
        u = i / max(1, n-1) * segs
        k = min(segs-1, int(u)); ft = u - k
        ft = ft*ft*(3-2*ft)                              # smoothstep
        if segs > 0:
            J = lerp_pose(kf[k][0], kf[k+1][0], ft)
            turn = kf[k][1]*(1-ft) + kf[k+1][1]*ft
        else:
            J, turn = kf[0][0], kf[0][1]
        frames.append(render(char_key, J, H=H, expr=expr, turn=turn))
    return frames


def _cubic(p0, p1, p2, n=18):
    """2차(관절 하나) 곡선 근사 — 어깨/골반→관절→끝."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0]
        y = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]
        pts.append((x, y))
    return pts


def render(char_key, joints, H=520, seed=0, facing="front", expr="neutral", turn=None, face=None, squish=True):
    """관절좌표로 캐릭터 렌더. turn(0=정면 0.5=옆 1.0=뒤)=몸회전(폭 squish+머리방향).
    face=front/side/back 로 머리방향 강제(옆투영 걷기처럼 관절이 이미 옆이면 squish=False+face=side)."""
    J = joints
    if turn is None:
        turn = 0.5 if facing in ("right", "left") else 0.0
    wf = (0.18 + 0.82 * abs(math.cos(turn * math.pi))) if squish else 1.0   # 몸 가로 폭
    spine_x = J["chest"][0]
    # 머리 방향: face 강제 없으면 turn으로
    if face is not None:
        view = face
    elif turn < 0.30: view = "front"
    elif turn > 0.72: view = "back"
    else: view = "side"
    ys = [v[1] for v in J.values()]; xs = [spine_x + (v[0]-spine_x)*wf for v in J.values()]
    span = max(ys) - min(ys)
    sc = H / (span + 14)
    minx, miny = min(xs), min(ys)
    top_clear = int(sc * 24)
    side_clear = int(sc * 18)
    bot_pad = int(sc * 8)
    def px(p):
        x = spine_x + (p[0]-spine_x)*wf
        return ((x-minx)*sc + side_clear, (p[1]-miny)*sc + top_clear)
    Wc = int((max(xs)-minx)*sc + side_clear*2)
    Hc = int((max(ys)-miny)*sc + top_clear + bot_pad)
    img = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = max(4, int(1.7 * sc))

    def limb(a, b, c, bow=0.0, lengthen=0.0, target=None):
        """a→b(관절)→c 곡선. bow=수직 방향으로 활처럼 휘게, lengthen=c를 방향으로 더 뻗기."""
        A, B, C = px(a), px(b), px(c)
        if lengthen:                                  # 팔 더 길게(잘 보이게)
            vx, vy = C[0]-B[0], C[1]-B[1]
            L = math.hypot(vx, vy) or 1
            C = (C[0] + vx/L*lengthen*sc, C[1] + vy/L*lengthen*sc)
        if bow:                                       # 곡선(활): 중간 관절을 수직으로 밀어 휘게
            vx, vy = C[0]-A[0], C[1]-A[1]
            L = math.hypot(vx, vy) or 1
            nx, ny = -vy/L, vx/L
            B = (B[0] + nx*bow*sc, B[1] + ny*bow*sc)
        dd = ImageDraw.Draw(target) if target else d
        pts = _cubic(A, B, C)
        dd.line(pts, fill=INK, width=lw, joint="curve")
        for p in (pts[0], pts[-1]):
            dd.ellipse([p[0]-lw/2, p[1]-lw/2, p[0]+lw/2, p[1]+lw/2], fill=INK)
        return pts[-1]                                # 손 끝 좌표

    def mitten(p, layer):
        r = 2.6 * sc
        ImageDraw.Draw(layer).ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r],
            fill=(252,250,247,255), outline=INK, width=max(2,int(lw*0.5)))

    # 1) 몸통·다리(뒤)
    limb(J["chest"], J["body"], J["pelvis"])
    limb(J["pelvis"], J["kneeLeft"], J["feetLeft"])
    limb(J["pelvis"], J["kneeRight"], J["feetRight"])
    for ft in (J["feetLeft"], J["feetRight"]):
        p = px(ft); dxn = 1 if ft[0] >= J["pelvis"][0] else -1
        fw, fh = 3.6*sc, 1.9*sc; cx = p[0]+dxn*fw*0.4
        d.ellipse([cx-fw, p[1]-fh*0.3, cx+fw, p[1]+fh], fill=(252,250,247,255), outline=INK, width=max(2,int(lw*0.5)))
    # 2) 머리 — 정면=원본AI얼굴 / 옆=진짜 프로필(그림) / 뒤=깨끗머리
    if view == "side":                                      # 옆모습 = 코·눈하나·귀하나 프로필 그림
        cj = px(J["chest"]); hj = px(J["head"])
        headspan = math.hypot(hj[0]-cj[0], hj[1]-cj[1]) or 1
        r = headspan * 1.05
        dxh = hj[0]-cj[0]; tilt = max(-headspan*0.5, min(headspan*0.5, dxh))
        neck = (cj[0] + tilt*0.4, cj[1] - headspan*0.10)
        hc = (neck[0], neck[1] - r*0.95)                   # 머리 중심(목 위)
        d.line([cj, (hc[0], hc[1]+r*0.9)], fill=INK, width=lw)
        fc = "right" if turn <= 0.5 else "left"
        draw_profile_head(img, hc[0], hc[1], r, facing=fc, expr=expr)
        hp = None
    else:
        want = {"front": "head_front", "back": "head_clean"}.get(view, "head_front")
        hp = head_part(char_key, want)
    real_side = False
    if hp:
        him, ax, ay = hp
        hj = px(J["head"]); cj = px(J["chest"])
        headspan = math.hypot(hj[0]-cj[0], hj[1]-cj[1]) or 1
        target_h = headspan * 2.2
        s = target_h / him.height
        hw, hh = max(1, int(him.width * s)), max(1, int(him.height * s))
        hres = him.resize((hw, hh), Image.LANCZOS)
        # 목 지점 = chest 바로 위(머리 쪽으로 살짝). 머리 회전은 몸 turn 방향으로 좌우 최대 ±45°만.
        dxh = hj[0] - cj[0]
        tilt = max(-headspan*0.5, min(headspan*0.5, dxh))   # 머리 좌우 기울기 제한(45°)
        neck = (cj[0] + tilt*0.4, cj[1] - headspan*0.10)
        axp, ayp = (him.width/2)*s, (him.height-2)*s        # 부품 목=하단중앙
        pos = (int(neck[0] - axp), int(neck[1] - ayp))
        d.line([cj, neck], fill=INK, width=lw)              # 목 선(몸→머리 연결)
        d.ellipse([cj[0]-lw/2, cj[1]-lw/2, cj[0]+lw/2, cj[1]+lw/2], fill=INK)
        img.alpha_composite(hres, pos)
        if view == "side" and not real_side:               # 원본 옆얼굴 없을 때만 그림
            fc = "right" if turn <= 0.5 else "left"
            draw_face_on(img, pos[0] + hw/2, pos[1] + hh*0.56, hw*0.40, facing=fc, expr=expr)

    # 3) 팔 — 곡선+길게+맨 위(얼굴/몸에 안 가리게 잘 보이도록)
    hL = limb(J["chest"], J["elbowLeft"], J["handLeft"], bow=-2.6, lengthen=1.4)
    mitten(hL, img)
    hR = limb(J["chest"], J["elbowRight"], J["handRight"], bow=2.6, lengthen=1.4)
    mitten(hR, img)
    return img


_EXPRMAP = {"happy": "happy", "talk": "talk", "surprised": "talk", "neutral": "neutral", "": "neutral"}
def render_pose_name(char_key, pose_name, H=520):
    c = _con()
    r = c.execute("SELECT joints_json,facing,expr FROM anim_poses WHERE pose_name=?", (pose_name,)).fetchone()
    c.close()
    if not r: return None
    facing = r[1] or "front"
    expr = _EXPRMAP.get(r[2] or "neutral", "neutral")
    return render(char_key, json.loads(r[0]), H=H, facing=facing, expr=expr)


def _sheet():
    from PIL import ImageFont
    ck = "zolla_girl"
    extract_head(ck, os.path.join(ROOT, "assets", "graphics", "poses", "stickman_zw_base.png"))
    names = ["walk1", "write_up", "write_mid", "explain", "point_right", "look",
             "sit_think", "sit_read", "sit_front", "sig_jump"]
    cell = 340
    cols = 5; rows = (len(names)+cols-1)//cols
    sheet = Image.new("RGB", (cell*cols, cell*rows), (245,244,240))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 22)
    for i, nm in enumerate(names):
        im = render_pose_name(ck, nm, H=cell-90)
        if im is None: continue
        r, c = divmod(i, cols)
        bg = Image.new("RGB", (cell, cell), (245,244,240))
        bg.paste(im.convert("RGB"), ((cell-im.width)//2, (cell-im.height)//2 + 20), im)
        sheet.paste(bg, (c*cell, r*cell))
        d.text((c*cell+10, r*cell+8), nm, font=f, fill=(30,30,40))
    out = os.path.join(ROOT, "scratch", "_motionrig_sheet.png")
    sheet.save(out); print("sheet ->", out)


if __name__ == "__main__":
    _sheet()
