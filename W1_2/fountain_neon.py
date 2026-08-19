# -*- coding: utf-8 -*-
"""한글분수 네온 씬 — **훈민정음 28자를 14자씩 두 판**으로 썼다가 물방울로 흩는다.

★사장님 지시(2026-08-14)
  "배경은 이미 만들어진 8초짜리 두 번 쓰던지 해서 분수 계속 나오게 하고 네온으로."
  "W24에서 본 스틱맨 네온처럼 나오면 좋은데."
  "실제로 광화문 광장 분수에 나오는 글자를 그대로 표현해."
  "물이 표현하는 것이니 글자가 만들어졌다가 물방울 흩어지듯이 흩어지게."
  "여러 자를 한꺼번에 썼다가 지웠다가 해야 한다. 14자면 천천히 보여 주고 두 번 쓰면."
  "모음 10개, 안 쓰는 것 4개 같이 하고, 자음 하고 해 보자."

## 왜 28자인가
광화문광장 한글분수는 물줄기가 글자를 만드는 게 아니라, 바닥 노즐 225개가
천(○)·지(□)·인(△) 모양으로 깔려 **노즐 배열 자체가 훈민정음 28자**다.
그래서 여기서도 28자를 그대로 켠다. 옛 글자 넷은 `old_jamo` 가 획 표에 얹는다.

  1판 — 자음 14자          ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ
  2판 — 모음 10 + 옛 4자   ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ + ㆍㅿㆁㆆ

## 한 판이 도는 차례
  ① 한 자씩 **획순대로** 켜 나간다 — 켠 글자는 그대로 남아 판이 채워진다
  ② 열넷이 다 켜지면 한 번 환하게 부푼다
  ③ **물방울로 흩어진다** — 획에서 방울을 떠 위로 튀었다가 떨어지며 사그라진다

## 배경
`perf_hangeul_fountain.mp4` 8초를 **앞으로 + 거꾸로**로 이어 물기둥이 안 끊기게 한다.
밤은 배경을 눌러 깔아(어둡게 + 푸른 기) 만들고, 네온은 그 위에 더하기로 얹는다.

    python W1_2/fountain_neon.py
"""
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

import old_jamo                                             # noqa: E402,F401  옛 글자 등록
from neon_hangeul import neon, neon_syllable                # noqa: E402

BG = "W1_2/bg/perf_hangeul_fountain.mp4"
OUT = "W1_2/motion6/fountain_neon.mp4"
TMP = "W1_2/_neon"
W, H, FPS = 1280, 720, 24

CYAN = ((255, 255, 255), (150, 245, 255), (0, 190, 235))    # 스틱맨 — W24 청록
WATER = ((255, 255, 255), (150, 235, 255), (30, 130, 255))  # 자모 — 물빛

PANELS = [("자음 14자", "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ"),
          ("모음 10 + 옛 4자", "ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣㆍㅿㆁㆆ")]

CUTS = "W1_2/motion6_cuts/reach_catch"
FOOT_Y, CHAR_H = 690, 300

COLS, CELL = 7, 150                      # 7칸 × 2줄 = 14자
GRID_X, GRID_Y = 210, 150                # 가운데 빈 자리에 판을 놓는다

WRITE = 0.42                             # 한 자 쓰는 데 걸리는 시간
HOLD = 1.1                               # 다 켜 놓고 머무는 시간
BURST = 1.6                              # 물방울로 흩어지는 시간
LEAD = 1.2                               # 판이 시작하기 전 뜸
DROPS = 900                              # 한 판에서 떠내는 물방울 수


def night(im):
    a = np.asarray(im, np.float32) * np.array([0.34, 0.40, 0.55], np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def bg_frames():
    d = os.path.join(TMP, "bg")
    os.makedirs(d, exist_ok=True)
    if len(glob.glob(os.path.join(d, "*.png"))) != 192:
        for f in glob.glob(os.path.join(d, "*.png")):
            os.remove(f)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", BG,
                        os.path.join(d, "f%03d.png")], check=True)
    fs = sorted(glob.glob(os.path.join(d, "*.png")))
    return fs + fs[::-1]


def cell_xy(i):
    return GRID_X + (i % COLS) * CELL, GRID_Y + (i // COLS) * CELL


def panel_alpha(jamo, upto, prog_last):
    """판 한 장의 알파 — 앞의 글자는 다 켜져 있고, 지금 글자만 획이 자란다."""
    m = Image.new("L", (W, H), 0)
    for i, ch in enumerate(jamo):
        if i > upto:
            break
        p = 1.0 if i < upto else prog_last
        if p <= 0:
            continue
        im = neon_syllable(ch, CELL - 16, p, WATER)          # 알파만 쓸 것이라 색은 무관
        x, y = cell_xy(i)
        m.paste(Image.fromarray(np.asarray(im)[:, :, 3], "L"), (x, y),
                Image.fromarray(np.asarray(im)[:, :, 3], "L"))
    return np.asarray(m)


def make_drops(alpha, seed):
    """다 켜진 판에서 **물방울을 떠낸다** — 획 위에서 고르게 집는다."""
    ys, xs = np.nonzero(alpha > 120)
    if not len(xs):
        return None
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(xs), size=min(DROPS, len(xs)), replace=False)
    px = xs[idx].astype(np.float32)
    py = ys[idx].astype(np.float32)
    cx, cy = px.mean(), py.mean()
    ang = np.arctan2(py - cy, px - cx)
    sp = rng.uniform(40, 210, len(px))
    vx = np.cos(ang) * sp + rng.normal(0, 26, len(px))
    vy = np.sin(ang) * sp * 0.5 - rng.uniform(90, 260, len(px))   # 위로 먼저 튄다
    r = rng.uniform(1.6, 4.2, len(px))
    return px, py, vx, vy, r


def draw_drops(d, t):
    """t초 뒤의 물방울 — 위로 튀었다가 중력에 떨어지며 사그라진다."""
    px, py, vx, vy, r = d
    G = 520.0
    x = px + vx * t
    y = py + vy * t + 0.5 * G * t * t
    m = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(m)
    keep = (y < H + 40) & (x > -40) & (x < W + 40)
    for xi, yi, ri in zip(x[keep], y[keep], r[keep]):
        dr.ellipse([xi - ri, yi - ri, xi + ri, yi + ri], fill=255)
    return np.asarray(m)


def char_neon(path, h):
    """★좌우를 뒤집어 쓴다 — 팔이 **글자 쪽(오른편)으로** 올라가야 한다.

    `reach_catch` 원본은 왼쪽으로 팔을 훑는다. 캐릭터는 화면 왼편에 서고 글자판은
    오른편에 뜨므로, 그대로 쓰면 글자 반대편으로 팔을 뻗는다. 방향이 배치의
    출발점이라 여기서 뒤집어 둔다.
    """
    im = ImageOps.mirror(Image.open(path).convert("RGBA"))
    k = h / float(im.height)
    im = im.resize((max(1, round(im.width * k)), h), Image.LANCZOS)
    return neon(np.asarray(im)[:, :, 3], CYAN, max(2, h // 90), max(6, h // 26))


def main():
    bgs = bg_frames()
    cuts = sorted(glob.glob(os.path.join(CUTS, "*.png")))
    od = os.path.join(TMP, "out")
    os.makedirs(od, exist_ok=True)
    for f in glob.glob(os.path.join(od, "*.png")):
        os.remove(f)

    span = LEAD + 14 * WRITE + HOLD + BURST
    total = span * len(PANELS) + 0.8
    n = int(round(total * FPS))
    print("한 판 %.1f초 (뜸 %.1f + 쓰기 %.1f + 머무름 %.1f + 흩어짐 %.1f) × %d판 → %.1f초"
          % (span, LEAD, 14 * WRITE, HOLD, BURST, len(PANELS), total))

    drops = {}
    for i in range(n):
        t = i / float(FPS)
        cv = night(Image.open(bgs[i % len(bgs)]).convert("RGB")).convert("RGBA")
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        pi = min(len(PANELS) - 1, int(t / span))
        u = t - pi * span
        name, jamo = PANELS[pi]

        # ── 스틱맨 — 글자를 쓰는 동안 팔을 훑어 올린다
        if LEAD <= u < LEAD + 14 * WRITE:
            f = ((u - LEAD) % WRITE) / WRITE
            ci = 12 + int(f * 18)
        else:
            ci = 0
        ch = char_neon(cuts[min(ci, len(cuts) - 1)], CHAR_H)
        lay.paste(ch, (140 - ch.width // 2, FOOT_Y - ch.height), ch)

        # ── 판
        w_end = LEAD + 14 * WRITE
        if LEAD <= u < w_end:                               # ① 한 자씩 획순대로
            k = int((u - LEAD) / WRITE)
            a = panel_alpha(jamo, k, min(1.0, ((u - LEAD) % WRITE) / (WRITE * 0.8)))
            g = 1.0
        elif u < w_end + HOLD:                              # ② 다 켜 놓고 부푼다
            a = panel_alpha(jamo, 13, 1.0)
            g = 1.0 + 0.9 * ((u - w_end) / HOLD)
        elif u < w_end + HOLD + BURST:                      # ③ 물방울로 흩어진다
            if pi not in drops:
                drops[pi] = make_drops(panel_alpha(jamo, 13, 1.0), pi)
            dt = u - (w_end + HOLD)
            a = draw_drops(drops[pi], dt) if drops[pi] else None
            g = max(0.0, 1.9 * (1.0 - dt / BURST))
        else:
            a, g = None, 0.0

        if a is not None and g > 0.02:
            lay = Image.alpha_composite(lay, neon(a, WATER, 5, 20, g))

        Image.alpha_composite(cv, lay).convert("RGB").save(
            os.path.join(od, "f%03d.png" % i))

    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(od, "f%03d.png"), "-c:v", "libx264",
                    "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    OUT], check=True)
    print("%s  %d프레임 · %dfps · %.1f초" % (OUT, n, FPS, n / float(FPS)))


if __name__ == "__main__":
    main()
