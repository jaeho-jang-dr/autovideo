# -*- coding: utf-8 -*-
"""home_vocab 지은 포즈(jieun_*.png)의 베이지 배경(#F5F5F0 ≈ 236,236,224)을
4모서리 연결 flood-fill 로 투명화한다.

기존 make_bg_transparent(thresh=232)는 베이지의 파랑채널(224<232) 때문에
코너에서 즉시 멈춰 아무것도 못 지웠다. 여기서는 '코너 색 기준 + 허용오차' 방식으로
실제 배경색만 안전하게 제거한다(캐릭터 내부의 순백·검정 라인은 색이 충분히 달라 보존).

사용:
  python scratch/transparentize_poses.py --only jieun_clapping          # 1장 테스트
  python scratch/transparentize_poses.py --all                          # 25개 포즈 일괄
  옵션: --tol 28 (허용오차), --backup (원본을 home_vocab/_opaque_backup/ 로 보존)
"""
import os
import sys
import glob
import argparse
from collections import deque

import numpy as np
from PIL import Image

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HV = os.path.join(ROOT, "home_vocab")

# 25개 포즈 키 (베이스/casual/sitting 변형 제외; sitting 본체는 포함)
POSE_KEYS = [
    "jieun_waking_up", "jieun_packing", "jieun_washing_face", "jieun_eating",
    "jieun_walking", "jieun_sleeping", "jieun_brushing_teeth", "jieun_studying",
    "jieun_reading", "jieun_sitting", "jieun_running", "jieun_pointing",
    "jieun_cheering", "jieun_bowing", "jieun_thinking", "jieun_raising_hand",
    "jieun_drawing", "jieun_drinking", "jieun_cleaning", "jieun_opening_door",
    "jieun_putting_on_shoes", "jieun_waiting", "jieun_waving", "jieun_clapping",
    "jieun_jumping",
]


def transparentize(path, out_path, tol=28):
    """4모서리에서 코너 평균색과 tol 이내로 '연결된' 배경만 투명화. (alpha%, ok) 반환."""
    img = Image.open(path).convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]
    rgb = arr[:, :, :3].astype(int)

    # 4모서리 색의 중앙값 = 배경색 추정 (테두리 한 줄 노이즈 회피용으로 median)
    corners = np.array([
        rgb[0, 0], rgb[0, w - 1], rgb[h - 1, 0], rgb[h - 1, w - 1]
    ])
    bg = np.median(corners, axis=0)

    seen = np.zeros((h, w), dtype=bool)
    out_alpha = arr[:, :, 3].copy()
    dq = deque([(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)])
    cleared = 0
    while dq:
        y, x = dq.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y, x]:
            continue
        seen[y, x] = True
        if np.abs(rgb[y, x] - bg).max() > tol:
            continue  # 배경색과 충분히 다르면 멈춤(=라인아트 외곽)
        out_alpha[y, x] = 0
        cleared += 1
        dq.append((y + 1, x)); dq.append((y - 1, x))
        dq.append((y, x + 1)); dq.append((y, x - 1))

    arr[:, :, 3] = out_alpha
    Image.fromarray(arr, "RGBA").save(out_path)
    pct = 100.0 * cleared / (w * h)
    return pct, bg.astype(int).tolist()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="단일 키만 처리 (예: jieun_clapping)")
    ap.add_argument("--all", action="store_true", help="25개 포즈 전부")
    ap.add_argument("--tol", type=int, default=28)
    ap.add_argument("--backup", action="store_true", help="원본을 _opaque_backup/ 로 보존")
    ap.add_argument("--preview", help="결과를 별도 파일로 저장(원본 미덮어쓰기)")
    args = ap.parse_args()

    if args.only:
        keys = [args.only]
    elif args.all:
        keys = POSE_KEYS
    else:
        ap.error("--only KEY 또는 --all 중 하나 필요")

    bdir = os.path.join(HV, "_opaque_backup")
    if args.backup:
        os.makedirs(bdir, exist_ok=True)

    done = 0
    for k in keys:
        src = os.path.join(HV, f"{k}.png")
        if not os.path.exists(src):
            print(f"  [SKIP] 없음: {k}")
            continue
        if args.preview and len(keys) == 1:
            out = os.path.join(HV, args.preview)
        else:
            if args.backup:
                import shutil
                shutil.copyfile(src, os.path.join(bdir, f"{k}.png"))
            out = src
        pct, bg = transparentize(src, out, tol=args.tol)
        flag = "OK" if pct > 8 else "LOW?"
        print(f"  [{flag}] {k:24} bg≈{bg} 투명화 {pct:5.1f}% -> {os.path.relpath(out, ROOT)}")
        done += 1
    print(f"Done. {done} processed (tol={args.tol}).")


if __name__ == "__main__":
    main()
