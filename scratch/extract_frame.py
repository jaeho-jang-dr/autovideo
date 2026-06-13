import cv2
import os

def extract():
    video_path = "chiropractic_science/scene_1.mp4"
    if not os.path.exists(video_path):
        print("Video file not found.")
        return
    
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames: {total_frames}")
    
    # Read the middle frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("scratch/scene_1_mid_frame.png", frame)
        print("Saved scratch/scene_1_mid_frame.png")
        
        # Save cropped bottom-right area (right 25%, bottom 20%)
        h, w, _ = frame.shape
        crop_y = int(h * 0.8)
        crop_x = int(w * 0.75)
        cropped = frame[crop_y:h, crop_x:w]
        cv2.imwrite("scratch/scene_1_cropped_corner.png", cropped)
        print(f"Saved cropped corner. Size: {cropped.shape}")
        
    cap.release()

if __name__ == "__main__":
    os.makedirs("scratch", exist_ok=True)
    extract()
