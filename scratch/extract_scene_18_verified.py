import cv2
import os

video_path = r"d:\Entertainments\DevEnvironment\autovideo\child_growth_science\child_growth_fixed.mp4"
output_path = r"C:\Users\antigravity\.gemini\antigravity\brain\4455adca-9bdd-4ddd-a2f1-84e32a8bad0a\scene_18_verified.png"

cap = cv2.VideoCapture(video_path)
if cap.isOpened():
    fps = cap.get(cv2.CAP_PROP_FPS)
    # Target timestamp: 145.0s (which is in Scene 18: 140.95s ~ 149.41s)
    frame_no = int(145.0 * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_path, frame)
        print("Successfully extracted 145.0s frame from patched child_growth_fixed.mp4")
    else:
        print("Failed to read frame")
    cap.release()
else:
    print("Failed to open child_growth_fixed.mp4")
