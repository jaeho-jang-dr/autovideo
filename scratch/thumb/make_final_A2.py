# -*- coding: utf-8 -*-
"""A안 썸네일 v2 — 날아다니는 글자를 '정확한 한글 자모' 오버레이로 교체.
왕/구도/타이틀 배치 유지. 자모는 정자로 직접 그려 획 정확성 보장. 영/한 · YT+4K.
사용: python make_final_A2.py [ko|en] [S]  (없으면 4종 전부)"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
ROOT="D:/Entertainments/DevEnvironment/autovideo"; OUT=os.path.join(ROOT,"scratch","thumb")
MALGUN=r"C:\Windows\Fonts\malgunbd.ttf"; IMPACT=r"C:\Windows\Fonts\impact.ttf"; ARIALBD=r"C:\Windows\Fonts\arialbd.ttf"
BASE="baseA2.png"    # 썸네일 전용 새 베이스(빈 하늘)
WM_CX, WM_CY = 0.898, 0.834; LOGO_R = 0.080
GOLD=(255,208,74,255); WHITE=(255,255,255,255)
# 자모 — 소용돌이 중심궤적(검출)을 호길이 간격으로 자동배치(겹침 방지). 아래 작게→위 크게.
import math
PATH=[(472,510),(513,472),(560,434),(491,396),(401,358),(330,320),(266,282),(293,244),(224,206),(204,168),(229,130),(268,92)]
CHARS=["ㅣ","ㅜ","ㅗ","ㅛ","ㅇ","ㅓ","ㅏ","ㅁ","ㄹ","ㄷ","ㄴ","ㄱ"]
SIZES=[32,35,38,41,44,47,50,53,55,58,60,62]     # 전체 축소(아래32→위62)
ROTS=[4,-8,8,-6,10,-8,6,-10,8,-6,10,-8]
def build_fly():
    dense=[]
    for i in range(len(PATH)-1):
        (x0,y0),(x1,y1)=PATH[i],PATH[i+1]; seg=math.hypot(x1-x0,y1-y0); steps=max(2,int(seg/3))
        for k in range(steps): dense.append((x0+(x1-x0)*k/steps, y0+(y1-y0)*k/steps))
    dense.append(PATH[-1]); cum=[0.0]
    for i in range(1,len(dense)): cum.append(cum[-1]+math.hypot(dense[i][0]-dense[i-1][0],dense[i][1]-dense[i-1][1]))
    total=cum[-1]; targ=[0.0]
    for i in range(len(SIZES)-1): targ.append(targ[-1]+(SIZES[i]+SIZES[i+1])/2+14)   # 간격=반크기합+여백14
    scale=(total*0.985)/targ[-1] if targ[-1]>0 else 1
    targ=[v*scale for v in targ]                                                     # 궤적 전체에 고루 펼침
    fly=[]
    for i,tl in enumerate(targ):
        j=0
        while j<len(cum)-1 and cum[j+1]<tl: j+=1
        if j>=len(dense)-1: x,y=dense[-1]
        else:
            f=(tl-cum[j])/max(1e-6,cum[j+1]-cum[j]); x=dense[j][0]+(dense[j+1][0]-dense[j][0])*f; y=dense[j][1]+(dense[j+1][1]-dense[j][1])*f
        fly.append((CHARS[i],int(x),int(y),SIZES[i],ROTS[i]))
    return fly
FLY=build_fly()

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

def mute_sky(base,W,H,S):
    """상단 하늘의 뭉개진 글자를 부드럽게 눌러줌(금빛 소용돌이 영역 살짝 블러+약한 골드 헤이즈)."""
    reg=(int(0.15*W),0,int(0.72*W),int(0.55*H))
    crop=base.crop(reg).filter(ImageFilter.GaussianBlur(4*S))
    base.paste(crop,reg)
    haze=Image.new("RGBA",(reg[2]-reg[0],reg[3]-reg[1]),(255,190,80,26)); base.alpha_composite(haze,(reg[0],reg[1]))

def fly_jamo(base,S):
    for ch,x,y,sz,rot in FLY:
        s=sz*S; canv=s*3; f=font(MALGUN,s)
        tmp=Image.new("RGBA",(canv,canv),(0,0,0,0))
        ImageDraw.Draw(tmp).text((canv//2,canv//2),ch,font=f,fill=(255,220,110,240),stroke_width=max(2,s//14),stroke_fill=(110,60,8,255),anchor="mm")
        tmp=tmp.rotate(rot,resample=Image.BICUBIC,center=(canv//2,canv//2))
        glow=tmp.filter(ImageFilter.GaussianBlur(int(0.10*s)+2))
        px,py=int(x*S-canv//2),int(y*S-canv//2)
        base.alpha_composite(glow,(px,py)); base.alpha_composite(glow,(px,py)); base.alpha_composite(tmp,(px,py))

def build(lang,S):
    W,H=1280*S,720*S
    base=cover(Image.open(os.path.join(OUT,BASE)).convert("RGB"),W,H).convert("RGBA")
    base=ImageEnhance.Contrast(base).enhance(1.06); base=ImageEnhance.Color(base).enhance(1.14)
    fly_jamo(base,S)              # 정확한 한글 자모 날림(빈 하늘이라 뭉개짐 처리 불필요)
    # 좌측 어둡게(글자 가독)
    g=Image.new("L",(W,1),0)
    for x in range(W): g.putpixel((x,0),int(220*max(0,1-(x/(W*0.55)))))
    dk=Image.new("RGBA",(W,H),(4,6,14,255)); dk.putalpha(g.resize((W,H))); base.alpha_composite(dk)
    vg=Image.new("L",(1,H),0)
    for y in range(H): vg.putpixel((0,y),int(120*max(0,(y-H*0.5)/(H*0.5))))
    vv=Image.new("RGBA",(W,H),(0,0,0,255)); vv.putalpha(vg.resize((W,H))); base.alpha_composite(vv)
    # 타이틀(축소+간격) — 5개 언어
    MSYH=r"C:\Windows\Fonts\msyhbd.ttc"; MEIRYO=r"C:\Windows\Fonts\meiryob.ttc"
    TT={
     "ko":(MALGUN,"세종대왕과",78,MALGUN,"한글",100,MALGUN,"한글은 어떻게 태어났을까?",40),
     "en":(IMPACT,"KING SEJONG",72,IMPACT,"& HANGEUL",96,ARIALBD,"How an Alphabet Was Born",38),
     "zh":(MSYH,"世宗大王与",82,MSYH,"韩文",106,MSYH,"韩文是怎样诞生的？",42),
     "ja":(MEIRYO,"世宗大王と",66,MEIRYO,"ハングル",90,MEIRYO,"ハングルはどう生まれた？",40),
     "es":(IMPACT,"REY SEJONG",72,IMPACT,"& HANGEUL",96,ARIALBD,"El nacimiento del Hangeul",34),
    }[lang]
    f1,l1,s1,f2,l2,s2,fh,hook,sh=TT
    dtext(base,(60*S,455*S),l1,font(f1,s1*S),WHITE,7*S,S,glow=(20,30,60))
    dtext(base,(60*S,562*S),l2,font(f2,s2*S),GOLD,8*S,S,glow=(255,150,30))
    dtext(base,(64*S,652*S),hook,font(fh,sh*S),WHITE,5*S,S)
    # 로고(전용 이미지엔 Veo 워터마크 없음) — 깨끗한 우하단 코너에 브랜딩
    try:
        sz=int(0.078*W); m=int(0.016*W)
        lg=Image.open(os.path.join(ROOT,"assets","drjay_ed_logo_circle.png")).convert("RGBA").resize((sz,sz),Image.LANCZOS)
        base.alpha_composite(lg,(W-sz-m, H-sz-m))
    except Exception: pass
    rgb=base.convert("RGB"); tag="4k" if S==3 else "yt"
    p=os.path.join(OUT,f"final_A_{lang}_{tag}.jpg"); rgb.save(p,quality=93); print("saved",p,rgb.size)

if len(sys.argv)>1:
    build(sys.argv[1], int(sys.argv[2]) if len(sys.argv)>2 else 1)
else:
    for lang in ("ko","en"):
        build(lang,1); build(lang,3)
print("DONE")
