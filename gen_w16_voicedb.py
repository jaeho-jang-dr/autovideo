# -*- coding: utf-8 -*-
"""W16 선희 음성 DB: KO-W16 스크립트(한/영)의 '…' 인용 한글 표현을 전부 선희(edge-tts ko)로 생성해
   web/public/audio/jamo/ 에 저장 → hangeul_audio_assets 등록."""
import os, re, sqlite3, subprocess, sys

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
TMP = os.path.join(ROOT, "scratch", "w16_voicedb_tmp"); os.makedirs(TMP, exist_ok=True)
KR = re.compile(r"[가-힣]")

def ff():
    for c in ["ffmpeg", r"C:\ffmpeg\bin\ffmpeg.exe"]:
        try: subprocess.run([c,"-version"],capture_output=True); return c
        except: pass
    return "ffmpeg"
FF = ff()

con = sqlite3.connect(os.path.join(ROOT,"channel","content.db")); cur = con.cursor()
spans = set()
for sk, se in cur.execute("SELECT script_kr, script_en FROM scenes WHERE episode='KO-W16'"):
    for txt in (sk or "", se or ""):
        for m in re.findall(r"'([^']+)'", txt):
            if KR.search(m): spans.add(m.strip())

spans = sorted(spans, key=len)
print(f"인용 한글 표현 {len(spans)}개 → 선희 DB 생성", flush=True)

made = skip = 0
FORCE = True    # 강제 재생성

for s in spans:
    out = os.path.join(JAMO, f"{s}.mp3")
    if not FORCE and os.path.exists(out) and os.path.getsize(out) > 800:
        skip += 1; continue
    raw = os.path.join(TMP, f"{abs(hash(s))%10**9}.mp3")
    try:
        save_tts(s, raw, lang="ko")                       # edge-tts 선희
        # 1.1배속 굽기
        subprocess.run([FF,"-y","-i",raw,"-filter:a","atempo=1.1","-vn",out],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        # DB 등록
        db_path = f"/audio/jamo/{s}.mp3"
        cur.execute("INSERT OR REPLACE INTO hangeul_audio_assets (text, filepath) VALUES (?, ?)", (s, db_path))
        made += 1
    except Exception as e:
        print(f"  ERR {s}: {str(e)[:40]}", flush=True)

con.commit()
con.close()
print(f"완료: 신규 {made}, 기존 {skip}, 총 {len(spans)}", flush=True)
