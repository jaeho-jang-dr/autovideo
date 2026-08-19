# -*- coding: utf-8 -*-
"""캐릭터·배경 자산을 **DB에 등록**한다 — 다음 편에서 꺼내 쓰려고.

★사장님 지시(2026-08-13)
  "캐릭터랑 자산의 이름을 다 데이터베이스에 저장해 놓고, 자산의 상태 — 투명컷인지
   스틸동영상인지 동영상 원본인지 — 로컬에 있는 위치까지 데이터베이스에 다 등록하고,
   다음 편에서 쓰고 싶을 때 언제든지 데이터베이스에서 찾아서 꺼내 쓸 수 있게 해 두라."
  "캐릭터 자산, 배경 자산도 마찬가지이다. 다 저장해 두라."

## 테이블 `char_assets` — 자산 하나가 한 행
| 칸 | 뜻 |
|---|---|
| `asset_key`   | 이름 (예: `zgirl_high_five2`, `steps_seat`) |
| `owner`       | 누구 것인가 — stickman · zman · zgirl · bg |
| `state`       | ★**상태** — `video`(동영상 원본) · `cutseq`(투명컷 스틸동영상) · `pose`(정지 투명컷) · `still`(정지 배경) · `guide`(기준 이미지) |
| `path`        | 로컬 위치 (레포 기준 상대경로) |
| `frames`      | 몇 장인가 (동영상은 1) |
| `w`,`h`       | 크기 |
| `ink_h`       | 잉크 키(서 있는 자세 기준) — 축척이 맞는지 여기서 본다 |
| `transparent` | 투명컷인가 (1/0) |
| `episode`     | 어느 편에서 만들었나 (W1-2) |
| `source`      | 어디서 왔나 (Flow Omni Flash 등) |
| `note`        | 한 줄 설명 |

## ★회차마다 따로 들어 있다 (사장님 2026-08-13)
  "특히 W24R 에서 많이 만들었고 이번 회에서 많이 만들고… 각 캐릭터 자산들 따로따로
   회차마다 들어 있다."

  그래서 회차 폴더를 **한 곳에 모으지 않고 있는 자리 그대로 등록**한다. `episode`
  칸으로 어느 회차 것인지 갈라 두면, 다음 편에서 `--find` 로 찾아 그 경로를 그대로
  쓰면 된다. 옮기지 않으니 기존 회차 렌더가 깨질 일이 없다.

  훑는 곳 — `W1_2` · `W24R` · `W24` · `W23` · `W22` · `W21` · `assets/graphics/poses`
  건너뛰는 곳 — `_` 로 시작하는 작업 버퍼, `_v1`/`_v2`/`_pre_fit` 백업, 검증 시트

## 쓰는 법
    python W1_2/register_assets.py                 # 훑어보기만
    python W1_2/register_assets.py --write         # DB에 등록
    python W1_2/register_assets.py --find 달리기    # 찾아 쓰기
    python W1_2/register_assets.py --list zgirl    # 그 캐릭터 자산 전부
"""
import argparse
import glob
import os
import sqlite3
import time

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

DB = "channel/content.db"

# ★회차별 자산이 든 곳 — (회차 이름, 폴더). 있는 자리 그대로 등록한다.
EPISODES = [
    ("W1-2", "W1_2"),
    ("W24R", "W24R"),
    ("W24",  "W24"),
    ("W23",  "W23"),
    ("W22",  "W22"),
    ("W21",  "W21"),
]
# 회차 안에서 자산으로 보는 폴더 (이 이름이면 그 상태로 등록)
CUTSEQ_DIRS = ("motion6_cuts", "motion6_stride", "group_cuts", "group_cuts_v2",
               "group_cuts_w", "cuts", "clip_frames", "walk_frames", "frames")
POSE_DIRS_N = ("poses", "pose_cuts", "_poses")
BG_DIRS = ("bg", "bg_clips", "backgrounds")
VIDEO_DIRS = ("motion6", "clips", "group_clips", "still_clips", "walks", "play",
              "dance", "bg_clips")
GUIDE_DIRS = ("guides", "motion_src", "_front_src")

SKIP_MARK = ("_v1", "_v2", "_pre_fit", "sheet", "_check", "_buf", "_tmp",
             "__pycache__", "_discarded", "_reject", "_pending", "_view",
             "_seam", "preview", "thumbs", "_frames", "_show", "_bgmeas",
             "_inspect", "_cmd", "_plan", "_scenes", "_stage")


def skip(p):
    q = p.replace("\\", "/").lower()
    return any(s in q for s in SKIP_MARK)

DDL = """
CREATE TABLE IF NOT EXISTS char_assets (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  asset_key   TEXT NOT NULL,
  owner       TEXT NOT NULL,
  state       TEXT NOT NULL,
  path        TEXT NOT NULL,
  frames      INTEGER DEFAULT 1,
  w           INTEGER,
  h           INTEGER,
  ink_h       INTEGER,
  transparent INTEGER DEFAULT 0,
  episode     TEXT,
  source      TEXT,
  note        TEXT,
  updated_at  TEXT,
  UNIQUE(asset_key, state, path)
);
CREATE INDEX IF NOT EXISTS ix_char_assets_key   ON char_assets(asset_key);
CREATE INDEX IF NOT EXISTS ix_char_assets_owner ON char_assets(owner, state);
"""

# 상태 이름 — 사장님 말씀 그대로
STATE_KR = {
    "video":  "동영상 원본",
    "cutseq": "투명컷 스틸동영상",
    "pose":   "정지 투명컷",
    "still":  "정지 배경",
    "guide":  "기준 이미지",
}


def owner_of(key, path=""):
    """이름과 경로로 **누구 자산인지** 가른다.

    ★한 클립에 여럿이 나오는 것(W24 group_cuts 처럼)은 `group` 으로 둔다 —
      스틱맨으로 몰아 두면 다음 편에서 꺼내 쓸 때 헷갈린다.
    """
    k = (key + " " + path).lower().replace("\\", "/")
    if "zgirl" in k or "zolla_girl" in k or "zollagirl" in k:
        return "zgirl"
    if "zman" in k or "zolla_man" in k or "zollaman" in k:
        return "zman"
    if "group_cut" in k or "group_clip" in k or "/trio" in k:
        return "group"                       # 여러 캐릭터가 함께 나오는 것
    for name, own in (("jieun", "jieun"), ("지은", "jieun"),
                      ("injun", "injun"), ("인준", "injun"),
                      ("madam", "madamjay"), ("teacher", "teacherjay"),
                      ("tj_", "teacherjay"), ("drjay", "drjay")):
        if name in k:
            return own
    if "stickman" in k or k.startswith(("sm_", "m6_", "m6:")):
        return "stickman"
    return "stickman"


def ink_h_of(p):
    try:
        a = np.asarray(Image.open(p).convert("RGBA").split()[-1]) > 8
    except Exception:
        return None
    if not a.any():
        return None
    r = np.nonzero(a.any(1))[0]
    return int(r[-1] - r[0] + 1)


def is_transparent(p):
    try:
        return Image.open(p).mode in ("RGBA", "LA")
    except Exception:
        return False


def row(key, own, state, path, frames, w, h, ih, tr, ep, src, note):
    return (key, own, state, path.replace("\\", "/"), frames, w, h, ih, tr,
            ep, src, note)


def scan_episode(ep, root):
    """회차 폴더 하나를 훑는다 — 있는 자리 그대로."""
    rows = []
    if not os.path.isdir(root):
        return rows

    # ① 동영상 원본
    for sub in VIDEO_DIRS:
        d = os.path.join(root, sub)
        if not os.path.isdir(d) or skip(d):
            continue
        for p in sorted(glob.glob(os.path.join(d, "*.mp4"))):
            k = os.path.splitext(os.path.basename(p))[0]
            own = "bg" if "bg" in sub else owner_of(k)
            rows.append(row(k, own, "video", p, 1, None, None, None, 0, ep,
                            "Flow " + sub,
                            "동영상 원본 (%dKB)" % (os.path.getsize(p) // 1024)))

    # ② 투명컷 스틸동영상 — 프레임 폴더
    for sub in CUTSEQ_DIRS:
        base = os.path.join(root, sub)
        if not os.path.isdir(base):
            continue
        for d in sorted(glob.glob(os.path.join(base, "*"))):
            if not os.path.isdir(d) or skip(d):
                continue
            fs = sorted(glob.glob(os.path.join(d, "*.png")))
            if len(fs) < 4:
                continue
            k = os.path.basename(d)
            im = Image.open(fs[0])
            ih = ink_h_of(fs[0])
            rows.append(row(k, owner_of(k, d), "cutseq", d, len(fs),
                            im.width, im.height, ih,
                            1 if is_transparent(fs[0]) else 0, ep,
                            "%s/%s" % (root, sub),
                            "%d컷 · 첫컷 잉크 %spx" % (len(fs), ih)))

    # ③ 정지 투명컷 포즈
    for sub in POSE_DIRS_N:
        d = os.path.join(root, sub)
        if not os.path.isdir(d) or skip(d):
            continue
        for p in sorted(glob.glob(os.path.join(d, "*.png"))):
            b = os.path.splitext(os.path.basename(p))[0]
            if skip(b):
                continue
            im = Image.open(p)
            rows.append(row(b, owner_of(b, p), "pose", p, 1, im.width, im.height,
                            ink_h_of(p), 1 if is_transparent(p) else 0, ep,
                            "%s/%s" % (root, sub), "정지 투명컷"))

    # ④ 배경 — 동영상·정지
    for sub in BG_DIRS:
        d = os.path.join(root, sub)
        if not os.path.isdir(d):
            continue
        for p in sorted(glob.glob(os.path.join(d, "*.mp4"))):
            k = os.path.splitext(os.path.basename(p))[0]
            rows.append(row(k, "bg", "video", p, 1, 1280, 720, None, 0, ep,
                            "Flow 배경 동영상",
                            "배경 동영상 (%dKB)" % (os.path.getsize(p) // 1024)))
        for p in sorted(glob.glob(os.path.join(d, "*.png"))):
            k = os.path.splitext(os.path.basename(p))[0]
            if k.startswith("_") or skip(k):
                continue
            im = Image.open(p)
            rows.append(row(k, "bg", "still", p, 1, im.width, im.height, None, 0,
                            ep, "Flow 배경 정지", "정지 배경"))
        for p in sorted(glob.glob(os.path.join(d, "still", "*.png"))):
            k = os.path.splitext(os.path.basename(p))[0]
            im = Image.open(p)
            rows.append(row(k, "bg", "still", p, 1, im.width, im.height, None, 0,
                            ep, "Flow 배경 정지", "정지 배경"))

    # ⑤ 기준 이미지
    for sub in GUIDE_DIRS:
        d = os.path.join(root, sub)
        if not os.path.isdir(d) or skip(d):
            continue
        for p in sorted(glob.glob(os.path.join(d, "*.png"))):
            b = os.path.splitext(os.path.basename(p))[0]
            im = Image.open(p)
            rows.append(row(b, owner_of(b, p), "guide", p, 1, im.width, im.height,
                            ink_h_of(p), 1 if is_transparent(p) else 0, ep,
                            "%s/%s" % (root, sub), "Flow 기준 이미지"))
    return rows


def scan():
    """(asset_key, owner, state, path, frames, w, h, ink_h, transparent,
       episode, source, note)"""
    rows = []
    for ep, root in EPISODES:
        rows += scan_episode(ep, root)

    # ⑥ m6 이동컷 라이브러리 (낱장 · 회차 공용)
    keys = {}
    for p in sorted(glob.glob("assets/graphics/poses/m6_*.png")):
        b = os.path.basename(p)[3:-4]
        if b[-3:-2] == "_" and b[-2:].isdigit():
            keys.setdefault(b[:-3], []).append(p)
    for k in sorted(keys):
        fs = keys[k]
        im = Image.open(fs[0])
        rows.append(row("m6:" + k, "stickman", "cutseq", "assets/graphics/poses",
                        len(fs), im.width, im.height, ink_h_of(fs[0]),
                        1 if is_transparent(fs[0]) else 0, "공용",
                        "m6 이동컷 라이브러리",
                        "낱장 m6_%s_NN.png · %d컷" % (k, len(fs))))
    return rows


def write(rows):
    c = sqlite3.connect(DB)
    c.executescript(DDL)
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    n = 0
    for r in rows:
        c.execute(
            "INSERT INTO char_assets (asset_key,owner,state,path,frames,w,h,ink_h,"
            "transparent,episode,source,note,updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(asset_key,state,path) DO UPDATE SET "
            "owner=excluded.owner, frames=excluded.frames, w=excluded.w, h=excluded.h,"
            "ink_h=excluded.ink_h, transparent=excluded.transparent,"
            "source=excluded.source, note=excluded.note, updated_at=excluded.updated_at",
            (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8],
             r[9], r[10], r[11], now))
        n += 1
    c.commit()
    return n


def show(rows):
    by = {}
    for r in rows:
        by.setdefault((r[1], r[2]), []).append(r)
    print("%-10s %-20s %5s" % ("주인", "상태", "개수"))
    for (own, st) in sorted(by):
        print("  %-8s %-20s %5d" % (own, STATE_KR.get(st, st), len(by[(own, st)])))

    ep = {}
    for r in rows:
        ep.setdefault(r[9], {}).setdefault(r[2], 0)
        ep[r[9]][r[2]] += 1
    print("\n%-8s %s" % ("회차", " · ".join("%s" % STATE_KR[s] for s in
                                            ("video", "cutseq", "pose", "still", "guide"))))
    for e in sorted(ep):
        d = ep[e]
        print("  %-6s %5d %10d %10d %10d %10d"
              % (e, d.get("video", 0), d.get("cutseq", 0), d.get("pose", 0),
                 d.get("still", 0), d.get("guide", 0)))
    print("\n합계 %d개" % len(rows))


def find(q):
    c = sqlite3.connect(DB)
    rs = c.execute(
        "SELECT asset_key,owner,state,path,frames,ink_h,note FROM char_assets "
        "WHERE asset_key LIKE ? OR note LIKE ? OR owner LIKE ? ORDER BY owner,state,asset_key",
        ("%%%s%%" % q, "%%%s%%" % q, "%%%s%%" % q)).fetchall()
    if not rs:
        print("없다:", q)
        return
    print("찾은 것 %d개\n" % len(rs))
    for k, own, st, p, fr, ih, note in rs:
        print("  %-22s %-9s %-18s %3d컷 잉크%-5s %s"
              % (k, own, STATE_KR.get(st, st), fr, ih or "-", p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--find", default=None)
    ap.add_argument("--list", default=None)
    a = ap.parse_args()
    if a.find or a.list:
        find(a.find or a.list)
        return 0
    rows = scan()
    show(rows)
    if a.write:
        n = write(rows)
        print("\n✅ char_assets 에 %d개 등록 (%s)" % (n, DB))
    else:
        print("\n등록하려면 --write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
