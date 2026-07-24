# -*- coding: utf-8 -*-
"""W12 썸네일: W10/W11 스타일(LEARN KOREAN 배너+태극기+큰 한글 훅+표현칩+캐릭터).
교통·지하철 환승 / 인천공항→강남역 / 인준. 1280x720 <2MB. 한글교육임이 한눈에 보이게."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"; DONG = "assets/fonts/Cafe24Dongdong.ttf"

# 배경: 지하철 승강장(2호선 초록) — 주제가 바로 읽히게
bg = Image.open("assets/graphics/bg/bg_w12_platform_line2.png").convert("RGBA")
r = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width*r), int(bg.height*r)))
bg = bg.crop(((bg.width-W)//2, 0, (bg.width-W)//2+W, H))
canvas = Image.new("RGBA", (W, H), (0,0,0,0)); canvas.paste(bg, (0,0))

# 왼쪽 텍스트 영역 밝은 베일
veil = Image.new("RGBA", (W, H), (0,0,0,0)); vd = ImageDraw.Draw(veil)
for x in range(830):
    vd.line([(x,0),(x,H)], fill=(255,255,255, int(125*(1-x/830))))
canvas = Image.alpha_composite(canvas, veil)

# 인준(카드 태그 포즈 = 교통 주제가 바로 읽힘) — 오른쪽
ij = Image.open("assets/graphics/poses/injun_w12_tap_card.png").convert("RGBA")
a = np.array(ij); ys, xs = np.where(a[:,:,3] > 25)
ij = ij.crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1))
mh = 690; mw = int(ij.width*mh/ij.height); ij = ij.resize((mw, mh))
canvas.alpha_composite(ij, (W-mw-40, H-mh+6))
d = ImageDraw.Draw(canvas)

def outline(draw, xy, txt, font, fill, oc=(20,20,20,255), ow=8):
    x,y = xy
    for dx in range(-ow, ow+1, 2):
        for dy in range(-ow, ow+1, 2):
            draw.text((x+dx, y+dy), txt, font=font, fill=oc)
    draw.text((x,y), txt, font=font, fill=fill)

def taegukgi(draw, cx, cy, R):
    draw.ellipse([cx-R,cy-R,cx+R,cy+R], fill=(255,255,255,255), outline=(20,20,20,255), width=3)
    draw.pieslice([cx-R,cy-R,cx+R,cy+R], 180,360, fill=(205,40,50,255))
    draw.pieslice([cx-R,cy-R,cx+R,cy+R], 0,180, fill=(30,80,170,255))
    rr=R/2
    draw.ellipse([cx-R,cy-rr,cx,cy+rr], fill=(205,40,50,255))
    draw.ellipse([cx,cy-rr,cx+R,cy+rr], fill=(30,80,170,255))

# ① LEARN KOREAN 배너 (한글교육 채널임을 즉시 인지)
f_ban = ImageFont.truetype(MALGUN, 62); bx,by = 40,34; btxt = "LEARN KOREAN"
tw = d.textbbox((0,0), btxt, font=f_ban)[2]
d.rounded_rectangle([bx,by,bx+tw+150,by+92], radius=20, fill=(211,47,47,255), outline=(255,255,255,255), width=5)
taegukgi(d, bx+58, by+46, 34); d.text((bx+108,by+13), btxt, font=f_ban, fill=(255,255,255,255))
# ② 토픽 칩
outline(d, (48,150), "지하철·버스 한국어 · SUBWAY", ImageFont.truetype(MALGUN,44), (255,255,255,255), ow=5)
# ③ 큰 한글 훅 — 오늘의 핵심어 '환승'
outline(d, (46,208), "환승!", ImageFont.truetype(MALGUN,182), (255,224,66,255), ow=11)
# ④ 영어 뜻
outline(d, (52,432), '= "Transfer"', ImageFont.truetype(MALGUN,64), (255,255,255,255), ow=6)
# ⑤ 표현 칩(동동체)
outline(d, (50,534), "타다 · 환승 · 내리다 · 출구", ImageFont.truetype(DONG,52), (255,255,255,255), ow=5)
# 장소(우하단)
outline(d, (W-470,H-48), "인천공항 → 강남역 · Seoul", ImageFont.truetype(MALGUN,32), (255,255,255,255), ow=4)

out = "hangeul_birth_vowels/hangeul_w12_thumb.png"
canvas.convert("RGB").save(out, quality=92)
jpg = "hangeul_birth_vowels/thumb_w12_1280x720.jpg"
canvas.convert("RGB").save(jpg, quality=90)
print(f"썸네일: {jpg}  {W}x{H}  {os.path.getsize(jpg)//1024}KB")
