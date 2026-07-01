# -*- coding: utf-8 -*-
"""다국어 A안 마스터 — KO 기준 타임라인(ko_dur+여백≈12분). 언어별 오디오 맞춤:
  · 슬롯보다 길면(JA/ZH) ffmpeg atempo로 압축  · 짧으면(KO/EN/ES) 자연속도+뒤 여백은 배경음악.
드래프트는 자막 burn-in(페이싱 확인). 최종 A안은 자막 소프트(.srt)로 뺄 예정.
사용: python compile_main_multi.py <lang> [narrdir]  (lang=ko/en/zh/ja/es)"""
import os, json, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import (ImageClip, VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip)
from moviepy.video.fx import MultiplySpeed, CrossFadeIn
from moviepy.audio.fx import MultiplyVolume, AudioFadeIn, AudioFadeOut

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SF = os.path.join(ROOT, "sejong_film"); MAIN = os.path.join(SF, "main")
KF = os.path.join(MAIN, "keyframes"); CLIPS = os.path.join(ROOT, "sejong_main_kf")
I18N = os.path.join(MAIN, "i18n"); FITDIR = os.path.join(MAIN, "audio_fit")
os.makedirs(FITDIR, exist_ok=True)
LOGO = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
BGM = os.path.join(ROOT, "assets", "audio", "yeomillak_bgm.wav")   # 여민락(CC BY, 한국저작권위원회) — 국악기 연주 용비어천가
FONTS = {"ko":r"C:\Windows\Fonts\malgunbd.ttf","en":r"C:\Windows\Fonts\malgunbd.ttf","es":r"C:\Windows\Fonts\malgunbd.ttf",
         "zh":r"C:\Windows\Fonts\msyhbd.ttc","ja":r"C:\Windows\Fonts\meiryob.ttc"}
W, H = 1920, 1080
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
NARRDIR = sys.argv[2] if len(sys.argv) > 2 else "audio_free"
AUD = os.path.join(MAIN, NARRDIR)
CAPFONT = FONTS.get(LANG, FONTS["ko"]); CAPFONT = CAPFONT if os.path.exists(CAPFONT) else FONTS["ko"]
GOLD=(245,200,75,255); WHITE=(255,255,255,255); XF=0.6
DISSOLVE=("디졸브","모프","페이드","입자와이프","슬라이드")
PAD=0.6          # KO 기준 씬 여백(초)
BGM_VOL=0.13
JAMO={28:["ㄱ","ㄴ","ㄷ","ㅁ","ㅂ","ㅅ","ㅇ","ㅈ","ㅎ","ㅏ","ㅓ","ㅗ","ㅜ"],37:["ㄱ","ㄴ","ㅁ"],38:["ㄴ","ㄷ","ㅌ"],39:["ㆍ","ㅡ","ㅣ"],40:["ㅏ","ㅓ","ㅗ","ㅜ"],47:["ㄱ","ㅁ","ㅇ","ㅏ","ㅣ","ㅡ"]}
TITLE={"ko":("세종대왕과 한글","한글은 어떻게 태어났을까?"),"en":("King Sejong & Hangeul","How were the letters born?"),
       "zh":("世宗大王与韩文","韩文是怎样诞生的？"),"ja":("世宗大王とハングル","ハングルはどう生まれた？"),"es":("El Rey Sejong y el Hangeul","¿Cómo nacieron las letras?")}

def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True,timeout=20).stdout.strip())
    except Exception: return 0.0

def _wrap(text,font,maxw):
    d=ImageDraw.Draw(Image.new("RGBA",(4,4)))
    if LANG in ("zh","ja"):
        lines=[]; cur=""
        for ch in text:
            if d.textlength(cur+ch,font=font)<=maxw: cur+=ch
            else: lines.append(cur); cur=ch
        if cur: lines.append(cur)
        return lines or [text]
    words=text.split(" "); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines or [text]

def text_img(text,size,fill,sw=6,shadow=True,glow=None,maxw=None,fontpath=None):
    font=ImageFont.truetype(fontpath or CAPFONT,size)
    lines=_wrap(text,font,maxw) if maxw else [text]
    asc,desc=font.getmetrics(); lh=asc+desc+8
    d0=ImageDraw.Draw(Image.new("RGBA",(4,4))); tw=max(d0.textlength(l,font=font) for l in lines)
    pad=sw+(46 if glow else 26); img=Image.new("RGBA",(int(tw)+pad*2,lh*len(lines)+pad*2),(0,0,0,0))
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
    draw_all(d,0,0,fill,(20,25,45,255)); return img

def pil_clip(img,d): return ImageClip(np.array(img.convert("RGBA")),transparent=True).with_duration(d)
def cover_fit_video(v):
    sc=max(W/v.w,H/v.h); v=v.resized(sc); x=(v.w-W)/2; y=(v.h-H)/2; return v.cropped(x1=x,y1=y,x2=x+W,y2=y+H)
def cover_fit_img(im):
    sc=max(W/im.width,H/im.height); im=im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
    l=(im.width-W)//2; t=(im.height-H)//2; return im.crop((l,t,l+W,t+H))

narr={d["n"]:d for d in json.load(open(os.path.join(I18N,"narration.json"),encoding="utf-8"))}
order=[r["n"] for r in json.load(open(os.path.join(I18N,"timeline.json"),encoding="utf-8"))["rows"]]
_LIM=int(os.environ.get("MULTI_MAXSCENES","0"))
if _LIM>0: order=order[:_LIM]   # 샘플 렌더용(앞 N씬)
TRANS={r["n"]:r["trans"] for r in json.load(open(os.path.join(I18N,"timeline.json"),encoding="utf-8"))["rows"]}
MUSIC={r["n"]:r["music"] for r in json.load(open(os.path.join(I18N,"timeline.json"),encoding="utf-8"))["rows"]}

# ---- 슬롯 = 5개 언어 씬별 최댓값(모두 자연속도로 들어감, 압축 불필요) ----
L5=["ko","en","zh","ja","es"]
SLOT={}
for n in order:
    if MUSIC[n]: SLOT[n]=2.6; continue
    ds=[dur(os.path.join(AUD,f"{L}_S{n:02d}.mp3")) for L in L5 if os.path.exists(os.path.join(AUD,f"{L}_S{n:02d}.mp3"))]
    SLOT[n]=round((max(ds) if ds else 3.0)+PAD,2)

logo=Image.open(LOGO).convert("RGBA").resize((96,96),Image.LANCZOS); LOGO_POS=(1727-48,895-48)

def fitted_audio(n):
    """언어 나레이션을 슬롯에 맞춤: 길면 atempo 압축, 짧으면 그대로."""
    p=os.path.join(AUD,f"{LANG}_S{n:02d}.mp3")
    if not os.path.exists(p): return None
    d=dur(p); target=SLOT[n]-0.3
    if d>target+0.05 and target>0.5:
        factor=min(2.0,max(0.5,d/target))
        fp=os.path.join(FITDIR,f"{LANG}_S{n:02d}_x{factor:.3f}.mp3")
        if not os.path.exists(fp) or os.path.getsize(fp)<800:
            subprocess.run(["ffmpeg","-y","-v","error","-i",p,"-filter:a",f"atempo={factor:.4f}",fp],timeout=60)
        return AudioFileClip(fp) if os.path.exists(fp) else AudioFileClip(p)
    return AudioFileClip(p)

def cap_text(n): return narr[n].get(LANG,"") or ""
def shot_visual(n,d):
    p=os.path.join(CLIPS,f"scene_{n}.mp4")
    if os.path.exists(p):
        v=cover_fit_video(VideoFileClip(p).without_audio()); return v.with_effects([MultiplySpeed(v.duration/d)]).subclipped(0,d)
    kp=os.path.join(KF,f"S{n:02d}.png")
    if os.path.exists(kp): return ImageClip(np.array(cover_fit_img(Image.open(kp).convert("RGB")))).with_duration(d)
    return ImageClip(np.zeros((H,W,3),np.uint8)).with_duration(d)
def jamo_overlay(n,d):
    out=[]; js=JAMO.get(n)
    if not js: return out
    k=len(js); span=min(260,(W-300)//k)
    for i,j in enumerate(js):
        ji=text_img(j,150,GOLD,glow=(255,210,90),shadow=False,fontpath=r"C:\Windows\Fonts\malgunbd.ttf")
        x=int(W*0.5-(k*span)/2+i*span+(span-ji.width)/2); y=int(H*0.30); st=0.3+i*0.25
        out.append(pil_clip(ji,max(0.2,d-st)).with_start(st).with_position((x,y)).with_effects([CrossFadeIn(0.25)]))
    return out

def build_shot(n):
    d=SLOT[n]; a=None if MUSIC[n] else fitted_audio(n)
    layers=[shot_visual(n,d)]; layers+=jamo_overlay(n,d)
    layers.append(pil_clip(logo,d).with_position(LOGO_POS))
    if n==1:
        t1,t2=TITLE[LANG]
        layers.append(pil_clip(text_img(t1,120,GOLD,glow=(255,210,90),shadow=True,maxw=W-300),d).with_position(("center",120)).with_effects([CrossFadeIn(0.6)]))
        layers.append(pil_clip(text_img(t2,52,WHITE,sw=4,shadow=True,maxw=W-360),d).with_position(("center",300)).with_effects([CrossFadeIn(0.8)]))
    if not MUSIC[n] and cap_text(n):
        cap=text_img(cap_text(n),46,WHITE,sw=5,shadow=True,maxw=W-300)
        layers.append(pil_clip(cap,d).with_position(("center",H-cap.height-64)).with_effects([CrossFadeIn(0.3)]))
    comp=CompositeVideoClip(layers,size=(W,H)).with_duration(d)
    return comp,a,d

placed=[]; auds=[]; narr_intervals=[]; t=0.0; prev="컷"
for n in order:
    comp,a,d=build_shot(n); inxf=XF if prev in DISSOLVE else 0.0; start=max(0.0,t-inxf)
    if inxf>0: comp=comp.with_effects([CrossFadeIn(inxf)])
    comp=comp.with_start(start); placed.append(comp)
    if a is not None:
        astart=start+(inxf*0.5); auds.append(a.with_start(astart))
        narr_intervals.append((astart, astart+a.duration))   # 덕킹용 나레이션 구간
    t=start+d; prev=TRANS[n]
TOTAL=t

# ---- 배경음악(여민락) + 덕킹: 나레이션 중 절반 볼륨, 빈곳 full ----
if os.path.exists(BGM):
    m=AudioFileClip(BGM); md=m.duration
    loops=[]; acc=0.0
    while acc<TOTAL: loops.append(m.with_start(acc)); acc+=md
    music_loop=CompositeAudioClip(loops).with_duration(TOTAL)
    pts=sorted(set([0.0,TOTAL]+[max(0.0,min(TOTAL,x)) for (s,e) in narr_intervals for x in (s,e)]))
    def _isnarr(mid): return any(s<=mid<e for (s,e) in narr_intervals)
    pieces=[]
    for i in range(len(pts)-1):
        t0,t1=pts[i],pts[i+1]
        if t1-t0<0.05: continue
        vol=(BGM_VOL*0.5) if _isnarr((t0+t1)/2) else BGM_VOL     # 나레이션=절반, 빈곳=full
        pieces.append(music_loop.subclipped(t0,t1).with_effects([MultiplyVolume(vol)]).with_start(t0))
    ducked=CompositeAudioClip(pieces).with_duration(TOTAL).with_effects([AudioFadeIn(1.5),AudioFadeOut(2.5)])
    auds=[ducked]+auds

final=CompositeVideoClip(placed,size=(W,H)).with_duration(TOTAL)
if auds: final=final.with_audio(CompositeAudioClip(auds))
out=os.path.join(MAIN,f"sejong_multi_draft_{LANG}.mp4")
final.write_videofile(out,fps=30,codec="libx264",audio_codec="aac",preset="medium",threads=4)
print("DONE:",out,f"{final.duration:.1f}s ({final.duration/60:.2f}분)")
