import cv2
import os
import numpy as np

out_dir = r"C:\Users\antigravity\.gemini\antigravity\brain\ddcce0ae-4499-40e2-a60b-84f4b372fe49"
img_path = os.path.join(out_dir, "test_patched_shoulder_280.png")
img = cv2.imread(img_path)

if img is not None:
    print("Spine profile for y=270~460 (Row: min BGR in x=635~650):")
    spine_ok = True
    for y in range(270, 460, 10):
        row_slice = img[y, 635:650]
        darkest_pixel = min(row_slice, key=lambda p: int(p[0]) + int(p[1]) + int(p[2]))
        val = int(darkest_pixel[0]) + int(darkest_pixel[1]) + int(darkest_pixel[2])
        print(f"  y={y}: darkest pixel color={darkest_pixel} (sum={val})")
        if val > 300:
            print(f"  WARNING: Missing spine line at y={y}!")
            spine_ok = False
            
    if spine_ok:
        print("SUCCESS: The spine line is fully intact along the entire patch height!")
    else:
        print("FAIL: The spine line has gaps/cuts!")
else:
    print("Could not read test image.")
