import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    # Search for black pixels in x=380~550, y=200~350
    crop = img_resized[200:350, 380:550]
    mask = (crop[:, :, 0] < 30) & (crop[:, :, 1] < 30) & (crop[:, :, 2] < 30)
    y_idx, x_idx = np.where(mask)
    
    print(f"Number of black pixels in x=380~550, y=200~350: {len(x_idx)}")
    if len(x_idx) > 0:
        print(f"  X range: {min(x_idx) + 380} ~ {max(x_idx) + 380}")
        print(f"  Y range: {min(y_idx) + 200} ~ {max(y_idx) + 200}")
else:
    print("Could not read image.")
