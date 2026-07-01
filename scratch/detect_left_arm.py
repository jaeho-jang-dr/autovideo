import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    # Search for black pixels in the stickman region (x: 500~750, y: 250~600)
    crop = img_resized[250:600, 500:750]
    mask = (crop[:, :, 0] < 30) & (crop[:, :, 1] < 30) & (crop[:, :, 2] < 30)
    y_idx, x_idx = np.where(mask)
    
    # We want to find the connected components to trace the limbs.
    # Let's save a visualization of the stickman joints.
    # In the side profile, the head is a circle.
    # Let's find where the neck is.
    # The neck is the junction below the head.
    # Let's write a script to trace lines from the neck.
    # We will print out all coordinates of black pixels that are NOT the spine (x != 642) and not the legs.
    # Specifically, the left arm starts near the shoulder.
    print("Stickman black pixels in the chest/arm area (y=320~450):")
    for y in range(320, 450, 5):
        row_mask = mask[y-250, :]
        row_xs = np.where(row_mask)[0] + 500
        print(f"  y={y}: xs={list(row_xs)}")
else:
    print("Could not read image.")
