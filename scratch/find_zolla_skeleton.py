import cv2
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    # We will search for black pixels in the region around the stickman (x: 480~700, y: 200~650)
    # The stickman is black (or dark color) on a green background.
    # Let's count pixels where R < 80, G < 80, B < 80
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    
    # We are interested in the region x: 480~700, y: 200~650
    crop = gray[200:650, 480:700]
    # Let's find coordinates of dark pixels (value < 100)
    y_indices, x_indices = np.where(crop < 100)
    
    # Map back to 1280x720 coordinates
    absolute_coords = []
    for y, x in zip(y_indices, x_indices):
        absolute_coords.append((x + 480, y + 200))
        
    print(f"Total dark pixels found: {len(absolute_coords)}")
    
    # Let's print out some representative coordinate lines/clusters to identify parts
    # 1. Head: circular structure. Let's find the head region (topmost dark pixels)
    y_coords = [c[1] for c in absolute_coords]
    min_y = min(y_coords)
    max_y = max(y_coords)
    print(f"Y range of zollaman: {min_y} ~ {max_y}")
    
    # Topmost pixels (y < min_y + 60) should contain the head
    head_pixels = [c for c in absolute_coords if c[1] < min_y + 60]
    head_x = [c[0] for c in head_pixels]
    head_y = [c[1] for c in head_pixels]
    print(f"Head center approx: ({int(np.mean(head_x))}, {int(np.mean(head_y))})")
    
    # Let's find the vertical line (spine) which should be around x = 510 or 648
    # Let's count occurrences of x-coordinates
    x_coords = [c[0] for c in absolute_coords]
    from collections import Counter
    x_counts = Counter(x_coords)
    most_common_x = x_counts.most_common(5)
    print("Most common X coordinates (vertical lines):")
    for x, count in most_common_x:
        print(f"  x={x}: {count} pixels")
        
    # Let's print all coordinates around y = 300 to 450 to see the shoulders/spine/arm
    print("\nCoordinates around Y=350 to Y=400:")
    for c in sorted(absolute_coords):
        if 350 <= c[1] <= 400 and c[0] % 5 == 0:
            print(f"  {c}")
            
else:
    print("Could not read image.")
