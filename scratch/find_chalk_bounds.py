import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    
    # Let's save a series of crops of the chalkboard to see where the chalkboard is
    # and where the original hand is.
    # The chalkboard is dark green (BGR: B around 70, G around 100, R around 65)
    # Let's find columns where the color is green.
    # We check columns from x = 0 to 1280 at row y = 300.
    row_y = 300
    row_pixels = img_resized[row_y, :, :]
    
    print("Color profile at row y=300:")
    for x in range(0, 1280, 50):
        print(f"  x={x}: BGR={row_pixels[x]}")
        
    # Let's find the chalkboard column boundaries (where BGR has green color)
    # Green chalkboard color matches: 50 <= B <= 90, 80 <= G <= 120, 45 <= R <= 85
    green_mask = (img_resized[:, :, 0] >= 50) & (img_resized[:, :, 0] <= 90) & \
                 (img_resized[:, :, 1] >= 80) & (img_resized[:, :, 1] <= 120) & \
                 (img_resized[:, :, 2] >= 45) & (img_resized[:, :, 2] <= 85)
                 
    y_indices, x_indices = np.where(green_mask)
    if len(x_indices) > 0:
        print(f"\nGreen chalkboard detected at X: {min(x_indices)} ~ {max(x_indices)}")
        print(f"Green chalkboard detected at Y: {min(y_indices)} ~ {max(y_indices)}")
        
    # Let's find where the original right hand is:
    # In the chalkboard region (say, x: 0 ~ 550, y: 150 ~ 500)
    # the stickman hand is black (BGR < 30) and the chalk is white (BGR > 200).
    # Let's search for these pixels in the chalkboard.
    chalkboard_crop = img_resized[150:500, 0:550]
    black_mask = (chalkboard_crop[:, :, 0] < 30) & (chalkboard_crop[:, :, 1] < 30) & (chalkboard_crop[:, :, 2] < 30)
    y_b, x_b = np.where(black_mask)
    if len(x_b) > 0:
        print(f"\nBlack pixels (hand/arm) in chalkboard region:")
        print(f"  X range: {min(x_b)} ~ {max(x_b)}")
        print(f"  Y range: {min(y_b) + 150} ~ {max(y_b) + 150}")
        
    white_mask = (chalkboard_crop[:, :, 0] > 200) & (chalkboard_crop[:, :, 1] > 200) & (chalkboard_crop[:, :, 2] > 200)
    y_w, x_w = np.where(white_mask)
    if len(x_w) > 0:
        print(f"\nWhite pixels (chalk drawings/hand highlight) in chalkboard region:")
        print(f"  X range: {min(x_w)} ~ {max(x_w)}")
        print(f"  Y range: {min(y_w) + 150} ~ {max(y_w) + 150}")
        
else:
    print("Could not read image.")
