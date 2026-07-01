# -*- coding: utf-8 -*-
"""Analyzes the layout of people in ap_thoracic.mp4 to determine their poses and roles.
"""
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
        
    for frame_no in [10, 100, 200]:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ok, frame = cap.read()
        if not ok:
            continue
            
        print(f"\n--- Frame {frame_no} ---")
        res = model.predict(frame, verbose=False, imgsz=640)[0]
        if res.keypoints is not None and len(res.keypoints) > 0:
            kxy = res.keypoints.xy.cpu().numpy()
            kcf = res.keypoints.conf
            kcf = kcf.cpu().numpy() if kcf is not None else np.ones((kxy.shape[0], 17))
            
            for idx, (kp, cf) in enumerate(zip(kxy, kcf)):
                valid = kp[cf > 0.3]
                if len(valid) == 0:
                    continue
                    
                # Bounding box
                min_x, max_x = valid[:, 0].min(), valid[:, 0].max()
                min_y, max_y = valid[:, 1].min(), valid[:, 1].max()
                w = max_x - min_x
                h = max_y - min_y
                cx = valid[:, 0].mean()
                cy = valid[:, 1].mean()
                
                # Check orientation: if width > height, the person is probably lying down
                orientation = "Horizontal (Lying Down)" if w > h * 1.2 else "Vertical (Standing/Sitting)"
                
                # Check head position (nose, eyes) vs feet position (ankles)
                # COCO ankles: LANKLE=15, RANKLE=16. Head: NOSE=0
                head_y = kp[0, 1] if cf[0] > 0.3 else None
                ankle_y = np.mean([kp[15, 1], kp[16, 1]]) if (cf[15] > 0.3 and cf[16] > 0.3) else None
                
                print(f"  Person {idx}: Center=({cx:.1f}, {cy:.1f}), Width={w:.1f}, Height={h:.1f}, Orientation={orientation}")
                if head_y and ankle_y:
                    print(f"    Head Y={head_y:.1f}, Ankles Y={ankle_y:.1f}")
        else:
            print("  No keypoints detected.")
            
    cap.release()

if __name__ == "__main__":
    main()
