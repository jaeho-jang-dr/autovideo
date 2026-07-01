# -*- coding: utf-8 -*-
"""최종 A안 썸네일 — S41 금빛반포. 글자 축소+간격, 로고 최소크기로 워터마크 덮음. 영/한 · YT(1280x720)+4K(3840x2160)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
ROOT="D:/Entertainments/DevEnvironment/autovideo"; OUT=os.path.join(ROOT,"scratch","thumb")
MALGUN=r"C:\Windows\Fonts\malgunbd.ttf"; IMPACT=r"C:\Windows\Fonts\impact.ttf"; ARIALBD=r"C:\Windows\Fonts\arialbd.ttf"
BASE="cand_41.jpg"
WM_CX, WM_CY = 0.898, 0.834      # Veo ✦ 워터마크 중심 비율(클립 프레임)
LOGO_R = 0.080                   # 로고 크기 = 0.08*W (≈102px@1280) — 워터마크(~90px) 최소 덮기
GOLD=(255,208,74,255); WHITE=(255,255,255,255)

def font(p,s):
    try: return ImageFont.truetype(p,s)
    except Exception: return ImageFont.truetype(MALGUN,s)
def cover(im,W,H):
    sc=max(W/im.width,H/im.height); im=im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
    if sc>1.2: im=im.filter(ImageFilter.UnsharpMask(radius=3,percent=110,threshold=2))
    l=(im.width-W)//2; t=(im.height-H)//2; return im.crop((l,t,l+W,t+H))
def dtext(base,xy,text,fnt,fill,sw,S,glow=None,anchor="lm"):
    x,y=xy
    if glow:
        g=Image.new("RGBA",base.size,(0,0,0,0)); ImageDraw.Draw(g).text((x,y),text,font=fnt,fill=glow+(255,),stroke_width=sw+2,stroke_fill=glow+(255,),anchor=anchor); base.alpha_composite(g.filter(ImageFilter.GaussianBlur(13*S)))
    s=Image.new("RGBA",base.size,(0,0,0,0)); ImageDraw.Draw(s).text((x+5*S,y+7*S),text,font=fnt,fill=(0,0,0,220),stroke_width=sw,stroke_fill=(0,0,0,220),anchor=anchor); base.alpha_composite(s.filter(ImageFilter.GaussianBlur(5*S)))
    ImageDraw.Draw(base).text((x,y),text,font=fnt,fill=fill,stroke_width=sw,stroke_fill=(12,16,32,255),anchor=anchor)

def build(lang,S):
    W,H=1280*S,720*S
    base=cover(Image.open(os.path.join(OUT,BASE)).convert("RGB"),W,H).convert("RGBA")
    base=ImageEnhance.Contrast(base).enhance(1.06); base=ImageEnhance.Color(base).enhance(1.14)
    # 좌측 어둡게(글자 가독)
    g=Image.new("L",(W,1),0)
    for x in range(W): g.putpixel((x,0),int(225*max(0,1-(x/(W*0.60)))))
    dk=Image.new("RGBA",(W,H),(4,6,14,255)); dk.putalpha(g.resize((W,H))); base.alpha_composite(dk)
    # 하단 비네트
    vg=Image.new("L",(1,H),0)
    for y in range(H): vg.putpixel((0,y),int(120*max(0,(y-H*0.5)/(H*0.5))))
    vv=Image.new("RGBA",(W,H),(0,0,0,255)); vv.putalpha(vg.resize((W,H))); base.alpha_composite(vv)
    # 자모 액센트(상단)
    jf=font(MALGUN,52*S)
    for ch,xx,yy in [("ㅎ",60,50),("ㅏ",126,46),("ㄴ",196,55),("ㄱ",264,44),("ㅡ",332,57),("ㄹ",398,48)]:
        dtext(base,(xx*S,yy*S),ch,jf,(255,225,120),4*S,S,glow=(255,190,60))
    # 타이틀(축소+간격) — 겹침 방지
    if lang=="ko":
        dtext(base,(60*S,452*S),"세종대왕과",font(MALGUN,78*S),WHITE,7*S,S,glow=(20,30,60))
        dtext(base,(60*S,560*S),"한글",font(MALGUN,100*S),GOLD,8*S,S,glow=(255,150,30))
        dtext(base,(64*S,650*S),"한글은 어떻게 태어났을까?",font(MALGUN,40*S),WHITE,5*S,S)
    else:
        dtext(base,(60*S,450*S),"KING SEJONG",font(IMPACT,72*S),WHITE,6*S,S,glow=(20,30,60))
        dtext(base,(60*S,558*S),"& HANGEUL",font(IMPACT,96*S),GOLD,7*S,S,glow=(255,150,30))
        dtext(base,(64*S,650*S),"How an Alphabet Was Born",font(ARIALBD,38*S),WHITE,5*S,S)
    # 로고 = 최소 크기, 워터마크 중심에
    try:
        sz=int(LOGO_R*W); wx,wy=int(WM_CX*W),int(WM_CY*H)
        lg=Image.open(os.path.join(ROOT,"assets","drjay_ed_logo_circle.png")).convert("RGBA").resize((sz,sz),Image.LANCZOS)
        base.alpha_composite(lg,(wx-sz//2,wy-sz//2))
    except Exception: pass
    rgb=base.convert("RGB")
    tag="4k" if S==3 else "yt"
    p=os.path.join(OUT,f"final_A_{lang}_{tag}.jpg"); rgb.save(p,quality=93); print("saved",p,rgb.size,int(os.path.getsize(p)/1024),"KB")

for lang in ("ko","en"):
    build(lang,1); build(lang,3)
print("DONE")
