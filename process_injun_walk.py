# -*- coding: utf-8 -*-
"""
Process and finalize Injun walk video for W20_package.
Requirements:
- Character: Injun (from reference image D:\Entertainments\DevEnvironment\autovideo\home_vocab\injun_base_side.png)
- Full side profile (완전한 옆모습)
- Natural walk cycle (자연스러운 걷기 사이클)
- Flat cartoon style maintained (플랫 카툰 스타일 유지)
- Pure solid white background (순수한 흰색 단색 배경: RGB(255,255,255))
- Fixed camera (카메라 고정)
- Feet touch ground (발이 바닥에 닿음)
- Duration: 8.0 seconds
- Output path: D:\Entertainments\DevEnvironment\autovideo\W20_package\injun_walk.mp4
"""

import os
import sys
import glob
import numpy as np
import subprocess
from PIL import Image
from scipy import ndimage

def process_veo_video_or_keyframes(veo_mp4_path, out_mp4_path, target_duration=8.0):
    print(f"Processing input video: {veo_mp4_path}")
    os.makedirs(os.path.dirname(out_mp4_path), exist_ok=True)
    
    # Extract frames from video
    temp_dir = r"D:\Entertainments\DevEnvironment\autovideo\scratch\injun_process_frames"
    os.makedirs(temp_dir, exist_ok=True)
    for f in glob.glob(os.path.join(temp_dir, "*.png")):
        try: os.remove(f)
        except: pass
        
    cmd_extract = [
        "ffmpeg", "-y", "-i", veo_mp4_path,
        "-vf", "fps=24",
        os.path.join(temp_dir, "frame_%04d.png")
    ]
    subprocess.run(cmd_extract, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    frame_files = sorted(glob.glob(os.path.join(temp_dir, "frame_*.png")))
    print(f"Extracted {len(frame_files)} frames from Veo video.")
    
    if not frame_files:
        raise RuntimeError("No frames extracted from Veo video.")
        
    # Read first frame to get canvas resolution
    sample_img = Image.open(frame_files[0])
    W, H = sample_img.size
    print(f"Original resolution: {W}x{H}")
    
    # Process frames: turn any off-white/gray background into pure #FFFFFF white (RGB 255,255,255)
    processed_dir = os.path.join(temp_dir, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    # Find walk cycle or loop frames to fit exactly target_duration (e.g. 8.0s * 24fps = 192 frames)
    target_frames_count = int(target_duration * 24)
    
    # Process images to enforce pure solid white background
    raw_images = []
    for fpath in frame_files:
        img = Image.open(fpath).convert("RGB")
        arr = np.array(img, dtype=np.uint8)
        # Background thresholding: pixels near white (R>220, G>220, B>220 and max-min difference small) -> 255,255,255
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        is_bg = (r > 215) & (g > 215) & (b > 215) & (np.abs(r.astype(int) - g.astype(int)) < 30) & (np.abs(g.astype(int) - b.astype(int)) < 30)
        
        # Also clean isolated border artifacts
        arr[is_bg] = [255, 255, 255]
        raw_images.append(Image.fromarray(arr))
        
    # If the Veo video is shorter than 8s, seamlessly tile/loop or adjust speed/loop to reach exactly 8.0s (192 frames)
    final_frames = []
    num_raw = len(raw_images)
    
    if num_raw >= target_frames_count:
        final_frames = raw_images[:target_frames_count]
    else:
        # Loop frames smoothly
        for i in range(target_frames_count):
            final_frames.append(raw_images[i % num_raw])
            
    # Save final frames
    for i, img in enumerate(final_frames):
        img.save(os.path.join(processed_dir, f"out_{i:04d}.png"))
        
    # Encode with ffmpeg to target mp4
    cmd_encode = [
        "ffmpeg", "-y",
        "-framerate", "24",
        "-i", os.path.join(processed_dir, "out_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        out_mp4_path
    ]
    subprocess.run(cmd_encode, check=True)
    
    # Verify resulting video
    cmd_probe = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration,nb_frames",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1",
        out_mp4_path
    ]
    res = subprocess.run(cmd_probe, capture_output=True, text=True)
    print("Final Video Info:\n", res.stdout)
    return out_mp4_path

if __name__ == "__main__":
    veo_input = r"D:\Entertainments\DevEnvironment\autovideo\scratch_injun_prompts\scene_1.mp4"
    out_target = r"D:\Entertainments\DevEnvironment\autovideo\W20_package\injun_walk.mp4"
    if os.path.exists(veo_input):
        process_veo_video_or_keyframes(veo_input, out_target)
    else:
        print(f"Input {veo_input} does not exist yet.")
