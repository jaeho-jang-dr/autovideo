# -*- coding: utf-8 -*-
"""정지 포즈 후처리: 신발 흰색화(외곽선 제외 전체) + 회색 팔→핑크(대형 무채색 영역만)."""
import sys, io, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import numpy as np
from PIL import Image
from scipy import ndimage
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
FEET_Y, BODY = 1209, 770

# 핑크 샘플(explain 가디건)
_pe = np.array(Image.open("assets/graphics/poses/jieun_w22_explain.png").convert("RGBA"))
_r = _pe[:, :, :3].astype(int); _a = _pe[:, :, 3] > 0
_pk = _a & (_r[:, :, 0] > 210) & (_r[:, :, 0] - _r[:, :, 2] > 15) & (_r[:, :, 0] - _r[:, :, 1] > 25) & (_r[:, :, 2] > 160)
PINK = _r[_pk].mean(0).round().astype(int) if _pk.sum() else np.array([236, 176, 192])
print("PINK target", PINK)


def shoe_white(rgba):
    a = rgba[:, :, 3] > 0
    rgb = rgba[:, :, :3].astype(int); lo = rgb.min(2); hi = rgb.max(2)
    yy = np.arange(rgba.shape[0])[:, None]
    foot = a & (yy > (FEET_Y - 0.14 * BODY))
    shoe = foot & (lo > 70) & ((hi - lo) < 42)     # 외곽선(어두움<70)만 남기고 회색·밝은 부분 흰색화
    for c, v in enumerate((250, 250, 250)):
        rgba[:, :, c][shoe] = v
    return rgba


def arm_pink(rgba):
    a = rgba[:, :, 3] > 0
    rgb = rgba[:, :, :3].astype(int); lo = rgb.min(2); hi = rgb.max(2)
    yy = np.arange(rgba.shape[0])[:, None]
    body = a & (yy > FEET_Y - BODY * 0.98) & (yy < FEET_Y - BODY * 0.14)   # 몸통~팔(신발/머리위 제외)
    gray = body & (lo >= 70) & (lo <= 200) & ((hi - lo) < 26)              # 무채색 회색(팔소매)
    # 대형 연결영역만(팔) — 작은 회색(폰·명찰글자)은 제외
    lbl, n = ndimage.label(gray)
    if n:
        sizes = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
        big = {i + 1 for i, s in enumerate(sizes) if s > 1500}
        armmask = np.isin(lbl, list(big)) if big else np.zeros_like(gray)
        rgba[:, :, 0][armmask] = PINK[0]; rgba[:, :, 1][armmask] = PINK[1]; rgba[:, :, 2][armmask] = PINK[2]
        print("  arm gray→pink px", int(armmask.sum()))
    return rgba


ARM_FIX = {"heart", "think_recall", "phone_tap", "bag_ready"}
for f in sorted(glob.glob("assets/graphics/poses/jieun_w22_*.png")):
    pose = os.path.basename(f).replace("jieun_w22_", "").replace(".png", "")
    if pose not in {"explain", "present_right", "present_left", "think_recall", "shake", "phone_tap", "count_two", "bag_ready", "heart"}:
        continue
    rgba = np.array(Image.open(f).convert("RGBA"))
    rgba = shoe_white(rgba)
    if pose in ARM_FIX:
        print(pose)
        rgba = arm_pink(rgba)
    Image.fromarray(rgba).save(f)
print("완료: 신발 흰색화(전체) + 팔 핑크(heart/think_recall/phone_tap/bag_ready)")
