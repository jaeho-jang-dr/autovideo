# -*- coding: utf-8 -*-
"""8프레임 걷기 시트 → 정확히 8컷 분리 → 엉덩이 기준 정합 → 순서대로 순환 + 좌→우 이동.
사용: python walk8_proper.py
"""
import os, subprocess
import numpy as np
from PIL import Image
from scipy import ndimage
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
SHEET = "scratch/w19_walk/jieun_walk_sheet.png"
OUT = "scratch/w19_walk"


def cutout(arr):
    rgb = arr[:, :, :3].astype(int); lo = rgb.min(axis=2); hi = rgb.max(axis=2)
    white = (lo > 205) & ((hi - lo) < 28)
    lbl, n = ndimage.label(white)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1]); border.discard(0)
    arr[np.isin(lbl, list(border)), 3] = 0
    H = arr.shape[0]
    dark = (arr[:, :, :3].max(axis=2) < 90) & (arr[:, :, 3] > 0)
    for y in range(int(H * 0.86), H):
        if dark[y].mean() > 0.45: arr[y, :, 3] = 0
    pure = (arr[:, :, 0] > 246) & (arr[:, :, 1] > 246) & (arr[:, :, 2] > 244)
    arr[pure, 3] = 0
    return arr


arr = cutout(np.array(Image.open(SHEET).convert("RGBA")))
H, W = arr.shape[:2]
# 8칸 경계 = 예상경계 ±35%에서 최소밀도 열
N = 8
colmass = (arr[: int(H * 0.8), :, 3] > 0).sum(axis=0).astype(float)
cuts = [0]
for i in range(1, N):
    c = int(W * i / N); win = int(W / N * 0.35)
    a, b = max(cuts[-1] + 5, c - win), min(W - 1, c + win)
    cuts.append(a + int(np.argmin(colmass[a:b])) if b > a else c)
cuts.append(W)

figs = []
for i in range(N):
    sub = arr[:, cuts[i]:cuts[i + 1]]
    ys, xs = np.where(sub[:, :, 3] > 0)
    if len(ys) == 0: continue
    figs.append(sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1])

# 정합: 엉덩이(높이 55% 밴드) 중심 x + 발끝 하단 정렬
CW = max(f.shape[1] for f in figs) + 100
CH = max(f.shape[0] for f in figs) + 16
reg = []
for i, f in enumerate(figs):
    fh, fw = f.shape[:2]
    band = f[int(fh * 0.50):int(fh * 0.60)]      # 엉덩이 밴드
    by, bx = np.where(band[:, :, 3] > 0)
    hip_cx = int(bx.mean()) if len(bx) else fw // 2
    canvas = np.zeros((CH, CW, 4), np.uint8)
    ox = CW // 2 - hip_cx; oy = CH - fh - 6
    ox = max(0, min(ox, CW - fw))
    canvas[oy:oy + fh, ox:ox + fw] = f
    Image.fromarray(canvas).save(f"{OUT}/w8_{i}.png")
    reg.append(Image.fromarray(canvas))
print(f"8컷 정합 완료 (캔버스 {CW}x{CH}, {len(reg)}컷)")

# 컨택트시트(검증)
cs = Image.new("RGB", (CW * len(reg), CH), (245, 245, 245))
for i, p in enumerate(reg): cs.paste(p, (i * CW, 0), p)
cs.save(f"{OUT}/w8_contact.png")

# 조립: 배경 위, 8컷 순환(각 2프레임 유지) + 좌→우 이동
BW, BH = 1280, 720
bg = Image.new("RGB", (BW, BH), (234, 228, 214))
scale = int(BH * 0.55) / CH
cw2, ch2 = int(CW * scale), int(CH * scale)
regr = [p.resize((cw2, ch2)) for p in reg]
FPS = 12; HOLD = 2
# 한 사이클(8컷=16프레임 with HOLD)에 두 보폭 전진 → cw2*0.5
cycle_frames = len(reg) * HOLD
stride_per_cycle = cw2 * 0.55
x_start, x_end = -cw2, BW
total_dist = x_end - x_start
cycles = total_dist / stride_per_cycle
nframes = int(cycles * cycle_frames)
foot_y = int(BH * 0.965) - ch2
tmp = f"{OUT}/_seq8"; os.makedirs(tmp, exist_ok=True)
for fn in os.listdir(tmp): os.remove(os.path.join(tmp, fn))
for k in range(nframes):
    fr = bg.copy()
    x = int(x_start + total_dist * (k / max(1, nframes - 1)))
    pose = regr[(k // HOLD) % len(regr)]
    fr.paste(pose, (x, foot_y), pose)
    fr.save(f"{tmp}/f{k:04d}.png")
out = f"{OUT}/walk8.mp4"
subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"★ 8프레임 걷기: {out} ({nframes/FPS:.1f}초)")
