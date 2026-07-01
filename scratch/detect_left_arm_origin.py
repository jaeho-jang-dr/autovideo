import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    crop = img_resized[250:350, 600:680]
    mask = (crop[:, :, 0] < 30) & (crop[:, :, 1] < 30) & (crop[:, :, 2] < 30)
    
    print("Tracing neck/shoulder area (y=270~325):")
    for y in range(270, 325, 2):
        row_mask = mask[y-250, :]
        row_xs = np.where(row_mask)[0] + 600
        print(f"  y={y}: xs={list(row_xs)}")
else:
    print("Could not read image.")
