import cv2
import os

def extract_first_frame():
    video_path = "chiropractic_science/scene_1.mp4"
    if not os.path.exists(video_path):
        print("Video file not found.")
        return
        
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read() # Read 1st frame (index 0)
    if ret:
        cv2.imwrite("scratch/scene_1_first_frame.png", frame)
        print("Saved scratch/scene_1_first_frame.png")
        
        # Save cropped bottom-right area (right 25%, bottom 20%)
        h, w, _ = frame.shape
        crop_y = int(h * 0.8)
        crop_x = int(w * 0.75)
        cropped = frame[crop_y:h, crop_x:w]
        cv2.imwrite("scratch/scene_1_first_frame_cropped.png", cropped)
        print(f"Saved cropped first frame corner. Size: {cropped.shape}")
        
    cap.release()

if __name__ == "__main__":
    extract_first_frame()
