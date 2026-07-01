import cv2

def save_frame():
    video_path = r"G:\내 드라이브\chiropracticos\archive\videos\techniques\gonstead_sitting.mp4"
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Failed to open video")
        return
        
    cap.set(cv2.CAP_PROP_POS_FRAMES, 60)
    ok, frame = cap.read()
    if ok:
        cv2.imwrite("scratch/gonstead_frame_60.png", frame)
        print("Saved scratch/gonstead_frame_60.png")
    else:
        print("Failed to read frame")
    cap.release()

if __name__ == "__main__":
    save_frame()
