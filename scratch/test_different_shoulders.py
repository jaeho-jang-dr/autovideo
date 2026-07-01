import cv2
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
img = cv2.imread(img_path)

if img is not None:
    img_resized = cv2.resize(img, (1280, 720))
    
    # 1. Erase white circle
    patch_circle = img_resized[170:250, 200:280].copy()
    img_resized[170:250, 420:500] = patch_circle
    
    # 2. Erase the original right arm completely (y: 270~460, x: 380~635)
    # The source is empty chalkboard (rows 270~460, cols 200~455)
    patch_width = 635 - 380
    patch_height = 460 - 270
    patch_arm = img_resized[270:460, 200:200 + patch_width].copy()
    
    test_img = img_resized.copy()
    test_img[270:460, 380:635] = patch_arm
    
    # 3. Draw active arm starting from the neck/shoulder junction
    # We will test r_shoulder = (640, 280)
    r_shoulder = (640, 280)
    mx, my = 300, 200
    r_hand = (mx, my)
    mid_x = (r_shoulder[0] + r_hand[0]) // 2
    mid_y = (r_shoulder[1] + r_hand[1]) // 2
    # Elbow should bend slightly left/downwards
    r_elbow = (int(mid_x - 15), int(mid_y + 30))
    
    arm_color = (17, 17, 17)
    stroke_w = 4
    cv2.line(test_img, r_shoulder, r_elbow, arm_color, stroke_w, cv2.LINE_AA)
    cv2.line(test_img, r_elbow, r_hand, arm_color, stroke_w, cv2.LINE_AA)
    cv2.line(test_img, r_hand, (r_hand[0] - 15, r_hand[1] - 10), (245, 245, 245), 6, cv2.LINE_AA)
    
    out_dir = r"C:\Users\antigravity\.gemini\antigravity\brain\ddcce0ae-4499-40e2-a60b-84f4b372fe49"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "test_patched_shoulder_280.png")
    cv2.imwrite(out_path, test_img)
    print(f"Test patched shoulder 280 saved to {out_path}")
else:
    print("Could not read image.")
