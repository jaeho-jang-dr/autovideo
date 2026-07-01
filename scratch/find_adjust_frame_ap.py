# -*- coding: utf-8 -*-
"""Finds the frame number where the thoracic adjustment (thrust) occurs in the AP Thoracic video.
Tracks all keypoints and finds the frame with the maximum global movement/velocity.
"""
import os
import cv2
import numpy as np
from ultralytics import YOLO

def main():
    video_path = r"G:\내 드라이브\chiropracticos\archive\videos\techniques\ap_thoracic.mp4"
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
    all_keypoints = []
    
    while True:
        ok, frame = cap.read()
        if not ok:
            break
            
        res = model.predict(frame, verbose=False, imgsz=640)[0]
        frame_kps = []
        if res.keypoints is not None and len(res.keypoints) > 0:
            kxy = res.keypoints.xy.cpu().numpy()
            kcf = res.keypoints.conf
            kcf = kcf.cpu().numpy() if kcf is not None else np.ones((kxy.shape[0], 17))
            
            for kp, cf in zip(kxy, kcf):
                valid = kp[cf > 0.3]
                if len(valid) > 0:
                    frame_kps.append(kp)
                    
        all_keypoints.append(frame_kps)
        frame_idx += 1
        
    cap.release()
    
    # Calculate global velocity (average frame-to-frame keypoint displacement for all detected people)
    velocities = []
    for i in range(1, len(all_keypoints)):
        kps1 = all_keypoints[i-1]
        kps2 = all_keypoints[i]
        
        # If we have people in both frames, find matching pairs and calculate distance
        if len(kps1) > 0 and len(kps2) > 0:
            frame_dists = []
            for kp2 in kps2:
                # Find closest person in kps1 by distance of mean coordinates
                p2_center = kp2.mean(axis=0)
                best_dist = float('inf')
                best_kp1 = None
                for kp1 in kps1:
                    p1_center = kp1.mean(axis=0)
                    d = np.linalg.norm(p2_center - p1_center)
                    if d < best_dist:
                        best_dist = d
                        best_kp1 = kp1
                if best_kp1 is not None:
                    # Calculate mean joint displacement
                    diff = np.linalg.norm(kp2 - best_kp1, axis=1)
                    frame_dists.append(np.mean(diff))
            if frame_dists:
                velocities.append((i, np.mean(frame_dists)))
                
    # Sort velocities to find the maximum movement
    velocities = sorted(velocities, key=lambda x: x[1], reverse=True)
    
    print("\n--- Top 10 frames with highest joint velocity in AP Thoracic ---")
    for i in range(min(10, len(velocities))):
        f, v = velocities[i]
        print(f"Frame {f:3d} (approx {f/24:.2f}s): Velocity = {v:.2f} px/frame")

if __name__ == "__main__":
    main()
