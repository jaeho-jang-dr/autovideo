# -*- coding: utf-8 -*-
"""걷기1(오른발 앞)·걷기2(왼발 앞) 2포즈 → 1-2-1-2 교차 + 왼→오른쪽 끝까지 이동 mp4.
사용: python walk2_assemble.py
"""
import os, subprocess
import numpy as np
from PIL import Image
from scipy import ndimage

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
SRC = "scratch/w19_walk/jieun_step2.png"
OUT = "scratch/w19_walk"


def cutout(arr):
    rgb = arr[:, :, :3].astype(int)
    lo = rgb.min(axis=2); hi = rgb.max(axis=2)
    white = (lo > 205) & ((hi - lo) < 28)
    lbl, n = ndimage.label(white)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1]); border.discard(0)
    arr[np.isin(lbl, list(border)), 3] = 0
    # 바닥선 제거(아래 14%에서 가로로 길게 이어진 어두운 줄)
    H = arr.shape[0]
    dark = (arr[:, :, :3].max(axis=2) < 90) & (arr[:, :, 3] > 0)
    for y in range(int(H * 0.85), H):
        if dark[y].mean() > 0.45: arr[y, :, 3] = 0
    # ★다리 사이 등 닫힌 순백 얼룩 제거(전역) — 크림 피부(약 240,232,218)는 보호되게 아주 흰 것만
    pure = (arr[:, :, 0] > 246) & (arr[:, :, 1] > 246) & (arr[:, :, 2] > 244)
    arr[pure, 3] = 0
    return arr


im = Image.open(SRC).convert("RGBA")
W = im.width
# 2칸 분리(가운데 divider 회피 위해 안쪽 여백)
halves = [np.array(im.crop((0, 0, W // 2, im.height))),
          np.array(im.crop((W // 2, 0, W, im.height)))]
figs = []
for h in halves:
    a = cutout(h)
    ys, xs = np.where(a[:, :, 3] > 0)
    figs.append(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1])

# 정합: 공통 캔버스, 발끝 하단 정렬, '상체(위 45%) 무게중심 x' 기준 가로 정렬(몸통 안정)
CW = max(f.shape[1] for f in figs) + 120
CH = max(f.shape[0] for f in figs) + 20
reg = []
for i, f in enumerate(figs):
    fh, fw = f.shape[:2]
    up = f[: int(fh * 0.45)]
    uy, ux = np.where(up[:, :, 3] > 0)
    anchor = int(ux.mean()) if len(ux) else fw // 2
    canvas = np.zeros((CH, CW, 4), np.uint8)
    ox = CW // 2 - anchor; oy = CH - fh - 6
    ox = max(0, min(ox, CW - fw))
    canvas[oy:oy + fh, ox:ox + fw] = f
    Image.fromarray(canvas).save(f"{OUT}/step_{i+1}.png")
    reg.append(Image.fromarray(canvas))
print(f"걷기1/걷기2 정합 완료 (캔버스 {CW}x{CH})")

# 조립: 배경 위, 1-2-1-2 교차 + 좌→우 끝까지
BW, BH = 1280, 720
bgp = "assets/graphics/bg/w19_bg_trail.png"
bg = Image.open(bgp).convert("RGB").resize((BW, BH)) if os.path.exists(bgp) else Image.new("RGB", (BW, BH), (236, 230, 216))
scale = int(BH * 0.55) / CH
cw2, ch2 = int(CW * scale), int(CH * scale)
regr = [p.resize((cw2, ch2)) for p in reg]

FPS = 12
HOLD = 5                 # 한 포즈 유지 프레임(≈0.42s/스텝 = 자연스러운 보행 리듬)
tmp = f"{OUT}/_seq2"; os.makedirs(tmp, exist_ok=True)
for f in os.listdir(tmp): os.remove(os.path.join(tmp, f))
x_start, x_end = -cw2, BW            # 왼편 밖 → 오른편 끝
# 한 스텝(HOLD프레임)당 stride만큼 전진하도록 총 프레임 산정
STRIDE = int(cw2 * 0.42)            # 스텝당 전진 거리(보폭)
steps = int((x_end - x_start) / STRIDE) + 1
nframes = steps * HOLD
foot_y = int(BH * 0.965) - ch2
for k in range(nframes):
    fr = bg.copy()
    x = int(x_start + (x_end - x_start) * (k / max(1, nframes - 1)))
    pose = regr[(k // HOLD) % 2]     # 1,2,1,2 교차
    fr.paste(pose, (x, foot_y), pose)
    fr.save(f"{tmp}/f{k:04d}.png")

out = f"{OUT}/walk2_across.mp4"
subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"★ 걷기 영상(1-2 교차, 좌→우 끝까지): {out}  ({nframes/FPS:.1f}초, {steps}스텝)")
