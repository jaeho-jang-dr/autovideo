import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    crop = img_resized[200:650, 480:700]
    
    # Reshape the crop to a list of pixels
    pixels = crop.reshape(-1, 3)
    
    # Find unique colors and their counts
    unique, counts = np.unique(pixels, axis=0, return_counts=True)
    
    # Sort by count descending
    sorted_idx = np.argsort(-counts)
    
    print("Most common colors in BGR:")
    for idx in sorted_idx[:15]:
        print(f"  Color {unique[idx]}: {counts[idx]} pixels")
else:
    print("Could not read image.")
