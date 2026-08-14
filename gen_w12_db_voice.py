# -*- coding: utf-8 -*-
"""W1-2 DB 발음 클립을 Azure **선희(여성)** 로 생성 → `web/public/audio/jamo/`.

★사장님 지시(2026-08-14)
  "데이터베이스 성우는 선희로 미리 만들어서 데이터베이스에 다 넣고 시작하라."

DB 발음 클립은 **영어판·일본어판 등 다른 언어판에서도 그대로 재사용**한다.
그래서 한글 발음은 언제나 한국어 성우(선희)로 만든다 — 영어판이라고 영어 음성으로
읽히면 발음 교육이 무너진다(발음 절대원칙).

★함정: `save_tts_azure` 의 성별은 `EDGE_ACTIVE_VOICE` 로 정해진다. 낡은 클립이 남성으로
  남아 있으면 여성 폴더에 있어도 남자 목소리가 난다 → 덮어쓴다.

  python gen_w12_db_voice.py --list      # 무엇을 만들지만 본다
  python gen_w12_db_voice.py             # 만든다
"""
import os
import re
import sqlite3
import sys
from datetime import datetime

os.environ["TTS_ENGINE"] = "azure"
os.environ["EDGE_ACTIVE_VOICE"] = "sunhi"            # ★여성(선희)
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
import tts_manager as tm                              # noqa: E402
try:
    tm.load_env()
except Exception as e:
    print("load_env warn:", e)

OUT = "web/public/audio/jamo"
DB = os.path.join(ROOT, "channel", "content.db")

# ── W1-2 가 가르치는 것 — 자모 8 + 단어 8 + 따라 하기 문장
JAMO = ["ㅏ", "ㅓ", "ㅗ", "ㅜ", "ㅡ", "ㅣ", "ㅐ", "ㅔ"]
WORDS = ["아이", "이", "오이", "우유", "오", "아우", "여우", "야외"]
SENTENCES = [
    "아이가 오이를 먹어요",
    "우유를 마셔요",
    "여우가 나왔어요",
    "야외에서 놀아요",
    "오, 정말요?",
    "아우가 형을 불러요",
    "모음만으로 만든 단어예요",
    "자음은 하나도 쓰지 않아요",
    "동그라미 이응은 소리가 나지 않아요",
    "따라 해 보세요",
]
# 특별 컷에서 새로 나온 말
EXTRA = ["수문장", "교대의식", "터널분수", "한글분수", "훈민정음", "태권도", "격파",
         "아래아", "반치음", "옛이응", "여린히읗"]

ALL = JAMO + WORDS + SENTENCES + EXTRA


def fname(w):
    """파일명에서 금지문자를 뺀다. 말하는 텍스트에는 물음표를 남겨 억양을 살린다."""
    return re.sub(r'[?*:"<>|/\\]', "", w).strip()


def register(rows):
    con = sqlite3.connect(DB)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for text, path in rows:
        cur = con.execute("SELECT id FROM hangeul_audio_assets WHERE text=?", (text,)).fetchone()
        if cur:
            con.execute("UPDATE hangeul_audio_assets SET filepath=?, created_at=? WHERE id=?",
                        (path, now, cur[0]))
        else:
            con.execute("INSERT INTO hangeul_audio_assets(text,filepath,created_at) VALUES(?,?,?)",
                        (text, path, now))
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM hangeul_audio_assets").fetchone()[0]
    con.close()
    return n


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if "--list" in sys.argv:
        for i, w in enumerate(ALL, 1):
            mark = "有" if os.path.exists(os.path.join(OUT, fname(w) + ".mp3")) else " "
            print("%3d [%s] %s" % (i, mark, w))
        print("\n총 %d개 (자모 %d · 단어 %d · 문장 %d · 특별 %d)"
              % (len(ALL), len(JAMO), len(WORDS), len(SENTENCES), len(EXTRA)))
        sys.exit(0)

    os.makedirs(OUT, exist_ok=True)
    print("=== W1-2 DB 발음 클립 %d개 → Azure 선희(여성) → %s ===" % (len(ALL), OUT), flush=True)
    ok = fail = 0
    rows = []
    for i, w in enumerate(ALL, 1):
        path = os.path.join(OUT, fname(w) + ".mp3")
        try:
            tm.save_tts_azure(w, path)               # ★덮어쓴다
            ok += 1
            rows.append((w, path.replace("\\", "/")))
            print("  %3d/%d  %s" % (i, len(ALL), w), flush=True)
        except Exception as e:
            fail += 1
            print("  %3d/%d  ★실패 %s — %s" % (i, len(ALL), w, str(e)[:70]), flush=True)
    n = register(rows) if rows else 0
    print("\n성공 %d · 실패 %d · DB hangeul_audio_assets 총 %d행" % (ok, fail, n))
