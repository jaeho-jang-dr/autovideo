#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_consonant_audio.py — 자음 19개(이름)를 선희(edge-tts SunHi) 목소리로 생성하고
content.db(hangeul_audio_assets)에 등록.

자음은 '이름'으로 읽는다: ㄱ=기역, ㄴ=니은, ㄷ=디귿 … ㄲ=쌍기역 …
기본 14 + 된소리(쌍자음) 5 = 19. 파일: web/public/audio/jamo/<글자>.mp3, DB: text=낱자.

실행: python generate_consonant_audio.py
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
MINDUR = 0.7   # 짧은 이름은 0.7초로 패딩 (이름이 길면 그대로)

# 낱자 -> 이름 (읽는 순서: 기본 14 + 된소리 5)
CONS = [
    ("ㄱ", "기역"), ("ㄴ", "니은"), ("ㄷ", "디귿"), ("ㄹ", "리을"), ("ㅁ", "미음"),
    ("ㅂ", "비읍"), ("ㅅ", "시옷"), ("ㅇ", "이응"), ("ㅈ", "지읒"), ("ㅊ", "치읓"),
    ("ㅋ", "키읔"), ("ㅌ", "티읕"), ("ㅍ", "피읖"), ("ㅎ", "히읗"),
    ("ㄲ", "쌍기역"), ("ㄸ", "쌍디귿"), ("ㅃ", "쌍비읍"), ("ㅆ", "쌍시옷"), ("ㅉ", "쌍지읒"),
]


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    has_created = "created_at" in {r[1] for r in cur.execute("pragma table_info(hangeul_audio_assets)")}
    tmp = os.path.join(ROOT, "scratch", "_c_tmp.mp3")

    for jamo, name in CONS:
        ok = save_tts_edge_tts(name, tmp, lang="ko")        # 선희 여성 목소리
        if not ok:
            raise RuntimeError(f"edge-tts(SunHi) failed for {jamo} ({name})")
        mp3 = os.path.join(OUTDIR, f"{jamo}.mp3")
        subprocess.run([FF, "-y", "-i", tmp, "-af", f"apad=whole_dur={MINDUR}", mp3],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        web = f"/audio/jamo/{jamo}.mp3"
        cur.execute("DELETE FROM hangeul_audio_assets WHERE text=?", (jamo,))
        if has_created:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath, created_at) VALUES (?,?, datetime('now'))",
                        (jamo, web))
        else:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath) VALUES (?,?)", (jamo, web))
        print(f"  {jamo} -> '{name}' (SunHi)  {web}")
    con.commit()
    con.close()
    print(f"\n{len(CONS)} consonant clips (edge-tts SunHi) regenerated + registered")

    # 미리듣기 concat
    sil = os.path.join(ROOT, "scratch", "_csil.mp3")
    subprocess.run([FF, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.18", sil],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    listf = os.path.join(ROOT, "scratch", "_cons_concat.txt")
    with open(listf, "w", encoding="utf-8") as f:
        for jamo, _ in CONS:
            f.write(f"file '{os.path.join(OUTDIR, jamo + '.mp3')}'\n")
            f.write(f"file '{sil}'\n")
    preview = os.path.join(ROOT, "scratch", "_cons_preview.mp3")
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", listf, "-c:a", "libmp3lame", preview],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("preview ->", preview)


if __name__ == "__main__":
    main()
