# -*- coding: utf-8 -*-
"""졸라맨·졸라걸 Flow 기준 이미지 — W24R 가이드를 스틱맨 규격으로 맞춘다.

★사장님 지시(2026-08-12): "졸라맨 졸라걸 기준 이미지도 W24R 에 있을 것이다."
  → `W24R/guides/zollaman{,_side}.png` · `zollagirl{,_side}.png` 가 그것이다.
    이미 Flow 에서 나온 한 벌이라 **새로 만들지 않는다**(가이드 3종 Flow 통일 원칙).

다만 원본은 크기·여백이 제각각이다(정면은 세로 크롭, 측면은 16:9 안에 작게).
스틱맨 `guide_front.png`/`guide_side.png` 와 **같은 규격**으로 맞춰야 Flow 가
같은 크기의 인물을 낸다 — 1280x720 · 흰 배경 · 정중앙 · 인물 키 620px.

    python W1_2/make_zolla_guides.py
"""
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SRC = "W24R/guides"
DST = "W1_2/motion_src"
W, H = 1280, 720
FIG_H = 620                      # 스틱맨 guide_front.png 실측과 맞춘다

PAIRS = [
    ("zollaman", "zman_front"),
    ("zollaman_side", "zman_side"),
    ("zollagirl", "zgirl_front"),
    ("zollagirl_side", "zgirl_side"),
]


def flatten_white(p):
    """알파를 흰 바탕에 합성한다(색 소품이 검게 뭉개지지 않게 RGB 를 살린다)."""
    im = Image.open(p).convert("RGBA")
    a = np.asarray(im).astype(np.float32)
    rgb, al = a[:, :, :3], a[:, :, 3:4] / 255.0
    return Image.fromarray((255 * (1 - al) + rgb * al).astype(np.uint8), "RGB")


def normalize(src, dst):
    im = flatten_white(src)
    g = np.asarray(im.convert("L"))
    ys, xs = np.nonzero(g < 240)                  # 흰 배경이 아닌 것 = 인물
    if not len(xs):
        raise RuntimeError("인물을 못 찾음: " + src)
    im = im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    w = max(1, round(im.width * FIG_H / im.height))
    im = im.resize((w, FIG_H), Image.LANCZOS)
    cv = Image.new("RGB", (W, H), (255, 255, 255))
    cv.paste(im, ((W - w) // 2, (H - FIG_H) // 2))
    cv.save(dst)
    return w


def main():
    os.makedirs(DST, exist_ok=True)
    for a, b in PAIRS:
        s = os.path.join(SRC, a + ".png")
        d = os.path.join(DST, "guide_%s.png" % b)
        if not os.path.exists(s):
            print("  ★없음:", s)
            continue
        w = normalize(s, d)
        print("  %-16s → %-28s 인물 %dx%d · 캔버스 %dx%d" % (a, os.path.basename(d), w, FIG_H, W, H))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
