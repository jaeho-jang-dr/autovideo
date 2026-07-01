#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_thumbnail.py — 초급 1주차 "한글의 탄생과 단모음" 썸네일.
구성: 훈민정음 해례본(투명도 50%)을 전체 배경 + 왼편 세종대왕(스틱맨+왕관)
      + 오른편 자모 28자 자유롭게 흩어짐 + 상단 제목.
출력: web/public/docs/hangeul_w1_thumbnail.png (1280x720)
"""
import os
import sys
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join(ROOT, "assets", "graphics")
W, H = 1280, 720
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_BD = "C:/Windows/Fonts/malgunbd.ttf"
GOLD = (210, 150, 40)

# 훈민정음 28자: 초성 17 + 중성 11 (아래아 ㆍ, 여린히읗 ㆆ, 옛이응 ㆁ, 반치음 ㅿ 포함)
JAMO28 = list("ㄱㅋㆁㄷㅌㄴㅂㅍㅁㅈㅊㅅㆆㅎㅇㄹㅿ") + list("ㆍㅡㅣㅗㅏㅜㅓㅛㅑㅠㅕ")


def pastel():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = (xx - W / 2) / (W / 2); dy = (yy - H / 2) / (H / 2)
    r = np.clip(np.sqrt(dx * dx + dy * dy) / 1.28, 0.0, 1.0)
    t = (r ** 1.4)[..., None]
    img = np.array([253, 252, 248], np.float32) * (1 - t) + np.array([230, 224, 238], np.float32) * t
    return Image.fromarray(img.astype(np.uint8), "RGB").convert("RGBA")


def haerye_bg(base, opacity=0.5):
    s = Image.open(os.path.join(G, "obj_haerye_scroll.png")).convert("RGBA")
    sc = max(W / s.width, H / s.height) * 1.02      # cover
    s = s.resize((int(s.width * sc), int(s.height * sc)), Image.LANCZOS)
    x = (W - s.width) // 2; y = (H - s.height) // 2
    a = s.split()[3].point(lambda v: int(v * opacity))
    s.putalpha(a)
    base.alpha_composite(s, (x, y))


def paste(base, path, cx, cy, scale):
    im = Image.open(path).convert("RGBA")
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def glyph(ch, size, rot, font, fill=(34, 30, 26, 255)):
    pad = size
    im = Image.new("RGBA", (size + pad * 2, size + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(font, size)
    b = d.textbbox((0, 0), ch, font=f)
    cx = (size + pad * 2) / 2 - (b[2] - b[0]) / 2 - b[0]
    cy = (size + pad * 2) / 2 - (b[3] - b[1]) / 2 - b[1]
    for ox in (-4, -2, 0, 2, 4):                       # 흰 후광 (배경 위에서 도드라지게)
        for oy in (-4, -2, 0, 2, 4):
            d.text((cx + ox, cy + oy), ch, font=f, fill=(255, 255, 255, 235))
    d.text((cx, cy), ch, font=f, fill=fill)
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)


def text_center(d, cx, y, s, font, fill, halo=None):
    w = d.textlength(s, font=font)
    if halo:
        for ox in (-3, 0, 3):
            for oy in (-3, 0, 3):
                d.text((cx - w / 2 + ox, y + oy), s, font=font, fill=halo)
    d.text((cx - w / 2, y), s, font=font, fill=fill)


TEXTS = {
    "ko": {"title": "한글의 탄생과 단모음", "tsize": 76,
           "sub": "Birth of Hangeul & Simple Vowels", "badge": "초급 · 1주차"},
    "en": {"title": "Birth of Hangeul & Vowels", "tsize": 64,
           "sub": "한글의 탄생과 단모음 · Beginner Week 1", "badge": "Beginner · Week 1"},
}


def build(lang):
    cfg = TEXTS[lang]
    base = pastel()
    haerye_bg(base, 0.40)                             # 해례본 전체 배경(옅게)

    # 오른편: 자모 28자 자유롭게 흩어짐 (흰 후광으로 도드라지게). seed 고정 → 언어 무관 동일 배치.
    rng = random.Random(11)
    placed = []
    for ch in JAMO28:
        for _ in range(50):
            x = rng.randint(700, 1230); y = rng.randint(115, 665)
            if all((x - px) ** 2 + (y - py) ** 2 > 92 ** 2 for px, py in placed):
                placed.append((x, y)); break
        else:
            placed.append((x, y))
        col = (GOLD + (255,)) if rng.random() < 0.22 else (34, 30, 26, 255)
        g = glyph(ch, rng.randint(52, 104), rng.uniform(-24, 24), FONT_BD, fill=col)
        base.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))

    # 왼편: 세종대왕 + 왕관
    paste(base, os.path.join(G, "poses", "stickman_sejong.png"), 305, 500, 0.78)
    paste(base, os.path.join(G, "obj_crown.png"), 305, 205, 0.60)

    # 상단: 제목
    d = ImageDraw.Draw(base)
    title = ImageFont.truetype(FONT_BD, cfg["tsize"])
    sub = ImageFont.truetype(FONT_BD, 34)
    badge = ImageFont.truetype(FONT_BD, 30)
    d.rounded_rectangle([170, 30, 1110, 196], radius=26, fill=(255, 255, 255, 150))
    text_center(d, 640, 50, cfg["title"], title, (34, 30, 26), halo=(255, 255, 255))
    d.rounded_rectangle([640 - 140, 138, 640 + 140, 150], radius=6, fill=(GOLD + (255,)))
    text_center(d, 640, 156, cfg["sub"], sub, (120, 108, 118))
    bw = d.textlength(cfg["badge"], font=badge)
    d.rounded_rectangle([40, 36, 40 + bw + 36, 82], radius=23, fill=(GOLD + (240,)))
    d.text((58, 42), cfg["badge"], font=badge, fill=(255, 255, 255))

    out = os.path.join(ROOT, "web", "public", "docs", f"hangeul_w1_thumbnail_{lang}.png")
    base.convert("RGB").save(out)
    base.convert("RGB").save(os.path.join(ROOT, "scratch", f"_thumbnail_{lang}.png"))
    print("thumbnail ->", out)
    return out


if __name__ == "__main__":
    langs = sys.argv[1:] or ["ko", "en"]
    for lg in langs:
        build(lg)
    # 하위호환: 기본 파일은 ko
    import shutil
    shutil.copy(os.path.join(ROOT, "web", "public", "docs", "hangeul_w1_thumbnail_ko.png"),
                os.path.join(ROOT, "web", "public", "docs", "hangeul_w1_thumbnail.png"))
