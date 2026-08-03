# -*- coding: utf-8 -*-
"""W24 나레이션 음성 사전 생성 — ★Azure 선희(SunHi) (2026-08-03).

사장님 지시: "데이터베이스 성우는 선희로 미리 다 음성을 다 만들어 놓고."

  · 34씬 한국어 나레이션 → `assets/audio/w24/ko_S<n>.mp3`
  · 34씬 영어 나레이션   → `assets/audio/w24/en_S<n>.mp3` (Emma)
  · 화면 글자(글리프) 발음 클립 → `assets/audio/w24/word_<글자>.mp3` (★영어판도 선희)

★캐시 함정: 이미 있는 파일은 건너뛴다. 대본이 바뀌면 `--force` 로 다시 만든다.
★엔진 확인: 로그에 `[Azure]` 가 찍혀야 진짜 Azure 다. 0건이면 캐시만 쓴 것이다.

사용:
  python build_w24_voice.py            # 없는 것만
  python build_w24_voice.py --force    # 전부 다시
  python build_w24_voice.py --ko-only
"""
import argparse
import json
import os
import re
import sqlite3
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

# .env 로드 (AZURE_SPEECH_KEY / REGION)
if os.path.exists(".env"):
    for ln in open(".env", encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
os.environ.setdefault("EDGE_ACTIVE_VOICE", "sunhi")     # ★선희 고정

DB = "channel/content.db"
EP = "KO-W24"
OUT = "assets/audio/w24"


def log(m):
    print(m, flush=True)


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def synth(text, out, lang, force):
    """Azure 우선, 실패하면 edge-tts(같은 선희 음성)로 떨어진다.
    ★edge-tts 는 **검수용 초안**이다. 유튜브 게시본은 Azure 로 다시 뽑아야 한다."""
    import tts_manager as T
    if os.path.exists(out) and not force and os.path.getsize(out) > 2000:
        return "cache"
    if not os.environ.get("W24_EDGE_ONLY"):
        try:
            if T.save_tts_azure(text, out, lang):
                return "Azure"
        except Exception:
            os.environ["W24_EDGE_ONLY"] = "1"      # 한 번 실패하면 이후는 바로 edge
    import asyncio, edge_tts
    voice = "ko-KR-SunHiNeural" if lang.startswith("ko") else "en-US-EmmaNeural"
    try:
        asyncio.run(edge_tts.Communicate(text, voice).save(out))
        return "edge" if os.path.exists(out) and os.path.getsize(out) > 2000 else "FAIL"
    except Exception as e:
        print(f"   ★edge 실패: {str(e)[:60]}")
        return "FAIL"


def main(a):
    os.makedirs(OUT, exist_ok=True)
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT seq,script_kr,script_en,image_prompt FROM scenes "
                       "WHERE episode=? ORDER BY seq", (EP,)).fetchall()
    con.close()
    if not rows:
        log(f"★{EP} 씬이 DB에 없다 — build_w24.py 먼저 돌린다")
        return 1
    log(f"{EP} {len(rows)}씬 · 음성 = Azure 선희(ko) / Emma(en)")

    stat = {"Azure": 0, "edge": 0, "cache": 0, "FAIL": 0}
    words = set()
    total_ko = total_en = 0.0

    for seq, ko, en, spec in rows:
        p = f"{OUT}/ko_S{seq:02d}.mp3"
        r = synth(ko, p, "ko", a.force)
        stat[r] += 1
        total_ko += dur(p) if os.path.exists(p) else 0
        mark = "☆" if r == "Azure" else " "
        log(f"  S{seq:02d} ko [{r:5s}]{mark} {dur(p):5.1f}s  {ko[:34]}")

        if not a.ko_only and en:
            pe = f"{OUT}/en_S{seq:02d}.mp3"
            re_ = synth(en, pe, "en", a.force)
            stat[re_] += 1
            total_en += dur(pe) if os.path.exists(pe) else 0

        # 화면 글자(글리프) → 발음 클립. ★영어판에서도 선희로 읽는다(한글 발음 원칙)
        try:
            g = json.loads(spec or "{}").get("glyph", "")
        except json.JSONDecodeError:
            g = ""
        for w in re.split(r"[·,/]", g):
            w = w.strip().strip("`")
            if w and re.search(r"[가-힣ㄱ-ㅎㅏ-ㅣ]", w) and len(w) <= 14:
                words.add(w)

    log(f"\n화면 글자 발음 클립 {len(words)}개 (★영어판도 선희)")
    for w in sorted(words):
        safe = re.sub(r"[^0-9A-Za-z가-힣ㄱ-ㅎㅏ-ㅣ]", "_", w)
        p = f"{OUT}/word_{safe}.mp3"
        r = synth(w, p, "ko", a.force)
        stat[r] += 1
        if r == "Azure":
            log(f"  {w:14s} [Azure] {dur(p):4.1f}s")

    log(f"\n생성 {stat['Azure']} · 캐시 {stat['cache']} · 실패 {stat['FAIL']}")
    log(f"KO 합계 {total_ko/60:.1f}분 · EN 합계 {total_en/60:.1f}분")
    if stat["Azure"] == 0 and not a.force:
        log("※새로 만든 게 없다 — 전부 캐시다. 대본이 바뀌었으면 --force 로 다시 돌린다")
    log(f"✅ {OUT}/")
    return 1 if stat["FAIL"] else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--ko-only", action="store_true")
    raise SystemExit(main(ap.parse_args()))
