# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

# Force stdout/stderr to UTF-8
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Constants for Blackboard box in 1280x720 frames
BOARD_X1, BOARD_X2 = 290, 1000
BOARD_Y1, BOARD_Y2 = 40, 454

# Standard Font configuration
FONT_PATH = "C:\\Windows\\Fonts\\malgun.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "arial.ttf"

def extract_hand_trajectory(video_path):
    """
    Run YOLOv8-pose to track the right wrist (Keypoint 10) across all frames.
    Returns a smoothed list of (x, y) coordinates.
    """
    print(f"Tracking right hand wrist in: {video_path}...")
    model_path = os.path.join(ROOT, "yolov8n-pose.pt")
    if not os.path.exists(model_path):
        # Fallback to yolov8s-pose.pt if nano isn't found
        model_path = os.path.join(ROOT, "yolov8s-pose.pt")
        
    model = YOLO(model_path)
    
    cap = cv2.VideoCapture(video_path)
    trajectory = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Run pose detection on current frame (silent mode)
        results = model(frame, verbose=False, device="cpu")
        
        # Default fallback is hand at center of board if undetected
        hx, hy = (BOARD_X1 + BOARD_X2) // 2, (BOARD_Y1 + BOARD_Y2) // 2
        
        if len(results) > 0 and results[0].keypoints is not None:
            keypoints = results[0].keypoints.xy  # Coordinates on frame
            if len(keypoints) > 0 and len(keypoints[0]) > 10:
                wrist = keypoints[0][10] # Keypoint index 10 is right_wrist
                wx, wy = float(wrist[0]), float(wrist[1])
                if wx > 0 and wy > 0:
                    hx, hy = wx, wy
                    
        trajectory.append((hx, hy))
        
    cap.release()
    
    # Smooth coordinates using moving average (window=5)
    smoothed = []
    w_size = 5
    for i in range(len(trajectory)):
        start = max(0, i - w_size // 2)
        end = min(len(trajectory), i + w_size // 2 + 1)
        chunk = trajectory[start:end]
        avg_x = sum([pt[0] for pt in chunk]) / len(chunk)
        avg_y = sum([pt[1] for pt in chunk]) / len(chunk)
        smoothed.append((avg_x, avg_y))
        
    return smoothed

def generate_hangeul_stroke_mask(text, step_index):
    """
    Generate a 1280x720 binary mask where the text strokes are assigned a progress score (0 to 1)
    based on Hangeul stroke ordering (Consonant -> Vowel -> Coda).
    """
    img = Image.new("L", (1280, 720), 0)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(FONT_PATH, 110)
    except IOError:
        font = ImageFont.load_default()
        
    # Positioning the characters horizontally on the blackboard
    # "달" (scene 1), "그" (scene 2), "림" (scene 3), "자" (scene 4)
    # The whiteboard coordinates range from X: 290 to 1000. Center is ~645.
    # Let's align the 4 letters evenly:
    # Char 1 ("달"): x=410, y=200
    # Char 2 ("그"): x=530, y=200
    # Char 3 ("림"): x=650, y=200
    # Char 4 ("자"): x=770, y=200
    char_positions = [
        ("달", 410, 200),
        ("그", 530, 200),
        ("림", 650, 200),
        ("자", 770, 200)
    ]
    
    # We want to pre-render all characters up to the current step.
    # For example, in Scene 3 ("림"), "달" and "그" are already fully written (progress=1.0),
    # while "림" is actively being written (progress based on time), and "자" is not written yet.
    pixel_progress_map = np.zeros((720, 1280), dtype=np.float32)
    
    for idx, (char, cx, cy) in enumerate(char_positions):
        # Render this character into a temporary single-channel image
        char_img = Image.new("L", (1280, 720), 0)
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((cx, cy), char, fill=255, font=font)
        
        char_arr = np.array(char_img)
        y_indices, x_indices = np.where(char_arr > 0)
        if len(x_indices) == 0:
            continue
            
        xmin, xmax = x_indices.min(), x_indices.max()
        ymin, ymax = y_indices.min(), y_indices.max()
        
        # If this character is already fully written in previous scenes
        if idx < step_index:
            pixel_progress_map[char_arr > 0] = 0.001  # Instant reveal
        elif idx == step_index:
            # Active character stroke sequence decomposition
            for y, x in zip(y_indices, x_indices):
                # Calculate simple Hangeul stroke sequence estimation
                # Consonant (Top/Left) -> Vowel (Right/Middle) -> Coda (Bottom)
                h_pct = (x - xmin) / max(1, xmax - xmin)
                v_pct = (y - ymin) / max(1, ymax - ymin)
                
                # Assign reveal scores (0.01 to 1.0)
                if char == "달":
                    # 'ㄷ' (top/left) -> 'ㅏ' (right vertical) -> 'ㄹ' (bottom)
                    if v_pct < 0.45 and h_pct < 0.6:
                        score = 0.1 + h_pct * 0.2
                    elif h_pct >= 0.5 and v_pct < 0.7:
                        score = 0.4 + v_pct * 0.2
                    else:
                        score = 0.7 + h_pct * 0.25
                elif char == "그":
                    # 'ㄱ' (top) -> 'ㅡ' (bottom horizontal)
                    if v_pct < 0.5:
                        score = 0.1 + h_pct * 0.4
                    else:
                        score = 0.5 + h_pct * 0.4
                elif char == "림":
                    # 'ㄹ' (top) -> 'ㅣ' (right) -> 'ㅁ' (bottom)
                    if v_pct < 0.4:
                        score = 0.1 + h_pct * 0.25
                    elif h_pct >= 0.55 and v_pct < 0.7:
                        score = 0.4 + v_pct * 0.25
                    else:
                        score = 0.7 + h_pct * 0.25
                elif char == "자":
                    # 'ㅈ' (top/left) -> 'ㅏ' (right vertical)
                    if h_pct < 0.6:
                        score = 0.1 + h_pct * 0.4
                    else:
                        score = 0.5 + v_pct * 0.4
                else:
                    # Fallback gradient
                    score = 0.1 + h_pct * 0.6 + v_pct * 0.3
                    
                pixel_progress_map[y, x] = np.clip(score, 0.01, 1.0)
                
    return pixel_progress_map

def process_hybrid_scene(scene_idx):
    """
    Process a single Veo clip: track wrist, erase original text,
    and render precise dynamic strokes.
    """
    video_path = os.path.join(ROOT, "jay_ekf_whiteboard", f"scene_{scene_idx + 1}.mp4")
    out_video_path = os.path.join(ROOT, "jay_ekf_whiteboard", f"scene_{scene_idx + 1}_hybrid.mp4")
    
    if not os.path.exists(video_path):
        print(f"[ERR] Video clip not found: {video_path}")
        return False
        
    # 1. Track wrist coordinates
    hand_traj = extract_hand_trajectory(video_path)
    
    # 2. Setup text progress map
    progress_map = generate_hangeul_stroke_mask("달그림자", scene_idx)
    
    # 3. Read whiteboard clean base texture
    clean_base_path = os.path.join(ROOT, "assets", "characters", "jay_whiteboard_clean_base.png")
    if not os.path.exists(clean_base_path):
        print(f"[WARN] Clean whiteboard base not found, creating a flat white region fallback.")
        clean_base = np.ones((720, 1280, 3), dtype=np.uint8) * 245
    else:
        clean_base = cv2.imread(clean_base_path)
        
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_video_path, fourcc, fps, (width, height))
    
    print(f"Synthesizing hybrid video frames (total: {total_frames})...")
    
    # We define writing active frames (typically 0.5s to 6.5s in an 8s clip)
    # Let's dynamically map frames to writing progress.
    # We assume JAY starts writing around frame 15 and finishes by frame 190.
    start_writing_frame = 15
    end_writing_frame = min(total_frames - 15, 190)
    
    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Get hand pos
        hx, hy = hand_traj[min(frame_idx, len(hand_traj)-1)]
        
        # Calculate writing progress based on frame count
        if frame_idx < start_writing_frame:
            write_progress = 0.0
        elif frame_idx > end_writing_frame:
            write_progress = 1.0
        else:
            write_progress = (frame_idx - start_writing_frame) / (end_writing_frame - start_writing_frame)
            
        # Create output frame (start with original, we modify the blackboard region)
        output_frame = frame.copy()
        
        # Create clean board base layer
        board_layer = clean_base.copy()
        
        # Draw the active Hangeul text on the board layer
        # Mask out pixels whose stroke score > write_progress
        text_mask = (progress_map > 0) & (progress_map <= write_progress)
        
        # Dark charcoal color for the writing font (#2E2E2E / BGR: 46, 46, 46)
        board_layer[text_mask] = [46, 46, 46]
        
        # Draw also previous characters fully (progress=0.001)
        prev_mask = (progress_map == 0.001)
        board_layer[prev_mask] = [46, 46, 46]
        
        # Erase old AI text inside original frame by projecting the clean board layer
        # But we must preserve JAY the stickman on top.
        # Stickman Extraction:
        # In the original frame inside the board boundaries, JAY's lines are dark.
        # Let's extract the stickman mask.
        crop_orig = frame[BOARD_Y1:BOARD_Y2, BOARD_X1:BOARD_X2]
        crop_gray = cv2.cvtColor(crop_orig, cv2.COLOR_BGR2GRAY)
        
        # We perform thresholding: stickman is very dark (#000000)
        _, stickman_mask = cv2.threshold(crop_gray, 90, 255, cv2.THRESH_BINARY_INV)
        
        # Remove small noises using morphology (opening)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        stickman_mask = cv2.morphologyEx(stickman_mask, cv2.MORPH_OPEN, kernel)
        
        # Combine base board + text
        composite_board = board_layer[BOARD_Y1:BOARD_Y2, BOARD_X1:BOARD_X2].copy()
        
        # Overlay original JAY stickman on top of the writing board
        composite_board[stickman_mask > 0] = crop_orig[stickman_mask > 0]
        
        # Project back to the output frame
        output_frame[BOARD_Y1:BOARD_Y2, BOARD_X1:BOARD_X2] = composite_board
        
        # Write frame
        out.write(output_frame)
        frame_idx += 1
        
    cap.release()
    out.release()
    print(f"Saved hybrid scene: {out_video_path}\n")
    return True

def main():
    print("=== Start Hybrid AI Motion + Digital Handwriting Processor ===")
    for i in range(4):
        print(f"\n--- Processing Scene {i+1}/4 ---")
        success = process_hybrid_scene(i)
        if not success:
            print(f"[ERR] Failed to process Scene {i+1}")
            return 1
            
    print("All hybrid scenes successfully synthesized!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
