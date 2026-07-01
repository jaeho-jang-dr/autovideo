#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_w4_glyphs.py — 4주차 "받침과 대표 7음" 글자/단어/기호 글리프 PNG + DB 등록.
 - 받침 낱자: ㄱㄴㄷㄹㅁㅂㅇ(대표7음) + ㅋㄲㅅㅈㅊㅌㅎㅍ(변하는 받침).
 - 예시 단어: 강 책 산 옷 물 곰 밥 부엌 꽃 앞.
 - 기호: sym_arrow(→). malgun bold 검정, 투명 배경. assets/graphics/letters/.
재실행: python generate_w4_glyphs.py
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

LETTERS = ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅇ",        # 대표 7음
           "ㅋ", "ㄲ", "ㅅ", "ㅈ", "ㅊ", "ㅌ", "ㅎ", "ㅍ",   # 변하는 받침
           "ㅏ"]                                            # 음절 조립 예시(강)용 모음
WORDS = ["강", "책", "산", "옷", "물", "곰", "밥", "부엌", "꽃", "앞",
         "받침", "대표7음"]
SYMS = {"sym_arrow": "→"}


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
                    "VALUES (?,?,?,?,?, datetime('now'))", (name_kr, name_en, typ, fp, "generate_w4_glyphs.py"))
    else:
        cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                    (name_kr, name_en, typ, fp, "generate_w4_glyphs.py"))


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
    print(f"{n} W4 glyphs (letters+words+syms) generated + registered")


if __name__ == "__main__":
    main()
