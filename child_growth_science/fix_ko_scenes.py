# -*- coding: utf-8 -*-
"""씬6·7 한글 나레이션 교정(Dae): 숫자를 한글로 정확히("십삼","이로"). 슬롯에 맞춰 교체 후 재먹싱."""
import os, re, json, subprocess, urllib.request
CG = "D:/Entertainments/DevEnvironment/autovideo/child_growth_science"
ROOT = "D:/Entertainments/DevEnvironment/autovideo"
KODIR = os.path.join(CG, "_ko_dae")
DAE = "HHlsD8ZpKBtIAyvlCGoz"
key = [l.split("=",1)[1].strip() for l in open(os.path.join(ROOT,".env"),encoding="utf-8") if l.startswith("ELEVEN_API_KEY=")][0]

# 교정 텍스트 (자막은 그대로 13/2, 오디오만 한글발음)
FIX = {
 6: "아들의 예상 키는, 아빠와 엄마의 키를 더한 뒤, 십삼 센티미터를 더하고, 이로 나누어 구합니다.",
 7: "딸의 예상 키는, 아빠와 엄마의 키를 더한 뒤, 십삼 센티미터를 빼고, 똑같이 이로 나눕니다.",
}
def parse(p):
    out=[]
    for blk in open(p,encoding="utf-8").read().strip().split("\n\n"):
        L=blk.strip().split("\n")
        if len(L)<3: continue
        m=re.match(r"(\d+):(\d+):([\d,\.]+) --> (\d+):(\d+):([\d,\.]+)",L[1])
        f=lambda h,mi,se:int(h)*3600+int(mi)*60+float(se.replace(",","."))
        out.append((f(m[1],m[2],m[3]),f(m[4],m[5],m[6])))
    return out
cues=parse(os.path.join(CG,"child_growth.ko.srt"))
def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
    except: return 0.0
def tts(text,out):
    b={"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.5,"similarity_boost":0.8,"style":0.0,"use_speaker_boost":True,"speed":1.0}}
    r=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{DAE}?output_format=mp3_44100_128",data=json.dumps(b).encode(),method="POST",headers={"xi-api-key":key,"Content-Type":"application/json"})
    open(out,"wb").write(urllib.request.urlopen(r,timeout=120).read())
def fit(src,slot,dst):
    d=dur(src); factor=max(0.85,min(1.2, d/slot if slot>0 else 1.0))
    subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-filter:a",f"atempo={factor:.4f}","-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","160k",dst+"_a.mp3"],timeout=60)
    subprocess.run(["ffmpeg","-y","-v","error","-i",dst+"_a.mp3","-af",f"apad,atrim=0:{slot:.3f}","-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","160k",dst],timeout=60)
    try: os.remove(dst+"_a.mp3")
    except: pass
for sc,txt in FIX.items():
    st,ed=cues[sc]; slot=ed-st
    raw=os.path.join(KODIR,f"{sc:03d}_raw.mp3"); tts(txt,raw)
    fitted=os.path.join(KODIR,f"{sc:03d}.mp3"); fit(raw,slot,fitted)
    print(f"씬{sc} 교정: 슬롯{slot:.1f}s -> {dur(fitted):.1f}s  「{txt[:30]}…」")
print("SCENES_FIXED")
