# -*- coding: utf-8 -*-
"""정주행 썸네일 — 30초 프레임(뇌+척추 인체) 베이스 + 강한 텍스트. KO/EN."""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT="D:/Entertainments/DevEnvironment/autovideo"; BW=ROOT+"/binge_watching"
BASE="scratch/binge_frames/thumb_base.png"
MALGUN=r"C:\Windows\Fonts\malgunbd.ttf"; IMPACT=r"C:\Windows\Fonts\impact.ttf"; ARIALBD=r"C:\Windows\Fonts\arialbd.ttf"
GOLD=(255,205,70); WHITE=(255,255,255); RED=(220,50,50)
def dtext(d,xy,t,f,fill,sw,glow=None):
    x,y=xy
    if glow:
        for dx in range(-sw-3,sw+4,2):
            for dy in range(-sw-3,sw+4,2): d.text((x+dx,y+dy),t,font=f,fill=glow)
    d.text((x,y),t,font=f,fill=fill,stroke_width=sw,stroke_fill=(15,15,15))
def build(lang,S=1):
    W,H=1280*S,720*S
    img=Image.open(ROOT+"/"+BASE).convert("RGB").resize((W,H),Image.LANCZOS)
    # 좌측 가독성: 어두운 그라데이션(화이트보드라 살짝만)
    ov=Image.new("RGBA",(W,H),(0,0,0,0));od=ImageDraw.Draw(ov)
    for x in range(W):
        a=int(150*max(0,(1-x/(W*0.58))));od.line([(x,0),(x,H)],fill=(10,10,15,a))
    img=Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")
    d=ImageDraw.Draw(img)
    if lang=="ko":
        dtext(d,(46*S,70*S),"밤샘 정주행,",ImageFont.truetype(MALGUN,int(92*S)),WHITE,int(6*S),glow=(20,20,30))
        dtext(d,(46*S,180*S),"내 몸의 경고",ImageFont.truetype(MALGUN,int(108*S)),GOLD,int(7*S),glow=(120,70,10))
        f3=ImageFont.truetype(MALGUN,int(40*S));badge="뇌·수면·건강에 생기는 일"
        d.rounded_rectangle([44*S,320*S,44*S+d.textlength(badge,font=f3)+44*S,395*S],radius=14*S,fill=(200,40,40,255))
        d.text((66*S,333*S),badge,font=f3,fill=WHITE)
    else:
        dtext(d,(46*S,60*S),"BINGE-WATCHING",ImageFont.truetype(IMPACT,int(84*S)),WHITE,int(5*S),glow=(20,20,30))
        dtext(d,(46*S,175*S),"& YOUR BODY",ImageFont.truetype(IMPACT,int(100*S)),GOLD,int(6*S),glow=(120,70,10))
        f3=ImageFont.truetype(ARIALBD,int(38*S));badge="What It Does to Your Health"
        d.rounded_rectangle([44*S,320*S,44*S+d.textlength(badge,font=f3)+44*S,393*S],radius=14*S,fill=(200,40,40,255))
        d.text((66*S,333*S),badge,font=f3,fill=WHITE)
    # 원본 로고 겹침 제거: 우하단 덮고 큰 로고 하나
    sz=int(104*S);m=int(22*S)
    bgc=img.getpixel((W-sz-m-70*S, H-sz-m-70*S))
    d.rectangle([W-sz-m-40*S, H-sz-m-40*S, W-4, H-4], fill=bgc)
    try:
        lg=Image.open(ROOT+"/assets/drjay_ed_logo_circle.png").convert("RGBA").resize((sz,sz),Image.LANCZOS)
        img.paste(lg,(W-sz-m,H-sz-m),lg)
    except: pass
    out=f"{BW}/thumb_{lang}_1280x720.jpg" if S==1 else f"{BW}/thumb_{lang}_4k.jpg"
    img.save(out,quality=93);print("saved",out.split("/")[-1])
for L in ["ko","en"]:
    build(L,1);build(L,3)
print("DONE")
