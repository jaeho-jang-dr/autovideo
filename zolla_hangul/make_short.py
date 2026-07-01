# -*- coding: utf-8 -*-
"""졸라맨·졸라녀 한글 '레고 블록' 쇼츠 (세로 1080x1920).
자모(자음+모음)가 하나씩 날아와 음절칸에 스냅 → 완성 글자(노란 블록)로 변신.
단어: 비티에스(BTS), 다이나마이트(dynamite). 아래에 영어 라벨.
프로그램 모션그래픽(MoviePy 2.x + PIL). 음악은 무음으로 렌더 후 별도 mux."""
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
OUT = os.path.join(ODIR, "dynamite_short_silent.mp4")
FONT = r"C:\Windows\Fonts\malgunbd.ttf"
HV = os.path.join(ROOT, "home_vocab")

VOWELS_H = set("ㅗㅛㅜㅠㅡ")          # 가로모음 → 자음 위 / 모음 아래
# 그 외 세로모음 → 자음 왼쪽 / 모음 오른쪽

CONS_COLOR = (255, 107, 107)   # 자음 = 코랄
VOW_COLOR  = (78, 205, 196)    # 모음 = 청록
SYL_COLOR  = (255, 213, 61)    # 완성 글자 = 노랑
INK        = (40, 40, 45)

# ---------- 폰트 캐시 ----------
_FC = {}
def font(sz):
    sz = int(sz)
    if sz not in _FC: _FC[sz] = ImageFont.truetype(FONT, sz)
    return _FC[sz]

# ---------- 이징 ----------
def ease_out_cubic(p): return 1 - (1 - p) ** 3
def clamp(v, a, b): return max(a, min(b, v))
def lerp(a, b, t): return a + (b - a) * t

# ---------- 블록 타일 ----------
def block_tile(char, w, h, fill, studs=True, text_rgb=INK):
    w, h = int(w), int(h)
    tile = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    r = max(10, int(min(w, h) * 0.16))
    d.rounded_rectangle([3, 3, w - 4, h - 4], radius=r, fill=fill + (255,),
                        outline=INK + (255,), width=max(3, w // 60))
    # 레고 스터드(위쪽 돌기)
    if studs:
        n = 2 if w < h * 1.3 else 3
        sr = int(min(w, h) * 0.11)
        for i in range(n):
            cx = int(w * (i + 1) / (n + 1))
            cy = int(h * 0.14)
            lighter = tuple(min(255, c + 35) for c in fill)
            d.ellipse([cx - sr, cy - sr, cx + sr, cy + sr],
                      fill=lighter + (255,), outline=INK + (255,), width=max(2, w // 90))
    # 글자
    fsz = int(min(w, h) * 0.62)
    f = font(fsz)
    bb = d.textbbox((0, 0), char, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((w - tw) / 2 - bb[0], (h - th) / 2 - bb[1] + h * 0.04), char,
           font=f, fill=text_rgb + (255,))
    return tile

def paste_alpha(base, tile, cx, cy, factor=1.0, angle=0.0):
    """tile을 중심(cx,cy)에 회전/투명도 적용해 합성."""
    if factor <= 0.01: return
    t = tile
    if abs(angle) > 0.5:
        t = t.rotate(angle, expand=True, resample=Image.BICUBIC)
    if factor < 0.99:
        a = t.split()[3].point(lambda v: int(v * factor))
        t = t.copy(); t.putalpha(a)
    x = int(cx - t.width / 2); y = int(cy - t.height / 2)
    base.alpha_composite(t, (x, y))

# ---------- 졸라 캐릭터 로드(흰 배경 제거) ----------
def load_zolla(path, target_h, flip=False):
    im = Image.open(path).convert("RGBA")
    arr = np.array(im)
    mask = ~((arr[:, :, 0] > 244) & (arr[:, :, 1] > 244) & (arr[:, :, 2] > 244))
    ys, xs = np.where(mask)
    if len(xs):
        im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        arr = np.array(im)
        white = (arr[:, :, 0] > 244) & (arr[:, :, 1] > 244) & (arr[:, :, 2] > 244)
        arr[white, 3] = 0
        im = Image.fromarray(arr)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    w = int(im.width * target_h / im.height)
    return im.resize((w, target_h), Image.LANCZOS)

print("졸라 캐릭터 로딩...")
ZMAN  = load_zolla(os.path.join(HV, "zollaman_base.png"), 430)
ZNYEO = load_zolla(os.path.join(HV, "zollanyeo_base.png"), 430, flip=True)
ZMAN_C  = load_zolla(os.path.join(HV, "zollaman_cheering.png"), 470)
ZNYEO_C = load_zolla(os.path.join(HV, "zollanyeo_cheering.png"), 470, flip=True)

# ---------- 단어 → 음절 빌드 계획 ----------
def plan_word(text, cell, gap, cy, t0, stagger, build):
    """각 음절의 칸 중심/자모/레이아웃/타이밍을 계산."""
    n = len(text)
    total = n * cell + (n - 1) * gap
    x0 = (W - total) / 2 + cell / 2
    syls = []
    for i, ch in enumerate(text):
        jamo = decompose_char(ch, fully_decompose=False)  # [자음, 모음] (받침 없음)
        cons, vow = jamo[0], jamo[1]
        layout = "TB" if vow in VOWELS_H else "LR"
        syls.append(dict(ch=ch, cons=cons, vow=vow, layout=layout,
                         cx=x0 + i * (cell + gap), cy=cy, cell=cell,
                         t_start=t0 + i * stagger, build=build))
    end = t0 + (n - 1) * stagger + build
    return syls, end

# 타임라인
T_INTRO = 3.0
W1_T0, W1_STAG, W1_BUILD, C1 = T_INTRO + 0.3, 1.55, 1.45, 200
word1, W1_END = plan_word("비티에스", C1, 22, 760, W1_T0, W1_STAG, W1_BUILD)
W1_LABEL = W1_END + 0.1
W1_HOLD_END = W1_LABEL + 2.2

GAP = 0.6
W2_T0, W2_STAG, W2_BUILD, C2 = W1_HOLD_END + GAP, 1.25, 1.25, 150
word2, W2_END = plan_word("다이나마이트", C2, 14, 760, W2_T0, W2_STAG, W2_BUILD)
W2_LABEL = W2_END + 0.1
W2_HOLD_END = W2_LABEL + 2.2

FIN_T0 = W2_HOLD_END + 0.5
DURATION = FIN_T0 + 4.2

# ---------- 자모 비행 시작점(가장자리) ----------
def origin(idx, cx, cy):
    edges = [(-W * 0.45, cy - 200), (W * 1.45, cy - 200),
             (cx, -H * 0.4), (W * 1.4, H * 1.3), (-W * 0.4, H * 1.3)]
    return edges[idx % len(edges)]

# ---------- 음절 1개 그리기 ----------
def draw_syllable(base, syl, t, global_idx):
    if t < syl["t_start"]:
        return
    cell = syl["cell"]; cx, cy = syl["cx"], syl["cy"]
    local = t - syl["t_start"]
    fly = 0.55      # 자모당 비행 시간
    stag = 0.30     # 두 자모 간 시차
    morph_at = stag + fly + 0.05
    morph_dur = 0.32

    # 자모 서브 타깃 & 크기
    if syl["layout"] == "LR":
        cw, ch = cell * 0.46, cell * 0.82
        vw, vh = cell * 0.40, cell * 0.86
        cons_t = (cx - cell * 0.23, cy)
        vow_t  = (cx + cell * 0.25, cy)
    else:  # TB
        cw, ch = cell * 0.84, cell * 0.44
        vw, vh = cell * 0.86, cell * 0.40
        cons_t = (cx, cy - cell * 0.23)
        vow_t  = (cx, cy + cell * 0.25)

    cons_tile = block_tile(syl["cons"], cw, ch, CONS_COLOR)
    vow_tile  = block_tile(syl["vow"],  vw, vh, VOW_COLOR)
    syl_tile  = block_tile(syl["ch"], cell * 0.92, cell * 0.92, SYL_COLOR)

    m = clamp((local - morph_at) / morph_dur, 0, 1) if local >= morph_at else 0.0

    # 베이스플레이트(칸) 윤곽
    if local < morph_at + morph_dur:
        d = ImageDraw.Draw(base)
        hw = cell / 2
        d.rounded_rectangle([cx - hw, cy - hw, cx + hw, cy + hw],
                            radius=int(cell * 0.14), outline=(170, 175, 185, 180),
                            width=3)

    # 두 자모 비행/착지
    for j, (tile, tgt, ox_idx) in enumerate([(cons_tile, cons_t, global_idx * 2),
                                             (vow_tile, vow_t, global_idx * 2 + 1)]):
        jt = local - j * stag
        if jt < 0:
            continue
        p = clamp(jt / fly, 0, 1)
        e = ease_out_cubic(p)
        sx, sy = origin(ox_idx, *tgt)
        px = lerp(sx, tgt[0], e); py = lerp(sy, tgt[1], e)
        # 착지 직전 살짝 오버슈트 바운스
        if 0.75 < p < 1.0:
            py -= math.sin((p - 0.75) / 0.25 * math.pi) * cell * 0.06
        ang = (1 - e) * (150 if j == 0 else -150)
        paste_alpha(base, tile, px, py, factor=(1 - m), angle=ang)

    # 완성 글자 변신
    if m > 0:
        paste_alpha(base, syl_tile, cx, cy, factor=m)

# ---------- 완성된 단어(정적) 그리기 ----------
def draw_word_static(base, syls, scale=1.0, dy=0, alpha=1.0):
    for s in syls:
        cell = s["cell"] * scale
        tile = block_tile(s["ch"], cell * 0.92, cell * 0.92, SYL_COLOR)
        cx = W / 2 + (s["cx"] - W / 2) * scale
        paste_alpha(base, tile, cx, s["cy"] * 0 + (760 * 0) + (s["cy"]) , 1.0) if False else None
        paste_alpha(base, tile, cx, (s["cy"]) + dy, factor=alpha)

# ---------- 텍스트 라벨 ----------
def label(base, text, cy, size, color=INK, alpha=1.0):
    d = ImageDraw.Draw(base)
    f = font(size)
    bb = d.textbbox((0, 0), text, font=f)
    tw = bb[2] - bb[0]
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    dl.text(((W - tw) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), text,
            font=f, fill=color + (int(255 * alpha),))
    base.alpha_composite(layer)

# ---------- 배경 ----------
def make_bg():
    top = np.array([255, 250, 242]); bot = np.array([224, 236, 255])
    col = (top[None, :] + (bot - top)[None, :] * (np.linspace(0, 1, H)[:, None])).astype(np.uint8)
    bg = np.repeat(col[:, None, :], W, axis=1)
    return Image.fromarray(bg, "RGB").convert("RGBA")
BG = make_bg()

def zolla_bob(base, t, cheer=False):
    man = ZMAN_C if cheer else ZMAN
    nyeo = ZNYEO_C if cheer else ZNYEO
    by = int(math.sin(t * 2.4) * 7)
    by2 = int(math.sin(t * 2.4 + 1.2) * 7)
    base.alpha_composite(man, (40, H - man.height - 60 + by))
    base.alpha_composite(nyeo, (W - nyeo.width - 40, H - nyeo.height - 60 + by2))

# ---------- 프레임 ----------
def make_frame(t):
    base = BG.copy()
    cheer = t >= FIN_T0
    zolla_bob(base, t, cheer=cheer)

    # 타이틀
    ti_a = clamp(t / 0.6, 0, 1)
    label(base, "한글은 레고처럼!", 230, 96, color=(60, 60, 70), alpha=ti_a)
    label(base, "자모가 모여 한 글자가 돼요", 340, 50, color=(120, 120, 135), alpha=ti_a)

    if t < W1_HOLD_END:
        for i, s in enumerate(word1):
            draw_syllable(base, s, t, i)
        if t >= W1_LABEL:
            a = clamp((t - W1_LABEL) / 0.4, 0, 1)
            label(base, "BTS", 980, 110, color=(60, 60, 70), alpha=a)
            label(base, "비티에스", 1110, 56, color=(150, 150, 165), alpha=a)
    elif t < W2_HOLD_END:
        for i, s in enumerate(word2):
            draw_syllable(base, s, t, i)
        if t >= W2_LABEL:
            a = clamp((t - W2_LABEL) / 0.4, 0, 1)
            label(base, "dynamite", 980, 96, color=(60, 60, 70), alpha=a)
            label(base, "다이나마이트", 1110, 52, color=(150, 150, 165), alpha=a)
    else:
        # 피날레: 두 단어 작게 + 영어 라벨
        a = clamp((t - FIN_T0) / 0.5, 0, 1)
        for s in word1:
            tile = block_tile(s["ch"], 120 * 0.92, 120 * 0.92, SYL_COLOR)
            cx = W / 2 + (s["cx"] - W / 2) * 0.6
            paste_alpha(base, tile, cx, 640, factor=a)
        for s in word2:
            tile = block_tile(s["ch"], 120 * 0.92, 120 * 0.92, SYL_COLOR)
            cx = W / 2 + (s["cx"] - W / 2) * 0.78
            paste_alpha(base, tile, cx, 820, factor=a)
        label(base, "BTS  dynamite", 1010, 104, color=(50, 50, 60), alpha=a)
        label(base, "한글, 블록처럼 조립!", 1140, 56, color=(150, 120, 60), alpha=a)

    return np.array(base.convert("RGB"))

def main():
    os.makedirs(ODIR, exist_ok=True)
    print(f"타임라인: intro→비티에스({W1_T0:.1f}~{W1_END:.1f})→"
          f"다이나마이트({W2_T0:.1f}~{W2_END:.1f})→피날레({FIN_T0:.1f}) / 총 {DURATION:.1f}s")
    clip = VideoClip(make_frame, duration=DURATION)
    threads = os.cpu_count() or 4
    clip.write_videofile(OUT, fps=FPS, codec="libx264", audio=False,
                         threads=threads, preset="medium", bitrate="6000k")
    print(f"[OK] {OUT}")

if __name__ == "__main__":
    main()
