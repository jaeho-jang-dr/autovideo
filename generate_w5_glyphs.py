#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_w5_glyphs.py — 5주차 "이중모음과 반모음 활주" 글자/단어/기호 글리프 PNG + DB 등록.
 - 단모음(합성용): ㅏㅓㅗㅜㅣㅐㅔㅡ
 - 이중모음(결과): ㅑㅕㅛㅠㅘㅝㅟㅚㅢㅒㅖ
 - 예시 단어: 야구 여우 요리 우유 얘기 예의 사과 샤워 외투 가위 의자
 - 기호: sym_arrow(→) sym_plus(+) / 제목어: 이중모음 반모음
malgun bold 검정, 투명 배경. assets/graphics/letters/.
재실행: python generate_w5_glyphs.py
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

LETTERS = ["ㅏ", "ㅓ", "ㅗ", "ㅜ", "ㅣ", "ㅐ", "ㅔ", "ㅡ",           # 단모음(합성용)
           "ㅑ", "ㅕ", "ㅛ", "ㅠ", "ㅘ", "ㅝ", "ㅟ", "ㅚ", "ㅢ", "ㅒ", "ㅖ"]  # 이중모음
WORDS = ["야구", "여우", "요리", "우유", "얘기", "예의",
         "사과", "샤워", "외투", "가위", "의자",
         "이중모음", "반모음"]
SYMS = {"sym_arrow": "→", "sym_plus": "+"}


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
                    "VALUES (?,?,?,?,?, datetime('now'))", (name_kr, name_en, typ, fp, "generate_w5_glyphs.py"))
    else:
        cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                    (name_kr, name_en, typ, fp, "generate_w5_glyphs.py"))


def main():
    os.makedirs(LDIR, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    has = "created_at" in {r[1] for r in cur.execute("pragma table_info(assets)")}
    n = 0
    for j in LETTERS:
        render(j).save(os.path.join(LDIR, f"letter_{j}.png"))
        reg(cur, has, j, f"letter_{j}", "letter", f"graphics/letters/letter_{j}.png")
        n += 1
    for w in WORDS:
        render(w).save(os.path.join(LDIR, f"word_{w}.png"))
        reg(cur, has, w, f"word_{w}", "word", f"graphics/letters/word_{w}.png")
        n += 1
    for key, ch in SYMS.items():
        render(ch, color=(70, 70, 70, 255)).save(os.path.join(LDIR, f"{key}.png"))
        reg(cur, has, ch, key, "object", f"graphics/letters/{key}.png")
        n += 1
    con.commit()
    con.close()
    print(f"{n} W5 glyphs (letters+words+syms) generated + registered")


if __name__ == "__main__":
    main()
