# -*- coding: utf-8 -*-
"""W17 선희 음성 DB: KO-W17 스크립트(한/영)의 '…' 인용 한글 표현을 전부 선희로 생성해
   web/public/audio/jamo/ 에 저장 → hangeul_audio_assets 등록.
   ★DB script는 build_w17이 norm_quotes 처리 후 저장한 것 → 클립 파일명이 ensure_scene_audio 조회와 일치.
   ★기본 Azure 선희(라이선스). 6월자 남성위험 클립(반말·축약어·케이팝·케이드라마·요)도 FORCE로 여성 재생성.
사용: TTS_ENGINE=azure EDGE_ACTIVE_VOICE=sunhi python gen_w17_voicedb.py   (기본 azure)
"""
import os, re, sqlite3, subprocess, sys

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
os.environ["ELEVEN_API_KEY"] = ""                       # ElevenLabs 끄기(한글강의는 선희/Emma)
os.environ.setdefault("EDGE_ACTIVE_VOICE", "sunhi")
os.environ.setdefault("TTS_ENGINE", "azure")            # 기본 정식 라이선스 Azure 선희
if os.environ.get("TTS_ENGINE", "").lower() == "azure":  # .env 로드(키/리전)
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
sys.path.insert(0, ROOT)
from tts_manager import save_tts

JAMO = os.environ.get("JAMO_OUT_DIR") or os.path.join(ROOT, "web", "public", "audio", "jamo")
os.makedirs(JAMO, exist_ok=True)
TMP = os.path.join(ROOT, "scratch", "w17_voicedb_tmp"); os.makedirs(TMP, exist_ok=True)
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
for sk, se in cur.execute("SELECT script_kr, script_en FROM scenes WHERE episode='KO-W17'"):
    for txt in (sk or "", se or ""):
        for m in re.findall(r"'([^']+)'", txt):
            if KR.search(m):
                spans.add(m.strip())

spans = sorted(spans, key=len)
print(f"인용 한글 표현 {len(spans)}개 → 선희 DB 생성 (engine={os.environ.get('TTS_ENGINE')})", flush=True)
for s in spans:
    print("   ", repr(s), flush=True)

made = err = 0
FORCE = True    # 강제 재생성(6월 남성 클립 여성 덮어쓰기 포함)

for s in spans:
    out = os.path.join(JAMO, f"{s}.mp3")
    raw = os.path.join(TMP, f"{abs(hash(s)) % 10**9}.mp3")
    try:
        save_tts(s, raw, lang="ko")                        # Azure 선희(폴백 edge 선희)
        subprocess.run([FF, "-y", "-i", raw, "-filter:a", "atempo=1.1", "-vn", out],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        db_path = f"/audio/jamo/{s}.mp3"
        cur.execute("INSERT OR REPLACE INTO hangeul_audio_assets (text, filepath) VALUES (?, ?)", (s, db_path))
        made += 1
    except Exception as e:
        print(f"  ERR {s!r}: {str(e)[:60]}", flush=True); err += 1

con.commit()
con.close()
print(f"완료: 생성 {made}, 실패 {err}, 총 {len(spans)}", flush=True)
