#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_lesson_thumbs.py — 요일별 7패턴 강의 썸네일 생성기.

설계: 7개 요일(월~일)=7개 스킬(핵심영상/어휘/문형/듣기/말하기/문화/복습) 각각 고유한
      '컬러 + 모티프(형식)' 패턴을 가진다. 이 7패턴이 24주 내내 반복(주마다 내용만 다름).
      → 한 주 안에서는 요일마다 형식·컬러가 비슷하되 구분되고, 주차가 바뀌어도 같은 요일은 같은 패턴.

입력: web/src/data/lessons168.json
출력: web/public/docs/lesson_thumbs/w{week}_d{day}_{ko,en}.png  (1280x720)
사용:
  python make_lesson_thumbs.py                 # 전체 168×2
  python make_lesson_thumbs.py --week 1        # 1주차만(14장)
  python make_lesson_thumbs.py --week 1 --day 2  # 1주 화요일만
"""
import os
import sys
import json
import math
import argparse

import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "web", "src", "data", "lessons168.json")
OUT = os.path.join(ROOT, "web", "public", "docs", "lesson_thumbs")
os.makedirs(OUT, exist_ok=True)
W, H = 1280, 720
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_BD = "C:/Windows/Fonts/malgunbd.ttf"
if not os.path.exists(FONT_BD):
    FONT_BD = FONT

# 요일(1=월..7=일) → 패턴: (요일ko, 요일en, accent, bg_tint, motif)
PATTERN = {
    1: ("월", "MON", (228, 76, 76),  (255, 239, 239), "video"),     # 핵심 영상
    2: ("화", "TUE", (240, 158, 40), (255, 247, 231), "vocab"),     # 어휘
    3: ("수", "WED", (58, 170, 92),  (235, 250, 239), "pattern"),   # 문형
    4: ("목", "THU", (56, 138, 230), (232, 243, 255), "listen"),    # 듣기
    5: ("금", "FRI", (150, 92, 222), (244, 237, 255), "speak"),     # 말하기
    6: ("토", "SAT", (28, 172, 168), (229, 248, 247), "culture"),   # 문화
    7: ("일", "SUN", (230, 92, 160), (255, 235, 245), "review"),    # 복습
}
LEVEL_ACCENT = {"beginner": (76, 175, 120), "intermediate": (90, 140, 230), "advanced": (210, 110, 70)}


def _font(path, sz):
    return ImageFont.truetype(path, sz)


def _grad_bg(tint):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = (yy / H * 0.6 + xx / W * 0.4)[..., None]
    top = np.array(tint, np.float32)
    bot = np.array([255, 255, 255], np.float32)
    img = top * (1 - t) + bot * t
    return Image.fromarray(img.astype(np.uint8), "RGB").convert("RGBA")


def _round(d, box, r, **kw):
    d.rounded_rectangle(box, radius=r, **kw)


def _center_text(d, cx, y, text, font, fill, stroke=0, stroke_fill=(255, 255, 255)):
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    d.text((cx - (r - l) / 2 - l, y), text, font=font, fill=fill,
           stroke_width=stroke, stroke_fill=stroke_fill)
    return b - t


def draw_motif(im, kind, acc, cx, cy, s=1.0):
    """요일별 모티프(형식). 큰 원형 배지 안에 패턴별 아이콘을 PIL로 직접 그림."""
    d = ImageDraw.Draw(im)
    R = int(150 * s)
    # 배지 원반
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(255, 255, 255, 235),
              outline=acc + (255,), width=8)
    a = acc + (255,)
    if kind == "video":            # ▶ 재생 삼각형 + 필름 느낌
        tri = [(cx - R * 0.32, cy - R * 0.42), (cx - R * 0.32, cy + R * 0.42), (cx + R * 0.5, cy)]
        d.polygon(tri, fill=a)
    elif kind == "vocab":          # 📚 단어카드 (가 자모 카드)
        for i, dx in enumerate((-0.5, -0.05, 0.4)):
            x = cx + R * dx
            _round(d, [x - R * 0.28, cy - R * 0.42, x + R * 0.28, cy + R * 0.42], R * 0.12,
                   fill=(255, 255, 255, 255), outline=a, width=6)
        f = _font(FONT_BD, int(R * 0.5))
        _center_text(d, cx, cy - R * 0.28, "가", f, a)
    elif kind == "pattern":        # 🧩 문형 블록 [   ]+[   ]
        bw = R * 0.5
        for sgn, lab in ((-1, ""), (1, "")):
            x = cx + sgn * R * 0.42
            _round(d, [x - bw / 2, cy - R * 0.22, x + bw / 2, cy + R * 0.22], 10, fill=a)
        f = _font(FONT_BD, int(R * 0.5))
        _center_text(d, cx, cy - R * 0.3, "+", f, a)
    elif kind == "listen":         # 👂 음파
        for i in range(1, 5):
            rr = R * 0.18 * i
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 300, 60, fill=a, width=7)
        d.ellipse([cx - R * 0.12, cy - R * 0.12, cx + R * 0.12, cy + R * 0.12], fill=a)
    elif kind == "speak":          # 🗣️ 말풍선
        _round(d, [cx - R * 0.55, cy - R * 0.5, cx + R * 0.55, cy + R * 0.25], R * 0.2, fill=a)
        d.polygon([(cx - R * 0.2, cy + R * 0.2), (cx - R * 0.4, cy + R * 0.55), (cx + R * 0.05, cy + R * 0.2)], fill=a)
        f = _font(FONT_BD, int(R * 0.42))
        _center_text(d, cx, cy - R * 0.32, "말", f, (255, 255, 255))
    elif kind == "culture":        # 🌏 지구/경복궁 지붕
        d.ellipse([cx - R * 0.5, cy - R * 0.5, cx + R * 0.5, cy + R * 0.5], outline=a, width=8)
        for ang in range(0, 180, 45):
            rad = math.radians(ang)
            d.line([(cx - R * 0.5 * math.cos(rad), cy - R * 0.5 * math.sin(rad)),
                    (cx + R * 0.5 * math.cos(rad), cy + R * 0.5 * math.sin(rad))], fill=a, width=4)
        d.ellipse([cx - R * 0.5, cy - R * 0.18, cx + R * 0.5, cy + R * 0.18], outline=a, width=4)
    elif kind == "review":         # 🎮 별/트로피
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = R * 0.55 if i % 2 == 0 else R * 0.24
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        d.polygon(pts, fill=a)


def render_thumb(lesson, lang):
    wk, day, lvl = lesson["week"], lesson["day"], lesson["level"]
    dk, den, acc, tint, motif = PATTERN[day]
    im = _grad_bg(tint)
    d = ImageDraw.Draw(im)
    lacc = LEVEL_ACCENT[lvl] + (255,)

    # 좌측 레벨 컬러 바 + 상단 요일/주차 칩
    _round(d, [0, 0, 26, H], 0, fill=lacc)
    # 강의 번호 배지(좌상단) — 요일 개념 대신 주차-강(예: 1-2)
    d.ellipse([70, 60, 196, 186], fill=acc + (255,))
    f_day = _font(FONT_BD, 52)
    _center_text(d, 133, 96, f"{wk}-{day}", f_day, (255, 255, 255))
    f_dn = _font(FONT_BD, 26)
    _center_text(d, 133, 196, f"{'강의' if lang == 'ko' else 'Lesson'} {(wk-1)*7+day}", f_dn, acc)

    # 우상단: 레벨 + 주차
    lv_ko = {"beginner": "초급", "intermediate": "중급", "advanced": "고급"}[lvl]
    f_lv = _font(FONT_BD, 34)
    tag = f"{lv_ko if lang=='ko' else lvl.title()} · {wk}{'주차' if lang=='ko' else 'wk'}"
    l, t, r, b = d.textbbox((0, 0), tag, font=f_lv)
    _round(d, [W - (r - l) - 110, 64, W - 50, 122], 26, fill=(255, 255, 255, 220), outline=lacc, width=3)
    d.text((W - (r - l) - 80, 74), tag, font=f_lv, fill=lacc)

    # 중앙 모티프 배지(우측)
    draw_motif(im, motif, acc, 980, 360, s=1.05)

    # 스킬명(요일 의미) 크게 — 모티프 아래
    skill = lesson["skill_ko"] if lang == "ko" else lesson["skill_en"]
    f_sk = _font(FONT_BD, 52)
    _center_text(d, 980, 540, skill, f_sk, acc + (255,))

    # 좌측: 주제(테마) + 강의 제목
    theme = lesson["theme_ko"] if lang == "ko" else lesson["theme_en"]
    title = lesson["title_ko"] if lang == "ko" else lesson["title_en"]
    f_th = _font(FONT_BD, 40)
    d.text((80, 300), theme, font=f_th, fill=(90, 84, 78))
    # 제목 워드랩(좌측 영역 폭 ~ 700)
    f_ti = _font(FONT_BD, 60)
    words = title.split(" ")
    lines, cur = [], ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if d.textlength(test, font=f_ti) <= 700:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    yy = 360
    for ln in lines[:3]:
        d.text((80, yy), ln, font=f_ti, fill=(34, 31, 28))
        yy += 74

    # 하단 브랜드
    f_br = _font(FONT_BD, 30)
    d.text((80, H - 70), "drjay-ed · 훈민정음" if lang == "ko" else "drjay-ed · Hunminjeongeum",
           font=f_br, fill=(120, 112, 104))

    out = os.path.join(OUT, f"w{wk}_d{day}_{lang}.png")
    im.convert("RGB").save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int, default=0)
    ap.add_argument("--day", type=int, default=0)
    args = ap.parse_args()
    lessons = json.load(open(DATA, encoding="utf-8"))
    n = 0
    for L in lessons:
        if args.week and L["week"] != args.week:
            continue
        if args.day and L["day"] != args.day:
            continue
        for lang in ("ko", "en"):
            render_thumb(L, lang)
            n += 1
    print(f"{n} thumbnails -> web/public/docs/lesson_thumbs/")


if __name__ == "__main__":
    main()
