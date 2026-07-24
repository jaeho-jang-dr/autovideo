# -*- coding: utf-8 -*-
"""W19 선희 음성 DB: KO-W19 스크립트(한/영)의 '…' 인용 한글 표현을 전부 선희로 생성해
   web/public/audio/jamo/ 에 저장 → hangeul_audio_assets 등록.
   ★DB script는 build_w19이 norm_quotes 처리 후 저장한 것 → 클립 파일명이 ensure_scene_audio 조회와 일치.
   ★초안(draft) = edge-tts 선희(무료, 크레딧 절약). 최종화 때는 TTS_ENGINE=azure 로 재생성.
사용: python gen_w19_voicedb.py            (기본 edge 선희)
      TTS_ENGINE=azure python gen_w19_voicedb.py   (최종 Azure 선희)
"""
import os, re, sqlite3, subprocess, sys

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
os.environ["ELEVEN_API_KEY"] = ""                       # ElevenLabs 끄기
os.environ.setdefault("EDGE_ACTIVE_VOICE", "sunhi")     # 선희
os.environ.setdefault("TTS_ENGINE", "edge")             # ★초안 기본 edge-tts
if os.environ.get("TTS_ENGINE", "").lower() == "azure":  # Azure면 .env 로드(키/리전)
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
sys.path.insert(0, ROOT)
from tts_manager import save_tts

JAMO = os.environ.get("JAMO_OUT_DIR") or os.path.join(ROOT, "web", "public", "audio", "jamo")
os.makedirs(JAMO, exist_ok=True)
TMP = os.path.join(ROOT, "scratch", "w19_voicedb_tmp"); os.makedirs(TMP, exist_ok=True)
KR = re.compile(r"[가-힣]")


def ff():
    for c in ["ffmpeg", r"C:\ffmpeg\bin\ffmpeg.exe"]:
        try:
            subprocess.run([c, "-version"], capture_output=True); return c
        except Exception:
            pass
    return "ffmpeg"
FF = ff()

con = sqlite3.connect(os.path.join(ROOT, "channel", "content.db")); cur = con.cursor()
spans = set()
for sk, se in cur.execute("SELECT script_kr, script_en FROM scenes WHERE episode='KO-W19'"):
    for txt in (sk or "", se or ""):
        for m in re.findall(r"'([^']+)'", txt):
            if KR.search(m):
                spans.add(m.strip())

spans = sorted(spans, key=len)
print(f"인용 한글 표현 {len(spans)}개 → 선희 DB 생성 (engine={os.environ.get('TTS_ENGINE')})", flush=True)
for s in spans:
    print("   ", repr(s), flush=True)

made = err = skip = 0
FORCE = os.environ.get("FORCE_TTS", "").strip() in ("1", "true", "yes")  # 기본 재사용(Azure 크레딧 절약)

for s in spans:
    out = os.path.join(JAMO, f"{s}.mp3")
    raw = os.path.join(TMP, f"{abs(hash(s)) % 10**9}.mp3")
    if os.path.exists(out) and not FORCE:
        cur.execute("INSERT OR REPLACE INTO hangeul_audio_assets (text, filepath) VALUES (?, ?)", (s, f"/audio/jamo/{s}.mp3"))
        skip += 1; continue
    try:
        save_tts(s, raw, lang="ko")                        # 선희(edge 또는 azure)
        subprocess.run([FF, "-y", "-i", raw, "-filter:a", "atempo=1.1", "-vn", out],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        db_path = f"/audio/jamo/{s}.mp3"
        cur.execute("INSERT OR REPLACE INTO hangeul_audio_assets (text, filepath) VALUES (?, ?)", (s, db_path))
        made += 1
    except Exception as e:
        print(f"  ERR {s!r}: {str(e)[:60]}", flush=True); err += 1

con.commit()
con.close()
print(f"완료: 생성 {made}, 재사용 {skip}, 실패 {err}, 총 {len(spans)}", flush=True)
