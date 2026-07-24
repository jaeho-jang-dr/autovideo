# -*- coding: utf-8 -*-
"""W14 썸네일 최종(A-1 확정): 하루 타임라인 띠 + 협재 바다 + 청록/화이트 큰 글자.
★사장님 지시: 마담제이는 왼쪽(글자 쪽)을 향한다. 기존 W10~13의 일률적 디자인 탈피.
개선: 캐릭터가 배경에 묻히지 않게 뒤에 밝은 원형 스포트 + 동사 칩 크게."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"; DONG = "assets/fonts/Cafe24Dongdong.ttf"

def outline(d, xy, txt, font, fill, oc=(12,70,90,255), ow=8):
    x, y = xy
    for dx in range(-ow, ow+1, 2):
        for dy in range(-ow, ow+1, 2):
            d.text((x+dx, y+dy), txt, font=font, fill=oc)
    d.text((x, y), txt, font=font, fill=fill)

def grad_v(size, c1, c2):
    w, h = size
    g = Image.new("RGB", (1, h)); dd = ImageDraw.Draw(g)
    for y in range(h):
        t = y / max(1, h-1)
        dd.point((0, y), fill=tuple(int(c1[i]*(1-t) + c2[i]*t) for i in range(3)))
    return g.resize((w, h), Image.BICUBIC)

# 배경: 협재 바다
bg = Image.open("assets/graphics/bg/bg_w14_sea.png").convert("RGB")
r = max(W/bg.width, H/bg.height); bg = bg.resize((int(bg.width*r), int(bg.height*r)))
c = bg.crop(((bg.width-W)//2, 0, (bg.width-W)//2+W, H)).convert("RGBA")

# 하단 어둡게(글자 대비)
sh = Image.new("RGBA", (W, H), (0,0,0,0)); sd = ImageDraw.Draw(sh)
for y in range(H//2, H):
    a = int(200 * (y - H//2) / (H//2))
    sd.line([(0,y),(W,y)], fill=(8,35,50,a))
c = Image.alpha_composite(c, sh)

# ① 상단 하루 타임라인 띠 (아침→낮→노을→밤)
SEGS = [((255,214,150),(255,178,102),"☀"), ((160,225,255),(90,190,235),"🏖"),
        ((255,160,120),(240,110,150),"🌇"), ((70,80,140),(30,35,80),"🌙")]
STRIP_H = 112
for i,(c1,c2,_) in enumerate(SEGS):
    c.paste(grad_v((W//4, STRIP_H), c1, c2).convert("RGBA"), (i*(W//4), 0))
d = ImageDraw.Draw(c)
for i in range(1,4):
    d.line([(i*(W//4),0),(i*(W//4),STRIP_H)], fill=(255,255,255,170), width=3)
try: fe = ImageFont.truetype("C:/Windows/Fonts/seguiemj.ttf", 34)
except Exception: fe = ImageFont.truetype(MALGUN, 28)
for i,(_,_,ic) in enumerate(SEGS):
    cx = i*(W//4) + (W//8); cy = STRIP_H//2
    d.ellipse([cx-30,cy-30,cx+30,cy+30], fill=(255,255,255,240), outline=(30,30,35,255), width=3)
    bb = d.textbbox((0,0), ic, font=fe)
    d.text((cx-(bb[2]-bb[0])//2, cy-(bb[3]-bb[1])//2-5), ic, font=fe, fill=(45,45,50), embedded_color=True)

# ② 캐릭터 뒤 밝은 스포트(배경에 묻히지 않게)
spot = Image.new("RGBA", (W,H), (0,0,0,0)); sp = ImageDraw.Draw(spot)
sp.ellipse([W-470, 140, W-10, 720], fill=(255,255,255,90))
c = Image.alpha_composite(c, spot)

# ③ 마담제이 — ★왼쪽(글자 쪽)을 향하게 리버스
mj = Image.open("assets/graphics/poses/mj_presenting.png").convert("RGBA")
a = np.array(mj); ys, xs = np.where(a[:,:,3] > 25)
mj = mj.crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1))
mj = mj.transpose(Image.FLIP_LEFT_RIGHT)                 # ★왼쪽 향함
mh = 470; mw = int(mj.width*mh/mj.height)
mj = mj.resize((mw, mh), Image.LANCZOS)
c.alpha_composite(mj, (W-mw-45, H-mh-8))
d = ImageDraw.Draw(c)

# ④ LEARN KOREAN 뱃지(빨간 배너 대신 청록 알약)
d.rounded_rectangle([38,132,306,186], radius=27, fill=(18,178,190,255), outline=(255,255,255,255), width=4)
d.text((60,143), "LEARN KOREAN", font=ImageFont.truetype(MALGUN,27), fill=(255,255,255,255))

# ⑤ 큰 글자 — 화이트 + 청록 그림자
outline(d, (40, 372), "나의 하루", ImageFont.truetype(MALGUN, 150), (255,255,255,255), oc=(10,88,110,255), ow=10)
outline(d, (46, 542), "My Daily Routine", ImageFont.truetype(MALGUN, 56), (110,240,232,255), oc=(8,58,78,255), ow=6)

# ⑥ 동사 칩(크게 — 배울 내용이 바로 읽히게)
chips = ["일어나다", "일하다", "자다"]
x = 46
for t in chips:
    fw = ImageFont.truetype(DONG, 44)
    tw = int(d.textlength(t, font=fw))
    d.rounded_rectangle([x, 626, x+tw+46, 692], radius=33, fill=(255,255,255,238), outline=(18,178,190,255), width=4)
    d.text((x+23, 634), t, font=fw, fill=(12,86,100))
    x += tw + 68

out = "hangeul_birth_vowels/hangeul_w14_thumb.png"
c.convert("RGB").save(out, quality=92)
jpg = "hangeul_birth_vowels/thumb_w14_1280x720.jpg"
c.convert("RGB").save(jpg, quality=90)
print(f"썸네일: {jpg}  {W}x{H}  {os.path.getsize(jpg)//1024}KB")
