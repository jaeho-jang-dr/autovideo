# -*- coding: utf-8 -*-
"""W11 선희 음성 DB: KO-W11 스크립트(한/영)의 '…' 인용 한글 표현을 전부 선희(edge-tts ko)로 생성해
   web/public/audio/jamo/ 에 저장 → CLIP_QUOTED 자동등록 → EN 나레이션 때 강조(1.4배) 한글 읽기 클립으로 사용."""
import os, re, sqlite3, subprocess, sys, time
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
os.environ["ELEVEN_API_KEY"] = ""          # ElevenLabs 끄기(한글강의는 선희/Emma)
os.environ.setdefault("EDGE_ACTIVE_VOICE", "sunhi")
if os.environ.get("TTS_ENGINE","").lower() == "azure":   # 정식(라이선스): Azure 선희 → .env 로드
    for line in open(os.path.join(ROOT,".env"), encoding="utf-8"):
        line=line.strip()
        if line and not line.startswith("#") and "=" in line:
            k,v=line.split("=",1); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
sys.path.insert(0, ROOT)
from tts_manager import save_tts
JAMO = os.environ.get("JAMO_OUT_DIR") or os.path.join(ROOT, "web", "public", "audio", "jamo")
os.makedirs(JAMO, exist_ok=True)
TMP = os.path.join(ROOT, "scratch", "w11_voicedb_tmp"); os.makedirs(TMP, exist_ok=True)
KR = re.compile(r"[가-힣]")
def ff():
    for c in ["ffmpeg", r"C:\ffmpeg\bin\ffmpeg.exe"]:
        try: subprocess.run([c,"-version"],capture_output=True); return c
        except: pass
    return "ffmpeg"
FF = ff()
con = sqlite3.connect(os.path.join(ROOT,"channel","content.db")); cur = con.cursor()
spans = set()
for sk, se in cur.execute("SELECT script_kr, script_en FROM scenes WHERE episode='KO-W11'"):
    for txt in (sk or "", se or ""):
        for m in re.findall(r"'([^']+)'", txt):
            if KR.search(m): spans.add(m.strip())
con.close()
spans = sorted(spans, key=len)
print(f"인용 한글 표현 {len(spans)}개 → 선희 DB 생성", flush=True)
made = skip = 0
FORCE = True    # ★모든 '  ' 표현을 선희(여성)로 강제 재생성 — 기존에 남성으로 섞인 '맛' 등 일소(사장님 지시)
for s in spans:
    out = os.path.join(JAMO, f"{s}.mp3")
    if not FORCE and os.path.exists(out) and os.path.getsize(out) > 800:
        skip += 1; continue
    raw = os.path.join(TMP, f"{abs(hash(s))%10**9}.mp3")
    try:
        save_tts(s, raw, lang="ko")                       # edge-tts 선희 → gTTS 폴백
        subprocess.run([FF,"-y","-i",raw,"-filter:a","atempo=1.1","-vn",out],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)   # 나레이션과 동일 1.1배속
        made += 1
    except Exception as e:
        print(f"  ERR {s}: {str(e)[:40]}", flush=True)
print(f"완료: 신규 {made}, 기존 {skip}, 총 {len(spans)}", flush=True)
