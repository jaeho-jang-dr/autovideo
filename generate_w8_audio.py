#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""generate_w8_audio.py — 8주차 요일/분 발음 클립(선희 edge-tts). 숫자 클립은 이미 존재.
재실행: python generate_w8_audio.py
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

WORDS = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일", "분"]


def gen(text, key, mindur=0.55):
    tmp = os.path.join(ROOT, "scratch", "_w8_tmp.mp3")
    if not save_tts_edge_tts(text, tmp, lang="ko"):
        raise RuntimeError(f"tts failed {text}")
    mp3 = os.path.join(OUTDIR, f"{key}.mp3")
    subprocess.run([FF, "-y", "-i", tmp, "-af", f"apad=whole_dur={mindur}", mp3],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return f"/audio/jamo/{key}.mp3"


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    has = "created_at" in {r[1] for r in cur.execute("pragma table_info(hangeul_audio_assets)")}
    for w in WORDS:
        web = gen(w, w)
        cur.execute("DELETE FROM hangeul_audio_assets WHERE text=?", (w,))
        if has:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath, created_at) VALUES (?,?, datetime('now'))", (w, web))
        else:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath) VALUES (?,?)", (w, web))
        print(f"  {w} -> {web}")
    con.commit()
    con.close()
    print(f"\n{len(WORDS)} W8 clips generated + registered")


if __name__ == "__main__":
    main()
