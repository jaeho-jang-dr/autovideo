import cv2
import os

video_path = r"d:\Entertainments\DevEnvironment\autovideo\scratch\Learn How to Think In English ( Stop Translating in Your Head ).mp4"
output_dir = r"d:\Entertainments\DevEnvironment\autovideo\scratch\think_english_frames"
os.makedirs(output_dir, exist_ok=True)

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)

# Extract frames at specific timestamps (seconds)
timestamps = [2, 5, 10, 15, 20, 25, 30, 45, 60, 90]

for ts in timestamps:
    frame_number = int(ts * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        out_path = os.path.join(output_dir, f"frame_{ts}s.png")
        cv2.imwrite(out_path, frame)
        print(f"Saved frame at {ts}s to {out_path}")
    else:
        print(f"Failed to extract frame at {ts}s")

cap.release()
