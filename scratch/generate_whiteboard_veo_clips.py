# -*- coding: utf-8 -*-
import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

def main():
    print("=== Start Whiteboard Veo Video Clips Generation Loop ===")
    
    prompts_file = "jay_Rhc_whiteboard_prompts.txt"
    force = "--force" in sys.argv
    
    # 5 Hangeul words: "강", "물", "꽃", "불", "차"
    for n in range(1, 6):
        out_clip_path = os.path.join(ROOT, "jay_Rhc_whiteboard", f"scene_{n}.mp4")
        
        # Check incremental generation: skip if file exists and has size
        if not force and os.path.exists(out_clip_path) and os.path.getsize(out_clip_path) > 0:
            print(f"[SKIP] Scene {n} video clip already exists at: {out_clip_path}")
            continue
            
        base_img_path = os.path.join(ROOT, "assets", "characters", f"jay_whiteboard_base_word_{n}.png")
        if not os.path.exists(base_img_path):
            print(f"[ERR] Reference base image not found for Scene {n}: {base_img_path}")
            continue
            
        cmd = [
            "python", "autoveo_flow.py",
            "--prompts", prompts_file,
            "--scene", str(n),
            "--upload", base_img_path
        ]
        if force:
            cmd.append("--force")
            
        print(f"\n>>> Running autoveo_flow for Scene {n}... Command: {' '.join(cmd)}")
        try:
            # Execute command and stream output
            res = subprocess.run(cmd, cwd=ROOT, check=True)
            if res.returncode == 0:
                print(f"[OK] Scene {n} generation finished successfully.")
            else:
                print(f"[ERR] Scene {n} generation failed with return code {res.returncode}")
        except subprocess.CalledProcessError as e:
            print(f"[ERR] subprocess execution error for Scene {n}: {e}")
            
    print("\n=== Whiteboard Veo Video Clips Generation Loop Finished ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
