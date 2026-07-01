import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    crop = img_resized[250:600, 500:750]
    
    # Stickman is black (BGR < 30)
    mask = (crop[:, :, 0] < 30) & (crop[:, :, 1] < 30) & (crop[:, :, 2] < 30)
    y_idx, x_idx = np.where(mask)
    coords = list(zip(x_idx + 500, y_idx + 250))
    
    print(f"Total stickman black pixels in cropped region: {len(coords)}")
    if len(coords) > 0:
        print(f"X range: {min(x_idx + 500)} ~ {max(x_idx + 500)}")
        print(f"Y range: {min(y_idx + 250)} ~ {max(y_idx + 250)}")
        
        # Let's count occurrence of X coordinates
        from collections import Counter
        x_counts = Counter([c[0] for c in coords])
        print("\nMost common X coordinates in crop:")
        for x, count in x_counts.most_common(10):
            print(f"  x={x}: {count} pixels")
            
        # Top 10 Y coordinates
        y_counts = Counter([c[1] for c in coords])
        print("Top 10 Y coordinates in crop:")
        for y, count in y_counts.most_common(10):
            print(f"  y={y}: {count} pixels")
            
        # Let's find head / shoulder / spine:
        # Topmost region of crop (y: 250 ~ 350)
        top_coords = [c for c in coords if c[1] < 350]
        if len(top_coords) > 0:
            top_xs = [c[0] for c in top_coords]
            top_ys = [c[1] for c in top_coords]
            print(f"\nTopmost pixels (y < 350):")
            print(f"  X range: {min(top_xs)} ~ {max(top_xs)}")
            print(f"  Y range: {min(top_ys)} ~ {max(top_ys)}")
            print(f"  Mean: ({int(np.mean(top_xs))}, {int(np.mean(top_ys))})")
else:
    print("Could not read image.")
