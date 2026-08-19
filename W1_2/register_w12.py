# -*- coding: utf-8 -*-
"""W1-2 자산 → **DB `anim_char_poses` 등록**. 렌더 배선 3단계 중 2단계.

★[[w24r-render-wiring-chain]] : **렌더는 컷 폴더를 보지 않는다. `anim_char_poses` 만 본다.**
  이걸 빼먹으면 캐릭터가 조용히 사라진다(오류도 안 난다).

  ①컷 파일  → W1_2/motion6_cuts · motion6_stride · pose_cuts 에 있는가
  ②**DB 등록** → 여기(이 스크립트)
  ③씬 배선  → 씬이 그 포즈를 실제로 쓰는가 (build 단계)

## 등록 규칙
- 파일은 **`assets/graphics/poses/w12_*.png`** 로 복사해 둔다(렌더가 보는 곳)
- 이름은 `<동작키>_<두자리>` (동작 컷) · `<포즈키>` (정지 포즈)
- ★**flip 컬럼을 쓰지 않는다.** 좌우 반전은 실파일(`*_l`)로 이미 만들어 두었다
  (W23 walk_l 이중 flip 사고)

    python W1_2/register_w12.py
    python W1_2/register_w12.py --dry
"""
import argparse
import glob
import os
import shutil
import sqlite3
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

import w12_manifest as M                                 # noqa: E402

DB = os.path.join(ROOT, "channel", "content.db")
POSE_DIR = "assets/graphics/poses"
CUT_DIRS = ["W1_2/motion6_cuts", "W1_2/motion6_stride"]
STILL_DIR = "W1_2/pose_cuts"

DDL = """CREATE TABLE IF NOT EXISTS anim_char_poses(
  id INTEGER PRIMARY KEY, char_key TEXT, pose_name TEXT, file_path TEXT,
  updated_at TEXT, flip INTEGER DEFAULT 0, pen INTEGER DEFAULT 0,
  UNIQUE(char_key,pose_name))"""


def char_of(name):
    """이름에서 캐릭터를 가른다 — 키(char_heights.base_h)가 캐릭터마다 다르다."""
    if name.startswith("zgirl"):
        return "w12_zgirl"
    if name.startswith("zman"):
        return "w12_zman"
    return "w12_stick"


def collect():
    rows, seen = [], set()
    # ── 동작 컷 ──
    for base in CUT_DIRS:
        for d in sorted(glob.glob(os.path.join(base, "*"))):
            if not os.path.isdir(d):
                continue
            key = os.path.basename(d)
            if key.startswith("m6_") or key.startswith(("walk_", "run_")) and "_" not in key[4:]:
                pass                                    # m6 라이브러리는 이미 등록돼 있다
            fs = sorted(glob.glob(os.path.join(d, "*.png")))
            if not fs:
                continue
            for i, p in enumerate(fs):
                rows.append((char_of(key), "%s_%02d" % (key, i), p))
    # ── 정지 포즈 ──
    for p in sorted(glob.glob(os.path.join(STILL_DIR, "*.png"))):
        name = os.path.splitext(os.path.basename(p))[0]
        rows.append((char_of(name), name, p))
    # ── 스틱맨 기존 정지 포즈(W1_2/_poses) ──
    for p in sorted(glob.glob("W1_2/_poses/stickman_w1d2_*.png")):
        name = os.path.splitext(os.path.basename(p))[0]
        rows.append(("w12_stick", name, p))
    out = []
    for ch, name, p in rows:
        if (ch, name) in seen:
            continue
        seen.add((ch, name))
        out.append((ch, name, p))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    rows = collect()
    by_char = {}
    for ch, _, _ in rows:
        by_char[ch] = by_char.get(ch, 0) + 1
    print("모을 것 %d행" % len(rows))
    for ch in sorted(by_char):
        print("  %-11s %4d행" % (ch, by_char[ch]))
    if a.dry:
        return 0

    os.makedirs(POSE_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recs = []
    for ch, name, src in rows:
        dst = os.path.join(POSE_DIR, "w12_%s.png" % name).replace("\\", "/")
        shutil.copyfile(src, dst)
        recs.append((ch, name, dst, now))

    con = sqlite3.connect(DB)
    con.execute(DDL)
    con.executemany(
        "INSERT INTO anim_char_poses(char_key,pose_name,file_path,updated_at,flip,pen) "
        "VALUES(?,?,?,?,0,0) "
        "ON CONFLICT(char_key,pose_name) DO UPDATE SET file_path=excluded.file_path,"
        " updated_at=excluded.updated_at, flip=0", recs)
    con.commit()

    print("\nDB 등록 완료")
    for ch in sorted(by_char):
        n = con.execute("SELECT COUNT(*) FROM anim_char_poses WHERE char_key=?",
                        (ch,)).fetchone()[0]
        print("  %-11s %4d행" % (ch, n))

    # ── ③ 씬 배선 검증 — 매니페스트가 부르는 이름이 DB 에 있는가 ──
    print("\n씬이 부르는 이름이 DB 에 있는가")
    have = set()
    for ch, nm in con.execute("SELECT char_key,pose_name FROM anim_char_poses"):
        have.add(nm)
    miss = []
    for sc, _, _, cuts, poses, _, _ in M.SCENES:
        for k in cuts:
            if k.startswith("m6_"):
                continue                                # m6 라이브러리 = 별도 char_key
            if not any(n.startswith(k + "_") for n in have):
                miss.append((sc, "컷 " + k))
        for k in poses:
            if k not in have:
                miss.append((sc, "포즈 " + k))
    if miss:
        for sc, what in miss:
            print("  ★S%-2d %s — DB 에 없다" % (sc, what))
    else:
        print("  전부 있다 — 26씬 배선 통과")
    con.close()
    return 1 if miss else 0


if __name__ == "__main__":
    raise SystemExit(main())
