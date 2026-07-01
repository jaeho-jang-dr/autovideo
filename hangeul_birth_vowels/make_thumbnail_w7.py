#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_thumbnail_w7.py — 초급 7주차 "인사말과 자기소개" 썸네일 (ko/en).
졸라걸(zollanyeo) 캐릭터 합성 + 말풍선 인사말(안녕하세요) + 자기소개 칩.
출력: web/public/docs/hangeul_w7_thumbnail_<lang>.png (1280x720)
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
ROSE = (224, 96, 110)
DEEP = (60, 40, 78)
TEAL = (38, 150, 138)

TEXTS = {
    "ko": {"title": "인사말과 자기소개", "tsize": 70, "study": "한글 공부",
           "badge": "초급 · 7주차", "sub": "인사 한마디로 마음이 가까워져요",
           "hello": "안녕하세요!", "chips": ["감사합니다", "반갑습니다", "저는 ~입니다"]},
    "en": {"title": "Greetings & Intro", "tsize": 74, "study": "Learn Hangeul",
           "badge": "Beginner · Week 7", "sub": "One greeting brings hearts closer",
           "hello": "안녕하세요!", "chips": ["감사합니다", "반갑습니다", "저는 ~입니다"]},
}


def bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(xx / W * 0.5 + yy / H * 0.5, 0, 1)[..., None]
    a = np.array([255, 238, 224], np.float32)
    b = np.array([86, 54, 110], np.float32)
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
    center(d, W / 2, 142, cfg["sub"], sub, (255, 228, 210))
    bf = ImageFont.truetype(FONT_BD, 28)
    bw = d.textlength(cfg["badge"], font=bf)
    d.rounded_rectangle([40, 34, 40 + bw + 34, 80], radius=22, fill=GOLD + (255,))
    d.text((57, 40), cfg["badge"], font=bf, fill=(70, 52, 14))
    sf = ImageFont.truetype(FONT_BD, 32)
    label = "★ " + cfg["study"]
    sw = d.textlength(label, font=sf)
    d.rounded_rectangle([W - sw - 78, 32, W - 34, 84], radius=24, fill=(255, 255, 255, 235))
    d.text((W - sw - 60, 39), label, font=sf, fill=DEEP)

    # 졸라걸 캐릭터 합성(왼쪽) + 발밑 그림자
    for cand in ("stickman_zw_waving.png", "stickman_zw_cheering.png", "stickman_zw_base.png"):
        p = os.path.join(POSES, cand)
        if os.path.exists(p):
            ch = Image.open(p).convert("RGBA")
            target_h = 430
            sc = target_h / ch.height
            ch = ch.resize((max(1, int(ch.width * sc)), target_h), Image.LANCZOS)
            cxp = 280
            sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).ellipse([cxp - 120, 622, cxp + 120, 662], fill=(0, 0, 0, 60))
            base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
            base.alpha_composite(ch, (int(cxp - ch.width / 2), int(642 - ch.height)))
            break

    # 말풍선: 안녕하세요!
    bx, by = 560, 300
    bw2, bh2 = 620, 150
    d.rounded_rectangle([bx, by, bx + bw2, by + bh2], radius=40, fill=(255, 255, 255, 245))
    d.polygon([(bx + 30, by + bh2 - 10), (bx - 36, by + bh2 + 44), (bx + 96, by + bh2 - 4)], fill=(255, 255, 255, 245))
    hf = ImageFont.truetype(FONT_BD, 72)
    center(d, bx + bw2 / 2, by + bh2 / 2, cfg["hello"], hf, ROSE)

    # 하단 자기소개 칩
    yb = 600
    xs = [520, 800, 1080]
    cols = [TEAL, (180, 110, 60), DEEP]
    for text, x, col in zip(cfg["chips"], xs, cols):
        chip(d, x, yb, text, (255, 255, 255, 235), col, 36, padx=18, pady=10, radius=16)

    out = os.path.join(ROOT, "web", "public", "docs", f"hangeul_w7_thumbnail_{lang}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    base.convert("RGB").save(out)
    base.convert("RGB").save(os.path.join(ROOT, "scratch", f"_thumb_w7_{lang}.png"))
    print("thumbnail ->", out)


if __name__ == "__main__":
    for lg in (sys.argv[1:] or ["ko", "en"]):
        build(lg)
