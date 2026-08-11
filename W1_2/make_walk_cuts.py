# -*- coding: utf-8 -*-
"""W24R 스틱맨 걷기 영상 → 한 스트라이드 8프레임 투명컷 (오른쪽/왼쪽).

원본 `W24R/walk_frames/stickman/f001~f192.png` (1280x720, **흰 배경**).
흰 배경을 지워 투명으로 만들고, 키를 통일해 저장한다.
왼쪽 걷기는 오른쪽을 **좌우 반전**해서 만든다.
"""
import glob
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "W24R", "walk_frames", "stickman")
OUT = os.path.join(ROOT, "W1_2", "_poses")
TARGET_H = 740          # 정지 포즈(키 739)와 맞춘다


def cut(im):
    """흰 배경 → 투명. 스틱맨은 검은 선뿐이라 밝기 하나로 가른다."""
    a = np.asarray(im.convert("L"), np.float32)
    # 밝을수록 배경. 부드러운 경계를 위해 램프를 준다
    alpha = np.clip((225.0 - a) / 55.0, 0, 1)
    rgb = np.zeros(a.shape + (3,), np.uint8)          # 잉크는 순검정
    rgb[..., :] = 26
    out = np.dstack([rgb, (alpha * 255).astype(np.uint8)])
    return Image.fromarray(out, "RGBA")


def trim_scale(im, target_h):
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    if not len(xs):
        return None
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    w, h = im.size
    nw = max(1, round(w * target_h / h))
    return im.resize((nw, target_h), Image.LANCZOS)


def main():
    fs = sorted(glob.glob(os.path.join(SRC, "*.png")))
    print("원본 %d 프레임" % len(fs))
    # ★한 스트라이드를 8등분 — 192프레임 중 다리 동작이 한 바퀴 도는 구간을 고른다.
    #   24fps 8초 = 192. 스트라이드 ≈ 34프레임이라 앞쪽 한 바퀴를 8등분.
    start, stride = 40, 34
    idx = [start + round(stride * i / 8) for i in range(8)]
    print("고른 프레임:", [i + 1 for i in idx])

    os.makedirs(OUT, exist_ok=True)
    made = []
    for k, i in enumerate(idx):
        im = trim_scale(cut(Image.open(fs[i])), TARGET_H)
        if im is None:
            print("  빈 프레임", i)
            continue
        pr = os.path.join(OUT, "stickman_w1d2_walk_r_%d.png" % k)
        im.save(pr)
        im.transpose(Image.FLIP_LEFT_RIGHT).save(
            os.path.join(OUT, "stickman_w1d2_walk_l_%d.png" % k))
        made.append(k)
        print("  walk_r_%d / walk_l_%d  %s" % (k, k, im.size))
    print("완료 %d쌍" % len(made))


if __name__ == "__main__":
    main()
