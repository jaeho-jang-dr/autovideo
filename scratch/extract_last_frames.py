import cv2
import os

video_path = r"d:\Entertainments\DevEnvironment\autovideo\workout_injury_science\workout_injury_fixed.mp4"
output_dir = r"C:\Users\antigravity\.gemini\antigravity\brain\4455adca-9bdd-4ddd-a2f1-84e32a8bad0a"

os.makedirs(output_dir, exist_ok=True)

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error opening video file")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
duration = total_frames / fps

print(f"FPS: {fps}, Total Frames: {total_frames}, Duration: {duration:.2f}s")

# Extract frames from duration - 15 to duration (1 frame per second)
start_sec = max(0.0, duration - 15.0)
for sec in range(int(start_sec), int(duration) + 1):
    frame_no = int(sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
    ret, frame = cap.read()
    if ret:
        out_name = f"last_frame_{sec}.png"
        out_path = os.path.join(output_dir, out_name)
        cv2.imwrite(out_path, frame)
        print(f"Saved {out_name} (at {sec}s)")
    else:
        print(f"Failed to read frame at {sec}s")

cap.release()
print("Done extracting frames!")
