# -*- coding: utf-8 -*-
"""수문장 컷 → **공용 자산 등록 + DB 저장**.

★사장님 지시(2026-08-13) "그래 되었다. 자산으로 올리고 DB에 저장하자."

## 좌우 반전을 만들지 않는 이유
`register_motion6.py` 는 오른쪽 향한 컷을 뒤집어 왼쪽(_l)을 같이 만든다. 수문장은
그렇게 하면 안 된다 — 정면 행진과 후면 걷기는 **좌우 방향이 없고**, 뒤집으면 창이
반대 손으로 넘어가고 검집도 반대쪽에 붙는다. 그래서 원본 그대로만 올린다.

## 올리는 것
  m6_guard_march_NN  64컷  정면 제자리 행진 (4스트라이드, 8초)
  m6_guard_away_NN   32컷  후면 걷기 — **전반부만** (원본 03~34컷)

  후반 두 스트라이드는 걷는 속도가 달라 버렸다(사장님 지적). 전반부 32컷은
  이음매 일치 0.731 로 제일 매끈해, 이어 붙이면 다리가 안 끊긴다.

    python W1_2/register_guard.py
"""
import glob
import os
import sqlite3
import shutil
import sys
from datetime import datetime

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

from cut_motion6 import body_top                                    # noqa: E402

POSE_DIR = "assets/graphics/poses"
DB = os.path.join(ROOT, "channel", "content.db")
CHAR = "m6_guard"
EP = "KO-W1-2"

# (자산 이름, 컷 폴더, 설명)
SETS = [
    ("guard_march", "W1_2/motion6_cuts/perf_guard_march",
     "수문장 정면 제자리 행진 · 4스트라이드"),
    ("guard_away", "W1_2/motion6_cuts/perf_guard_away_half",
     "수문장 후면 걷기 · 전반부 32컷(원본 03~34)"),
]

DDL_POSES = """CREATE TABLE IF NOT EXISTS anim_char_poses(
  id INTEGER PRIMARY KEY, char_key TEXT, pose_name TEXT, file_path TEXT,
  updated_at TEXT, flip INTEGER DEFAULT 0, pen INTEGER DEFAULT 0,
  UNIQUE(char_key,pose_name))"""

# ★오늘 확정된 투명컷 규격 — 사장님 말씀 그대로 남긴다.
RULES = [
    ("투명컷", "선만 남기고 속은 투명",
     "갓·도포·상하의는 테두리 선만 남기고 속은 비친다",
     "얼굴은 보이고 눈코입.. 얼굴만 흰색 나머지는 선으로 쌓인 투명"),
    ("투명컷", "흰색으로 남는 곳", "① 얼굴 동그라미 안 ② 창 두 줄 사이 — 이 둘뿐",
     "창은 검은 외부줄 안은 흰색"),
    ("투명컷", "사람은 통으로",
     "모자·얼굴·팔·상하의·다리가 한 덩어리로 이어지고 그 밖은 전부 투명",
     "사람은 통으로 모자 얼굴 팔 상하의 다리 연결 해서 그 밖은 다 투명"),
    ("투명컷", "바깥은 예외 없이 투명",
     "선에 갇힌 주머니도 뚫는다. 종이 질감 티끌(프레임당 100~300개)도 턴다",
     "사람의 바깥 부분은 전부 투명으로.. 컷 한다"),
    ("규격", "키 재는 법", "든 물건(창)은 빼고 **갓 끝 ~ 발바닥**만 740px",
     "키높이는 발과 모자끝 까지만 측정해"),
    ("컷", "후반부는 버린다",
     "후면 걷기는 전반부 32컷만 쓴다 — 뒤 두 스트라이드는 속도가 달라졌다",
     "처음 4스트라이드는 일정한 걷기 속도인데 마지막 두 스트라이드는 "
     "속도가 달라서 첫 4스트라이드까지만 선택해서 자르자"),
    ("기준 이미지", "수문장 정지 이미지는 회전 클립에서 골라낸다",
     "정면 옆모습을 두 번 뽑았으나 Flow 가 두 번 다 정면으로 그렸다 → "
     "8초 회전 클립을 만들어 88번(후면)·96번 프레임을 골랐다",
     "가로 하자 / 96번 프레임을 잡아서 측면 행진으로 만들어 보자"),
]


def measure(d):
    fs = sorted(glob.glob(os.path.join(d, "*.png")))
    hs, ws = [], []
    for p in fs:
        a = np.asarray(Image.open(p).convert("RGBA"))[:, :, 3]
        ys = np.nonzero((a > 8).any(1))[0]
        hs.append(int(ys[-1] - body_top(a) + 1))
        ws.append(Image.open(p).width)
    return fs, hs, ws


def main():
    os.makedirs(POSE_DIR, exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute(DDL_POSES)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows, cards = [], []

    for name, d, desc in SETS:
        fs, hs, ws = measure(d)
        if not fs:
            print("  ★컷 없음:", d)
            continue
        for i, p in enumerate(fs):
            pn = "%s_%02d" % (name, i)
            fp = os.path.join(POSE_DIR, "m6_%s.png" % pn).replace("\\", "/")
            shutil.copyfile(p, fp)
            rows.append((CHAR, pn, fp, now))
        im = Image.open(rows[-1][2])
        print("  %-12s %2d컷 → %s · 키 %d~%d · 폭 %d~%d"
              % (name, len(fs), POSE_DIR, min(hs), max(hs), min(ws), max(ws)))
        cards.append(("m6:%s" % name, "stickman_guard", "cutseq", POSE_DIR,
                      len(fs), int(im.width), int(im.height), int(max(hs)),
                      1, EP, "m6 이동컷 라이브러리", desc, now))

    con.executemany(
        "INSERT INTO anim_char_poses(char_key,pose_name,file_path,updated_at,flip,pen) "
        "VALUES(?,?,?,?,0,0) ON CONFLICT(char_key,pose_name) DO UPDATE SET "
        "file_path=excluded.file_path, updated_at=excluded.updated_at, flip=0", rows)
    # ★두 번 돌려도 되게 — 색을 입히고 다시 등록할 일이 생긴다(2026-08-13).
    con.executemany(
        "INSERT INTO char_assets(asset_key,owner,state,path,frames,w,h,ink_h,"
        "transparent,episode,source,note,updated_at) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) "
        "ON CONFLICT(asset_key,state,path) DO UPDATE SET frames=excluded.frames,"
        " w=excluded.w, h=excluded.h, ink_h=excluded.ink_h, note=excluded.note,"
        " updated_at=excluded.updated_at", cards)
    have = {(t, k) for t, k in
            con.execute("SELECT topic,key FROM stage_rules WHERE episode=?", (EP,))}
    con.executemany(
        "INSERT INTO stage_rules(episode,topic,key,value,said,updated_at) "
        "VALUES(?,?,?,?,?,?)",
        [(EP, t, k, v, s, now) for t, k, v, s in RULES if (t, k) not in have])
    con.commit()

    n = con.execute("SELECT COUNT(*) FROM anim_char_poses WHERE char_key=?",
                    (CHAR,)).fetchone()[0]
    nr = con.execute("SELECT COUNT(*) FROM stage_rules WHERE episode=?",
                     (EP,)).fetchone()[0]
    con.close()
    print("\nanim_char_poses  %d행 등록 → char_key='%s' (총 %d행)" % (len(rows), CHAR, n))
    print("char_assets      %d행 (m6:guard_march · m6:guard_away)" % len(cards))
    print("stage_rules      %d행 추가 (%s 총 %d행)" % (len(RULES), EP, nr))


if __name__ == "__main__":
    main()
