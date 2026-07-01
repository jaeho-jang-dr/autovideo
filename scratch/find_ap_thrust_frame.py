# -*- coding: utf-8 -*-
"""Finds the frame number where the AP thoracic thrust occurs by analyzing the distance
between the chiropractor (who is standing and leans/drops) and the patient (who is lying down).
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
        
    frame_idx = 0
    history = []
    
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
                    min_x, max_x = valid[:, 0].min(), valid[:, 0].max()
                    min_y, max_y = valid[:, 1].min(), valid[:, 1].max()
                    w = max_x - min_x
                    h = max_y - min_y
                    cx = valid[:, 0].mean()
                    cy = valid[:, 1].mean()
                    detected.append({
                        "kp": kp,
                        "cf": cf,
                        "cx": cx,
                        "cy": cy,
                        "w": w,
                        "h": h
                    })
                    
        # Identify patient vs chiropractor
        # Patient is lying down: horizontal orientation (large width/height ratio) or located lower in some views.
        # Let's see: the person who has larger width (lying down horizontally) is the patient.
        # The person who stands above and has smaller width but taller height (when standing) is the chiropractor.
        patient = None
        chiro = None
        
        if len(detected) >= 2:
            # Sort by width (the lying person has a very wide bounding box)
            detected_sorted = sorted(detected, key=lambda x: x["w"], reverse=True)
            patient = detected_sorted[0]
            chiro = detected_sorted[1]
        elif len(detected) == 1:
            patient = detected[0] # assume patient is detected
            
        if patient and chiro:
            # Calculate distance between chiropractor's chest (shoulders mean) and patient's chest (torso center)
            # COCO shoulders: LSH=5, RSH=6. Hips: LHIP=11, RHIP=12
            chiro_sh = np.mean([chiro["kp"][5], chiro["kp"][6]], axis=0) if (chiro["cf"][5] > 0.3 and chiro["cf"][6] > 0.3) else chiro["kp"].mean(axis=0)
            patient_chest = np.mean([patient["kp"][5], patient["kp"][6], patient["kp"][11], patient["kp"][12]], axis=0)
            
            dist = np.linalg.norm(chiro_sh - patient_chest)
            history.append((frame_idx, dist))
        else:
            history.append((frame_idx, None))
            
        frame_idx += 1
        
    cap.release()
    
    # Analyze history to find where the distance drops rapidly (the "thrust/drop" phase)
    # We look for a sudden drop followed by a rebound or stabilization
    deltas = []
    for i in range(1, len(history)):
        f1, d1 = history[i-1]
        f2, d2 = history[i]
        if d1 is not None and d2 is not None:
            deltas.append((f2, d1 - d2)) # positive means distance is decreasing (approaching)
            
    # Sort by speed of approach (deltas)
    deltas = sorted(deltas, key=lambda x: x[1], reverse=True)
    
    print("\n--- Top 10 frames with fastest body drop (approach speed) ---")
    for i in range(min(10, len(deltas))):
        f, diff = deltas[i]
        print(f"Frame {f:3d} (approx {f/24:.2f}s): Approach delta = {diff:.2f} px")

if __name__ == "__main__":
    main()
