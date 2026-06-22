# -*- coding: utf-8 -*-
"""오프닝 가이드(G1) 목업 — Flow 생성 전 방향 제시용.
파르테논 50% 배경 + 졸라맨/졸라걸 2배 손잡기 + 불규칙 회전 색색 자모블록."""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HV = os.path.join(ROOT, "home_vocab")
ODIR = os.path.dirname(os.path.abspath(__file__))
FONT = r"C:\Windows\Fonts\malgunbd.ttf"
W, H = 1080, 1920

def keyed(path, target_h, flip=False):
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    m = ~((a[:,:,0]>244)&(a[:,:,1]>244)&(a[:,:,2]>244))
    ys, xs = np.where(m)
    im = im.crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1))
    a = np.array(im); w=(a[:,:,0]>244)&(a[:,:,1]>244)&(a[:,:,2]>244); a[w,3]=0
    im = Image.fromarray(a)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((int(im.width*target_h/im.height), target_h), Image.LANCZOS)

def parthenon(alpha=128):
    """반투명 파르테논 신전 실루엣(전체 화면 배경)."""
    layer = Image.new("RGBA", (W, H), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    cream = (236, 228, 210, alpha); line=(180,170,150,alpha)
    base_y, top_y = 1500, 560
    left, right = 70, W-70
    n_col = 8
    # 기단
    d.rectangle([left-20, base_y, right+20, base_y+70], fill=cream, outline=line, width=3)
    d.rectangle([left-40, base_y+70, right+40, base_y+150], fill=cream, outline=line, width=3)
    # 기둥
    cap_y = top_y+150
    cw = (right-left)/n_col
    for i in range(n_col):
        x = left + i*cw + cw*0.18
        d.rounded_rectangle([x, cap_y, x+cw*0.64, base_y], radius=8, fill=cream, outline=line, width=3)
        for fl in range(3):  # 세로 홈
            fx = x + cw*0.64*(fl+1)/4
            d.line([fx, cap_y+10, fx, base_y-10], fill=line, width=2)
    # 엔타블러처 + 페디먼트(삼각형 지붕)
    d.rectangle([left-30, top_y+90, right+30, cap_y], fill=cream, outline=line, width=3)
    d.polygon([(left-50, top_y+90),(right+50, top_y+90),(W/2, top_y-90)], fill=cream, outline=line, width=4)
    return layer

def jamo_block(ch, size, color):
    s=int(size); t=Image.new("RGBA",(s,s),(0,0,0,0)); d=ImageDraw.Draw(t)
    d.rounded_rectangle([2,2,s-3,s-3], radius=int(s*0.16), fill=color+(255,), outline=(40,40,45,255), width=max(3,s//30))
    sr=int(s*0.1)
    for i in range(2):
        cx=int(s*(i+1)/3); cy=int(s*0.16)
        d.ellipse([cx-sr,cy-sr,cx+sr,cy+sr], fill=tuple(min(255,c+35) for c in color)+(255,), outline=(40,40,45,255), width=2)
    f=ImageFont.truetype(FONT, int(s*0.6)); bb=d.textbbox((0,0),ch,font=f)
    d.text(((s-(bb[2]-bb[0]))/2-bb[0],(s-(bb[3]-bb[1]))/2-bb[1]+s*0.04), ch, font=f, fill=(40,40,45,255))
    return t

def main():
    # 배경 그라데이션(하늘)
    top=np.array([250,244,232]); bot=np.array([214,226,246])
    col=(top[None,:]+(bot-top)[None,:]*np.linspace(0,1,H)[:,None]).astype(np.uint8)
    base=Image.fromarray(np.repeat(col[:,None,:],W,axis=1),"RGB").convert("RGBA")
    # 파르테논 50%
    base.alpha_composite(parthenon(alpha=128))
    # 불규칙 회전 색색 자모블록(스웜 방향 암시)
    COLORS=[(255,107,107),(78,205,196),(255,213,61),(155,140,255),(120,200,120),(255,160,90)]
    swarm=[("ㄷ",150,15),("ㅏ",96,-25),("ㅇ",120,40),("ㅌ",170,-12),("ㅣ",80,30),
           ("ㅁ",110,-35),("ㅡ",130,18),("ㅂ",90,-20)]
    pts=[(190,360),(360,250),(560,330),(760,260),(900,400),(840,640),(230,620),(640,560)]
    for (ch,sz,ang),(x,y),c in zip(swarm,pts,COLORS+COLORS):
        bl=jamo_block(ch,sz,c).rotate(ang,expand=True,resample=Image.BICUBIC)
        base.alpha_composite(bl,(int(x-bl.width/2),int(y-bl.height/2)))
    # 졸라 2배 손잡기(중앙, 안쪽 손 맞닿게)
    man=keyed(os.path.join(HV,"zollaman_base.png"), 880)
    girl=keyed(os.path.join(HV,"zollanyeo_base.png"), 880, flip=True)
    baseline=1780
    mx=W//2-man.width+70; gx=W//2-70
    base.alpha_composite(man,(mx, baseline-man.height))
    base.alpha_composite(girl,(gx, baseline-girl.height))
    # 손잡기 표시(맞닿는 지점 작은 하트)
    d=ImageDraw.Draw(base); hx,hy=W//2, baseline-int(man.height*0.5)
    d.ellipse([hx-16,hy-12,hx-2,hy+2],fill=(255,90,120,255)); d.ellipse([hx+2,hy-12,hx+16,hy+2],fill=(255,90,120,255))
    d.polygon([(hx-15,hy-2),(hx+15,hy-2),(hx,hy+18)],fill=(255,90,120,255))
    # 캡션
    f=ImageFont.truetype(FONT,46); f2=ImageFont.truetype(FONT,34)
    d.text((60,90),"가이드 #1 — 오프닝",font=f,fill=(50,50,60))
    d.text((60,150),"손잡고 시작 · 파르테논 50% 배경 · 캐릭터 2배 · 자모 불규칙 회전 스웜",font=f2,fill=(110,110,125))
    out=os.path.join(ODIR,"_guide_G1_mock.png")
    base.convert("RGB").save(out); print("[OK]",out)

if __name__=="__main__":
    main()
