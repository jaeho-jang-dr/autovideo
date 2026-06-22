# -*- coding: utf-8 -*-
"""레슨 엔진 — 벤치마크(TED-Ed/English-class) 연출 기법을 내장한 플랫 레이어드 렌더러.
레슨 = 씬(컷) 리스트(데이터). 각 씬 = {dur, trans, els:[element...], sub}.
element 타입: text / image / presenter / spotlight / underline / check / badge.
기법 내장: 파스텔·오프화이트 배경, 포인트컬러 스포트라이트, 타이포 콜아웃(팝/타이핑/슬라이드),
  밑줄·체크·번호배지, 프리젠터 포인팅(보브), Pan&Zoom, 많은 짧은 컷(크로스페이드), TED-Ed식 자막.
대본/에셋만 바꿔 새 레슨 양산. → benchmark_db.py 기법 카탈로그를 코드로 구현한 것.
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip

W,H,FPS=1080,1920,30
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FB=r"C:\Windows\Fonts\malgunbd.ttf"; FR=r"C:\Windows\Fonts\malgun.ttf"
INK=(38,38,52); ACCENT=(255,196,40); XF=0.35   # 컷 크로스페이드(부드러운 전환)

_fc={}
def font(sz,bold=True):
    k=(int(sz),bold)
    if k not in _fc: _fc[k]=ImageFont.truetype(FB if bold else FR,int(sz))
    return _fc[k]
def clamp(v,a,b): return max(a,min(b,v))
def lerp(a,b,t): return a+(b-a)*t
def eo(p): return 1-(1-clamp(p,0,1))**3            # ease-out

# ── 배경 ──
def pastel_bg():
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    d=np.clip(np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2),0,1)
    tx=(xx/W)[...,None]
    white=np.array([252,252,255]); pink=np.array([255,206,221]); blue=np.array([206,224,255])
    col=white*(1-d[...,None]*0.85)+(pink*(1-tx)+blue*tx)*(d[...,None]*0.85)
    return Image.fromarray(col.astype(np.uint8),"RGB").convert("RGBA")
def offwhite_bg():
    return Image.new("RGBA",(W,H),(245,245,240,255))
BGS={"pastel":pastel_bg,"offwhite":offwhite_bg}

# ── 에셋/요소 렌더 헬퍼 ──
def keyed(path,h,flip=False):
    p=path if os.path.isabs(path) else os.path.join(ROOT,path)
    im=Image.open(p).convert("RGBA"); a=np.array(im)
    m=~((a[:,:,0]>238)&(a[:,:,1]>238)&(a[:,:,2]>238))
    ys,xs=np.where(m)
    if len(xs): im=im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
    a=np.array(im); w=(a[:,:,0]>238)&(a[:,:,1]>238)&(a[:,:,2]>238); a[w,3]=0
    im=Image.fromarray(a)
    if flip: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((max(1,int(im.width*h/im.height)),int(h)),Image.LANCZOS)

def text_tile(text,size,color,bold=True):
    f=font(size,bold); sw=max(2,int(size*0.05))
    d0=ImageDraw.Draw(Image.new("RGBA",(4,4)))
    bb=d0.textbbox((0,0),text,font=f,stroke_width=sw)
    w=bb[2]-bb[0]+12; h=bb[3]-bb[1]+12
    t=Image.new("RGBA",(max(2,int(w)),max(2,int(h))),(0,0,0,0))
    ImageDraw.Draw(t).text((6-bb[0],6-bb[1]),text,font=f,fill=color+(255,),
        stroke_width=sw,stroke_fill=(255,255,255,235))   # TED-Ed식: 박스 없이 옅은 외곽선
    return t

_glow={}
def glow(r,color=ACCENT):
    k=(int(r),color)
    if k in _glow: return _glow[k]
    s=int(r*2); g=Image.new("RGBA",(s,s),(0,0,0,0))
    ImageDraw.Draw(g).ellipse([s*0.2,s*0.2,s*0.8,s*0.8],fill=color+(190,))
    g=g.filter(ImageFilter.GaussianBlur(r*0.25)); _glow[k]=g; return g

def paste(base,tile,cx,cy,scale=1.0,alpha=1.0,angle=0.0):
    if alpha<=0.02 or scale<=0.02: return
    t=tile
    if abs(scale-1)>1e-3: t=t.resize((max(2,int(t.width*scale)),max(2,int(t.height*scale))),Image.BICUBIC)
    if abs(angle)>0.5: t=t.rotate(angle,expand=True,resample=Image.BICUBIC)
    if alpha<0.99: t=t.copy(); t.putalpha(t.split()[3].point(lambda v:int(v*alpha)))
    base.alpha_composite(t,(int(cx-t.width/2),int(cy-t.height/2)))

# ── 요소 상태(인/아웃 애니) ──
def el_state(el,tl):
    t0=el.get("t_in",0.0); t1=el.get("t_out")
    if tl<t0: return None
    if t1 is not None and tl>t1: return None
    din=el.get("in_dur",0.5); a=1.0; dx=dy=0.0; sc=el.get("scale",1.0); prog=1.0
    p=clamp((tl-t0)/din,0,1); k=el.get("in","fade")
    if k=="fade": a=p
    elif k=="pop": a=clamp(p*2,0,1); sc*= (0.5+0.5*eo(p))+(math.sin(p*math.pi)*0.14 if p<1 else 0)
    elif k in("slide_l","slide_r","slide_u","slide_d"):
        a=clamp(p*2,0,1); off=(1-eo(p))*220; dxy={"slide_l":(-1,0),"slide_r":(1,0),"slide_u":(0,-1),"slide_d":(0,1)}[k]
        dx,dy=dxy[0]*off,dxy[1]*off
    elif k=="type": a=1.0; prog=p
    if t1 is not None:
        dout=el.get("out_dur",0.35); q=clamp((t1-tl)/dout,0,1)
        if q<1: a*=q
    return a,dx,dy,sc,prog

def el_render(base,el,tl):
    st=el_state(el,tl)
    if st is None: return
    a,dx,dy,sc,prog=st
    x,y=el["pos"]; x+=dx; y+=dy; typ=el["type"]
    if typ=="text":
        full=el["text"]; txt=full[:max(1,int(len(full)*prog))] if el.get("in")=="type" and prog<1 else full
        paste(base,text_tile(txt,el["size"],el.get("color",INK),el.get("bold",True)),x,y,scale=sc,alpha=a)
    elif typ in("image","presenter"):
        img=el["_img"]; bob=math.sin(tl*3.0)*el.get("bob",0)
        paste(base,img,x,y+bob,scale=sc,alpha=a)
    elif typ=="spotlight":
        paste(base,glow(el.get("r",240),el.get("color",ACCENT)),x,y,alpha=a*el.get("strength",0.7))
    elif typ=="underline":
        d=ImageDraw.Draw(base); wdt=int(el["width"]*eo(clamp((tl-el.get("t_in",0))/el.get("in_dur",0.5),0,1)))
        th=el.get("th",10); c=el.get("color",ACCENT)
        d.rounded_rectangle([x-el["width"]//2,y,x-el["width"]//2+wdt,y+th],radius=th//2,fill=c+(int(255*a),))
    elif typ=="check":
        d=ImageDraw.Draw(base); pr=eo(clamp((tl-el.get("t_in",0))/el.get("in_dur",0.4),0,1)); s=el.get("size",60)
        c=el.get("color",(80,190,90))+(int(255*a),)
        p1=(x-s*0.5,y); p2=(x-s*0.1,y+s*0.45); p3=(x+s*0.6,y-s*0.5)
        if pr<0.5: d.line([p1,(lerp(p1[0],p2[0],pr*2),lerp(p1[1],p2[1],pr*2))],fill=c,width=max(6,s//6))
        else:
            d.line([p1,p2],fill=c,width=max(6,s//6)); q=(pr-0.5)*2
            d.line([p2,(lerp(p2[0],p3[0],q),lerp(p2[1],p3[1],q))],fill=c,width=max(6,s//6))
    elif typ=="badge":
        d=ImageDraw.Draw(base); r=el.get("r",46); c=el.get("color",ACCENT)
        d.ellipse([x-r,y-r,x+r,y+r],fill=c+(int(255*a),),outline=INK+(int(255*a),),width=4)
        paste(base,text_tile(str(el["num"]),r*1.1,INK),x,y,alpha=a)

# ── 자막(TED-Ed식: 박스 없이 옅은 외곽선, 하단 큰 마진, 중앙) ──
def draw_sub(base,text,alpha=1.0):
    if not text: return
    f=font(40,False); d=ImageDraw.Draw(base)
    bb=d.textbbox((0,0),text,font=f,stroke_width=4); tw=bb[2]-bb[0]
    lay=Image.new("RGBA",base.size,(0,0,0,0))
    ImageDraw.Draw(lay).text(((W-tw)/2-bb[0],H-300),text,font=f,fill=(40,40,55,int(255*alpha)),
        stroke_width=4,stroke_fill=(255,255,255,int(220*alpha)))
    base.alpha_composite(lay)

# ── 렌더 ──
def _preload(scenes):
    for s in scenes:
        for el in s.get("els",[]):
            if el["type"] in("image","presenter") and "_img" not in el:
                el["_img"]=keyed(el["img"],el.get("h",600),el.get("flip",False))

def render_scene(s,tl,bgkind):
    base=BGS.get(bgkind,pastel_bg)()
    for el in s.get("els",[]): el_render(base,el,tl)
    draw_sub(base,s.get("sub"),1.0)
    return base

def render(scenes,out,bgkind="pastel"):
    _preload(scenes)
    starts=[]; t=0.0
    for s in scenes: starts.append(t); t+=s["dur"]
    total=t
    def frame(tt):
        i=max(0,min(len(scenes)-1,next((j for j in range(len(scenes)) if starts[j]<=tt<starts[j]+scenes[j]["dur"]),len(scenes)-1)))
        tl=tt-starts[i]
        cur=render_scene(scenes[i],tl,bgkind)
        if i>0 and scenes[i].get("trans","fade")=="fade" and tl<XF:   # 부드러운 컷 전환
            prev=render_scene(scenes[i-1],scenes[i-1]["dur"]-(XF-tl),bgkind)
            a=tl/XF; cur=Image.blend(prev,cur,a)
        return np.array(cur.convert("RGB"))
    print(f"씬 {len(scenes)}개, 총 {total:.1f}s 렌더...")
    VideoClip(frame,duration=total).write_videofile(out,fps=FPS,codec="libx264",audio=False,
        threads=os.cpu_count() or 4,preset="medium",bitrate="6000k")
    print(f"[OK] {out}")
