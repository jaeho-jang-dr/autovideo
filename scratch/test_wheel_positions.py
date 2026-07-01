import cv2
import numpy as np

body_path = r"d:\Entertainments\DevEnvironment\autovideo\scratch\layers\body.png"
wheel_path = r"d:\Entertainments\DevEnvironment\autovideo\scratch\layers\wheel.png"

body = cv2.imread(body_path, cv2.IMREAD_UNCHANGED)
wheel = cv2.imread(wheel_path, cv2.IMREAD_UNCHANGED)

body_h, body_w = body.shape[:2]
body_x = (1280 - body_w) // 2
body_y = (720 - body_h) // 2

# We will test two coordinate sets:
# Option A: Rear=450, Front=850, Y=480
# Option B: Rear=460, Front=820, Y=460
# Option C: Rear=440, Front=840, Y=470

options = [
    {"name": "OptionA", "rear_x": 450, "front_x": 850, "y": 480},
    {"name": "OptionB", "rear_x": 460, "front_x": 820, "y": 460},
    {"name": "OptionC", "rear_x": 440, "front_x": 840, "y": 470}
]

for opt in options:
    # Canvas with solid navy background
    canvas = np.zeros((720, 1280, 4), dtype=np.uint8)
    canvas[:, :] = [10, 25, 47, 255]
    
    # Draw body
    body_alpha = body[:, :, 3] / 255.0
    for c in range(3):
        canvas[body_y:body_y+body_h, body_x:body_x+body_w, c] = (
            body[:, :, c] * body_alpha + 
            canvas[body_y:body_y+body_h, body_x:body_x+body_w, c] * (1.0 - body_alpha)
        ).astype(np.uint8)
        
    # Draw wheels (rear and front)
    wh, ww = wheel.shape[:2]
    wheel_alpha = wheel[:, :, 3] / 255.0
    
    for wx in [opt["rear_x"], opt["front_x"]]:
        wy = opt["y"]
        # Center the wheel at (wx, wy)
        x1_dst = int(wx - ww // 2)
        y1_dst = int(wy - wh // 2)
        
        # Paste wheel
        for c in range(3):
            canvas[y1_dst:y1_dst+wh, x1_dst:x1_dst+ww, c] = (
                wheel[:, :, c] * wheel_alpha + 
                canvas[y1_dst:y1_dst+wh, x1_dst:x1_dst+ww, c] * (1.0 - wheel_alpha)
            ).astype(np.uint8)
            
    out_path = f"d:\\Entertainments\\DevEnvironment\\autovideo\\scratch\\alignment_{opt['name']}.png"
    cv2.imwrite(out_path, canvas)
    print(f"Saved {opt['name']} to {out_path}")
