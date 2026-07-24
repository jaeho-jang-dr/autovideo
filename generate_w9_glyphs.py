#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""generate_w9_glyphs.py — KO-W09 "위치·장소" 글자 PNG(동동체) + DB 등록.
 - 폰트: Cafe24Dongdong (사용자 지정 '글자 동동체').
 - 위치어/장소어 = word_<w>.png (크게), 예문/대화 = ex_<key>.png.
재실행: python generate_w9_glyphs.py
"""
import os, sys, sqlite3
from PIL import Image, ImageDraw, ImageFont
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

ROOT = os.path.dirname(os.path.abspath(__file__))
LDIR = os.path.join(ROOT, "assets", "graphics", "letters")
DB = os.path.join(ROOT, "channel", "content.db")
FONT = os.path.join(ROOT, "assets", "fonts", "Cafe24Dongdong.ttf")   # 동동체
os.makedirs(LDIR, exist_ok=True)

# 크게 보여줄 위치어/장소어
WORDS = ["앞", "뒤", "옆", "위", "밑", "안", "밖", "사이", "왼쪽", "오른쪽",
         "마트", "학교", "은행", "카페", "공원", "위치와 장소 표현"]

# 예문/대화  (파일키: 문장)
EX = {
 "학교앞에서만나요": "학교 앞에서 만나요",
 "집뒤에공원이있어요": "집 뒤에 공원이 있어요",
 "은행옆에카페가있어요": "은행 옆에 카페가 있어요",
 "책상위에책이있어요": "책상 위에 책이 있어요",
 "의자밑에가방이있어요": "의자 밑에 가방이 있어요",
 "가방안에책이있어요": "가방 안에 책이 있어요",
 "집밖에자동차가있어요": "집 밖에 자동차가 있어요",
 "은행과카페사이에있어요": "은행과 카페 사이에 있어요",
 "왼쪽에학교가있어요": "왼쪽에 학교가 있어요",
 "오른쪽에마트가있어요": "오른쪽에 마트가 있어요",
 "마트에서우유를사요": "마트에서 우유를 사요",
 "학교에걸어서가요": "학교에 걸어서 가요",
 "공원안에서산책해요": "공원 안에서 산책해요",
 "Q마트가어디에있어요": "마트가 어디에 있어요?",
 "A학교앞에있어요": "학교 앞에 있어요",
 "Q은행이어디에있어요": "은행이 어디에 있어요?",
 "A카페옆에있어요": "카페 옆에 있어요",
 "왼쪽으로가세요": "왼쪽으로 가세요",
 "학교앞에서오른쪽": "학교 앞에서 오른쪽",
}


def render(text, size=200, color=(40, 40, 46, 255)):
    f = ImageFont.truetype(FONT, size)
    tmp = Image.new("RGBA", (len(text) * (size + 30) + 80, int(size * 1.7)), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    b = d.textbbox((0, 0), text, font=f)
    d.text((40 - b[0], 40 - b[1]), text, font=f, fill=color)
    bb = tmp.split()[3].getbbox()
    pad = 16
    return tmp.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), bb[2] + pad, bb[3] + pad))


def reg(cur, has, name_kr, typ, fp):
    cur.execute("DELETE FROM assets WHERE file_path=?", (fp,))
    if has:
        cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt, created_at) "
                    "VALUES (?,?,?,?,?, datetime('now'))", (name_kr, name_kr, typ, fp, "generate_w9_glyphs.py"))
    else:
        cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                    (name_kr, name_kr, typ, fp, "generate_w9_glyphs.py"))


def main():
    con = sqlite3.connect(DB); cur = con.cursor()
    has = "created_at" in {r[1] for r in cur.execute("pragma table_info(assets)")}
    n = 0
    for w in WORDS:
        fn = f"word_{w}.png"
        render(w, size=200).save(os.path.join(LDIR, fn))
        reg(cur, has, w, "word", f"assets/graphics/letters/{fn}"); n += 1
    for key, sent in EX.items():
        fn = f"ex_{key}.png"
        render(sent, size=120).save(os.path.join(LDIR, fn))
        reg(cur, has, sent, "example", f"assets/graphics/letters/{fn}"); n += 1
    con.commit(); con.close()
    print(f"동동체 글자 {n}개 생성+등록 (WORDS {len(WORDS)} + EX {len(EX)}) → {LDIR}")


if __name__ == "__main__":
    main()
