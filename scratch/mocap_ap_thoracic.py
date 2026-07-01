# -*- coding: utf-8 -*-
"""AP Thoracic Chiropractic Motion Capture & Retargeting with Rigged Characters.
Extracts 2-person motion (Injoon as adjuster, Jieun as patient) from ap_thoracic.mp4,
tracks them, applies temporal smoothing, and renders them by warping and overlaying
their actual character PNG parts onto a high-res 1280x720 canvas.
Flashes the adjustment close-up at the thrust moment.
"""
import os, sys
import numpy as np, cv2
from ultralytics import YOLO

# COCO-17 keypoint indices
NOSE,LEYE,REYE,LEAR,REAR,LSH,RSH,LEL,REL,LWR,RWR,LHIP,RHIP,LKN,RKN,LAN,RAN = range(17)
BEIGE=(212,230,240)     # Beige background (BGR #F5F5F0)

def get_transparent_char(img_path):
    """Load image and make the beige background color transparent, cropping to bounding box."""
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
        
    if img.shape[2] == 3:
        alpha = np.full((img.shape[0], img.shape[1], 1), 255, dtype=np.uint8)
        img = np.concatenate((img, alpha), axis=2)
        
    bg_sample = img[5, 5, :3].astype(float)
    diff = img[:, :, :3].astype(float) - bg_sample
    dist = np.sqrt(np.sum(diff ** 2, axis=2))
    img[dist < 40, 3] = 0
    
    alpha = img[:, :, 3]
    ys, xs = np.where(alpha > 10)
    if len(ys) > 0:
        min_y, max_y = ys.min(), ys.max()
        min_x, max_x = xs.min(), xs.max()
        return img[min_y:max_y+1, min_x:max_x+1]
    return img

def split_parts(char_img):
    """Split the full-body character image into logical body parts based on relative ratios."""
    H, W = char_img.shape[:2]
    parts = {
        "head": char_img[0:int(H*0.23), :],
        "torso": char_img[int(H*0.23):int(H*0.63), :],
        "arm_l": char_img[int(H*0.23):int(H*0.60), int(W*0.62):],
        "arm_r": char_img[int(H*0.23):int(H*0.60), :int(W*0.38)],
        "leg_l": char_img[int(H*0.63):, int(W*0.48):],
        "leg_r": char_img[int(H*0.63):, :int(W*0.52)]
    }
    
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
    """Scale, rotate, and draw a cropped body part aligned from pt_a to pt_b on the canvas."""
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
    """Draw all body parts of a rigged character based on keypoints."""
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
        
    # Scale factors for male vs female proportions
    thickness_leg = 1.2 if gender == "male" else 1.0
    thickness_arm = 1.0
    thickness_torso = 1.1 if gender == "male" else 1.0
    
    # 1. Legs (LHIP->LAN, RHIP->RAN)
    for leg_name, hip_j, ankle_j in [("leg_l", 11, 15), ("leg_r", 12, 16)]:
        h_pt = P(hip_j)
        a_pt = P(ankle_j)
        if h_pt and a_pt:
            part_img = parts[leg_name]
            pivot = (part_img.shape[1] // 2, 0)
            draw_part_on_bone(canvas, part_img, h_pt, a_pt, pivot, thickness_leg)
            
    # 2. Torso (sh_mid -> hip_mid)
    part_torso = parts["torso"]
    pivot_torso = (part_torso.shape[1] // 2, 0)
    draw_part_on_bone(canvas, part_torso, sh_mid, hip_mid, pivot_torso, thickness_torso)
    
    # 3. Arms (LSH->LWR, RSH->RWR)
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
    
    shw = np.hypot(sh_l[0]-sh_r[0], sh_l[1]-sh_r[1])
    head_h = shw * 0.95
    dx, dy = hc[0] - sh_mid[0], hc[1] - sh_mid[1]
    dh = np.hypot(dx, dy) or 1.0
    head_top = (int(sh_mid[0] + dx/dh * (dh + head_h)), int(sh_mid[1] + dy/dh * (dh + head_h)))
    draw_part_on_bone(canvas, part_head, sh_mid, head_top, pivot_head, 1.0)

def smooth_seq(kps, win=7):
    """Smooth keypoints sequence using temporal moving average to reduce jitter."""
    n = len(kps)
    if n == 0: return kps
    arr = np.stack(kps)
    out = arr.copy()
    h = win // 2
    for t in range(n):
        a = max(0, t - h)
        b = min(n, t + h + 1)
        out[t] = arr[a:b].mean(axis=0)
    return [out[t] for t in range(n)]

def get_person_center(kp, cf, thr=0.3):
    valid = kp[cf > thr]
    if len(valid) > 0:
        return valid.mean(axis=0)
    return kp.mean(axis=0)

def main():
    video_path = r"G:\내 드라이브\chiropracticos\archive\videos\techniques\ap_thoracic.mp4"
    out_path = r"ap_thoracic/scene_1.mp4"
    
    model = YOLO("yolov8s-pose.pt")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open source video: {video_path}")
        return
        
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Source video: {src_w}x{src_h}, {fps} FPS, {total_frames} frames")
    
    # Load character assets
    jieun_raw = get_transparent_char("home_vocab/jieun_base_front.png")
    injun_raw = get_transparent_char("home_vocab/injun_base_front.png")
    
    if jieun_raw is None or injun_raw is None:
        print("Error: Could not load characters from home_vocab/")
        return
        
    jieun_parts = split_parts(jieun_raw)
    injun_parts = split_parts(injun_raw)
    
    # Target high-resolution canvas size (1280x720)
    tgt_w, tgt_h = 1280, 720
    scale_x = tgt_w / src_w
    scale_y = tgt_h / src_h
    
    # Phase 1: Keypoints extraction & tracking
    injoon_kps, injoon_cfs = [], []
    jieun_kps, jieun_cfs = [], []
    
    injoon_last_kp = np.zeros((17, 2))
    injoon_last_cf = np.zeros(17)
    jieun_last_kp = np.zeros((17, 2))
    jieun_last_cf = np.zeros(17)
    
    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
            
        res = model.predict(frame, verbose=False, imgsz=640)[0]
        detected = []
        if res.keypoints is not None and len(res.keypoints) > 0:
            kxy = res.keypoints.xy.cpu().numpy()
            kcf = res.keypoints.conf
            kcf = kcf.cpu().numpy() if kcf is not None else np.ones((kxy.shape[0], 17))
            
            for kp, cf in zip(kxy, kcf):
                valid = kp[cf > 0.3]
                if len(valid) > 0:
                    min_x, max_x = valid[:, 0].min(), valid[:, 0].max()
                    min_y, max_y = valid[:, 1].min(), valid[:, 1].max()
                    w = max_x - min_x
                    h = max_y - min_y
                    detected.append({
                        "kp": kp.astype(float),
                        "cf": cf.astype(float),
                        "w": w,
                        "h": h,
                        "center": get_person_center(kp, cf)
                    })
                    
        assigned_injoon = None
        assigned_jieun = None
        
        # We classify by width of bounding box
        # Patient (Jieun) is lying down and has a wide bounding box
        # Chiropractor (Injoon) stands next and is more vertical
        if len(detected) >= 2:
            detected_sorted = sorted(detected, key=lambda x: x["w"], reverse=True)
            assigned_jieun = detected_sorted[0]
            assigned_injoon = detected_sorted[1]
        elif len(detected) == 1:
            p = detected[0]
            if p["w"] > p["h"] * 1.1 or p["center"][0] > src_w * 0.45:
                assigned_jieun = p
            else:
                assigned_injoon = p
                
        if assigned_injoon is not None:
            injoon_last_kp = assigned_injoon["kp"]
            injoon_last_cf = assigned_injoon["cf"]
        injoon_kps.append(injoon_last_kp.copy())
        injoon_cfs.append(injoon_last_cf.copy())
        
        if assigned_jieun is not None:
            jieun_last_kp = assigned_jieun["kp"]
            jieun_last_cf = assigned_jieun["cf"]
        jieun_kps.append(jieun_last_kp.copy())
        jieun_cfs.append(jieun_last_cf.copy())
        
        frame_idx += 1
        
    cap.release()
    
    # Phase 2: Temporal Smoothing (win=7 to handle supine layout jitter)
    injoon_kps = smooth_seq(injoon_kps, win=7)
    jieun_kps = smooth_seq(jieun_kps, win=7)
    
    # Scale keypoints to high-res canvas
    for t in range(len(injoon_kps)):
        injoon_kps[t][:, 0] *= scale_x
        injoon_kps[t][:, 1] *= scale_y
        jieun_kps[t][:, 0] *= scale_x
        jieun_kps[t][:, 1] *= scale_y
        
    # Phase 3: Render to output mp4
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(out_path, fourcc, fps, (tgt_w, tgt_h))
    
    adjust_closeup = cv2.imread("assets/ap_thoracic_closeup.png")
    if adjust_closeup is not None:
        print("[INFO] Loaded assets/ap_thoracic_closeup.png for flash effect.")
    else:
        print("[WARN] Could not load assets/ap_thoracic_closeup.png.")
        
    for frame_idx, (kp_m, cf_m, kp_g, cf_g) in enumerate(zip(injoon_kps, injoon_cfs, jieun_kps, jieun_cfs)):
        canvas = np.full((tgt_h, tgt_w, 3), BEIGE, np.uint8)
        
        # Display 0.1s adjustment close-up flash at frames 247-248 (thrust moment)
        if frame_idx in (247, 248) and adjust_closeup is not None:
            canvas = cv2.resize(adjust_closeup, (tgt_w, tgt_h))
        else:
            # Draw patient (Jieun) first, then chiropractor (Injoon) in front
            draw_rigged_character(canvas, kp_g, cf_g, jieun_parts, gender="female")
            draw_rigged_character(canvas, kp_m, cf_m, injun_parts, gender="male")
            
        vw.write(canvas)
        
    vw.release()
    print(f"[SUCCESS] Exported rigged AP thoracic animation -> {out_path} ({len(injoon_kps)} frames)")

if __name__ == "__main__":
    main()
