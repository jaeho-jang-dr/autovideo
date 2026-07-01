import cv2
import numpy as np
from ultralytics import YOLO

def inspect_players():
    # Load video
    video_path = r"G:\내 드라이브\chiropracticos\archive\videos\techniques\gonstead_sitting.mp4"
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Failed to open video")
        return
        
    model = YOLO("yolov8s-pose.pt")
    
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video Resolution: {W}x{H}, FPS: {fps}, Total Frames: {total_frames}")
    
    frame_count = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
            
        frame_count += 1
        # Inspect every 10 frames to save output size
        if frame_count % 15 != 0 and frame_count != 1:
            continue
            
        res = model.predict(frame, verbose=False, imgsz=640)[0]
        if res.keypoints is not None and len(res.keypoints) > 0:
            kxy = res.keypoints.xy.cpu().numpy()
            kcf = res.keypoints.conf
            kcf = kcf.cpu().numpy() if kcf is not None else np.ones((kxy.shape[0], 17))
            
            print(f"Frame {frame_count}: Detected {len(kxy)} people")
            for i, (kp, cf) in enumerate(zip(kxy, kcf)):
                # Calculate bounding box
                valid_kp = kp[cf > 0.3]
                if len(valid_kp) > 0:
                    min_x, min_y = valid_kp[:, 0].min(), valid_kp[:, 1].min()
                    max_x, max_y = valid_kp[:, 0].max(), valid_kp[:, 1].max()
                    # Center of hips or shoulders
                    cog_x, cog_y = valid_kp[:, 0].mean(), valid_kp[:, 1].mean()
                    print(f"  Person {i}: Box [{min_x:.1f}, {min_y:.1f}, {max_x:.1f}, {max_y:.1f}], Center [{cog_x:.1f}, {cog_y:.1f}], Avg Conf: {cf.mean():.2f}")
                else:
                    print(f"  Person {i}: No valid keypoints above threshold")
        else:
            print(f"Frame {frame_count}: No people detected")
            
        if frame_count > 300: # limit output
            break
            
    cap.release()

if __name__ == "__main__":
    inspect_players()
