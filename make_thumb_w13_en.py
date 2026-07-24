# -*- coding: utf-8 -*-
"""W13 영어판 썸네일 — make_thumb_w13.py(한글판)과 같은 디자인, 텍스트만 영어.
   ★한글 훅('오른쪽?')은 유지: 한국어 교육 채널이라 한글이 주인공(발음/뜻은 영어로).
   1280x720 <2MB."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"; DONG = "assets/fonts/Cafe24Dongdong.ttf"

bg = Image.open("assets/graphics/bg/bg_w13_fork.png").convert("RGBA")
r = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width*r), int(bg.height*r)))
bg = bg.crop(((bg.width-W)//2, 0, (bg.width-W)//2+W, H))
canvas = Image.new("RGBA", (W, H), (0,0,0,0)); canvas.paste(bg, (0,0))

veil = Image.new("RGBA", (W, H), (0,0,0,0)); vd = ImageDraw.Draw(veil)
for x in range(830):
    vd.line([(x,0),(x,H)], fill=(255,255,255, int(130*(1-x/830))))
canvas = Image.alpha_composite(canvas, veil)

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

# ① LEARN KOREAN 배너 (동일)
f_ban = ImageFont.truetype(MALGUN, 62); bx,by = 40,34; btxt = "LEARN KOREAN"
tw = d.textbbox((0,0), btxt, font=f_ban)[2]
d.rounded_rectangle([bx,by,bx+tw+150,by+92], radius=20, fill=(211,47,47,255), outline=(255,255,255,255), width=5)
taegukgi(d, bx+58, by+46, 34); d.text((bx+108,by+13), btxt, font=f_ban, fill=(255,255,255,255))
# ② 토픽 칩 — ★영어
outline(d, (48,150), "ASKING DIRECTIONS", ImageFont.truetype(MALGUN,44), (255,255,255,255), ow=5)
# ③ 큰 한글 훅 (유지 — 한글이 주인공)
outline(d, (46,208), "오른쪽?", ImageFont.truetype(MALGUN,150), (255,224,66,255), ow=11)
# ④ 발음 + 뜻 — ★영어
outline(d, (52,392), '[o-reun-jjok] = "Right?"', ImageFont.truetype(MALGUN,54), (255,255,255,255), ow=6)
# ⑤ 표현 칩 — ★한글 + 영어 뜻
outline(d, (50,492), "Right · Left · Straight", ImageFont.truetype(MALGUN,50), (255,255,255,255), ow=5)
outline(d, (50,566), '"Say it again, please"', ImageFont.truetype(MALGUN,48), (255,255,255,255), ow=5)
# 장소(우하단) — ★영어
outline(d, (W-470,H-48), "Seongsan Ilchulbong · Jeju", ImageFont.truetype(MALGUN,32), (255,255,255,255), ow=4)

out = "hangeul_birth_vowels/hangeul_w13_thumb_en.png"
canvas.convert("RGB").save(out, quality=92)
jpg = "hangeul_birth_vowels/thumb_w13_en_1280x720.jpg"
canvas.convert("RGB").save(jpg, quality=90)
print(f"영어판 썸네일: {jpg}  {W}x{H}  {os.path.getsize(jpg)//1024}KB")
