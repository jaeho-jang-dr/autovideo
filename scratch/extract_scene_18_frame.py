import cv2
import os

video_path = r"d:\Entertainments\DevEnvironment\autovideo\child_growth_science\scene_18.mp4"
output_path = r"C:\Users\antigravity\.gemini\antigravity\brain\4455adca-9bdd-4ddd-a2f1-84e32a8bad0a\scene_18_first_frame.png"

cap = cv2.VideoCapture(video_path)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_path, frame)
        print("Successfully extracted first frame of scene_18.mp4")
    else:
        print("Failed to read frame")
    cap.release()
else:
    print("Failed to open scene_18.mp4")
