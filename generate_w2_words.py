#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_w2_words.py — 2주차 모아쓰기 시연용 음절/단어 글자를 글리프 PNG로 렌더 + DB 등록.
malgun bold 검정 글자, 투명 배경. assets/graphics/letters/word_<X>.png. type='word'.
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

WORDS = ["가", "나", "머", "디", "고", "누", "드", "기",
         "고기", "누나", "머리", "바나나", "아버지", "어머니", "오이", "호수", "지도"]


def render(text):
    f = ImageFont.truetype(FONT, 200)
    tmp = Image.new("RGBA", (len(text) * 230 + 80, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    b = d.textbbox((0, 0), text, font=f)
    d.text((40 - b[0], 40 - b[1]), text, font=f, fill=(28, 28, 28, 255))
    bb = tmp.split()[3].getbbox()
    pad = 16
    crop = tmp.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), bb[2] + pad, bb[3] + pad))
    return crop


def main():
    os.makedirs(LDIR, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    has_created = "created_at" in {r[1] for r in cur.execute("pragma table_info(assets)")}
    n = 0
    for w in WORDS:
        im = render(w)
        fn = f"word_{w}.png"
        im.save(os.path.join(LDIR, fn))
        fp = f"graphics/letters/{fn}"
        cur.execute("DELETE FROM assets WHERE file_path=?", (fp,))
        if has_created:
            cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt, created_at) "
                        "VALUES (?,?,?,?,?, datetime('now'))", (w, f"word_{w}", "word", fp, "generate_w2_words.py glyph"))
        else:
            cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                        (w, f"word_{w}", "word", fp, "generate_w2_words.py glyph"))
        print(f"  {w} -> {fn} {im.size}")
        n += 1
    con.commit()
    con.close()
    print(f"\n{n} word glyphs generated + registered")


if __name__ == "__main__":
    main()
