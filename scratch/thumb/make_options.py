# -*- coding: utf-8 -*-
"""썸네일 3안(얼굴 제외) — S41 금빛반포 / S48 축제 / S15 즉위. 미리보기 1280x720 KO."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
ROOT="D:/Entertainments/DevEnvironment/autovideo"; OUT=os.path.join(ROOT,"scratch","thumb")
MALGUN=r"C:\Windows\Fonts\malgunbd.ttf"; W,H=1280,720
def font(s): return ImageFont.truetype(MALGUN,s)
def cover(im,cx=0.5):
    sc=max(W/im.width,H/im.height); im=im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
    l=int((im.width-W)*cx); t=(im.height-H)//2; return im.crop((l,t,l+W,t+H))
def dtext(base,xy,text,fnt,fill,sw=8,glow=None,anchor="lm"):
    x,y=xy
    if glow:
        g=Image.new("RGBA",base.size,(0,0,0,0)); ImageDraw.Draw(g).text((x,y),text,font=fnt,fill=glow+(255,),stroke_width=sw+2,stroke_fill=glow+(255,),anchor=anchor); base.alpha_composite(g.filter(ImageFilter.GaussianBlur(13)))
    s=Image.new("RGBA",base.size,(0,0,0,0)); ImageDraw.Draw(s).text((x+5,y+7),text,font=fnt,fill=(0,0,0,220),stroke_width=sw,stroke_fill=(0,0,0,220),anchor=anchor); base.alpha_composite(s.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(base).text((x,y),text,font=fnt,fill=fill,stroke_width=sw,stroke_fill=(12,16,32,255),anchor=anchor)
GOLD=(255,208,74,255); WHITE=(255,255,255,255)
def band_bottom(base):
    g=Image.new("L",(1,H),0)
    for y in range(H): g.putpixel((0,y),int(225*max(0,(y-H*0.42)/(H*0.58))))
    v=Image.new("RGBA",(W,H),(4,6,14,255)); v.putalpha(g.resize((W,H))); base.alpha_composite(v)
def jamo(base):
    jf=font(58)
    for ch,xx,yy in [("ㅎ",60,52),("ㅏ",132,48),("ㄴ",206,58),("ㄱ",278,46),("ㅡ",350,60),("ㄹ",420,50)]:
        dtext(base,(xx,yy),ch,jf,(255,225,120),sw=4,glow=(255,190,60))
def logo(base):
    # Veo ✦ 워터마크(클립 프레임 고정: 가로 89.9%, 세로 82.9%)를 반드시 덮도록 그 중심에 배치
    try:
        sz=int(0.095*W)                       # ~122px @1280 — 워터마크(~90px) 여유 있게 덮음
        wx,wy=int(0.899*W),int(0.829*H)
        l=Image.open(os.path.join(ROOT,"assets","drjay_ed_logo_circle.png")).convert("RGBA").resize((sz,sz),Image.LANCZOS)
        base.alpha_composite(l,(wx-sz//2, wy-sz//2))
    except Exception: pass
def build(key,src,cx,title_y=470):
    base=cover(Image.open(os.path.join(OUT,src)).convert("RGB"),cx).convert("RGBA")
    base=ImageEnhance.Contrast(base).enhance(1.06); base=ImageEnhance.Color(base).enhance(1.14)
    band_bottom(base); jamo(base)
    dtext(base,(64,title_y),"세종대왕과",font(96),WHITE,sw=8,glow=(20,30,60))
    dtext(base,(64,title_y+108),"한글",font(126),GOLD,sw=9,glow=(255,150,30))
    dtext(base,(68,title_y+205),"한글은 어떻게 태어났을까?",font(44),WHITE,sw=5)
    logo(base)
    p=os.path.join(OUT,f"opt_{key}.jpg"); base.convert("RGB").save(p,quality=92); print("saved",p)
build("A","cand_41.jpg",0.35)   # 금빛 반포: 왼쪽으로 크롭(세종 오른쪽 유지)
build("B","cand_48.jpg",0.5)    # 축제
build("C","cand_15.jpg",0.5)    # 즉위
