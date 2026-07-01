#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_thumbnail_w6.py — 초급 6주차 "연음과 음운 변동" 썸네일 (ko/en).
★ 졸라맨(zollaman) 캐릭터를 실제로 합성해 노출(사용자 요청). 연음 화살표(음악→으막) + 표기/발음 칩.
출력: web/public/docs/hangeul_w6_thumbnail_<lang>.png (1280x720)
재실행: python hangeul_birth_vowels/make_thumbnail_w6.py
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
POSES = os.path.join(ROOT, "assets", "graphics", "poses")
W, H = 1280, 720
FONT_BD = "C:/Windows/Fonts/malgunbd.ttf"
FONT = "C:/Windows/Fonts/malgun.ttf"
if not os.path.exists(FONT_BD):
    FONT_BD = FONT

WHITE = (255, 255, 255)
GOLD = (245, 205, 110)
CORAL = (232, 116, 86)       # 표기형
GREEN = (46, 150, 110)       # 발음형
DEEP = (44, 60, 90)
INK = (34, 34, 44)

TEXTS = {
    "ko": {"title": "연음과 음운 변동", "tsize": 70, "study": "한글 공부",
           "badge": "초급 · 6주차", "sub": "받침이 넘어가 자연스럽게!",
           "spell": "음악", "sound": "으막", "lab1": "표기형", "lab2": "발음형",
           "chips": [("옷이", "오시"), ("꽃이", "꼬치"), ("좋아요", "조아요")]},
    "en": {"title": "Liaison & Sound Rules", "tsize": 72, "study": "Learn Hangeul",
           "badge": "Beginner · Week 6", "sub": "Batchim glides over — naturally!",
           "spell": "음악", "sound": "으막", "lab1": "spelling", "lab2": "sound",
           "chips": [("옷이", "오시"), ("꽃이", "꼬치"), ("좋아요", "조아요")]},
}


def bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(xx / W * 0.45 + yy / H * 0.55, 0, 1)[..., None]   # 살구→남색 흐름(이어짐 느낌)
    a = np.array([248, 232, 214], np.float32)
    b = np.array([40, 64, 104], np.float32)
    img = a * (1 - g) + b * g
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def center(d, cx, cy, text, font, fill):
    b = d.textbbox((0, 0), text, font=font)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), text, font=font, fill=fill)


def chip(d, cx, cy, text, fill, tcol, fsize, padx=26, pady=12, radius=20):
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

    # 제목 + 부제 + 배지/리본
    title = ImageFont.truetype(FONT_BD, cfg["tsize"])
    tw = d.textlength(cfg["title"], font=title)
    d.text((W / 2 - tw / 2 + 2, 46), cfg["title"], font=title, fill=(0, 0, 0))
    d.text((W / 2 - tw / 2, 44), cfg["title"], font=title, fill=WHITE)
    sub = ImageFont.truetype(FONT_BD, 30)
    center(d, W / 2, 142, cfg["sub"], sub, (250, 226, 198))
    bf = ImageFont.truetype(FONT_BD, 28)
    bw = d.textlength(cfg["badge"], font=bf)
    d.rounded_rectangle([40, 34, 40 + bw + 34, 80], radius=22, fill=GOLD + (255,))
    d.text((57, 40), cfg["badge"], font=bf, fill=(70, 52, 14))
    sf = ImageFont.truetype(FONT_BD, 32)
    label = "★ " + cfg["study"]
    sw = d.textlength(label, font=sf)
    d.rounded_rectangle([W - sw - 78, 32, W - 34, 84], radius=24, fill=(255, 255, 255, 235))
    d.text((W - sw - 60, 39), label, font=sf, fill=DEEP)

    # ★ 졸라맨 캐릭터 합성(왼쪽) — 사용자 요청: 썸네일에 졸라맨 노출
    for cand in ("stickman_zm_point_l.png", "stickman_zm_cheering.png", "stickman_zm_base.png"):
        p = os.path.join(POSES, cand)
        if os.path.exists(p):
            ch = Image.open(p).convert("RGBA")
            target_h = 420
            scale = target_h / ch.height
            ch = ch.resize((max(1, int(ch.width * scale)), target_h), Image.LANCZOS)
            # 발밑 그림자
            sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
            sd = ImageDraw.Draw(sh)
            cxp = 250
            sd.ellipse([cxp - 120, 620, cxp + 120, 660], fill=(0, 0, 0, 60))
            base.alpha_composite(sh.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(8)))
            base.alpha_composite(ch, (int(cxp - ch.width / 2), int(640 - ch.height)))
            break

    # 연음 핵심: 음악 → 으막 (큰 화살표)
    cy = 350
    af = ImageFont.truetype(FONT_BD, 72)
    chip(d, 640, cy, cfg["spell"], CORAL + (255,), WHITE, 88, padx=30, pady=16, radius=26)
    center(d, 820, cy, "→", af, GOLD)
    chip(d, 1010, cy, cfg["sound"], GREEN + (255,), WHITE, 88, padx=30, pady=16, radius=26)
    lf = ImageFont.truetype(FONT_BD, 26)
    center(d, 640, cy + 96, cfg["lab1"], lf, (250, 226, 198))
    center(d, 1010, cy + 96, cfg["lab2"], lf, (210, 240, 224))

    # 하단 미니 표기/발음 칩들
    yb = 600
    xs = [560, 820, 1080]
    for (sp, so), x in zip(cfg["chips"], xs):
        chip(d, x, yb, f"{sp}→{so}", (255, 255, 255, 235), DEEP, 40, padx=18, pady=10, radius=16)

    out = os.path.join(ROOT, "web", "public", "docs", f"hangeul_w6_thumbnail_{lang}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    base.convert("RGB").save(out)
    base.convert("RGB").save(os.path.join(ROOT, "scratch", f"_thumb_w6_{lang}.png"))
    print("thumbnail ->", out)


if __name__ == "__main__":
    for lg in (sys.argv[1:] or ["ko", "en"]):
        build(lg)
