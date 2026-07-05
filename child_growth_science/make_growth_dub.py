# -*- coding: utf-8 -*-
"""child_growth 더빙 교체: KO=Dae, EN=Alice. 각 씬을 자막 슬롯에 꽉 맞춤(공백0, KO/EN 동기).
영상(4K)은 그대로, 오디오만 재-먹싱. 출력: child_growth_dub.mp4 (KO기본+EN트랙+ko/en자막)."""
import os, re, json, subprocess, urllib.request
CG = "D:/Entertainments/DevEnvironment/autovideo/child_growth_science"
ROOT = "D:/Entertainments/DevEnvironment/autovideo"
VIDEO = os.path.join(CG, "child_growth.mp4")
KODIR = os.path.join(CG, "_ko_dae"); ENDIR = os.path.join(CG, "_en_alice")
os.makedirs(KODIR, exist_ok=True); os.makedirs(ENDIR, exist_ok=True)
TMP = os.path.join(CG, "_dub_tmp"); os.makedirs(TMP, exist_ok=True)
VID = {"Dae": "HHlsD8ZpKBtIAyvlCGoz", "Alice": "Xb7hH8MSUJpSbSDYk0k2"}
key = [l.split("=",1)[1].strip() for l in open(os.path.join(ROOT,".env"),encoding="utf-8") if l.startswith("ELEVEN_API_KEY=")][0]

def parse(p):
    out=[]
    for blk in open(p,encoding="utf-8").read().strip().split("\n\n"):
        L=blk.strip().split("\n")
        if len(L)<3: continue
        m=re.match(r"(\d+):(\d+):([\d,\.]+) --> (\d+):(\d+):([\d,\.]+)",L[1])
        if not m: continue
        f=lambda h,mi,se:int(h)*3600+int(mi)*60+float(se.replace(",","."))
        out.append((f(m[1],m[2],m[3]), f(m[4],m[5],m[6]), " ".join(L[2:])))
    return out
ko=parse(os.path.join(CG,"child_growth.ko.srt")); en=parse(os.path.join(CG,"child_growth.en.srt"))
N=len(ko)
def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
    except: return 0.0
VDUR=dur(VIDEO)
def tts(vid,text,out):
    b={"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.5,"similarity_boost":0.8,"style":0.0,"use_speaker_boost":True,"speed":1.0}}
    r=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128",data=json.dumps(b).encode(),method="POST",headers={"xi-api-key":key,"Content-Type":"application/json"})
    open(out,"wb").write(urllib.request.urlopen(r,timeout=120).read())
def fit(src,slot,dst):
    """자연 클립을 슬롯 길이에 꽉 맞춤: atempo(0.85~1.2) + 정확히 트림/패드."""
    d=dur(src); factor=max(0.85,min(1.2, d/slot if slot>0 else 1.0))
    subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-filter:a",f"atempo={factor:.4f}","-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","160k",dst+"_a.mp3"],timeout=60)
    # 정확히 slot 길이로 pad+trim
    subprocess.run(["ffmpeg","-y","-v","error","-i",dst+"_a.mp3","-af",f"apad,atrim=0:{slot:.3f}","-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","160k",dst],timeout=60)
    try: os.remove(dst+"_a.mp3")
    except: pass

def build(lang, cues, voice, outdir):
    parts=[]
    for i,(st,ed,txt) in enumerate(cues):
        slot=ed-st
        raw=os.path.join(outdir,f"{i:03d}_raw.mp3")
        if not os.path.exists(raw) or os.path.getsize(raw)<800:
            tts(VID[voice],txt,raw)
        fitted=os.path.join(outdir,f"{i:03d}.mp3"); fit(raw,slot,fitted); parts.append((st,fitted))
    # concat 순서대로(슬롯 연속) → 트랙
    listf=os.path.join(TMP,f"list_{lang}.txt")
    with open(listf,"w",encoding="utf-8") as f:
        for _,p in parts: f.write(f"file '{p}'\n")
    track=os.path.join(CG,f"track_{lang}.m4a")
    subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",listf,"-af",f"apad,atrim=0:{VDUR:.3f}","-c:a","aac","-b:a","192k",track],timeout=180)
    print(f"{lang} 트랙: {dur(track):.1f}s (영상 {VDUR:.1f}s)"); return track

kot=build("ko",ko,"Dae",KODIR)
ent=build("en",en,"Alice",ENDIR)
# 먹싱: 영상 copy + ko(기본)+en(트랙) + 기존 자막 유지
out=os.path.join(CG,"child_growth_dub.mp4")
subprocess.run(["ffmpeg","-y","-v","error","-i",VIDEO,"-i",kot,"-i",ent,
    "-map","0:v","-map","1:a","-map","2:a","-map","0:s?",
    "-c:v","copy","-c:a","aac","-b:a","192k","-c:s","copy",
    "-metadata:s:a:0","language=kor","-metadata:s:a:0","title=한국어(Dae)",
    "-metadata:s:a:1","language=eng","-metadata:s:a:1","title=English(Alice)",
    "-disposition:a:0","default", out],timeout=600)
print("DUB DONE:",out,f"{dur(out)/60:.2f}분")
