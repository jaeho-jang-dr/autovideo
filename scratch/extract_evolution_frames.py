import cv2
import os

video_path = r"d:\Entertainments\DevEnvironment\autovideo\assets\videos\jay_whiteboard_consonants_evolution.mp4"
artifact_dir = r"C:\Users\antigravity\.gemini\antigravity\brain\ddcce0ae-4499-40e2-a60b-84f4b372fe49"
os.makedirs(artifact_dir, exist_ok=True)

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Failed to open video: {video_path}")
    exit(1)

fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Video FPS: {fps}")

# Extract frames at specific timestamps (seconds)
timestamps = [1.0, 4.0, 6.8, 15.0]

for ts in timestamps:
    frame_number = int(ts * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        out_path = os.path.join(artifact_dir, f"evolution_frame_{ts}s.png")
        cv2.imwrite(out_path, frame)
        print(f"Saved frame at {ts}s to {out_path}")
    else:
        print(f"Failed to extract frame at {ts}s")

cap.release()
