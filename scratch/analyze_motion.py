import cv2
import numpy as np

video_path = r"d:\Entertainments\DevEnvironment\autovideo\child_growth_science\scene_18.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Failed to open video")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps
print(f"Total frames: {total_frames}, FPS: {fps}, Duration: {duration:.2f}s")

# Extract first, middle, and last frame to analyze camera movement
ret, first_frame = cap.read()
cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
ret, last_frame = cap.read()

if first_frame is not None and last_frame is not None:
    # Use template matching on a static part of the image to find offset
    # Let's crop a patch from the center of first frame
    h, w, _ = first_frame.shape
    patch_size = 200
    cy, cx = h // 2, w // 2
    patch = first_frame[cy - patch_size//2 : cy + patch_size//2, cx - patch_size//2 : cx + patch_size//2]
    
    # Match patch in last frame
    res = cv2.matchTemplate(last_frame, patch, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    # Original patch center was (cx, cy)
    # Matched patch center in last frame is max_loc + patch_size/2
    matched_x = max_loc[0] + patch_size//2
    matched_y = max_loc[1] + patch_size//2
    
    dx = matched_x - cx
    dy = matched_y - cy
    print(f"Camera displacement from first to last frame: dx={dx}, dy={dy}")
    print(f"Velocity per frame: vx={dx / total_frames:.4f}, vy={dy / total_frames:.4f}")
else:
    print("Failed to read frames for analysis")

cap.release()
