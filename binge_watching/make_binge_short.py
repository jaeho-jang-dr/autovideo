# -*- coding: utf-8 -*-
"""아이 키 성장 쇼츠(9:16) — 본편 클립 재사용 + Dae/Alice 나레이션 + 큰 자막. KO/EN.
씬0(훅)+씬6(아들공식)+씬7(딸공식). 사용: python make_growth_short.py <ko|en>"""
import os, re, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip
CG = "binge_watching"
ROOT = "."
LANG = sys.argv[1] if len(sys.argv)>1 else "ko"
MASTER = f"{CG}/binge_watching_science_4k.mp4"
ADIR = f"{CG}/_ko_sunhi" if LANG=="ko" else f"{CG}/_en_emma"
SRT = f"{CG}/binge_watching.{LANG}.srt"
MALGUN=r"C:\Windows\Fonts\malgunbd.ttf"; ARIALBD=r"C:\Windows\Fonts\arialbd.ttf"
FONT = MALGUN if LANG=="ko" else ARIALBD
W,H=1080,1920
SCENES=[0,2,20]
TITLE = {"ko":"밤샘 정주행\n내 몸엔 무슨 일이?","en":"Binge-Watching\n& Your Body"}[LANG]

def parse(p):
    out=[]
    for blk in open(p,encoding="utf-8").read().strip().split("\n\n"):
        L=blk.strip().split("\n")
        if len(L)<3: continue
        m=re.match(r"(\d+):(\d+):([\d,\.]+) --> (\d+):(\d+):([\d,\.]+)",L[1])
        f=lambda h,mi,se:int(h)*3600+int(mi)*60+float(se.replace(",","."))
        out.append((f(m[1],m[2],m[3]),f(m[4],m[5],m[6])," ".join(L[2:])))
    return out
cues=parse(SRT)
def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
    except: return 0.0

def wrap(txt,font,maxw,d):
    words=txt.split(" "); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines

def text_png(txt,size,fill,maxw,sw=5):
    font=ImageFont.truetype(FONT,size); tmp=ImageDraw.Draw(Image.new("RGBA",(4,4)))
    lines=[]
    for seg in txt.split("\n"): lines+=wrap(seg,font,maxw,tmp)
    asc,desc=font.getmetrics(); lh=asc+desc+10
    im=Image.new("RGBA",(maxw+80,lh*len(lines)+40),(0,0,0,0)); d=ImageDraw.Draw(im)
    for i,l in enumerate(lines):
        lw=d.textlength(l,font=font); x=(im.width-lw)/2; y=20+i*lh
        d.text((x,y),l,font=font,fill=fill,stroke_width=sw,stroke_fill=(25,45,30,255))
    return im

VID_H=608  # 16:9 클립을 폭 1080에 맞춤 -> 짝수 높이 608
segs=[]; auds=[]; t=0.0
for idx,sc in enumerate(SCENES):
    st,ed,txt=cues[sc]; slot=ed-st
    ap=os.path.join(ADIR,f"{sc:03d}.mp3"); ad=dur(ap) if os.path.exists(ap) else slot
    seglen=ad
    # Scale video height to H (1920) and crop horizontal edges to fill 9:16 screen (Crop-to-Center)
    v=VideoFileClip(MASTER).subclipped(st,ed).without_audio().resized(height=H)
    x_center = v.w / 2
    v=v.cropped(x1=x_center - W/2, y1=0, width=W, height=H)
    v=v.with_duration(seglen).with_position(("center", "center"))
    # 제목(상단)
    ti=text_png(TITLE, 78, (255,255,255,255), W-120, sw=6)
    tclip=ImageClip(np.array(ti)).with_duration(seglen).with_position(("center",120))
    # 자막(하단)
    ci=text_png(txt, 58, (255,230,120,255), W-120, sw=5)
    cclip=ImageClip(np.array(ci)).with_duration(seglen).with_position(("center", H - ci.size[1] - 120))
    comp=CompositeVideoClip([v,tclip,cclip],size=(W,H)).with_duration(seglen).with_start(t)
    segs.append(comp)
    if os.path.exists(ap): auds.append(AudioFileClip(ap).with_start(t))
    t+=seglen
final=CompositeVideoClip(segs,size=(W,H)).with_duration(t)
# 로고
try:
    lg=Image.open(os.path.join(ROOT,"assets","drjay_ed_logo_circle.png")).convert("RGBA").resize((90,90),Image.LANCZOS)
    lclip=ImageClip(np.array(lg),transparent=True).with_duration(t).with_position((W-110,H-150))
    final=CompositeVideoClip([final,lclip],size=(W,H)).with_duration(t)
except Exception: pass
temp_audio = f"{CG}/temp_{LANG}.m4a"
if auds: final=final.with_audio(CompositeAudioClip(auds))
out=os.path.join(CG,f"binge_short_{LANG}.mp4")
final.write_videofile(out,fps=30,codec="libx264",audio_codec="aac",preset="medium",threads=4,temp_audiofile=temp_audio,remove_temp=False)
print("SHORT DONE:",out,f"{final.duration:.1f}s")

# Clean up resources and temporary files to avoid Windows process locks
final.close()
for s in segs:
    try: s.close()
    except: pass
if os.path.exists(temp_audio):
    import time
    time.sleep(1.5)
    try: os.remove(temp_audio)
    except Exception as e:
        print(f"Warning: could not remove temp audio file {temp_audio}: {e}")

