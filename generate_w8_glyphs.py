#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""generate_w8_glyphs.py — 8주차 "숫자·날짜·시간" 단어 글리프 PNG + DB 등록.
재실행: python generate_w8_glyphs.py
"""
import os
import sys
import sqlite3

from PIL import Image, ImageDraw, ImageFont

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
LDIR = os.path.join(ROOT, "assets", "graphics", "letters")
DB = os.path.join(ROOT, "channel", "content.db")
FONT = "C:/Windows/Fonts/malgunbd.ttf"
if not os.path.exists(FONT):
    FONT = "C:/Windows/Fonts/malgun.ttf"

WORDS = ["하나", "둘", "셋", "넷", "다섯", "여섯", "일곱", "여덟", "아홉", "열",
         "일", "이", "삼", "사", "오", "육", "칠", "팔", "구", "십",
         "월", "화", "수", "목", "금", "토", "요일",
         "시", "분", "세", "삼십", "세 시", "삼십 분",
         "숫자", "날짜", "시간", "고유어", "한자어", "개수"]


def render(text, color=(28, 28, 28, 255)):
    f = ImageFont.truetype(FONT, 200)
    tmp = Image.new("RGBA", (len(text) * 230 + 80, 320), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    b = d.textbbox((0, 0), text, font=f)
    d.text((40 - b[0], 40 - b[1]), text, font=f, fill=color)
    bb = tmp.split()[3].getbbox()
    pad = 16
    return tmp.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), bb[2] + pad, bb[3] + pad))


def reg(cur, has, name_kr, name_en, typ, fp):
    cur.execute("DELETE FROM assets WHERE file_path=?", (fp,))
    if has:
        cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt, created_at) "
                    "VALUES (?,?,?,?,?, datetime('now'))", (name_kr, name_en, typ, fp, "generate_w8_glyphs.py"))
    else:
        cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                    (name_kr, name_en, typ, fp, "generate_w8_glyphs.py"))


def main():
    os.makedirs(LDIR, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    has = "created_at" in {r[1] for r in cur.execute("pragma table_info(assets)")}
    n = 0
    for w in WORDS:
        render(w).save(os.path.join(LDIR, f"word_{w}.png"))
        reg(cur, has, w, f"word_{w}", "word", f"graphics/letters/word_{w}.png")
        n += 1
    con.commit()
    con.close()
    print(f"{n} W8 glyphs generated + registered")


if __name__ == "__main__":
    main()
