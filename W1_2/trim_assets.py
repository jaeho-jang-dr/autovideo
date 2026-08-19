# -*- coding: utf-8 -*-
"""자산을 **규격에 맞춰** 다듬는다 — 잉크 여백 없애기.

★사장님 지시(2026-08-13)
  "싸이즈도 일정 규격에 맞추어서 저장해야 한다."

## 무엇이 어긋나 있었나
1024×1024 캔버스로 뽑힌 포즈들은 발 밑에 **투명 여백이 203~307px** 남아 있었다.
합성기(`place_xy`)는 **이미지 아래끝**을 발 y 에 맞추고 **이미지 높이**로 크기를
정하므로, 이 여백이 그대로 두 가지 사고가 된다.

  · 발이 땅에서 **뜬다** (여백만큼 아래로 밀림)
  · 키가 **줄어든다** (1024 로 나누니 잉크는 721/1024 = 70% 로만 보임)

교정 9·12·15·20번이 전부 이 하나였다. 근본은 **잉크 밖 여백**이므로 여기서 깎는다.

## 규격
  · 정지 포즈  — 잉크 bbox 로 딱 잘라 저장한다(여백 0)
  · 동작 컷    — ★**폴더 전체의 합집합 bbox** 로 잘라야 한다. 프레임마다 따로 자르면
                 프레임끼리 기준이 달라져 캐릭터가 덜덜 떤다
  · 원본은 `<이름>_v1.png` / `<폴더>_v1/` 로 보관한다

    python W1_2/trim_assets.py                 # 검사만
    python W1_2/trim_assets.py --fix           # 실제로 깎는다
    python W1_2/trim_assets.py --cuts --fix    # 동작 컷 폴더까지
"""
import argparse
import glob
import os
import shutil

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

POSE_DIRS = ["W1_2/pose_cuts", "W1_2/_poses"]
CUT_DIRS = ["W1_2/motion6_cuts", "W1_2/motion6_stride"]
SLACK = 8                          # 이만큼 이하 여백은 그냥 둔다(안티에일리어싱)


def ink_box(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im.split()[-1]) > 8
    if not a.any():
        return None, im.size
    ys, xs = np.nonzero(a)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1), im.size


def pad_of(box, size):
    if not box:
        return (0, 0, 0, 0)
    return (box[0], box[1], size[0] - box[2], size[1] - box[3])


def trim_pose(path, fix):
    box, size = ink_box(path)
    if not box:
        return 0
    l, t, r, b = pad_of(box, size)
    if max(l, t, r, b) <= SLACK:
        return 0
    print("  %-34s %4dx%-4d 여백 좌%d 상%d 우%d 하%d → 잉크 %dx%d"
          % (os.path.splitext(os.path.basename(path))[0], size[0], size[1],
             l, t, r, b, box[2] - box[0], box[3] - box[1]))
    if not fix:
        return 1
    bak = os.path.splitext(path)[0] + "_v1.png"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    Image.open(path).convert("RGBA").crop(box).save(path)
    return 1


def trim_folder(d, fix):
    """★한 폴더는 **합집합 bbox** 하나로 자른다 — 프레임 사이 기준이 흔들리면 떤다."""
    fs = sorted(glob.glob(os.path.join(d, "*.png")))
    if not fs:
        return 0
    L = T = 10 ** 9
    R = B = 0
    size = None
    for p in fs:
        box, size = ink_box(p)
        if not box:
            continue
        L, T = min(L, box[0]), min(T, box[1])
        R, B = max(R, box[2]), max(B, box[3])
    if size is None or R <= L:
        return 0
    l, t, r, b = L, T, size[0] - R, size[1] - B
    if max(l, t, r, b) <= SLACK:
        return 0
    print("  %-24s %2d프레임 %4dx%-4d 여백 좌%d 상%d 우%d 하%d → %dx%d"
          % (os.path.basename(d), len(fs), size[0], size[1], l, t, r, b, R - L, B - T))
    if not fix:
        return 1
    bak = d + "_v1"
    if not os.path.isdir(bak):
        shutil.copytree(d, bak)
    for p in fs:
        Image.open(p).convert("RGBA").crop((L, T, R, B)).save(p)
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--cuts", action="store_true")
    a = ap.parse_args()

    print("정지 포즈%s" % (" · ★깎는다" if a.fix else " (검사만)"))
    n = 0
    for d in POSE_DIRS:
        for p in sorted(glob.glob(os.path.join(d, "*.png"))):
            b = os.path.splitext(os.path.basename(p))[0]
            if b.endswith("_v1") or "sheet" in b:
                continue
            n += trim_pose(p, a.fix)

    if a.cuts:
        print("\n동작 컷%s" % (" · ★깎는다" if a.fix else " (검사만)"))
        for base in CUT_DIRS:
            for d in sorted(glob.glob(os.path.join(base, "*"))):
                if os.path.isdir(d) and not d.endswith("_v1"):
                    n += trim_folder(d, a.fix)

    print("\n여백 있는 자산 %d개%s" % (n, " 깎았다" if a.fix else " — 깎으려면 --fix"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
