# -*- coding: utf-8 -*-
"""최면 영상 재작업: 인트로(씬1)·아웃트로(씬16) 제거 → 씬 2~15만 사용.
나레이션 Azure 선희(KO)/Emma(EN) 1.1배속, 슬롯=max(ko,en)+pad, 영상 슬롯맞춤.
출력: hypnosis_azure.mp4 (KO기본+EN 오디오트랙 + ko/en 소프트자막) + ko/en .srt 새로 생성."""
import os, re, subprocess, urllib.request
import numpy as np
from PIL import Image
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.fx import MultiplySpeed

ROOT = "D:/Entertainments/DevEnvironment/autovideo"
HS = os.path.join(ROOT, "hypnosis_science")
W, H = 1920, 1080
USE = list(range(2, 16))            # 씬 2~15 (인트로1·아웃트로16 제거)
PAD = 0.35
SPEED = 1.1                          # 나레이션 1.1배속
VOICE = {"ko": "ko-KR-SunHiNeural", "en": "en-US-EmmaMultilingualNeural"}
XML = {"ko": "ko-KR", "en": "en-US"}
LOGO = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
KODIR = os.path.join(HS, "_ko_sunhi"); ENDIR = os.path.join(HS, "_en_emma")
TMP = os.path.join(HS, "_az2_tmp")
for d in (KODIR, ENDIR, TMP): os.makedirs(d, exist_ok=True)
key = [l.split("=",1)[1].strip() for l in open(os.path.join(ROOT,".env"),encoding="utf-8") if l.startswith("AZURE_SPEECH_KEY=")][0]
region = [l.split("=",1)[1].strip() for l in open(os.path.join(ROOT,".env"),encoding="utf-8") if l.startswith("AZURE_SPEECH_REGION=")][0]

def log(m): print(m, flush=True)
def esc(t): return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
    except Exception: return 0.0
def tts(text, lang, out):
    ssml=f'<speak version="1.0" xml:lang="{XML[lang]}"><voice name="{VOICE[lang]}">{esc(text)}</voice></speak>'
    req=urllib.request.Request(f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"), method="POST",
        headers={"Ocp-Apim-Subscription-Key":key,"Content-Type":"application/ssml+xml",
                 "X-Microsoft-OutputFormat":"audio-24khz-96kbitrate-mono-mp3","User-Agent":"drjay-tts"})
    open(out,"wb").write(urllib.request.urlopen(req,timeout=40).read())
def atempo(src, factor, dst):
    subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-filter:a",f"atempo={factor:.4f}","-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","160k",dst],timeout=60)
def pad_to(src, slot, dst):
    subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-af",f"apad,atrim=0:{slot:.3f}","-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","160k",dst],timeout=60)

# ---- 시나리오 파싱 (ko/en) ----
scenes={}; cur=None
for line in open(os.path.join(HS,"scenario.txt"),encoding="utf-8"):
    s=line.strip()
    m=re.match(r"\[Scene (\d+)\]", s)
    if m: cur=int(m.group(1)); scenes[cur]={}
    elif s.startswith("text_en:") and cur: scenes[cur]["en"]=s[len("text_en:"):].strip()
    elif s.startswith("text:") and cur: scenes[cur]["ko"]=s[len("text:"):].strip()

# ---- 1) TTS + 1.1x, 슬롯 계산 ----
info={}
for n in USE:
    ko_raw=os.path.join(KODIR,f"{n:02d}_raw.mp3"); en_raw=os.path.join(ENDIR,f"{n:02d}_raw.mp3")
    if not os.path.exists(ko_raw) or os.path.getsize(ko_raw)<600: tts(scenes[n]["ko"],"ko",ko_raw)
    if not os.path.exists(en_raw) or os.path.getsize(en_raw)<600: tts(scenes[n]["en"],"en",en_raw)
    ko11=os.path.join(KODIR,f"{n:02d}_11.mp3"); en11=os.path.join(ENDIR,f"{n:02d}_11.mp3")
    atempo(ko_raw,SPEED,ko11); atempo(en_raw,SPEED,en11)
    dko,den=dur(ko11),dur(en11); slot=round(max(dko,den)+PAD,3)
    info[n]={"slot":slot,"ko":ko11,"en":en11}
    log(f"S{n:02d} ko={dko:.1f} en={den:.1f} slot={slot:.1f}")
TOTAL=sum(info[n]["slot"] for n in USE)
log(f"총 길이 {TOTAL:.1f}s ({TOTAL/60:.2f}분), {len(USE)}씬")

# ---- 2) 오디오 트랙(ko/en): 슬롯 패딩 후 concat ----
def build_track(lang):
    parts=[]
    for n in USE:
        fitted=os.path.join(TMP,f"{lang}_{n:02d}.mp3"); pad_to(info[n][lang],info[n]["slot"],fitted); parts.append(fitted)
    listf=os.path.join(TMP,f"list_{lang}.txt")
    open(listf,"w",encoding="utf-8").write("\n".join(f"file '{p}'" for p in parts))
    track=os.path.join(TMP,f"track_{lang}.m4a")
    subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",listf,"-c:a","aac","-b:a","192k",track],timeout=180)
    return track
kot=build_track("ko"); ent=build_track("en")
log(f"오디오 트랙: ko={dur(kot):.1f}s en={dur(ent):.1f}s")

# ---- 3) 자막(ko/en) 새로 생성 ----
def fmt(x):
    h=int(x//3600); m=int((x%3600)//60); s=x%60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".",",")
for lang in ("ko","en"):
    t=0.0; lines=[]
    for i,n in enumerate(USE,1):
        lines.append(f"{i}\n{fmt(t)} --> {fmt(t+info[n]['slot'])}\n{scenes[n][lang]}\n")
        t+=info[n]["slot"]
    open(os.path.join(HS,f"hypnosis_science.{lang}.srt"),"w",encoding="utf-8").write("\n".join(lines))
log("자막 ko/en .srt 재생성 완료")

# ---- 4) 영상 재구성 (씬 2~15, 슬롯맞춤, 로고+워터마크커버) ----
logo_im=Image.open(LOGO).convert("RGBA").resize((96,96),Image.LANCZOS)
segs=[]
for n in USE:
    slot=info[n]["slot"]
    v=VideoFileClip(os.path.join(HS,f"scene_{n}.mp4")).without_audio().resized(new_size=(W,H))
    v=v.with_effects([MultiplySpeed(v.duration/slot)])
    lg=ImageClip(np.array(logo_im),transparent=True).with_duration(slot).with_position((1727-48,895-48))  # Veo 워터마크 중심 덮기
    comp=CompositeVideoClip([v,lg],size=(W,H)).with_duration(slot)
    segs.append(comp)
final=concatenate_videoclips(segs,method="compose")
silent=os.path.join(TMP,"silent.mp4")
final.write_videofile(silent,fps=24,codec="libx264",audio=False,preset="medium",threads=4)
final.close()
for s in segs:
    try: s.close()
    except Exception: pass

# ---- 5) 멀티트랙 먹싱 (영상 + ko/en 오디오 + ko/en 소프트자막) ----
out=os.path.join(HS,"hypnosis_azure.mp4")
subprocess.run(["ffmpeg","-y","-v","error","-i",silent,"-i",kot,"-i",ent,
    "-i",os.path.join(HS,"hypnosis_science.ko.srt"),"-i",os.path.join(HS,"hypnosis_science.en.srt"),
    "-map","0:v","-map","1:a","-map","2:a","-map","3","-map","4",
    "-c:v","copy","-c:a","aac","-b:a","192k","-c:s","mov_text",
    "-metadata:s:a:0","language=kor","-metadata:s:a:0","title=한국어(선희)",
    "-metadata:s:a:1","language=eng","-metadata:s:a:1","title=English(Emma)",
    "-metadata:s:s:0","language=kor","-metadata:s:s:1","language=eng",
    "-disposition:a:0","default", out],timeout=600)
log(f"HYPNOSIS AZURE DONE: {out}  {dur(out)/60:.2f}분  ({W}x{H})")
