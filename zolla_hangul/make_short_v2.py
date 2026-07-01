# -*- coding: utf-8 -*-
"""졸라 한글 레고 쇼츠 v2 (세로 1080x1920) — 춤+군무 내러티브.
졸라맨·졸라녀가 신나게 춤추는 동안, 비티에스+다이나마이트의 '모든 자모'가 한꺼번에
날아와 위에서 떠다닌다 → 삐뚤게 슬롯에 조합 → 하나(다의 ㄷ)가 툭 떨어진다 →
춤추던 졸라맨이 다가가 주워서 위로 던져 올린다 → 그 순간 모든 글자가 동시에 똑바로
완성(노란 블록)되고 → 아래에 영어(BTS / dynamite)가 붙어 표시된다.
프로그램 모션그래픽(PIL+MoviePy). 음악은 무음 렌더 후 finalize에서 mux."""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "scratch"))
from hangeul_decomposer import decompose_char
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

W, H, FPS = 1080, 1920, 30
ODIR = os.path.join(ROOT, "zolla_hangul")
OUT = os.path.join(ODIR, "dynamite_short_v2_silent.mp4")
FONT = r"C:\Windows\Fonts\malgunbd.ttf"
HV = os.path.join(ROOT, "home_vocab")

VOWELS_H = set("ㅗㅛㅜㅠㅡ")
CONS_COLOR = (255, 107, 107); VOW_COLOR = (78, 205, 196)
SYL_COLOR = (255, 213, 61); INK = (40, 40, 45)

_FC = {}
def font(sz):
    sz = int(sz)
    if sz not in _FC: _FC[sz] = ImageFont.truetype(FONT, sz)
    return _FC[sz]

def ease(p): return 1 - (1 - p) ** 3
def ease_io(p): return 0.5 - 0.5 * math.cos(math.pi * clamp(p, 0, 1))
def clamp(v, a, b): return max(a, min(b, v))
def lerp(a, b, t): return a + (b - a) * t

# ---------- 블록 타일 ----------
def block_tile(char, w, h, fill, studs=True, text_rgb=INK):
    w, h = int(w), int(h)
    tile = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    r = max(9, int(min(w, h) * 0.16))
    d.rounded_rectangle([3, 3, w - 4, h - 4], radius=r, fill=fill + (255,),
                        outline=INK + (255,), width=max(3, w // 55))
    if studs:
        n = 2 if w < h * 1.3 else 3
        sr = int(min(w, h) * 0.11)
        for i in range(n):
            cx = int(w * (i + 1) / (n + 1)); cy = int(h * 0.15)
            lt = tuple(min(255, c + 35) for c in fill)
            d.ellipse([cx - sr, cy - sr, cx + sr, cy + sr], fill=lt + (255,),
                      outline=INK + (255,), width=max(2, w // 90))
    f = font(int(min(w, h) * 0.62))
    bb = d.textbbox((0, 0), char, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((w - tw) / 2 - bb[0], (h - th) / 2 - bb[1] + h * 0.04), char,
           font=f, fill=text_rgb + (255,))
    return tile

def paste_alpha(base, tile, cx, cy, factor=1.0, angle=0.0):
    if factor <= 0.01: return
    t = tile
    if abs(angle) > 0.5:
        t = t.rotate(angle, expand=True, resample=Image.BICUBIC)
    if factor < 0.99:
        t = t.copy(); t.putalpha(t.split()[3].point(lambda v: int(v * factor)))
    base.alpha_composite(t, (int(cx - t.width / 2), int(cy - t.height / 2)))

# ---------- 졸라 포즈 로드(흰 배경 제거, 고정 크롭으로 정렬 유지) ----------
CROP = (340, 20, 1040, 760)  # (left,upper,right,lower) 동일 크롭 → 발/크기 정렬 유지
def load_pose(path, target_h, flip=False):
    im = Image.open(path).convert("RGBA").crop(CROP)
    arr = np.array(im)
    white = (arr[:, :, 0] > 244) & (arr[:, :, 1] > 244) & (arr[:, :, 2] > 244)
    arr[white, 3] = 0
    im = Image.fromarray(arr)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    w = int(im.width * target_h / im.height)
    return im.resize((w, target_h), Image.LANCZOS)

CH_H = 470
def load_set(prefix, flip):
    names = ["base", "pointing", "waving", "clapping", "cheering", "jumping"]
    return {n: load_pose(os.path.join(HV, f"{prefix}_{n}.png"), CH_H, flip) for n in names}
print("졸라 포즈 로딩...")
MAN = load_set("zollaman", False)
NYEO = load_set("zollanyeo", True)
CH_W = MAN["base"].width  # 동일 크롭/높이 → 폭 동일

# ---------- 단어/자모 계획 ----------
def build_jamos():
    rows = [dict(text="비티에스", cy=640, cell=170, gap=24),
            dict(text="다이나마이트", cy=900, cell=135, gap=15)]
    jamos = []; syllables = []
    for ri, row in enumerate(rows):
        text = row["text"]; n = len(text); cell = row["cell"]; gap = row["gap"]
        total = n * cell + (n - 1) * gap
        x0 = (W - total) / 2 + cell / 2
        for i, ch in enumerate(text):
            cx = x0 + i * (cell + gap); cy = row["cy"]
            cons, vow = decompose_char(ch, fully_decompose=False)[:2]
            layout = "TB" if vow in VOWELS_H else "LR"
            syllables.append(dict(ch=ch, cx=cx, cy=cy, cell=cell))
            if layout == "LR":
                cw, chh = cell * 0.46, cell * 0.82; vw, vh = cell * 0.40, cell * 0.86
                ct = (cx - cell * 0.23, cy); vt = (cx + cell * 0.25, cy)
            else:
                cw, chh = cell * 0.84, cell * 0.44; vw, vh = cell * 0.86, cell * 0.40
                ct = (cx, cy - cell * 0.23); vt = (cx, cy + cell * 0.25)
            for role, (chj, col, sz, tgt) in {
                "cons": (cons, CONS_COLOR, (cw, chh), ct),
                "vow":  (vow, VOW_COLOR, (vw, vh), vt)}.items():
                k = len(jamos)
                jamos.append(dict(char=chj, color=col, w=sz[0], h=sz[1],
                    target=tgt, syl=len(syllables) - 1,
                    crook_a=((-1) ** k) * (7 + (k % 4) * 4),
                    crook_dx=((-1) ** k) * sz[0] * 0.10, crook_dy=((k % 3) - 1) * sz[1] * 0.10,
                    anchor=(120 + (k * 137) % 840, 290 + (k * 71) % 250),
                    origin=[(-200, 300), (W + 200, 350), (W * 0.3, -250),
                            (W * 0.7, -250), (W + 200, H * 0.5)][k % 5]))
    return jamos, syllables

JAMOS, SYLS = build_jamos()
DROP_IDX = next(i for i, j in enumerate(JAMOS) if j["syl"] == 4 and j["char"] == "ㄷ")  # 다의 ㄷ

# ---------- 타임라인 ----------
T_FLYIN = 3.5; T_FLOAT = 6.0; T_ASMB = 10.0
T_DROP = 11.5; T_WALK = 13.5; T_TOSS = 15.5; T_DONE = 16.4
T_END = 20.5
DROP_GROUND = (JAMOS[DROP_IDX]["target"][0] - 30, 1430)  # 떨어진 위치(졸라맨 앞 바닥)
MAN_X0, NYEO_X0 = 255, 825          # 캐릭터 figure 중심 x
MAN_BASE_Y = 1900                   # 캐릭터 바닥(붙일 기준 y)

# ---------- 댄스 ----------
DANCE = ["base", "pointing", "waving", "clapping"]
def dance_pose(poses, t, phase_off=0.0, celebrate=False):
    if celebrate:
        return poses["cheering"] if int(t * 3) % 2 else poses["jumping"]
    beat = 0.46
    idx = int((t + phase_off) / beat) % len(DANCE)
    return poses[DANCE[idx]]

def draw_char(base, poses, center_x, t, celebrate=False, phase_off=0.0, override=None):
    pose = override if override is not None else dance_pose(poses, t, phase_off, celebrate)
    beat = 0.46
    hop = abs(math.sin(math.pi * (t + phase_off) / beat)) * (30 if not celebrate else 55)
    sway = math.sin(2 * math.pi * (t + phase_off) / (beat * 2)) * 12
    ang = math.sin(2 * math.pi * (t + phase_off) / (beat * 2)) * 5
    cx = center_x + sway
    cy = MAN_BASE_Y - hop
    paste_alpha(base, pose, cx, cy - pose.height / 2, 1.0, angle=ang)
    return cx

def man_hand(man_cx, t):
    # 던질 때 손 위치(대략 머리 위)
    return (man_cx, MAN_BASE_Y - CH_H * 0.82)

# ---------- 배경 ----------
def make_bg():
    top = np.array([255, 250, 242]); bot = np.array([224, 236, 255])
    col = (top[None, :] + (bot - top)[None, :] * (np.linspace(0, 1, H)[:, None])).astype(np.uint8)
    return Image.fromarray(np.repeat(col[:, None, :], W, axis=1), "RGB").convert("RGBA")
BG = make_bg()

def label(base, text, cy, size, color=INK, alpha=1.0):
    if alpha <= 0.01: return
    f = font(size); d = ImageDraw.Draw(base)
    bb = d.textbbox((0, 0), text, font=f); tw = bb[2] - bb[0]
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(((W - tw) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]),
                               text, font=f, fill=color + (int(255 * alpha),))
    base.alpha_composite(layer)

# ---------- 자모 현재 위치 계산 ----------
def jamo_pos(j, idx, t, man_cx):
    """(x, y, angle, factor) — 단계별 자모 위치."""
    tx, ty = j["target"]
    crook = (tx + j["crook_dx"], ty + j["crook_dy"], j["crook_a"])
    if t < T_FLYIN:                                  # 가장자리→플로팅
        p = ease(clamp(t / T_FLYIN, 0, 1))
        ox, oy = j["origin"]; ax, ay = j["anchor"]
        return lerp(ox, ax, p), lerp(oy, ay, p), (1 - p) * 200, 1.0
    if t < T_ASMB:                                   # 플로팅(웨이브)
        ax, ay = j["anchor"]
        wob = math.sin(t * 1.6 + idx) * 14
        wob2 = math.cos(t * 1.3 + idx * 0.7) * 12
        return ax + wob, ay + wob2, math.sin(t * 2 + idx) * 12, 1.0
    if idx != DROP_IDX:
        if t < T_ASMB + 1.6:                         # 삐뚤 조합으로 이동
            p = ease(clamp((t - T_ASMB) / 1.6, 0, 1))
            ax, ay = j["anchor"]
            return lerp(ax, crook[0], p), lerp(ay, crook[1], p), lerp(math.sin(idx) * 12, crook[2], p), 1.0
        return crook[0], crook[1], crook[2], 1.0      # 삐뚤하게 대기
    # ----- 떨어지는 자모 -----
    if t < T_ASMB + 1.6:                              # 일단 삐뚤 슬롯으로
        p = ease(clamp((t - T_ASMB) / 1.6, 0, 1))
        ax, ay = j["anchor"]
        return lerp(ax, crook[0], p), lerp(ay, crook[1], p), lerp(0, crook[2], p), 1.0
    if t < T_DROP:                                    # 슬롯에서 흔들(곧 떨어질 듯)
        return crook[0], crook[1], crook[2] + math.sin(t * 18) * 6, 1.0
    if t < T_WALK:                                    # 중력 낙하 → 바닥
        p = clamp((t - T_DROP) / (T_WALK - T_DROP), 0, 1)
        gx, gy = DROP_GROUND
        x = lerp(crook[0], gx, p)
        y = lerp(crook[1], gy, p * p) + (math.sin(p * math.pi) * 0)   # 가속 낙하
        return x, y, crook[2] + p * 120, 1.0
    if t < T_TOSS:                                    # 졸라맨이 주워 손에 듦
        hx, hy = man_hand(man_cx, t)
        p = ease(clamp((t - T_WALK) / (T_TOSS - T_WALK), 0, 1))
        gx, gy = DROP_GROUND
        return lerp(gx, hx, p), lerp(gy, hy, p), 60 * (1 - p), 1.0
    if t < T_DONE:                                    # 위로 던져 → 슬롯 복귀(포물선)
        p = ease(clamp((t - T_TOSS) / (T_DONE - T_TOSS), 0, 1))
        hx, hy = man_hand(man_cx, T_TOSS)
        x = lerp(hx, tx, p)
        y = lerp(hy, ty, p) - math.sin(p * math.pi) * 220        # 포물선 토스
        return x, y, p * 360, 1.0
    return tx, ty, 0, 1.0

# ---------- 프레임 ----------
def make_frame(t):
    base = BG.copy()
    celebrate = t >= T_DONE
    # 졸라맨: 보통은 제자리 춤, WALK~TOSS엔 떨어진 곳으로 이동 + 던지기 포즈
    if T_WALK - 2.0 <= t < T_TOSS:
        wp = ease(clamp((t - (T_WALK - 2.0)) / 2.0, 0, 1))
        man_target = DROP_GROUND[0] + 10
        man_cx = lerp(MAN_X0, man_target, wp)
        pose_ov = MAN["base"]
    elif T_TOSS <= t < T_DONE:
        man_cx = DROP_GROUND[0] + 10
        pose_ov = MAN["cheering"]            # 던지는 순간 팔 위로
    else:
        man_cx = MAN_X0; pose_ov = None

    man_cx_drawn = draw_char(base, MAN, man_cx, t, celebrate=celebrate, override=pose_ov)
    draw_char(base, NYEO, NYEO_X0, t, celebrate=celebrate, phase_off=0.23)

    # 타이틀(조합 시작 전까지)
    ti = clamp(t / 0.6, 0, 1) * (1 - clamp((t - (T_ASMB - 0.5)) / 1.0, 0, 1))
    label(base, "한글은 레고처럼!", 150, 84, color=(60, 60, 70), alpha=ti)

    # 완성 전: 자모들(비행/플로팅/조합/낙하/토스)
    if t < T_DONE:
        for idx, j in enumerate(JAMOS):
            x, y, a, fac = jamo_pos(j, idx, t, man_cx_drawn)
            tile = block_tile(j["char"], j["w"], j["h"], j["color"])
            paste_alpha(base, tile, x, y, factor=fac, angle=a)
        # 슬롯 가이드(조합 단계)
        if T_ASMB <= t < T_DONE:
            d = ImageDraw.Draw(base)
            for s in SYLS:
                hw = s["cell"] / 2
                d.rounded_rectangle([s["cx"] - hw, s["cy"] - hw, s["cx"] + hw, s["cy"] + hw],
                                    radius=int(s["cell"] * 0.14), outline=(175, 180, 190, 150), width=3)
    # 완성: 동시에 노란 글자 + 영어 라벨 붙음
    if t >= T_ASMB:
        m = clamp((t - T_DONE) / 0.5, 0, 1)
        if m > 0:
            for s in SYLS:
                tile = block_tile(s["ch"], s["cell"] * 0.94, s["cell"] * 0.94, SYL_COLOR)
                paste_alpha(base, tile, s["cx"], s["cy"], factor=m)
    if celebrate:
        la = clamp((t - T_DONE - 0.3) / 0.5, 0, 1)
        slide = (1 - la) * 50
        label(base, "BTS", 770 + slide, 92, color=(55, 55, 65), alpha=la)
        label(base, "dynamite", 1035 + slide, 80, color=(55, 55, 65), alpha=la)
        label(base, "한글, 블록처럼 조립!", 1170, 50, color=(150, 120, 60), alpha=clamp((t-T_DONE-0.8)/0.5,0,1))
    return np.array(base.convert("RGB"))

def main():
    os.makedirs(ODIR, exist_ok=True)
    print(f"DROP_IDX={DROP_IDX} ({JAMOS[DROP_IDX]['char']}), 자모 {len(JAMOS)}개, 음절 {len(SYLS)}개, 총 {T_END:.1f}s")
    clip = VideoClip(make_frame, duration=T_END)
    clip.write_videofile(OUT, fps=FPS, codec="libx264", audio=False,
                         threads=os.cpu_count() or 4, preset="medium", bitrate="6000k")
    print(f"[OK] {OUT}")

if __name__ == "__main__":
    main()
