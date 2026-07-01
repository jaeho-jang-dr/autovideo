import cv2
import numpy as np

def analyze():
    img_path = r"home_vocab/zolla_pair_base.png"
    img = cv2.imread(img_path)
    if img is None:
        print("Error: Could not read image.")
        return
    
    h, w, c = img.shape
    print(f"Image shape: {w}x{h}")
    
    # Let's split into left and right halves
    mid_x = w // 2
    left_half = img[:, :mid_x]
    right_half = img[:, mid_x:]
    
    # Convert to RGB/HSV to find orange and black
    # Black: very dark colors
    # Orange: H in [5, 25], S in [100, 255], V in [100, 255] (or simple color thresholding)
    # Let's count black pixels (R < 50, G < 50, B < 50)
    black_mask_left = (left_half[:, :, 0] < 50) & (left_half[:, :, 1] < 50) & (left_half[:, :, 2] < 50)
    black_mask_right = (right_half[:, :, 0] < 50) & (right_half[:, :, 1] < 50) & (right_half[:, :, 2] < 50)
    
    num_black_left = np.sum(black_mask_left)
    num_black_right = np.sum(black_mask_right)
    
    # Let's count orange pixels
    # In BGR: B is low, R is high, G is medium
    # R > 150, G > 50, G < 160, B < 80
    bgr = img
    orange_mask = (bgr[:, :, 2] > 150) & (bgr[:, :, 1] > 50) & (bgr[:, :, 1] < 160) & (bgr[:, :, 0] < 80)
    orange_mask_left = orange_mask[:, :mid_x]
    orange_mask_right = orange_mask[:, mid_x:]
    
    num_orange_left = np.sum(orange_mask_left)
    num_orange_right = np.sum(orange_mask_right)
    
    print(f"Left half black pixels: {num_black_left}")
    print(f"Right half black pixels: {num_black_right}")
    print(f"Left half orange pixels: {num_orange_left}")
    print(f"Right half orange pixels: {num_orange_right}")
    
    if num_black_left > 100 and num_black_right > 100:
        print("Both halves have black pixels (stick figures).")
    else:
        print("Warning: One or both halves do not have enough black pixels.")
        
    if num_orange_right > 50 and num_orange_left < 20:
        print("Orange hair detected on the right half (female figure).")
    else:
        print("Warning: Orange hair check failed.")

if __name__ == '__main__':
    analyze()
