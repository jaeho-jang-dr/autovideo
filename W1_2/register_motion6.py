# -*- coding: utf-8 -*-
"""한 스트라이드 컷 → **좌우 반전본 생성 + DB 등록**.

★사장님 지시(2026-08-11): "리버스 만들어서 왼편 걷기 달리기도 등록한다."

원본은 오른쪽을 향한다(_r). 좌우로 뒤집으면 왼쪽 걷기/달리기(_l)가 된다.

★flip 컬럼을 쓰지 않고 **실제로 뒤집은 파일**을 만들어 flip=0 으로 넣는다.
  W23 에서 walk_l 을 flip=1 로 넣었다가 렌더 쪽에서 한 번 더 뒤집혀
  이중 flip 사고가 났다. 파일로 박아두면 그 사고가 원천적으로 안 난다.
"""
import argparse
import glob
import os
import shutil
import sqlite3
import sys
from datetime import datetime

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

SRC = "W1_2/motion6_stride"
POSE_DIR = "assets/graphics/poses"
DB = os.path.join(ROOT, "channel", "content.db")
CHAR = "m6_stick"          # 스틱맨 이동 동작 6종


DDL = """CREATE TABLE IF NOT EXISTS anim_char_poses(
  id INTEGER PRIMARY KEY, char_key TEXT, pose_name TEXT, file_path TEXT,
  updated_at TEXT, flip INTEGER DEFAULT 0, pen INTEGER DEFAULT 0,
  UNIQUE(char_key,pose_name))"""


def register(rows):
    con = sqlite3.connect(DB)
    con.execute(DDL)                       # 없으면 만들어서 넣는다
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con.executemany(
        "INSERT INTO anim_char_poses(char_key,pose_name,file_path,updated_at,flip,pen) "
        "VALUES(?,?,?,?,0,0) "
        "ON CONFLICT(char_key,pose_name) DO UPDATE SET file_path=excluded.file_path,"
        " updated_at=excluded.updated_at, flip=0",
        [(CHAR, p, f, now) for p, f in rows])
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM anim_char_poses WHERE char_key=?",
                    (CHAR,)).fetchone()[0]
    con.close()
    return n


def one(key, src=SRC):
    """key(오른쪽 향함) → _r 등록 + 좌우 반전 _l 생성·등록."""
    fs = sorted(glob.glob(os.path.join(src, key, "*.png")))
    if not fs:
        print("  ★컷 없음:", key)
        return []
    os.makedirs(POSE_DIR, exist_ok=True)
    rows = []
    for i, p in enumerate(fs):
        # 오른쪽 향함 — 원본 그대로 복사
        rn = "%s_r_%02d" % (key, i)
        rf = os.path.join(POSE_DIR, "m6_%s.png" % rn).replace("\\", "/")
        shutil.copyfile(p, rf)
        rows.append((rn, rf))
        # 왼쪽 향함 — 좌우 반전
        ln = "%s_l_%02d" % (key, i)
        lf = os.path.join(POSE_DIR, "m6_%s.png" % ln).replace("\\", "/")
        ImageOps.mirror(Image.open(p).convert("RGBA")).save(lf)
        rows.append((ln, lf))

    a = Image.open(rows[0][1])
    print("  %-11s %2d컷 → 오른쪽 %d · 왼쪽 %d · %dx%d"
          % (key, len(fs), len(fs), len(fs), a.width, a.height))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--src", default=SRC, help="컷이 든 폴더 (기본 motion6_stride)")
    a = ap.parse_args()
    keys = a.keys or sorted(os.path.basename(d) for d in glob.glob(os.path.join(a.src, "*"))
                            if os.path.isdir(d))
    rows = []
    for k in keys:
        rows += one(k, a.src)
    if not rows:
        print("등록할 것 없음")
        return
    n = register(rows)
    print("DB 등록 %d행 → char_key='%s' (총 %d행)" % (len(rows), CHAR, n))


if __name__ == "__main__":
    main()
