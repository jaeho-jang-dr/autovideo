# -*- coding: utf-8 -*-
"""W23 인준 정지 포즈: 흰배경 플러드필 컷아웃(흰 운동화 보존) → 키 통일(발끝 정렬)
   → W23/poses_still_norm/injun_w23_<key>.png (1024x1280 RGBA)

프레임컷(`W23/poses/`)과 **같은 잣대**로 맞춘다 — 캔버스 1024x1280 · 몸높이 770 · 발끝 y=1208.
(측정은 cutrang.body_metrics 와 동일: 폭 기준으로 머리끝을 찾아 **든 팔·손가락은 키에서 제외**)

1) 측정만:  python cutout_injun_w23.py measure
2) 저장:    python cutout_injun_w23.py apply
"""
import glob
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
SRC = "W23/poses_still"
DST = "W23/poses_still_norm"
CANVAS_W, CANVAS_H = 1024, 1280
FEET_Y = 1208          # ★프레임컷 실측값과 동일(walk_r_0 · board_write_0)
TARGET_BODY = 770      # ★머리끝~발끝 몸높이 통일값(든 팔 제외)


def cutout(src):
    """밝고 무채색 = 흰배경. 테두리에 닿은 흰 덩어리만 지운다(옷·운동화 속 흰색은 보존)."""
    arr = np.array(Image.open(src).convert("RGBA"))
    rgb = arr[:, :, :3].astype(int)
    lo, hi = rgb.min(axis=2), rgb.max(axis=2)
    white = (lo > 200) & ((hi - lo) < 30)
    lbl, _ = ndimage.label(white)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    arr[np.isin(lbl, list(border)), 3] = 0
    ys, xs = np.where(arr[:, :, 3] > 0)
    if len(ys) == 0:
        return None
    return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def body_metrics(crop):
    """머리끝~발끝 몸높이 + 몸통 중심 x. 상단부터 스캔해 몸통폭 절반 이상이 지속되는 첫 행 = 머리끝."""
    alpha = crop[:, :, 3] > 0
    w = alpha.sum(axis=1).astype(float)
    H = len(w)
    torso = np.median(w[int(H * 0.42):int(H * 0.72)]) or w.max()
    thr = max(0.5 * torso, 0.12 * w.max())
    head_top = 0
    for y in range(H):
        if w[y] >= thr and np.mean(w[y:y + 22] >= thr * 0.6) > 0.6:
            head_top = y
            break
    band = alpha[int(H * 0.42):int(H * 0.72)]
    bx = np.where(band.any(axis=0))[0]
    cx = int(bx.mean()) if len(bx) else crop.shape[1] // 2
    return head_top, (H - 1) - head_top, cx


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "measure"
    files = sorted(glob.glob(f"{SRC}/injun_w23_*.png"))
    print(f"대상 {len(files)}장  모드={mode}  (기준 키 {TARGET_BODY}px · 발끝 y={FEET_Y})")
    if mode == "apply":
        os.makedirs(DST, exist_ok=True)
    rows = []
    for p in files:
        key = os.path.basename(p).replace("injun_w23_", "")[:-4]
        crop = cutout(p)
        if crop is None:
            print(f"  ★{key} 컷아웃 실패"); continue
        head_top, span, cx = body_metrics(crop)
        s = TARGET_BODY / span
        nh, nw = round(crop.shape[0] * s), round(crop.shape[1] * s)
        rows.append((key, span, round(s, 3), nw, nh))
        if mode == "apply":
            im = Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)
            cv = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
            cv.paste(im, (CANVAS_W // 2 - round(cx * s), FEET_Y + 1 - nh), im)
            cv.save(f"{DST}/injun_w23_{key}.png")
    print(f"\n{'키':>4} {'원본키':>7} {'배율':>6} {'리사이즈':>12}")
    for key, span, s, nw, nh in rows:
        print(f"{key:18s} {span:7d} {s:6.3f}   {nw:4d}x{nh:<4d}")
    v = [r[1] for r in rows]
    print(f"\n원본 키 편차: {min(v)}~{max(v)} ({max(v)-min(v)}px, {(max(v)-min(v))/max(v)*100:.1f}%)"
          f"  →  통일 후 전부 {TARGET_BODY}px")
    if mode != "apply":
        print("※ 저장하려면: python cutout_injun_w23.py apply")


if __name__ == "__main__":
    main()
