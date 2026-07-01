import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    
    # Threshold to find dark pixels (stickman lines)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    
    # We focus on the region x: 450~800, y: 150~700
    mask = np.zeros_like(thresh)
    mask[150:700, 450:800] = thresh[150:700, 450:800]
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Number of contours found: {len(contours)}")
    
    # Let's find coordinates of dark pixels and cluster them by x and y
    y_idx, x_idx = np.where(mask > 0)
    
    # Let's count coordinates
    print(f"Min X: {np.min(x_idx)}, Max X: {np.max(x_idx)}")
    print(f"Min Y: {np.min(y_idx)}, Max Y: {np.max(y_idx)}")
    
    # Find head center: circular shape at the top.
    # Topmost part of the stickman: y between min_y and min_y + 80
    min_y = np.min(y_idx)
    head_y_mask = (y_idx >= min_y) & (y_idx <= min_y + 80)
    head_xs = x_idx[head_y_mask]
    head_ys = y_idx[head_y_mask]
    head_center_x = int(np.mean(head_xs))
    head_center_y = int(np.mean(head_ys))
    print(f"Detected Head Center: ({head_center_x}, {head_center_y})")
    
    # Neck: right below the head. Let's say y around head_center_y + 30
    # Spine: vertical line going down from neck. Let's find vertical lines by looking at X distribution.
    # We look at y between head_center_y + 40 and head_center_y + 120
    spine_y_mask = (y_idx >= head_center_y + 40) & (y_idx <= head_center_y + 120)
    spine_xs = x_idx[spine_y_mask]
    # Let's find the peak X coordinate
    from collections import Counter
    spine_x_counts = Counter(spine_xs)
    spine_x = spine_x_counts.most_common(1)[0][0]
    print(f"Detected Spine X: {spine_x}")
    
    # Hips: where spine ends. y around head_center_y + 120
    pelvis_y = head_center_y + 120
    print(f"Detected Pelvis Y (approx): {pelvis_y}")
    
    # Arms: let's look for dark pixels branching out from the spine at y around head_center_y + 40 to +60
    # Left arm (resting on hip): in the original image, it extends towards x > spine_x
    # Right arm (pointing to board): in the original image, it extends towards x < spine_x
    
    left_arm_pixels = []
    right_arm_pixels = []
    
    for x, y in zip(x_idx, y_idx):
        if head_center_y + 30 <= y <= pelvis_y + 30:
            if x > spine_x + 10:
                left_arm_pixels.append((x, y))
            elif x < spine_x - 10:
                right_arm_pixels.append((x, y))
                
    print(f"Left arm pixels count (x > spine_x + 10): {len(left_arm_pixels)}")
    if len(left_arm_pixels) > 0:
        la_xs = [p[0] for p in left_arm_pixels]
        la_ys = [p[1] for p in left_arm_pixels]
        print(f"  Left arm X range: {min(la_xs)} ~ {max(la_xs)}")
        print(f"  Left arm Y range: {min(la_ys)} ~ {max(la_ys)}")
        
    print(f"Right arm pixels count (x < spine_x - 10): {len(right_arm_pixels)}")
    if len(right_arm_pixels) > 0:
        ra_xs = [p[0] for p in right_arm_pixels]
        ra_ys = [p[1] for p in right_arm_pixels]
        print(f"  Right arm X range: {min(ra_xs)} ~ {max(ra_xs)}")
        print(f"  Right arm Y range: {min(ra_ys)} ~ {max(ra_ys)}")
        
else:
    print("Could not read image.")
