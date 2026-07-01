#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
compile_real_scenario.py — 사용자 시나리오(scenario.txt) 및 천지인 조음 원리 100% 반영 역공학 비디오 컴파일러.
이 스크립트는 사용자가 제공한 진짜 대본(Scene 0 ~ Scene 6)에 기초하여,
YOLOv8-pose 손끝 추적을 천지인(하늘, 땅, 사람) 및 아/어/오/우 결합 천체 궤적에 동기화하고,
78% Dolly Zoom-Crop으로 워터마크를 제거한 고품질 교육 영상을 렌더링합니다.
"""
import os
import sys
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

# Real User Scenario (Scene 0 ~ Scene 6)
SCENARIO = [
    {
        "seq": 0,
        "text": "안녕하세요! 오늘 우리는 세계에서 가장 과학적인 문자, 한글의 탄생 비밀과 모음의 원리를 알아봅니다. 한글은 어떻게 생겨났을까요?",
        "desc": "Intro: Vowels and Hangeul birth"
    },
    {
        "seq": 1,
        "text": "아주 먼 옛날, 한국인들은 한글이 없어서 중국의 한자를 빌려 글을 썼습니다. 하지만 한자는 너무 복잡해서 양반들만 쓸 수 있었고, 일반 백성들은 글을 읽지도 쓰지도 못했습니다.",
        "desc": "Scene 1: Borrowing Chinese Hanja"
    },
    {
        "seq": 2,
        "text": "법을 읽지 못해 억울한 일을 당하는 백성들을 보고, 세종대왕은 깊은 슬픔과 안타까움을 느꼈습니다. '내 이를 가엾게 여겨 새로 스물여덟 글자를 만드노니...'",
        "desc": "Scene 2: King Sejong's sorrow"
    },
    {
        "seq": 3,
        "text": "드디어 1443년, 누구나 쉽게 배울 수 있는 혁신적인 문자 '훈민정음'이 창제되었습니다. 지혜로운 사람은 아침에, 어리석은 사람도 열흘이면 배울 수 있는 글자였습니다.",
        "desc": "Scene 3: Birth of Hunminjeongeum"
    },
    {
        "seq": 4,
        "text": "한글의 모음은 우주의 3대 요소인 하늘, 땅, 사람을 모델로 만들었습니다. 이를 '천지인'이라고 부릅니다.",
        "desc": "Scene 4: Cheon-Ji-In prime elements"
    },
    {
        "seq": 5,
        "text": "하늘의 점이 사람의 오른쪽에 붙으면 해가 뜨는 동쪽을 뜻하는 밝은 모음 'ㅏ'가 되고, 왼쪽에 붙으면 해가 지는 서쪽을 뜻하는 어두운 모음 'ㅓ'가 됩니다.",
        "desc": "Scene 5: Creation of ㅏ and ㅓ"
    },
    {
        "seq": 6,
        "text": "마찬가지로 하늘의 점이 땅의 위에 붙으면 땅 위로 솟아오르는 밝은 모음 'ㅗ'가 되며, 아래에 붙으면 땅 아래로 가라앉는 어두운 모음 'ㅜ'가 됩니다.",
        "desc": "Scene 6: Creation of ㅗ and ㅜ"
    }
]

# Helper: Read Image with Unicode Path support
def imread_unicode(path):
    try:
        with open(path, "rb") as f:
            file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
        return cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
    except Exception as e:
        print(f"[ERROR] Failed to read image: {path}. Error: {e}")
        return None

# Elastic scale bounce helper
def elastic_scale(progress, base=1.0):
    if progress <= 0.0:
        return 0.001
    if progress >= 1.0:
        return base
    val = 1.0 - math.exp(-6.0 * progress) * math.cos(2.0 * math.pi * progress)
    return max(0.001, base * val)

# Overlay Transparent PNG
def overlay_alpha(bg_img, fg_img, x, y, scale=1.0, rotate_deg=0.0, opacity=1.0):
    if fg_img is None:
        return
    h_fg, w_fg = fg_img.shape[:2]
    if scale != 1.0:
        new_w = max(1, int(w_fg * scale))
        new_h = max(1, int(h_fg * scale))
        fg_img = cv2.resize(fg_img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        h_fg, w_fg = fg_img.shape[:2]
    if rotate_deg != 0.0:
        M = cv2.getRotationMatrix2D((w_fg // 2, h_fg // 2), rotate_deg, 1.0)
        fg_img = cv2.warpAffine(fg_img, M, (w_fg, h_fg), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_TRANSPARENT)
    x1, y1 = int(x - w_fg // 2), int(y - h_fg // 2)
    x2, y2 = x1 + w_fg, y1 + h_fg
    h_bg, w_bg = bg_img.shape[:2]
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
        bg_img[y1_c:y2_c, x1_c:x2_c, :3] = (alpha * fg_crop[:, :, :3] + (1.0 - alpha) * bg_rgb).astype(np.uint8) if 'bg_rgb' in globals() else (alpha * fg_crop[:, :, :3] + (1.0 - alpha) * bg_crop[:, :, :3]).astype(np.uint8)
    else:
        bg_img[y1_c:y2_c, x1_c:x2_c, :3] = fg_crop[:, :, :3]

# -----------------------------------------------------------------------------
# 1. TRACKING HAND TRAJECTORY VIA YOLOv8-pose
# -----------------------------------------------------------------------------
def track_wrist_trajectory(video_path):
    """오른손 목(Right Wrist - Keypoint 10) 좌표 추적 및 스무딩"""
    print(f"[YOLO-pose] Tracking hand in: {os.path.basename(video_path)}...")
    model_path = os.path.join(ROOT_DIR, "yolov8n-pose.pt")
    if not os.path.exists(model_path):
        model_path = os.path.join(ROOT_DIR, "yolov8s-pose.pt")
    if not os.path.exists(model_path):
        raise FileNotFoundError("YOLOv8 model files not found in root!")

    from ultralytics import YOLO
    model = YOLO(model_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    cap = cv2.VideoCapture(video_path)
    raw_traj = []
    default_x, default_y = 800, 360

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame, verbose=False, device=device)
        hx, hy = default_x, default_y
        if len(results) > 0 and results[0].keypoints is not None:
            kpts = results[0].keypoints.xy
            if len(kpts) > 0 and len(kpts[0]) > 10:
                wrist = kpts[0][10]
                wx, wy = float(wrist[0]), float(wrist[1])
                if wx > 0 and wy > 0:
                    hx, hy = wx, wy
        raw_traj.append((hx, hy))
    cap.release()

    # 5-frame average
    smoothed = []
    w_size = 5
    for i in range(len(raw_traj)):
        start = max(0, i - w_size // 2)
        end = min(len(raw_traj), i + w_size // 2 + 1)
        chunk = raw_traj[start:end]
        avg_x = sum([pt[0] for pt in chunk]) / len(chunk)
        avg_y = sum([pt[1] for pt in chunk]) / len(chunk)
        smoothed.append((avg_x, avg_y))
    return smoothed

# -----------------------------------------------------------------------------
# 2. FRAME COMPOSITOR FOR USER SCENARIO
# -----------------------------------------------------------------------------
def composite_user_scene(scene_idx, orig_video, output_video, hand_trajectory):
    cap = cv2.VideoCapture(orig_video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (WIDTH, HEIGHT))
    
    print(f"[Render] Compositing Scene {scene_idx} ({total_frames} frames)...")
    
    # Load scroll frame
    scroll_img = imread_unicode(os.path.join(ROOT_DIR, "assets", "graphics", "obj_haerye_scroll.png"))
    
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
        
        # 2. Coordinate mapping
        hx_raw, hy_raw = hand_trajectory[min(frame_idx, len(hand_trajectory)-1)]
        hx = int((hx_raw - x1) * (WIDTH / crop_w))
        hy = int((hy_raw - y1) * (HEIGHT / crop_h))
        
        t = frame_idx / total_frames
        
        # Convert canvas to PIL for beautiful Korean text rendering
        pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        
        try:
            font_title = ImageFont.truetype(FONT_PATH, 48)
            font_body = ImageFont.truetype(FONT_PATH, 28)
            font_large = ImageFont.truetype(FONT_PATH, 90)
            font_hanja = ImageFont.truetype(FONT_PATH, 55)
        except Exception:
            font_title = font_body = font_large = font_hanja = ImageFont.load_default()

        # ----------------------------------------------------
        # Scene-by-Scene Educational Motion Graphics
        # ----------------------------------------------------
        if scene_idx == 0:
            # [Scene 0] Intro: Floating Hangeul characters
            letters = [("ㄱ", 200, 150), ("ㄴ", 980, 180), ("ㄷ", 300, 380), ("ㄹ", 880, 420),
                       ("ㅏ", 450, 120), ("ㅓ", 750, 140), ("ㅗ", 380, 300), ("ㅜ", 820, 320)]
            for char, lx, ly in letters:
                # sinusoidal floating & rotation
                float_y = int(20 * math.sin(2.0 * math.pi * t + lx))
                draw.text((lx, ly + float_y), char, font=font_title, fill=(46, 46, 46, 180))
            
            # Highlight title
            draw.text((640 - 150, 220), "한글의 탄생", font=font_large, fill=(30, 30, 30))
            
        elif scene_idx == 1:
            # [Scene 1] Chinese Hanja cluttering
            hanjas = [("難", 180, 120), ("繁", 1000, 150), ("漢", 280, 350), ("字", 920, 400),
                      ("難", 420, 180), ("繁", 780, 200)]
            for char, lx, ly in hanjas:
                pulse = 1.0 + 0.15 * math.sin(2.0 * math.pi * t + lx)
                f_size = int(55 * pulse)
                try:
                    f = ImageFont.truetype(FONT_PATH, f_size)
                except Exception:
                    f = font_hanja
                draw.text((lx, ly), char, font=f, fill=(80, 80, 80, 150))
                
            # Text annotation box: "한자 (Chinese Characters) - Too Complex"
            draw.rounded_rectangle([420, 280, 860, 350], radius=15, outline=(46, 46, 46), width=3, fill=(245, 245, 240))
            draw.text((450, 295), "한자: 너무 복잡하고 어려움", font=font_body, fill=(220, 50, 50))
            
        elif scene_idx == 2:
            # [Scene 2] King Sejong's scroll & statement
            canvas = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            # Draw Sejong scroll in center-bottom
            if scroll_img is not None:
                overlay_alpha(canvas, scroll_img, 640, 340, scale=0.95)
            pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)
            
            # Write Hunminjeongeum text sequentially
            statement = "내 이를 가엾게 여겨\n새로 스물여덟 글자를 만드노니"
            # simple typewriter reveal
            reveal_len = int(len(statement) * np.clip(t / 0.8, 0.0, 1.0))
            curr_text = statement[:reveal_len]
            draw.text((450, 290), curr_text, font=font_body, fill=(46, 46, 46))
            
        elif scene_idx == 3:
            # [Scene 3] Hunminjeongeum shining
            canvas = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            if scroll_img is not None:
                overlay_alpha(canvas, scroll_img, 640, 340, scale=1.0)
            pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)
            
            # Shining letters popping out
            all_chars = "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㅏㅓㅗㅜㅡㅣ"
            glow_p = np.clip((t - 0.2) / 0.7, 0.0, 1.0)
            if glow_p > 0.0:
                for idx, char in enumerate(all_chars):
                    ang = (idx * 20) * (math.pi / 180)
                    dist = 120 + 200 * glow_p
                    lx = int(640 + dist * math.cos(ang))
                    ly = int(340 + dist * math.sin(ang))
                    draw.text((lx - 20, ly - 20), char, font=font_title, fill=(230, 90, 90) if idx % 2 == 0 else (46, 46, 46))

        elif scene_idx == 4:
            # [Scene 4] Cheon-Ji-In three panels
            # Draw three boxes side by side
            box_width, box_height = 240, 300
            y_pos = 180
            xs = [200, 520, 840] # Sky, Earth, Human
            labels = [("하늘 (Sky)", "•"), ("땅 (Earth)", "ㅡ"), ("사람 (Human)", "ㅣ")]
            
            for idx, (label, symbol) in enumerate(labels):
                bx = xs[idx]
                p_box = np.clip((t - idx * 0.15) / 0.4, 0.0, 1.0)
                if p_box > 0.0:
                    scale = elastic_scale(p_box, 1.0)
                    w_curr, h_curr = int(box_width * scale), int(box_height * scale)
                    
                    # Draw rounded container
                    draw.rounded_rectangle([bx - w_curr//2, y_pos, bx + w_curr//2, y_pos + h_curr], radius=10, outline=(46, 46, 46), width=3, fill=(250, 245, 235))
                    
                    # Draw symbol
                    draw.text((bx - 20, y_pos + 60), symbol, font=font_large, fill=(220, 80, 80) if idx==0 else (46, 46, 46))
                    
                    # Draw label text
                    draw.text((bx - 60, y_pos + 220), label, font=font_body, fill=(46, 46, 46))

        elif scene_idx == 5:
            # [Scene 5] Creation of ㅏ and ㅓ
            # Vertical line ㅣ is in the center
            line_start, line_end = (640, 200), (640, 480)
            draw.line([line_start, line_end], fill=(46, 46, 46), width=10)
            draw.text((615, 140), "ㅣ", font=font_title, fill=(46, 46, 46))
            
            # Sun dot '•' moves according to timeline
            # 0.0 ~ 0.5: Dot rises on the right to make 'ㅏ'
            # 0.5 ~ 1.0: Dot transitions to the left to make 'ㅓ'
            dot_r = 16
            if t < 0.5:
                p = t / 0.5
                dot_x = int(640 + 80 * p)
                dot_y = 340
                draw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=(220, 80, 80))
                # Label ㅏ
                draw.text((760, 310), "ㅏ", font=font_large, fill=(220, 80, 80))
            else:
                p = (t - 0.5) / 0.5
                dot_x = int(720 - 160 * p)
                dot_y = 340
                draw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=(80, 80, 220))
                # Draw ㅏ (fade)
                draw.text((760, 310), "ㅏ", font=font_large, fill=(46, 46, 46, 100))
                # Label ㅓ
                draw.text((450, 310), "ㅓ", font=font_large, fill=(80, 80, 220))
                
            # Connect hand to active dot
            if 0.15 < t < 0.85:
                draw.ellipse([hx - 8, hy - 8, hx + 8, hy + 8], fill=(230, 100, 100))

        elif scene_idx == 6:
            # [Scene 6] Creation of ㅗ and ㅜ
            # Horizontal line ㅡ is in the center
            line_start, line_end = (480, 340), (800, 340)
            draw.line([line_start, line_end], fill=(46, 46, 46), width=10)
            draw.text((615, 360), "ㅡ", font=font_title, fill=(46, 46, 46))
            
            # Sun dot '•' moves according to timeline
            # 0.0 ~ 0.5: Dot rises ABOVE the line to make 'ㅗ'
            # 0.5 ~ 1.0: Dot sinks BELOW the line to make 'ㅜ'
            dot_r = 16
            if t < 0.5:
                p = t / 0.5
                dot_x = 640
                dot_y = int(340 - 80 * p)
                draw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=(220, 80, 80))
                # Label ㅗ
                draw.text((610, 120), "ㅗ", font=font_large, fill=(220, 80, 80))
            else:
                p = (t - 0.5) / 0.5
                dot_x = 640
                dot_y = int(260 + 160 * p)
                draw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=(80, 80, 220))
                # Draw ㅗ (fade)
                draw.text((610, 120), "ㅗ", font=font_large, fill=(46, 46, 46, 100))
                # Label ㅜ
                draw.text((610, 480), "ㅜ", font=font_large, fill=(80, 80, 220))
                
            # Connect hand to active dot
            if 0.15 < t < 0.85:
                draw.ellipse([hx - 8, hy - 8, hx + 8, hy + 8], fill=(230, 100, 100))

        # 3. Channel logo badge (45x45px bottom right)
        canvas = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        logo = imread_unicode(LOGO_PATH)
        if logo is not None:
            overlay_alpha(canvas, logo, WIDTH - 60, HEIGHT - 55, scale=45.0 / logo.shape[0])

        out.write(canvas)
        frame_idx += 1
        
    cap.release()
    out.release()
    print(f"[Render] Scene {scene_idx} complete.")
    return True

# -----------------------------------------------------------------------------
# 3. MAIN ASSEMBLY PIPELINE
# -----------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("  [NEW] K-Lingo Journey: 30s Hangeul Birth & Vowels Compiler")
    print("  Syncing with real scenario.txt & Cheon-Ji-In scientific design")
    print("=" * 70)
    
    # 1. Generate TTS Narrations
    print("\n--- [Phase 1] Generate Scenario Narrations ---")
    tts_files = []
    for s in SCENARIO:
        seq = s["seq"]
        txt = s["text"]
        out_path = os.path.join(TTS_CACHE_DIR, f"scene_{seq}.mp3")
        print(f" -> TTS Scene {seq}: {txt[:25]}...")
        save_tts(txt, out_path, lang='ko')
        tts_files.append(out_path)

    # 2. Frame-by-frame Composite
    print("\n--- [Phase 2] YOLOv8-pose wrist tracking & graphic overlay ---")
    rendered_clips = []
    for s in SCENARIO:
        seq = s["seq"]
        orig_video = os.path.join(SCENE_DIR, f"scene_{seq}.mp4")
        temp_out = os.path.join(PROJECT_DIR, f"scene_{seq}_real_overlay.mp4")
        
        if not os.path.exists(orig_video):
            print(f"[ERROR] Source video clip {orig_video} not found! Please verify autoveo downloads.")
            sys.exit(1)
            
        # Extract hand coordinates
        trajectory = track_wrist_trajectory(orig_video)
        
        # Render overlays
        composite_user_scene(seq, orig_video, temp_out, trajectory)
        rendered_clips.append(temp_out)

    # 3. MoviePy Timeline Assembly
    print("\n--- [Phase 3] Timeline Assembly & Audio Mix ---")
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
        
        v_clip = VideoFileClip(video_path)
        a_clip = AudioFileClip(tts_path)
        
        # 1.1x speed scale for gTTS
        a_clip_sped = a_clip.with_effects([MultiplyVolume(1.0)]).with_duration(a_clip.duration / 1.1)
        target_scene_dur = max(5.0, a_clip_sped.duration + 0.8)
        
        # Extended base video
        v_clip_final = v_clip.with_duration(target_scene_dur)
        
        # Audio Mix
        audio_layers = [a_clip_sped.with_start(0.2)]
        
        # Add SFX cues
        if seq == 0 and sfx_bell:
            audio_layers.append(sfx_bell.with_start(0.2).with_effects([MultiplyVolume(0.5)]))
        elif seq == 1 and sfx_whoosh:
            audio_layers.append(sfx_whoosh.with_start(0.8).with_effects([MultiplyVolume(0.3)]))
        elif seq == 2 and sfx_pop:
            audio_layers.append(sfx_pop.with_start(1.0).with_effects([MultiplyVolume(0.4)]))
        elif seq == 3 and sfx_bell:
            audio_layers.append(sfx_bell.with_start(0.5).with_effects([MultiplyVolume(0.6)]))
        elif seq == 5 and sfx_whoosh:
            audio_layers.append(sfx_whoosh.with_start(0.6).with_effects([MultiplyVolume(0.4)]))
        elif seq == 6 and sfx_pop:
            audio_layers.append(sfx_pop.with_start(0.6).with_effects([MultiplyVolume(0.4)]))

        scene_audio = CompositeAudioClip(audio_layers).with_duration(target_scene_dur)
        v_clip_final = v_clip_final.with_audio(scene_audio)
        
        moviepy_clips.append(v_clip_final)
        
        subtitle_configs.append({
            "start": total_timeline,
            "duration": target_scene_dur,
            "text": s["text"]
        })
        
        total_timeline += target_scene_dur

    final_video = concatenate_videoclips(moviepy_clips, method="compose")
    
    # 4. BGM Loop Mix
    if os.path.exists(BGM_PATH):
        bgm_clip = AudioFileClip(BGM_PATH)
        if bgm_clip.duration < final_video.duration:
            loops = int(math.ceil(final_video.duration / bgm_clip.duration))
            bgm_loops = [bgm_clip.with_start(i * bgm_clip.duration) for i in range(loops)]
            bgm_full = CompositeAudioClip(bgm_loops).with_duration(final_video.duration)
        else:
            bgm_full = bgm_clip.with_duration(final_video.duration)
        bgm_full = bgm_full.with_effects([MultiplyVolume(0.08)])
        
        if final_video.audio:
            final_video.audio = CompositeAudioClip([final_video.audio, bgm_full])
        else:
            final_video.audio = bgm_full

    # 5. Formatted subtitles
    sub_clips = []
    for sub in subtitle_configs:
        txt = sub["text"]
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
            print(f"[Sub Check] Subtitle creation skipped: {e}")

    if sub_clips:
        final_video = CompositeVideoClip([final_video] + sub_clips, size=(WIDTH, HEIGHT))

    # 6. Render
    threads = os.cpu_count() or 4
    print(f"\n[No-Upscale] Rendering 720p draft directly to {OUTPUT_FILE} (Threads: {threads})...")
    final_video.write_videofile(
        OUTPUT_FILE,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=threads,
        preset="fast"
    )
    
    # 7. Cleanup
    print("\nCleaning up temporary scene videos...")
    for temp_file in rendered_clips:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"Warning: Failed to delete temporary file {temp_file}: {e}")

    print("\n" + "=" * 70)
    print("  🎉 New Scientific Zolla Hangeul Video successfully compiled!")
    print(f"   - Location: {OUTPUT_FILE}")
    print("=" * 70)
    
    # 8. Auto-play
    print("\nLaunching video file in the default media player...")
    if sys.platform == "win32":
        os.startfile(OUTPUT_FILE)
    else:
        subprocess.run(["xdg-open", OUTPUT_FILE], check=False)

if __name__ == "__main__":
    main()
