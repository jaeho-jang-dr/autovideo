# -*- coding: utf-8 -*-
"""step_1(걷기1)·step_2(걷기2=다리미러) 두 컷을 1-2 교차 + 좌→오른쪽 이동 걷기 mp4.
사용: python walk_mirror_assemble.py
"""
import os, subprocess
from PIL import Image
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
OUT = "scratch/w19_walk"

s1 = Image.open(f"{OUT}/step_1.png").convert("RGBA")
s2 = Image.open(f"{OUT}/step_2.png").convert("RGBA")
CW = max(s1.width, s2.width); CH = max(s1.height, s2.height)

BW, BH = 1280, 720
bgp = "assets/graphics/bg/w19_bg_trail.png"
bg = Image.open(bgp).convert("RGB").resize((BW, BH)) if os.path.exists(bgp) else Image.new("RGB", (BW, BH), (234, 228, 214))
scale = int(BH * 0.55) / CH
cw2, ch2 = int(CW * scale), int(CH * scale)
poses = [s1.resize((cw2, ch2)), s2.resize((cw2, ch2))]

FPS = 12
HOLD = 5                       # 한 스텝 유지(≈0.42s)
STRIDE = int(cw2 * 0.40)       # 스텝당 전진(보폭)
x_start, x_end = -cw2, BW
steps = int((x_end - x_start) / STRIDE) + 1
nframes = steps * HOLD
foot_y = int(BH * 0.965) - ch2
tmp = f"{OUT}/_seqm"; os.makedirs(tmp, exist_ok=True)
for f in os.listdir(tmp): os.remove(os.path.join(tmp, f))
for k in range(nframes):
    fr = bg.copy()
    x = int(x_start + (x_end - x_start) * (k / max(1, nframes - 1)))
    pose = poses[(k // HOLD) % 2]
    fr.paste(pose, (x, foot_y), pose)
    fr.save(f"{tmp}/f{k:04d}.png")

out = f"{OUT}/walk_mirror.mp4"
subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"★ 미러 걷기 영상: {out}  ({nframes/FPS:.1f}초, {steps}스텝)")
