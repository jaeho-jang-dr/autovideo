# -*- coding: utf-8 -*-
"""
make_jieun_walk_3sec.py
지은이(cut2.png 외형 유지) 오른쪽으로 걸어가는 옆모습 걷기 비디오 생성 (3~4초, 고정 카메라, 흰색 단색 배경)
"""
import os
import subprocess
import numpy as np
from PIL import Image
from scipy import ndimage

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
OUT = "scratch/w19_walk"
TARGET_MP4 = os.path.join(OUT, "jieun_walk_video.mp4")

def cut_crop(path):
    a = np.array(Image.open(path).convert("RGBA"))
    rgb = a[:, :, :3].astype(int)
    lo = rgb.min(2)
    hi = rgb.max(2)
    white = (lo > 208) & ((hi - lo) < 26)
    lbl, _ = ndimage.label(white)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    a[np.isin(lbl, list(border)), 3] = 0
    H = a.shape[0]
    dark = (a[:, :, :3].max(2) < 90) & (a[:, :, 3] > 0)
    for y in range(int(H * 0.88), H):
        if dark[y].mean() > 0.5:
            a[y, :, 3] = 0
    pure = (a[:, :, 0] > 246) & (a[:, :, 1] > 246) & (a[:, :, 2] > 244)
    a[pure, 3] = 0
    ys, xs = np.where(a[:, :, 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

# Load keyframes (cut1, cut2, cut3)
raw = [cut_crop(f"{OUT}/cut{i}.png") for i in (1, 2, 3)]

# Normalize canvas height based on cut1
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
    ox = CW // 2 - hip
    oy = CH - fh - 6
    ox = max(0, min(ox, CW - fw))
    cv[oy:oy + fh, ox:ox + fw] = f
    reg.append(Image.fromarray(cv))

# Video parameters: 3.5 seconds duration, 24 fps -> 84 total frames
BW, BH = 1280, 720
FPS = 24
DURATION_SEC = 3.5
TOTAL_FRAMES = int(FPS * DURATION_SEC) # 84 frames

bg = Image.new("RGB", (BW, BH), (255, 255, 255)) # Solid white background
scale = int(BH * 0.60) / CH
cw2, ch2 = int(CW * scale), int(CH * scale)
regr = [p.resize((cw2, ch2), Image.Resampling.LANCZOS) for p in reg]

# Cycle 1-2-1-3 for walking leg alternating cross and arm swing
ORDER = [0, 1, 0, 2] # 4 poses per cycle
HOLD = 4 # Each pose held for 4 frames (at 24fps = 6 steps per second, smooth walk)

# Smooth rightward translation across fixed camera screen
x_start = int(BW * 0.15)
x_end = int(BW * 0.70)
foot_y = int(BH * 0.92) - ch2

tmp = f"{OUT}/_seq_jieun"
os.makedirs(tmp, exist_ok=True)
for fn in os.listdir(tmp):
    os.remove(os.path.join(tmp, fn))

for k in range(TOTAL_FRAMES):
    fr = bg.copy()
    progress = k / max(1, TOTAL_FRAMES - 1)
    x = int(x_start + (x_end - x_start) * progress)
    
    pose_idx = ORDER[(k // HOLD) % len(ORDER)]
    pose = regr[pose_idx]
    
    # Slight micro-bobbing for natural walking dynamics (vertical bounce)
    bob = int(np.sin(k * np.pi / HOLD) * 3)
    
    fr.paste(pose, (x, foot_y + bob), pose)
    fr.save(f"{tmp}/f{k:04d}.png")

# Compile to MP4 using ffmpeg
subprocess.run([
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", f"{tmp}/f%04d.png",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    TARGET_MP4
], check=True)

print(f"SUCCESS: {TARGET_MP4} ({DURATION_SEC} sec, {TOTAL_FRAMES} frames, {FPS} FPS)")
