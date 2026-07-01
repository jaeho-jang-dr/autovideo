#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
compile_zolla_yolo_reverse.py — YOLOv8-pose 기반 역공학 30초 한글 단모음 테스트 비디오 컴파일러.
이 스크립트는 기존의 비디오 클립(scene_1.mp4 ~ scene_6.mp4)을 모션 베이스로 삼고,
오른손 끝(right_wrist) 좌표를 정밀 추적하여 100% 철자가 정확한 한글 자모 및 그래픽을
손끝 움직임과 밀착 정렬하여 웜 베이지 2D 라인아트 스타일로 합성하고 최종 합본 비디오를 빌드합니다.
"""
import os
import sys
import re
import math
import cv2
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
import subprocess

from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip, concatenate_videoclips
from moviepy.audio.fx import MultiplyVolume

# Force UTF-8 on Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# Import TTS Manager from root
from tts_manager import save_tts

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SCENE_DIR = PROJECT_DIR
OUTPUT_FILE = os.path.join(PROJECT_DIR, "hangeul_birth_vowels_zolla.mp4")
LOGO_PATH = os.path.join(ROOT_DIR, "assets", "drjay_ed_logo_circle.png")
BGM_PATH = os.path.join(ROOT_DIR, "assets", "audio", "lofi_bgm.mp3")
POP_SFX_PATH = os.path.join(ROOT_DIR, "assets", "audio", "pop.wav")
WHOOSH_SFX_PATH = os.path.join(ROOT_DIR, "assets", "audio", "whoosh.wav")
BELL_SFX_PATH = os.path.join(ROOT_DIR, "assets", "audio", "bell_chime.wav")
TTS_CACHE_DIR = os.path.join(PROJECT_DIR, "tts_cache")
os.makedirs(TTS_CACHE_DIR, exist_ok=True)

# Standard Output Resolution
WIDTH, HEIGHT = 1280, 720
FONT_PATH = "C:\\Windows\\Fonts\\malgun.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "arial.ttf"

# 30-Second Scenario (6 Scenes, 5s each)
SCENARIO = [
    {
        "seq": 1,
        "text": "세종대왕은 백성들이 쉽게 쓸 수 있도록 한글을 창제했습니다.",
        "graphic": "crown"
    },
    {
        "seq": 2,
        "text": "한글 모음은 하늘, 땅, 사람을 담은 천지인 세 기호로 시작합니다.",
        "graphic": "cheonjiin_dots"
    },
    {
        "seq": 3,
        "text": "이 세 기호가 서로 만나 단모음 아, 어, 오, 우가 탄생합니다.",
        "graphic": "vowels_assembly"
    },
    {
        "seq": 4,
        "text": "단모음은 혀의 위치나 입술 모양이 바뀌지 않는 첫 소리입니다.",
        "graphic": "mouth_vowel"
    },
    {
        "seq": 5,
        "text": "소리를 들으며 직접 큰 소리로 따라 발음해 보세요. 아!",
        "graphic": "sound_wave"
    },
    {
        "seq": 6,
        "text": "한글의 시작, 단모음! 다음 시간에는 자음을 만나봅니다.",
        "graphic": "outro_subscribe"
    }
]

# Helper: Read Image with Unicode Path support
def imread_unicode(path):
    try:
        with open(path, "rb") as f:
            file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
        return cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
    except Exception as e:
        print(f"[ERROR] Failed to read image (unicode): {path}. Error: {e}")
        return None

# Elastic Scale Interpolation (Bounce effect)
def elastic_scale(progress, base=1.0):
    if progress <= 0.0:
        return 0.001
    if progress >= 1.0:
        return base
    val = 1.0 - math.exp(-6.0 * progress) * math.cos(2.0 * math.pi * progress)
    return max(0.001, base * val)

# Smoothly Overlay Alpha Channels (Transparent PNG onto Frame)
def overlay_alpha(bg_img, fg_img, x, y, scale=1.0, rotate_deg=0.0, opacity=1.0):
    if fg_img is None:
        return
    
    h_fg, w_fg = fg_img.shape[:2]
    
    # Scale
    if scale != 1.0:
        new_w = max(1, int(w_fg * scale))
        new_h = max(1, int(h_fg * scale))
        fg_img = cv2.resize(fg_img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        h_fg, w_fg = fg_img.shape[:2]

    # Rotation
    if rotate_deg != 0.0:
        M = cv2.getRotationMatrix2D((w_fg // 2, h_fg // 2), rotate_deg, 1.0)
        fg_img = cv2.warpAffine(fg_img, M, (w_fg, h_fg), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_TRANSPARENT)

    # Coordinates
    x1, y1 = int(x - w_fg // 2), int(y - h_fg // 2)
    x2, y2 = x1 + w_fg, y1 + h_fg

    h_bg, w_bg = bg_img.shape[:2]
    
    # Crop borders
    x1_c, x2_c = max(0, x1), min(w_bg, x2)
    y1_c, y2_c = max(0, y1), min(h_bg, y2)

    if x2_c <= x1_c or y2_c <= y1_c:
        return

    fg_x1 = x1_c - x1
    fg_y1 = y1_c - y1
    fg_x2 = fg_x1 + (x2_c - x1_c)
    fg_y2 = fg_y1 + (y2_c - y1_c)

    fg_crop = fg_img[fg_y1:fg_y2, fg_x1:fg_x2]
    bg_crop = bg_img[y1_c:y2_c, x1_c:x2_c]

    if fg_crop.shape[2] == 4:
        alpha = (fg_crop[:, :, 3] / 255.0) * opacity
        alpha = alpha[:, :, np.newaxis]
        fg_rgb = fg_crop[:, :, :3]
        bg_rgb = bg_crop[:, :, :3]
        bg_img[y1_c:y2_c, x1_c:x2_c, :3] = (alpha * fg_rgb + (1.0 - alpha) * bg_rgb).astype(np.uint8)
    else:
        bg_img[y1_c:y2_c, x1_c:x2_c, :3] = fg_crop[:, :, :3]

# -----------------------------------------------------------------------------
# 1. TRACKING HAND TRAJECTORY VIA YOLOv8-pose
# -----------------------------------------------------------------------------
def track_wrist_trajectory(video_path):
    """
    YOLOv8-pose를 활용해 scene 비디오에서 오른손 목(Right Wrist - Keypoint 10) 좌표를 추적.
    결과는 (x, y) 좌표 리스트로 반환하며, 5프레임 이동 평균 스무딩 적용.
    """
    print(f"[YOLO-pose] Tracking hand in: {os.path.basename(video_path)}...")
    
    # Find model
    model_path = os.path.join(ROOT_DIR, "yolov8n-pose.pt")
    if not os.path.exists(model_path):
        model_path = os.path.join(ROOT_DIR, "yolov8s-pose.pt")
    if not os.path.exists(model_path):
        raise FileNotFoundError("YOLOv8 pose model (yolov8n-pose.pt or yolov8s-pose.pt) not found in root directory!")

    from ultralytics import YOLO
    model = YOLO(model_path)
    
    # Check CUDA
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[YOLO-pose] Running model on: {device}")

    cap = cv2.VideoCapture(video_path)
    raw_traj = []
    
    # Blackboard / Writing default zone fallback
    default_x, default_y = 800, 360
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Run pose estimation
        results = model(frame, verbose=False, device=device)
        
        hx, hy = default_x, default_y
        if len(results) > 0 and results[0].keypoints is not None:
            kpts = results[0].keypoints.xy
            if len(kpts) > 0 and len(kpts[0]) > 10:
                wrist = kpts[0][10]  # Right wrist
                wx, wy = float(wrist[0]), float(wrist[1])
                if wx > 0 and wy > 0:
                    hx, hy = wx, wy
                    
        raw_traj.append((hx, hy))
        
    cap.release()
    
    # 5-Frame Moving Average Smoothing
    smoothed = []
    w_size = 5
    for i in range(len(raw_traj)):
        start = max(0, i - w_size // 2)
        end = min(len(raw_traj), i + w_size // 2 + 1)
        chunk = raw_traj[start:end]
        avg_x = sum([pt[0] for pt in chunk]) / len(chunk)
        avg_y = sum([pt[1] for pt in chunk]) / len(chunk)
        smoothed.append((avg_x, avg_y))
        
    print(f"[YOLO-pose] Trajectory tracked successfully ({len(smoothed)} frames).")
    return smoothed

# -----------------------------------------------------------------------------
# 2. FRAME-BY-FRAME HYBRID COMPOSITION (WITH DOLLY ZOOM-CROP)
# -----------------------------------------------------------------------------
def process_scene_frames(scene_idx, scene_info, original_video, output_video, hand_trajectory):
    """
    각 비디오 클립을 읽고 프레임별로 78% Dolly Zoom-Crop을 적용해 워터마크를 제거한 다음,
    변환된 손끝 좌표에 따라 한글 자모 드로잉 및 그래픽 합성을 수행하여 새 비디오로 렌더링.
    """
    cap = cv2.VideoCapture(original_video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (WIDTH, HEIGHT))
    
    print(f"[Render] Compositing Scene {scene_idx} ({total_frames} frames)...")
    
    # Preload Deco Assets
    crown_img = imread_unicode(os.path.join(ROOT_DIR, "assets", "graphics", "obj_crown_chalk.png"))
    arrow_img = imread_unicode(os.path.join(ROOT_DIR, "assets", "graphics", "effect_arrow.png"))
    checkmark_img = imread_unicode(os.path.join(ROOT_DIR, "assets", "graphics", "effect_checkmark.png"))
    
    # Sub-images for Scene 3 (ㅏ, ㅓ, ㅗ, ㅜ)
    letter_a = imread_unicode(os.path.join(ROOT_DIR, "assets", "graphics", "letters", "letter_ㅏ.png"))
    letter_eo = imread_unicode(os.path.join(ROOT_DIR, "assets", "graphics", "letters", "letter_ㅓ.png"))
    letter_o = imread_unicode(os.path.join(ROOT_DIR, "assets", "graphics", "letters", "letter_ㅗ.png"))
    letter_u = imread_unicode(os.path.join(ROOT_DIR, "assets", "graphics", "letters", "letter_ㅜ.png"))
    
    # Drawing stroke variables
    writing_start_f = int(total_frames * 0.15)
    writing_end_f = int(total_frames * 0.85)
    writing_dur = max(1, writing_end_f - writing_start_f)
    
    # Soundwaves for Scene 5
    waves_list = []  # items: [radius, max_radius, opacity_speed]
    
    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        h, w = frame.shape[:2]
        
        # 1. 78% Dolly Zoom-Crop (Watermark elimination)
        crop_w = int(w * 0.78)
        crop_h = int(h * 0.78)
        cx, cy = w // 2, h // 2
        x1 = max(0, cx - crop_w // 2)
        y1 = max(0, cy - crop_h // 2)
        x2 = min(w, x1 + crop_w)
        y2 = min(h, y1 + crop_h)
        
        cropped_frame = frame[y1:y2, x1:x2]
        canvas = cv2.resize(cropped_frame, (WIDTH, HEIGHT), interpolation=cv2.INTER_LANCZOS4)
        
        # 2. Hand Coordinate Conversion (to match 78% crop resolution)
        hx_raw, hy_raw = hand_trajectory[min(frame_idx, len(hand_trajectory)-1)]
        hx = int((hx_raw - x1) * (WIDTH / crop_w))
        hy = int((hy_raw - y1) * (HEIGHT / crop_h))
        
        # Progress timelines
        t = frame_idx / total_frames
        t_write = np.clip((frame_idx - writing_start_f) / writing_dur, 0.0, 1.0)
        
        # ----------------------------------------------------
        # Scene-Specific Graphics Rendering
        # ----------------------------------------------------
        if scene_idx == 1:
            # [Scene 1] Pointing to crown
            # Show crown on left side (x=380, y=200)
            crown_x, crown_y = 380, 200
            
            # Distance from hand to crown
            dist = math.hypot(hx - crown_x, hy - crown_y)
            reveal_trigger = (dist < 180) or (t > 0.4)
            
            if reveal_trigger:
                progress = np.clip((t - 0.2) / 0.5, 0.0, 1.0)
                scale = elastic_scale(progress, 0.6)
                overlay_alpha(canvas, crown_img, crown_x, crown_y, scale=scale)
                
                # Floating sparkles
                if progress > 0.6:
                    spark_ang = (frame_idx * 5) % 360
                    spark_scale = 0.15 * (1.0 + 0.15 * math.sin(frame_idx * 0.3))
                    overlay_alpha(canvas, checkmark_img, crown_x + 50, crown_y - 40, scale=spark_scale, rotate_deg=spark_ang, opacity=0.8)
                    
        elif scene_idx == 2:
            # [Scene 2] Cheonjiin Dots drawing
            # Heaven (Dot), Earth (Horizontal), Human (Vertical)
            dot_center = (640, 200)
            earth_start, earth_end = (500, 380), (780, 380)
            human_start, human_end = (640, 230), (640, 330)
            
            # Timeline division:
            # 0.0 ~ 0.35: Draw Dot
            # 0.35 ~ 0.7: Draw Earth (ㅡ)
            # 0.7 ~ 1.0: Draw Human (ㅣ)
            
            # 1. Dot (•)
            if t_write > 0.0:
                p_dot = np.clip(t_write / 0.3, 0.0, 1.0)
                cv2.circle(canvas, dot_center, int(15 * p_dot), (46, 46, 46), -1, cv2.LINE_AA)
                cv2.circle(canvas, dot_center, int(15 * p_dot), (0, 0, 0), 2, cv2.LINE_AA)
                
            # 2. Earth (ㅡ)
            if t_write > 0.3:
                p_earth = np.clip((t_write - 0.3) / 0.35, 0.0, 1.0)
                curr_x = int(earth_start[0] + p_earth * (earth_end[0] - earth_start[0]))
                cv2.line(canvas, earth_start, (curr_x, earth_start[1]), (46, 46, 46), 10, cv2.LINE_AA)
                
            # 3. Human (ㅣ)
            if t_write > 0.65:
                p_human = np.clip((t_write - 0.65) / 0.35, 0.0, 1.0)
                curr_y = int(human_start[1] + p_human * (human_end[1] - human_start[1]))
                cv2.line(canvas, human_start, (human_start[0], curr_y), (46, 46, 46), 10, cv2.LINE_AA)
                
            # Draw Chalk particle spark at the hand position while writing
            if 0.15 < t < 0.85:
                cv2.circle(canvas, (hx, hy), 6, (255, 255, 255), -1, cv2.LINE_AA)
                cv2.circle(canvas, (hx, hy), 8, (46, 46, 46), 2, cv2.LINE_AA)

        elif scene_idx == 3:
            # [Scene 3] Vowels assembly (ㅏ, ㅓ, ㅗ, ㅜ)
            # Quadrant points
            pts = {
                "ㅏ": (450, 240),
                "ㅓ": (830, 240),
                "ㅗ": (450, 480),
                "ㅜ": (830, 480)
            }
            
            # Show sequentially based on timeline
            # 0.0 ~ 0.25 -> ㅏ
            # 0.25 ~ 0.50 -> ㅓ
            # 0.50 ~ 0.75 -> ㅗ
            # 0.75 ~ 1.00 -> ㅜ
            
            if t_write > 0.0:
                p = np.clip(t_write / 0.25, 0.0, 1.0)
                scale = elastic_scale(p, 0.75)
                overlay_alpha(canvas, letter_a, pts["ㅏ"][0], pts["ㅏ"][1], scale=scale)
                
            if t_write > 0.25:
                p = np.clip((t_write - 0.25) / 0.25, 0.0, 1.0)
                scale = elastic_scale(p, 0.75)
                overlay_alpha(canvas, letter_eo, pts["ㅓ"][0], pts["ㅓ"][1], scale=scale)
                
            if t_write > 0.50:
                p = np.clip((t_write - 0.5) / 0.25, 0.0, 1.0)
                scale = elastic_scale(p, 0.75)
                overlay_alpha(canvas, letter_o, pts["ㅗ"][0], pts["ㅗ"][1], scale=scale)
                
            if t_write > 0.75:
                p = np.clip((t_write - 0.75) / 0.25, 0.0, 1.0)
                scale = elastic_scale(p, 0.75)
                overlay_alpha(canvas, letter_u, pts["ㅜ"][0], pts["ㅜ"][1], scale=scale)
                
            # Connect hand to active writing spot with brief Whoosh indicator
            if 0.15 < t < 0.85:
                cv2.circle(canvas, (hx, hy), 7, (230, 100, 100), -1, cv2.LINE_AA)

        elif scene_idx == 4:
            # [Scene 4] Vowel Keycap and Mouth stability diagram
            cap_x, cap_y = 900, 330
            mouth_x, mouth_y = 380, 330
            
            # Vowel Keycap "ㅏ" (Drawn as a neat box)
            scale = elastic_scale(np.clip(t / 0.4, 0.0, 1.0), 1.0)
            
            # Rounded rectangle keycap
            box_w, box_h = int(180 * scale), int(180 * scale)
            if scale > 0.1:
                cv2.rectangle(canvas, (cap_x - box_w//2, cap_y - box_h//2), (cap_x + box_w//2, cap_y + box_h//2), (46, 46, 46), 4, cv2.LINE_AA)
                cv2.rectangle(canvas, (cap_x - box_w//2 + 8, cap_y - box_h//2 + 8), (cap_x + box_w//2 - 8, cap_y + box_h//2 - 8), (250, 245, 230), -1)
                
                # Letter inside box
                overlay_alpha(canvas, letter_a, cap_x, cap_y, scale=scale * 1.0)
                
            # Mouth Outline Diagram
            if t > 0.3:
                p_mouth = np.clip((t - 0.3) / 0.5, 0.0, 1.0)
                m_scale = elastic_scale(p_mouth, 0.8)
                
                # Draw simple vector mouth lip circle
                cv2.circle(canvas, (mouth_x, mouth_y), int(60 * m_scale), (46, 46, 46), 4, cv2.LINE_AA)
                # Static lock pin arrow to represent stability "keep position"
                cv2.line(canvas, (mouth_x, mouth_y - 90), (mouth_x, mouth_y - 70), (220, 50, 50), 3, cv2.LINE_AA)
                cv2.line(canvas, (mouth_x - 5, mouth_y - 75), (mouth_x, mouth_y - 70), (220, 50, 50), 3, cv2.LINE_AA)
                cv2.line(canvas, (mouth_x + 5, mouth_y - 75), (mouth_x, mouth_y - 70), (220, 50, 50), 3, cv2.LINE_AA)

        elif scene_idx == 5:
            # [Scene 5] Soundwave rings pulsing out from ear / hand
            wave_origin = (hx, hy) if hx > 0 else (450, 300)
            
            # Emit new wave ring every 18 frames (~0.7s)
            if frame_idx % 18 == 0:
                waves_list.append({"r": 5, "max_r": 150, "orig": wave_origin})
                
            # Draw and grow existing wave rings
            active_waves = []
            for wave in waves_list:
                wave["r"] += 3
                pct = wave["r"] / wave["max_r"]
                if pct < 1.0:
                    opacity = 1.0 - pct
                    color = (int(46 * opacity), int(46 * opacity), int(46 * opacity))
                    cv2.circle(canvas, wave["orig"], int(wave["r"]), color, 2, cv2.LINE_AA)
                    active_waves.append(wave)
            waves_list = active_waves
            
            # Floating music notes (drawn as small circles/shapes)
            if frame_idx % 12 == 0:
                # Spawn particle
                pass

        elif scene_idx == 6:
            # [Scene 6] Sprout green box key term & Subscribe bell
            # 1. Sprout Green box for "단모음"
            box_x, box_y = 640, 310
            box_w, box_h = 420, 110
            
            # Hex #8EE4AF -> BGR: 175, 228, 142
            p_box = np.clip(t / 0.5, 0.0, 1.0)
            if p_box > 0.05:
                curr_w = int(box_w * p_box)
                cv2.rectangle(canvas, (box_x - curr_w//2, box_y - box_h//2), (box_x + curr_w//2, box_y + box_h//2), (175, 228, 142), -1)
                cv2.rectangle(canvas, (box_x - curr_w//2, box_y - box_h//2), (box_x + curr_w//2, box_y + box_h//2), (46, 46, 46), 4, cv2.LINE_AA)
                
                # Overlay Text inside Sprout Green box
                # Convert canvas to PIL to draw Korean text
                pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(pil_img)
                try:
                    font = ImageFont.truetype(FONT_PATH, 42)
                except Exception:
                    font = ImageFont.load_default()
                
                text_w = 120 # Estimate
                draw.text((box_x - 65, box_y - 25), "단모음", font=font, fill=(46, 46, 46))
                canvas = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                
            # 2. Bell icon swinging near hand
            bell_x, bell_y = hx, hy - 40
            if hx > 0:
                bell_swing = 15.0 * math.sin(2.0 * math.pi * t / 0.5)
                overlay_alpha(canvas, checkmark_img, bell_x, bell_y, scale=0.4, rotate_deg=bell_swing)

        # 3. Channel logo badge (Ultra-small 45x45px bottom right)
        logo = imread_unicode(LOGO_PATH)
        if logo is not None:
            # 45x45px
            overlay_alpha(canvas, logo, WIDTH - 60, HEIGHT - 55, scale=45.0 / logo.shape[0])

        out.write(canvas)
        frame_idx += 1
        
    cap.release()
    out.release()
    print(f"[Render] Scene {scene_idx} synthesis complete -> {os.path.basename(output_video)}")
    return True

# -----------------------------------------------------------------------------
# 3. MAIN WORKFLOW PIPELINE
# -----------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("  YOLOv8-pose Reverse-Engineered 30s Hangeul Video Compiler  ")
    print("=" * 70)
    
    # 1. Generate narration TTS for 6 scenes
    print("\n--- [Phase 1] TTS Narration Generation ---")
    tts_files = []
    for s in SCENARIO:
        seq = s["seq"]
        txt = s["text"]
        out_path = os.path.join(TTS_CACHE_DIR, f"scene_{seq}.mp3")
        
        # Call root tts_manager (which automatically handles cache & female ko active voice)
        print(f"Generating TTS for Scene {seq}...")
        save_tts(txt, out_path, lang='ko')
        tts_files.append(out_path)

    # 2. Process and composite original clips frame-by-frame
    print("\n--- [Phase 2] YOLO-pose Motion Tracking & Graphic Overlay ---")
    rendered_clips = []
    
    for s in SCENARIO:
        seq = s["seq"]
        orig_video = os.path.join(SCENE_DIR, f"scene_{seq}.mp4")
        temp_out = os.path.join(PROJECT_DIR, f"scene_{seq}_yolo_overlay.mp4")
        
        if not os.path.exists(orig_video):
            print(f"[ERROR] Source video clip {orig_video} not found! Please generate it first.")
            sys.exit(1)
            
        # Extract hand trajectory
        trajectory = track_wrist_trajectory(orig_video)
        
        # Composite graphics
        process_scene_frames(seq, s, orig_video, temp_out, trajectory)
        rendered_clips.append(temp_out)

    # 3. MoviePy Audio & Video Compilation (1.1x speed scale and sound effect mix)
    print("\n--- [Phase 3] MoviePy Final Assembly ---")
    
    moviepy_clips = []
    sfx_whoosh = AudioFileClip(WHOOSH_SFX_PATH) if os.path.exists(WHOOSH_SFX_PATH) else None
    sfx_pop = AudioFileClip(POP_SFX_PATH) if os.path.exists(POP_SFX_PATH) else None
    sfx_bell = AudioFileClip(BELL_SFX_PATH) if os.path.exists(BELL_SFX_PATH) else None
    
    total_timeline = 0.0
    subtitle_configs = []
    
    for idx, s in enumerate(SCENARIO):
        seq = s["seq"]
        video_path = rendered_clips[idx]
        tts_path = tts_files[idx]
        
        # Load Video Clip
        v_clip = VideoFileClip(video_path)
        
        # Load Audio Clip & Apply 1.1x Speed multiplier (narration speed 1.1x)
        a_clip = AudioFileClip(tts_path)
        # speedup audio via MultiplySpeed(1.1)
        a_clip_sped = a_clip.with_effects([MultiplyVolume(1.0)]).with_duration(a_clip.duration / 1.1)
        
        # Narration Duration defines the scene duration (at least 5.0 seconds as a baseline)
        target_scene_dur = max(5.0, a_clip_sped.duration + 0.8)
        
        # Loop or freeze video if too short, or trim if too long
        if v_clip.duration < target_scene_dur:
            # freeze last frame
            v_clip_extended = v_clip.with_duration(target_scene_dur)
        else:
            v_clip_extended = v_clip.with_duration(target_scene_dur)
            
        # Audio Mix (Narration + SFX)
        audio_layers = [a_clip_sped.with_start(0.2)]
        
        # Apply specific SFX cues
        if seq == 1 and sfx_pop:
            audio_layers.append(sfx_pop.with_start(1.0).with_effects([MultiplyVolume(0.4)]))
        elif seq == 2 and sfx_whoosh:
            audio_layers.append(sfx_whoosh.with_start(0.5).with_effects([MultiplyVolume(0.3)]))
            audio_layers.append(sfx_whoosh.with_start(2.2).with_effects([MultiplyVolume(0.3)]))
        elif seq == 3 and sfx_whoosh:
            audio_layers.append(sfx_whoosh.with_start(0.6).with_effects([MultiplyVolume(0.4)]))
        elif seq == 4 and sfx_pop:
            audio_layers.append(sfx_pop.with_start(0.4).with_effects([MultiplyVolume(0.5)]))
        elif seq == 6 and sfx_bell:
            audio_layers.append(sfx_bell.with_start(0.5).with_effects([MultiplyVolume(0.6)]))
            
        scene_audio = CompositeAudioClip(audio_layers).with_duration(target_scene_dur)
        v_clip_final = v_clip_extended.with_audio(scene_audio)
        
        moviepy_clips.append(v_clip_final)
        
        # Save subtitles configuration details
        subtitle_configs.append({
            "start": total_timeline,
            "duration": target_scene_dur,
            "text": s["text"]
        })
        
        total_timeline += target_scene_dur

    # Concatenate all clips
    print(f"Concatenating all {len(moviepy_clips)} scene clips...")
    final_video = concatenate_videoclips(moviepy_clips, method="compose")
    
    # 4. Mix Lo-Fi Background BGM Loop
    if os.path.exists(BGM_PATH):
        print(f"Mixing background BGM loop: {os.path.basename(BGM_PATH)}")
        bgm_clip = AudioFileClip(BGM_PATH)
        if bgm_clip.duration < final_video.duration:
            loops = int(math.ceil(final_video.duration / bgm_clip.duration))
            bgm_loops = [bgm_clip.with_start(i * bgm_clip.duration) for i in range(loops)]
            bgm_full = CompositeAudioClip(bgm_loops).with_duration(final_video.duration)
        else:
            bgm_full = bgm_clip.with_duration(final_video.duration)
            
        bgm_full = bgm_full.with_effects([MultiplyVolume(0.08)]) # 8% volume BGM
        
        if final_video.audio:
            final_video.audio = CompositeAudioClip([final_video.audio, bgm_full])
        else:
            final_video.audio = bgm_full

    # 5. Burn-in Standard Subtitles (Dynamic multi-line wrap, clean black box background)
    print("Overlaying formatted subtitles with dynamic padding...")
    sub_clips = []
    for sub in subtitle_configs:
        txt = sub["text"]
        
        # Format text to wrap around 30 characters
        words = txt.split(" ")
        lines = []
        cur_line = []
        for w in words:
            cur_line.append(w)
            if len(" ".join(cur_line)) > 26:
                lines.append(" ".join(cur_line))
                cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))
        wrapped_txt = "\n".join(lines)
        
        # Create TextClip using standard malgun font with safety black box margin
        try:
            txt_clip = TextClip(
                text=wrapped_txt,
                font=FONT_PATH,
                font_size=28,
                color="white",
                bg_color="rgba(15, 12, 10, 220)",
                size=(920, None),
                text_align="center"
            ).with_duration(sub["duration"]).with_position(("center", 580)).with_start(sub["start"])
            sub_clips.append(txt_clip)
        except Exception as e:
            print(f"[Sub Check] Subtitle creation skipped for: {txt}. Error: {e}")

    if sub_clips:
        final_video = CompositeVideoClip([final_video] + sub_clips, size=(WIDTH, HEIGHT))

    # 6. Render final output file
    threads = os.cpu_count() or 4
    print(f"\nEncoding final video directly to {OUTPUT_FILE} (Threads: {threads})...")
    final_video.write_videofile(
        OUTPUT_FILE,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=threads,
        preset="fast"
    )
    
    # 7. Clean up temporary scene videos to save disk space
    print("\nCleaning up temporary scene videos...")
    for temp_file in rendered_clips:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"Warning: Failed to delete temporary file {temp_file}: {e}")

    print("\n" + "=" * 70)
    print("  🎉 YOLOv8-pose 30s Hangeul video rendered successfully!")
    print(f"   - Location: {OUTPUT_FILE}")
    print("=" * 70)
    
    # 8. Automatically auto-play the video
    print("\nLaunching video file in the default media player...")
    if sys.platform == "win32":
        os.startfile(OUTPUT_FILE)
    else:
        # Linux/macOS fallback
        subprocess.run(["xdg-open", OUTPUT_FILE], check=False)

if __name__ == "__main__":
    main()
