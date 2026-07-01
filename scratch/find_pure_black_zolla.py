import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    
    # Stickman BGR should be very close to [0, 0, 0]
    # Let's say B < 30, G < 30, R < 30
    h, w, _ = img_resized.shape
    mask = (img_resized[:, :, 0] < 30) & (img_resized[:, :, 1] < 30) & (img_resized[:, :, 2] < 30)
    
    y_idx, x_idx = np.where(mask)
    coords = list(zip(x_idx, y_idx))
    
    print(f"Total stickman black pixels: {len(coords)}")
    print(f"X range: {min(x_idx)} ~ {max(x_idx)}")
    print(f"Y range: {min(y_idx)} ~ {max(y_idx)}")
    
    # Print vertical line peaks in the stickman region (x > 450)
    xs_stick = [c[0] for c in coords if c[0] > 450]
    from collections import Counter
    x_counts = Counter(xs_stick)
    print("\nMost common X coordinates of stickman (vertical lines):")
    for x, count in x_counts.most_common(10):
        print(f"  x={x}: {count} pixels")
        
    # Let's find the head center: topmost part
    min_y = min(y_idx)
    head_ys = [c[1] for c in coords if c[1] < min_y + 60]
    head_xs = [c[0] for c in coords if c[1] < min_y + 60]
    print(f"Head Y range: {min(head_ys)} ~ {max(head_ys)}")
    print(f"Head X range: {min(head_xs)} ~ {max(head_xs)}")
    print(f"Head Center: ({int(np.mean(head_xs))}, {int(np.mean(head_ys))})")
    
    # Spine/Body vertical line:
    # Let's see the Y range of pixels along the main vertical line (e.g. x = 642)
    spine_pixels = [c for c in coords if 640 <= c[0] <= 644]
    print(f"Spine pixels count: {len(spine_pixels)}")
    if len(spine_pixels) > 0:
        ys_spine = [c[1] for c in spine_pixels]
        print(f"Spine Y range: {min(ys_spine)} ~ {max(ys_spine)}")
        
    # Rest of the arms:
    # Let's print out all black pixels with x < 635 (which should be the original right arm pointing to the board!)
    right_arm_pixels = [c for c in coords if c[0] < 635]
    print(f"Right arm pixels count (x < 635): {len(right_arm_pixels)}")
    if len(right_arm_pixels) > 0:
        ra_xs = [c[0] for c in right_arm_pixels]
        ra_ys = [c[1] for c in right_arm_pixels]
        print(f"  Right arm X range: {min(ra_xs)} ~ {max(ra_xs)}")
        print(f"  Right arm Y range: {min(ra_ys)} ~ {max(ra_ys)}")
        
else:
    print("Could not read image.")
