# -*- coding: utf-8 -*-
"""
Generate 8-frame walk cycle for Injun character.
Uses injun_w16_walk_r1.png and injun_w16_walk_r2.png with passing poses.
"""

import os
import glob
import math
import numpy as np
from PIL import Image, ImageChops

POSE_DIR = r"D:\Entertainments\DevEnvironment\autovideo\assets\graphics\poses"
OUT_DIR = r"D:\Entertainments\DevEnvironment\autovideo\scratch\injun_active_walk"
os.makedirs(OUT_DIR, exist_ok=True)

def load_and_crop(path):
    im = Image.open(path).convert("RGBA")
    arr = np.array(im)
    ys, xs = np.where(arr[:, :, 3] > 10)
    if len(ys) == 0:
        return im
    crop = arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray(crop)

img_r1 = load_and_crop(os.path.join(POSE_DIR, "injun_w16_walk_r1.png"))
img_r2 = load_and_crop(os.path.join(POSE_DIR, "injun_w16_walk_r2.png"))

print(f"r1 size: {img_r1.size}, r2 size: {img_r2.size}")

# Standardize height
target_h = 520
scale_r1 = target_h / img_r1.height
scale_r2 = target_h / img_r2.height

r1_res = img_r1.resize((int(img_r1.width * scale_r1), target_h), Image.Resampling.LANCZOS)
r2_res = img_r2.resize((int(img_r2.width * scale_r2), target_h), Image.Resampling.LANCZOS)

# Create 8 walk cycle poses
# 0: Contact R1
# 1: Down R1
# 2: Passing R1->R2
# 3: Up R1->R2
# 4: Contact R2
# 5: Down R2
# 6: Passing R2->R1
# 7: Up R2->R1

canvas_w = 600
canvas_h = 600

def place_centered(img, offset_x=0, offset_y=0):
    cv = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    ox = (canvas_w - img.width) // 2 + offset_x
    oy = canvas_h - img.height - 20 + offset_y
    cv.paste(img, (ox, oy), img)
    return cv

def create_passing_pose(img_a, img_b, alpha_ratio=0.5, bob_y=-8, scale_w=0.92):
    # Blend images and apply narrow width / vertical bob for passing stance
    w_new = int(img_a.width * scale_w)
    h_new = int(img_a.height * 1.02)
    
    a_scaled = img_a.resize((w_new, h_new), Image.Resampling.LANCZOS)
    b_scaled = img_b.resize((w_new, h_new), Image.Resampling.LANCZOS)
    
    blended = Image.blend(a_scaled, b_scaled, alpha_ratio)
    return blended, bob_y

poses = []

# Pose 0: Contact R1 (Left leg forward, right leg back)
poses.append(place_centered(r1_res, offset_x=0, offset_y=0))

# Pose 1: Down R1
p1_img, p1_bob = create_passing_pose(r1_res, r2_res, alpha_ratio=0.25, bob_y=4, scale_w=0.96)
poses.append(place_centered(p1_img, offset_x=2, offset_y=p1_bob))

# Pose 2: Passing R1->R2 (Legs crossing)
p2_img, p2_bob = create_passing_pose(r1_res, r2_res, alpha_ratio=0.5, bob_y=-6, scale_w=0.90)
poses.append(place_centered(p2_img, offset_x=4, offset_y=p2_bob))

# Pose 3: Up R1->R2
p3_img, p3_bob = create_passing_pose(r1_res, r2_res, alpha_ratio=0.75, bob_y=-10, scale_w=0.94)
poses.append(place_centered(p3_img, offset_x=2, offset_y=p3_bob))

# Pose 4: Contact R2 (Right leg forward, left leg back)
poses.append(place_centered(r2_res, offset_x=0, offset_y=0))

# Pose 5: Down R2
p5_img, p5_bob = create_passing_pose(r2_res, r1_res, alpha_ratio=0.25, bob_y=4, scale_w=0.96)
poses.append(place_centered(p5_img, offset_x=-2, offset_y=p5_bob))

# Pose 6: Passing R2->R1 (Legs crossing)
p6_img, p6_bob = create_passing_pose(r2_res, r1_res, alpha_ratio=0.5, bob_y=-6, scale_w=0.90)
poses.append(place_centered(p6_img, offset_x=-4, offset_y=p6_bob))

# Pose 7: Up R2->R1
p7_img, p7_bob = create_passing_pose(r2_res, r1_res, alpha_ratio=0.75, bob_y=-10, scale_w=0.94)
poses.append(place_centered(p7_img, offset_x=-2, offset_y=p7_bob))

# Save pose contact sheet for inspection
contact = Image.new("RGBA", (canvas_w * 8, canvas_h), (240, 240, 240, 255))
for idx, p in enumerate(poses):
    p.save(os.path.join(OUT_DIR, f"pose_{idx}.png"))
    contact.paste(p, (idx * canvas_w, 0), p)

contact.save(os.path.join(OUT_DIR, "walk_cycle_contact_sheet.png"))
print("Generated 8 walk cycle pose files in scratch/injun_active_walk")
