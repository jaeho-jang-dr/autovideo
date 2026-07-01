# -*- coding: utf-8 -*-
import os
import sys
import cv2
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

def extract_last_frame(video_path, output_path):
    print(f"Extracting last frame from {video_path}...")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERR] Cannot open video: {video_path}")
        return False
        
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"  Video frame count: {frame_count}")
    
    # Try setting position to the last frame (frame_count - 1)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_path, frame)
        print(f"[OK] Extracted last frame to {output_path}")
        cap.release()
        return True
        
    # Fallback: Read sequentially to get the absolute last valid frame
    print("  [WARN] Failed to set frame index. Falling back to sequential read...")
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    last_frame = None
    while True:
        r, f = cap.read()
        if not r:
            break
        last_frame = f
        
    if last_frame is not None:
        cv2.imwrite(output_path, last_frame)
        print(f"[OK] Extracted last frame (sequential fallback) to {output_path}")
        cap.release()
        return True
        
    cap.release()
    print(f"[ERR] Failed to read any frame from {video_path}")
    return False

def main():
    print("=== Start Whiteboard Veo Clips Generation Loop (ekf / 달 그림자) ===")
    
    prompts_file = "jay_ekf_whiteboard_prompts.txt"
    force = "--force" in sys.argv
    project_dir = os.path.join(ROOT, "jay_ekf_whiteboard")
    os.makedirs(project_dir, exist_ok=True)
    
    clean_base_image = os.path.join(ROOT, "assets", "characters", "jay_whiteboard_clean_base.png")
    if not os.path.exists(clean_base_image):
        print(f"[ERR] Blank base image not found: {clean_base_image}")
        return 1
        
    for n in range(1, 5):
        out_clip_path = os.path.join(project_dir, f"scene_{n}.mp4")
        last_frame_path = os.path.join(project_dir, f"scene_{n}_last.png")
        
        # Determine the base image for this scene
        if n == 1:
            base_image = clean_base_image
        else:
            base_image = os.path.join(project_dir, f"scene_{n-1}_last.png")
            
        if not os.path.exists(base_image):
            print(f"[ERR] Base reference image not found for Scene {n}: {base_image}")
            return 1
            
        # Incremental Generation Check: skip if clip and last frame already exist
        if not force and os.path.exists(out_clip_path) and os.path.getsize(out_clip_path) > 0 and os.path.exists(last_frame_path):
            print(f"[SKIP] Scene {n} video and last frame already exist. Skipping...")
            continue
            
        cmd = [
            "python", "autoveo_flow.py",
            "--prompts", prompts_file,
            "--scene", str(n),
            "--upload", base_image
        ]
        if force:
            cmd.append("--force")
            
        print(f"\n>>> Running autoveo_flow for Scene {n} ('{['달', '그', '림', '자'][n-1]}')... Command: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, cwd=ROOT, check=True)
            if res.returncode != 0:
                print(f"[ERR] autoveo_flow failed for Scene {n} with return code {res.returncode}")
                return 1
        except subprocess.CalledProcessError as e:
            print(f"[ERR] subprocess execution error for Scene {n}: {e}")
            return 1
            
        # Extract the last frame of the newly generated clip
        if not os.path.exists(out_clip_path) or os.path.getsize(out_clip_path) == 0:
            print(f"[ERR] Generated clip not found at expected path: {out_clip_path}")
            return 1
            
        if not extract_last_frame(out_clip_path, last_frame_path):
            print(f"[ERR] Failed to extract last frame for transition after Scene {n}")
            return 1
            
    print("\n=== Whiteboard Veo Clips Generation Loop (ekf) Finished Successfully ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
