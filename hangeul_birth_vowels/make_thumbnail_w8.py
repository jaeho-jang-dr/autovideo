#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_thumbnail_w8.py — 초급 8주차 "숫자·날짜·시간" 썸네일 (ko/en).
졸라맨(zollaman) 캐릭터 합성 + 고유어/한자어 숫자 칩 + 요일 미니칩.
출력: web/public/docs/hangeul_w8_thumbnail_<lang>.png (1280x720)
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSES = os.path.join(ROOT, "assets", "graphics", "poses")
W, H = 1280, 720
FONT_BD = "C:/Windows/Fonts/malgunbd.ttf"
FONT = "C:/Windows/Fonts/malgun.ttf"
if not os.path.exists(FONT_BD):
    FONT_BD = FONT

WHITE = (255, 255, 255)
GOLD = (245, 205, 110)
BLUE = (58, 110, 196)        # 고유어
ORANGE = (220, 120, 54)      # 한자어
DEEP = (40, 52, 84)

TEXTS = {
    "ko": {"title": "숫자·날짜·시간", "tsize": 72, "study": "한글 공부",
           "badge": "초급 · 8주차", "sub": "숫자 두 가지로 날짜·시간까지!",
           "lab1": "고유어", "n1": "하나 둘 셋", "lab2": "한자어", "n2": "일 이 삼",
           "days": ["월", "화", "수", "목", "금", "토", "일"]},
    "en": {"title": "Numbers, Dates & Time", "tsize": 64, "study": "Learn Hangeul",
           "badge": "Beginner · Week 8", "sub": "Two number systems for dates & time!",
           "lab1": "native", "n1": "하나 둘 셋", "lab2": "Sino", "n2": "일 이 삼",
           "days": ["월", "화", "수", "목", "금", "토", "일"]},
}


def bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(xx / W * 0.5 + yy / H * 0.5, 0, 1)[..., None]
    a = np.array([224, 234, 248], np.float32)
    b = np.array([34, 48, 86], np.float32)
    img = a * (1 - g) + b * g
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def center(d, cx, cy, text, font, fill):
    b = d.textbbox((0, 0), text, font=font)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), text, font=font, fill=fill)


def chip(d, cx, cy, text, fill, tcol, fsize, padx=22, pady=11, radius=18):
    f = ImageFont.truetype(FONT_BD, fsize)
    tw = d.textlength(text, font=f)
    b = d.textbbox((0, 0), text, font=f)
    th = b[3] - b[1]
    d.rounded_rectangle([cx - tw / 2 - padx, cy - th / 2 - pady, cx + tw / 2 + padx, cy + th / 2 + pady],
                        radius=radius, fill=fill)
    center(d, cx, cy, text, f, tcol)


def build(lang):
    cfg = TEXTS[lang]
    base = bg()
    d = ImageDraw.Draw(base)

    title = ImageFont.truetype(FONT_BD, cfg["tsize"])
    tw = d.textlength(cfg["title"], font=title)
    d.text((W / 2 - tw / 2 + 2, 46), cfg["title"], font=title, fill=(0, 0, 0))
    d.text((W / 2 - tw / 2, 44), cfg["title"], font=title, fill=WHITE)
    sub = ImageFont.truetype(FONT_BD, 30)
    center(d, W / 2, 142, cfg["sub"], sub, (220, 232, 248))
    bf = ImageFont.truetype(FONT_BD, 28)
    bw = d.textlength(cfg["badge"], font=bf)
    d.rounded_rectangle([40, 34, 40 + bw + 34, 80], radius=22, fill=GOLD + (255,))
    d.text((57, 40), cfg["badge"], font=bf, fill=(70, 52, 14))
    sf = ImageFont.truetype(FONT_BD, 32)
    label = "★ " + cfg["study"]
    sw = d.textlength(label, font=sf)
    d.rounded_rectangle([W - sw - 78, 32, W - 34, 84], radius=24, fill=(255, 255, 255, 235))
    d.text((W - sw - 60, 39), label, font=sf, fill=DEEP)

    # 졸라맨 캐릭터 합성(왼쪽)
    for cand in ("stickman_zm_point_l.png", "stickman_zm_cheering.png", "stickman_zm_base.png"):
        p = os.path.join(POSES, cand)
        if os.path.exists(p):
            ch = Image.open(p).convert("RGBA")
            target_h = 420
            sc = target_h / ch.height
            ch = ch.resize((max(1, int(ch.width * sc)), target_h), Image.LANCZOS)
            cxp = 270
            sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).ellipse([cxp - 120, 620, cxp + 120, 660], fill=(0, 0, 0, 60))
            base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
            base.alpha_composite(ch, (int(cxp - ch.width / 2), int(640 - ch.height)))
            break

    # 두 숫자 체계 카드 (고유어 / 한자어)
    lf = ImageFont.truetype(FONT_BD, 30)
    nf = ImageFont.truetype(FONT_BD, 56)
    # 고유어 카드
    d.rounded_rectangle([540, 270, 900, 470], radius=26, fill=(255, 255, 255, 240))
    center(d, 720, 312, cfg["lab1"], lf, BLUE)
    center(d, 720, 400, cfg["n1"], nf, DEEP)
    # 한자어 카드
    d.rounded_rectangle([930, 270, 1240, 470], radius=26, fill=(255, 255, 255, 240))
    center(d, 1085, 312, cfg["lab2"], lf, ORANGE)
    center(d, 1085, 400, cfg["n2"], nf, DEEP)

    # 하단 요일 미니칩
    yb = 612
    s = 40
    gap = 16
    n = len(cfg["days"])
    total = n * (2 * s) + (n - 1) * gap
    x = 540 + s
    for g in cfg["days"]:
        chip(d, x, yb, g, (255, 255, 255, 235), DEEP, 44, padx=8, pady=8, radius=14)
        x += 2 * s + gap

    out = os.path.join(ROOT, "web", "public", "docs", f"hangeul_w8_thumbnail_{lang}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    base.convert("RGB").save(out)
    base.convert("RGB").save(os.path.join(ROOT, "scratch", f"_thumb_w8_{lang}.png"))
    print("thumbnail ->", out)


if __name__ == "__main__":
    for lg in (sys.argv[1:] or ["ko", "en"]):
        build(lg)
