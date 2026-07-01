# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
sys.stdout.reconfigure(encoding="utf-8")

from scratch.track_and_synthesize_whiteboard import process_hybrid_scene

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
    print("=== Start Sequential Closed-Loop Hybrid Whiteboard Pipeline (ekf / 달 그림자) ===")
    
    prompts_file = "jay_ekf_whiteboard_prompts.txt"
    project_dir = os.path.join(ROOT, "jay_ekf_whiteboard")
    os.makedirs(project_dir, exist_ok=True)
    
    clean_base_image = os.path.join(ROOT, "assets", "characters", "jay_whiteboard_clean_base.png")
    if not os.path.exists(clean_base_image):
        print(f"[ERR] Blank base image not found: {clean_base_image}")
        return 1
        
    # We will generate scenes sequentially: 1 -> 2 -> 3 -> 4
    for n in range(1, 5):
        print(f"\n==========================================")
        print(f"   Executing Pipeline Step {n}/4: '{['달', '그', '림', '자'][n-1]}'")
        print(f"==========================================")
        
        orig_clip_path = os.path.join(project_dir, f"scene_{n}.mp4")
        hybrid_clip_path = os.path.join(project_dir, f"scene_{n}_hybrid.mp4")
        hybrid_last_path = os.path.join(project_dir, f"scene_{n}_hybrid_last.png")
        
        # 1. Determine upload reference image
        if n == 1:
            base_image = clean_base_image
        else:
            base_image = os.path.join(project_dir, f"scene_{n-1}_hybrid_last.png")
            
        if not os.path.exists(base_image):
            print(f"[ERR] Base reference image not found for Scene {n}: {base_image}")
            return 1
            
        # 2. Call autoveo_flow.py to generate and download Scene N
        cmd = [
            "python", "autoveo_flow.py",
            "--prompts", prompts_file,
            "--scene", str(n),
            "--upload", base_image,
            "--force"
        ]
        
        print(f"\n>>> [Pipeline] Generating Veo Clip for Scene {n}... Command: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, cwd=ROOT, check=True)
            if res.returncode != 0:
                print(f"[ERR] autoveo_flow failed for Scene {n} with return code {res.returncode}")
                return 1
        except subprocess.CalledProcessError as e:
            print(f"[ERR] subprocess execution error for Scene {n}: {e}")
            return 1
            
        if not os.path.exists(orig_clip_path) or os.path.getsize(orig_clip_path) == 0:
            print(f"[ERR] Generated clip not found at expected path: {orig_clip_path}")
            return 1
            
        # 3. Immediately run wrist tracking + Hangeul stroke compositing
        print(f"\n>>> [Pipeline] Synthesizing precise digital handwriting for Scene {n}...")
        success = process_hybrid_scene(n - 1)
        if not success or not os.path.exists(hybrid_clip_path):
            print(f"[ERR] Hybrid text synthesis failed for Scene {n}")
            return 1
            
        # 4. Extract the last frame of the hybrid composite video
        print(f"\n>>> [Pipeline] Extracting transition base image for Scene {n}...")
        if not extract_last_frame(hybrid_clip_path, hybrid_last_path):
            print(f"[ERR] Failed to extract last frame from hybrid video for Scene {n}")
            return 1
            
        print(f"[OK] Scene {n} pipeline cycle finished successfully!")
        
    print("\n==========================================")
    print("   Closed-Loop Pipeline Execution Completed!")
    print("==========================================")
    return 0

if __name__ == "__main__":
    sys.exit(main())
