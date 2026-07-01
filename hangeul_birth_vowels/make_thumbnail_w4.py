#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_thumbnail_w4.py — 초급 4주차 "받침과 대표 7음" 썸네일 (ko/en).
받침=토대(흙/이끼 그린) 테마 + 대표 7음 7타일(ㄱㄴㄷㄹㅁㅂㅇ) + 예시단어 미니칩.
출력: web/public/docs/hangeul_w4_thumbnail_<lang>.png (1280x720)
재실행: python hangeul_birth_vowels/make_thumbnail_w4.py
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
TEAL = (38, 150, 138)        # 받침 = 든든한 토대
DEEP = (22, 92, 92)
INK = (34, 44, 44)
GRAY = (110, 120, 120)

REP = list("ㄱㄴㄷㄹㅁㅂㅇ")           # 대표 7음
TEXTS = {
    "ko": {"title": "받침과 대표 7음", "tsize": 74, "study": "한글 공부",
           "badge": "초급 · 4주차", "sub": "모든 받침은 일곱 소리로",
           "words": ["책", "산", "옷", "물", "곰", "밥", "강"]},
    "en": {"title": "Batchim & 7 Sounds", "tsize": 76, "study": "Learn Hangeul",
           "badge": "Beginner · Week 4", "sub": "Every final consonant = one of seven",
           "words": ["책", "산", "옷", "물", "곰", "밥", "강"]},
}


def bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(yy / H * 0.7 + xx / W * 0.3, 0, 1)[..., None]    # 위(밝은 민트)→아래(딥 틸)
    top = np.array([214, 240, 232], np.float32)
    bot = np.array([26, 104, 100], np.float32)
    img = top * (1 - g) + bot * g
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

    # 제목 (그림자 + 흰색)
    title = ImageFont.truetype(FONT_BD, cfg["tsize"])
    tw = d.textlength(cfg["title"], font=title)
    d.text((W / 2 - tw / 2 + 2, 50), cfg["title"], font=title, fill=(0, 0, 0))
    d.text((W / 2 - tw / 2, 48), cfg["title"], font=title, fill=WHITE)
    # 부제
    sub = ImageFont.truetype(FONT_BD, 30)
    center(d, W / 2, 152, cfg["sub"], sub, (224, 246, 240))
    # 배지(좌상) + 강조 리본(우상)
    bf = ImageFont.truetype(FONT_BD, 28)
    bw = d.textlength(cfg["badge"], font=bf)
    d.rounded_rectangle([40, 36, 40 + bw + 34, 82], radius=22, fill=GOLD + (255,))
    d.text((57, 42), cfg["badge"], font=bf, fill=(70, 52, 14))
    sf = ImageFont.truetype(FONT_BD, 32)
    label = "★ " + cfg["study"]
    sw = d.textlength(label, font=sf)
    d.rounded_rectangle([W - sw - 78, 34, W - 34, 86], radius=24, fill=(255, 255, 255, 235))
    d.text((W - sw - 60, 41), label, font=sf, fill=DEEP)

    # 히어로: 대표 7음 7타일 (ㄱㄴㄷㄹㅁㅂㅇ)
    cy = 372
    n = len(REP)
    s = 74
    gap = 24
    total = n * (2 * s) + (n - 1) * gap
    x = (W - total) / 2 + s
    for g in REP:
        tile(d, x, cy, s, g, WHITE, DEEP, 96)
        x += 2 * s + gap
    # 강조 받침 라벨
    capf = ImageFont.truetype(FONT_BD, 30)
    lab = "대표 7음" if lang == "ko" else "the 7 sounds"
    lw = d.textlength(lab, font=capf)
    d.rounded_rectangle([W / 2 - lw / 2 - 20, cy + 96, W / 2 + lw / 2 + 20, cy + 142], radius=22, fill=GOLD + (255,))
    center(d, W / 2, cy + 119, lab, capf, (70, 52, 14))

    # 하단 예시단어 미니칩 (책 산 옷 물 곰 밥 강)
    yb = 648
    wf = ImageFont.truetype(FONT_BD, 44)
    chips = cfg["words"]
    cw = 116
    totalw = len(chips) * cw
    x = (W - totalw) / 2 + cw / 2
    for w in chips:
        d.rounded_rectangle([x - 50, yb - 38, x + 50, yb + 38], radius=18, fill=(255, 255, 255, 235))
        center(d, x, yb, w, wf, TEAL)
        x += cw

    out = os.path.join(ROOT, "web", "public", "docs", f"hangeul_w4_thumbnail_{lang}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    base.convert("RGB").save(out)
    base.convert("RGB").save(os.path.join(ROOT, "scratch", f"_thumb_w4_{lang}.png"))
    print("thumbnail ->", out)


if __name__ == "__main__":
    for lg in (sys.argv[1:] or ["ko", "en"]):
        build(lg)
