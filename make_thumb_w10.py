# -*- coding: utf-8 -*-
"""W10 썸네일 v2: '한글 공부'가 한눈에 보이게 — LEARN KOREAN 배너 강조 + 큰 한글 훅. 1280x720 <2MB."""
import os
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"
DONG = "assets/fonts/Cafe24Dongdong.ttf"

# 배경(광안대교 해변) cover-fit
bg = Image.open("assets/graphics/bg/bg_w10_beach.png").convert("RGBA")
r = max(W / bg.width, H / bg.height)
bg = bg.resize((int(bg.width * r), int(bg.height * r)))
bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H))
canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0)); canvas.paste(bg, (0, 0))

# 왼쪽 텍스트 영역 밝은 베일
veil = Image.new("RGBA", (W, H), (0, 0, 0, 0)); vd = ImageDraw.Draw(veil)
for x in range(780):
    vd.line([(x, 0), (x, H)], fill=(255, 255, 255, int(105 * (1 - x / 780))))
canvas = Image.alpha_composite(canvas, veil)
d = ImageDraw.Draw(canvas)

# 인준(오른쪽) — 손 흔들기(친근)
inj = Image.open("assets/graphics/poses/injun_w10_wave_right.png").convert("RGBA")
ih = 640; iw = int(inj.width * ih / inj.height); inj = inj.resize((iw, ih))
canvas.alpha_composite(inj, (W - iw - 20, H - ih - 0)); d = ImageDraw.Draw(canvas)

def outline(draw, xy, txt, font, fill, oc=(20, 20, 20, 255), ow=8):
    x, y = xy
    for dx in range(-ow, ow + 1, 2):
        for dy in range(-ow, ow + 1, 2):
            draw.text((x + dx, y + dy), txt, font=font, fill=oc)
    draw.text((x, y), txt, font=font, fill=fill)

def taegukgi(draw, cx, cy, R):
    # 간단 태극기 원(빨강 위/파랑 아래)
    draw.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(255,255,255,255), outline=(20,20,20,255), width=3)
    draw.pieslice([cx-R, cy-R, cx+R, cy+R], 180, 360, fill=(205,40,50,255))   # 위 빨강
    draw.pieslice([cx-R, cy-R, cx+R, cy+R], 0, 180, fill=(30,80,170,255))     # 아래 파랑
    rr = R/2
    draw.ellipse([cx-R, cy-rr, cx, cy+rr], fill=(205,40,50,255))
    draw.ellipse([cx, cy-rr, cx+R, cy+rr], fill=(30,80,170,255))

# ① LEARN KOREAN 배너(빨강, 최상단 — 한글공부임을 즉시)
f_ban = ImageFont.truetype(MALGUN, 62)
bx, by = 40, 34
btxt = "LEARN KOREAN"
tw = d.textbbox((0,0), btxt, font=f_ban)[2]
d.rounded_rectangle([bx, by, bx+tw+150, by+92], radius=20, fill=(211,47,47,255), outline=(255,255,255,255), width=5)
taegukgi(d, bx+58, by+46, 34)
d.text((bx+108, by+13), btxt, font=f_ban, fill=(255,255,255,255))

# ② 토픽 칩
f_top = ImageFont.truetype(MALGUN, 46)
outline(d, (48, 150), "한국어 쇼핑 회화 · SHOPPING", f_top, (255,255,255,255), ow=5)

# ③ 큰 한글 훅
f_hook = ImageFont.truetype(MALGUN, 176)
outline(d, (42, 210), "얼마예요?", f_hook, (255, 224, 66, 255), ow=11)

# ④ 영어 뜻
f_en = ImageFont.truetype(MALGUN, 64)
outline(d, (50, 420), "= \"How much?\"", f_en, (255,255,255,255), ow=6)

# ⑤ 표현 칩(동동체)
f_chip = ImageFont.truetype(DONG, 50)
outline(d, (50, 520), "이거 주세요 · 결제 · 할인", f_chip, (255,255,255,255), ow=5)

# 장소(우하단)
f_place = ImageFont.truetype(MALGUN, 32)
outline(d, (W-350, H-48), "광안리 · Gwangalli", f_place, (255,255,255,255), ow=4)

out = "hangeul_birth_vowels/hangeul_w10_thumb.png"
canvas.convert("RGB").save(out, quality=90)
print(f"썸네일 v2: {out}  {W}x{H}  {os.path.getsize(out)//1024}KB")
