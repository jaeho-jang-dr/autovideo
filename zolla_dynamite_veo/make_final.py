# -*- coding: utf-8 -*-
"""최종 합성 — 파스텔 배경 + 춤추는 졸라 듀오(투명 50%) + 한글 자모 조립(힙합맨/힙합걸).
연출: '맨'의 받침 ㄴ이 흔들흔들 → 띠우웅 떨어짐 → 춤추던 졸라맨이 손으로 주워 → 제자리에 붙임.
가독성↑: 빈 자리 표시(흐릿한 ㄴ) + 줍는 동안 ㄴ 확대·글로우 + 느린 동선 + 붙일 때 팝.
졸라맨 손목 위치는 _man_norm.npy(정규화 좌표)로 추적.
"""
import os, sys, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import make_jamo_assembly as ja
from make_jamo_assembly import ease, clamp, lerp

DUO=os.path.join(HERE,"_duo2.mp4"); OUT=os.path.join(HERE,"_final.mp4")
BEIGE_RGB=np.array([240,230,212]); GHOST=0.5; SNAP=7
W,H=ja.W,ja.H
MAN=np.load(os.path.join(HERE,"_man_norm.npy")); MANCF=np.load(os.path.join(HERE,"_man_cf.npy"))

NL=ja.SYLS[2]["jamos"][2]; SKIP={(2,2)}          # 힙합맨 → 맨 → 받침 ㄴ
SLOT=(NL["tx"],NL["ty"]); FLOOR=(W*0.30, H*0.80); BASE_SC=max(1.05,NL["tscale"])
# 타임라인(초) — 천천히, 단계 또렷하게
T_WOB=7.0; T_DROP=7.9; T_LAND=9.1; T_GRAB=9.9; T_HELD=10.7; T_CARRY=11.6; T_DONE=12.9
DUR=14.3

def make_glow(r,color=(90,220,255)):
    s=int(r*2); g=Image.new("RGBA",(s,s),(0,0,0,0))
    ImageDraw.Draw(g).ellipse([s*0.22,s*0.22,s*0.78,s*0.78],fill=color+(200,))
    return g.filter(ImageFilter.GaussianBlur(r*0.22))
GLOW=make_glow(150,(255,210,80))

def man_hand(hk):
    hk=int(min(max(hk,0),len(MAN)-1)); cf=MANCF[hk]
    cands=[(10,cf[10]),(9,cf[9])]; cands=[c for c in cands if c[1]>0.2]
    if cands:
        idx=max(cands,key=lambda c:c[1])[0]; return float(MAN[hk][idx][0]),float(MAN[hk][idx][1])
    return FLOOR

_ph={}   # 단계별 캡처(손 위치 등)
def neun_state(t, hand):
    """반환: (cx,cy,ang,scale,alpha,highlight)  highlight=글로우 강도"""
    sx,sy=SLOT; fx,fy=FLOOR
    if t < NL["start"]: return None
    if t < NL["start"]+NL["dur"]:                 # 조립 비행
        p=clamp((t-NL["start"])/NL["dur"],0,1); e=ease(p)
        return (lerp(NL["ox"],sx,e),lerp(NL["oy"],sy,e),lerp(NL["ospin"],0,e),NL["tscale"],clamp(p*3,0,1),0)
    if t < T_WOB:  return (sx,sy,0,NL["tscale"],1.0,0)
    if t < T_DROP:                                # 흔들흔들(점점 크게)
        k=t-T_WOB; return (sx+math.sin(k*22)*5, sy+math.sin(k*16)*6, math.sin(k*26)*16, NL["tscale"],1.0, clamp(k/0.9,0,1)*0.5)
    if t < T_LAND:                                # 띠우웅 떨어짐
        p=clamp((t-T_DROP)/(T_LAND-T_DROP),0,1)
        y=sy+(fy-sy)*min(1.0,p*1.2)
        if p>0.75: y-=math.sin((p-0.75)/0.25*math.pi)*55      # 바운스
        return (lerp(sx,fx,p)+math.sin(p*7)*18, y, p*230, BASE_SC*1.15, 1.0, 0.6)
    if t < T_GRAB:                                # 바닥에서 통통(졸라맨 다가옴)
        k=t-T_LAND; return (fx,fy-abs(math.sin(k*9))*10,math.sin(t*14)*7,BASE_SC*1.15,1.0,0.6+math.sin(k*6)*0.2)
    if t < T_HELD:                                # 손으로 끌려 올라옴(줍기) — 또렷하게
        p=ease(clamp((t-T_GRAB)/(T_HELD-T_GRAB),0,1))
        return (lerp(fx,hand[0],p),lerp(fy,hand[1],p),lerp(35,0,p),BASE_SC*1.25,1.0,0.9)
    if t < T_CARRY:                               # 손에 들고 잠깐 정지(GOT IT 비트)
        return (hand[0],hand[1],math.sin(t*8)*6,BASE_SC*1.3,1.0,1.0)
    if t < T_DONE:                                # 제자리에 갖다 붙임(포물선) + 도착 팝
        if "h" not in _ph: _ph["h"]=hand
        hx,hy=_ph["h"]; p=ease(clamp((t-T_CARRY)/(T_DONE-T_CARRY),0,1))
        pop=1.0+(math.sin((p-0.82)/0.18*math.pi)*0.28 if p>0.82 else 0.0)
        return (lerp(hx,sx,p),lerp(hy,sy,p)-math.sin(p*math.pi)*130,0,BASE_SC*1.25*pop,1.0,0.9*(1-p))
    # 완성 후 잠깐 살짝 출렁였다 안정
    s=BASE_SC*(1.0+max(0.0,0.12*math.sin((t-T_DONE)*10))*math.exp(-(t-T_DONE)*3))
    return (sx,sy,0,s,1.0,0)

def main():
    cap=cv2.VideoCapture(DUO); fps=cap.get(cv2.CAP_PROP_FPS) or 20
    maxN=int(DUR*fps); i=0
    vw=cv2.VideoWriter(OUT,cv2.VideoWriter_fourcc(*"mp4v"),fps,(W,H))
    ghost_tile=ja.glyph_tile(NL["ch"],NL["fs"],(150,150,165))
    while i<maxN:
        ok,fr=cap.read()
        if not ok:
            cap.set(cv2.CAP_PROP_POS_FRAMES,0); ok,fr=cap.read()
            if not ok: break
        t=i/fps
        if fr.shape[1]!=W or fr.shape[0]!=H: fr=cv2.resize(fr,(W,H))
        rgb=cv2.cvtColor(fr,cv2.COLOR_BGR2RGB).astype(np.float32)
        base=np.array(ja.BG.convert("RGB")).astype(np.float32)
        dist=np.abs(rgb-BEIGE_RGB).sum(2); a=np.where(dist>45,GHOST,0.0)[...,None]
        base=base*(1-a)+rgb*a
        pim=Image.fromarray(base.astype(np.uint8),"RGB").convert("RGBA")
        ja.draw_overlay(pim, t, skip=SKIP)
        # 빈 자리 표시(ㄴ이 빠져있는 동안 흐릿하게 "여기로 돌아옴")
        if T_DROP-0.1 <= t < T_DONE-0.05:
            ga=0.30*(1-clamp((t-(T_DONE-0.6))/0.55,0,1))
            ja.paste(pim, ghost_tile, SLOT[0], SLOT[1], scale=NL["tscale"], alpha=ga)
        hk=(i//SNAP)*SNAP; hand=man_hand(hk)
        st=neun_state(t, hand)
        if st:
            cx,cy,ang,sc,al,hl=st
            if hl>0.02: ja.paste(pim, GLOW, cx, cy, alpha=clamp(hl,0,1)*0.65)
            ja.draw_jamo(pim, NL, t, cx, cy, ang=ang, scale=sc, alpha=al)
        vw.write(cv2.cvtColor(np.array(pim.convert("RGB")),cv2.COLOR_RGB2BGR)); i+=1
    vw.release(); cap.release()
    print(f"[OK] {OUT} ({i} frames @ {fps:.0f}fps, {i/fps:.1f}s)")

if __name__=="__main__":
    main()
