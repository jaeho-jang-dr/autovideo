import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    # Let's search for pixels with B < 50, G < 50, R < 50 (black lines of stickman)
    # in the region x: 480~700, y: 200~650
    crop = img_resized[200:650, 500:900]
    
    y_idx, x_idx = np.where((crop[:, :, 0] < 50) & (crop[:, :, 1] < 50) & (crop[:, :, 2] < 50))
    
    # Absolute coordinates in 1280x720
    coords = [(x + 500, y + 200) for y, x in zip(y_idx, x_idx)]
    print(f"Number of black/dark pixels: {len(coords)}")
    
    # Print out X distribution to find vertical lines (spine/legs)
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    
    if len(coords) > 0:
        print(f"X range of black pixels: {min(xs)} ~ {max(xs)}")
        print(f"Y range of black pixels: {min(ys)} ~ {max(ys)}")
        
        # Let's print the coordinate counts for X
        from collections import Counter
        x_counts = Counter(xs)
        print("Top 10 X coordinates:")
        for x, count in x_counts.most_common(10):
            print(f"  x={x}: {count} pixels")
            
        # Top 10 Y coordinates
        y_counts = Counter(ys)
        print("Top 10 Y coordinates:")
        for y, count in y_counts.most_common(10):
            print(f"  y={y}: {count} pixels")
            
else:
    print("Could not read image.")
