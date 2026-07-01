# -*- coding: utf-8 -*-
"""세종대왕과 한글 — 본편 하이브리드 컴포지터 (48샷, 16:9).
샷별 Veo 클립(sejong_main_kf/scene_S##.mp4) + 자막(한/영) + 나레이션 + 로고(우하단 워터마크 덮기)
+ 전환(디졸브/모프=크로스페이드, 컷/매치컷=하드컷) + 개념샷 정확한 한글 자모 오버레이.
사용: python compile_main_hybrid.py ko|en [free|11]
  free=무료 gTTS(audio_free) / 11=ElevenLabs(audio). 기본 free."""
import os, re, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import (ImageClip, VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip)
from moviepy.video.fx import FadeIn, MultiplySpeed, CrossFadeIn

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SF = os.path.join(ROOT, "sejong_film")
MAIN = os.path.join(SF, "main")
KF = os.path.join(MAIN, "keyframes")
CLIPS = os.path.join(ROOT, "sejong_main_kf")        # scene_<n>.mp4 (autoveo 출력)
LOGO = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"
W, H = 1920, 1080
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
NARR = sys.argv[2] if len(sys.argv) > 2 else "free"
AUD = os.path.join(MAIN, "audio_free" if NARR == "free" else "audio")
APREFIX = "" if NARR == "free" else ""   # audio_free: ko_S01.mp3 / audio(11): ko_S01.mp3 동일 규칙 권장

GOLD = (245, 200, 75, 255); WHITE = (255, 255, 255, 255)
XF = 0.6
DISSOLVE = ("디졸브", "모프", "페이드", "입자와이프", "슬라이드")   # 크로스페이드
JAMO = {  # 개념샷 정확한 한글 자모 오버레이
    28: ["ㄱ","ㄴ","ㄷ","ㅁ","ㅂ","ㅅ","ㅇ","ㅈ","ㅎ","ㅏ","ㅓ","ㅗ","ㅜ"],
    37: ["ㄱ","ㄴ","ㅁ"], 38: ["ㄴ","ㄷ","ㅌ"], 39: ["ㆍ","ㅡ","ㅣ"],
    40: ["ㅏ","ㅓ","ㅗ","ㅜ"], 47: ["ㄱ","ㅁ","ㅇ","ㅏ","ㅣ","ㅡ"],
}
TITLE = {"ko": ("세종대왕과 한글","한글은 어떻게 태어났을까?"), "en": ("King Sejong & Hangeul","How were the letters born?")}

# ---------- 텍스트 ----------
def _wrap(text, font, maxw):
    words=text.split(" "); lines=[]; cur=""
    d=ImageDraw.Draw(Image.new("RGBA",(4,4)))
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines or [text]

def text_img(text,size,fill,sw=6,shadow=True,glow=None,maxw=None):
    font=ImageFont.truetype(MALGUN,size)
    lines=_wrap(text,font,maxw) if maxw else [text]
    asc,desc=font.getmetrics(); lh=asc+desc+8
    d0=ImageDraw.Draw(Image.new("RGBA",(4,4)))
    tw=max(d0.textlength(l,font=font) for l in lines)
    pad=sw+(46 if glow else 26)
    img=Image.new("RGBA",(int(tw)+pad*2,lh*len(lines)+pad*2),(0,0,0,0))
    def draw_all(dd,ox,oy,col,scol):
        for i,l in enumerate(lines):
            lw=dd.textlength(l,font=font); x=(img.width-lw)/2+ox; y=pad+i*lh+oy
            dd.text((x,y),l,font=font,fill=col,stroke_width=sw,stroke_fill=scol)
    d=ImageDraw.Draw(img)
    if glow:
        g=Image.new("RGBA",img.size,(0,0,0,0)); dg=ImageDraw.Draw(g)
        draw_all(dg,0,0,glow+(255,),glow+(255,)); g=g.filter(ImageFilter.GaussianBlur(16))
        img=Image.alpha_composite(img,g); img=Image.alpha_composite(img,g); d=ImageDraw.Draw(img)
    if shadow:
        sh=Image.new("RGBA",img.size,(0,0,0,0)); ds=ImageDraw.Draw(sh)
        draw_all(ds,4,6,(0,0,0,200),(0,0,0,200)); sh=sh.filter(ImageFilter.GaussianBlur(6))
        img=Image.alpha_composite(img,sh); d=ImageDraw.Draw(img)
    draw_all(d,0,0,fill,(20,25,45,255))
    return img

def pil_clip(img,dur):
    return ImageClip(np.array(img.convert("RGBA")),transparent=True).with_duration(dur)

def cover_fit_video(v):
    sc=max(W/v.w,H/v.h); v=v.resized(sc)
    x=(v.w-W)/2; y=(v.h-H)/2
    return v.cropped(x1=x,y1=y,x2=x+W,y2=y+H)

def cover_fit_img(im):
    sc=max(W/im.width,H/im.height)
    im=im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
    l=(im.width-W)//2; t=(im.height-H)//2
    return im.crop((l,t,l+W,t+H))

# ---------- 스크립트 파싱 ----------
shots=[]  # (n, mode, trans, ko, en)
cur=None
for line in open(os.path.join(SF,"sejong_master_shotscript_48.md"),encoding="utf-8"):
    mh=re.match(r"^\*\*S(\d+)\s*·\s*([🎬✏️].*?)\s*·.*?(?:→(\S+))?\*\*",line)
    if mh:
        n=int(mh.group(1)); mode="real" if "🎬" in mh.group(2) else "anim"
        trans=(mh.group(3) or "컷")
        cur={"n":n,"mode":mode,"trans":trans,"ko":"","en":""}; shots.append(cur); continue
    mk=re.match(r"^-\s*KO:\s*(.*)$",line); me=re.match(r"^-\s*EN:\s*(.*)$",line)
    if mk and cur: cur["ko"]=mk.group(1).strip()
    if me and cur: cur["en"]=me.group(1).strip()

LOGO_SZ=96
logo=Image.open(LOGO).convert("RGBA").resize((LOGO_SZ,LOGO_SZ),Image.LANCZOS)
# Veo ✦ 워터마크는 모든 클립에서 고정 위치(렌더 기준 중심 ≈1727,895). 로고를 그 중심에 딱 맞춰 덮음.
WM_CX, WM_CY = 1727, 895
LOGO_POS=(WM_CX-LOGO_SZ//2, WM_CY-LOGO_SZ//2)

def aud(n):
    p=os.path.join(AUD,f"{LANG}_S{n:02d}.mp3")
    return AudioFileClip(p) if os.path.exists(p) else None

def cap_text(s):
    return s["ko"] if LANG=="ko" else s["en"]

def is_music(t): return ("음악" in t and "없음" in t) or t.lower().startswith("(music")

def shot_visual(n,dur):
    p=os.path.join(CLIPS,f"scene_{n}.mp4")
    if os.path.exists(p):
        v=cover_fit_video(VideoFileClip(p).without_audio())
        return v.with_effects([MultiplySpeed(v.duration/dur)]).subclipped(0,dur)
    kp=os.path.join(KF,f"S{n:02d}.png")
    if os.path.exists(kp):
        return ImageClip(np.array(cover_fit_img(Image.open(kp).convert("RGB")))).with_duration(dur)
    return ImageClip(np.zeros((H,W,3),np.uint8)).with_duration(dur)

def jamo_overlay(n,dur):
    out=[]; js=JAMO.get(n)
    if not js: return out
    k=len(js); span=min(260, (W-300)//k)
    for i,j in enumerate(js):
        ji=text_img(j,150,GOLD,glow=(255,210,90),shadow=False)
        x=int(W*0.5-(k*span)/2+i*span+(span-ji.width)/2)
        y=int(H*0.30); st=0.3+i*0.25
        out.append(pil_clip(ji,max(0.2,dur-st)).with_start(st).with_position((x,y)).with_effects([CrossFadeIn(0.25)]))
    return out

# ---------- 샷 클립 빌드 ----------
def build_shot(s):
    n=s["n"]; a=aud(n)
    music=is_music(cap_text(s))
    dur=(a.duration+0.55) if (a and not music) else (2.6 if music else 3.4)
    # 레이어 순서(뒤→앞): ① 영상(맨 아래) ② 자모 ③ 로고(워터마크 덮기) ④ 타이틀 ⑤ 자막(맨 앞, 안 깨지도록)
    layers=[shot_visual(n,dur)]
    layers+=jamo_overlay(n,dur)
    # 로고: 영상 위·자막 아래 (워터마크만 덮고 자막은 가리지 않음)
    layers.append(pil_clip(logo,dur).with_position(LOGO_POS))
    # S01: 타이틀 오버레이(오프닝)
    if n==1:
        t1,t2=TITLE[LANG]
        layers.append(pil_clip(text_img(t1,120,GOLD,glow=(255,210,90),shadow=True,maxw=W-300),dur).with_position(("center",120)).with_effects([CrossFadeIn(0.6)]))
        layers.append(pil_clip(text_img(t2,52,WHITE,sw=4,shadow=True,maxw=W-360),dur).with_position(("center",300)).with_effects([CrossFadeIn(0.8)]))
    # 자막(음악샷 제외)
    if not music:
        cap=text_img(cap_text(s),48,WHITE,sw=5,shadow=True,maxw=W-300)
        layers.append(pil_clip(cap,dur).with_position(("center",H-cap.height-64)).with_effects([CrossFadeIn(0.3)]))
    comp=CompositeVideoClip(layers,size=(W,H)).with_duration(dur)
    return comp,(a if (a and not music) else None),dur

# ---------- 타임라인(전환) 조립 ----------
placed=[]; auds=[]; t=0.0; prev_trans="컷"
for s in shots:
    comp,a,dur=build_shot(s)
    inxf=XF if prev_trans in DISSOLVE else 0.0
    start=max(0.0,t-inxf)
    if inxf>0: comp=comp.with_effects([CrossFadeIn(inxf)])
    comp=comp.with_start(start)
    placed.append(comp)
    if a is not None: auds.append(a.with_start(start+(inxf*0.5)))
    t=start+dur
    prev_trans=s["trans"]

final=CompositeVideoClip(placed,size=(W,H)).with_duration(t)
if auds: final=final.with_audio(CompositeAudioClip(auds))
TAG = sys.argv[3] if len(sys.argv) > 3 else ""   # 출력 버전 태그(옛 영상 보존용). 예: v2 -> sejong_main_hybrid_ko_v2.mp4
out=os.path.join(MAIN,f"sejong_main_hybrid_{LANG}{('_'+TAG) if TAG else ''}.mp4")
final.write_videofile(out,fps=30,codec="libx264",audio_codec="aac",preset="medium",threads=4)
print("DONE:",out,f"{final.duration:.1f}s ({final.duration/60:.1f}분)")
