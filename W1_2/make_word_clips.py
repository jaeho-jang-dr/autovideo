# -*- coding: utf-8 -*-
"""W1-2 새 낱말의 **선희 발음 클립**을 만들어 DB 에 등록한다.

★사장님 지시(2026-08-17)
  "아이 이 오이 우유만 가지고 계속 말하니 너무 반복만 하고 있다. 모음만으로
   만들어진 단어들 많이 있으니 더 추가해서 설명해 보자 — 이유, 야유, 위."

## 왜 클립이 따로 있어야 하나
자막 속 한글은 **선희 DB 클립**이 읽는다([[feedback-korean-pronunciation-principle]]).
클립이 없으면 영어 성우(Emma)가 한글을 읽어 발음 교육이 무너진다. 새 낱말을
대본에 넣기 전에 클립부터 만들어야 하는 이유다.

## 이미 있는 클립과 같은 규격
기존 낱말 클립을 재 보니 **183~202Hz · 0.41~0.54초** 였다. 같은 엔진(edge-tts
SunHi)으로 만들고 길이도 같은 대역인지 확인한다 — 한 영상 안에서 목소리가
바뀌면 그게 더 눈에 띈다.

  python W1_2/make_word_clips.py
"""
import os
import sqlite3
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from tts_manager import save_tts_edge_tts                  # noqa: E402

DB = os.path.join(ROOT, "channel", "content.db")
OUT = os.path.join(ROOT, "web", "public", "audio", "jamo")
WORDS = ["위", "이유", "우와", "야유", "아야", "여유", "유아"]


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def main():
    os.makedirs(OUT, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cols = {r[1] for r in cur.execute("pragma table_info(hangeul_audio_assets)")}
    tmp = os.path.join(ROOT, "scratch", "_w12_word.mp3")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)

    for w in WORDS:
        mp3 = os.path.join(OUT, w + ".mp3")
        if os.path.exists(mp3):
            print("  %-4s 이미 있음 (%.2f초)" % (w, dur(mp3)))
            continue
        if not save_tts_edge_tts(w, tmp, lang="ko"):        # 선희 여성 목소리
            raise RuntimeError("edge-tts(SunHi) 실패: %s" % w)
        # 앞뒤 무음을 떼어 기존 낱말 클립과 같은 길이 대역으로 맞춘다
        trim = ("silenceremove=start_periods=1:start_silence=0.03:"
                "start_threshold=-45dB:detection=peak,areverse,"
                "silenceremove=start_periods=1:start_silence=0.03:"
                "start_threshold=-45dB:detection=peak,areverse")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", trim,
                        "-c:a", "libmp3lame", "-b:a", "160k", mp3], check=True)
        web = "/audio/jamo/%s.mp3" % w
        cur.execute("DELETE FROM hangeul_audio_assets WHERE text=?", (w,))
        if "created_at" in cols:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath, created_at) "
                        "VALUES (?,?, datetime('now'))", (w, web))
        else:
            cur.execute("INSERT INTO hangeul_audio_assets (text, filepath) VALUES (?,?)",
                        (w, web))
        print("  %-4s 만듦 %.2f초  →  %s" % (w, dur(mp3), web))
    con.commit()
    con.close()


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
