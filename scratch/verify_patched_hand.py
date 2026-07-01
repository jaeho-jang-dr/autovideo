import cv2
import os
import numpy as np

out_dir = r"C:\Users\antigravity\.gemini\antigravity\brain\ddcce0ae-4499-40e2-a60b-84f4b372fe49"
img_path = os.path.join(out_dir, "test_patched_shoulder_648_280_full_hand.png")
img = cv2.imread(img_path)

if img is not None:
    # We will search for black pixels in the region where the original hand was (x: 485~550, y: 200~290).
    # Since we drew a new arm in test_patched_shoulder_648_280_full_hand.png, some of those pixels will belong to the new arm!
    # But wait, let's just make sure there is no leftover "unpatched" black pixels.
    # The new arm is drawn from (648, 280) to (300, 200).
    # Let's count black pixels in x: 450~550, y: 200~260 (which is above the new arm, since the new arm goes from 648 to 300, at y=200~280).
    # Wait, the new arm line: y goes from 280 to 200, so it is below y=200, but let's check.
    # Let's just find if the region x: 485~550, y: 203~260 has any black pixels.
    # The new arm line goes through (648, 280) to elbow, and elbow is at (int(mid_x-15), int(mid_y+30)).
    # mid_x = 474, mid_y = 240, elbow = (459, 270).
    # The line segment 1: (648, 280) to (459, 270). The y range is 270~280.
    # The line segment 2: (459, 270) to (300, 200). The y range is 200~270.
    # So for y = 200~260, the line x goes from 300 to 459.
    # So for x > 480 and y < 260, there should be NO black pixels from the new arm!
    # In the original image, the hand was at x: 485~549, y: 203~260.
    # Let's count black pixels in x: 480~550, y: 200~260 in the test image.
    crop = img[200:260, 480:550]
    mask = (crop[:, :, 0] < 30) & (crop[:, :, 1] < 30) & (crop[:, :, 2] < 30)
    y_idx, x_idx = np.where(mask)
    
    print(f"Number of black pixels in test image at x=480~550, y=200~260: {len(x_idx)}")
    if len(x_idx) == 0:
        print("SUCCESS: The hand is completely erased!")
    else:
        print(f"FAIL: Hand pixels still found at x={min(x_idx)+480}~{max(x_idx)+480}, y={min(y_idx)+200}~{max(y_idx)+200}!")
else:
    print("Could not read test image.")
