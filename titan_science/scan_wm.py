# -*- coding: utf-8 -*-
"""titan 클립의 Veo 워터마크(반짝임) 위치·크기를 실측한다.

배경은 클립마다 움직이지만 워터마크는 **같은 자리에 계속 밝게** 박혀 있다.
그래서 여러 클립·여러 프레임의 밝기를 **최소값으로 누적**하면
움직이는 배경은 어두워지고 워터마크만 밝게 남는다.
"""
import os
import subprocess

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIP_DIR = os.path.join(ROOT, "titan_science", "keyframes")
WORK = os.path.join(ROOT, "titan_science", "_wm")
# 오른쪽 아래 구석만 본다
BOX = (1020, 560, 1280, 720)          # x0, y0, x1, y1


def frames(clip, times):
    out = []
    for t in times:
        p = os.path.join(WORK, "f.png")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", clip,
                        "-frames:v", "1", p], check=True)
        out.append(np.asarray(Image.open(p).convert("L").crop(BOX), np.float32))
    return out


def main():
    os.makedirs(WORK, exist_ok=True)
    clips = sorted(f for f in os.listdir(CLIP_DIR) if f.endswith(".mp4"))[:12]
    acc = None
    for c in clips:
        for a in frames(os.path.join(CLIP_DIR, c), [1.0, 3.0, 5.0, 7.0]):
            acc = a if acc is None else np.minimum(acc, a)
    Image.fromarray(acc.astype(np.uint8)).save(os.path.join(WORK, "wm_min.png"))

    # 누적 최소밝기가 높은 곳 = 항상 밝은 곳 = 워터마크
    thr = acc.max() * 0.72
    ys, xs = np.nonzero(acc >= thr)
    if not len(xs):
        print("워터마크를 못 찾았다")
        return 1
    x0, x1 = xs.min() + BOX[0], xs.max() + BOX[0]
    y0, y1 = ys.min() + BOX[1], ys.max() + BOX[1]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = x1 - x0 + 1, y1 - y0 + 1
    # 대각선 마름모라 꼭짓점까지 다 덮으려면 최소 포함원 = 긴 변
    d = max(w, h)
    print("클립 %d개 · 프레임 %d장 누적" % (len(clips), len(clips) * 4))
    print("워터마크 상자  x %d~%d  y %d~%d   (%dx%d)" % (x0, x1, y0, y1, w, h))
    print("중심 (%.1f, %.1f) · 최소 포함원 지름 %d" % (cx, cy, d))

    # 눈으로 확인할 표시본
    im = Image.open(os.path.join(WORK, "probe1.png")).convert("RGB")
    a = np.asarray(im).copy()
    a[int(y0):int(y1) + 1, int(x0):int(x0) + 2] = (255, 0, 0)
    a[int(y0):int(y1) + 1, int(x1) - 1:int(x1) + 1] = (255, 0, 0)
    a[int(y0):int(y0) + 2, int(x0):int(x1) + 1] = (255, 0, 0)
    a[int(y1) - 1:int(y1) + 1, int(x0):int(x1) + 1] = (255, 0, 0)
    Image.fromarray(a).crop((BOX[0], BOX[1], BOX[2], BOX[3])).resize(
        ((BOX[2] - BOX[0]) * 3, (BOX[3] - BOX[1]) * 3), Image.NEAREST).save(
        os.path.join(WORK, "wm_marked.png"))
    print(os.path.join(WORK, "wm_marked.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
