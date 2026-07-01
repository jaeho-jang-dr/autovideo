# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_base_image_for_word(word, output_path):
    base_img_path = os.path.join(ROOT, "assets", "characters", "jay_whiteboard_writing_side_opaque.png")
    if not os.path.exists(base_img_path):
        print(f"[ERR] Base image not found: {base_img_path}")
        return False
        
    # Read base image and resize to 1280x720 (standard video/composition size)
    img = cv2.imread(base_img_path)
    img_resized = cv2.resize(img, (1280, 720))
    
    # 1. Apply precision erasure masks to clear original arm and letters
    # Whiteboard active inner area is x: 290 ~ 1000, y: 40 ~ 454
    
    # Block A: Complete left side of board (x: 290 ~ 480, y: 40 ~ 454) - erases "제이의"
    img_resized[40:454, 290:480] = (255, 255, 255)
    
    # Block B: Right side behind Jay's head (x: 732 ~ 1000, y: 40 ~ 454) - erases "각"
    img_resized[40:454, 732:1000] = (255, 255, 255)
    
    # Block C: Fine erase behind Jay's ear/head (x: 720 ~ 735, y: 190 ~ 280)
    img_resized[190:280, 720:735] = (255, 255, 255)
    
    # Block D: In front of face, above left arm (x: 480 ~ 560, y: 100 ~ 315) - erases marker/hand
    img_resized[100:315, 480:560] = (255, 255, 255)
    
    # Block E: In front of torso, below left arm (x: 480 ~ 600, y: 365 ~ 454) - erases lower right arm
    img_resized[365:454, 480:600] = (255, 255, 255)
    
    # Block F: Upper right arm starting near shoulder (x: 570 ~ 620, y: 280 ~ 315)
    img_resized[280:315, 570:620] = (255, 255, 255)
    
    # 2. Convert to PIL Image for high-quality text overlay
    pil_img = Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # Load Malgun Gothic (system font on Windows)
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    if not os.path.exists(font_path):
        font_path = "arial.ttf"
    try:
        font = ImageFont.truetype(font_path, 180)
    except IOError:
        font = ImageFont.load_default()
        
    # Calculate text bounding box for centering
    try:
        bbox = draw.textbbox((0, 0), word, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except AttributeError:
        tw, th = draw.textsize(word, font=font)
        bbox = [0, 0, tw, th]
        
    # Center word horizontally on the left chalkboard area (X: 290 ~ 480, center is around 385)
    # Vertically centered on chalkboard (Y: 40 ~ 454, center is around 247)
    pos_x = 385 - tw // 2
    pos_y = 247 - th // 2
    
    draw.text((pos_x - bbox[0], pos_y - bbox[1]), word, fill=(17, 17, 17), font=font)
    
    # Save the resulting composite BGR image
    cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, cv2_img)
    print(f"[OK] Generated reference image for '{word}' -> {output_path}")
    return True

def main():
    words = ["강", "물", "꽃", "불", "차"]
    print("=== Generating 5 Whiteboard Base Images for Google Flow ===")
    for idx, w in enumerate(words):
        out_name = f"jay_whiteboard_base_word_{idx+1}.png"
        out_path = os.path.join(ROOT, "assets", "characters", out_name)
        generate_base_image_for_word(w, out_path)
    print("=== Base Image Generation Completed! ===")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
