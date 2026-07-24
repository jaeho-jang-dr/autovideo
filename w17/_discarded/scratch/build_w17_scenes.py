# -*- coding: utf-8 -*-
import os
import sys
import shutil
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG_DIR = os.path.join(ROOT, "w17", "backgrounds")
CHAR_DIR = os.path.join(ROOT, "assets", "characters")
OUT_DIR = os.path.join(ROOT, "w17")

# 48씬 매핑 정보 (W17 Advanced Course - 검증된 포즈 & 불국사 10종 배경 전용 롤백판)
SCENE_MAP = {
    0: {"bg": "w17_bg_entrance", "pose": "waving", "pos": "right"},
    1: {"bg": "w17_bg_entrance", "pose": "waving", "pos": "right"},
    2: {"bg": "w17_bg_temple_valley", "pose": "explaining", "pos": "right"},
    3: {"bg": "w17_bg_temple_valley", "pose": "thinking", "pos": "right"},
    4: {"bg": "w17_bg_entrance", "pose": "explaining", "pos": "right"},
    5: {"bg": "w17_bg_stairs_far", "pose": "pointing_right", "pos": "left"},
    6: {"bg": "w17_bg_stairs_far", "pose": "cheering", "pos": "right"},
    7: {"bg": "w17_bg_stairs_close", "pose": "explaining", "pos": "right"},
    8: {"bg": "w17_bg_stairs_close", "pose": "explaining", "pos": "right"},
    9: {"bg": "w17_bg_stairs_close", "pose": "explaining", "pos": "right"},
    10: {"bg": "w17_bg_stairs_close", "pose": "thinking", "pos": "right"},
    11: {"bg": "w17_bg_dancheong", "pose": "explaining", "pos": "right"},
    12: {"bg": "w17_bg_dancheong", "pose": "thinking", "pos": "right"},
    13: {"bg": "w17_bg_dancheong", "pose": "explaining", "pos": "right"},
    14: {"bg": "w17_bg_dancheong", "pose": "thinking", "pos": "right"},
    15: {"bg": "w17_bg_entrance", "pose": "explaining", "pos": "right"},
    16: {"bg": "w17_bg_entrance", "pose": "thinking", "pos": "right"},
    17: {"bg": "w17_bg_stairs_far", "pose": "explaining", "pos": "right"},
    18: {"bg": "w17_bg_stairs_far", "pose": "thinking", "pos": "right"},
    19: {"bg": "w17_bg_stairs_close", "pose": "explaining", "pos": "right"},
    20: {"bg": "w17_bg_stairs_close", "pose": "thinking", "pos": "right"},
    21: {"bg": "w17_bg_stairs_close", "pose": "explaining", "pos": "right"},
    22: {"bg": "w17_bg_dancheong", "pose": "explaining", "pos": "right"},
    23: {"bg": "w17_bg_dancheong", "pose": "explaining", "pos": "right"},
    24: {"bg": "w17_bg_dancheong", "pose": "explaining", "pos": "right"},
    25: {"bg": "w17_bg_dancheong", "pose": "explaining", "pos": "right"},
    26: {"bg": "w17_bg_dancheong", "pose": "explaining", "pos": "right"},
    27: {"bg": "w17_bg_courtyard", "pose": "cheering", "pos": "right"},
    28: {"bg": "w17_bg_courtyard", "pose": "explaining", "pos": "right"},
    29: {"bg": "w17_bg_temple_valley", "pose": "cheering", "pos": "right"},
    30: {"bg": "w17_bg_temple_valley", "pose": "explaining", "pos": "right"},
    31: {"bg": "w17_bg_garden", "pose": "thinking", "pos": "right"},
    32: {"bg": "w17_bg_garden", "pose": "thinking", "pos": "right"},
    33: {"bg": "w17_bg_entrance", "pose": "pointing_left", "pos": "right"},
    34: {"bg": "w17_bg_entrance", "pose": "cheering", "pos": "right"},
    35: {"bg": "w17_bg_dancheong", "pose": "waving", "pos": "right"},
    36: {"bg": "w17_bg_dancheong", "pose": "explaining", "pos": "right"},
    37: {"bg": "w17_bg_dancheong", "pose": "pointing_left", "pos": "right"},
    38: {"bg": "w17_bg_dancheong", "pose": "explaining", "pos": "right"},
    39: {"bg": "w17_bg_garden", "pose": "explaining", "pos": "right"},
    40: {"bg": "w17_bg_garden", "pose": "explaining", "pos": "right"},
    41: {"bg": "w17_bg_garden", "pose": "pointing_left", "pos": "right"},
    42: {"bg": "w17_bg_temple_valley", "pose": "explaining", "pos": "right"},
    43: {"bg": "w17_bg_temple_valley", "pose": "cheering", "pos": "right"},
    44: {"bg": "w17_bg_courtyard", "pose": "explaining", "pos": "right"},
    45: {"bg": "w17_bg_entrance", "pose": "walk_right", "pos": "left"},
    46: {"bg": "w17_bg_outro", "pose": "waving", "pos": "right"},
    47: {"bg": "w17_bg_outro", "pose": "bowing", "pos": "right"}
}

def main():
    # Clean up old scene images in OUT_DIR
    for f in os.listdir(OUT_DIR):
        if f.startswith("scene_") and f.endswith(".png"):
            try:
                os.remove(os.path.join(OUT_DIR, f))
            except Exception:
                pass

    print("Starting scene image compilation for 48 scenes...")
    for scene_id, data in SCENE_MAP.items():
        bg_name = data["bg"]
        pose_name = data["pose"]
        position = data["pos"]
        
        bg_path = os.path.join(BG_DIR, f"{bg_name}.png")
        pose_path = os.path.join(CHAR_DIR, f"teacher_jay_{pose_name}.png")
        out_path = os.path.join(OUT_DIR, f"scene_{scene_id}.png")
        
        if not os.path.exists(bg_path):
            print(f"[ERR] Background not found: {bg_path}")
            continue
        if not os.path.exists(pose_path):
            print(f"[ERR] Pose not found: {pose_path}")
            continue
            
        # Open assets
        bg = Image.open(bg_path).convert("RGBA")
        pose = Image.open(pose_path).convert("RGBA")
        
        # Resize character (height: ~420px, keep aspect ratio)
        target_height = 420
        w_orig, h_orig = pose.size
        scale = target_height / h_orig
        target_width = int(w_orig * scale)
        pose_resized = pose.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Calculate coordinates
        # Canvas: 1280 x 720
        bg_w, bg_h = bg.size
        
        # Default positioning coords
        bottom_margin = 35
        y = bg_h - target_height - bottom_margin
        
        if position == "right":
            right_margin = 90
            x = bg_w - target_width - right_margin
        else: # left
            left_margin = 90
            x = left_margin
            
        # Paste with alpha channel transparency
        canvas = Image.new("RGBA", bg.size)
        canvas.paste(bg, (0, 0))
        canvas.paste(pose_resized, (x, y), mask=pose_resized)
        
        # Save as RGB
        final_img = canvas.convert("RGB")
        final_img.save(out_path, "PNG")
        print(f"  Compiled scene {scene_id} -> {out_path}")
        
    print("[OK] All 48 scene images compiled successfully.")

if __name__ == "__main__":
    main()
