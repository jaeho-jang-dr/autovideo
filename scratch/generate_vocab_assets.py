import os
import cv2
import numpy as np

output_dir = r"d:\Entertainments\DevEnvironment\autovideo\scratch\vocab_assets"
os.makedirs(output_dir, exist_ok=True)

# Helper to create a blank transparent 150x150 canvas
def create_canvas():
    return np.zeros((150, 150, 4), dtype=np.uint8)

# 1. 가방 (Bag)
def draw_bag():
    img = create_canvas()
    color = (255, 255, 255, 255) # White line art
    thick = 3
    # Body
    cv2.rectangle(img, (30, 50), (120, 130), color, thick)
    # Handle
    cv2.ellipse(img, (75, 50), (25, 25), 0, 180, 360, color, thick)
    # Pocket
    cv2.rectangle(img, (45, 85), (105, 120), color, thick)
    # Zipper line
    cv2.line(img, (30, 70), (120, 70), color, thick)
    return img

# 2. 자전거 (Bicycle)
def draw_bicycle():
    img = create_canvas()
    color = (255, 255, 255, 255)
    thick = 3
    # Left wheel
    cv2.circle(img, (45, 105), 22, color, thick)
    # Right wheel
    cv2.circle(img, (105, 105), 22, color, thick)
    # Frame lines
    cv2.line(img, (45, 105), (75, 105), color, thick) # chainstay
    cv2.line(img, (45, 105), (65, 65), color, thick)  # seatstay
    cv2.line(img, (75, 105), (65, 65), color, thick)  # seattube
    cv2.line(img, (75, 105), (95, 65), color, thick)  # downtube
    cv2.line(img, (65, 65), (95, 65), color, thick)   # toptube
    cv2.line(img, (95, 65), (105, 105), color, thick) # fork
    # Seat
    cv2.line(img, (65, 65), (65, 55), color, thick)
    cv2.line(img, (55, 55), (75, 55), color, thick)
    # Handlebars
    cv2.line(img, (95, 65), (95, 50), color, thick)
    cv2.line(img, (90, 50), (105, 50), color, thick)
    return img

# 3. 시계 (Clock)
def draw_clock():
    img = create_canvas()
    color = (255, 255, 255, 255)
    thick = 3
    # Outer circle
    cv2.circle(img, (75, 75), 55, color, thick)
    # Center dot
    cv2.circle(img, (75, 75), 4, color, -1)
    # Hour hand (pointing to 2 o'clock)
    cv2.line(img, (75, 75), (95, 55), color, thick + 1)
    # Minute hand (pointing to 12 o'clock)
    cv2.line(img, (75, 75), (75, 35), color, thick)
    # Hour tick marks
    cv2.line(img, (75, 25), (75, 30), color, thick)
    cv2.line(img, (75, 125), (75, 120), color, thick)
    cv2.line(img, (25, 75), (30, 75), color, thick)
    cv2.line(img, (125, 75), (120, 75), color, thick)
    return img

# 4. 책 (Book)
def draw_book():
    img = create_canvas()
    color = (255, 255, 255, 255)
    thick = 3
    # Left page outline
    cv2.line(img, (75, 50), (35, 40), color, thick)
    cv2.line(img, (35, 40), (35, 110), color, thick)
    cv2.line(img, (35, 110), (75, 120), color, thick)
    # Right page outline
    cv2.line(img, (75, 50), (115, 40), color, thick)
    cv2.line(img, (115, 40), (115, 110), color, thick)
    cv2.line(img, (115, 110), (75, 120), color, thick)
    # Center spine
    cv2.line(img, (75, 50), (75, 120), color, thick)
    # Text lines on left page
    cv2.line(img, (45, 65), (65, 70), color, 2)
    cv2.line(img, (45, 80), (65, 85), color, 2)
    cv2.line(img, (45, 95), (65, 100), color, 2)
    # Text lines on right page
    cv2.line(img, (85, 70), (105, 65), color, 2)
    cv2.line(img, (85, 85), (105, 80), color, 2)
    cv2.line(img, (85, 100), (105, 95), color, 2)
    return img

# 5. 안경 (Glasses)
def draw_glasses():
    img = create_canvas()
    color = (255, 255, 255, 255)
    thick = 3
    # Left lens
    cv2.circle(img, (45, 75), 20, color, thick)
    # Right lens
    cv2.circle(img, (105, 75), 20, color, thick)
    # Bridge
    cv2.ellipse(img, (75, 75), (15, 10), 0, 180, 360, color, thick)
    # Temple arms (left and right)
    cv2.line(img, (25, 75), (15, 60), color, thick)
    cv2.line(img, (125, 75), (135, 60), color, thick)
    return img

# 6. 신발 (Shoes)
def draw_shoes():
    img = create_canvas()
    color = (255, 255, 255, 255)
    thick = 3
    # Sole
    cv2.line(img, (25, 115), (125, 115), color, thick)
    # Heel
    cv2.line(img, (25, 115), (25, 80), color, thick)
    # Ankle collar
    cv2.line(img, (25, 80), (55, 80), color, thick)
    # Tongue & front slope
    cv2.line(img, (55, 80), (75, 100), color, thick)
    cv2.line(img, (75, 100), (125, 115), color, thick)
    # Toe cap
    cv2.ellipse(img, (125, 110), (10, 5), 0, 270, 90, color, thick)
    # Laces
    cv2.line(img, (60, 90), (70, 80), color, 2)
    cv2.line(img, (70, 90), (60, 80), color, 2)
    return img

# 7. 연필 (Pencil)
def draw_pencil():
    img = create_canvas()
    color = (255, 255, 255, 255)
    thick = 3
    # Body lines
    cv2.line(img, (20, 60), (105, 60), color, thick)
    cv2.line(img, (20, 90), (105, 90), color, thick)
    # Eraser collar
    cv2.line(img, (20, 60), (20, 90), color, thick)
    cv2.rectangle(img, (10, 60), (20, 90), color, thick)
    # Pencil lines
    cv2.line(img, (20, 75), (105, 75), color, 2)
    # Cone tip
    cv2.line(img, (105, 60), (135, 75), color, thick)
    cv2.line(img, (105, 90), (135, 75), color, thick)
    # Pencil lead tip
    pts = np.array([[120, 68], [135, 75], [120, 82]], np.int32)
    cv2.polylines(img, [pts], False, color, thick)
    return img

# 8. 우산 (Umbrella)
def draw_umbrella():
    img = create_canvas()
    color = (255, 255, 255, 255)
    thick = 3
    # Canopy dome
    cv2.ellipse(img, (75, 75), (50, 40), 0, 180, 360, color, thick)
    # Canopy bottom wavy curves
    cv2.ellipse(img, (40, 75), (15, 10), 0, 0, 180, color, thick)
    cv2.ellipse(img, (75, 75), (20, 10), 0, 0, 180, color, thick)
    cv2.ellipse(img, (110, 75), (15, 10), 0, 0, 180, color, thick)
    # Shaft
    cv2.line(img, (75, 35), (75, 115), color, thick)
    # Handle (J-hook)
    cv2.ellipse(img, (65, 115), (10, 10), 0, 0, 180, color, thick)
    return img

# 9. 모자 (Hat)
def draw_hat():
    img = create_canvas()
    color = (255, 255, 255, 255)
    thick = 3
    # Brim (Ellipse)
    cv2.ellipse(img, (75, 105), (55, 15), 0, 0, 360, color, thick)
    # Cap Dome
    cv2.ellipse(img, (75, 100), (35, 45), 0, 180, 360, color, thick)
    # Hat ribbon line
    cv2.ellipse(img, (75, 102), (35, 10), 0, 180, 360, color, thick)
    return img

# 10. 컵 (Cup)
def draw_cup():
    img = create_canvas()
    color = (255, 255, 255, 255)
    thick = 3
    # Main Cylinder
    cv2.line(img, (55, 45), (55, 115), color, thick)
    cv2.line(img, (115, 45), (115, 115), color, thick)
    # Bottom Curve
    cv2.ellipse(img, (85, 115), (30, 10), 0, 0, 180, color, thick)
    # Top Rim
    cv2.ellipse(img, (85, 45), (30, 8), 0, 0, 360, color, thick)
    # Handle on the left
    cv2.ellipse(img, (55, 80), (18, 25), 0, 90, 270, color, thick)
    return img

def main():
    assets = {
        "bag.png": draw_bag(),
        "bicycle.png": draw_bicycle(),
        "clock.png": draw_clock(),
        "book.png": draw_book(),
        "glasses.png": draw_glasses(),
        "shoes.png": draw_shoes(),
        "pencil.png": draw_pencil(),
        "umbrella.png": draw_umbrella(),
        "hat.png": draw_hat(),
        "cup.png": draw_cup()
    }
    
    for filename, img in assets.items():
        out_path = os.path.join(output_dir, filename)
        cv2.imwrite(out_path, img)
        print(f"Generated line-art icon: {out_path} (Size: {img.shape})")

if __name__ == '__main__':
    main()
