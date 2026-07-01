#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_w2_sounds.py — 2주차 교정: 자음 '소리'(그느므스응)와 단어(누나·오빠) 발음을
선희(edge-tts SunHi)로 길고 또렷하게 생성 → web/public/audio/jamo/ + content.db.

자음 소리는 atempo<1 로 늘려 또렷/길게(사용자 요청 "길게"). 단어는 자연 길이.
나레이션의 '그' '느' … '누나' '오빠' (따옴표 포함) 위치에 이 클립이 삽입된다.
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

# 자음 소리(길게): key=음절, stretch=atempo, mindur
SOUNDS = ["그", "느", "므", "스", "응"]   # 자음 소리 — 길게
WORDS = ["누나", "오빠"]                   # 단어 — 자연 길이


def gen(text, key, stretch=None, mindur=0.9):
    tmp = os.path.join(ROOT, "scratch", "_s_tmp.mp3")
    if not save_tts_edge_tts(text, tmp, lang="ko"):
        raise RuntimeError(f"tts failed {text}")
    mp3 = os.path.join(OUTDIR, f"{key}.mp3")
    af = f"apad=whole_dur={mindur}"
    if stretch:
        af = f"atempo={stretch}," + af
    subprocess.run([FF, "-y", "-i", tmp, "-af", af, mp3],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return f"/audio/jamo/{key}.mp3"


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    has = "created_at" in {r[1] for r in cur.execute("pragma table_info(hangeul_audio_assets)")}
    items = [(s, s, 0.7, 1.1) for s in SOUNDS] + [(w, w, None, 0.95) for w in WORDS]
    for text, key, st, md in items:
        web = gen(text, key, stretch=st, mindur=md)
        cur.execute("DELETE FROM hangeul_audio_assets WHERE text=?", (key,))
        if has:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath, created_at) VALUES (?,?, datetime('now'))", (key, web))
        else:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath) VALUES (?,?)", (key, web))
        print(f"  {key} ({'sound' if st else 'word'}) -> {web}")
    con.commit()
    con.close()
    print(f"\n{len(items)} sound/word clips generated + registered")


if __name__ == "__main__":
    main()
