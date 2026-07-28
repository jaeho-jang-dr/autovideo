# -*- coding: utf-8 -*-
"""W23 배경에서 Veo 워터마크 제거 (2026-07-28).

Flow/Veo 산출물은 **우하단에 'Veo' 워터마크**가 박혀 나온다(1280x720 기준 ≈ x1232~1276, y686~714).
정지 배경은 PIL 로 주변 픽셀을 늘려 덮고, 배경 동영상은 ffmpeg `delogo` 로 지운다.

사용: python strip_veo_watermark.py [--check]
"""
import glob
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
STILL = "assets/graphics/bg"
CLIPS = "W23/bg_clips"
BAK = "scratch/_bg_before_wm"
# 1280x720 기준 워터마크 상자(여유 포함)
BOX = (1228, 682, 1280, 718)


def has_watermark(p):
    """워터마크 자리에 밝은 글자 획이 있는지 — 주변 중앙값보다 밝은 픽셀 비율로 판정."""
    im = Image.open(p).convert("L")
    sx, sy = im.width / 1280, im.height / 720
    b = (int(BOX[0] * sx), int(BOX[1] * sy), int(BOX[2] * sx), int(BOX[3] * sy))
    crop = np.array(im.crop(b)).astype(int)
    ring = np.array(im.crop((b[0] - 60, b[1], b[0], b[3]))).astype(int)
    return float((crop > np.median(ring) + 26).mean())


def fix_still(p):
    im = Image.open(p).convert("RGB")
    sx, sy = im.width / 1280, im.height / 720
    b = (int(BOX[0] * sx), int(BOX[1] * sy), int(BOX[2] * sx), int(BOX[3] * sy))
    # ★왼쪽 인접 띠를 좌우반전해 덮되, **가장자리를 페더링**해 이음매를 없앤다.
    #   (그냥 붙이면 4K로 확대했을 때 사각 자국이 보인다)
    w, h = b[2] - b[0], b[3] - b[1]
    pad = 10
    src = im.crop((b[0] - w - pad, b[1] - pad, b[0] + pad, b[3] + pad)) \
            .transpose(Image.FLIP_LEFT_RIGHT).filter(ImageFilter.GaussianBlur(2.0))
    W2, H2 = src.size
    mx = np.minimum(np.arange(W2), np.arange(W2)[::-1]) / max(1, pad)
    my = np.minimum(np.arange(H2), np.arange(H2)[::-1]) / max(1, pad)
    mask = np.clip(np.minimum(mx[None, :], my[:, None]), 0, 1)
    im.paste(src, (b[0] - pad, b[1] - pad),
             Image.fromarray((mask * 255).astype("uint8"), "L"))
    im.save(p)


def fix_clip(p):
    sx, sy = 1.0, 1.0                                  # 클립은 1280x720 실측
    x, y = int(BOX[0] * sx), int(BOX[1] * sy)
    w, h = int((BOX[2] - BOX[0]) * sx) - 1, int((BOX[3] - BOX[1]) * sy)
    tmp = p + ".tmp.mp4"
    r = subprocess.run(["ffmpeg", "-y", "-i", p, "-vf", f"delogo=x={x}:y={y}:w={w}:h={h}",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                        "-c:a", "copy", tmp], capture_output=True)
    if r.returncode == 0 and os.path.exists(tmp):
        os.replace(tmp, p)
        return True
    print("   ★실패:", r.stderr.decode("utf-8", "replace")[-200:])
    return False


if __name__ == "__main__":
    stills = sorted(glob.glob(f"{STILL}/bg_w23_*.png"))
    clips = sorted(glob.glob(f"{CLIPS}/bg_w23_*.mp4"))
    if "--check" in sys.argv:
        print("=== 정지 배경 워터마크 지수(0.02 넘으면 있음) ===")
        for p in stills:
            print(f"  {os.path.basename(p):32s} {has_watermark(p):.3f}")
        sys.exit(0)

    # ★Veo 산출물(배경 동영상 + 거기서 뽑은 정지)만 대상. 나노바나나 7장은 워터마크가 없다.
    VEO_KEYS = {"gate_in", "to_garden", "coaster_rush", "to_carousel", "parade_fills", "night_finale",
                "gate_plaza", "flower_path", "coaster_rail", "carousel_plaza", "parade_street"}
    stills = [p for p in stills
              if os.path.basename(p)[len("bg_w23_"):-4] in VEO_KEYS]

    os.makedirs(BAK, exist_ok=True)
    n = 0
    print("=== 정지 배경 ===")
    for p in stills:
        v = has_watermark(p)
        shutil.copy(p, f"{BAK}/{os.path.basename(p)}")
        fix_still(p)
        print(f"  ✅ {os.path.basename(p)} {v:.3f} → {has_watermark(p):.3f}")
        n += 1
    print("=== 배경 동영상 ===")
    for p in clips:
        shutil.copy(p, f"{BAK}/{os.path.basename(p)}")
        print(f"  {os.path.basename(p)} …", end=" ", flush=True)
        print("✅" if fix_clip(p) else "실패")
        n += 1
    print(f"\n총 {n}개 처리 · 원본 백업 → {BAK}")
