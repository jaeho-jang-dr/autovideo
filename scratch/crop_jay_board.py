import cv2
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    # Resize to 1280x720 to match video scale
    img_resized = cv2.resize(img, (1280, 720))
    # Crop the region around Jay (x: 450~700, y: 250~650)
    crop = img_resized[250:650, 450:700]
    out_path = os.path.join(ROOT, "scratch", "jay_cropped_board.png")
    cv2.imwrite(out_path, crop)
    print(f"Cropped Jay saved to {out_path}")
else:
    print("Could not read base image.")
