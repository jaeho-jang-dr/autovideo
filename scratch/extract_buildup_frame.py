import cv2
import os

video_path = r"d:\Entertainments\DevEnvironment\autovideo\line_craft\vocab_buildup.mp4"
output_path = r"C:\Users\antigravity\.gemini\antigravity\brain\1d40511b-87be-45ca-a4f2-c44c6e859424\vocab_buildup_frame.png"

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Could not open video.")
    exit(1)

# Go to 28.0 seconds (28 * 1000 ms)
cap.set(cv2.CAP_PROP_POS_MSEC, 28000)
ret, frame = cap.read()
if ret:
    cv2.imwrite(output_path, frame)
    print(f"Successfully saved frame to {output_path}")
else:
    print("Error: Could not read frame at 28.0 seconds.")

cap.release()
