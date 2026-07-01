# -*- coding: utf-8 -*-
"""ElevenLabs 5개 언어 나레이션 — narration.json → audio_11/{lang}_S##.mp3.
목소리: KO=Kanna, EN=Alice, ZH=Jackie, JA=Kinako, ES=Valentina. 캐시(존재 시 스킵).
사용: python make_narration_11.py <lang>  (ko/en/zh/ja/es) [--force]"""
import os, json, subprocess, urllib.request, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
MAIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
I18N = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(MAIN, "audio_11")
os.makedirs(OUT, exist_ok=True)
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
FORCE = "--force" in sys.argv
MODEL = "eleven_multilingual_v2"
VOICE_NAME = {"ko":"Kanna","en":"Alice","zh":"X_zh_Jackie","ja":"X_ja_Kinako","es":"X_es_Valentina"}
SPEED = {"ko":1.1,"en":1.05,"zh":1.1,"ja":1.1,"es":1.05}

key=None
for ln in open(os.path.join(MAIN,"..","..",".env"),encoding="utf-8"):
    if ln.strip().startswith("ELEVEN_API_KEY="): key=ln.split("=",1)[1].strip()

def api_get(path):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.elevenlabs.io/v1/"+path,headers={"xi-api-key":key}),timeout=40))
vs=api_get("voices")["voices"]
def find(sub): return next((v["voice_id"] for v in vs if sub.lower() in v["name"].lower()),None)
VID=find(VOICE_NAME[LANG])
print(f"{LANG} 목소리 '{VOICE_NAME[LANG]}' -> {'OK' if VID else 'NOT FOUND'}")
if not VID: sys.exit("목소리 못 찾음")

def tts(text,out):
    body=json.dumps({"text":text,"model_id":MODEL,"voice_settings":{"stability":0.5,"similarity_boost":0.8,"style":0.0,"use_speaker_boost":True,"speed":SPEED[LANG]}}).encode()
    req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VID}?output_format=mp3_44100_128",data=body,method="POST",headers={"xi-api-key":key,"Content-Type":"application/json"})
    open(out,"wb").write(urllib.request.urlopen(req,timeout=120).read())
def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True,timeout=20).stdout.strip())
    except Exception: return 0.0
def clean(t): return t.replace("“","").replace("”","").replace("‘","'").replace("’","'")

data=json.load(open(os.path.join(I18N,"narration.json"),encoding="utf-8"))
tot=0.0; made=0
for d in data:
    if d["music"] or not d.get(LANG): continue
    out=os.path.join(OUT,f"{LANG}_S{d['n']:02d}.mp3")
    if (not FORCE) and os.path.exists(out) and os.path.getsize(out)>1000:
        tot+=dur(out); continue
    try:
        tts(clean(d[LANG]),out); dd=dur(out); tot+=dd; made+=1; print(f"[OK] {LANG}_S{d['n']:02d} {dd:4.1f}s")
    except Exception as e:
        print(f"[ERR] {LANG}_S{d['n']:02d}: {str(e)[:90]}")
print(f"== {LANG} 신규 {made}개, 총 {tot:.1f}s ({tot/60:.1f}분) ==")
