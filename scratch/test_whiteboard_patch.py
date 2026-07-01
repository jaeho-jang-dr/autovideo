import cv2
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_whiteboard_writing_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    test_img = img_resized.copy()
    
    # Whiteboard inner area: x: 290 ~ 1000, y: 40 ~ 454
    
    # 1. Left chalkboard region (x: 290 ~ 530, y: 40 ~ 454)
    test_img[40:455, 290:530] = (255, 255, 255)
    
    # 2. Right chalkboard region behind Jay (x: 740 ~ 1000, y: 40 ~ 454)
    test_img[40:455, 740:1000] = (255, 255, 255)
    
    # 3. Precision erases to clean remaining marker parts close to Jay's face
    # y: 170 ~ 200 -> erase up to x: 573 (erases floating residue at y=170~185, head profile is at x=577)
    test_img[170:200, 530:573] = (255, 255, 255)
    # y: 200 ~ 230 -> erase up to x: 570 (cheek is at x: 580)
    test_img[200:230, 530:570] = (255, 255, 255)
    # y: 230 ~ 270 -> erase up to x: 580 (neck is at x: 611)
    test_img[230:270, 530:580] = (255, 255, 255)
    # y: 270 ~ 455 -> erase up to x: 570 (shoulder is at x: 599)
    test_img[270:455, 530:570] = (255, 255, 255)
    
    # Draw the active arm
    r_shoulder = (648, 280)
    mx, my = 300, 200
    r_hand = (mx, my)
    mid_x = (r_shoulder[0] + r_hand[0]) // 2
    mid_y = (r_shoulder[1] + r_hand[1]) // 2
    r_elbow = (int(mid_x - 15), int(mid_y + 30))
    
    arm_color = (17, 17, 17)
    stroke_w = 4
    cv2.line(test_img, r_shoulder, r_elbow, arm_color, stroke_w, cv2.LINE_AA)
    cv2.line(test_img, r_elbow, r_hand, arm_color, stroke_w, cv2.LINE_AA)
    cv2.line(test_img, r_hand, (r_hand[0] - 15, r_hand[1] - 10), (17, 17, 17), 6, cv2.LINE_AA) # marker stroke
    
    out_dir_gemini = r"C:\Users\antigravity\.gemini\antigravity\brain\ddcce0ae-4499-40e2-a60b-84f4b372fe49"
    os.makedirs(out_dir_gemini, exist_ok=True)
    
    out_path = os.path.join(out_dir_gemini, "test_whiteboard_patch.png")
    cv2.imwrite(out_path, test_img)
    print(f"Test whiteboard patched image saved to {out_path}")
else:
    print("Could not read image.")
