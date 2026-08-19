# -*- coding: utf-8 -*-
"""얼굴 동그라미 안이 **뚫린 컷**을 찾아 흰색으로 채운다.

★사장님 지적(2026-08-14)
  "정면은 얼굴이 할로우고 측면은 얼굴 흰색인데 이러면 아니 된다.
   정면도 흰색 얼굴로 바꾸어라. 데이터베이스를 바꿔서 다른 데서도
   정면 흰색 얼굴로 나오게 하라."

블록3 영상에서 `high_five` 컷의 머리 안으로 배경(붉은 문)이 그대로 비쳤다.
얼굴이 비면 캐릭터가 아니라 구멍으로 보인다.

## 어떻게 찾나
잉크(검은 선) 한 덩어리를 메워 생긴 **안쪽 조각들 중 맨 위의 둥근 것**이 머리다.
그 안이 투명하면(알파가 낮으면) 뚫린 것이다. 눈·코·입은 잉크라 건드리지 않는다.

## 어떻게 채우나
머리 안쪽에서 **잉크가 아닌 곳만** 흰색·불투명으로 만든다. 그래서 눈·코·입은 남는다.
(전에 얼굴을 통째로 칠해 눈코입까지 지운 적이 있다 — 2026-08-13 사고)

    python W1_2/fill_face.py                # 검사만
    python W1_2/fill_face.py --fix          # 고치고 DB 갱신
"""
import argparse
import glob
import os
import shutil
import sqlite3
import sys
from datetime import datetime

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

DB = os.path.join(ROOT, "channel", "content.db")
CUT_DIRS = ["W1_2/motion6_cuts", "W1_2/motion6_stride"]
POSE_DIR = "assets/graphics/poses"
FACE_RATIO, FACE_MIN = 1.8, 0.004


def head_mask(a):
    """머리 동그라미 안쪽(눈·코·입 뺀 곳)."""
    al, rgb = a[:, :, 3], a[:, :, :3].astype(int)
    on = al > 8
    ink = on & (rgb.max(2) < 170)
    if not ink.any():
        return None, None
    lab, n = ndimage.label(ink)
    if n == 0:
        return None, None
    sz = ndimage.sum(ink, lab, range(1, n + 1))
    main = lab == (int(np.argmax(sz)) + 1)
    inside = ndimage.binary_fill_holes(main) & ~main
    hl, hn = ndimage.label(inside)
    area = float(main.sum())
    best = None
    for i in range(1, hn + 1):
        h = hl == i
        if h.sum() < area * FACE_MIN:
            continue
        ys, xs = np.nonzero(h)
        w, ht = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        if max(w, ht) / float(max(1, min(w, ht))) >= FACE_RATIO:
            continue
        if best is None or ys.min() < best[0]:
            best = (ys.min(), h)
    if best is None:
        return None, None
    # 머리 동그라미 안을 통째로 메운 뒤, 잉크(눈코입)를 뺀다
    circle = ndimage.binary_fill_holes(best[1] | (main & ndimage.binary_dilation(best[1], np.ones((3, 3)))))
    return circle & ~ink, circle


def check_one(p, fix=False):
    im = Image.open(p).convert("RGBA")
    a = np.array(im)
    face, circle = head_mask(a)
    if face is None or not face.any():
        return None
    filled = float((a[:, :, 3][face] > 200).mean())
    if filled >= 0.9 or not fix:
        return filled
    bak = os.path.splitext(p)[0] + "_hollow.png"
    if not os.path.exists(bak):
        shutil.copy2(p, bak)
    a[:, :, 0][face] = 255
    a[:, :, 1][face] = 255
    a[:, :, 2][face] = 255
    a[:, :, 3][face] = 255
    Image.fromarray(a, "RGBA").save(p)
    return filled


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("names", nargs="*")
    a = ap.parse_args()

    targets = []
    for base in CUT_DIRS:
        for d in sorted(glob.glob(os.path.join(base, "*"))):
            if not os.path.isdir(d) or any(v in d for v in ("_v1", "_v2", "_pre_fit", "_prev")):
                continue
            if a.names and os.path.basename(d) not in a.names:
                continue
            targets.append(d)

    print("얼굴 검사%s" % (" · ★채운다" if a.fix else " (검사만)"))
    fixed_dirs = []
    for d in targets:
        fs = [p for p in sorted(glob.glob(d + "/*.png")) if "_hollow" not in p]
        vals = [v for v in (check_one(p, a.fix) for p in fs) if v is not None]
        if not vals:
            continue
        m = float(np.mean(vals))
        n_bad = sum(1 for v in vals if v < 0.9)
        if n_bad:
            print("  %-24s %2d/%d컷 뚫림 (평균 %.2f)%s"
                  % (os.path.basename(d), n_bad, len(vals), m, " → 채움" if a.fix else ""))
            fixed_dirs.append(os.path.basename(d))
    if not fixed_dirs:
        print("  뚫린 컷 없음")
        return 0

    if a.fix:
        # ★DB 가 가리키는 실파일도 같이 고친다 — 다른 회차에서도 이 파일을 쓴다
        con = sqlite3.connect(DB)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = con.execute("SELECT id,pose_name,file_path FROM anim_char_poses").fetchall()
        n_db = 0
        for i, pn, fp in rows:
            if not fp or not os.path.exists(fp):
                continue
            if not any(fp.replace("\\", "/").find(d) >= 0 for d in fixed_dirs):
                continue
            if check_one(fp, True) is not None:
                con.execute("UPDATE anim_char_poses SET updated_at=? WHERE id=?", (now, i))
                n_db += 1
        # 공용 포즈 라이브러리도
        n_pose = 0
        for p in sorted(glob.glob(os.path.join(POSE_DIR, "*.png"))):
            if "_v1" in p or "_v2" in p or "_hollow" in p:
                continue
            v = check_one(p, True)
            if v is not None and v < 0.9:
                n_pose += 1
        con.commit()
        con.close()
        print("\nDB 파일 %d개 · 공용 포즈 %d장 같이 고침" % (n_db, n_pose))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
