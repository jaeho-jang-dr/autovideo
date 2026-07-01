import cv2
import os
import numpy as np

out_dir = r"C:\Users\antigravity\.gemini\antigravity\brain\ddcce0ae-4499-40e2-a60b-84f4b372fe49"
img_path = os.path.join(out_dir, "test_patched_arm.png")
img = cv2.imread(img_path)

if img is not None:
    # Let's inspect the vertical slice at columns 635 to 650, rows 270 to 470
    # to see if there is any green/chalkboard color (around BGR [70, 97, 63]) or wall color [225, 239, 238]
    # crossing the spine.
    # The spine is a black line.
    # Let's print out the min value in each row in the range x=635~650 (this should be the spine line, which is dark)
    print("Spine profile (Row: min BGR in x=635~650):")
    spine_ok = True
    for y in range(270, 470, 10):
        row_slice = img[y, 635:650]
        # Find the darkest pixel in this horizontal slice
        darkest_pixel = min(row_slice, key=lambda p: int(p[0]) + int(p[1]) + int(p[2]))
        val = int(darkest_pixel[0]) + int(darkest_pixel[1]) + int(darkest_pixel[2])
        print(f"  y={y}: darkest pixel color={darkest_pixel} (sum={val})")
        # If the darkest pixel is very light (e.g. sum > 300), it means the spine line is missing!
        if val > 300:
            print(f"  WARNING: Missing spine line at y={y}!")
            spine_ok = False
            
    if spine_ok:
        print("SUCCESS: The spine line is fully intact along the entire patch height!")
    else:
        print("FAIL: The spine line has gaps/cuts!")
else:
    print("Could not read test image.")
