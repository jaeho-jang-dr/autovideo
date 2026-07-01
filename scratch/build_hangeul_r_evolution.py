# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import cv2
import sqlite3
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy.video.fx as fx
from moviepy import (
    AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip, concatenate_videoclips, VideoClip
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
sys.stdout.reconfigure(encoding='utf-8')

import math

def generate_text_lineart(text, output_path, font_size=180, stroke_width=6, color=(245, 245, 245, 255)):
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    if not os.path.exists(font_path):
        font_path = "arial.ttf"
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()
    dummy_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    dummy_draw = ImageDraw.Draw(dummy_img)
    try:
        bbox = dummy_draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except AttributeError:
        w, h = dummy_draw.textsize(text, font=font)
        bbox = [0, 0, w, h]
    margin = stroke_width * 2 + 15
    size_w = int(w + margin * 2)
    size_h = int(h + margin * 2)
    img = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    x = margin - bbox[0]
    y = margin - bbox[1]
    draw.text((x, y), text, fill=color, font=font, stroke_width=stroke_width, stroke_fill=color)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    return output_path

def draw_active_arm(canvas, mx, my, stroke_w=4):
    if mx is None or my is None:
        mx, my = 480, 270
    r_shoulder = (648, 280)
    r_hand = (mx, my)
    mid_x = (r_shoulder[0] + r_hand[0]) // 2
    mid_y = (r_shoulder[1] + r_hand[1]) // 2
    r_elbow = (int(mid_x - 15), int(mid_y + 30))
    arm_color = (17, 17, 17)
    cv2.line(canvas, r_shoulder, r_elbow, arm_color, stroke_w, cv2.LINE_AA)
    cv2.line(canvas, r_elbow, r_hand, arm_color, stroke_w, cv2.LINE_AA)
    cv2.line(canvas, r_hand, (r_hand[0] - 15, r_hand[1] - 10), (245, 245, 245), 6, cv2.LINE_AA)

# ==========================================
# 1. PROCEDURAL 2D ZOLLA JOINT ENGINE
# ==========================================
class ProceduralZolla:
    def __init__(self, stroke_w=4):
        self.stroke_w = stroke_w
        self.color = (245, 245, 245) # BGR White/Light Chalk

    def draw_ellipse_rotated(self, canvas, center, axes, angle, color, thickness):
        cv2.ellipse(canvas, center, axes, angle, 0, 360, color, thickness, cv2.LINE_AA)

    def draw_jay(self, canvas, cx, cy, pose, t, mx=None, my=None):
        # Dynamic Breathing: sinusoidal vertical oscillation
        breath_y = int(3.5 * math.sin(2.0 * math.pi * t / 2.5))
        ny = cy + breath_y
        nx = cx

        # Proportions (scaled up by ~25%)
        head_r = 30
        spine_len = 80

        head_c = (nx, ny - head_r - 5)
        pelvis = (nx, ny + spine_len)

        # 1. Spine (Neck to Pelvis)
        cv2.line(canvas, (nx, ny), pelvis, self.color, self.stroke_w, cv2.LINE_AA)

        # 2. Head (Empty circle outlined in black)
        cv2.circle(canvas, head_c, head_r, self.color, self.stroke_w, cv2.LINE_AA)

        # 3. Eyes (Dot eyes with blinking)
        blink = False
        cycle_time = t % 4.0
        if cycle_time > 3.85:
            blink = True

        eye_offset_x = 9
        eye_y = head_c[1] - 4
        if not blink:
            cv2.circle(canvas, (head_c[0] - eye_offset_x, eye_y), 3, self.color, -1, cv2.LINE_AA)
            cv2.circle(canvas, (head_c[0] + eye_offset_x, eye_y), 3, self.color, -1, cv2.LINE_AA)
        else:
            cv2.line(canvas, (head_c[0] - eye_offset_x - 4, eye_y), (head_c[0] - eye_offset_x + 4, eye_y), self.color, 2, cv2.LINE_AA)
            cv2.line(canvas, (head_c[0] + eye_offset_x - 4, eye_y), (head_c[0] + eye_offset_x + 4, eye_y), self.color, 2, cv2.LINE_AA)

        # 4. Mouth (Smiling line)
        mouth_y = head_c[1] + 9
        cv2.ellipse(canvas, (head_c[0], mouth_y), (10, 5), 0, 0, 180, self.color, 2, cv2.LINE_AA)

        # 5. Two Hair Strands on top of head
        hair_root = (head_c[0], head_c[1] - head_r)
        cv2.line(canvas, hair_root, (hair_root[0] - 6, hair_root[1] - 14), self.color, 2, cv2.LINE_AA)
        cv2.line(canvas, hair_root, (hair_root[0] + 6, hair_root[1] - 14), self.color, 2, cv2.LINE_AA)

        # 6. Arms and Legs Joints Calculation
        l_shoulder = (nx - 3, ny + 12)
        r_shoulder = (nx + 3, ny + 12)

        # Defaults (Base Stand)
        l_elbow = (l_shoulder[0] - 30, l_shoulder[1] + 30)
        l_hand = (l_elbow[0] - 20, l_elbow[1] + 25)
        r_elbow = (r_shoulder[0] + 30, r_shoulder[1] + 30)
        r_hand = (r_elbow[0] + 20, r_elbow[1] + 25)

        l_hip = (pelvis[0] - 8, pelvis[1])
        r_hip = (pelvis[0] + 8, pelvis[1])
        l_knee = (l_hip[0] - 12, l_hip[1] + 45)
        l_foot = (l_knee[0] - 6, l_knee[1] + 45)
        r_knee = (r_hip[0] + 12, r_hip[1] + 45)
        r_foot = (r_knee[0] + 6, r_knee[1] + 45)

        if pose == "writing_g" and mx is not None and my is not None:
            r_hand = (mx, my)
            r_elbow = (int((r_shoulder[0] + r_hand[0]) / 2 + 15), int((r_shoulder[1] + r_hand[1]) / 2 - 15))
            
            # Left arm sits on hip
            l_elbow = (l_shoulder[0] - 20, l_shoulder[1] + 15)
            l_hand = (l_shoulder[0] - 8, l_elbow[1] + 15)
            
        elif pose == "pointing":
            wave_amp = 6.0 * math.sin(2.0 * math.pi * t / 1.0)
            r_elbow = (r_shoulder[0] + 45, r_shoulder[1] - 12)
            r_hand = (r_elbow[0] + 45, int(r_elbow[1] + wave_amp))
            
            l_elbow = (l_shoulder[0] - 25, l_shoulder[1] + 20)
            l_hand = (l_shoulder[0] - 10, l_elbow[1] + 20)

        # Draw Limbs (Lines)
        # Left Arm
        cv2.line(canvas, l_shoulder, l_elbow, self.color, self.stroke_w, cv2.LINE_AA)
        cv2.line(canvas, l_elbow, l_hand, self.color, self.stroke_w, cv2.LINE_AA)
        # Right Arm
        cv2.line(canvas, r_shoulder, r_elbow, self.color, self.stroke_w, cv2.LINE_AA)
        cv2.line(canvas, r_elbow, r_hand, self.color, self.stroke_w, cv2.LINE_AA)
        # Left Leg
        cv2.line(canvas, l_hip, l_knee, self.color, self.stroke_w, cv2.LINE_AA)
        cv2.line(canvas, l_knee, l_foot, self.color, self.stroke_w, cv2.LINE_AA)
        # Right Leg
        cv2.line(canvas, r_hip, r_knee, self.color, self.stroke_w, cv2.LINE_AA)
        cv2.line(canvas, r_knee, r_foot, self.color, self.stroke_w, cv2.LINE_AA)

        # 7. Hands & Feet: Empty Oval Outlines
        hand_axes = (14, 8)
        foot_axes = (16, 8)
        
        l_hand_ang = int(math.degrees(math.atan2(l_hand[1]-l_elbow[1], l_hand[0]-l_elbow[0])))
        r_hand_ang = int(math.degrees(math.atan2(r_hand[1]-r_elbow[1], r_hand[0]-r_elbow[0])))
        l_foot_ang = int(math.degrees(math.atan2(l_foot[1]-l_knee[1], l_foot[0]-l_knee[0])))
        r_foot_ang = int(math.degrees(math.atan2(r_foot[1]-r_knee[1], r_foot[0]-r_knee[0])))

        self.draw_ellipse_rotated(canvas, l_hand, hand_axes, l_hand_ang, self.color, 2)
        self.draw_ellipse_rotated(canvas, r_hand, hand_axes, r_hand_ang, self.color, 2)
        self.draw_ellipse_rotated(canvas, l_foot, foot_axes, l_foot_ang, self.color, 2)
        self.draw_ellipse_rotated(canvas, r_foot, foot_axes, r_foot_ang, self.color, 2)

# ==========================================
# 2. OpenCV Doodle drawing functions
# ==========================================
def draw_river_doodle(out_path):
    img = np.zeros((200, 200, 4), dtype=np.uint8)
    color = (245, 245, 245, 255)
    thick = 6
    
    # 3 winding river lines
    pts1 = np.array([[20, 80], [60, 60], [100, 110], [150, 70], [180, 120]], np.int32)
    cv2.polylines(img, [pts1], False, color, thick, lineType=cv2.LINE_AA)
    
    pts2 = pts1 + np.array([0, 25])
    cv2.polylines(img, [pts2], False, color, thick, lineType=cv2.LINE_AA)
    
    pts3 = pts1 + np.array([0, -25])
    cv2.polylines(img, [pts3], False, color, thick, lineType=cv2.LINE_AA)
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, img)
    print(f"Generated River Doodle -> {out_path}")
    return out_path

def draw_flower_doodle(out_path):
    img = np.zeros((200, 200, 4), dtype=np.uint8)
    color = (245, 245, 245, 255)
    thick = 6
    
    # Center circle
    cv2.circle(img, (100, 90), 16, color, thick, lineType=cv2.LINE_AA)
    
    # Petals
    petals = [
        (100, 60, 10, 18, 0),    # Top
        (100, 120, 10, 18, 0),   # Bottom
        (70, 90, 18, 10, 0),    # Left
        (130, 90, 18, 10, 0),   # Right
        (80, 70, 14, 14, 45),   # Top-Left
        (120, 110, 14, 14, 45),  # Bottom-Right
        (120, 70, 14, 14, -45),  # Top-Right
        (80, 110, 14, 14, -45)   # Bottom-Left
    ]
    for cx, cy, rx, ry, angle in petals:
        cv2.ellipse(img, (cx, cy), (rx, ry), angle, 0, 360, color, thick, lineType=cv2.LINE_AA)
        
    # Stem & Leaf
    cv2.line(img, (100, 130), (100, 185), color, thick, lineType=cv2.LINE_AA)
    pts_leaf = np.array([[100, 155], [125, 145], [100, 170]], np.int32)
    cv2.polylines(img, [pts_leaf], True, color, thick, lineType=cv2.LINE_AA)
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, img)
    print(f"Generated Flower Doodle -> {out_path}")
    return out_path

def draw_bean_doodle(out_path):
    img = np.zeros((200, 200, 4), dtype=np.uint8)
    color = (245, 245, 245, 255)
    thick = 6
    
    # 3 coffee/pea beans
    cv2.ellipse(img, (80, 100), (18, 28), 30, 0, 360, color, thick, lineType=cv2.LINE_AA)
    cv2.ellipse(img, (120, 100), (18, 28), -30, 0, 360, color, thick, lineType=cv2.LINE_AA)
    cv2.ellipse(img, (100, 135), (28, 18), 0, 0, 360, color, thick, lineType=cv2.LINE_AA)
    
    # Center grooves
    cv2.ellipse(img, (80, 100), (6, 16), 30, 180, 360, color, thick - 2, lineType=cv2.LINE_AA)
    cv2.ellipse(img, (120, 100), (6, 16), -30, 180, 360, color, thick - 2, lineType=cv2.LINE_AA)
    cv2.ellipse(img, (100, 135), (16, 6), 0, 90, 270, color, thick - 2, lineType=cv2.LINE_AA)
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, img)
    print(f"Generated Bean Doodle -> {out_path}")
    return out_path

def make_subtitle_clip(text, duration, start_time):
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    if not os.path.exists(font_path):
        font_path = "arial.ttf"
    
    font_size = 28
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()
        
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_str = " ".join(current_line)
        dummy_img = Image.new("RGBA", (1, 1))
        draw_dummy = ImageDraw.Draw(dummy_img)
        bbox = draw_dummy.textbbox((0, 0), test_str, font=font)
        w = bbox[2] - bbox[0]
        if w > 1000:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
        
    wrapped_text = "\n".join(lines)
    num_lines = len(lines)
    
    padding_y = 14 if num_lines == 1 else 18
    padding_x = 30
    
    max_w = 0
    dummy_img = Image.new("RGBA", (1, 1))
    draw_dummy = ImageDraw.Draw(dummy_img)
    
    line_heights = []
    for line in lines:
        bbox = draw_dummy.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        max_w = max(max_w, w)
        line_heights.append(h)
        
    spacing = 8
    total_h = sum(line_heights) + spacing * (num_lines - 1)
    
    box_w = max_w + padding_x * 2
    box_h = total_h + padding_y * 2
    
    img = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    box_x1 = (1280 - box_w) // 2
    box_y1 = 720 - box_h - 70
    box_x2 = box_x1 + box_w
    box_y2 = box_y1 + box_h
    
    draw.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], radius=12, fill=(17, 17, 17, 200))
    
    current_y = box_y1 + padding_y
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_x = box_x1 + (box_w - line_w) // 2
        draw.text((line_x, current_y), line, fill=(255, 255, 255, 255), font=font)
        current_y += line_heights[i] + spacing
        
    temp_dir = os.path.join(ROOT, "scratch", "temp_audio")
    os.makedirs(temp_dir, exist_ok=True)
    import uuid
    temp_path = os.path.join(temp_dir, f"subtitle_{uuid.uuid4().hex[:8]}.png")
    img.save(temp_path, "PNG")
    
    clip = (ImageClip(temp_path)
            .with_start(start_time)
            .with_duration(duration)
            .with_position((0, 0)))
    return clip

def main():
    print("Generating evolution graphic assets...")
    
    # 1. Image Text assets (Chalk White versions)
    txt_g = generate_text_lineart("ㄱ", os.path.join(ROOT, "assets", "graphics", "letters", "letter_ㄱ_chalk.png"), font_size=180, stroke_width=6)
    txt_kk = generate_text_lineart("ㄲ", os.path.join(ROOT, "assets", "graphics", "letters", "letter_ㄲ_chalk.png"), font_size=180, stroke_width=6)
    txt_k = generate_text_lineart("ㅋ", os.path.join(ROOT, "assets", "graphics", "letters", "letter_ㅋ_chalk.png"), font_size=180, stroke_width=6)
    
    txt_gang = generate_text_lineart("강", os.path.join(ROOT, "assets", "graphics", "letters", "word_강_chalk.png"), font_size=140, stroke_width=5)
    txt_kkot = generate_text_lineart("꽃", os.path.join(ROOT, "assets", "graphics", "letters", "word_꽃_chalk.png"), font_size=140, stroke_width=5)
    txt_kong = generate_text_lineart("콩", os.path.join(ROOT, "assets", "graphics", "letters", "word_콩_chalk.png"), font_size=140, stroke_width=5)
    
    # 2. Doodle Object assets (Chalk White versions)
    obj_river = draw_river_doodle(os.path.join(ROOT, "assets", "graphics", "obj_river_chalk.png"))
    obj_flower = draw_flower_doodle(os.path.join(ROOT, "assets", "graphics", "obj_flower_chalk.png"))
    obj_bean = draw_bean_doodle(os.path.join(ROOT, "assets", "graphics", "obj_bean_chalk.png"))
    
    # 3. Audio SFX paths
    pop_sound = os.path.join(ROOT, "assets", "audio", "pop.wav")
    whoosh_sound = os.path.join(ROOT, "assets", "audio", "whoosh.wav")
    chime_sound = os.path.join(ROOT, "assets", "audio", "bell_chime.wav")
    
    has_audio = os.path.exists(pop_sound)
    
    # Generate Narrations dynamically
    sc1_nar_path = "scratch/sfx_scene_1_narration.mp3"
    sc2_nar_path = "scratch/sfx_scene_2_narration.mp3"
    
    for p in (sc1_nar_path, sc2_nar_path):
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass
        
    gTTS(text="기억에 이렇게 획을 보태면 다른 자음으로 확장할수 있고", lang="ko").save(sc1_nar_path)
    gTTS(text="그 자음들이 다른 자음 모음과 합해져서 글자가 됩니다.", lang="ko").save(sc2_nar_path)
        
    # Load SFX audio clips
    whoosh_audio = AudioFileClip(whoosh_sound)
    pop_audio = AudioFileClip(pop_sound)
    chime_audio = AudioFileClip(chime_sound)
    
    sc1_narration = AudioFileClip(sc1_nar_path).with_effects([fx.MultiplySpeed(1.1)])
    sc2_narration = AudioFileClip(sc2_nar_path).with_effects([fx.MultiplySpeed(1.1)])
    
    zolla_engine = ProceduralZolla(stroke_w=4)
    
    # Generate procedural background and blackboard
    base_img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
    base_img = cv2.imread(base_img_path)
    base_img_resized = cv2.resize(base_img, (1280, 720))
    # Erase the white circle on the chalkboard by patching it with clean chalkboard texture
    patch = base_img_resized[170:250, 200:280].copy()
    base_img_resized[170:250, 420:500] = patch
    
    # 2. Erase the original static right arm and hand completely by patching clean chalkboard texture
    # We use a split patch: y=200~280, x=380~560 for the hand, and y=280~460, x=380~640 for the arm.
    patch_hand = base_img_resized[200:280, 200:380].copy()
    patch_arm = base_img_resized[280:460, 200:460].copy()
    base_img_resized[200:280, 380:560] = patch_hand
    base_img_resized[280:460, 380:640] = patch_arm
    
    wood_bg = base_img_resized
    
    # ========================================================
    # 🎥 SCENE 1: 'ㄱ' drawn three times and flies to UP, RIGHT, LEFT (11.0s)
    # ========================================================
    scene_1_dur = 11.0
    
    def make_scene_1_frame(t):
        frame = wood_bg.copy()
        
        # Determine current marker position (mx, my) and drawing path
        mx, my = 350, 300
        char_pose = "pointing"
        
        marker_color = (245, 245, 245) # BGR White/Light Chalk
        marker_thick = 8
        
        if t >= 0.5:
            if t < 2.0:
                char_pose = "writing_g"
                if t < 1.0:
                    p = (t - 0.5) / 0.5
                    mx = int(250 + 100 * p)
                    my = 200
                    cv2.line(frame, (250, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif t < 1.5:
                    p = (t - 1.0) / 0.5
                    mx = 350
                    my = int(200 + 100 * p)
                    cv2.line(frame, (250, 200), (350, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (350, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                else:
                    mx, my = 350, 300
                    cv2.line(frame, (250, 200), (350, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (350, 200), (350, 300), marker_color, marker_thick, cv2.LINE_AA)
            
            elif 3.2 <= t < 4.7:
                char_pose = "writing_g"
                if t < 3.45:
                    p = (t - 3.2) / 0.25
                    mx = int(210 + 80 * p)
                    my = 200
                    cv2.line(frame, (210, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif t < 3.7:
                    p = (t - 3.45) / 0.25
                    mx = 290
                    my = int(200 + 100 * p)
                    cv2.line(frame, (210, 200), (290, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (290, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif t < 3.95:
                    p = (t - 3.7) / 0.25
                    mx = int(310 + 80 * p)
                    my = 200
                    cv2.line(frame, (210, 200), (290, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (290, 200), (290, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (310, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif t < 4.2:
                    p = (t - 3.95) / 0.25
                    mx = 390
                    my = int(200 + 100 * p)
                    cv2.line(frame, (210, 200), (290, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (290, 200), (290, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (310, 200), (390, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (390, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                else:
                    mx, my = 390, 300
                    cv2.line(frame, (210, 200), (290, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (290, 200), (290, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (310, 200), (390, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (390, 200), (390, 300), marker_color, marker_thick, cv2.LINE_AA)
                        
            elif 6.0 <= t < 7.5:
                char_pose = "writing_g"
                if t < 6.33:
                    p = (t - 6.0) / 0.33
                    mx = int(250 + 100 * p)
                    my = 200
                    cv2.line(frame, (250, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif t < 6.66:
                    p = (t - 6.33) / 0.33
                    mx = 350
                    my = int(200 + 100 * p)
                    cv2.line(frame, (250, 200), (350, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (350, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif t < 7.0:
                    p = (t - 6.66) / 0.34
                    mx = int(250 + 80 * p)
                    my = 250
                    cv2.line(frame, (250, 200), (350, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (350, 200), (350, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 250), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                else:
                    mx, my = 330, 250
                    cv2.line(frame, (250, 200), (350, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (350, 200), (350, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 250), (330, 250), marker_color, marker_thick, cv2.LINE_AA)
        
        draw_active_arm(frame, mx, my)
        
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
    bg_1 = VideoClip(make_scene_1_frame).with_duration(scene_1_dur)
               
    # 1. ㄱ flies UP to become "강"
    def fly_up(t):
        p = min(1.0, t / 1.0)
        f = 1.0 - (1.0 - p)**3
        cur_x = 300
        cur_y = 230 + (130 - 230) * f
        return (int(cur_x), int(cur_y))
        
    fly_g_up = (ImageClip(txt_g)
                .with_start(2.0)
                .with_duration(1.0)
                .with_position(fly_up)
                .resized(width=70))
                
    word_gang_spot = (ImageClip(txt_gang)
                      .with_start(3.0)
                      .with_duration(scene_1_dur - 3.0)
                      .resized(width=80)
                      .with_position((300, 130)))
                      
    # 2. ㄲ flies RIGHT to become ㄲ -> "꽃"
    def fly_right(t):
        p = min(1.0, t / 1.0)
        f = 1.0 - (1.0 - p)**3
        cur_x = 300 + (410 - 300) * f
        cur_y = 230 + (350 - 230) * f
        return (int(cur_x), int(cur_y))
        
    fly_g_right = (ImageClip(txt_kk)
                   .with_start(4.7)
                   .with_duration(1.0)
                   .with_position(fly_right)
                   .resized(width=70))
                   
    kk_spot_temp = (ImageClip(txt_kk)
                    .with_start(5.7)
                    .with_duration(0.8)
                    .resized(width=70)
                    .with_position((415, 355)))
                    
    word_kkot_spot = (ImageClip(txt_kkot)
                      .with_start(6.5)
                      .with_duration(scene_1_dur - 6.5)
                      .resized(width=80)
                      .with_position((410, 350)))
                      
    # 3. ㅋ flies LEFT to become "콩"
    def fly_left(t):
        p = min(1.0, t / 1.0)
        f = 1.0 - (1.0 - p)**3
        cur_x = 300 + (210 - 300) * f
        cur_y = 230 + (350 - 230) * f
        return (int(cur_x), int(cur_y))
        
    fly_g_left = (ImageClip(txt_k)
                  .with_start(7.5)
                  .with_duration(1.0)
                  .with_position(fly_left)
                  .resized(width=70))
                  
    k_spot_temp = (ImageClip(txt_k)
                   .with_start(8.5)
                   .with_duration(0.8)
                   .resized(width=70)
                   .with_position((215, 355)))
                   
    word_kong_spot = (ImageClip(txt_kong)
                      .with_start(9.3)
                      .with_duration(scene_1_dur - 9.3)
                      .resized(width=80)
                      .with_position((210, 350)))
              
    logo_path = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
    logo_1 = None
    if os.path.exists(logo_path):
        logo_1 = (ImageClip(logo_path)
                  .resized((45, 45))
                  .with_duration(scene_1_dur)
                  .with_position((1280 - 45 - 20, 720 - 45 - 20)))
                  
    sub_1 = make_subtitle_clip("기억에 이렇게 획을 보태면 다른 자음으로 확장할수 있고", scene_1_dur, 0.0)
              
    clips_1 = [
        bg_1, fly_g_up, word_gang_spot, fly_g_right, kk_spot_temp, word_kkot_spot, 
        fly_g_left, k_spot_temp, word_kong_spot, sub_1
    ]
    if logo_1:
        clips_1.append(logo_1)
        
    scene_1 = CompositeVideoClip(clips_1, size=(1280, 720))
    
    if has_audio:
        s1_audios = [
            pop_audio.with_start(0.5),        # 1st ㄱ drawn
            whoosh_audio.with_start(2.0),     # 1st ㄱ flies
            pop_audio.with_start(3.0),        # "강" appears
            
            pop_audio.with_start(3.2),        # 2nd ㄱ drawn
            whoosh_audio.with_start(4.7),     # 2nd ㄱ flies
            pop_audio.with_start(5.7),        # "ㄲ" appears
            chime_audio.with_start(6.5),      # "꽃" appears
            
            pop_audio.with_start(6.0),        # 3rd ㄱ drawn
            whoosh_audio.with_start(7.5),     # 3rd ㄱ flies
            pop_audio.with_start(8.5),        # "ㅋ" appears
            chime_audio.with_start(9.3),      # "콩" appears
            
            sc1_narration.with_start(0.5)     # Scene 1 narration
        ]
        scene_1 = scene_1.with_audio(CompositeAudioClip(s1_audios))
        
    # ========================================================
    # 🎥 SCENE 2: Words morph to corresponding drawings (8.0s)
    # ========================================================
    scene_2_dur = 8.0
    
    def make_scene_2_frame(t):
        frame = wood_bg.copy()
        cx, cy = 880, 300
        
        if 1.8 <= t < 3.0:
            char_pose = "writing_g"
            p = t - 1.8
            if p < 0.4:  # Drawing River (1.8s ~ 2.2s)
                factor = p / 0.4
                mx = int(340 + 30 * math.sin(2.0 * math.pi * factor * 2.0))
                my = int(170 + 20 * math.cos(2.0 * math.pi * factor * 2.0))
            elif p < 0.8:  # Drawing Flower (2.2s ~ 2.6s)
                factor = (p - 0.4) / 0.4
                mx = int(450 + 30 * math.sin(2.0 * math.pi * factor * 2.0))
                my = int(390 + 20 * math.cos(2.0 * math.pi * factor * 2.0))
            else:  # Drawing Bean (2.6s ~ 3.0s)
                factor = (p - 0.8) / 0.4
                mx = int(250 + 30 * math.sin(2.0 * math.pi * factor * 2.0))
                my = int(390 + 20 * math.cos(2.0 * math.pi * factor * 2.0))
        else:
            char_pose = "pointing"
            mx, my = None, None
            
        draw_active_arm(frame, mx, my)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
    bg_2 = VideoClip(make_scene_2_frame).with_duration(scene_2_dur)
    
    # In Scene 2, the words STAY on screen for the entire duration!
    word_gang_clip = (ImageClip(txt_gang).with_duration(scene_2_dur).resized(width=80).with_position((300, 130)))
    word_kkot_clip = (ImageClip(txt_kkot).with_duration(scene_2_dur).resized(width=80).with_position((410, 350)))
    word_kong_clip = (ImageClip(txt_kong).with_duration(scene_2_dur).resized(width=80).with_position((210, 350)))
    
    # Doodle drawings appear behind the words and stay on screen alongside the words
    doodle_start = 1.8
    doodle_dur = scene_2_dur - doodle_start
    
    river_clip = (ImageClip(obj_river).with_start(doodle_start).with_duration(doodle_dur).resized(width=200).with_opacity(0.3).with_position((240, 70)))
    flower_clip = (ImageClip(obj_flower).with_start(doodle_start).with_duration(doodle_dur).resized(width=200).with_opacity(0.3).with_position((350, 290)))
    bean_clip = (ImageClip(obj_bean).with_start(doodle_start).with_duration(doodle_dur).resized(width=200).with_opacity(0.3).with_position((150, 290)))
    
    logo_2 = None
    if os.path.exists(logo_path):
        logo_2 = (ImageClip(logo_path)
                  .resized((45, 45))
                  .with_duration(scene_2_dur)
                  .with_position((1280 - 45 - 20, 720 - 45 - 20)))
                  
    sub_2 = make_subtitle_clip("그 자음들이 다른 자음 모음과 합해져서 글자가 됩니다.", scene_2_dur, 0.0)
                 
    clips_2 = [
        bg_2, 
        river_clip, flower_clip, bean_clip, 
        word_gang_clip, word_kkot_clip, word_kong_clip, 
        sub_2
    ]
    if logo_2:
        clips_2.append(logo_2)
        
    scene_2 = CompositeVideoClip(clips_2, size=(1280, 720))
    
    if has_audio:
        s2_audios = [
            chime_audio.with_start(1.8),      # magic chime when morphing to doodles
            sc2_narration.with_start(0.5)     # Scene 2 narration
        ]
        scene_2 = scene_2.with_audio(CompositeAudioClip(s2_audios))
        
    # ========================================================
    # 🔄 CONCATENATE & RENDER
    # ========================================================
    final_video = concatenate_videoclips([scene_1, scene_2])
    output_path = os.path.join(ROOT, "assets", "videos", "jay_whiteboard_r_evolution.mp4")
    
    print(f"Rendering evolution video to: {output_path}...")
    final_video.write_videofile(
        output_path, fps=30, codec="libx264", audio_codec="aac",
        threads=os.cpu_count() or 4, logger="bar"
    )
    print("Video rendered successfully!")

    # Save last frame
    last_frame_path = os.path.join(ROOT, "assets", "characters", "chalkboard_r_final.png")
    final_video.save_frame(last_frame_path, t=final_video.duration - 0.1)
    print(f"Saved last frame to: {last_frame_path}")

    # 4. DATABASE REGISTRATION
    print("\n=== Registering in Local SQLite content.db ===")
    sqlite_path = os.path.join(ROOT, "channel", "content.db")
    if os.path.exists(sqlite_path):
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        
        project = "jay_r_evolution"
        scene_no = 1
        scene_name = "Jay_Whiteboard_R_Evolution_Video"
        base_image = "assets/characters/jay_writing_board_side_opaque.png"
        
        c_desc = (
            "Hangeul Consonants ㄱ, ㄲ, ㅋ drawn on chalkboard, flying out to become words 강, 꽃, 콩, "
            "which remain next to their corresponding doodles."
        )
        file_path = "assets/videos/jay_whiteboard_r_evolution.mp4"
        duration_sec = scene_1_dur + scene_2_dur
        
        cur.execute("SELECT id FROM video_clips WHERE project=? AND scene_no=?", (project, scene_no))
        row = cur.fetchone()
        
        if row:
            cur.execute("""
                UPDATE video_clips
                SET scene_name=?, base_image=?, file_path=?, duration_sec=?, status='success', notes=?
                WHERE id=?
            """, (scene_name, base_image, file_path, duration_sec, c_desc, row[0]))
            print(f"Updated SQLite video_clips record (ID: {row[0]})")
        else:
            cur.execute("""
                INSERT INTO video_clips (project, scene_no, scene_name, base_image, file_path, duration_sec, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, 'success', ?)
            """, (project, scene_no, scene_name, base_image, file_path, duration_sec, c_desc))
            print("Inserted new SQLite video_clips record!")
            
        conn.commit()
        cur.close()
        conn.close()
        print("Registration completed successfully!")
    else:
        print("[ERR] content.db not found.")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
