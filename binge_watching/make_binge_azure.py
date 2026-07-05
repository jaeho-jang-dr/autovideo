# -*- coding: utf-8 -*-
"""정주행 나레이션을 Azure TTS로 재생성: KO=선희(SunHi), EN=Emma. 각 씬 슬롯에 맞춤.
영상은 그대로, 오디오만 재-먹싱. 출력: binge_azure.mp4 (KO기본+EN트랙+한/영 자막)."""
import os, re, subprocess, urllib.request
BW = "D:/Entertainments/DevEnvironment/autovideo/binge_watching"
ROOT = "D:/Entertainments/DevEnvironment/autovideo"
VIDEO = os.path.join(BW, "binge_watching.mp4")
KODIR = os.path.join(BW, "_ko_sunhi"); ENDIR = os.path.join(BW, "_en_emma")
os.makedirs(KODIR, exist_ok=True); os.makedirs(ENDIR, exist_ok=True)
TMP = os.path.join(BW, "_az_tmp"); os.makedirs(TMP, exist_ok=True)
VOICE = {"ko": "ko-KR-SunHiNeural", "en": "en-US-EmmaMultilingualNeural"}
XMLLANG = {"ko": "ko-KR", "en": "en-US"}
key = [l.split("=",1)[1].strip() for l in open(os.path.join(ROOT,".env"),encoding="utf-8") if l.startswith("AZURE_SPEECH_KEY=")][0]
region = [l.split("=",1)[1].strip() for l in open(os.path.join(ROOT,".env"),encoding="utf-8") if l.startswith("AZURE_SPEECH_REGION=")][0]

def parse(p):
    out=[]
    for blk in open(p,encoding="utf-8").read().strip().split("\n\n"):
        L=blk.strip().split("\n")
        if len(L)<3: continue
        m=re.match(r"(\d+):(\d+):([\d,\.]+) --> (\d+):(\d+):([\d,\.]+)",L[1])
        f=lambda h,mi,se:int(h)*3600+int(mi)*60+float(se.replace(",","."))
        out.append((f(m[1],m[2],m[3]),f(m[4],m[5],m[6])," ".join(L[2:])))
    return out
ko=parse(os.path.join(BW,"binge_watching.ko.srt")); en=parse(os.path.join(BW,"binge_watching.en.srt"))
def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
    except: return 0.0
VDUR=dur(VIDEO)
def esc(t): return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def tts(text,lang,out):
    ssml=f'<speak version="1.0" xml:lang="{XMLLANG[lang]}"><voice name="{VOICE[lang]}">{esc(text)}</voice></speak>'
    req=urllib.request.Request(f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),method="POST",
        headers={"Ocp-Apim-Subscription-Key":key,"Content-Type":"application/ssml+xml",
                 "X-Microsoft-OutputFormat":"audio-24khz-96kbitrate-mono-mp3","User-Agent":"drjay-tts"})
    open(out,"wb").write(urllib.request.urlopen(req,timeout=40).read())
def fit(src,slot,dst):
    d=dur(src); factor=max(0.85,min(1.25, d/slot if slot>0 else 1.0))
    subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-filter:a",f"atempo={factor:.4f}","-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","160k",dst+"_a.mp3"],timeout=60)
    subprocess.run(["ffmpeg","-y","-v","error","-i",dst+"_a.mp3","-af",f"apad,atrim=0:{slot:.3f}","-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","160k",dst],timeout=60)
    try: os.remove(dst+"_a.mp3")
    except: pass
def build(lang, cues, outdir):
    parts=[]
    for i,(st,ed,txt) in enumerate(cues):
        slot=ed-st; raw=os.path.join(outdir,f"{i:03d}_raw.mp3")
        if not os.path.exists(raw) or os.path.getsize(raw)<600: tts(txt,lang,raw)
        fitted=os.path.join(outdir,f"{i:03d}.mp3"); fit(raw,slot,fitted); parts.append(fitted)
    listf=os.path.join(TMP,f"list_{lang}.txt")
    with open(listf,"w",encoding="utf-8") as f:
        for p in parts: f.write(f"file '{p}'\n")
    track=os.path.join(BW,f"track_{lang}.m4a")
    subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",listf,"-af",f"apad,atrim=0:{VDUR:.3f}","-c:a","aac","-b:a","192k",track],timeout=180)
    print(f"{lang} 트랙: {dur(track):.1f}s (영상 {VDUR:.1f}s)"); return track
kot=build("ko",ko,KODIR)
ent=build("en",en,ENDIR)
out=os.path.join(BW,"binge_azure.mp4")
subprocess.run(["ffmpeg","-y","-v","error","-i",VIDEO,"-i",kot,"-i",ent,
    "-map","0:v","-map","1:a","-map","2:a","-map","0:s?",
    "-c:v","copy","-c:a","aac","-b:a","192k","-c:s","copy",
    "-metadata:s:a:0","language=kor","-metadata:s:a:0","title=한국어(선희)",
    "-metadata:s:a:1","language=eng","-metadata:s:a:1","title=English(Emma)",
    "-disposition:a:0","default", out],timeout=600)
print("AZURE DUB DONE:",out,f"{dur(out)/60:.2f}분")
