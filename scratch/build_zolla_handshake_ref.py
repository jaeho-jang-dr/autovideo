# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
from PIL import Image, ImageChops
from collections import deque

# Add root directory to python path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# Force UTF-8 encoding for standard outputs
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

MAN_PATH = os.path.join(ROOT, "home_vocab", "zollaman_base.png")
WOMAN_PATH = os.path.join(ROOT, "home_vocab", "zollanyeo_base.png")
OUT_REF_PATH = os.path.join(ROOT, "home_vocab", "zolla_handshake_ref.png")

def trim_and_transparentize(in_path, out_path, tol=28, thr=20):
    """
    Trims the white borders around the character, then flood-fills the white background
    to make it transparent. Saves the resulting image to out_path.
    """
    # 1. Trim the extra white border
    im = Image.open(in_path).convert("RGB")
    bg_img = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg_img).convert("L").point(lambda x: 255 if x > thr else 0)
    bbox = diff.getbbox()
    trimmed = im.crop(bbox) if bbox else im
    
    # 2. Transparentize using flood fill from corners
    img_rgba = trimmed.convert("RGBA")
    arr = np.array(img_rgba)
    h, w = arr.shape[:2]
    rgb = arr[:, :, :3].astype(int)
    
    # Corners to estimate background color
    corners = np.array([
        rgb[0, 0], rgb[0, w - 1], rgb[h - 1, 0], rgb[h - 1, w - 1]
    ])
    bg_color = np.median(corners, axis=0)
    
    seen = np.zeros((h, w), dtype=bool)
    out_alpha = arr[:, :, 3].copy()
    dq = deque([(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)])
    
    while dq:
        y, x = dq.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y, x]:
            continue
        seen[y, x] = True
        # If the pixel color is too different from the background, stop flood fill
        if np.abs(rgb[y, x] - bg_color).max() > tol:
            continue
        out_alpha[y, x] = 0
        dq.append((y + 1, x))
        dq.append((y - 1, x))
        dq.append((y, x + 1))
        dq.append((y, x - 1))
        
    arr[:, :, 3] = out_alpha
    final_img = Image.fromarray(arr, "RGBA")
    final_img.save(out_path)
    print(f"Processed: {os.path.basename(in_path)} -> {os.path.basename(out_path)} (size: {final_img.size})")
    return final_img.size

def main():
    print("Step 1: Trimming and transparentizing stickman base images...")
    tmp_man = os.path.join(ROOT, "home_vocab", "_tmp_man_trans.png")
    tmp_woman = os.path.join(ROOT, "home_vocab", "_tmp_woman_trans.png")
    tmp_bg = os.path.join(ROOT, "home_vocab", "_tmp_white_bg.png")
    
    w_m, h_m = trim_and_transparentize(MAN_PATH, tmp_man)
    w_w, h_w = trim_and_transparentize(WOMAN_PATH, tmp_woman)
    
    # Create white background image of size 1024x1024
    canvas_w, canvas_h = 1024, 1024
    Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255)).save(tmp_bg)
    
    print("\nStep 2: Composing images using MoviePy...")
    from moviepy import ImageClip, CompositeVideoClip
    
    # Load clips
    bg_clip = ImageClip(tmp_bg).with_duration(1)
    
    # We want to scale them to a height of 700 pixels, keeping their aspect ratio.
    target_h = 700
    
    man_clip = ImageClip(tmp_man).with_duration(1)
    woman_clip = ImageClip(tmp_woman).with_duration(1)
    
    # Calculate resized sizes
    man_resized_w = int(w_m * (target_h / h_m))
    woman_resized_w = int(w_w * (target_h / h_w))
    
    # Resize clips in MoviePy 2.x
    man_clip = man_clip.resized(height=target_h)
    woman_clip = woman_clip.resized(height=target_h)
    
    # Center them horizontally, very close to each other.
    # Gap between them: 30 pixels (close to each other)
    gap = 30
    total_w = man_resized_w + gap + woman_resized_w
    start_x = (canvas_w - total_w) / 2
    
    man_x = start_x
    woman_x = start_x + man_resized_w + gap
    
    # Center them vertically
    y_pos = (canvas_h - target_h) / 2
    
    print(f"Placing Zollaman at X={man_x:.1f}, Y={y_pos:.1f} (width={man_resized_w})")
    print(f"Placing Zollanyeo at X={woman_x:.1f}, Y={y_pos:.1f} (width={woman_resized_w})")
    
    man_clip = man_clip.with_position((man_x, y_pos))
    woman_clip = woman_clip.with_position((woman_x, y_pos))
    
    # Composite
    composite = CompositeVideoClip([bg_clip, man_clip, woman_clip], size=(canvas_w, canvas_h))
    
    # Save the frame at t=0
    composite.save_frame(OUT_REF_PATH, t=0)
    print(f"\n[SUCCESS] Composed reference image saved to: {OUT_REF_PATH}")
    
    # Clean up temp files
    for p in (tmp_man, tmp_woman, tmp_bg):
        try:
            os.remove(p)
        except Exception:
            pass
            
if __name__ == "__main__":
    main()
