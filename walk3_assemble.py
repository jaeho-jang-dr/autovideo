# -*- coding: utf-8 -*-
"""컷1(모음)·컷2(앞다리 앞)·컷3(앞다리 뒤) → 1-2-1-3 순환 + 좌→우 이동 걷기.
사용: python walk3_assemble.py
"""
import os, subprocess
import numpy as np
from PIL import Image
from scipy import ndimage
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
OUT = "scratch/w19_walk"


def cut_crop(path):
    a = np.array(Image.open(path).convert("RGBA"))
    rgb = a[:, :, :3].astype(int); lo = rgb.min(2); hi = rgb.max(2)
    white = (lo > 208) & ((hi - lo) < 26)
    lbl, _ = ndimage.label(white)
    b = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1]); b.discard(0)
    a[np.isin(lbl, list(b)), 3] = 0
    H = a.shape[0]
    dark = (a[:, :, :3].max(2) < 90) & (a[:, :, 3] > 0)
    for y in range(int(H * 0.88), H):
        if dark[y].mean() > 0.5: a[y, :, 3] = 0
    pure = (a[:, :, 0] > 246) & (a[:, :, 1] > 246) & (a[:, :, 2] > 244); a[pure, 3] = 0
    ys, xs = np.where(a[:, :, 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


raw = [cut_crop(f"{OUT}/cut{i}.png") for i in (1, 2, 3)]
# 크기 정규화: 몸높이(bbox height) 같게(컷1 기준)
TH = raw[0].shape[0]
figs = []
for f in raw:
    r = TH / f.shape[0]
    figs.append(np.array(Image.fromarray(f).resize((max(1, int(f.shape[1] * r)), TH))))

CW = max(f.shape[1] for f in figs) + 160
CH = max(f.shape[0] for f in figs) + 16
reg = []
for i, f in enumerate(figs):
    fh, fw = f.shape[:2]
    band = f[int(fh * 0.50):int(fh * 0.60)]
    by, bx = np.where(band[:, :, 3] > 0)
    hip = int(bx.mean()) if len(bx) else fw // 2
    cv = np.zeros((CH, CW, 4), np.uint8)
    ox = CW // 2 - hip; oy = CH - fh - 6
    ox = max(0, min(ox, CW - fw)); cv[oy:oy + fh, ox:ox + fw] = f
    Image.fromarray(cv).save(f"{OUT}/w3_{i+1}.png")
    reg.append(Image.fromarray(cv))
print(f"3컷 정합 {CW}x{CH}")

BW, BH = 1280, 720
bg = Image.new("RGB", (BW, BH), (234, 228, 214))
scale = int(BH * 0.55) / CH
cw2, ch2 = int(CW * scale), int(CH * scale)
regr = [p.resize((cw2, ch2)) for p in reg]
ORDER = [0, 1, 0, 2]          # 1-2-1-3
FPS = 12; HOLD = 4
cycle = len(ORDER) * HOLD
stride_per_cycle = cw2 * 0.6
x_start, x_end = -cw2, BW
nframes = int((x_end - x_start) / stride_per_cycle * cycle)
foot_y = int(BH * 0.965) - ch2
tmp = f"{OUT}/_seq3"; os.makedirs(tmp, exist_ok=True)
for fn in os.listdir(tmp): os.remove(os.path.join(tmp, fn))
for k in range(nframes):
    fr = bg.copy()
    x = int(x_start + (x_end - x_start) * (k / max(1, nframes - 1)))
    pose = regr[ORDER[(k // HOLD) % len(ORDER)]]
    fr.paste(pose, (x, foot_y), pose)
    fr.save(f"{tmp}/f{k:04d}.png")
out = f"{OUT}/walk3.mp4"
subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"★ 1-2-1-3 걷기: {out} ({nframes/FPS:.1f}초)")
