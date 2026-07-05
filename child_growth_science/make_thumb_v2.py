# -*- coding: utf-8 -*-
"""아이 키 성장 썸네일 v2 — 40초 프레임(새싹+키재기자) 베이스 + 큰 텍스트. KO/EN."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
CG = "D:/Entertainments/DevEnvironment/autovideo/child_growth_science"
ROOT = "D:/Entertainments/DevEnvironment/autovideo"
BASE = "scratch/cg_frames/thumb_base.png"
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"; IMPACT = r"C:\Windows\Fonts\impact.ttf"; ARIALBD = r"C:\Windows\Fonts\arialbd.ttf"
GOLD=(255,205,70); WHITE=(255,255,255); DARK=(35,55,40)

def dtext(d, xy, txt, font, fill, sw, glow=None):
    x,y=xy
    if glow:
        for dx in range(-sw-3,sw+4,2):
            for dy in range(-sw-3,sw+4,2):
                d.text((x+dx,y+dy),txt,font=font,fill=glow)
    d.text((x,y),txt,font=font,fill=fill,stroke_width=sw,stroke_fill=(20,35,25))

def build(lang, S=1):
    W,H=1280*S,720*S
    img=Image.open(os.path.join(ROOT,BASE)).convert("RGB").resize((W,H),Image.LANCZOS)
    # 좌측 가독성 위해 살짝 어둡게 그라데이션
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    for x in range(W):
        a=int(120*max(0,(1-x/(W*0.62))))
        od.line([(x,0),(x,H)],fill=(15,30,20,a))
    img=Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")
    d=ImageDraw.Draw(img)
    if lang=="ko":
        dtext(d,(48*S,90*S),"우리 아이 키",ImageFont.truetype(MALGUN,int(96*S)),WHITE,int(6*S),glow=(20,40,25))
        dtext(d,(48*S,205*S),"얼마나 클까?",ImageFont.truetype(MALGUN,int(112*S)),GOLD,int(7*S),glow=(120,70,10))
        # 하단 배지
        f3=ImageFont.truetype(MALGUN,int(40*S))
        d.rounded_rectangle([44*S,470*S,760*S,545*S],radius=14*S,fill=(30,90,55,255))
        d.text((66*S,483*S),"키 크는 과학, 부모 필독!",font=f3,fill=WHITE)
    else:
        dtext(d,(48*S,80*S),"HOW TALL",ImageFont.truetype(IMPACT,int(120*S)),WHITE,int(6*S),glow=(20,40,25))
        dtext(d,(48*S,215*S),"WILL THEY GROW?",ImageFont.truetype(IMPACT,int(84*S)),GOLD,int(6*S),glow=(120,70,10))
        f3=ImageFont.truetype(ARIALBD,int(38*S))
        d.rounded_rectangle([44*S,470*S,790*S,545*S],radius=14*S,fill=(30,90,55,255))
        d.text((66*S,483*S),"The Science of Height — for Parents",font=f3,fill=WHITE)
    # 로고
    try:
        sz=int(96*S); m=int(20*S)
        lg=Image.open(os.path.join(ROOT,"assets","drjay_ed_logo_circle.png")).convert("RGBA").resize((sz,sz),Image.LANCZOS)
        img.paste(lg,(W-sz-m,H-sz-m),lg)
    except Exception: pass
    out=os.path.join(CG,f"thumb_{lang}_1280x720.jpg" if S==1 else f"thumb_{lang}_4k.jpg")
    img.save(out,quality=93); print("saved",out,img.size)

for L in ["ko","en"]:
    build(L,1); build(L,3)
print("THUMB_DONE")
