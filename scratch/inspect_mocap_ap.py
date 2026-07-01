# -*- coding: utf-8 -*-
"""Draws YOLOv8-pose skeletons and frame numbers on the original video frames of ap_thoracic.mp4,
saving the result to scratch/ap_skeletons.mp4. This helps us manually audit the video.
"""
import os
import cv2
import numpy as np
from ultralytics import YOLO

def main():
    video_path = r"G:\내 드라이브\chiropracticos\archive\videos\techniques\ap_thoracic.mp4"
    out_path = r"scratch/ap_skeletons.mp4"
    
    model = YOLO("yolov8s-pose.pt")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
        
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Source video: {src_w}x{src_h}, {fps} FPS, {total_frames} frames")
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(out_path, fourcc, fps, (src_w, src_h))
    
    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
            
        res = model.predict(frame, verbose=False, imgsz=640)[0]
        
        # Draw frame number
        cv2.putText(frame, f"Frame: {frame_idx}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        if res.keypoints is not None and len(res.keypoints) > 0:
            kxy = res.keypoints.xy.cpu().numpy()
            kcf = res.keypoints.conf
            kcf = kcf.cpu().numpy() if kcf is not None else np.ones((kxy.shape[0], 17))
            
            for idx, (kp, cf) in enumerate(zip(kxy, kcf)):
                # Draw skeleton
                for joint_idx, (x, y) in enumerate(kp):
                    if cf[joint_idx] > 0.3:
                        cv2.circle(frame, (int(x), int(y)), 3, (0, 255, 0), -1)
                        cv2.putText(frame, str(joint_idx), (int(x), int(y)-4), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)
                        
                # Draw connections for bones
                # COCO connections
                bones = [(5,6), (5,7), (7,9), (6,8), (8,10), (5,11), (6,12), (11,12), (11,13), (13,15), (12,14), (14,16)]
                for pt1, pt2 in bones:
                    if cf[pt1] > 0.3 and cf[pt2] > 0.3:
                        p1 = (int(kp[pt1, 0]), int(kp[pt1, 1]))
                        p2 = (int(kp[pt2, 0]), int(kp[pt2, 1]))
                        cv2.line(frame, p1, p2, (0, 255, 255), 1)
                        
        vw.write(frame)
        frame_idx += 1
        
    cap.release()
    vw.release()
    print(f"Audit video saved to: {out_path}")

if __name__ == "__main__":
    main()
