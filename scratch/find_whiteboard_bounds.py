import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_whiteboard_writing_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    print(f"Image resized to 1280x720")
    
    # Let's inspect the color profile at row y=300
    row_y = 300
    row_pixels = img_resized[row_y, :, :]
    
    print("\nColor profile at row y=300:")
    for x in range(0, 1280, 50):
        print(f"  x={x}: BGR={row_pixels[x]}")
        
    # Let's find white pixels (board background)
    # The whiteboard is white, so let's say B > 240, G > 240, R > 240
    white_mask = (img_resized[:, :, 0] > 240) & (img_resized[:, :, 1] > 240) & (img_resized[:, :, 2] > 240)
    y_w, x_w = np.where(white_mask)
    if len(x_w) > 0:
        print(f"\nWhite board detected at X: {min(x_w)} ~ {max(x_w)}")
        print(f"White board detected at Y: {min(y_w)} ~ {max(y_w)}")
        
    # Let's check the blackboard's actual box size on whiteboard image
    # The outer boundary is black (BGR < 30)
    # The board top edge, left edge, bottom edge, etc.
    # Usually the board is in the region x: 250 ~ 1050, y: 50 ~ 450 approximately.
    # Let's look at the shape. In the first image view:
    # There is a rectangle representing the chalkboard (whiteboard in this case).
    # Its borders: left border is around x=280? Top is around y=36?
    # Let's analyze it by looking at columns with black lines.
    
    # We can detect the blackboard borders by looking at a horizontal line y=100.
    # In y=100, the board background is white, and the background of room is beige.
    # Beige color is around B=232, G=232, R=228 or similar.
    # Let's print out the exact colors around boundaries.
    
else:
    print("Could not read image.")
