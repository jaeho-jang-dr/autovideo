#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_w3_audio.py — 3주차 "거센소리와 된소리" 발음 클립을 선희(edge-tts SunHi)로 생성.
 - 자음 '소리'를 글자(jamo) 파일명으로 저장: ㄱ.mp3=그, ㅋ.mp3=크, ㄲ.mp3=끄 …
   (compile_stickman 의 낱자 삽입 경로가 web/public/audio/jamo/<jamo>.mp3 를 찾아 끼워넣고,
    letter_<jamo> 글자와 맥동 동기화됨.)
 - 최소대립쌍 단어: 코 타조 포도 치마 까치 꼬리 땅 빵 개 캐 깨 자 차 짜 (자연 길이).
재실행: python generate_w3_audio.py
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

# 자음 글자 → 들려줄 '소리'(음절). 파일명은 글자(jamo)로 저장.
SOUND = {
    "ㄱ": "그", "ㄷ": "드", "ㅂ": "브", "ㅈ": "즈", "ㅅ": "스",        # 예사소리
    "ㅋ": "크", "ㅌ": "트", "ㅍ": "프", "ㅊ": "츠",                    # 거센소리
    "ㄲ": "끄", "ㄸ": "뜨", "ㅃ": "쁘", "ㅆ": "쓰", "ㅉ": "쯔",        # 된소리
}
# 최소대립쌍·예시 단어 (자연 길이)
WORDS = ["코", "타조", "포도", "치마", "까치", "꼬리", "땅", "빵",
         "개", "캐", "깨", "자", "차", "짜"]


def gen(text, key, stretch=None, mindur=0.7):
    tmp = os.path.join(ROOT, "scratch", "_w3_tmp.mp3")
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
    # 자음 소리: 살짝만 또렷하게(0.92), 단어: 자연 길이
    items = [(s, j, 0.92, 0.72) for j, s in SOUND.items()] + [(w, w, None, 0.55) for w in WORDS]
    for text, key, st, md in items:
        web = gen(text, key, stretch=st, mindur=md)
        cur.execute("DELETE FROM hangeul_audio_assets WHERE text=?", (key,))
        if has:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath, created_at) VALUES (?,?, datetime('now'))", (key, web))
        else:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath) VALUES (?,?)", (key, web))
        print(f"  {key} ('{text}') -> {web}")
    con.commit()
    con.close()
    print(f"\n{len(items)} W3 sound/word clips generated + registered")


if __name__ == "__main__":
    main()
