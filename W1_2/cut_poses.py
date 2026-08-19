# -*- coding: utf-8 -*-
"""**정지 포즈 PNG** → 투명컷. 동작 컷과 **같은 잣대**로 맞춘다.

`cut_oneshot.py` 는 mp4 를 받는다. 정지 포즈는 PNG 한 장이라 이쪽을 쓴다.
투명컷·머리 기준 크기·부스러기 제거는 **cut_oneshot 의 함수를 그대로 빌려 쓴다** —
동작 컷과 잣대가 달라지면 한 씬 안에서 캐릭터 크기가 튄다.

    python W1_2/cut_poses.py                 # _poses_z 전부(졸라, 색 보존)
    python W1_2/cut_poses.py --src W1_2/_poses --no-color   # 스틱맨
"""
import argparse
import glob
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

import cut_oneshot as C                                  # noqa: E402

SRC = "W1_2/_poses_z"
OUT = "W1_2/pose_cuts"


def key_of(name):
    """파일이름에서 캐릭터를 알아낸다 — char_head() 가 그걸로 기준을 고른다."""
    b = os.path.basename(name)
    if b.startswith("zgirl"):
        return "zgirl_high_five"        # 졸라걸 기준 이미지를 쓰는 아무 키
    if b.startswith("zman"):
        return "zman_head_tilt"         # 졸라맨
    return "run_front"                  # 스틱맨


def one(path, keep_color, out_dir):
    name = os.path.splitext(os.path.basename(path))[0]
    im = Image.open(path)
    # 배경 임계값 — 정지 포즈는 흰 바탕이라 코너에서 재면 된다
    g = np.asarray(im.convert("L"))
    corners = np.concatenate([g[:80, :80].ravel(), g[:80, -80:].ravel(),
                              g[-80:, :80].ravel(), g[-80:, -80:].ravel()])
    thr = max(150, int(corners.min()) - 12)

    cut = C.cut(im, thr, keep_color)
    b = C.bbox(cut) if cut is not None else None
    if b is None:
        print("  ★비었다:", name)
        return 0
    head = C.head_span(cut)
    target = C.char_head(key_of(name), keep_color)
    if not head or not target:
        print("  ★머리를 못 찾았다:", name)
        return 0
    s = target / float(head)

    c = cut.crop(b)
    w, h = max(1, round(c.width * s)), max(1, round(c.height * s))
    os.makedirs(out_dir, exist_ok=True)
    c.resize((w, h), Image.LANCZOS).save(os.path.join(out_dir, name + ".png"))
    print("  %-22s 임계 %3d · 머리 %3.0f→%3.0f · 키 %3d (서기 740 기준 %3d%%) · 폭 %d"
          % (name, thr, head, target, h, round(h * 100 / C.TARGET_H), w))
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--no-color", action="store_true")
    a = ap.parse_args()
    fs = sorted(glob.glob(os.path.join(a.src, "*.png")))
    if not fs:
        print("대상 없음:", a.src)
        return 1
    n = 0
    for p in fs:
        n += one(p, not a.no_color, a.out)
    print("%d장 → %s" % (n, a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
