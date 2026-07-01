#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_vowel_rest_audio.py — 나머지 모음 13개(이중·복합모음)를 선희(edge-tts SunHi)로 생성하고
content.db(hangeul_audio_assets)에 등록.

단모음 8개(ㅏㅓㅗㅜㅡㅣㅐㅔ)는 이미 등록됨. 여기서는 나머지 13개:
ㅑㅒㅕㅖㅛ ㅘㅙㅚㅝㅞㅟ ㅠㅢ → 음절형(야 얘 여 예 요 와 왜 외 워 웨 위 유 의), ~0.5초.

실행: python generate_vowel_rest_audio.py
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
SLOT = 0.5

# 낱자 -> 음절형 (가나다 순 중 단모음 8개 제외한 13개)
REST = [
    ("ㅑ", "야"), ("ㅒ", "얘"), ("ㅕ", "여"), ("ㅖ", "예"), ("ㅛ", "요"),
    ("ㅘ", "와"), ("ㅙ", "왜"), ("ㅚ", "외"), ("ㅝ", "워"), ("ㅞ", "웨"),
    ("ㅟ", "위"), ("ㅠ", "유"), ("ㅢ", "의"),
]


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    has_created = "created_at" in {r[1] for r in cur.execute("pragma table_info(hangeul_audio_assets)")}
    tmp = os.path.join(ROOT, "scratch", "_vr_tmp.mp3")

    for jamo, syl in REST:
        ok = save_tts_edge_tts(syl, tmp, lang="ko")          # 선희 여성 목소리
        if not ok:
            raise RuntimeError(f"edge-tts(SunHi) failed for {jamo} ({syl})")
        mp3 = os.path.join(OUTDIR, f"{jamo}.mp3")
        subprocess.run([FF, "-y", "-i", tmp, "-af", f"apad=whole_dur={SLOT}", "-t", str(SLOT + 0.05), mp3],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        web = f"/audio/jamo/{jamo}.mp3"
        cur.execute("DELETE FROM hangeul_audio_assets WHERE text=?", (jamo,))
        if has_created:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath, created_at) VALUES (?,?, datetime('now'))",
                        (jamo, web))
        else:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath) VALUES (?,?)", (jamo, web))
        print(f"  {jamo} -> '{syl}' (SunHi)  {web}")
    con.commit()

    total_v = cur.execute(
        "SELECT count(*) FROM hangeul_audio_assets WHERE text IN "
        "('ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ')"
    ).fetchone()[0]
    con.close()
    print(f"\n{len(REST)} more vowels registered. Total vowels in DB now: {total_v}/21")

    # 미리듣기 concat (13개)
    sil = os.path.join(ROOT, "scratch", "_vrsil.mp3")
    subprocess.run([FF, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.12", sil],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    listf = os.path.join(ROOT, "scratch", "_vrest_concat.txt")
    with open(listf, "w", encoding="utf-8") as f:
        for jamo, _ in REST:
            f.write(f"file '{os.path.join(OUTDIR, jamo + '.mp3')}'\n")
            f.write(f"file '{sil}'\n")
    preview = os.path.join(ROOT, "scratch", "_vrest_preview.mp3")
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", listf, "-c:a", "libmp3lame", preview],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("preview ->", preview)


if __name__ == "__main__":
    main()
