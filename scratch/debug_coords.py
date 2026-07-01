import cv2
import os

img_path = r"C:\Users\antigravity\.gemini\antigravity\brain\4455adca-9bdd-4ddd-a2f1-84e32a8bad0a\scene_18_first_frame.png"
output_path = r"C:\Users\antigravity\.gemini\antigravity\brain\4455adca-9bdd-4ddd-a2f1-84e32a8bad0a\coords_debug.png"

img = cv2.imread(img_path)
if img is None:
    print("Failed to load first frame image")
    exit()

# Try coordinates to inspect overlay positions
# Bounding boxes for incorrect labels (x1, y1, x2, y2)
masks = {
    "CAPITATE_top": (625, 275, 695, 315),
    "CAPITATE_mid": (575, 325, 645, 365),
    "SCAPHOID": (605, 370, 695, 410),
    "HAMATE_left": (535, 430, 605, 490),
    "LUNATE_mid": (610, 435, 680, 495),
    "SOAPE_IUID": (565, 490, 645, 550),
    "Bottom_area": (460, 550, 860, 720)
}

# 8 Carpal bone center points (x, y)
bones = {
    "Trapezium": (660, 295),
    "Trapezoid": (610, 345),
    "Capitate": (650, 390),
    "Scaphoid": (570, 390),
    "Hamate": (645, 465),
    "Lunate": (570, 460),
    "Triquetrum": (535, 490),
    "Pisiform": (605, 520)
}

# Draw masks as semi-transparent green boxes
overlay = img.copy()
for name, box in masks.items():
    x1, y1, x2, y2 = box
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1)
cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)

# Draw bone text centers as red dots with names
for name, pt in bones.items():
    x, y = pt
    cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
    cv2.putText(img, name, (x + 8, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

cv2.imwrite(output_path, img)
print(f"Debug image saved to {output_path}")
