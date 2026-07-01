#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_thumbnail_w3.py — 초급 3주차 썸네일 (ko/en). W1·W2와 완전히 다른 디자인:
따뜻(거센)↔차가운(된) 대각 그라데이션 + ㄱ→ㅋ→ㄲ 삼총사 타일 + '한글 공부' 강조 리본
+ 하단 거센(ㅋㅌㅍㅊ)·된(ㄲㄸㅃㅆㅉ) 미니 타일.
출력: web/public/docs/hangeul_w3_thumbnail_<lang>.png (1280x720)
"""
import os
import sys
import math

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
GOLD = (245, 198, 92)
CORAL = (236, 110, 74)      # 거센소리 — 따뜻한 바람
DEEPC = (200, 74, 52)
INDIGO = (84, 92, 196)      # 된소리 — 단단/긴장
DEEPI = (44, 50, 120)
GRAY = (120, 124, 132)

ASPIR = list("ㅋㅌㅍㅊ")
TENSE = list("ㄲㄸㅃㅆㅉ")
TEXTS = {
    "ko": {"title": "거센소리와 된소리", "tsize": 74, "study": "한글 공부",
           "badge": "초급 · 3주차", "sub": "거센소리 ㅋㅌㅍㅊ · 된소리 ㄲㄸㅃㅆㅉ",
           "lab": ["예사소리", "거센소리", "된소리"]},
    "en": {"title": "Aspirated & Tense", "tsize": 78, "study": "Learn Hangeul",
           "badge": "Beginner · Week 3", "sub": "Aspirated ㅋㅌㅍㅊ · Tense ㄲㄸㅃㅆㅉ",
           "lab": ["plain", "aspirated", "tense"]},
}


def bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(xx / W * 0.62 + yy / H * 0.38, 0, 1)[..., None]   # 좌상(따뜻)→우하(차가움) 대각
    warm = np.array([238, 126, 84], np.float32)
    cool = np.array([46, 52, 124], np.float32)
    img = warm * (1 - g) + cool * g
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def center(d, cx, cy, text, font, fill):
    b = d.textbbox((0, 0), text, font=font)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), text, font=font, fill=fill)


def tile(d, cx, cy, s, glyph, fill, gcol, fsize, radius=28, shadow=True):
    x0, y0, x1, y1 = cx - s, cy - s, cx + s, cy + s
    if shadow:
        d.rounded_rectangle([x0 + 7, y0 + 9, x1 + 7, y1 + 9], radius=radius, fill=(0, 0, 0, 75))
    d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)
    f = ImageFont.truetype(FONT_BD, fsize)
    center(d, cx, cy, glyph, f, gcol)


def airpuff(d, cx, cy):
    for k, rad in enumerate((24, 36, 50)):
        pts = []
        for i in range(16):
            a = (-0.6 + 1.2 * i / 15) * math.pi / 2
            pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
        d.line(pts, fill=(255, 255, 255, 220 - k * 40), width=4 - k)


def build(lang):
    cfg = TEXTS[lang]
    base = bg()
    d = ImageDraw.Draw(base)

    # 제목
    title = ImageFont.truetype(FONT_BD, cfg["tsize"])
    tw = d.textlength(cfg["title"], font=title)
    d.text((W / 2 - tw / 2 + 2, 46), cfg["title"], font=title, fill=(0, 0, 0))
    d.text((W / 2 - tw / 2, 44), cfg["title"], font=title, fill=WHITE)
    # 부제
    sub = ImageFont.truetype(FONT_BD, 30)
    center(d, W / 2, 150, cfg["sub"], sub, (255, 236, 224))
    # 배지(좌상) + '한글 공부' 강조 리본(우상)
    bf = ImageFont.truetype(FONT_BD, 28)
    bw = d.textlength(cfg["badge"], font=bf)
    d.rounded_rectangle([40, 36, 40 + bw + 34, 82], radius=22, fill=GOLD + (255,))
    d.text((57, 42), cfg["badge"], font=bf, fill=(60, 44, 12))
    sf = ImageFont.truetype(FONT_BD, 32)
    label = "★ " + cfg["study"]
    sw = d.textlength(label, font=sf)
    d.rounded_rectangle([W - sw - 78, 34, W - 34, 86], radius=24, fill=(255, 255, 255, 235))
    d.text((W - sw - 60, 41), label, font=sf, fill=DEEPI)

    # 히어로: ㄱ → ㅋ → ㄲ (예사·거센·된)
    cy = 392
    labf = ImageFont.truetype(FONT_BD, 28)
    cols = [(286, "ㄱ", (255, 255, 255, 255), GRAY, cfg["lab"][0]),
            (640, "ㅋ", CORAL + (255,), WHITE, cfg["lab"][1]),
            (994, "ㄲ", INDIGO + (255,), WHITE, cfg["lab"][2])]
    for cx, g, fill, gcol, lab in cols:
        tile(d, cx, cy, 108, g, fill, gcol, 170)
        # 라벨 칩
        lw = d.textlength(lab, font=labf)
        d.rounded_rectangle([cx - lw / 2 - 16, cy + 128, cx + lw / 2 + 16, cy + 170], radius=20, fill=(0, 0, 0, 110))
        center(d, cx, cy + 149, lab, labf, WHITE)
    # 화살표
    af = ImageFont.truetype(FONT_BD, 70)
    center(d, 463, cy, "→", af, GOLD)
    center(d, 817, cy, "→", af, GOLD)
    airpuff(d, 760, 330)        # 거센소리 타일 옆 공기 분출

    # 하단 미니 타일: 거센 ㅋㅌㅍㅊ | 된 ㄲㄸㅃㅆㅉ
    yb = 648
    x = 150
    for c in ASPIR:
        tile(d, x, yb, 36, c, CORAL + (255,), WHITE, 50, radius=14, shadow=False); x += 92
    x += 72
    d.line([(x - 40, yb - 40), (x - 40, yb + 40)], fill=(255, 255, 255, 120), width=3)
    for c in TENSE:
        tile(d, x, yb, 36, c, INDIGO + (255,), WHITE, 50, radius=14, shadow=False); x += 92

    out = os.path.join(ROOT, "web", "public", "docs", f"hangeul_w3_thumbnail_{lang}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    base.convert("RGB").save(out)
    base.convert("RGB").save(os.path.join(ROOT, "scratch", f"_thumb_w3_{lang}.png"))
    print("thumbnail ->", out)


if __name__ == "__main__":
    for lg in (sys.argv[1:] or ["ko", "en"]):
        build(lg)
