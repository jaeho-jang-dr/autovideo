# -*- coding: utf-8 -*-
"""Finds the frame number where the cervical adjustment (thrust) occurs in the Gonstead Sitting video.
Tracks the patient's head movement using YOLOv8-pose and finds the frame with the maximum displacement/velocity.
"""
import os
import cv2
import numpy as np
from ultralytics import YOLO

def main():
    video_path = r"G:\내 드라이브\chiropracticos\archive\videos\techniques\gonstead_sitting.mp4"
    model = YOLO("yolov8s-pose.pt")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
        
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video loaded: {src_w}x{src_h}, {total_frames} frames")
    
    frame_idx = 0
    jieun_head_pos = []
    
    # We will track the person on the right (patient/Jieun)
    # The chiropractor is on the left
    while True:
        ok, frame = cap.read()
        if not ok:
            break
            
        res = model.predict(frame, verbose=False, imgsz=640)[0]
        detected = []
        if res.keypoints is not None and len(res.keypoints) > 0:
            kxy = res.keypoints.xy.cpu().numpy()
            kcf = res.keypoints.conf
            kcf = kcf.cpu().numpy() if kcf is not None else np.ones((kxy.shape[0], 17))
            
            for kp, cf in zip(kxy, kcf):
                valid = kp[cf > 0.3]
                if len(valid) > 0:
                    center_x = valid[:, 0].mean()
                    detected.append((center_x, kp, cf))
                    
        # Sort by x-coordinate, chiropractor is left, patient is right
        detected = sorted(detected, key=lambda x: x[0])
        
        # If we have at least one person, check if we can get the right-most person's head keypoints
        if len(detected) >= 2:
            # Patient is the second person (right-most)
            kp, cf = detected[1][1], detected[1][2]
        elif len(detected) == 1:
            # If only one is detected, check if it's on the right half
            cx, kp, cf = detected[0]
            if cx > src_w * 0.4:
                # Patient
                pass
            else:
                kp, cf = None, None
        else:
            kp, cf = None, None
            
        if kp is not None:
            # Head keypoints are 0 to 4 (nose, eyes, ears)
            head_kps = kp[0:5]
            head_cf = cf[0:5]
            valid_head = head_kps[head_cf > 0.3]
            if len(valid_head) > 0:
                head_pos = valid_head.mean(axis=0)
                jieun_head_pos.append((frame_idx, head_pos))
            else:
                jieun_head_pos.append((frame_idx, None))
        else:
            jieun_head_pos.append((frame_idx, None))
            
        frame_idx += 1
        
    cap.release()
    
    # Calculate velocities
    velocities = []
    for i in range(1, len(jieun_head_pos)):
        f1, p1 = jieun_head_pos[i-1]
        f2, p2 = jieun_head_pos[i]
        if p1 is not None and p2 is not None:
            dist = np.linalg.norm(p2 - p1)
            velocities.append((f2, dist))
            
    # Sort velocities to find the maximum movement
    velocities = sorted(velocities, key=lambda x: x[1], reverse=True)
    
    print("\n--- Top 10 frames with highest head velocity ---")
    for i in range(min(10, len(velocities))):
        f, v = velocities[i]
        print(f"Frame {f:3d} (approx {f/24:.2f}s): Velocity = {v:.2f} px/frame")

if __name__ == "__main__":
    main()
