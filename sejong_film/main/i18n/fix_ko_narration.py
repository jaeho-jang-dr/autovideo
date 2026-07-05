# -*- coding: utf-8 -*-
"""KO 나레이션 문제 씬 수정 — 자모는 DB 성우클립, 텍스트는 Kanna(ElevenLabs), 사이 0.2초 간격.
연도는 한글로 풀어 정확 발음. 자막(narration.json)은 안 건드리고 오디오(audio_11/ko_S##.mp3)만 재조립.
사용: python fix_ko_narration.py"""
import os, json, subprocess, urllib.request, hashlib, re, tempfile, shutil
ROOT="D:/Entertainments/DevEnvironment/autovideo"
MAIN=os.path.join(ROOT,"sejong_film","main"); I18N=os.path.join(MAIN,"i18n")
AUD=os.path.join(MAIN,"audio_11"); JAMO_DIR=os.path.join(ROOT,"web","public","audio","jamo")
TMP=os.path.join(MAIN,"_ko_fix_tmp"); os.makedirs(TMP,exist_ok=True)
GAP=0.2  # 성우↔나레이터 간격(초)

key=None
for ln in open(os.path.join(ROOT,".env"),encoding="utf-8"):
    if ln.strip().startswith("ELEVEN_API_KEY="): key=ln.split("=",1)[1].strip()
def api_get(p): return json.load(urllib.request.urlopen(urllib.request.Request("https://api.elevenlabs.io/v1/"+p,headers={"xi-api-key":key}),timeout=40))
VID=next(v["voice_id"] for v in api_get("voices")["voices"] if "kanna" in v["name"].lower())

# 자모 집합(호환 자모 U+3131~3163 + ㆍ U+318D)
def is_jamo(ch): return ('ㄱ'<=ch<='ㅣ') or ch=='ㆍ'
def jamo_file(ch):
    name='아래아' if ch=='ㆍ' else ch
    p=os.path.join(JAMO_DIR,name+".mp3"); return p if os.path.exists(p) else None

# 연도 → 한글(오디오용). 자막은 그대로.
YEAR={'1443':'천사백사십삼','1446':'천사백사십육','1450':'천 사백오십','580':'오백팔십'}
def fix_years(t):
    for k,v in YEAR.items(): t=t.replace(k+'년', v+' 년')
    return t

def norm(src,dst):
    subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","128k",dst],timeout=60)

def silence(dst):
    subprocess.run(["ffmpeg","-y","-v","error","-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-t",str(GAP),"-c:a","libmp3lame","-b:a","128k",dst],timeout=30)

def tts_kanna(text,dst):
    body=json.dumps({"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.5,"similarity_boost":0.8,"style":0.0,"use_speaker_boost":True,"speed":1.1}}).encode()
    raw=os.path.join(TMP,"_raw.mp3")
    req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VID}?output_format=mp3_44100_128",data=body,method="POST",headers={"xi-api-key":key,"Content-Type":"application/json"})
    open(raw,"wb").write(urllib.request.urlopen(req,timeout=120).read()); norm(raw,dst)

def segment(text):
    """텍스트를 [('text',..)|('jamo',ch)] 로. 자모 주변 따옴표/쉼표만 있는 텍스트조각은 스킵."""
    text=text.replace('‘','').replace('’','').replace('“','').replace('”','')
    segs=[]; buf=''
    for ch in text:
        if is_jamo(ch):
            if re.search(r'[가-힣A-Za-z0-9]',buf): segs.append(('text',buf))
            buf=''; segs.append(('jamo',ch))
        else: buf+=ch
    if re.search(r'[가-힣A-Za-z0-9]',buf): segs.append(('text',buf))
    return segs

data={x['n']:x for x in json.load(open(os.path.join(I18N,'narration.json'),encoding='utf-8'))}
TARGETS=[27,37,38,39,40,41,45,49]
sil=os.path.join(TMP,"sil.mp3"); silence(sil)

def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True,timeout=20).stdout.strip())
    except: return 0.0

for n in TARGETS:
    ko=data[n]['ko']
    segs=segment(ko)
    parts=[]  # 정규화된 조각 경로들
    for i,(kind,val) in enumerate(segs):
        out=os.path.join(TMP,f"S{n:02d}_{i:02d}.mp3")
        if kind=='jamo':
            jf=jamo_file(val)
            if jf: norm(jf,out); parts.append(out)
            else: print(f"  [WARN] 자모 파일 없음: {val}")
        else:
            txt=fix_years(val).strip()
            if txt: tts_kanna(txt,out); parts.append(out)
    # 조각 사이 0.2초 간격 넣어 concat
    listf=os.path.join(TMP,f"list_{n}.txt")
    with open(listf,"w",encoding="utf-8") as f:
        for j,p in enumerate(parts):
            if j>0: f.write(f"file '{sil}'\n")
            f.write(f"file '{p}'\n")
    outp=os.path.join(AUD,f"ko_S{n:02d}.mp3")
    subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",listf,"-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","128k",outp],timeout=60)
    print(f"S{n:02d}: {len(segs)}조각(자모 {sum(1 for k,_ in segs if k=='jamo')}) -> {dur(outp):.1f}s")

shutil.rmtree(TMP,ignore_errors=True)
print("KO 수정 완료:",TARGETS)
