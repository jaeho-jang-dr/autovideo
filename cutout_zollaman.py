#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cutout_zollaman.py — 졸라맨 포즈 PNG(흰 배경 불투명)를 투명 컷아웃으로 변환.

문제: home_vocab/zollaman_*.png 는 흰 배경이 alpha=255 불투명 → 영상에서 사각형이 배경을 가림.
해법: 4모서리에서 연결된 '근사-흰색' 배경만 flood-fill로 투명화(내부 흰색=얼굴/셔츠는 외곽과 단절돼 보존),
      이어 캐릭터 bbox로 트림 → 스틱맨처럼 '사람 라인만' 남는다.
출력: assets/graphics/poses/zollaman_<pose>.png (렌더러가 이 경로를 먼저 탐색).
재실행: python cutout_zollaman.py
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "home_vocab")
DST = os.path.join(ROOT, "assets", "graphics", "poses")
os.makedirs(DST, exist_ok=True)
WHITE_TOL = 36       # 배경으로 볼 '근사-흰색' 허용오차 (255-tol 이상)


def cutout(src_path, dst_path):
    im = Image.open(src_path).convert("RGBA")
    a = np.asarray(im).copy()
    h, w = a.shape[:2]
    rgb = a[:, :, :3].astype(np.int16)
    # 근사-흰색 마스크 (3채널 모두 255-tol 이상)
    near_white = np.all(rgb >= (255 - WHITE_TOL), axis=2)
    # 4모서리에서 BFS flood-fill (연결된 흰색 배경만)
    bg = np.zeros((h, w), dtype=bool)
    dq = deque()
    for (sy, sx) in ((0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)):
        if near_white[sy, sx] and not bg[sy, sx]:
            bg[sy, sx] = True
            dq.append((sy, sx))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not bg[ny, nx] and near_white[ny, nx]:
                bg[ny, nx] = True
                dq.append((ny, nx))
    # 배경 → 투명
    a[bg, 3] = 0
    # 캐릭터 bbox 트림 (alpha>0)
    ys, xs = np.where(a[:, :, 3] > 8)
    if len(ys) == 0:
        Image.fromarray(a, "RGBA").save(dst_path)
        return im.size, im.size
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    pad = 6
    y0 = max(0, y0 - pad); x0 = max(0, x0 - pad)
    y1 = min(h - 1, y1 + pad); x1 = min(w - 1, x1 + pad)
    crop = Image.fromarray(a[y0:y1 + 1, x0:x1 + 1], "RGBA")
    crop.save(dst_path)
    return im.size, crop.size


def main():
    n = 0
    sizes = []
    for f in sorted(os.listdir(SRC)):
        if f.startswith(("zollaman_", "zollanyeo_")) and f.endswith(".png"):
            orig, cropped = cutout(os.path.join(SRC, f), os.path.join(DST, f))
            sizes.append((f, cropped))
            n += 1
    print(f"cut out {n} zollaman poses -> assets/graphics/poses/")
    for f, c in sizes[:6]:
        print(f"  {f}: {c[0]}x{c[1]}")


if __name__ == "__main__":
    main()
