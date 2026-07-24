# -*- coding: utf-8 -*-
"""한글강의 W1 썸네일 KO/EN — 천지인(단모음 원리) 히어로 + 볼드 타이틀. 1280x720."""
import os
from PIL import Image, ImageDraw, ImageFont
FB = r"C:\Windows\Fonts\malgunbd.ttf"
W, H = 1280, 720
LOGO = "assets/drjay_ed_logo_circle.png"

def cover(im, w, h):
    r = max(w/im.width, h/im.height)
    im2 = im.resize((int(im.width*r), int(im.height*r)), Image.LANCZOS)
    x=(im2.width-w)//2; y=(im2.height-h)//2
    return im2.crop((x, y, x+w, y+h))

def vgrad(w, h, top_a, bot_a):
    g = Image.new("L",(1,h))
    for y in range(h):
        g.putpixel((0,y), int(top_a+(bot_a-top_a)*(y/(h-1))))
    return g.resize((w,h))

def fit(text, size, maxw):
    while size>28:
        f=ImageFont.truetype(FB,size)
        if ImageDraw.Draw(Image.new("RGB",(9,9))).textlength(text,font=f)<=maxw: return f
        size-=2
    return ImageFont.truetype(FB,size)

def stroke(d,xy,t,f,fill,sw=6):
    d.text(xy,t,font=f,fill=fill,stroke_width=sw,stroke_fill=(20,20,25))

def make(hero, lines, accent, sub, out):
    img=cover(Image.open(hero).convert("RGB"), W, H)
    img.paste(Image.new("RGB",(W,200),(10,10,20)),(0,0),vgrad(W,200,120,0))
    img.paste(Image.new("RGB",(W,430),(6,6,16)),(0,H-430),vgrad(W,430,0,235))
    d=ImageDraw.Draw(img)
    fs=94 if len(max(lines,key=len))<15 else 76
    fonts=[fit(t,fs,W-120) for t in lines]
    lh=max(f.size for f in fonts)+10
    y=H-58-lh*len(lines)
    for t,f in zip(lines,fonts):
        if accent and accent in t:
            pre,post=t.split(accent,1); x=60
            stroke(d,(x,y),pre,f,(255,255,255)); x+=d.textlength(pre,font=f)
            stroke(d,(x,y),accent,f,(255,214,10)); x+=d.textlength(accent,font=f)
            stroke(d,(x,y),post,f,(255,255,255))
        else: stroke(d,(60,y),t,f,(255,255,255))
        y+=lh
    sf=fit(sub,38,W-120); stroke(d,(62,H-52),sub,sf,(232,232,238),sw=4)
    try:
        lg=Image.open(LOGO).convert("RGBA").resize((104,104)); img.paste(lg,(W-126,22),lg)
    except Exception: pass
    img.save(out,quality=92); print("saved",out,flush=True)

make("scratch/thumb_w1/ko_62.jpg", ["한글의 탄생과", "단모음의 비밀"], "단모음",
     "세종대왕과 훈민정음 · 한국어 W1", "hangeul_birth_vowels/thumb_w1_ko.jpg")
make("scratch/thumb_w1/en_62.jpg", ["The Birth of Hangeul", "& Its Vowels"], "Hangeul",
     "King Sejong's Alphabet · Learn Korean W1", "hangeul_birth_vowels/thumb_w1_en.jpg")
print("THUMBS_DONE", flush=True)
