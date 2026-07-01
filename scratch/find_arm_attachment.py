import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    # We want to print out the coordinates of all dark pixels in x=600~645, y=365~395
    # to see where the shoulder/neck line branches out.
    crop = img_resized[365:395, 600:645]
    y_idx, x_idx = np.where((crop[:, :, 0] < 50) & (crop[:, :, 1] < 50) & (crop[:, :, 2] < 50))
    
    print("Coordinates of dark pixels near shoulder/neck:")
    coords = [(x + 600, y + 365) for y, x in zip(y_idx, x_idx)]
    # Group by Y and print the X coordinates
    from collections import defaultdict
    y_to_xs = defaultdict(list)
    for cx, cy in coords:
        y_to_xs[cy].append(cx)
        
    for cy in sorted(y_to_xs.keys()):
        print(f"  y={cy}: xs={sorted(y_to_xs[cy])}")
else:
    print("Could not read image.")
