# -*- coding: utf-8 -*-
"""
Render active Injun walking video for W20_package/injun_walk.mp4
Guarantees:
- 8.0 seconds duration (192 frames @ 24fps)
- 1280x720 HD resolution
- Pure solid white background (RGB 255, 255, 255)
- Fixed camera
- Feet touch ground line
- Active continuous walk cycle with alternating leg strides and swinging arms
"""

import os
import glob
import subprocess
import numpy as np
from PIL import Image

BASE_DIR = r"D:\Entertainments\DevEnvironment\autovideo"
POSE_DIR = os.path.join(BASE_DIR, r"scratch\injun_active_walk")
OUT_PKG = os.path.join(BASE_DIR, "W20_package")
OUT_MP4 = os.path.join(OUT_PKG, "injun_walk.mp4")
FRAME_DIR = os.path.join(BASE_DIR, r"scratch\injun_render_frames")

os.makedirs(OUT_PKG, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)

# Clean frame dir
for f in glob.glob(os.path.join(FRAME_DIR, "*.png")):
    try: os.remove(f)
    except: pass

# Load the 8 pose images
poses = []
for i in range(8):
    p_path = os.path.join(POSE_DIR, f"pose_{i}.png")
    poses.append(Image.open(p_path).convert("RGBA"))

CANVAS_W = 1280
CANVAS_H = 720
FPS = 24
DURATION_SEC = 8.0
TOTAL_FRAMES = int(DURATION_SEC * FPS) # 192 frames

# Pure solid white background
BG_WHITE = Image.new("RGB", (CANVAS_W, CANVAS_H), (255, 255, 255))

# Scale poses for 720p canvas
# Target character height = ~500px (~70% of 720)
target_h = 500
scaled_poses = []
for p in poses:
    sc = target_h / p.height
    w_sc = int(p.width * sc)
    scaled_poses.append(p.resize((w_sc, target_h), Image.Resampling.LANCZOS))

# Ground line: feet touch Y = 670
ground_foot_y = 670 - target_h

# Travel from left (-200) to right (1100) across 192 frames
start_x = -180
end_x = 1120
total_dist = end_x - start_x

# Walk stride rate: 2.0 full walk cycles (16 steps) per second = 16 cycles across 8 seconds
# 192 frames / 16 cycles = 12 frames per cycle (1.5 frames per pose index)
POSES_PER_SEC = 16.0

print(f"Rendering {TOTAL_FRAMES} frames...")
for f_idx in range(TOTAL_FRAMES):
    t = f_idx / (TOTAL_FRAMES - 1) # 0.0 to 1.0
    
    # Position X moves smoothly from left to right
    curr_x = int(start_x + total_dist * t)
    
    # Active cycle index
    pose_idx = int((f_idx * POSES_PER_SEC / FPS)) % len(scaled_poses)
    curr_pose = scaled_poses[pose_idx]
    
    # Composite over pure white canvas
    frame = BG_WHITE.copy()
    frame.paste(curr_pose, (curr_x, ground_foot_y), curr_pose)
    
    frame.save(os.path.join(FRAME_DIR, f"frame_{f_idx:04d}.png"))

print(f"Frames rendered. Encoding to {OUT_MP4} via FFmpeg...")

cmd_ffmpeg = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(FRAME_DIR, "frame_%04d.png"),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    OUT_MP4
]
subprocess.run(cmd_ffmpeg, check=True)

print("FFmpeg encoding complete!")

# Verify probe metadata
cmd_probe = [
    "ffprobe", "-v", "error",
    "-select_streams", "v:0",
    "-show_entries", "stream=width,height,duration,r_frame_rate",
    "-show_entries", "format=duration,size",
    "-of", "default=noprint_wrappers=1",
    OUT_MP4
]
res = subprocess.run(cmd_probe, capture_output=True, text=True)
print("=== Final MP4 Metadata ===")
print(res.stdout)
