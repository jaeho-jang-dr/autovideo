# -*- coding: utf-8 -*-
"""정주행 쇼츠 9:16 오리지널 구글 Flow 비디오 합성 및 한/영 나레이션+자막 빌더.
사용: python binge_watching/make_binge_short_916.py <ko|en>"""
import os, re, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, CompositeAudioClip
from moviepy.video.fx import MultiplySpeed as VideoMultiplySpeed
from moviepy.audio.fx import MultiplySpeed as AudioMultiplySpeed

CG = "binge_watching"
ROOT = "."
LANG = sys.argv[1] if len(sys.argv)>1 else "ko"
ADIR = f"{CG}/_ko_sunhi" if LANG=="ko" else f"{CG}/_en_emma"
SRT = f"{CG}/binge_watching.{LANG}.srt"
MALGUN=r"C:\Windows\Fonts\malgunbd.ttf"; ARIALBD=r"C:\Windows\Fonts\arialbd.ttf"
FONT = MALGUN if LANG=="ko" else ARIALBD
W,H=2160,3840 # 세로 4K UHD 해상도로 업스케일
SCENES=[0,2,20]
TITLE = {"ko":"밤샘 정주행\n내 몸엔 무슨 일이?","en":"Binge-Watching\n& Your Body"}[LANG]
SRC_DIR = "shorts_src" # 구글 Flow에서 aspect=9:16 으로 뽑아낸 소스 디렉토리

# SRT 파서
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

segs=[]; auds=[]; t=0.0
for idx,sc in enumerate(SCENES):
    # 씬 소스 경로 (shorts_prompts/scene_0.mp4 등)
    sc_path = os.path.join(SRC_DIR, f"scene_{sc}.mp4")
    if not os.path.exists(sc_path):
        # 폴백: binge_watching 아래 scene_0.mp4 등을 1080x1920으로 크롭하여 사용
        sc_path = os.path.join(CG, f"scene_{sc}.mp4")
        print(f"Warning: 9:16 source not found. Using fallback crop for scene {sc}")
        is_fallback = True
    else:
        is_fallback = False
        
    st,ed,txt=cues[sc]; slot=ed-st
    ap=os.path.join(ADIR,f"{sc:03d}.mp3")
    
    # 오디오 1.1배속 로드 및 길이 계산
    if os.path.exists(ap):
        ac = AudioFileClip(ap)
        # 1.1x 오디오 속도 향상 적용
        ac = ac.with_effects([AudioMultiplySpeed(1.1)])
        seglen = ac.duration
    else:
        ac = None
        seglen = slot / 1.1 # 나레이션 속도 가상 배속에 맞춰 길이 축소
        
    # 비디오 클립 로드 및 9:16 처리
    v = VideoFileClip(sc_path).without_audio()
    if is_fallback:
        # 가로형 폴백 비디오는 높이를 1920으로 늘린 다음 가로 중앙부 크롭
        v = v.resized(height=H)
        x_center = v.w / 2
        v = v.cropped(x1=x_center - W/2, y1=0, width=W, height=H)
    else:
        # 오리지널 9:16 비디오는 그대로 사용하되 해상도 안전화 resizing
        v = v.resized(width=W, height=H)
        
    # 비디오 속도를 오디오 실제 듀레이션(seglen)에 맞춰 변경하여 동기화
    speed_factor = v.duration / seglen
    v = v.with_effects([VideoMultiplySpeed(speed_factor)])
    v = v.with_position(("center", "center"))
    
    # 제목(상단)
    ti=text_png(TITLE, 156, (255,255,255,255), W-240, sw=12) # 폰트/패딩/스트로크 2배 비례 보정
    tclip=ImageClip(np.array(ti)).with_duration(seglen).with_position(("center",240))
    # 자막(하단)
    ci=text_png(txt, 116, (255,230,120,255), W-240, sw=10) # 폰트/패딩/스트로크 2배 비례 보정
    cclip=ImageClip(np.array(ci)).with_duration(seglen).with_position(("center", H - ci.size[1] - 240))
    
    comp=CompositeVideoClip([v,tclip,cclip],size=(W,H)).with_duration(seglen).with_start(t)
    segs.append(comp)
    if ac:
        auds.append(ac.with_start(t))
    t+=seglen

final=CompositeVideoClip(segs,size=(W,H)).with_duration(t)

# 채널 로고
try:
    lg=Image.open(os.path.join(ROOT,"assets","drjay_ed_logo_circle.png")).convert("RGBA").resize((180,180),Image.LANCZOS)
    lclip=ImageClip(np.array(lg),transparent=True).with_duration(t).with_position((W-220,H-300))
    final=CompositeVideoClip([final,lclip],size=(W,H)).with_duration(t)
except Exception: pass

temp_audio = f"{CG}/temp_{LANG}.m4a"
if auds: final=final.with_audio(CompositeAudioClip(auds))
out=os.path.join(CG,f"binge_short_{LANG}.mp4")
final.write_videofile(out,fps=30,codec="libx264",audio_codec="aac",preset="medium",threads=4,temp_audiofile=temp_audio,remove_temp=False)
print("SHORT DONE:",out,f"{final.duration:.1f}s")

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
