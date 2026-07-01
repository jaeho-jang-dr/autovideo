import cv2
import numpy as np

body_path = r"d:\Entertainments\DevEnvironment\autovideo\scratch\layers\body.png"
wheel_path = r"d:\Entertainments\DevEnvironment\autovideo\scratch\layers\wheel.png"

body = cv2.imread(body_path, cv2.IMREAD_UNCHANGED)
wheel = cv2.imread(wheel_path, cv2.IMREAD_UNCHANGED)

body_h, body_w = body.shape[:2]
body_x = (1280 - body_w) // 2
body_y = (720 - body_h) // 2

# Create a solid navy background canvas [B=47, G=25, R=10]
canvas = np.zeros((720, 1280, 4), dtype=np.uint8)
canvas[:, :] = [10, 25, 47, 255] # Solid BGRA

# Alpha blend body onto the canvas
body_alpha = body[:, :, 3] / 255.0
for c in range(3):
    canvas[body_y:body_y+body_h, body_x:body_x+body_w, c] = (
        body[:, :, c] * body_alpha + 
        canvas[body_y:body_y+body_h, body_x:body_x+body_w, c] * (1.0 - body_alpha)
    ).astype(np.uint8)

# Draw a coordinate grid on the canvas
grid_canvas = canvas.copy()
for x in range(0, 1280, 50):
    cv2.line(grid_canvas, (x, 0), (x, 720), (200, 200, 200, 255), 1)
    if x % 100 == 0:
        cv2.putText(grid_canvas, str(x), (x, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (250, 250, 250, 255), 1)
        
for y in range(0, 720, 50):
    cv2.line(grid_canvas, (0, y), (1280, y), (200, 200, 200, 255), 1)
    if y % 100 == 0:
        cv2.putText(grid_canvas, str(y), (10, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (250, 250, 250, 255), 1)

cv2.imwrite(r"d:\Entertainments\DevEnvironment\autovideo\scratch\body_grid.png", grid_canvas)
print("Saved body grid image to scratch/body_grid.png")
