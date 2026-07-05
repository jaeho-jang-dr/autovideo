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


# ---------- 머리 부품 추출 ----------
def extract_head(char_key, base_png, head_frac=0.34):
    """원본 컷아웃 상단(머리+머리카락+얼굴)을 잘라 부품으로 저장.
    부착점(ax,ay)=목 연결부(부품 하단 중앙) — 렌더 시 머리 관절에 맞춤."""
    ensure_tables()
    im = Image.open(base_png).convert("RGBA")
    a = np.array(im)[:, :, 3]
    h, w = a.shape
    # 머리 영역: 상단 head_frac. 목(가장 좁은 행) 아래로 살짝 포함.
    cut = int(h * head_frac)
    head = im.crop((0, 0, w, cut))
    # 좌우 여백 트림
    ha = np.array(head)[:, :, 3]
    xs = np.where(ha.sum(axis=0) > 0)[0]
    if len(xs):
        head = head.crop((max(0, xs[0]-4), 0, min(w, xs[-1]+4), cut))
    outdir = os.path.join(ROOT, "assets", "graphics", "parts")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, f"{char_key}_head.png")
    head.save(out)
    ax, ay = head.width / 2, head.height - 2      # 목=하단 중앙
    fp = os.path.relpath(out, ROOT).replace(os.sep, "/")
    c = _con()
    c.execute("DELETE FROM anim_char_parts WHERE char_key=? AND part='head'", (char_key,))
    c.execute("INSERT INTO anim_char_parts(char_key,part,file_path,ax,ay,updated_at) VALUES (?,?,?,?,?,datetime('now'))",
              (char_key, "head", fp, ax, ay))
    c.commit(); c.close()
    print(f"  head part -> {fp} ({head.size}) attach=({ax:.0f},{ay:.0f})")
    return out


# ---------- 포즈 렌더 ----------
_PARTS = {}
def head_part(char_key):
    if char_key not in _PARTS:
        c = _con()
        r = c.execute("SELECT file_path,ax,ay FROM anim_char_parts WHERE char_key=? AND part='head'", (char_key,)).fetchone()
        c.close()
        if r:
            _PARTS[char_key] = (Image.open(os.path.join(ROOT, r[0])).convert("RGBA"), r[1], r[2])
        else:
            _PARTS[char_key] = None
    return _PARTS[char_key]


def _cubic(p0, p1, p2, n=18):
    """2차(관절 하나) 곡선 근사 — 어깨/골반→관절→끝."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0]
        y = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]
        pts.append((x, y))
    return pts


def render(char_key, joints, H=520, seed=0):
    """관절좌표(60x80 단위)로 캐릭터 렌더. 팔다리=선, 손발=도형, 머리=원본 부품."""
    J = joints
    # 60x80 단위 → 픽셀. 스키 세로 ~ y 8..68
    ys = [v[1] for v in J.values()]; xs = [v[0] for v in J.values()]
    span = max(ys) - min(ys)
    sc = H / (span + 14)
    pad = int(6 * sc)
    minx, miny = min(xs), min(ys)
    def px(p): return ((p[0]-minx)*sc + pad + 40*sc*0, (p[1]-miny)*sc + pad)
    Wc = int((max(xs)-minx)*sc + pad*2 + 80*sc)
    Hc = int((max(ys)-miny)*sc + pad*2 + 30*sc)
    img = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = max(4, int(1.7 * sc))

    def limb(a, b, c):
        pts = _cubic(px(a), px(b), px(c))
        d.line(pts, fill=INK, width=lw, joint="curve")
        for p in (pts[0], pts[-1]):
            d.ellipse([p[0]-lw/2, p[1]-lw/2, p[0]+lw/2, p[1]+lw/2], fill=INK)

    # 몸통·팔·다리
    limb(J["chest"], J["body"], J["pelvis"])
    limb(J["chest"], J["elbowLeft"], J["handLeft"])
    limb(J["chest"], J["elbowRight"], J["handRight"])
    limb(J["pelvis"], J["kneeLeft"], J["feetLeft"])
    limb(J["pelvis"], J["kneeRight"], J["feetRight"])
    # 손(장갑)
    for hd in (J["handLeft"], J["handRight"]):
        p = px(hd); r = 2.4 * sc
        d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=(252,250,247,255), outline=INK, width=max(2,int(lw*0.5)))
    # 발(신발)
    for ft, kn in [(J["feetLeft"], J["kneeLeft"]), (J["feetRight"], J["kneeRight"])]:
        p = px(ft); dxn = 1 if ft[0] >= J["pelvis"][0] else -1
        fw, fh = 3.6*sc, 1.9*sc
        cx = p[0] + dxn*fw*0.4
        d.ellipse([cx-fw, p[1]-fh*0.3, cx+fw, p[1]+fh], fill=(252,250,247,255), outline=INK, width=max(2,int(lw*0.5)))
    # 머리 부품(원본 얼굴) — 머리 관절에 부착점 맞춤
    hp = head_part(char_key)
    if hp:
        him, ax, ay = hp
        # 머리 크기: 관절 head~chest 거리로 스케일
        hj = px(J["head"]); cj = px(J["chest"])
        headspan = math.hypot(hj[0]-cj[0], hj[1]-cj[1]) or 1
        target_h = headspan * 2.9
        s = target_h / him.height
        hw, hh = max(1, int(him.width*s)), max(1, int(him.height*s))
        hres = him.resize((hw, hh), Image.LANCZOS)
        # 부착점(목)이 머리관절보다 살짝 아래(chest 쪽)로
        axp, ayp = ax*s, ay*s
        pos = (int(hj[0]-axp), int(hj[1]-ayp + target_h*0.16))
        img.alpha_composite(hres, pos)
    return img


def render_pose_name(char_key, pose_name, H=520):
    c = _con()
    r = c.execute("SELECT joints_json FROM anim_poses WHERE pose_name=?", (pose_name,)).fetchone()
    c.close()
    if not r: return None
    return render(char_key, json.loads(r[0]), H=H)


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
