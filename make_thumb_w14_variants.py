# -*- coding: utf-8 -*-
"""W14 썸네일 A안(하루 타임라인) 시안 4종 — 기존 일률적 디자인 탈피.
사장님 지시: 레이아웃·글자 크기·색상 확 바꾸기. 빨간 배너 축소/변형, 노란 글자 탈피."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"; DONG = "assets/fonts/Cafe24Dongdong.ttf"
OUT = "scratch/w14_thumbs"; os.makedirs(OUT, exist_ok=True)

def load_char(name="mj_presenting.png", h=560, flip=False):
    """flip=True → 좌우 반전(왼쪽을 향하게). 오른쪽에 선 캐릭터가 왼쪽 글자를 바라보도록."""
    p = f"assets/graphics/poses/{name}"
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert("RGBA")
    a = np.array(im); ys, xs = np.where(a[:, :, 3] > 25)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    w = int(im.width * h / im.height)
    return im.resize((w, h), Image.LANCZOS)

def outline(d, xy, txt, font, fill, oc=(25,25,30,255), ow=7):
    x, y = xy
    for dx in range(-ow, ow+1, 2):
        for dy in range(-ow, ow+1, 2):
            d.text((x+dx, y+dy), txt, font=font, fill=oc)
    d.text((x, y), txt, font=font, fill=fill)

def grad_v(size, c1, c2):
    w, h = size
    g = Image.new("RGB", (1, h))
    dd = ImageDraw.Draw(g)
    for y in range(h):
        t = y / max(1, h-1)
        dd.point((0, y), fill=tuple(int(c1[i]*(1-t) + c2[i]*t) for i in range(3)))
    return g.resize((w, h), Image.BICUBIC)

def timeline_strip(canvas, y0, h, segs):
    """상단 하루 타임라인 띠: 아침→낮→노을→밤 그라데이션 + 구분선"""
    d = ImageDraw.Draw(canvas)
    n = len(segs)
    sw = W // n
    for i, (c1, c2, icon) in enumerate(segs):
        g = grad_v((sw, h), c1, c2).convert("RGBA")
        canvas.paste(g, (i*sw, y0))
    d = ImageDraw.Draw(canvas)
    for i in range(1, n):
        d.line([(i*sw, y0), (i*sw, y0+h)], fill=(255,255,255,160), width=3)
    # 아이콘(원형)
    for i, (c1, c2, icon) in enumerate(segs):
        cx = i*sw + sw//2; cy = y0 + h//2
        d.ellipse([cx-26, cy-26, cx+26, cy+26], fill=(255,255,255,235), outline=(30,30,35,255), width=3)
        try:
            fe = ImageFont.truetype("C:/Windows/Fonts/seguiemj.ttf", 30)
        except Exception:
            fe = ImageFont.truetype(MALGUN, 26)
        bb = d.textbbox((0,0), icon, font=fe)
        d.text((cx-(bb[2]-bb[0])//2, cy-(bb[3]-bb[1])//2-4), icon, font=fe, fill=(40,40,45), embedded_color=True)

SEGS = [((255,214,150),(255,178,102),"☀"),   # 아침
        ((160,225,255),(90,190,235),"🏖"),   # 낮
        ((255,160,120),(240,110,150),"🌇"),  # 노을
        ((70,80,140),(30,35,80),"🌙")]       # 밤

# ─────────────────────────────────────────────────────────────
# 시안 1: 타임라인 상단 띠 + 중앙하단 큰 글자(화이트) + 청록 강조
def v1():
    bg = Image.open("assets/graphics/bg/bg_w14_sea.png").convert("RGB") if os.path.exists("assets/graphics/bg/bg_w14_sea.png") \
         else Image.new("RGB",(W,H),(120,200,215))
    r = max(W/bg.width, H/bg.height); bg = bg.resize((int(bg.width*r), int(bg.height*r)))
    bg = bg.crop(((bg.width-W)//2, 0, (bg.width-W)//2+W, H)).convert("RGBA")
    c = bg.copy()
    # 하단 어둡게(글자 대비)
    sh = Image.new("RGBA",(W,H),(0,0,0,0)); sd = ImageDraw.Draw(sh)
    for y in range(H//2, H):
        a = int(190 * (y-H//2)/(H//2))
        sd.line([(0,y),(W,y)], fill=(10,30,45,a))
    c = Image.alpha_composite(c, sh)
    timeline_strip(c, 0, 108, SEGS)
    ch = load_char("mj_presenting.png", 430, flip=True)   # ★왼쪽 향하게(글자 쪽을 바라봄)
    if ch: c.alpha_composite(ch, (W-ch.width-40, H-ch.height-10))
    d = ImageDraw.Draw(c)
    # 작은 뱃지(빨간 배너 대신)
    d.rounded_rectangle([36,128,296,178], radius=25, fill=(20,180,190,255), outline=(255,255,255,255), width=4)
    d.text((58,138), "LEARN KOREAN", font=ImageFont.truetype(MALGUN,26), fill=(255,255,255,255))
    # 중앙하단 큰 글자 — 화이트 + 청록 그림자
    outline(d, (40, 380), "나의 하루", ImageFont.truetype(MALGUN, 148), (255,255,255,255), oc=(10,90,110,255), ow=10)
    outline(d, (46, 545), "My Daily Routine", ImageFont.truetype(MALGUN, 58), (120,240,235,255), oc=(10,50,70,255), ow=6)
    outline(d, (48, 630), "일어나다 · 일하다 · 자다", ImageFont.truetype(DONG, 44), (255,255,255,255), oc=(10,60,80,255), ow=5)
    c.convert("RGB").save(f"{OUT}/v1_timeline_teal.jpg", quality=90)

# 시안 2: 노을 그라데이션 배경 + 세로 큰 글자 + 시간 아이콘 세로열
def v2():
    c = grad_v((W,H), (255,190,120), (255,110,150)).convert("RGBA")
    bgp = "assets/graphics/bg/bg_w14_sunset.png"
    if os.path.exists(bgp):
        bg = Image.open(bgp).convert("RGB")
        r = max(W/bg.width, H/bg.height); bg = bg.resize((int(bg.width*r), int(bg.height*r)))
        bg = bg.crop(((bg.width-W)//2, 0, (bg.width-W)//2+W, H)).convert("RGBA")
        bg.putalpha(150); c = Image.alpha_composite(c, bg)
    ch = load_char("mj_presenting.png", 620)
    if ch: c.alpha_composite(ch, (W-ch.width-60, H-ch.height))
    d = ImageDraw.Draw(c)
    # 좌측 세로 시간 아이콘
    try: fe = ImageFont.truetype("C:/Windows/Fonts/seguiemj.ttf", 40)
    except Exception: fe = ImageFont.truetype(MALGUN, 34)
    for i, ic in enumerate(["☀","🏖","🌇","🌙"]):
        cy = 160 + i*130
        d.ellipse([40,cy-34,108,cy+34], fill=(255,255,255,235), outline=(60,40,60,255), width=3)
        d.text((58,cy-24), ic, font=fe, fill=(50,40,50), embedded_color=True)
    # 큰 글자 — 딥네이비 + 화이트 아웃라인(노랑 탈피)
    outline(d, (150, 130), "나의", ImageFont.truetype(MALGUN, 130), (30,40,90,255), oc=(255,255,255,255), ow=9)
    outline(d, (150, 275), "하루", ImageFont.truetype(MALGUN, 130), (30,40,90,255), oc=(255,255,255,255), ow=9)
    outline(d, (152, 430), "My Day in Korean", ImageFont.truetype(MALGUN, 52), (255,255,255,255), oc=(120,50,80,255), ow=6)
    outline(d, (154, 520), "아침부터 밤까지", ImageFont.truetype(DONG, 52), (255,240,180,255), oc=(120,50,80,255), ow=5)
    d.rounded_rectangle([150,610,470,668], radius=29, fill=(255,255,255,240), outline=(30,40,90,255), width=4)
    d.text((172,622), "LEARN KOREAN", font=ImageFont.truetype(MALGUN,30), fill=(30,40,90,255))
    c.convert("RGB").save(f"{OUT}/v2_sunset_vertical.jpg", quality=90)

# 시안 3: 좌우 분할(아침/밤) + 중앙 캐릭터 + 하단 띠
def v3():
    c = Image.new("RGBA",(W,H))
    day = "assets/graphics/bg/bg_w14_window.png"; night = "assets/graphics/bg/bg_w14_night_sky.png"
    def half(p, fb):
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            r = max((W//2)/im.width, H/im.height); im = im.resize((int(im.width*r), int(im.height*r)))
            return im.crop((0,0,W//2,H)).convert("RGBA")
        return Image.new("RGBA",(W//2,H), fb)
    c.paste(half(day,(255,220,160,255)), (0,0))
    c.paste(half(night,(30,35,80,255)), (W//2,0))
    d = ImageDraw.Draw(c)
    d.line([(W//2,0),(W//2,H)], fill=(255,255,255,220), width=6)
    ch = load_char("mj_presenting.png", 560)
    if ch: c.alpha_composite(ch, ((W-ch.width)//2, H-ch.height-6))
    # 상단 라벨
    outline(d,(60,40),"아침", ImageFont.truetype(MALGUN,86),(255,255,255,255),oc=(200,120,40,255),ow=8)
    outline(d,(W-250,40),"밤", ImageFont.truetype(MALGUN,86),(255,255,255,255),oc=(20,25,60,255),ow=8)
    # 하단 큰 글자 띠
    d.rectangle([0,H-150,W,H], fill=(15,25,45,225))
    outline(d,(40,H-136),"나의 하루 일과", ImageFont.truetype(MALGUN,84),(255,255,255,255),oc=(0,0,0,255),ow=6)
    d.text((44,H-42), "Daily Routine in Korean · 일어나다 · 자다", font=ImageFont.truetype(DONG,34), fill=(140,235,225))
    c.convert("RGB").save(f"{OUT}/v3_split_day_night.jpg", quality=90)

# 시안 4: 타임라인 띠 하단 + 대형 숫자시계 느낌 + 민트/코랄 대비
def v4():
    bgp = "assets/graphics/bg/bg_w14_beach.png"
    if os.path.exists(bgp):
        bg = Image.open(bgp).convert("RGB")
        r = max(W/bg.width, H/bg.height); bg = bg.resize((int(bg.width*r), int(bg.height*r)))
        c = bg.crop(((bg.width-W)//2,0,(bg.width-W)//2+W,H)).convert("RGBA")
    else:
        c = Image.new("RGBA",(W,H),(150,225,225,255))
    # 좌측 반투명 코랄 패널(캐릭터 색과 조화)
    pan = Image.new("RGBA",(W,H),(0,0,0,0)); pd=ImageDraw.Draw(pan)
    pd.polygon([(0,0),(700,0),(560,H),(0,H)], fill=(255,120,100,205))
    c = Image.alpha_composite(c, pan)
    ch = load_char("mj_presenting.png", 600)
    if ch: c.alpha_composite(ch, (W-ch.width-30, H-ch.height))
    d = ImageDraw.Draw(c)
    outline(d,(50,60),"나의 하루", ImageFont.truetype(MALGUN,120),(255,255,255,255),oc=(150,40,30,255),ow=9)
    outline(d,(54,205),"일과와 동작", ImageFont.truetype(MALGUN,76),(255,240,170,255),oc=(150,40,30,255),ow=7)
    # 동사 칩(민트)
    chips=["일어나다","공부하다","일하다","자다"]
    for i,t in enumerate(chips):
        y=330+i*78
        d.rounded_rectangle([50,y,430,y+62], radius=31, fill=(60,215,200,240), outline=(255,255,255,255), width=3)
        d.text((78,y+10), t, font=ImageFont.truetype(DONG,42), fill=(15,60,60))
    timeline_strip(c, H-90, 90, SEGS)
    c.convert("RGB").save(f"{OUT}/v4_coral_chips.jpg", quality=90)

for f in (v1, v2, v3, v4):
    try:
        f(); print("  ✅", f.__name__)
    except Exception as e:
        print("  ✗", f.__name__, str(e)[:70])
print("시안 폴더:", OUT)
