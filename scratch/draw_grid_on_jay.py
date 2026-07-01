import cv2
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    # We will draw a coordinate grid on the image from x=450 to 700, and y=250 to 650
    # Let's draw horizontal and vertical lines every 10 pixels in this region, and labels every 50 pixels.
    grid_img = img_resized.copy()
    
    # Let's draw vertical lines
    for x in range(450, 700, 10):
        color = (0, 0, 255) if x % 50 == 0 else (200, 200, 200)
        thick = 2 if x % 50 == 0 else 1
        cv2.line(grid_img, (x, 250), (x, 650), color, thick)
        if x % 50 == 0:
            cv2.putText(grid_img, str(x), (x, 245), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            
    # Let's draw horizontal lines
    for y in range(250, 650, 10):
        color = (0, 0, 255) if y % 50 == 0 else (200, 200, 200)
        thick = 2 if y % 50 == 0 else 1
        cv2.line(grid_img, (450, y), (700, y), color, thick)
        if y % 50 == 0:
            cv2.putText(grid_img, str(y), (440, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            
    # Crop and save
    crop = grid_img[230:660, 430:720]
    out_dir = r"C:\Users\antigravity\.gemini\antigravity\brain\ddcce0ae-4499-40e2-a60b-84f4b372fe49"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "jay_cropped_board_grid.png")
    cv2.imwrite(out_path, crop)
    print(f"Grid image saved to {out_path}")
else:
    print("Could not read image.")
