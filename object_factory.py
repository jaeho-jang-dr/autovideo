#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
object_factory.py — 한글 탄생·단모음 영상용 소품/기호를 스틱맨과 동일한 잉크 스타일로
                    파라메트릭 제작하고 content.db `assets`(type=object) 에 등록한다.

stickman_factory 의 잉크 스탬프 헬퍼를 재사용해 선 굵기·손그림 흔들림을 통일한다.
출력: assets/graphics/<name>.png (투명 배경, 512² 기본).
실행: python object_factory.py
"""
import os
import sys
import math
import random
import sqlite3

from PIL import Image, ImageDraw, ImageFont
from stickman_factory import stamp_stroke, INK, SS  # 동일 잉크 스타일 공유

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
GDIR = os.path.join(ROOT, "assets", "graphics")
DB = os.path.join(ROOT, "channel", "content.db")
FONT = "C:/Windows/Fonts/malgun.ttf"
BASE = 512                      # base canvas
GOLD = (242, 179, 61, 255)      # warm accent (sun / sparkle)
RED = (200, 60, 50, 255)

C = BASE * SS // 2              # supersampled center


def canvas():
    img = Image.new("RGBA", (BASE * SS, BASE * SS), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def finish(img, name):
    img = img.resize((BASE, BASE), Image.LANCZOS)
    out = os.path.join(GDIR, f"{name}.png")
    img.save(out)
    return f"assets/graphics/{name}.png"


def ellipse_pts(cx, cy, rx, ry, n=140, rot=0.0):
    pts = []
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(n + 1):
        a = i / n * math.tau
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return pts


def stamp_ellipse(draw, cx, cy, rx, ry, width, rng, wobble=0.6, rot=0.0, fill=INK):
    stamp_stroke(draw, ellipse_pts(cx, cy, rx, ry, rot=rot), width, rng, wobble=wobble, fill=fill)


# ---- mouth diagrams (front-view lips, ink) ---------------------------------
def draw_mouth(draw, rng, kind):
    """kind: vertical / mid / round / flat — 단모음 입모양 교육용."""
    lw = 9 * SS
    if kind == "vertical":           # ㅏ/ㅓ : jaw dropped, tall opening, flat lips
        ow, oh, lipw = 70 * SS, 120 * SS, lw
        draw.ellipse([C - ow, C - oh, C + ow, C + oh], fill=(40, 30, 30, 255))
        stamp_ellipse(draw, C, C, ow, oh, lipw, rng)
    elif kind == "mid":              # ㅐ/ㅔ : moderate oval opening
        ow, oh = 95 * SS, 78 * SS
        draw.ellipse([C - ow, C - oh, C + ow, C + oh], fill=(40, 30, 30, 255))
        stamp_ellipse(draw, C, C, ow, oh, lw, rng)
    elif kind == "round":            # ㅗ/ㅜ : tightly rounded, pushed forward
        r = 60 * SS
        draw.ellipse([C - r, C - r, C + r, C + r], fill=(40, 30, 30, 255))
        stamp_ellipse(draw, C, C, r, r, lw * 1.7, rng)        # thick pursed lips
        stamp_ellipse(draw, C, C, r * 1.55, r * 1.45, lw, rng, wobble=0.4)  # protrusion ring
    elif kind == "flat":             # ㅡ/ㅣ : stretched flat & wide
        ow, oh = 150 * SS, 26 * SS
        draw.ellipse([C - ow, C - oh, C + ow, C + oh], fill=(40, 30, 30, 255))
        stamp_ellipse(draw, C, C, ow, oh, lw, rng)
        stamp_stroke(draw, [(C - ow * 0.8, C), (C + ow * 0.8, C)], lw * 0.7, rng, wobble=0.3)  # lip seam
        for k in (-2, -1, 1, 2):     # teeth hint
            x = C + k * 38 * SS
            stamp_stroke(draw, [(x, C - oh * 0.6), (x, C + oh * 0.6)], lw * 0.5, rng, wobble=0.1)


# ---- props ------------------------------------------------------------------
def draw_sun(draw, rng):
    r = 120 * SS
    draw.ellipse([C - r, C - r, C + r, C + r], fill=GOLD)
    stamp_ellipse(draw, C, C, r, r, 9 * SS, rng)
    for i in range(12):
        a = i / 12 * math.tau
        x1, y1 = C + (r + 22 * SS) * math.cos(a), C + (r + 22 * SS) * math.sin(a)
        x2, y2 = C + (r + 70 * SS) * math.cos(a), C + (r + 70 * SS) * math.sin(a)
        stamp_stroke(draw, [(x1, y1), (x2, y2)], 8 * SS, rng, wobble=0.2, taper=True)


def draw_mirror(draw, rng):
    cx, cy = C, C - 40 * SS
    rx, ry = 105 * SS, 130 * SS
    stamp_ellipse(draw, cx, cy, rx, ry, 11 * SS, rng)          # frame
    stamp_ellipse(draw, cx, cy, rx * 0.82, ry * 0.82, 6 * SS, rng, wobble=0.3)
    draw.ellipse([cx - rx * 0.78, cy - ry * 0.78, cx + rx * 0.78, cy + ry * 0.78], fill=(214, 230, 236, 110))
    stamp_stroke(draw, [(cx - 30 * SS, cy - 60 * SS), (cx - 55 * SS, cy + 10 * SS)], 7 * SS, rng, wobble=0.3)  # shine
    # handle
    stamp_stroke(draw, [(cx, cy + ry), (cx, cy + ry + 110 * SS)], 16 * SS, rng, wobble=0.3)


def draw_bell(draw, rng):
    cx, cy = C, C - 20 * SS
    pts = [(cx - 95 * SS, cy + 90 * SS), (cx - 80 * SS, cy + 10 * SS),
           (cx - 55 * SS, cy - 55 * SS), (cx, cy - 80 * SS),
           (cx + 55 * SS, cy - 55 * SS), (cx + 80 * SS, cy + 10 * SS),
           (cx + 95 * SS, cy + 90 * SS)]
    stamp_stroke(draw, pts, 10 * SS, rng)
    stamp_stroke(draw, [(cx - 115 * SS, cy + 90 * SS), (cx + 115 * SS, cy + 90 * SS)], 10 * SS, rng)  # rim
    stamp_stroke(draw, [(cx, cy - 80 * SS), (cx, cy - 110 * SS)], 9 * SS, rng)                         # top loop
    draw.ellipse([cx - 16 * SS, cy + 100 * SS, cx + 16 * SS, cy + 132 * SS], fill=INK)                 # clapper
    for s in (-1, 1):                                                                                  # ring lines
        bx = cx + s * 150 * SS
        stamp_stroke(draw, [(bx, cy - 30 * SS), (bx + s * 28 * SS, cy - 30 * SS)], 7 * SS, rng, wobble=0.2)
        stamp_stroke(draw, [(bx, cy + 20 * SS), (bx + s * 28 * SS, cy + 20 * SS)], 7 * SS, rng, wobble=0.2)


def draw_dot(draw, rng):            # 하늘(天) = round dot •
    r = 56 * SS
    draw.ellipse([C - r, C - r, C + r, C + r], fill=INK)


def draw_hline(draw, rng):          # 땅(地) = horizontal line ㅡ
    stamp_stroke(draw, [(C - 150 * SS, C), (C + 150 * SS, C)], 18 * SS, rng, wobble=0.4)


def draw_vline(draw, rng):          # 사람(人) = vertical line ㅣ
    stamp_stroke(draw, [(C, C - 160 * SS), (C, C + 160 * SS)], 18 * SS, rng, wobble=0.4)


def draw_text_glyph(draw, rng, text, size, color=INK, ring=False):
    f = ImageFont.truetype(FONT, int(size * SS))
    b = draw.textbbox((0, 0), text, font=f)
    w, h = b[2] - b[0], b[3] - b[1]
    if ring:
        r = max(w, h) // 2 + 46 * SS
        stamp_ellipse(draw, C, C, r, r, 11 * SS, rng)
    draw.text((C - w / 2 - b[0], C - h / 2 - b[1]), text, font=f, fill=color)


def draw_crown(draw, rng):          # 세종대왕 왕관 (잉크)
    pts = [(-120, 70), (-120, 10), (-80, -80), (-40, 10), (0, -95),
           (40, 10), (80, -80), (120, 10), (120, 70), (-120, 70)]
    pts = [(C + x * SS, C + y * SS) for x, y in pts]
    stamp_stroke(draw, pts, 10 * SS, rng)
    stamp_stroke(draw, [(C - 120 * SS, C + 42 * SS), (C + 120 * SS, C + 42 * SS)], 9 * SS, rng, wobble=0.3)  # band line
    for tx, ty in [(-80, -80), (0, -95), (80, -80)]:                       # jewels on tips
        x, y = C + tx * SS, C + ty * SS
        r = 14 * SS
        draw.ellipse([x - r, y - r, x + r, y + r], fill=GOLD)
        stamp_ellipse(draw, x, y, r, r, 5 * SS, rng, wobble=0.2)
    for jx in (-60, 0, 60):                                                # band gems
        x, y = C + jx * SS, C + 56 * SS
        r = 9 * SS
        draw.ellipse([x - r, y - r, x + r, y + r], fill=RED)


def draw_book(draw, rng):           # 펼친 한자 책 (잉크) — 어려운 한자(천자문 天地玄黃…)
    def p(x, y):
        return (C + x * SS, C + y * SS)
    # 펼친 책: 두 페이지가 가운데서 만나는 얕은 V 형태
    left = [p(-156, 64), p(-150, -64), p(-6, -44), p(-6, 78), p(-156, 64)]
    right = [p(156, 64), p(150, -64), p(6, -44), p(6, 78), p(156, 64)]
    # 책등 받침(아래)
    stamp_stroke(draw, [p(-156, 64), p(-6, 78), p(156, 64)], 11 * SS, rng, wobble=0.3)
    for page in (left, right):
        stamp_stroke(draw, page, 10 * SS, rng, wobble=0.3)
    stamp_stroke(draw, [p(0, -44), p(0, 78)], 8 * SS, rng, wobble=0.2)   # 가운데 책등
    # 한자 (천자문 첫 구절 — '어려운 글자' 상징)
    try:
        hf = ImageFont.truetype("C:/Windows/Fonts/batang.ttc", int(30 * SS))
    except Exception:
        hf = ImageFont.truetype(FONT, int(30 * SS))
    cols = [(-112, "天地"), (-62, "玄黃"), (62, "宇宙"), (112, "洪荒")]
    for cx, chars in cols:
        for i, ch in enumerate(chars):
            x, y = p(cx, -22 + i * 44)
            b = draw.textbbox((0, 0), ch, font=hf)
            draw.text((x - (b[2] - b[0]) / 2 - b[0], y - (b[3] - b[1]) / 2 - b[1]), ch, font=hf, fill=INK)


def draw_sparkle(draw, rng):
    def star(cx, cy, R):
        for a in (0, math.pi / 2):
            for d in (1, -1):
                tip = (cx + d * R * math.cos(a), cy + d * R * math.sin(a))
                stamp_stroke(draw, [(cx, cy), tip], 7 * SS, rng, wobble=0.1, taper=True)
        r = R * 0.16
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
    star(C, C - 20 * SS, 90 * SS)
    star(C + 140 * SS, C + 90 * SS, 55 * SS)
    star(C - 130 * SS, C + 70 * SS, 45 * SS)


def draw_head_profile(draw, rng):    # 발음기관 측면 머리 (입·혀·목)
    cx, cy = C, C
    R = 150 * SS
    stamp_ellipse(draw, cx, cy, R, R * 1.06, 9 * SS, rng)                 # head ring
    nose = [(cx + R * 0.96, cy - 8 * SS), (cx + R * 1.20, cy + 20 * SS), (cx + R * 0.95, cy + 36 * SS)]
    stamp_stroke(draw, nose, 8 * SS, rng, wobble=0.2)                     # nose bump
    mx, my = cx + R * 0.5, cy + R * 0.42
    draw.polygon([(mx, my - 26 * SS), (cx + R * 1.02, my - 4 * SS),
                  (cx + R * 1.02, my + 20 * SS), (mx, my + 32 * SS)], fill=(48, 34, 34, 255))  # open mouth
    stamp_stroke(draw, [(mx, my - 26 * SS), (cx + R * 1.04, my - 2 * SS)], 7 * SS, rng, wobble=0.12)
    stamp_stroke(draw, [(mx, my + 32 * SS), (cx + R * 1.04, my + 18 * SS)], 7 * SS, rng, wobble=0.12)
    stamp_stroke(draw, [(mx - 8 * SS, my + 24 * SS), (mx + 34 * SS, my + 8 * SS), (cx + R * 0.96, my + 12 * SS)],
                 7 * SS, rng, wobble=0.2, fill=(196, 90, 90, 255))        # tongue (reddish)
    r = 18 * SS                                                          # ear
    draw.ellipse([cx - R * 0.2 - r, cy - r, cx - R * 0.2 + r, cy + r], outline=INK, width=int(7 * SS))


def draw_block(draw, rng):           # 모아쓰기 음절 블록 프레임 (초성+중성)
    s = 150 * SS
    pts = [(C - s, C - s), (C + s, C - s), (C + s, C + s), (C - s, C + s), (C - s, C - s)]
    stamp_stroke(draw, pts, 9 * SS, rng, wobble=0.25)
    for seg in [[(C, C - s), (C, C + s)], [(C - s, C), (C + s, C)]]:      # faint guide cross
        stamp_stroke(draw, seg, 4 * SS, rng, wobble=0.15, fill=(190, 180, 170, 255))


def draw_card(draw, rng):            # 플래시카드 프레임
    w, h = 140 * SS, 180 * SS
    pts = [(C - w, C - h), (C + w, C - h), (C + w, C + h), (C - w, C + h), (C - w, C - h)]
    stamp_stroke(draw, pts, 9 * SS, rng, wobble=0.25)
    stamp_ellipse(draw, C - w + 22 * SS, C - h + 22 * SS, 4 * SS, 4 * SS, 6 * SS, rng)  # corner dot


def draw_plus(draw, rng):            # 가획(+) 표시
    g = (210, 150, 40, 255)
    stamp_stroke(draw, [(C - 70 * SS, C), (C + 70 * SS, C)], 18 * SS, rng, wobble=0.15, fill=g)
    stamp_stroke(draw, [(C, C - 70 * SS), (C, C + 70 * SS)], 18 * SS, rng, wobble=0.15, fill=g)


def draw_reddot(draw, rng):          # 발음 위치 강조 (빨간 점)
    r = 60 * SS
    draw.ellipse([C - r, C - r, C + r, C + r], fill=(214, 70, 60, 180))
    stamp_ellipse(draw, C, C, r, r, 7 * SS, rng, wobble=0.2, fill=(180, 50, 45, 255))


OBJECTS = [
    ("organ_head_profile", draw_head_profile, "발음기관 머리(입·혀·목)", "Head profile (speech organs)"),
    ("obj_block", draw_block, "모아쓰기 음절 블록", "Syllable block frame"),
    ("obj_card", draw_card, "플래시카드", "Flashcard frame"),
    ("obj_plus", draw_plus, "가획(+) 표시", "Plus-stroke mark"),
    ("obj_reddot", draw_reddot, "발음 위치 강조 점", "Articulation highlight dot"),
    ("mouth_open_vertical", lambda d, r: draw_mouth(d, r, "vertical"), "입을 세로로 크게 연 입모양(ㅏ/ㅓ)", "Mouth open vertically (ㅏ/ㅓ)"),
    ("mouth_mid_open",      lambda d, r: draw_mouth(d, r, "mid"),      "중간으로 벌린 입모양(ㅐ/ㅔ)", "Mouth mid-open (ㅐ/ㅔ)"),
    ("mouth_rounded",       lambda d, r: draw_mouth(d, r, "round"),    "동그랗게 모은 입모양(ㅗ/ㅜ)", "Rounded lips (ㅗ/ㅜ)"),
    ("mouth_flat_wide",     lambda d, r: draw_mouth(d, r, "flat"),     "옆으로 납작한 입모양(ㅡ/ㅣ)", "Flat wide lips (ㅡ/ㅣ)"),
    ("obj_crown",   draw_crown,  "세종대왕 왕관", "King's crown"),
    ("obj_book",    draw_book,    "두꺼운 옛 한자책", "Thick old books"),
    ("obj_sun",     draw_sun,    "해 (동/서 밝은 모음)", "Sun"),
    ("obj_mirror",  draw_mirror, "손거울 (입모양 점검)", "Hand mirror"),
    ("obj_bell",    draw_bell,   "알림 종 (구독)", "Notification bell"),
    ("sym_heaven_dot", draw_dot,   "천(天) 둥근 점 •", "Heaven dot"),
    ("sym_earth_line", draw_hline, "지(地) 가로선 ㅡ", "Earth horizontal line"),
    ("sym_human_line", draw_vline, "인(人) 세로선 ㅣ", "Human vertical line"),
    ("obj_qmark",    lambda d, r: draw_text_glyph(d, r, "?", 300), "물음표", "Question mark"),
    ("obj_badge_28", lambda d, r: draw_text_glyph(d, r, "28", 150, ring=True), "스물여덟 글자 뱃지", "28 letters badge"),
    ("obj_sparkle",  draw_sparkle, "반짝임 입자", "Sparkle particles"),
]


def main():
    os.makedirs(GDIR, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    has_created = "created_at" in {r[1] for r in cur.execute("pragma table_info(assets)")}
    manifest = []
    for name, fn, ko, en in OBJECTS:
        img, draw = canvas()
        fn(draw, random.Random(abs(hash(name)) % 1000 + 1))
        path = finish(img, name)
        manifest.append((name, path, ko, en))
        print("saved", path)

    paths = [m[1] for m in manifest]
    cur.executemany("DELETE FROM assets WHERE file_path=?", [(p,) for p in paths])
    for name, path, ko, en in manifest:
        flow = f"object_factory.py (parametric ink) | {en}"
        if has_created:
            cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt, created_at) "
                        "VALUES (?,?,?,?,?, datetime('now'))", (ko, name, "object", path, flow))
        else:
            cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) "
                        "VALUES (?,?,?,?,?)", (ko, name, "object", path, flow))
    con.commit()
    print(f"\nregistered {len(manifest)} objects to assets (type=object)")
    con.close()


if __name__ == "__main__":
    main()
