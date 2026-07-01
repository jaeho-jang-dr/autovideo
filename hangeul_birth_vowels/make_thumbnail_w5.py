#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_thumbnail_w5.py — 초급 5주차 "이중모음과 반모음 활주" 썸네일 (ko/en).
활주(glide) 테마: 보라-청록 흐름 그라데이션 + 합성 화살표(ㅣ→ㅑ, ㅗ+ㅏ→ㅘ) + 이중모음 미니칩.
출력: web/public/docs/hangeul_w5_thumbnail_<lang>.png (1280x720)
재실행: python hangeul_birth_vowels/make_thumbnail_w5.py
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1280, 720
FONT_BD = "C:/Windows/Fonts/malgunbd.ttf"
FONT = "C:/Windows/Fonts/malgun.ttf"
if not os.path.exists(FONT_BD):
    FONT_BD = FONT

WHITE = (255, 255, 255)
GOLD = (245, 205, 110)
PURP = (124, 92, 196)        # 반모음 글라이드
DEEP = (60, 48, 120)
TEAL = (38, 150, 138)
INK = (34, 34, 44)

DIPH = list("ㅑㅕㅛㅠ") + list("ㅘㅝㅟㅢ")
TEXTS = {
    "ko": {"title": "이중모음과 반모음 활주", "tsize": 66, "study": "한글 공부",
           "badge": "초급 · 5주차", "sub": "두 모음이 미끄러지면 한 소리"},
    "en": {"title": "Double Vowels & Glides", "tsize": 72, "study": "Learn Hangeul",
           "badge": "Beginner · Week 5", "sub": "Two vowels glide into one sound"},
}


def bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(xx / W * 0.5 + yy / H * 0.5, 0, 1)[..., None]   # 보라(좌상)→청록(우하) 흐름
    a = np.array([222, 214, 244], np.float32)
    b = np.array([30, 112, 110], np.float32)
    img = a * (1 - g) + b * g
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def center(d, cx, cy, text, font, fill):
    b = d.textbbox((0, 0), text, font=font)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), text, font=font, fill=fill)


def tile(d, cx, cy, s, glyph, fill, gcol, fsize, radius=22, shadow=True):
    x0, y0, x1, y1 = cx - s, cy - s, cx + s, cy + s
    if shadow:
        d.rounded_rectangle([x0 + 6, y0 + 8, x1 + 6, y1 + 8], radius=radius, fill=(0, 0, 0, 70))
    d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)
    f = ImageFont.truetype(FONT_BD, fsize)
    center(d, cx, cy, glyph, f, gcol)


def build(lang):
    cfg = TEXTS[lang]
    base = bg()
    d = ImageDraw.Draw(base)

    title = ImageFont.truetype(FONT_BD, cfg["tsize"])
    tw = d.textlength(cfg["title"], font=title)
    d.text((W / 2 - tw / 2 + 2, 50), cfg["title"], font=title, fill=(0, 0, 0))
    d.text((W / 2 - tw / 2, 48), cfg["title"], font=title, fill=WHITE)
    sub = ImageFont.truetype(FONT_BD, 30)
    center(d, W / 2, 146, cfg["sub"], sub, (235, 230, 248))
    bf = ImageFont.truetype(FONT_BD, 28)
    bw = d.textlength(cfg["badge"], font=bf)
    d.rounded_rectangle([40, 36, 40 + bw + 34, 82], radius=22, fill=GOLD + (255,))
    d.text((57, 42), cfg["badge"], font=bf, fill=(70, 52, 14))
    sf = ImageFont.truetype(FONT_BD, 32)
    label = "★ " + cfg["study"]
    sw = d.textlength(label, font=sf)
    d.rounded_rectangle([W - sw - 78, 34, W - 34, 86], radius=24, fill=(255, 255, 255, 235))
    d.text((W - sw - 60, 41), label, font=sf, fill=DEEP)

    # 히어로: 두 개의 합성 화살표 — ㅣ→ㅑ (y활음), ㅗ+ㅏ→ㅘ (w활음)
    cy = 370
    af = ImageFont.truetype(FONT_BD, 64)
    # y-glide: ㅣ → ㅑ
    tile(d, 250, cy, 70, "ㅣ", WHITE, PURP, 96)
    center(d, 372, cy, "→", af, GOLD)
    tile(d, 494, cy, 70, "ㅑ", PURP + (255,), WHITE, 96)
    # w-glide: ㅗ + ㅏ → ㅘ
    tile(d, 700, cy, 60, "ㅗ", WHITE, TEAL, 80)
    center(d, 800, cy, "+", af, (90, 90, 110))
    tile(d, 900, cy, 60, "ㅏ", WHITE, TEAL, 80)
    center(d, 1000, cy, "→", af, GOLD)
    tile(d, 1110, cy, 70, "ㅘ", TEAL + (255,), WHITE, 92)
    # 라벨
    lf = ImageFont.truetype(FONT_BD, 26)
    center(d, 372, cy + 118, "ㅣ" + (" 활음" if lang == "ko" else "-glide"), lf, (60, 48, 120))
    center(d, 900, cy + 118, "ㅗ/ㅜ" + (" 활음" if lang == "ko" else "-glide"), lf, (20, 90, 86))

    # 하단 이중모음 미니칩
    yb = 648
    s = 40
    gap = 18
    total = len(DIPH) * (2 * s) + (len(DIPH) - 1) * gap
    x = (W - total) / 2 + s
    for g in DIPH:
        tile(d, x, yb, s, g, (255, 255, 255, 235), DEEP, 52, radius=14, shadow=False)
        x += 2 * s + gap

    out = os.path.join(ROOT, "web", "public", "docs", f"hangeul_w5_thumbnail_{lang}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    base.convert("RGB").save(out)
    base.convert("RGB").save(os.path.join(ROOT, "scratch", f"_thumb_w5_{lang}.png"))
    print("thumbnail ->", out)


if __name__ == "__main__":
    for lg in (sys.argv[1:] or ["ko", "en"]):
        build(lg)
