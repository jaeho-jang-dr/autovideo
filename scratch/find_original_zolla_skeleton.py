import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    
    # Stickman is black (value < 100)
    y_idx, x_idx = np.where(gray < 100)
    coords = list(zip(x_idx, y_idx))
    
    print(f"Total dark pixels: {len(coords)}")
    print(f"X range: {min(x_idx)} ~ {max(x_idx)}")
    print(f"Y range: {min(y_idx)} ~ {max(y_idx)}")
    
    # Let's count occurrence of X coordinates
    from collections import Counter
    x_counts = Counter(x_idx)
    print("\nMost common X coordinates (vertical lines):")
    for x, count in x_counts.most_common(10):
        print(f"  x={x}: {count} pixels")
        
    # Let's see if there are black pixels in x=500 to 520, which is where they thought the spine was!
    x_500_520 = [c for c in coords if 500 <= c[0] <= 520]
    print(f"\nNumber of dark pixels in x=500~520: {len(x_500_520)}")
    if len(x_500_520) > 0:
        ys_500_520 = [c[1] for c in x_500_520]
        print(f"  Y range in x=500~520: {min(ys_500_520)} ~ {max(ys_500_520)}")
        
    # Let's print out the spine of the stickman: where is it?
    # Usually a stickman has a head, spine, arms, legs.
    # Let's print all coordinates around y = 370 to 390
    print("\nDark pixels around Y=380:")
    y380_coords = [c for c in coords if 378 <= c[1] <= 382]
    # Group by X
    x_to_ys = {}
    for cx, cy in y380_coords:
        if cx not in x_to_ys:
            x_to_ys[cx] = []
        x_to_ys[cx].append(cy)
    for cx in sorted(x_to_ys.keys()):
        print(f"  x={cx}: ys={x_to_ys[cx]}")
else:
    print("Could not read image.")
