import cv2
import numpy as np

def analyze_first():
    img = cv2.imread("scratch/scene_1_first_frame_cropped.png")
    if img is None:
        print("Image not found.")
        return
        
    bg_color = np.array([201, 219, 226], dtype=np.float32)
    diff = np.linalg.norm(img.astype(np.float32) - bg_color, axis=2)
    
    threshold_val = 15.0
    logo_mask = (diff > threshold_val).astype(np.uint8) * 255
    
    ys, xs = np.where(logo_mask > 0)
    if len(xs) > 0 and len(ys) > 0:
        min_x, max_x = np.min(xs), np.max(xs)
        min_y, max_y = np.min(ys), np.max(ys)
        print(f"FIRST FRAME LOGO DETECTED!")
        print(f"X range: [{min_x + 960}, {max_x + 960}], Y range: [{min_y + 576}, {max_y + 576}]")
    else:
        print("NO LOGO DETECTED IN FIRST FRAME using standard color distance threshold.")

if __name__ == "__main__":
    analyze_first()
