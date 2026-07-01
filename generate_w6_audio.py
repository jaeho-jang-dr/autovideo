#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_w6_audio.py — 6주차 "연음과 음운 변동" 표기형/발음형 단어 발음 클립(선희 edge-tts).
표기형(옷이)도 edge-tts가 자연 연음으로 [오시]로 읽어 발음형과 동일하게 들림 → 연음 학습 의도와 일치.
이미 있는 클립(음악·으막·우서요)은 건너뜀. 재실행: python generate_w6_audio.py
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

WORDS = ["음악", "으막", "옷이", "오시", "꽃이", "꼬치", "책을", "채글",
         "한국어", "한구거", "좋아요", "조아요", "웃어요", "우서요", "있어요", "이써요"]


def gen(text, key, mindur=0.6):
    tmp = os.path.join(ROOT, "scratch", "_w6_tmp.mp3")
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
    print(f"\n{len(WORDS)} W6 word clips generated + registered")


if __name__ == "__main__":
    main()
