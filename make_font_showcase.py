#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_font_showcase.py — 글씨랑 6종 폰트 한눈에 비교 시트(항상 참고용).
자모·단어·문장·숫자를 6종 폰트로 나란히 렌더. 출력: scratch/geulssirang_fonts.png
재실행: python make_font_showcase.py
"""
import os, sqlite3
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")

# DB에서 6종 폰트 로드
con = sqlite3.connect(DB)
FONTS = [(r[0], r[1], os.path.join(ROOT, r[2]), r[3])
         for r in con.execute("SELECT korean_name, family, file_path, use_for FROM hangeul_fonts ORDER BY id")]
con.close()

SAMPLES = [
    ("자음", "ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅅ ㅇ ㅈ ㅊ ㅋ ㅌ ㅍ ㅎ"),
    ("모음", "ㅏ ㅑ ㅓ ㅕ ㅗ ㅛ ㅜ ㅠ ㅡ ㅣ ㅐ ㅔ"),
    ("받침 대표음", "강 책 산 옷 물 곰 밥"),
    ("이중모음", "야 여 요 유 와 워 외 위 의"),
    ("단어", "한글 받침 대표 7음 이중모음"),
    ("문장", "오늘은 받침을 배워요."),
    ("숫자·영문", "0123456789  ABC  Hello"),
]

LABELW = 300          # 왼쪽 폰트명 칸
COLW = 1200           # 샘플 렌더 폭
ROWH = 150            # 각 폰트 행 높이
HEADH = 60            # 샘플 헤더 높이
PAD = 30
SAMPLE_SIZE = 62

labelfont = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 30)
subfont = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 18)
headfont = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 26)

# 캔버스: 각 샘플마다 (헤더 + 6폰트 행)
block_h = HEADH + ROWH * len(FONTS) + 20
W = LABELW + COLW + PAD * 2
H = PAD * 2 + block_h * len(SAMPLES) + 80

img = Image.new("RGB", (W, H), (250, 249, 245))
d = ImageDraw.Draw(img)

# 제목
d.text((PAD, 20), "글씨랑 Geulssirang — 6종 글자체 비교", font=ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 38), fill=(30, 30, 40))
y = 80

for stitle, stext in SAMPLES:
    # 샘플 헤더 밴드
    d.rectangle([PAD, y, W - PAD, y + HEADH], fill=(232, 236, 244))
    d.text((PAD + 16, y + 14), f"◆ {stitle}", font=headfont, fill=(40, 60, 110))
    y += HEADH + 6
    for kname, family, path, use in FONTS:
        # 왼쪽: 폰트명 + 용도
        d.text((PAD + 8, y + ROWH // 2 - 30), kname, font=labelfont, fill=(20, 20, 20))
        d.text((PAD + 8, y + ROWH // 2 + 8), use, font=subfont, fill=(150, 150, 150))
        # 오른쪽: 샘플 렌더
        try:
            f = ImageFont.truetype(path, SAMPLE_SIZE)
            d.text((LABELW + PAD, y + ROWH // 2 - SAMPLE_SIZE // 2 - 6), stext, font=f, fill=(28, 26, 30))
        except Exception as e:
            d.text((LABELW + PAD, y + 40), f"[로드실패 {e}]", font=subfont, fill=(200, 0, 0))
        # 구분선
        d.line([(PAD, y + ROWH), (W - PAD, y + ROWH)], fill=(230, 228, 222), width=1)
        y += ROWH
    y += 20

out = os.path.join(ROOT, "scratch", "geulssirang_fonts.png")
img.save(out)
print("showcase ->", out, img.size)
