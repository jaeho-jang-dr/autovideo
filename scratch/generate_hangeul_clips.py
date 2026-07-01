# -*- coding: utf-8 -*-
import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
sys.stdout.reconfigure(encoding="utf-8")

def main():
    print("=== Start Generating Veo Video Clips for Hangeul Birth and Vowels (30s) ===")
    
    prompts_file = "hangeul_birth_vowels_prompts.txt"
    project_dir = os.path.join(ROOT, "hangeul_birth_vowels")
    os.makedirs(project_dir, exist_ok=True)
    
    # We will use the same base image jay_base_side_opaque.png for consistency
    base_image = os.path.join(ROOT, "assets", "characters", "jay_base_side_opaque.png")
    if not os.path.exists(base_image):
        # Fallback to general base front if side is not found
        base_image = os.path.join(ROOT, "assets", "characters", "jay_base_front_opaque.png")
        
    if not os.path.exists(base_image):
        print(f"[ERR] Base character image not found: {base_image}")
        return 1
        
    for n in range(1, 7):
        out_clip_path = os.path.join(project_dir, f"scene_{n}.mp4")
        
        # Skip if already exists
        if os.path.exists(out_clip_path) and os.path.getsize(out_clip_path) > 0:
            print(f"[SKIP] Scene {n} video already exists. Skipping...")
            continue
            
        cmd = [
            "python", "autoveo_flow.py",
            "--prompts", prompts_file,
            "--scene", str(n),
            "--upload", base_image,
            "--force"
        ]
        
        print(f"\n>>> [Veo] Generating Clip for Scene {n}/6... Command: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, cwd=ROOT, check=True)
            if res.returncode != 0:
                print(f"[ERR] autoveo_flow failed for Scene {n} with return code {res.returncode}")
                return 1
        except subprocess.CalledProcessError as e:
            print(f"[ERR] subprocess execution error for Scene {n}: {e}")
            return 1
            
        # Move the downloaded clip into our project directory
        # autoveo_flow downloads into root/hangeul_birth_vowels/scene_N.mp4 based on prompts filename
        if not os.path.exists(out_clip_path) or os.path.getsize(out_clip_path) == 0:
            print(f"[ERR] Generated clip not found at expected path: {out_clip_path}")
            return 1
            
        print(f"[OK] Scene {n} video generated successfully!")
        
    print("\n=== All 6 Veo Video Clips Generated Successfully ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
