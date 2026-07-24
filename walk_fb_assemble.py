# -*- coding: utf-8 -*-
"""걷기1(step_1) + 걷기2(제미나이 전후미러 jieun_step2_fb) → 크기정규화·정합 → 1-2 교차 + 좌→우 걷기.
사용: python walk_fb_assemble.py
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
    white = (lo > 210) & ((hi - lo) < 26)
    lbl, _ = ndimage.label(white)
    b = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1]); b.discard(0)
    a[np.isin(lbl, list(b)), 3] = 0
    H = a.shape[0]
    dark = (a[:, :, :3].max(2) < 90) & (a[:, :, 3] > 0)
    for y in range(int(H * 0.86), H):
        if dark[y].mean() > 0.45: a[y, :, 3] = 0
    pure = (a[:, :, 0] > 246) & (a[:, :, 1] > 246) & (a[:, :, 2] > 244); a[pure, 3] = 0
    ys, xs = np.where(a[:, :, 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


f1 = cut_crop(f"{OUT}/step_1.png")
f2 = cut_crop(f"{OUT}/jieun_step2_fb.png")
# 크기 정규화: 두 컷 몸높이(bbox height)를 같게 → f2를 f1 높이에 맞춤
TH = f1.shape[0]
r = TH / f2.shape[0]
f2i = Image.fromarray(f2).resize((max(1, int(f2.shape[1] * r)), TH)); f2 = np.array(f2i)
figs = [f1, f2]

# 정합: 엉덩이(55%밴드) 중심 x + 발끝 하단
CW = max(f.shape[1] for f in figs) + 120
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
    Image.fromarray(cv).save(f"{OUT}/fb_{i+1}.png")
    reg.append(Image.fromarray(cv))
print(f"정합 완료 {CW}x{CH}")

BW, BH = 1280, 720
bg = Image.new("RGB", (BW, BH), (234, 228, 214))
scale = int(BH * 0.55) / CH
cw2, ch2 = int(CW * scale), int(CH * scale)
regr = [p.resize((cw2, ch2)) for p in reg]
FPS = 12; HOLD = 5
STRIDE = int(cw2 * 0.40)
x_start, x_end = -cw2, BW
steps = int((x_end - x_start) / STRIDE) + 1
nframes = steps * HOLD
foot_y = int(BH * 0.965) - ch2
tmp = f"{OUT}/_seqfb"; os.makedirs(tmp, exist_ok=True)
for fn in os.listdir(tmp): os.remove(os.path.join(tmp, fn))
for k in range(nframes):
    fr = bg.copy()
    x = int(x_start + (x_end - x_start) * (k / max(1, nframes - 1)))
    fr.paste(regr[(k // HOLD) % 2], (x, foot_y), regr[(k // HOLD) % 2])
    fr.save(f"{tmp}/f{k:04d}.png")
out = f"{OUT}/walk_fb.mp4"
subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"★ 전후미러 걷기: {out} ({nframes/FPS:.1f}초)")
