# -*- coding: utf-8 -*-
"""W1-3 대본의 인용어(' ') 중 DB에 없는 발음 클립을 Azure TTS 선희 음성으로 미리 생성해
web/public/audio/jamo/에 저장하고 hangeul_audio_assets에 등록한다.
사장님 지시(2026-09-01): "자막 한글 나레이션은 선희가 읽고 데이타베이스에 들어갈 말들은
' ' 안에 넣어서 미리 azure tts 선희로 데이타 베이스에 다 넣는다."
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("EDGE_ACTIVE_VOICE", "sunhi")
from tts_manager import save_tts_azure

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JAMO_DIR = os.path.join(ROOT, "web", "public", "audio", "jamo")
DB = os.path.join(ROOT, "channel", "content.db")

WORDS = ["까닭", "느긋함", "방", "아", "으차", "음절 상자", "우애"]


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    made = []
    for w in WORDS:
        out = os.path.join(JAMO_DIR, f"{w}.mp3")
        cur.execute("SELECT 1 FROM hangeul_audio_assets WHERE text=?", (w,))
        if cur.fetchone():
            print(f"[skip] '{w}' 이미 DB에 있음")
            continue
        print(f"[gen] '{w}' -> {out}")
        save_tts_azure(w, out, lang="ko")
        rel = "/audio/jamo/%s.mp3" % w
        cur.execute(
            "INSERT INTO hangeul_audio_assets (text, filepath, created_at) VALUES (?, ?, datetime('now','localtime'))",
            (w, rel),
        )
        conn.commit()
        made.append(w)
    conn.close()
    print("완료:", made if made else "(생성분 없음, 모두 이미 있었음)")


if __name__ == "__main__":
    main()
