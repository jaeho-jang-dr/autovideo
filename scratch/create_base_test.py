import os
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_text_lineart_on_board(word, output_path):
    base_img_path = os.path.join(ROOT, "assets", "characters", "jay_whiteboard_writing_side_opaque.png")
    if not os.path.exists(base_img_path):
        print(f"[ERR] Base image not found: {base_img_path}")
        return False
        
    # Read and resize to 1280x720
    img = cv2.imread(base_img_path)
    img_resized = cv2.resize(img, (1280, 720))
    
    # 1. Clear chalkboard regions & original right arm precision masks
    # Whiteboard active inner area is x: 290 ~ 1000, y: 40 ~ 454
    
    # Block A: Complete left side of board (x: 290 ~ 480, y: 40 ~ 454)
    img_resized[40:454, 290:480] = (255, 255, 255)
    
    # Block B: Right side behind Jay's head (x: 732 ~ 1000, y: 40 ~ 454) - erases "각" completely
    img_resized[40:454, 732:1000] = (255, 255, 255)
    
    # Block C: Fine erase behind Jay's ear/head (x: 720 ~ 735, y: 190 ~ 280)
    img_resized[190:280, 720:735] = (255, 255, 255)
    
    # Block D: In front of face, above left arm (x: 480 ~ 560, y: 100 ~ 315) - erases marker/hand
    img_resized[100:315, 480:560] = (255, 255, 255)
    
    # Block E: In front of torso, below left arm (x: 480 ~ 600, y: 365 ~ 454) - erases lower right arm
    img_resized[365:454, 480:600] = (255, 255, 255)
    
    # Block F: Upper right arm starting near shoulder (x: 570 ~ 620, y: 280 ~ 315)
    img_resized[280:315, 570:620] = (255, 255, 255)
    
    # Convert to PIL Image for drawing text
    pil_img = Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # Load Font
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    if not os.path.exists(font_path):
        font_path = "arial.ttf"
    try:
        font = ImageFont.truetype(font_path, 180)
    except IOError:
        font = ImageFont.load_default()
        
    # Calculate word size & position
    try:
        bbox = draw.textbbox((0, 0), word, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except AttributeError:
        # Fallback for older PIL versions
        tw, th = draw.textsize(word, font=font)
        bbox = [0, 0, tw, th]
        
    # Center position on the left-side whiteboard (X: 290 ~ 530, center is around 410)
    # But wait, original "제이의" was at x: 290 ~ 450.
    # If we center it, let's put it at pos_x = 410 - tw//2
    # Vertically, board center is 247. pos_y = 247 - th//2
    pos_x = 410 - tw // 2
    pos_y = 247 - th // 2
    
    # Offset adjustment for text drawing
    draw.text((pos_x - bbox[0], pos_y - bbox[1]), word, fill=(17, 17, 17), font=font)
    
    # Save image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, cv2_img)
    print(f"[OK] Generated base image with word '{word}' -> {output_path}")
    return True

if __name__ == "__main__":
    test_out = os.path.join(ROOT, "assets", "characters", "jay_whiteboard_base_word_1.png")
    generate_text_lineart_on_board("강", test_out)
