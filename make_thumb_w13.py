# -*- coding: utf-8 -*-
"""W13 썸네일: W10/W11/W12 스타일(LEARN KOREAN 배너+태극기+큰 한글 훅+표현칩+캐릭터).
길 찾기·위치 안내 / 성산일출봉 / 지은. 1280x720 <2MB."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"; DONG = "assets/fonts/Cafe24Dongdong.ttf"

# 배경: 갈림길(길 찾기 주제가 바로 읽힘) — 성산일출봉 보이는 컷
bg = Image.open("assets/graphics/bg/bg_w13_fork.png").convert("RGBA")
r = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width*r), int(bg.height*r)))
bg = bg.crop(((bg.width-W)//2, 0, (bg.width-W)//2+W, H))
canvas = Image.new("RGBA", (W, H), (0,0,0,0)); canvas.paste(bg, (0,0))

# 왼쪽 텍스트 영역 밝은 베일
veil = Image.new("RGBA", (W, H), (0,0,0,0)); vd = ImageDraw.Draw(veil)
for x in range(830):
    vd.line([(x,0),(x,H)], fill=(255,255,255, int(130*(1-x/830))))
canvas = Image.alpha_composite(canvas, veil)

# 지은(오른쪽 가리키는 포즈 = 길 안내 주제가 바로 읽힘) — 오른쪽
je = Image.open("assets/graphics/poses/jieun_w13_point_right.png").convert("RGBA")
a = np.array(je); ys, xs = np.where(a[:,:,3] > 25)
je = je.crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1))
mh = 690; mw = int(je.width*mh/je.height); je = je.resize((mw, mh))
canvas.alpha_composite(je, (W-mw-30, H-mh+6))
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

# ① LEARN KOREAN 배너
f_ban = ImageFont.truetype(MALGUN, 62); bx,by = 40,34; btxt = "LEARN KOREAN"
tw = d.textbbox((0,0), btxt, font=f_ban)[2]
d.rounded_rectangle([bx,by,bx+tw+150,by+92], radius=20, fill=(211,47,47,255), outline=(255,255,255,255), width=5)
taegukgi(d, bx+58, by+46, 34); d.text((bx+108,by+13), btxt, font=f_ban, fill=(255,255,255,255))
# ② 토픽 칩
outline(d, (48,150), "길 찾기 한국어 · DIRECTIONS", ImageFont.truetype(MALGUN,44), (255,255,255,255), ow=5)
# ③ 큰 한글 훅 — 오늘의 핵심어
outline(d, (46,208), "오른쪽?", ImageFont.truetype(MALGUN,150), (255,224,66,255), ow=11)
# ④ 영어 뜻
outline(d, (52,392), '= "Right or Left?"', ImageFont.truetype(MALGUN,58), (255,255,255,255), ow=6)
# ⑤ 표현 칩(동동체)
outline(d, (50,492), "오른쪽 · 왼쪽 · 똑바로", ImageFont.truetype(DONG,52), (255,255,255,255), ow=5)
outline(d, (50,566), "다시 말해 주세요", ImageFont.truetype(DONG,52), (255,255,255,255), ow=5)
# 장소(우하단)
outline(d, (W-450,H-48), "성산일출봉 · Jeju", ImageFont.truetype(MALGUN,32), (255,255,255,255), ow=4)

out = "hangeul_birth_vowels/hangeul_w13_thumb.png"
canvas.convert("RGB").save(out, quality=92)
jpg = "hangeul_birth_vowels/thumb_w13_1280x720.jpg"
canvas.convert("RGB").save(jpg, quality=90)
print(f"썸네일: {jpg}  {W}x{H}  {os.path.getsize(jpg)//1024}KB")
