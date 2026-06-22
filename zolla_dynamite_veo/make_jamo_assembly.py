# -*- coding: utf-8 -*-
"""한글 자모 조립 애니메이션 — "힙합맨" + "힙합걸" (자모 18개, 전 음절 받침).
※ 블록(박스) 아님: 단순 자모 글자가 제각각 크기로 비정형적으로 빙빙 돌며 날아와
   하나씩(초성→중성→종성) 제자리에 붙고, 합쳐지면 실제 완성 글자(힙/합/맨/걸)로 정리.
   자음=코랄 / 모음=청록 / 받침=앰버 글자색. 세로 1080x1920, 어두운 무대 톤.
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "scratch"))
from hangeul_decomposer import decompose_char
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

W,H,FPS=1080,1920,30
OUT=os.path.join(ROOT,"zolla_dynamite_veo","_jamo_assembly.mp4")
FONT=r"C:\Windows\Fonts\malgunbd.ttf"
CONS=(240,80,110); VOW=(40,160,180); BAT=(235,150,40); DONE=(34,34,54)  # 밝은 배경용(완성=진한 남색)

_FC={}
def font(s):
    s=max(8,int(s))
    if s not in _FC: _FC[s]=ImageFont.truetype(FONT,s)
    return _FC[s]
def ease(p): return 1-(1-p)**3
def clamp(v,a,b): return max(a,min(b,v))
def lerp(a,b,t): return a+(b-a)*t
def rnd(i,seed):
    x=math.sin((i+1)*12.9898+seed*78.233)*43758.5453
    return x-math.floor(x)

def glyph_tile(ch,size,color):
    """단순 자모 글자(투명배경, 가독용 옅은 외곽선)."""
    f=font(size)
    d0=ImageDraw.Draw(Image.new("RGBA",(4,4)))
    bb=d0.textbbox((0,0),ch,font=f,stroke_width=max(1,int(size*0.04)))
    w=bb[2]-bb[0]+10; h=bb[3]-bb[1]+10
    t=Image.new("RGBA",(int(w),int(h)),(0,0,0,0))
    ImageDraw.Draw(t).text((5-bb[0],5-bb[1]),ch,font=f,fill=color+(255,),
        stroke_width=max(1,int(size*0.04)),stroke_fill=(12,12,18,230))
    return t

def paste(base,tile,cx,cy,scale=1.0,angle=0.0,alpha=1.0):
    if alpha<=0.02 or scale<=0.02: return
    t=tile
    if abs(scale-1.0)>1e-3:
        t=t.resize((max(2,int(t.width*scale)),max(2,int(t.height*scale))),Image.BICUBIC)
    if abs(angle)>0.5:
        t=t.rotate(angle,expand=True,resample=Image.BICUBIC)
    if alpha<0.99:
        t=t.copy(); t.putalpha(t.split()[3].point(lambda v:int(v*alpha)))
    base.alpha_composite(t,(int(cx-t.width/2),int(cy-t.height/2)))

def plan():
    rows=[("힙합맨",560),("힙합걸",1120)]; C=240; gap=46
    syls=[]; gi=0
    for ri,(word,cy) in enumerate(rows):
        n=len(word); total=n*C+(n-1)*gap; x0=(W-total)/2+C/2
        for si,ch in enumerate(word):
            cx=x0+si*(C+gap)
            parts=decompose_char(ch,fully_decompose=False)
            cons=parts[0]; vow=parts[1]; bat=parts[2] if len(parts)>2 else None
            slots=[("cons",cons,CONS,(cx-C*0.20,cy-C*0.16),C*0.52),
                   ("vow", vow, VOW,(cx+C*0.21,cy-C*0.11),C*0.60)]
            if bat: slots.append(("bat",bat,BAT,(cx,cy+C*0.30),C*0.48))
            order=ri*3+si
            jamos=[]
            for j,(role,jch,col,tgt,fs) in enumerate(slots):
                start=order*1.0 + j*0.32
                jamos.append(dict(ch=jch,col=col,tx=tgt[0],ty=tgt[1],fs=fs,
                    start=start,dur=0.9,
                    tscale=0.8+rnd(gi,5)*0.5,   # 자모별 다른 크기(날아온 그대로 유지)
                    ox=rnd(gi,1)*W, oy=(-260 if rnd(gi,2)<0.5 else H+260),
                    ospin=(540+rnd(gi,4)*720)*(1 if gi%2 else -1)))
                gi+=1
            asm=max(x["start"]+x["dur"] for x in jamos)
            syls.append(dict(ch=ch,cx=cx,cy=cy,C=C,jamos=jamos,asm=asm))
    last=max(s["asm"] for s in syls)
    return syls,last

SYLS, ASSEMBLE_END = plan()
DUR = ASSEMBLE_END + 2.4

def make_bg():
    """중앙은 희고 밝게, 주변은 파스텔 분홍(왼쪽)·파랑(오른쪽)으로 옅게."""
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    d=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2); d=np.clip(d,0,1)
    tx=(xx/W)[...,None]
    white=np.array([252,252,255]); pink=np.array([255,206,221]); blue=np.array([206,224,255])
    edge=pink*(1-tx)+blue*tx                      # 왼쪽 분홍 → 오른쪽 파랑
    col=white*(1-d[...,None]*0.85)+edge*(d[...,None]*0.85)
    return Image.fromarray(col.astype(np.uint8),"RGB").convert("RGBA")
BG=make_bg()

def label(base,txt,cy,sz,color,alpha=1.0):
    if alpha<=0.02: return
    f=font(sz); d=ImageDraw.Draw(base); bb=d.textbbox((0,0),txt,font=f); tw=bb[2]-bb[0]
    lay=Image.new("RGBA",base.size,(0,0,0,0))
    ImageDraw.Draw(lay).text(((W-tw)/2-bb[0],cy-(bb[3]-bb[1])/2-bb[1]),txt,font=f,fill=color+(int(255*alpha),))
    base.alpha_composite(lay)

def draw_overlay(base, t, skip=()):
    """base(RGBA) 위에 타이틀+자모조립 그림. skip=특정 (음절idx,자모idx)는 외부에서 직접 처리."""
    label(base,"Korean letters are built from blocks",120,56,(50,50,70),clamp(t/0.6,0,1))
    for si,s in enumerate(SYLS):
        for ji,j in enumerate(s["jamos"]):
            if (si,ji) in skip: continue
            if t<j["start"]: continue
            p=clamp((t-j["start"])/j["dur"],0,1); e=ease(p)
            tile=glyph_tile(j["ch"],j["fs"],j["col"])
            cx=lerp(j["ox"],j["tx"],e); cy=lerp(j["oy"],j["ty"],e)
            ang=lerp(j["ospin"],0.0,e)
            paste(base,tile,cx,cy,scale=j["tscale"],angle=ang,alpha=clamp(p*3,0,1))
    if t>ASSEMBLE_END-0.2:
        a=clamp((t-(ASSEMBLE_END-0.2))/0.5,0,1)
        label(base,"HIPHOP MAN  ·  HIPHOP GIRL",1520,46,(90,90,115),a)

def draw_jamo(base, j, t, cx, cy, ang=None, scale=None, alpha=None):
    """단일 자모를 임의 위치/각도/크기로 그린다(졸라맨이 줍는 ㄴ 등 외부 제어용)."""
    tile=glyph_tile(j["ch"],j["fs"],j["col"])
    paste(base,tile,cx,cy,scale=(j["tscale"] if scale is None else scale),
          angle=(0.0 if ang is None else ang),alpha=(1.0 if alpha is None else alpha))

def make_frame(t):
    base=BG.copy(); draw_overlay(base,t)
    return np.array(base.convert("RGB"))

def main():
    print(f"음절 {len(SYLS)}개, 자모 {sum(len(s['jamos']) for s in SYLS)}개, 조립완료 {ASSEMBLE_END:.1f}s, 총 {DUR:.1f}s")
    VideoClip(make_frame,duration=DUR).write_videofile(OUT,fps=FPS,codec="libx264",audio=False,
        threads=os.cpu_count() or 4,preset="medium",bitrate="6000k")
    print(f"[OK] {OUT}")

if __name__=="__main__":
    main()
