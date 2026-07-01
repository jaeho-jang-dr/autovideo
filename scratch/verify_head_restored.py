import cv2
import os
import numpy as np

out_dir = r"C:\Users\antigravity\.gemini\antigravity\brain\ddcce0ae-4499-40e2-a60b-84f4b372fe49"
img_path = os.path.join(out_dir, "test_face_restored.png")
img = cv2.imread(img_path)

if img is not None:
    # 1. Check head intactness (columns 588~635, rows 240~270)
    # In the original image, there were head pixels in this region.
    # Let's count black pixels in this region in the restored image.
    crop_head = img[240:270, 588:635]
    mask_head = (crop_head[:, :, 0] < 30) & (crop_head[:, :, 1] < 30) & (crop_head[:, :, 2] < 30)
    num_head_pixels = np.sum(mask_head)
    print(f"Number of head/face black pixels found in test image: {num_head_pixels}")
    
    # 2. Check hand erasure (columns 480~550, rows 200~260)
    crop_hand = img[200:260, 480:550]
    mask_hand = (crop_hand[:, :, 0] < 30) & (crop_hand[:, :, 1] < 30) & (crop_hand[:, :, 2] < 30)
    num_hand_pixels = np.sum(mask_hand)
    print(f"Number of hand black pixels found in test image: {num_hand_pixels}")
    
    if num_head_pixels > 50 and num_hand_pixels == 0:
        print("SUCCESS: Head is fully restored and hand is completely erased!")
    else:
        print("FAIL: Head restoration or hand erasure failed!")
        print(f"  num_head_pixels = {num_head_pixels} (expected > 50)")
        print(f"  num_hand_pixels = {num_hand_pixels} (expected == 0)")
else:
    print("Could not read test image.")
