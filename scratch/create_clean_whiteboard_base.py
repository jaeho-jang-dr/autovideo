# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    base_img_path = os.path.join(ROOT, "assets", "characters", "jay_whiteboard_writing_side_opaque.png")
    if not os.path.exists(base_img_path):
        print(f"[ERR] Base image not found: {base_img_path}")
        return 1
        
    img = cv2.imread(base_img_path)
    img_resized = cv2.resize(img, (1280, 720))
    
    # Apply precision block erasures (derived from Rhc version testing)
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
    
    out_path = os.path.join(ROOT, "assets", "characters", "jay_whiteboard_clean_base.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, img_resized)
    print(f"[OK] Generated pure clean whiteboard base image -> {out_path}")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
