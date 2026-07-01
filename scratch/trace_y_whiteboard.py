import cv2
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_whiteboard_writing_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    
    # Trace column x=400 (which is inside the whiteboard) from y=0 to 720
    # to find the top and bottom borders (black lines where BGR < 50)
    col_x = 400
    print("Tracing y values at x=400:")
    black_y = []
    for y in range(720):
        bgr = img_resized[y, col_x]
        if bgr[0] < 50 and bgr[1] < 50 and bgr[2] < 50:
            black_y.append(y)
            
    print(f"Detected black pixels at y coordinates: {black_y}")
    
    # Let's print some segments of black_y to see the border coordinates
    # Usually we will see clusters of black pixels at the top border and bottom border
    
else:
    print("Could not read image.")
