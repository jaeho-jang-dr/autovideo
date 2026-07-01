import cv2
import numpy as np

def get_transparent_char(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
        
    # Ensure 4 channels
    if img.shape[2] == 3:
        # Add alpha channel
        alpha = np.full((img.shape[0], img.shape[1], 1), 255, dtype=np.uint8)
        img = np.concatenate((img, alpha), axis=2)
        
    # Get corner pixel color as background sample
    bg_sample = img[5, 5, :3].astype(float)
    
    # Calculate distance to background color
    diff = img[:, :, :3].astype(float) - bg_sample
    dist = np.sqrt(np.sum(diff ** 2, axis=2))
    
    # Set pixels close to background color to transparent
    img[dist < 40, 3] = 0
    
    # Crop to non-transparent bounding box
    alpha = img[:, :, 3]
    ys, xs = np.where(alpha > 10)
    if len(ys) > 0:
        min_y, max_y = ys.min(), ys.max()
        min_x, max_x = xs.min(), xs.max()
        cropped = img[min_y:max_y+1, min_x:max_x+1]
        return cropped
        
    return img

def split_parts(char_img):
    H, W = char_img.shape[:2]
    
    parts = {
        "head": char_img[0:int(H*0.23), :],
        "torso": char_img[int(H*0.23):int(H*0.63), :],
        "arm_l": char_img[int(H*0.23):int(H*0.60), int(W*0.62):],
        "arm_r": char_img[int(H*0.23):int(H*0.60), :int(W*0.38)],
        "leg_l": char_img[int(H*0.63):, int(W*0.48):],
        "leg_r": char_img[int(H*0.63):, :int(W*0.52)]
    }
    
    # Trim each part's transparency bounds to prevent empty borders
    trimmed_parts = {}
    for name, part in parts.items():
        alpha = part[:, :, 3]
        ys, xs = np.where(alpha > 5)
        if len(ys) > 0:
            trimmed_parts[name] = part[ys.min():ys.max()+1, xs.min():xs.max()+1]
        else:
            trimmed_parts[name] = part
            
    return trimmed_parts

def draw_part_on_bone(canvas, part_img, pt_a, pt_b, pivot_in_part, thickness_scale=1.0):
    H_p, W_p = part_img.shape[:2]
    dist = np.hypot(pt_b[0] - pt_a[0], pt_b[1] - pt_a[1])
    if dist < 5.0:
        return
        
    angle = np.arctan2(pt_b[1] - pt_a[1], pt_b[0] - pt_a[0])
    rot_angle = angle - np.pi/2
    
    scale_y = dist / H_p
    scale_x = scale_y * thickness_scale
    
    new_w = int(max(1, W_p * scale_x))
    new_h = int(max(1, H_p * scale_y))
    resized = cv2.resize(part_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    px = int(pivot_in_part[0] * scale_x)
    py = int(pivot_in_part[1] * scale_y)
    
    T1 = np.array([[1, 0, -px],
                   [0, 1, -py],
                   [0, 0, 1]], dtype=float)
    cos_a = np.cos(rot_angle)
    sin_a = np.sin(rot_angle)
    R = np.array([[cos_a, -sin_a, 0],
                  [sin_a, cos_a, 0],
                  [0, 0, 1]], dtype=float)
    T2 = np.array([[1, 0, pt_a[0]],
                   [0, 1, pt_a[1]],
                   [0, 0, 1]], dtype=float)
    
    M = T2 @ R @ T1
    M = M[:2, :]
    
    h_c, w_c = canvas.shape[:2]
    warped = cv2.warpAffine(resized, M, (w_c, h_c), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    
    rgb_w = warped[:, :, :3]
    alpha_w = warped[:, :, 3] / 255.0
    alpha_w = np.expand_dims(alpha_w, axis=2)
    
    canvas[:, :, :3] = (1.0 - alpha_w) * canvas[:, :, :3] + alpha_w * rgb_w
    canvas[:, :, :3] = canvas[:, :, :3].astype(np.uint8)

def draw_rigged_character(canvas, kp, cf, parts, gender="female", thr=0.3):
    def P(i): return (int(kp[i,0]), int(kp[i,1])) if cf[i] > thr else None
    
    sh_l, sh_r = P(5), P(6)
    hip_l, hip_r = P(11), P(12)
    
    if not (sh_l and sh_r and hip_l and hip_r):
        return
        
    sh_mid = ((sh_l[0]+sh_r[0])//2, (sh_l[1]+sh_r[1])//2)
    hip_mid = ((hip_l[0]+hip_r[0])//2, (hip_l[1]+hip_r[1])//2)
    
    pts = [P(i) for i in (0,1,2,3,4) if P(i)]
    if pts:
        hc = (int(np.mean([p[0] for p in pts])), int(np.mean([p[1] for p in pts])))
    else:
        shw = np.hypot(sh_l[0]-sh_r[0], sh_l[1]-sh_r[1])
        hc = (sh_mid[0], int(sh_mid[1] - shw * 0.7))
        
    # Draw body parts in depth order: legs, torso, arms, head
    # Thickness scale adjusts the horizontal width of the parts
    thickness_leg = 1.2 if gender == "male" else 1.0
    thickness_arm = 1.0
    thickness_torso = 1.1 if gender == "male" else 1.0
    
    # 1. Legs
    for leg_name, hip_j, ankle_j in [("leg_l", 11, 15), ("leg_r", 12, 16)]:
        h_pt = P(hip_j)
        a_pt = P(ankle_j)
        if h_pt and a_pt:
            part_img = parts[leg_name]
            pivot = (part_img.shape[1] // 2, 0)
            draw_part_on_bone(canvas, part_img, h_pt, a_pt, pivot, thickness_leg)
            
    # 2. Torso
    part_torso = parts["torso"]
    pivot_torso = (part_torso.shape[1] // 2, 0)
    # We slightly scale torso thickness based on shoulder width vs spine length
    draw_part_on_bone(canvas, part_torso, sh_mid, hip_mid, pivot_torso, thickness_torso)
    
    # 3. Arms
    for arm_name, sh_j, wr_j in [("arm_l", 5, 9), ("arm_r", 6, 10)]:
        s_pt = P(sh_j)
        w_pt = P(wr_j)
        if s_pt and w_pt:
            part_img = parts[arm_name]
            pivot = (part_img.shape[1] // 2, 0)
            draw_part_on_bone(canvas, part_img, s_pt, w_pt, pivot, thickness_arm)
            
    # 4. Head
    part_head = parts["head"]
    pivot_head = (part_head.shape[1] // 2, int(part_head.shape[0] * 0.85)) # chin/neck
    # Draw head pointing from sh_mid through hc
    # To prevent head elongation, we match target distance to head's original height
    shw = np.hypot(sh_l[0]-sh_r[0], sh_l[1]-sh_r[1])
    head_h = shw * 0.95
    # Calculate target head top coordinate
    dx, dy = hc[0] - sh_mid[0], hc[1] - sh_mid[1]
    dh = np.hypot(dx, dy) or 1.0
    head_top = (int(sh_mid[0] + dx/dh * (dh + head_h)), int(sh_mid[1] + dy/dh * (dh + head_h)))
    draw_part_on_bone(canvas, part_head, sh_mid, head_top, pivot_head, 1.0)

def test():
    jieun = get_transparent_char("home_vocab/jieun_base_front.png")
    injun = get_transparent_char("home_vocab/injun_base_front.png")
    
    # Create a mock pose (standing)
    kp = np.array([
        [640, 200], # nose
        [630, 190], # leye
        [650, 190], # reye
        [620, 195], # lear
        [660, 195], # rear
        [580, 280], # lsh
        [700, 280], # rsh
        [560, 380], # lel
        [720, 380], # rel
        [550, 480], # lwr
        [730, 480], # rwr
        [600, 480], # lhip
        [680, 480], # rhip
        [600, 580], # lkn
        [680, 580], # rkn
        [600, 680], # lan
        [680, 680]  # ran
    ], dtype=float)
    cf = np.ones(17)
    
    canvas = np.full((720, 1280, 3), (212, 230, 240), dtype=np.uint8) # BEIGE
    
    if jieun is not None:
        jieun_parts = split_parts(jieun)
        draw_rigged_character(canvas, kp, cf, jieun_parts, gender="female")
        cv2.imwrite("scratch/rigging_test_jieun.png", canvas)
        print("Successfully rendered and saved scratch/rigging_test_jieun.png")
        
    canvas = np.full((720, 1280, 3), (212, 230, 240), dtype=np.uint8) # BEIGE
    if injun is not None:
        injun_parts = split_parts(injun)
        # Shift pose slightly to the left
        kp_injun = kp.copy()
        kp_injun[:, 0] -= 200
        draw_rigged_character(canvas, kp_injun, cf, injun_parts, gender="male")
        cv2.imwrite("scratch/rigging_test_injun.png", canvas)
        print("Successfully rendered and saved scratch/rigging_test_injun.png")

if __name__ == "__main__":
    test()
