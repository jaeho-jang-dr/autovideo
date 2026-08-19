# -*- coding: utf-8 -*-
"""동작 컷 폴더의 **축척을 규격에 맞춘다** — 첫 프레임(서 있는 자세)을 기준 키로.

★사장님 지시(2026-08-13) "싸이즈도 일정 규격에 맞추어서 저장해야 한다."

## 왜 폴더째 **한 배율**인가
프레임마다 따로 키를 맞추면 자세가 바뀔 때 몸이 커졌다 작아졌다 한다(사장님이 가장
싫어하시는 것). 그래서 **첫 프레임의 잉크 키**로 배율 하나를 구하고, 그 배율을
64프레임 전부에 똑같이 먹인다. 자세에 따른 잉크 높이 변화는 그대로 남는다.

## 캐릭터별 기준 (실측한 기존 자산과 같은 값)
  스틱맨 740 · 졸라맨 775 · 졸라걸 745

    python W1_2/fit_cut_height.py zgirl_high_five2            # 재 보기만
    python W1_2/fit_cut_height.py zgirl_high_five2 --fix
    python W1_2/fit_cut_height.py zman_run_side2 --fix --target 775
"""
import argparse
import glob
import os
import shutil

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

CUT_DIRS = ["W1_2/motion6_cuts", "W1_2/motion6_stride"]
STAND = {"stickman": 740, "zman": 775, "zgirl": 745}


def target_of(key):
    if key.startswith("zgirl"):
        return STAND["zgirl"]
    if key.startswith("zman"):
        return STAND["zman"]
    return STAND["stickman"]


def ink_h(p):
    a = np.asarray(Image.open(p).convert("RGBA").split()[-1]) > 8
    if not a.any():
        return 0
    r = np.nonzero(a.any(1))[0]
    return int(r[-1] - r[0] + 1)


def find_dir(key):
    for base in CUT_DIRS:
        d = os.path.join(base, key)
        if os.path.isdir(d):
            return d
    return None


def fit(key, fix=False, target=None):
    d = find_dir(key)
    if not d:
        print("  ★폴더 없음:", key)
        return
    fs = sorted(glob.glob(os.path.join(d, "*.png")))
    if not fs:
        return
    tgt = target or target_of(key)
    first = ink_h(fs[0])
    if not first:
        return
    k = tgt / float(first)
    hs = [ink_h(p) for p in fs]
    print("  %-22s %2d컷 · 첫컷 %4dpx → 기준 %d · 배율 %.3f · 잉크 %d~%d → %d~%d"
          % (key, len(fs), first, tgt, k, min(hs), max(hs),
             round(min(hs) * k), round(max(hs) * k)))
    if not fix or abs(k - 1.0) < 0.01:
        return
    bak = d + "_pre_fit"
    if not os.path.isdir(bak):
        shutil.copytree(d, bak)
    for p in fs:
        im = Image.open(p).convert("RGBA")
        w = max(1, round(im.width * k))
        h = max(1, round(im.height * k))
        im.resize((w, h), Image.LANCZOS).save(p)
    print("       → 64컷 모두 %.3f배 (원본 %s)" % (k, os.path.basename(bak)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="+")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--target", type=int, default=None)
    a = ap.parse_args()
    print("축척 맞추기%s\n" % (" · ★고친다" if a.fix else " (재 보기만)"))
    for k in a.keys:
        fit(k, a.fix, a.target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
