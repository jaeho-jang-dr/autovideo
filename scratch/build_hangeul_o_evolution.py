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
def draw_crown_doodle(out_path):
    img = np.zeros((200, 200, 4), dtype=np.uint8)
    color = (245, 245, 245, 255)
    thick = 6
    # Crown shape: W shape with base
    pts = np.array([[30, 150], [30, 70], [70, 110], [100, 50], [130, 110], [170, 70], [170, 150]], np.int32)
    cv2.polylines(img, [pts], False, color, thick, lineType=cv2.LINE_AA)
    cv2.line(img, (20, 150), (180, 150), color, thick, lineType=cv2.LINE_AA)
    # Jewels (3 small circles on peaks)
    cv2.circle(img, (30, 70), 6, color, -1, lineType=cv2.LINE_AA)
    cv2.circle(img, (100, 50), 6, color, -1, lineType=cv2.LINE_AA)
    cv2.circle(img, (170, 70), 6, color, -1, lineType=cv2.LINE_AA)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, img)
    print(f"Generated Crown Doodle -> {out_path}")
    return out_path

def draw_sun_doodle(out_path):
    img = np.zeros((200, 200, 4), dtype=np.uint8)
    color = (245, 245, 245, 255)
    thick = 6
    cx, cy = 100, 100
    r = 35
    # Center sun circle
    cv2.circle(img, (cx, cy), r, color, thick, lineType=cv2.LINE_AA)
    # 8 ray lines extending outward
    for i in range(8):
        angle = i * math.pi / 4
        x1 = int(cx + (r + 10) * math.cos(angle))
        y1 = int(cy + (r + 10) * math.sin(angle))
        x2 = int(cx + (r + 30) * math.cos(angle))
        y2 = int(cy + (r + 30) * math.sin(angle))
        cv2.line(img, (x1, y1), (x2, y2), color, thick - 2, lineType=cv2.LINE_AA)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, img)
    print(f"Generated Sun Doodle -> {out_path}")
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
    print("Generating evolution graphic assets (ㅇ)...")
    txt_g = generate_text_lineart("ㅇ", os.path.join(ROOT, "assets", "graphics", "letters", "letter_ㅇ_chalk.png"), font_size=180, stroke_width=6)
    txt_kk = generate_text_lineart("ㅎ", os.path.join(ROOT, "assets", "graphics", "letters", "letter_ㅎ_chalk.png"), font_size=180, stroke_width=6)
    
    txt_gang = generate_text_lineart("왕", os.path.join(ROOT, "assets", "graphics", "letters", "word_왕_chalk.png"), font_size=140, stroke_width=5)
    txt_kkot = generate_text_lineart("해", os.path.join(ROOT, "assets", "graphics", "letters", "word_해_chalk.png"), font_size=140, stroke_width=5)
    
    obj_river = draw_crown_doodle(os.path.join(ROOT, "assets", "graphics", "obj_crown_chalk.png"))
    obj_flower = draw_sun_doodle(os.path.join(ROOT, "assets", "graphics", "obj_sun_chalk.png"))
    
    pop_sound = os.path.join(ROOT, "assets", "audio", "pop.wav")
    whoosh_sound = os.path.join(ROOT, "assets", "audio", "whoosh.wav")
    chime_sound = os.path.join(ROOT, "assets", "audio", "bell_chime.wav")
    
    has_audio = os.path.exists(pop_sound)
    
    sc1_nar_path = "scratch/sfx_scene_1_narration_o.mp3"
    sc2_nar_path = "scratch/sfx_scene_2_narration_o.mp3"
    
    for p in (sc1_nar_path, sc2_nar_path):
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass
        
    gTTS(text="이응에 이렇게 획을 보태면 다른 자음으로 확장할수 있고", lang="ko").save(sc1_nar_path)
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
    
    patch_hand = base_img_resized[200:270, 200:380].copy()
    patch_arm = base_img_resized[270:460, 200:455].copy()
    base_img_resized[200:270, 380:560] = patch_hand
    base_img_resized[270:460, 380:635] = patch_arm
    wood_bg = base_img_resized
    
    # ========================================================
    # 🎥 SCENE 1: 'ㅇ' and 'ㅎ' drawn and fly (8.0s total)
    # ========================================================
    scene_1_dur = 8.0
    
    def make_scene_1_frame(t):
        frame = wood_bg.copy()
        mx, my = 350, 300
        marker_color = (245, 245, 245)
        marker_thick = 8
        
        if t >= 0.5:
            if t < 2.0:
                p = (t - 0.5) / 1.5
                angle = p * 2.0 * math.pi
                mx = int(300 + 50 * math.sin(angle))
                my = int(250 - 50 * math.cos(angle))
                
                num_points = int(p * 50)
                for idx in range(num_points):
                    ang = (idx / 50.0) * 2.0 * math.pi
                    pt_x = int(300 + 50 * math.sin(ang))
                    pt_y = int(250 - 50 * math.cos(ang))
                    cv2.circle(frame, (pt_x, pt_y), 4, marker_color, -1, lineType=cv2.LINE_AA)
            
            elif 3.2 <= t < 4.7:
                p = (t - 3.2) / 1.5
                if p < 0.2:
                    p2 = p / 0.2
                    mx = int(280 + 40 * p2)
                    my = 160
                    cv2.line(frame, (280, 160), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                elif p < 0.45:
                    p2 = (p - 0.2) / 0.25
                    mx = int(250 + 100 * p2)
                    my = 190
                    cv2.line(frame, (280, 160), (320, 160), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 190), (mx, my), marker_color, marker_thick, cv2.LINE_AA)
                else:
                    p2 = (p - 0.45) / 0.55
                    angle = p2 * 2.0 * math.pi
                    mx = int(300 + 40 * math.sin(angle))
                    my = int(250 - 40 * math.cos(angle))
                    
                    cv2.line(frame, (280, 160), (320, 160), marker_color, marker_thick, cv2.LINE_AA)
                    cv2.line(frame, (250, 190), (350, 190), marker_color, marker_thick, cv2.LINE_AA)
                    
                    num_pts = int(p2 * 40)
                    for idx in range(num_pts):
                        ang = (idx / 40.0) * 2.0 * math.pi
                        pt_x = int(300 + 40 * math.sin(ang))
                        pt_y = int(250 - 40 * math.cos(ang))
                        cv2.circle(frame, (pt_x, pt_y), 4, marker_color, -1, lineType=cv2.LINE_AA)
        
        draw_active_arm(frame, mx, my)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
    bg_1 = VideoClip(make_scene_1_frame).with_duration(scene_1_dur)
               
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
              
    logo_path = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
    logo_1 = None
    if os.path.exists(logo_path):
        logo_1 = (ImageClip(logo_path)
                  .resized((45, 45))
                  .with_duration(scene_1_dur)
                  .with_position((1280 - 45 - 20, 720 - 45 - 20)))
                  
    sub_1 = make_subtitle_clip("이응에 이렇게 획을 보태면 다른 자음으로 확장할수 있고", scene_1_dur, 0.0)
              
    clips_1 = [
        bg_1, fly_g_up, word_gang_spot, fly_g_right, kk_spot_temp, word_kkot_spot, sub_1
    ]
    if logo_1:
        clips_1.append(logo_1)
        
    scene_1 = CompositeVideoClip(clips_1, size=(1280, 720))
    
    if has_audio:
        s1_audios = [
            pop_audio.with_start(0.5),
            whoosh_audio.with_start(2.0),
            pop_audio.with_start(3.0),
            
            pop_audio.with_start(3.2),
            whoosh_audio.with_start(4.7),
            pop_audio.with_start(5.7),
            chime_audio.with_start(6.5),
            
            sc1_narration.with_start(0.5)
        ]
        scene_1 = scene_1.with_audio(CompositeAudioClip(s1_audios))
        
    # ========================================================
    # 🎥 SCENE 2: Words morph to corresponding drawings (6.0s)
    # ========================================================
    scene_2_dur = 6.0
    
    def make_scene_2_frame(t):
        frame = wood_bg.copy()
        
        if 1.8 <= t < 2.6:
            p = t - 1.8
            if p < 0.4:
                factor = p / 0.4
                mx = int(340 + 30 * math.sin(2.0 * math.pi * factor * 2.0))
                my = int(170 + 20 * math.cos(2.0 * math.pi * factor * 2.0))
            else:
                factor = (p - 0.4) / 0.4
                mx = int(450 + 30 * math.sin(2.0 * math.pi * factor * 2.0))
                my = int(390 + 20 * math.cos(2.0 * math.pi * factor * 2.0))
        else:
            mx, my = None, None
            
        draw_active_arm(frame, mx, my)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
    bg_2 = VideoClip(make_scene_2_frame).with_duration(scene_2_dur)
    
    word_gang_clip = (ImageClip(txt_gang).with_duration(scene_2_dur).resized(width=80).with_position((300, 130)))
    word_kkot_clip = (ImageClip(txt_kkot).with_duration(scene_2_dur).resized(width=80).with_position((410, 350)))
    
    doodle_start = 1.8
    doodle_dur = scene_2_dur - doodle_start
    
    river_clip = (ImageClip(obj_river).with_start(doodle_start).with_duration(doodle_dur).resized(width=200).with_opacity(0.3).with_position((240, 70)))
    flower_clip = (ImageClip(obj_flower).with_start(doodle_start).with_duration(doodle_dur).resized(width=200).with_opacity(0.3).with_position((350, 290)))
    
    logo_2 = None
    if os.path.exists(logo_path):
        logo_2 = (ImageClip(logo_path)
                  .resized((45, 45))
                  .with_duration(scene_2_dur)
                  .with_position((1280 - 45 - 20, 720 - 45 - 20)))
                  
    sub_2 = make_subtitle_clip("그 자음들이 다른 자음 모음과 합해져서 글자가 됩니다.", scene_2_dur, 0.0)
                 
    clips_2 = [
        bg_2, 
        river_clip, flower_clip, 
        word_gang_clip, word_kkot_clip, 
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
    output_path = os.path.join(ROOT, "assets", "videos", "jay_whiteboard_o_evolution.mp4")
    
    print(f"Rendering evolution video to: {output_path}...")
    final_video.write_videofile(
        output_path, fps=30, codec="libx264", audio_codec="aac",
        threads=os.cpu_count() or 4, logger="bar"
    )
    print("Video rendered successfully!")

    print("\n=== Registering in Local SQLite content.db ===")
    sqlite_path = os.path.join(ROOT, "channel", "content.db")
    if os.path.exists(sqlite_path):
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        
        project = "jay_o_evolution"
        scene_no = 1
        scene_name = "Jay_Whiteboard_O_Evolution_Video"
        base_image = "assets/characters/jay_writing_board_side_opaque.png"
        
        c_desc = (
            "Hangeul Consonants ㅇ, ㅎ drawn on chalkboard, flying out to become words 왕, 해, "
            "which remain next to their corresponding doodles."
        )
        file_path = "assets/videos/jay_whiteboard_o_evolution.mp4"
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
