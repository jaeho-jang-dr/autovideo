# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import cv2
import sqlite3
import math
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy.video.fx as fx
from moviepy import (
    AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip, concatenate_videoclips, VideoClip
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
sys.stdout.reconfigure(encoding='utf-8')

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
# 2. OpenCV Doodle drawing functions
# ==========================================
def draw_snow_doodle(out_path):
    img = np.zeros((200, 200, 4), dtype=np.uint8)
    color = (245, 245, 245, 255)
    thick = 6
    cx, cy = 100, 100
    for i in range(8):
        angle = i * math.pi / 4
        x2 = int(cx + 65 * math.cos(angle))
        y2 = int(cy + 65 * math.sin(angle))
        cv2.line(img, (cx, cy), (x2, y2), color, thick, lineType=cv2.LINE_AA)
        v1_x = int(x2 - 15 * math.cos(angle - math.pi/4))
        v1_y = int(y2 - 15 * math.sin(angle - math.pi/4))
        v2_x = int(x2 - 15 * math.cos(angle + math.pi/4))
        v2_y = int(y2 - 15 * math.sin(angle + math.pi/4))
        cv2.line(img, (x2, y2), (v1_x, v1_y), color, thick - 2, lineType=cv2.LINE_AA)
        cv2.line(img, (x2, y2), (v2_x, v2_y), color, thick - 2, lineType=cv2.LINE_AA)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, img)
    print(f"Generated Snow Doodle -> {out_path}")
    return out_path

def draw_moon_doodle(out_path):
    img = np.zeros((200, 200, 4), dtype=np.uint8)
    color = (245, 245, 245, 255)
    thick = 6
    cv2.ellipse(img, (90, 100), (60, 60), 0, -80, 80, color, thick, lineType=cv2.LINE_AA)
    cv2.ellipse(img, (115, 100), (50, 50), 0, -78, 78, color, thick, lineType=cv2.LINE_AA)
    cv2.line(img, (100, 41), (104, 51), color, thick, lineType=cv2.LINE_AA)
    cv2.line(img, (100, 159), (104, 149), color, thick, lineType=cv2.LINE_AA)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, img)
    print(f"Generated Moon Doodle -> {out_path}")
    return out_path

def draw_earth_doodle(out_path):
    img = np.zeros((200, 200, 4), dtype=np.uint8)
    color = (245, 245, 245, 255)
    thick = 6
    # Ground line
    cv2.line(img, (20, 160), (180, 160), color, thick, lineType=cv2.LINE_AA)
    # Sprout stem
    cv2.line(img, (100, 160), (100, 95), color, thick, lineType=cv2.LINE_AA)
    # Left leaf
    cv2.ellipse(img, (85, 105), (15, 8), -30, 0, 360, color, thick - 2, lineType=cv2.LINE_AA)
    # Right leaf
    cv2.ellipse(img, (115, 105), (15, 8), 30, 0, 360, color, thick - 2, lineType=cv2.LINE_AA)
    # Pebbles
    cv2.ellipse(img, (50, 160), (12, 6), 0, 180, 360, color, thick - 2, lineType=cv2.LINE_AA)
    cv2.ellipse(img, (150, 160), (15, 8), 0, 180, 360, color, thick - 2, lineType=cv2.LINE_AA)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, img)
    print(f"Generated Earth Doodle -> {out_path}")
    return out_path

def draw_tower_doodle(out_path):
    img = np.zeros((200, 200, 4), dtype=np.uint8)
    color = (245, 245, 245, 255)
    thick = 6
    cv2.rectangle(img, (40, 160), (160, 185), color, thick, lineType=cv2.LINE_AA)
    cv2.rectangle(img, (50, 120), (150, 160), color, thick, lineType=cv2.LINE_AA)
    cv2.rectangle(img, (65, 85), (135, 120), color, thick, lineType=cv2.LINE_AA)
    cv2.rectangle(img, (80, 55), (120, 85), color, thick, lineType=cv2.LINE_AA)
    cv2.line(img, (100, 55), (100, 20), color, thick, lineType=cv2.LINE_AA)
    cv2.circle(img, (100, 25), 8, color, thick, lineType=cv2.LINE_AA)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, img)
    print(f"Generated Tower Doodle -> {out_path}")
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
    print("Generating evolution graphic assets (ㄴ, ㄷ, ㄸ, ㅌ)...")
    txt_g = generate_text_lineart("ㄴ", os.path.join(ROOT, "assets", "graphics", "letters", "letter_ㄴ_chalk.png"), font_size=180, stroke_width=6)
    txt_d = generate_text_lineart("ㄷ", os.path.join(ROOT, "assets", "graphics", "letters", "letter_ㄷ_chalk.png"), font_size=180, stroke_width=6)
    txt_dd = generate_text_lineart("ㄸ", os.path.join(ROOT, "assets", "graphics", "letters", "letter_ㄸ_chalk.png"), font_size=180, stroke_width=6)
    txt_t = generate_text_lineart("ㅌ", os.path.join(ROOT, "assets", "graphics", "letters", "letter_ㅌ_chalk.png"), font_size=180, stroke_width=6)
    
    txt_nun = generate_text_lineart("눈", os.path.join(ROOT, "assets", "graphics", "letters", "word_눈_chalk.png"), font_size=140, stroke_width=5)
    txt_dal = generate_text_lineart("달", os.path.join(ROOT, "assets", "graphics", "letters", "word_달_chalk.png"), font_size=140, stroke_width=5)
    txt_ttang = generate_text_lineart("땅", os.path.join(ROOT, "assets", "graphics", "letters", "word_땅_chalk.png"), font_size=140, stroke_width=5)
    txt_tap = generate_text_lineart("탑", os.path.join(ROOT, "assets", "graphics", "letters", "word_탑_chalk.png"), font_size=140, stroke_width=5)
    
    obj_snow = draw_snow_doodle(os.path.join(ROOT, "assets", "graphics", "obj_snow_chalk.png"))
    obj_moon = draw_moon_doodle(os.path.join(ROOT, "assets", "graphics", "obj_moon_chalk.png"))
    obj_earth = draw_earth_doodle(os.path.join(ROOT, "assets", "graphics", "obj_earth_chalk.png"))
    obj_tower = draw_tower_doodle(os.path.join(ROOT, "assets", "graphics", "obj_tower_chalk.png"))
    
    pop_sound = os.path.join(ROOT, "assets", "audio", "pop.wav")
    whoosh_sound = os.path.join(ROOT, "assets", "audio", "whoosh.wav")
    chime_sound = os.path.join(ROOT, "assets", "audio", "bell_chime.wav")
    
    has_audio = os.path.exists(pop_sound)
    
    sc1_nar_path = "scratch/sfx_scene_1_narration_n.mp3"
    sc2_nar_path = "scratch/sfx_scene_2_narration_n.mp3"
    
    for p in (sc1_nar_path, sc2_nar_path):
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass
        
    gTTS(text="니은에 이렇게 획을 보태면 다른 자음으로 확장할수 있고", lang="ko").save(sc1_nar_path)
    gTTS(text="그 자음들이 다른 자음 모음과 합해져서 글자가 됩니다.", lang="ko").save(sc2_nar_path)
        
    whoosh_audio = AudioFileClip(whoosh_sound)
    pop_audio = AudioFileClip(pop_sound)
    chime_audio = AudioFileClip(chime_sound)
    
    sc1_narration = AudioFileClip(sc1_nar_path).with_effects([fx.MultiplySpeed(1.1)])
    sc2_narration = AudioFileClip(sc2_nar_path).with_effects([fx.MultiplySpeed(1.1)])
    
    base_img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
    base_img = cv2.imread(base_img_path)
    base_img_resized = cv2.resize(base_img, (1280, 720))
    patch = base_img_resized[170:250, 200:280].copy()
    base_img_resized[170:250, 420:500] = patch
    
    # 280px Split Patch to preserve round chin/head
    patch_hand = base_img_resized[200:270, 200:380].copy()
    patch_arm = base_img_resized[270:460, 200:455].copy()
    base_img_resized[200:270, 380:560] = patch_hand
    base_img_resized[270:460, 380:635] = patch_arm
    wood_bg = base_img_resized
    
    # ========================================================
    # 🎥 SCENE 1: 'ㄴ, ㄷ, ㄸ, ㅌ' drawn and fly (13.5s)
    # ========================================================
    scene_1_dur = 13.5
    
    def make_scene_1_frame(t):
        prev_frame_path = os.path.join(ROOT, "assets", "characters", "chalkboard_r_final.png")
        if t < 1.0 and os.path.exists(prev_frame_path):
            prev_frame = cv2.imread(prev_frame_path)
            prev_frame = cv2.resize(prev_frame, (1280, 720))
            return cv2.cvtColor(prev_frame, cv2.COLOR_BGR2RGB)
            
        t_rel = t - 1.0
        frame = wood_bg.copy()
        mx, my = 350, 300
        char_pose = "pointing"
        marker_color = (245, 245, 245)
        marker_thick = 8
        
        if t_rel >= 0.5:
            # 1. ㄴ: t_rel = 0.5 ~ 2.0
            if t_rel < 2.0:
                char_pose = "writing_g"
                if t_rel < 1.25:
                    p = (t_rel - 0.5) / 0.75
                    mx = 250
                    my = int(200 + 100 * p)
                    cv2.line(frame, (250, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                else:
                    p = (t_rel - 1.25) / 0.75
                    mx = int(250 + 100 * p)
                    my = 300
                    cv2.line(frame, (250, 200), (250, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 300), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
            
            # 2. ㄷ: t_rel = 3.2 ~ 4.7
            elif 3.2 <= t_rel < 4.7:
                char_pose = "writing_g"
                if t_rel < 3.7:
                    p = (t_rel - 3.2) / 0.5
                    mx = int(250 + 100 * p)
                    my = 200
                    cv2.line(frame, (250, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif t_rel < 4.2:
                    p = (t_rel - 3.7) / 0.5
                    mx = 250
                    my = int(200 + 100 * p)
                    cv2.line(frame, (250, 200), (350, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                else:
                    p = (t_rel - 4.2) / 0.5
                    mx = int(250 + 100 * p)
                    my = 300
                    cv2.line(frame, (250, 200), (350, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 200), (250, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 300), (mx, my), marker_color, marker_thick, cv2.LINE_AA)

            # 3. ㄸ: t_rel = 5.9 ~ 7.4
            elif 5.9 <= t_rel < 7.4:
                char_pose = "writing_g"
                # First ㄷ: top, vertical, bottom (x=210~290)
                if t_rel < 6.15:
                    p = (t_rel - 5.9) / 0.25
                    mx = int(210 + 80 * p)
                    my = 200
                    cv2.line(frame, (210, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif t_rel < 6.4:
                    p = (t_rel - 6.15) / 0.25
                    mx = 210
                    my = int(200 + 100 * p)
                    cv2.line(frame, (210, 200), (290, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (210, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif t_rel < 6.65:
                    p = (t_rel - 6.4) / 0.25
                    mx = int(210 + 80 * p)
                    my = 300
                    cv2.line(frame, (210, 200), (290, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (210, 200), (210, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (210, 300), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                # Second ㄷ: top, vertical, bottom (x=310~390)
                elif t_rel < 6.9:
                    p = (t_rel - 6.65) / 0.25
                    mx = int(310 + 80 * p)
                    my = 200
                    cv2.line(frame, (210, 200), (290, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (210, 200), (210, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (210, 300), (290, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (310, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif t_rel < 7.15:
                    p = (t_rel - 6.9) / 0.25
                    mx = 310
                    my = int(200 + 100 * p)
                    cv2.line(frame, (210, 200), (290, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (210, 200), (210, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (210, 300), (290, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (310, 200), (390, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (310, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                else:
                    p = (t_rel - 7.15) / 0.25
                    mx = int(310 + 80 * p)
                    my = 300
                    cv2.line(frame, (210, 200), (290, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (210, 200), (210, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (210, 300), (290, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (310, 200), (390, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (310, 200), (310, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (310, 300), (mx, my), marker_color, marker_thick, cv2.LINE_AA)

            # 4. ㅌ: t_rel = 8.6 ~ 10.1
            elif 8.6 <= t_rel < 10.1:
                char_pose = "writing_g"
                if t_rel < 8.9:
                    p = (t_rel - 8.6) / 0.3
                    mx = int(250 + 100 * p)
                    my = 200
                    cv2.line(frame, (250, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif t_rel < 9.2:
                    p = (t_rel - 8.9) / 0.3
                    mx = int(250 + 80 * p)
                    my = 250
                    cv2.line(frame, (250, 200), (350, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 250), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif t_rel < 9.6:
                    p = (t_rel - 9.2) / 0.4
                    mx = 250
                    my = int(200 + 100 * p)
                    cv2.line(frame, (250, 200), (350, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 250), (330, 250), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 200), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                else:
                    p = (t_rel - 9.6) / 0.5
                    mx = int(250 + 100 * p)
                    my = 300
                    cv2.line(frame, (250, 200), (350, 200), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 250), (330, 250), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 200), (250, 300), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 300), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
        
        draw_active_arm(frame, mx, my)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
    bg_1 = VideoClip(make_scene_1_frame).with_duration(scene_1_dur)
               
    def fly_top_left(t):
        p = min(1.0, t / 1.0)
        f = 1.0 - (1.0 - p)**3
        cur_x = 300 + (200 - 300) * f
        cur_y = 230 + (120 - 230) * f
        return (int(cur_x), int(cur_y))
        
    def fly_top_right(t):
        p = min(1.0, t / 1.0)
        f = 1.0 - (1.0 - p)**3
        cur_x = 300 + (380 - 300) * f
        cur_y = 230 + (120 - 230) * f
        return (int(cur_x), int(cur_y))
        
    def fly_bottom_left(t):
        p = min(1.0, t / 1.0)
        f = 1.0 - (1.0 - p)**3
        cur_x = 300 + (200 - 300) * f
        cur_y = 230 + (340 - 230) * f
        return (int(cur_x), int(cur_y))
        
    def fly_bottom_right(t):
        p = min(1.0, t / 1.0)
        f = 1.0 - (1.0 - p)**3
        cur_x = 300 + (380 - 300) * f
        cur_y = 230 + (340 - 230) * f
        return (int(cur_x), int(cur_y))
        
    # Consonant fly clips
    fly_g_1 = (ImageClip(txt_g)
               .with_start(3.2)
               .with_duration(1.0)
               .with_position(fly_top_left)
               .resized(width=70))
               
    word_nun_spot = (ImageClip(txt_nun)
                     .with_start(3.2)
                     .with_duration(scene_1_dur - 3.2)
                     .resized(width=80)
                     .with_position((200, 120)))
                     
    fly_g_2 = (ImageClip(txt_d)
               .with_start(5.9)
               .with_duration(1.0)
               .with_position(fly_top_right)
               .resized(width=70))
               
    word_dal_spot = (ImageClip(txt_dal)
                     .with_start(5.9)
                     .with_duration(scene_1_dur - 5.9)
                     .resized(width=80)
                     .with_position((380, 120)))
                     
    fly_g_3 = (ImageClip(txt_dd)
               .with_start(8.6)
               .with_duration(1.0)
               .with_position(fly_bottom_left)
               .resized(width=70))
               
    word_ttang_spot = (ImageClip(txt_ttang)
                       .with_start(8.6)
                       .with_duration(scene_1_dur - 8.6)
                       .resized(width=80)
                       .with_position((200, 340)))
                       
    fly_g_4 = (ImageClip(txt_t)
               .with_start(11.3)
               .with_duration(1.0)
               .with_position(fly_bottom_right)
               .resized(width=70))
               
    word_tap_spot = (ImageClip(txt_tap)
                     .with_start(11.3)
                     .with_duration(scene_1_dur - 11.3)
                     .resized(width=80)
                     .with_position((380, 340)))
              
    logo_path = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
    logo_1 = None
    if os.path.exists(logo_path):
        logo_1 = (ImageClip(logo_path)
                  .resized((45, 45))
                  .with_duration(scene_1_dur)
                  .with_position((1280 - 45 - 20, 720 - 45 - 20)))
                  
    sub_1 = make_subtitle_clip("니은에 이렇게 획을 보태면 다른 자음으로 확장할수 있고", scene_1_dur - 1.0, 1.0)
              
    clips_1 = [
        bg_1, fly_g_1, word_nun_spot, fly_g_2, word_dal_spot, 
        fly_g_3, word_ttang_spot, fly_g_4, word_tap_spot, sub_1
    ]
    if logo_1:
        clips_1.append(logo_1)
        
    scene_1 = CompositeVideoClip(clips_1, size=(1280, 720))
    
    if has_audio:
        s1_audios = [
            whoosh_audio.with_start(1.0),
            
            pop_audio.with_start(1.5),
            pop_audio.with_start(3.0),
            whoosh_audio.with_start(3.2),
            chime_audio.with_start(4.2),
            
            pop_audio.with_start(4.2),
            pop_audio.with_start(5.7),
            whoosh_audio.with_start(5.9),
            chime_audio.with_start(6.9),
            
            pop_audio.with_start(6.9),
            pop_audio.with_start(8.4),
            whoosh_audio.with_start(8.6),
            chime_audio.with_start(9.6),
            
            pop_audio.with_start(9.6),
            pop_audio.with_start(11.1),
            whoosh_audio.with_start(11.3),
            chime_audio.with_start(12.3),
            
            sc1_narration.with_start(0.5)
        ]
        scene_1 = scene_1.with_audio(CompositeAudioClip(s1_audios))
        
    # ========================================================
    # 🎥 SCENE 2: Words morph to corresponding drawings (8.0s)
    # ========================================================
    scene_2_dur = 8.0
    
    def make_scene_2_frame(t):
        frame = wood_bg.copy()
        
        # Circle trace animation for 4 words (0.5s per word)
        if 1.8 <= t < 3.8:
            p = t - 1.8
            if p < 0.5:
                factor = p / 0.5
                mx = int(240 + 30 * math.sin(2.0 * math.pi * factor * 2.0))
                my = int(160 + 20 * math.cos(2.0 * math.pi * factor * 2.0))
            elif p < 1.0:
                factor = (p - 0.5) / 0.5
                mx = int(420 + 30 * math.sin(2.0 * math.pi * factor * 2.0))
                my = int(160 + 20 * math.cos(2.0 * math.pi * factor * 2.0))
            elif p < 1.5:
                factor = (p - 1.0) / 0.5
                mx = int(240 + 30 * math.sin(2.0 * math.pi * factor * 2.0))
                my = int(380 + 20 * math.cos(2.0 * math.pi * factor * 2.0))
            else:
                factor = (p - 1.5) / 0.5
                mx = int(420 + 30 * math.sin(2.0 * math.pi * factor * 2.0))
                my = int(380 + 20 * math.cos(2.0 * math.pi * factor * 2.0))
        else:
            mx, my = None, None
            
        draw_active_arm(frame, mx, my)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
    bg_2 = VideoClip(make_scene_2_frame).with_duration(scene_2_dur)
    
    word_nun_clip = (ImageClip(txt_nun).with_duration(scene_2_dur).resized(width=80).with_position((200, 120)))
    word_dal_clip = (ImageClip(txt_dal).with_duration(scene_2_dur).resized(width=80).with_position((380, 120)))
    word_ttang_clip = (ImageClip(txt_ttang).with_duration(scene_2_dur).resized(width=80).with_position((200, 340)))
    word_tap_clip = (ImageClip(txt_tap).with_duration(scene_2_dur).resized(width=80).with_position((380, 340)))
    
    doodle_start = 1.8
    doodle_dur = scene_2_dur - doodle_start
    
    snow_doodle = (ImageClip(obj_snow).with_start(doodle_start).with_duration(doodle_dur).resized(width=200).with_opacity(0.3).with_position((140, 60)))
    moon_doodle = (ImageClip(obj_moon).with_start(doodle_start).with_duration(doodle_dur).resized(width=200).with_opacity(0.3).with_position((320, 60)))
    earth_doodle = (ImageClip(obj_earth).with_start(doodle_start).with_duration(doodle_dur).resized(width=200).with_opacity(0.3).with_position((140, 280)))
    tower_doodle = (ImageClip(obj_tower).with_start(doodle_start).with_duration(doodle_dur).resized(width=200).with_opacity(0.3).with_position((320, 280)))
    
    logo_2 = None
    if os.path.exists(logo_path):
        logo_2 = (ImageClip(logo_path)
                  .resized((45, 45))
                  .with_duration(scene_2_dur)
                  .with_position((1280 - 45 - 20, 720 - 45 - 20)))
                  
    sub_2 = make_subtitle_clip("그 자음들이 다른 자음 모음과 합해져서 글자가 됩니다.", scene_2_dur, 0.0)
                 
    clips_2 = [
        bg_2, 
        snow_doodle, moon_doodle, earth_doodle, tower_doodle, 
        word_nun_clip, word_dal_clip, word_ttang_clip, word_tap_clip, 
        sub_2
    ]
    if logo_2:
        clips_2.append(logo_2)
        
    scene_2 = CompositeVideoClip(clips_2, size=(1280, 720))
    
    if has_audio:
        s2_audios = [
            chime_audio.with_start(1.8),
            sc2_narration.with_start(0.5)
        ]
        scene_2 = scene_2.with_audio(CompositeAudioClip(s2_audios))
        
    final_video = concatenate_videoclips([scene_1, scene_2])
    output_path = os.path.join(ROOT, "assets", "videos", "jay_whiteboard_s_evolution.mp4")
    
    print(f"Rendering evolution video to: {output_path}...")
    final_video.write_videofile(
        output_path, fps=30, codec="libx264", audio_codec="aac",
        threads=os.cpu_count() or 4, logger="bar"
    )
    print("Video rendered successfully!")

    # Save last frame
    last_frame_path = os.path.join(ROOT, "assets", "characters", "chalkboard_s_final.png")
    final_video.save_frame(last_frame_path, t=final_video.duration - 0.1)
    print(f"Saved last frame to: {last_frame_path}")

    print("\n=== Registering in Local SQLite content.db ===")
    sqlite_path = os.path.join(ROOT, "channel", "content.db")
    if os.path.exists(sqlite_path):
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        
        project = "jay_s_evolution"
        scene_no = 1
        scene_name = "Jay_Whiteboard_S_Evolution_Video"
        base_image = "assets/characters/jay_writing_board_side_opaque.png"
        
        c_desc = (
            "Hangeul Consonants ㄴ, ㄷ, ㄸ, ㅌ drawn on chalkboard, flying out to become words 눈, 달, 땅, 탑, "
            "which remain next to their corresponding doodles."
        )
        file_path = "assets/videos/jay_whiteboard_s_evolution.mp4"
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
