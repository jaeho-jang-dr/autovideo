import os
import cv2
import numpy as np
import math

output_dir = r"d:\Entertainments\DevEnvironment\autovideo\scratch\vocab_assets"
os.makedirs(output_dir, exist_ok=True)

def create_transparent_canvas(w, h):
    return np.zeros((h, w, 4), dtype=np.uint8)

# 1. Stickman (300x500)
def draw_stickman():
    img = create_transparent_canvas(300, 500)
    color = (28, 28, 28, 255) # Clean charcoal black
    thick = 6 # Bold line-art weight
    
    # Head (Circle)
    cv2.circle(img, (150, 100), 45, color, thick)
    # Eyes
    cv2.circle(img, (135, 95), 4, color, -1)
    cv2.circle(img, (165, 95), 4, color, -1)
    # Mouth (neutral friendly curve)
    cv2.ellipse(img, (150, 115), (8, 5), 0, 0, 180, color, thick - 2)
    # Spine (Body line)
    cv2.line(img, (150, 145), (150, 320), color, thick)
    
    # Left Arm
    cv2.line(img, (150, 180), (100, 240), color, thick)
    # Right Arm
    cv2.line(img, (150, 180), (200, 240), color, thick)
    
    # Left Leg
    cv2.line(img, (150, 320), (110, 430), color, thick)
    cv2.line(img, (110, 430), (95, 430), color, thick) # Foot
    
    # Right Leg
    cv2.line(img, (150, 320), (190, 430), color, thick)
    cv2.line(img, (190, 430), (205, 430), color, thick) # Foot
    
    return img

# 2. Translation Icon (200x200)
def draw_translation_icon():
    img = create_transparent_canvas(200, 200)
    
    # Blue color palette matching the screenshot
    blue_dark = (120, 60, 25, 255) # RGBA (BGR: 25, 60, 120) -> deep blue
    blue_light = (235, 160, 40, 255) # RGBA -> bright blue
    
    # Let's draw using OpenCV
    # Left/Upper bubble (Dark blue)
    pts_bubble1 = np.array([
        [40, 40], [120, 40], [120, 100], [80, 100], [60, 120], [60, 100], [40, 100]
    ], np.int32)
    cv2.fillPoly(img, [pts_bubble1], (115, 66, 32, 255)) # Dark Blue-grey
    cv2.polylines(img, [pts_bubble1], True, (255, 255, 255, 255), 3)
    
    # Text "A" inside upper bubble
    cv2.putText(img, "A", (65, 82), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255, 255), 3, cv2.LINE_AA)
    
    # Right/Lower bubble (Secondary dark blue)
    pts_bubble2 = np.array([
        [90, 90], [170, 90], [170, 150], [150, 150], [150, 170], [130, 150], [90, 150]
    ], np.int32)
    cv2.fillPoly(img, [pts_bubble2], (95, 52, 24, 255))
    cv2.polylines(img, [pts_bubble2], True, (255, 255, 255, 255), 3)
    
    # Text "文" inside lower bubble
    # Since 文 is Unicode, let's draw using Pillow inside the compile script or render path.
    # To keep this clean, let's write simple lines representing 文 or use a temporary shape.
    # We will draw a Chinese letter representation with lines:
    cv2.line(img, (115, 110), (145, 110), (255, 255, 255, 255), 3) # top bar
    cv2.line(img, (130, 103), (130, 110), (255, 255, 255, 255), 3) # top dot
    cv2.line(img, (130, 110), (115, 135), (255, 255, 255, 255), 3) # left sweep
    cv2.line(img, (126, 117), (145, 135), (255, 255, 255, 255), 3) # right sweep
    
    # Light-blue circular arrows around the bubbles
    cv2.ellipse(img, (100, 100), (75, 75), 0, 200, 300, (235, 160, 40, 255), 4) # top arrow curve
    cv2.ellipse(img, (100, 100), (75, 75), 0, 20, 120, (235, 160, 40, 255), 4)  # bottom arrow curve
    
    # Arrow heads
    cv2.line(img, (168, 72), (175, 60), (235, 160, 40, 255), 4)
    cv2.line(img, (168, 72), (155, 78), (235, 160, 40, 255), 4)
    
    cv2.line(img, (32, 128), (25, 140), (235, 160, 40, 255), 4)
    cv2.line(img, (32, 128), (45, 122), (235, 160, 40, 255), 4)
    
    return img

# 3. Window (250x300)
def draw_window():
    img = create_transparent_canvas(250, 300)
    color = (28, 28, 28, 255)
    thick = 5
    # Perspective window frame matching screenshot
    cv2.line(img, (20, 70), (160, 20), color, thick)
    cv2.line(img, (160, 20), (160, 220), color, thick)
    cv2.line(img, (160, 220), (20, 270), color, thick)
    cv2.line(img, (20, 270), (20, 70), color, thick)
    
    # Window sill block at bottom
    cv2.line(img, (10, 260), (10, 275), color, thick)
    cv2.line(img, (10, 275), (180, 220), color, thick)
    cv2.line(img, (180, 220), (180, 205), color, thick)
    cv2.line(img, (180, 205), (10, 260), color, thick)
    
    # Inner glass frame dividers
    cv2.line(img, (90, 45), (90, 245), color, thick - 1)
    cv2.line(img, (20, 170), (160, 120), color, thick - 2)
    
    # Small flower pot sitting on sill
    cv2.rectangle(img, (115, 200), (145, 225), color, thick - 1) # Pot
    cv2.ellipse(img, (130, 195), (10, 7), 0, 180, 360, color, thick - 2) # Leaf left
    cv2.ellipse(img, (130, 195), (7, 10), 0, 210, 330, color, thick - 2) # Leaf center
    return img

# 4. Fan (250x250)
def draw_fan():
    img = create_transparent_canvas(250, 250)
    color = (28, 28, 28, 255)
    thick = 5
    # Outer grill
    cv2.circle(img, (125, 100), 75, color, thick)
    cv2.circle(img, (125, 100), 20, color, thick)
    
    # Blades (4 blades)
    for a in [0, 90, 180, 270]:
        rad = math.radians(a)
        # Petal-like blades
        cx = int(125 + 40 * math.cos(rad))
        cy = int(100 + 40 * math.sin(rad))
        cv2.ellipse(img, (cx, cy), (25, 15), a, 0, 360, color, thick - 1)
        
    # Stand neck
    cv2.line(img, (125, 175), (125, 215), color, thick)
    # Bottom stand base
    cv2.ellipse(img, (125, 215), (45, 12), 0, 0, 360, color, thick)
    return img

# 5. Bag (250x250)
def draw_bag():
    img = create_transparent_canvas(250, 250)
    color = (28, 28, 28, 255)
    thick = 5
    # Main round body
    cv2.ellipse(img, (125, 140), (65, 80), 0, 180, 360, color, thick)
    cv2.line(img, (60, 140), (60, 220), color, thick)
    cv2.line(img, (190, 140), (190, 220), color, thick)
    cv2.ellipse(img, (125, 220), (65, 12), 0, 0, 180, color, thick)
    
    # Outer front pocket
    cv2.rectangle(img, (85, 160), (165, 215), color, thick)
    
    # Side pocket
    cv2.ellipse(img, (58, 170), (10, 20), 0, 90, 270, color, thick)
    
    # Top carry loop
    cv2.ellipse(img, (125, 60), (20, 20), 0, 180, 360, color, thick)
    return img

# 6. Chair (250x300)
def draw_chair():
    img = create_transparent_canvas(250, 300)
    color = (28, 28, 28, 255)
    thick = 5
    # Curved backrest
    cv2.ellipse(img, (125, 75), (55, 45), 0, 180, 360, color, thick)
    cv2.line(img, (70, 75), (70, 150), color, thick)
    cv2.line(img, (180, 75), (180, 150), color, thick)
    
    # Circular Seat cushion
    cv2.ellipse(img, (125, 150), (60, 20), 0, 0, 360, color, thick)
    
    # Legs (4 legs with perspective angle)
    cv2.line(img, (75, 165), (75, 270), color, thick)   # Front-left
    cv2.line(img, (175, 165), (175, 270), color, thick) # Front-right
    cv2.line(img, (95, 168), (95, 240), color, thick)   # Back-left
    cv2.line(img, (155, 168), (155, 240), color, thick) # Back-right
    return img

# 7. Bottle (250x250)
def draw_bottle():
    img = create_transparent_canvas(250, 250)
    color = (28, 28, 28, 255)
    thick = 5
    # Ribbed water bottle cylinder
    cv2.line(img, (95, 90), (95, 220), color, thick)
    cv2.line(img, (155, 90), (155, 220), color, thick)
    cv2.ellipse(img, (125, 220), (30, 10), 0, 0, 180, color, thick) # base
    
    # Rib grips (inner ellipses)
    cv2.ellipse(img, (125, 130), (30, 6), 0, 0, 180, color, thick - 1)
    cv2.ellipse(img, (125, 170), (30, 6), 0, 0, 180, color, thick - 1)
    
    # Neck and cap
    cv2.ellipse(img, (125, 90), (30, 6), 0, 0, 360, color, thick)
    cv2.line(img, (110, 90), (110, 65), color, thick)
    cv2.line(img, (140, 90), (140, 65), color, thick)
    cv2.rectangle(img, (105, 45), (145, 65), color, thick) # cap
    cv2.circle(img, (125, 45), (6), color, -1)             # tip loop
    return img

# 8. Phone (250x250)
def draw_phone():
    img = create_transparent_canvas(250, 250)
    color = (28, 28, 28, 255)
    thick = 5
    # Tilted phone outline (25 degrees angle)
    rect = ((125, 125), (90, 170), 25)
    box = cv2.boxPoints(rect)
    box = np.int32(np.round(box))
    cv2.drawContours(img, [box], 0, color, thick)
    
    # Inner screen
    screen_rect = ((125, 125), (76, 136), 25)
    screen_box = cv2.boxPoints(screen_rect)
    screen_box = np.int32(np.round(screen_box))
    cv2.drawContours(img, [screen_box], 0, color, thick - 2)
    
    # Home button circle (lower end)
    # Calculate offset along tilted axis: angle is 25 degrees
    # Home button center: (125 + dx, 125 + dy)
    angle_rad = math.radians(25 + 90) # points down the length
    btn_x = int(125 + 68 * math.cos(angle_rad))
    btn_y = int(125 + 68 * math.sin(angle_rad))
    cv2.circle(img, (btn_x, btn_y), 7, color, thick - 2)
    
    # Speaker bar (upper end)
    spk_x = int(125 - 68 * math.cos(angle_rad))
    spk_y = int(125 - 68 * math.sin(angle_rad))
    # Draw short line perpendicular to length
    perp_rad = math.radians(25)
    p1 = (int(spk_x - 12 * math.cos(perp_rad)), int(spk_y - 12 * math.sin(perp_rad)))
    p2 = (int(spk_x + 12 * math.cos(perp_rad)), int(spk_y + 12 * math.sin(perp_rad)))
    cv2.line(img, p1, p2, color, thick - 2)
    return img

def main():
    assets = {
        "stickman.png": draw_stickman(),
        "translation_icon.png": draw_translation_icon(),
        "window.png": draw_window(),
        "fan.png": draw_fan(),
        "bag.png": draw_bag(),
        "chair.png": draw_chair(),
        "bottle.png": draw_bottle(),
        "phone.png": draw_phone()
    }
    
    for filename, img in assets.items():
        out_path = os.path.join(output_dir, filename)
        cv2.imwrite(out_path, img)
        print(f"Generated clean black outline asset: {out_path}")

if __name__ == '__main__':
    main()
