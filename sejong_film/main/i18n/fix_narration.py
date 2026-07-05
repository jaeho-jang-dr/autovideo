# -*- coding: utf-8 -*-
"""나레이션 문제 씬 수정(범용) — 자모는 DB 한국어 성우클립, 텍스트는 원어민, 사이 0.2초.
ZH/JA는 연도 숫자를 한자로 풀어 정확 발음. 자막(narration.json)은 안 건드리고 audio_11/{lang}_S##.mp3만 재조립.
사용: python fix_narration.py <lang>   (en/zh/ja/es; ko는 fix_ko_narration.py로 이미 처리)"""
import os, json, subprocess, urllib.request, re, shutil, sys
LANG=sys.argv[1]
ROOT="D:/Entertainments/DevEnvironment/autovideo"
MAIN=os.path.join(ROOT,"sejong_film","main"); I18N=os.path.join(MAIN,"i18n")
AUD=os.path.join(MAIN,"audio_11"); JAMO_DIR=os.path.join(ROOT,"web","public","audio","jamo")
TMP=os.path.join(MAIN,f"_fix_tmp_{LANG}"); os.makedirs(TMP,exist_ok=True)
GAP=0.2
MODEL="eleven_multilingual_v2"
VOICE_NAME={"en":"Alice","zh":"X_zh_Jackie","ja":"X_ja_Kinako","es":"X_es_Valentina"}
SPEED={"en":1.05,"zh":1.1,"ja":1.1,"es":1.05}
YEAR_SPELL={
 "zh":{'1443':'一千四百四十三','1446':'一千四百四十六','1450':'一千四百五十','580':'五百八十'},
 "ja":{'1443':'千四百四十三','1446':'千四百四十六','1450':'千四百五十','580':'五百八十'},
 "en":{}, "es":{},
}[LANG]

key=None
for ln in open(os.path.join(ROOT,".env"),encoding="utf-8"):
    if ln.strip().startswith("ELEVEN_API_KEY="): key=ln.split("=",1)[1].strip()
def api_get(p): return json.load(urllib.request.urlopen(urllib.request.Request("https://api.elevenlabs.io/v1/"+p,headers={"xi-api-key":key}),timeout=40))
VID=next(v["voice_id"] for v in api_get("voices")["voices"] if VOICE_NAME[LANG].lower() in v["name"].lower())
print(f"{LANG} 보이스 {VOICE_NAME[LANG]} -> {VID[:8]}…")

def is_jamo(ch): return ('ㄱ'<=ch<='ㅣ') or ch=='ㆍ'
def jamo_file(ch):
    name='아래아' if ch=='ㆍ' else ch
    p=os.path.join(JAMO_DIR,name+".mp3"); return p if os.path.exists(p) else None
def fix_years(t):
    for k,v in YEAR_SPELL.items(): t=t.replace(k,v)
    return t
def norm(src,dst):
    subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","128k",dst],timeout=60)
def silence(dst):
    subprocess.run(["ffmpeg","-y","-v","error","-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-t",str(GAP),"-c:a","libmp3lame","-b:a","128k",dst],timeout=30)
def tts(text,dst):
    body=json.dumps({"text":text,"model_id":MODEL,"voice_settings":{"stability":0.5,"similarity_boost":0.8,"style":0.0,"use_speaker_boost":True,"speed":SPEED[LANG]}}).encode()
    raw=os.path.join(TMP,"_raw.mp3")
    req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VID}?output_format=mp3_44100_128",data=body,method="POST",headers={"xi-api-key":key,"Content-Type":"application/json"})
    open(raw,"wb").write(urllib.request.urlopen(req,timeout=120).read()); norm(raw,dst)
def segment(text):
    text=text.replace('‘','').replace('’','').replace('“','').replace('”','')
    segs=[]; buf=''
    for ch in text:
        if is_jamo(ch):
            if re.search(r'[가-힣A-Za-z0-9一-鿿぀-ヿ]',buf): segs.append(('text',buf))
            buf=''; segs.append(('jamo',ch))
        else: buf+=ch
    if re.search(r'[가-힣A-Za-z0-9一-鿿぀-ヿ]',buf): segs.append(('text',buf))
    return segs
def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True,timeout=20).stdout.strip())
    except: return 0.0

data={x['n']:x for x in json.load(open(os.path.join(I18N,'narration.json'),encoding='utf-8'))}
CAND=[27,37,38,39,40,41,45,49]
sil=os.path.join(TMP,"sil.mp3"); silence(sil)
done=[]
for n in CAND:
    txt0=data[n][LANG]
    has_jamo=any(is_jamo(c) for c in txt0)
    has_year=any(k in txt0 for k in YEAR_SPELL)
    if not (has_jamo or has_year): continue   # 이 언어에서 문제없는 씬은 기존 오디오 유지
    segs=segment(txt0); parts=[]
    for i,(kind,val) in enumerate(segs):
        out=os.path.join(TMP,f"S{n:02d}_{i:02d}.mp3")
        if kind=='jamo':
            jf=jamo_file(val)
            if jf: norm(jf,out); parts.append(out)
            else: print(f"  [WARN] 자모 파일 없음: {val}")
        else:
            t=fix_years(val).strip()
            if t: tts(t,out); parts.append(out)
    listf=os.path.join(TMP,f"list_{n}.txt")
    with open(listf,"w",encoding="utf-8") as f:
        for j,p in enumerate(parts):
            if j>0: f.write(f"file '{sil}'\n")
            f.write(f"file '{p}'\n")
    outp=os.path.join(AUD,f"{LANG}_S{n:02d}.mp3")
    subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",listf,"-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","128k",outp],timeout=60)
    print(f"{LANG}_S{n:02d}: 자모{sum(1 for k,_ in segs if k=='jamo')} 연도{'O' if has_year else '-'} -> {dur(outp):.1f}s"); done.append(n)
shutil.rmtree(TMP,ignore_errors=True)
print(f"{LANG} 수정 완료:",done)
