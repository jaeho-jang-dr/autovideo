#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_intermediate_thumbs.py — 중급 1~7주(W9-15) 썸네일 (ko/en), 캐릭터 없음(사용자 요청).
제목 + 어휘 칩 그리드 중심의 깔끔한 디자인. 주차별 색 테마.
출력: web/public/docs/hangeul_w{N}_thumbnail_{lang}.png (1280x720)
재실행: python make_intermediate_thumbs.py [week ...]
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_intermediate import WEEKS

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H = 1280, 720
FONT_BD = "C:/Windows/Fonts/malgunbd.ttf" if os.path.exists("C:/Windows/Fonts/malgunbd.ttf") else "C:/Windows/Fonts/malgun.ttf"
WHITE = (255, 255, 255)
GOLD = (245, 205, 110)

# 주차별 (밝은 top, 진한 bottom, accent)
THEME = {
    9:  ((214, 240, 232), (26, 104, 100), (30, 120, 112)),
    10: ((250, 226, 230), (150, 40, 70), (190, 60, 90)),
    11: ((252, 232, 214), (150, 70, 24), (200, 100, 40)),
    12: ((222, 226, 248), (44, 50, 120), (70, 80, 170)),
    13: ((224, 244, 226), (28, 96, 52), (40, 140, 80)),
    14: ((232, 222, 244), (70, 44, 110), (110, 70, 160)),
    15: ((216, 234, 248), (34, 70, 120), (50, 110, 170)),
    16: ((244, 236, 220), (120, 84, 24), (170, 120, 40)),
    # 고급(W17-24)
    17: ((248, 224, 238), (120, 30, 90), (170, 50, 120)),
    18: ((230, 236, 250), (40, 60, 130), (70, 90, 180)),
    19: ((224, 242, 238), (24, 100, 92), (40, 140, 124)),
    20: ((250, 230, 220), (150, 60, 40), (200, 90, 60)),
    21: ((234, 228, 248), (74, 48, 120), (114, 78, 168)),
    22: ((220, 240, 230), (30, 100, 70), (48, 142, 100)),
    23: ((220, 232, 248), (34, 64, 120), (52, 102, 170)),
    24: ((250, 236, 210), (140, 96, 20), (196, 140, 40)),
}
EN_TITLE_SIZE = {9: 64, 10: 64, 11: 60, 12: 58, 13: 62, 14: 64, 15: 56, 16: 60,
                 17: 58, 18: 56, 19: 60, 20: 52, 21: 60, 22: 66, 23: 64, 24: 56}


def center(d, cx, cy, text, font, fill):
    b = d.textbbox((0, 0), text, font=font)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), text, font=font, fill=fill)


def chip(d, cx, cy, text, fill, tcol, fsize, padx=26, pady=14, radius=22):
    f = ImageFont.truetype(FONT_BD, fsize)
    tw = d.textlength(text, font=f)
    b = d.textbbox((0, 0), text, font=f)
    th = b[3] - b[1]
    d.rounded_rectangle([cx - tw / 2 - padx, cy - th / 2 - pady, cx + tw / 2 + padx, cy + th / 2 + pady],
                        radius=radius, fill=fill)
    center(d, cx, cy, text, f, tcol)


def build(week, lang):
    cfg = WEEKS[week]
    top, bot, accent = THEME[week]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(xx / W * 0.5 + yy / H * 0.5, 0, 1)[..., None]
    img = (np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g)
    base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(base)

    title = cfg["title_ko"] if lang == "ko" else cfg["title_en"]
    tsize = 70 if lang == "ko" else EN_TITLE_SIZE.get(week, 60)
    tf = ImageFont.truetype(FONT_BD, tsize)
    tw = d.textlength(title, font=tf)
    d.text((W / 2 - tw / 2 + 2, 78), title, font=tf, fill=(0, 0, 0))
    d.text((W / 2 - tw / 2, 76), title, font=tf, fill=WHITE)
    # subtitle (hook, ko only meaningful; en use title_en already shown -> use a generic en sub)
    sub = cfg["hook_ko"] if lang == "ko" else "Learn the key words for this lesson"
    sf = ImageFont.truetype(FONT_BD, 28)
    center(d, W / 2, 210, sub, sf, tuple(min(255, c + 150) for c in bot))

    # badge + 강조
    bf = ImageFont.truetype(FONT_BD, 30)
    lvl_ko, lvl_en, n = ("고급", "Advanced", week - 16) if week >= 17 else ("중급", "Intermediate", week - 8)
    badge = f"{lvl_ko} · {n}주차" if lang == "ko" else f"{lvl_en} · Week {n}"
    bw = d.textlength(badge, font=bf)
    d.rounded_rectangle([40, 36, 40 + bw + 36, 86], radius=24, fill=GOLD + (255,))
    d.text((58, 43), badge, font=bf, fill=(70, 52, 14))
    sff = ImageFont.truetype(FONT_BD, 32)
    lab = "★ 한글 공부" if lang == "ko" else "★ Learn Hangeul"
    sw = d.textlength(lab, font=sff)
    d.rounded_rectangle([W - sw - 80, 34, W - 34, 88], radius=24, fill=(255, 255, 255, 235))
    d.text((W - sw - 62, 42), lab, font=sff, fill=bot)

    # 어휘 칩 그리드 (캐릭터 자리 대신 화면 가득)
    words = [v[0] for v in cfg["vocab"]]
    n = len(words)
    cols = 2 if n <= 4 else 3
    rows = (n + cols - 1) // cols
    cw, ch = 360, 130
    gx = (W - cols * cw) / 2 + cw / 2
    gy = 320
    fs = 52 if max(len(w.replace(" ", "")) for w in words) <= 3 else 40
    for i, wd in enumerate(words):
        r, c = divmod(i, cols)
        x = gx + c * cw
        y = gy + r * ch
        chip(d, x, y, wd, (255, 255, 255, 240), accent, fs, padx=22, pady=14, radius=20)

    out = os.path.join(ROOT, "web", "public", "docs", f"hangeul_w{week}_thumbnail_{lang}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    base.convert("RGB").save(out)
    print("thumb ->", os.path.basename(out))


def main():
    weeks = [int(a) for a in sys.argv[1:]] or list(range(9, 16))
    for w in weeks:
        for lang in ("ko", "en"):
            build(w, lang)


if __name__ == "__main__":
    main()
