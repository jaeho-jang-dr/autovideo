#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_thumbnail_w2.py — 초급 2주차 썸네일 (ko/en). W1과 완전히 다른 디자인:
볼드한 청록 배경 + 모아쓰기 블록(ㄱ+ㅏ→가)이 주인공 + 하단 자음 10자 타일. 스틱맨 없음.
출력: web/public/docs/hangeul_w2_thumbnail_<lang>.png (1280x720)
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
INK = (32, 40, 44)
GOLD = (245, 196, 90)
CORAL = (240, 120, 90)
TEAL = (40, 170, 160)
CONS = list("ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅎ")
TEXTS = {
    "ko": {"title": "기초 자음과 모아쓰기", "tsize": 72, "sub": "Basic Consonants & Syllable Blocks", "badge": "초급 · 2주차"},
    "en": {"title": "Consonants & Syllable Blocks", "tsize": 62, "sub": "기초 자음과 모아쓰기 · Beginner Week 2", "badge": "Beginner · Week 2"},
}


def bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = (xx / W * 0.5 + yy / H * 0.5)[..., None]
    top = np.array([26, 142, 134], np.float32)      # teal
    bot = np.array([14, 92, 92], np.float32)        # deep teal
    img = top * (1 - g) + bot * g
    # 가벼운 중앙 하이라이트
    dx = (xx - W / 2) / (W / 2); dy = (yy - H * 0.46) / (H / 2)
    r = np.clip(1 - np.sqrt(dx * dx + dy * dy), 0, 1)[..., None]
    img = img + r * 26
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def tile(d, cx, cy, s, glyph, fill, gcol, fsize, radius=26, shadow=True):
    x0, y0, x1, y1 = cx - s, cy - s, cx + s, cy + s
    if shadow:
        d.rounded_rectangle([x0 + 8, y0 + 10, x1 + 8, y1 + 10], radius=radius, fill=(0, 0, 0, 70))
    d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)
    f = ImageFont.truetype(FONT_BD, fsize)
    b = d.textbbox((0, 0), glyph, font=f)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), glyph, font=f, fill=gcol)


def sym(d, cx, cy, ch, size, col):
    f = ImageFont.truetype(FONT_BD, size)
    b = d.textbbox((0, 0), ch, font=f)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), ch, font=f, fill=col)


def build(lang):
    cfg = TEXTS[lang]
    base = bg()
    d = ImageDraw.Draw(base)

    # 상단 제목 (밝은 배경 위 흰 글씨)
    title = ImageFont.truetype(FONT_BD, cfg["tsize"])
    sub = ImageFont.truetype(FONT_BD, 32)
    badge = ImageFont.truetype(FONT_BD, 30)
    tw = d.textlength(cfg["title"], font=title)
    d.text((W / 2 - tw / 2 + 2, 52), cfg["title"], font=title, fill=(0, 60, 58))     # shadow
    d.text((W / 2 - tw / 2, 50), cfg["title"], font=title, fill=(255, 255, 255))
    sw = d.textlength(cfg["sub"], font=sub)
    d.text((W / 2 - sw / 2, 138), cfg["sub"], font=sub, fill=(206, 240, 236))
    bw = d.textlength(cfg["badge"], font=badge)
    d.rounded_rectangle([40, 38, 40 + bw + 36, 86], radius=23, fill=(GOLD + (255,)))
    d.text((58, 44), cfg["badge"], font=badge, fill=(60, 44, 12))

    # 중앙 히어로: 모아쓰기 ㄱ + ㅏ → 가
    cy = 400
    tile(d, 300, cy, 95, "ㄱ", (255, 255, 255, 255), CORAL, 150)
    sym(d, 445, cy, "+", 86, (255, 255, 255))
    tile(d, 590, cy, 95, "ㅏ", (255, 255, 255, 255), TEAL, 150)
    sym(d, 748, cy, "→", 92, GOLD)
    tile(d, 940, cy, 120, "가", (GOLD + (255,)), (60, 44, 12), 200)

    # 하단: 자음 10자 미니 타일
    n = len(CONS); tw2 = 96; x0 = W / 2 - (n * tw2) / 2 + tw2 / 2
    for i, c in enumerate(CONS):
        tile(d, int(x0 + i * tw2), 640, 40, c, (255, 255, 255, 235), INK, 56, radius=14, shadow=False)

    out = os.path.join(ROOT, "web", "public", "docs", f"hangeul_w2_thumbnail_{lang}.png")
    base.convert("RGB").save(out)
    base.convert("RGB").save(os.path.join(ROOT, "scratch", f"_thumb_w2_{lang}.png"))
    print("thumbnail ->", out)


if __name__ == "__main__":
    for lg in (sys.argv[1:] or ["ko", "en"]):
        build(lg)
