#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_vowel_audio.py — 단모음 정확 발음을 **선희(edge-tts ko-KR-SunHiNeural, 내레이션과 동일
여성 목소리)**로 생성하고 content.db(hangeul_audio_assets)에 등록.

핵심:
 - 낱자 'ㅏ' 가 아니라 ㅇ을 붙인 **음절형**(아 어 오 우 으 이 애 에)으로 합성해야 모음 소릿값이 정확.
 - 각 클립 길이 ~0.5초 (짧고 또렷하게). 순서: ㅏ ㅓ ㅗ ㅜ ㅡ ㅣ ㅐ ㅔ.
 - 파일은 web/public/audio/jamo/<글자>.mp3 에 덮어쓰고, DB는 text=낱자, filepath=/audio/jamo/<글자>.mp3.

실행: python generate_vowel_audio.py
"""
import os
import sys
import sqlite3
import subprocess

import imageio_ffmpeg

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from tts_manager import save_tts_edge_tts

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = os.path.join(ROOT, "channel", "content.db")
OUTDIR = os.path.join(ROOT, "web", "public", "audio", "jamo")
FF = imageio_ffmpeg.get_ffmpeg_exe()
SLOT = 0.5   # 각 모음 길이(초)

# 발음 순서 + 낱자->음절형(정확 소릿값)
ORDER = ["ㅏ", "ㅓ", "ㅗ", "ㅜ", "ㅡ", "ㅣ", "ㅐ", "ㅔ"]
SYL = {"ㅏ": "아", "ㅓ": "어", "ㅗ": "오", "ㅜ": "우", "ㅡ": "으", "ㅣ": "이", "ㅐ": "애", "ㅔ": "에"}


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    has_created = "created_at" in {r[1] for r in cur.execute("pragma table_info(hangeul_audio_assets)")}
    tmp = os.path.join(ROOT, "scratch", "_v_tmp.mp3")

    for jamo in ORDER:
        ok = save_tts_edge_tts(SYL[jamo], tmp, lang="ko")     # 선희 여성 목소리
        if not ok:
            raise RuntimeError(f"edge-tts(SunHi) failed for {jamo}")
        mp3 = os.path.join(OUTDIR, f"{jamo}.mp3")
        # ~0.5초 슬롯: 0.5초보다 짧으면 무음 패딩, 길면 0.55초로 컷
        subprocess.run([FF, "-y", "-i", tmp, "-af", f"apad=whole_dur={SLOT}", "-t", str(SLOT + 0.05), mp3],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        web = f"/audio/jamo/{jamo}.mp3"
        cur.execute("DELETE FROM hangeul_audio_assets WHERE text=?", (jamo,))
        if has_created:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath, created_at) VALUES (?,?, datetime('now'))",
                        (jamo, web))
        else:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath) VALUES (?,?)", (jamo, web))
        print(f"  {jamo} -> '{SYL[jamo]}' (SunHi)  {web}")
    con.commit()
    con.close()
    print(f"\n{len(ORDER)} vowel clips (edge-tts SunHi, ~{SLOT}s) regenerated + registered")

    # 미리듣기 concat: ㅏ ㅓ ㅗ ㅜ ㅡ ㅣ ㅐ ㅔ
    sil = os.path.join(ROOT, "scratch", "_sil.mp3")
    subprocess.run([FF, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.12", sil],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    listf = os.path.join(ROOT, "scratch", "_vowel_concat.txt")
    with open(listf, "w", encoding="utf-8") as f:
        for j in ORDER:
            f.write(f"file '{os.path.join(OUTDIR, j + '.mp3')}'\n")
            f.write(f"file '{sil}'\n")
    preview = os.path.join(ROOT, "scratch", "_vowel_preview.mp3")
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", listf, "-c:a", "libmp3lame", preview],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("preview ->", preview)


if __name__ == "__main__":
    main()
