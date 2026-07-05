# -*- coding: utf-8 -*-
"""face_overlay.py — 라인아트 캐릭터 머리에 얼굴(눈·입)+주황 머리묶음을 그려 졸라걸 스타일로.
머리(최상단 블롭) 추적→얼굴 요소 오버레이. 사용: python face_overlay.py <src_dir> <out_dir>
"""
import sys, os, glob
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

SRC = sys.argv[1] if len(sys.argv) > 1 else "scratch/lineart3"
OUT = sys.argv[2] if len(sys.argv) > 2 else "scratch/faced"
os.makedirs(OUT, exist_ok=True)
INK = (24, 21, 19)
ORANGE = (232, 126, 58)


def find_head(a):
    """어두운(선) 픽셀에서 머리 영역(상단 블롭) 찾기 → (cx, cy, r)."""
    dark = a < 130
    ys = np.where(dark.any(axis=1))[0]
    if len(ys) < 5:
        return None
    top = ys[0]; bot = ys[-1]; H = bot - top
    # 머리 = 상단 ~16% 밴드
    hb = int(top + H * 0.16)
    band = dark[top:hb]
    xs = np.where(band.any(axis=0))[0]
    if len(xs) < 3:
        return None
    cx = (xs[0] + xs[-1]) / 2
    cy = (top + hb) / 2
    r = (xs[-1] - xs[0]) / 2
    return cx, cy, r


def add_face(img):
    g = np.array(img.convert("L"))
    hd = find_head(g)
    d = ImageDraw.Draw(img)
    if hd is None:
        return img
    cx, cy, r = hd
    # 주황 머리묶음(정수리 뒤)
    br = r * 0.5
    d.ellipse([cx - br, cy - r*1.15 - br, cx + br, cy - r*1.15 + br], fill=ORANGE, outline=INK, width=max(2, int(r*0.08)))
    d.ellipse([cx - r*0.7, cy - r*0.95, cx + r*0.7, cy - r*0.2], fill=ORANGE, outline=None)  # 앞머리
    # 눈 2개
    ex = r * 0.34; ey = cy + r * 0.05; er = max(2, r * 0.14)
    for sx in (-1, 1):
        d.ellipse([cx + sx*ex - er, ey - er, cx + sx*ex + er, ey + er], fill=INK)
    # 볼(선택) / 입(웃음)
    mw = r * 0.42; my = cy + r * 0.5
    d.arc([cx - mw, my - r*0.25, cx + mw, my + r*0.3], 20, 160, fill=INK, width=max(2, int(r*0.11)))
    return img


if __name__ == "__main__":
    fs = sorted(glob.glob(os.path.join(SRC, "*.png")))
    for i, f in enumerate(fs):
        im = Image.open(f).convert("RGB")
        im = add_face(im)
        im.save(os.path.join(OUT, f"f_{i:04d}.png"))
    print(f"FACE_DONE {len(fs)} -> {OUT}")
