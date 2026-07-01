# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import cv2
import sqlite3
import math
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import (
    AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip, concatenate_videoclips, VideoClip
)
from moviepy.audio.fx import MultiplyVolume
import moviepy.video.fx as fx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

# Force UTF-8 console output
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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

def blend_rgba_on_bgr(bgr_frame, rgba_img, pos_x, pos_y, col_start=0, col_end=None):
    """
    Blends rgba_img onto bgr_frame at (pos_x, pos_y) considering alpha channel.
    Only blends columns from col_start to col_end.
    """
    h, w, c = rgba_img.shape
    if col_end is None:
        col_end = w
        
    col_start = max(0, min(w, col_start))
    col_end = max(0, min(w, col_end))
    if col_start >= col_end:
        return
        
    # Crop the image to the specified column range
    cropped_rgba = rgba_img[:, col_start:col_end]
    ch, cw, _ = cropped_rgba.shape
    
    # Calculate target region coordinates on bgr_frame
    t_start_x = pos_x + col_start
    t_end_x = pos_x + col_end
    t_start_y = pos_y
    t_end_y = pos_y + ch
    
    # Handle bounds check
    if t_start_x < 0 or t_start_y < 0 or t_end_x > bgr_frame.shape[1] or t_end_y > bgr_frame.shape[0]:
        f_y1 = max(0, t_start_y)
        f_y2 = min(bgr_frame.shape[0], t_end_y)
        f_x1 = max(0, t_start_x)
        f_x2 = min(bgr_frame.shape[1], t_end_x)
        
        img_y1 = f_y1 - t_start_y
        img_y2 = f_y2 - t_start_y
        img_x1 = f_x1 - t_start_x
        img_x2 = f_x2 - t_start_x
        
        if (f_y2 - f_y1) <= 0 or (f_x2 - f_x1) <= 0:
            return
            
        roi = bgr_frame[f_y1:f_y2, f_x1:f_x2]
        img_crop = cropped_rgba[img_y1:img_y2, img_x1:img_x2]
    else:
        roi = bgr_frame[t_start_y:t_end_y, t_start_x:t_end_x]
        img_crop = cropped_rgba
        
    alpha = img_crop[:, :, 3] / 255.0
    alpha = np.expand_dims(alpha, axis=2) # Shape (h, w, 1)
    rgb = img_crop[:, :, :3]
    
    blended = (rgb * alpha + roi * (1.0 - alpha)).astype(np.uint8)
    
    if t_start_x < 0 or t_start_y < 0 or t_end_x > bgr_frame.shape[1] or t_end_y > bgr_frame.shape[0]:
        bgr_frame[f_y1:f_y2, f_x1:f_x2] = blended
    else:
        bgr_frame[t_start_y:t_end_y, t_start_x:t_end_x] = blended

def draw_active_arm(canvas, mx, my, is_erasing=False, stroke_w=4):
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
    
    if is_erasing:
        # Eraser rectangle: 40x25 with grey fill and dark border
        ex1, ey1 = mx - 20, my - 12
        ex2, ey2 = mx + 20, my + 12
        cv2.rectangle(canvas, (ex1, ey1), (ex2, ey2), (180, 180, 180), -1, cv2.LINE_AA)
        cv2.rectangle(canvas, (ex1, ey1), (ex2, ey2), (60, 60, 60), 2, cv2.LINE_AA)
    else:
        # Chalk line
        cv2.line(canvas, r_hand, (r_hand[0] - 15, r_hand[1] - 10), (245, 245, 245), 6, cv2.LINE_AA)

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
    print("=== Start School Classroom Whiteboard Video Generation ===")
    
    # Paths & Assets
    base_img_path = os.path.join(ROOT, "assets", "characters", "jay_writing_board_side_opaque.png")
    sfx_chalk_path = os.path.join(ROOT, "scratch", "sfx_chalk_writing.wav")
    sfx_whoosh_path = os.path.join(ROOT, "assets", "audio", "whoosh.wav")
    bgm_path = os.path.join(ROOT, "assets", "audio", "lofi_bgm.mp3")
    logo_path = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
    output_path = os.path.join(ROOT, "assets", "videos", "jay_Rhc_whiteboard.mp4")
    
    # 1. Base Image Prep & Patches
    base_img = cv2.imread(base_img_path)
    base_img_resized = cv2.resize(base_img, (1280, 720))
    # Erase the white circle
    patch = base_img_resized[170:250, 200:280].copy()
    base_img_resized[170:250, 420:500] = patch
    # 280px Split Patch to preserve round chin/head
    patch_hand = base_img_resized[200:270, 200:380].copy()
    patch_arm = base_img_resized[270:460, 200:455].copy()
    base_img_resized[200:270, 380:560] = patch_hand
    base_img_resized[270:460, 380:635] = patch_arm
    wood_bg = base_img_resized

    words_data = [
        {"word": "집", "narr": "첫 번째 단어는 집입니다. 우리가 편히 쉬는 보금자리입니다."},
        {"word": "학교", "narr": "두 번째 단어는 학교입니다. 친구들과 함께 공부하며 배우는 곳입니다."},
        {"word": "교실", "narr": "세 번째 단어는 교실입니다. 학교 안에서 수업을 들으며 꿈을 키우는 공간입니다."},
        {"word": "창문", "narr": "네 번째 단어는 창문입니다. 교실 밖 아름다운 풍경을 내다보는 창입니다."},
        {"word": "도시", "narr": "다섯 번째 단어는 도시입니다. 수많은 사람들이 모여 바쁘게 살아가는 곳입니다."},
        {"word": "꽃", "narr": "마지막 단어는 꽃입니다. 칠판 위에 아름답게 피어난 지식의 꽃입니다."}
    ]

    segments = []
    
    for idx, item in enumerate(words_data):
        word = item["word"]
        narr_text = item["narr"]
        print(f"Processing segment {idx+1}/6: '{word}'...")

        # A. Word lineart PNG generation
        txt_path = os.path.join(ROOT, "scratch", "temp_audio", f"txt_{idx}.png")
        generate_text_lineart(word, txt_path, font_size=180, stroke_width=6)
        text_img = cv2.imread(txt_path, cv2.IMREAD_UNCHANGED)
        th, tw, _ = text_img.shape
        
        # Centering the text on the board
        pos_x = 320 - tw // 2
        pos_y = 280 - th // 2

        # B. TTS Voice synthesis
        tts_path = os.path.join(ROOT, "scratch", "temp_audio", f"narr_{idx}.mp3")
        if os.path.exists(tts_path):
            try:
                os.remove(tts_path)
            except Exception:
                pass
        gTTS(text=narr_text, lang="ko").save(tts_path)
        
        # Load and apply 1.1x speed
        narr_clip = AudioFileClip(tts_path).with_effects([fx.MultiplySpeed(1.1)])
        narr_dur = narr_clip.duration
        
        # Time intervals
        pre_write_dur = 0.5
        write_dur = 2.0
        explain_dur = narr_dur
        erase_dur = 1.0
        post_erase_dur = 0.5
        segment_total_dur = pre_write_dur + write_dur + explain_dur + erase_dur + post_erase_dur

        # C. Custom frame-by-frame draw logic
        def make_segment_frame(t):
            frame = wood_bg.copy()
            
            if t < pre_write_dur:
                # Phase 1: Pre-write pause (0.5s)
                mx = pos_x
                my = pos_y + th // 2
                is_erasing = False
                # Text: none
            elif t < pre_write_dur + write_dur:
                # Phase 2: Writing (2.0s)
                t_rel = t - pre_write_dur
                p = t_rel / write_dur
                mx = pos_x + int(tw * p)
                my = pos_y + th // 2 + int(10 * math.sin(2.0 * math.pi * 5.0 * t_rel))
                is_erasing = False
                # Text: partial reveal
                blend_rgba_on_bgr(frame, text_img, pos_x, pos_y, col_start=0, col_end=int(tw * p))
            elif t < pre_write_dur + write_dur + explain_dur:
                # Phase 3: Explanation (narr_dur)
                t_rel = t - (pre_write_dur + write_dur)
                mx = pos_x + tw + 15
                my = pos_y + th // 2 + int(6 * math.sin(2.0 * math.pi * t_rel / 1.0))
                is_erasing = False
                # Text: fully visible
                blend_rgba_on_bgr(frame, text_img, pos_x, pos_y, col_start=0, col_end=tw)
            elif t < pre_write_dur + write_dur + explain_dur + erase_dur:
                # Phase 4: Erasing (1.0s)
                t_rel = t - (pre_write_dur + write_dur + explain_dur)
                p = t_rel / erase_dur
                mx = pos_x + int(tw * p)
                my = pos_y + th // 2 + int(20 * math.sin(2.0 * math.pi * 3.0 * t_rel))
                is_erasing = True
                # Text: partial erase from left to right
                blend_rgba_on_bgr(frame, text_img, pos_x, pos_y, col_start=int(tw * p), col_end=tw)
            else:
                # Phase 5: Post-erase pause (0.5s)
                mx = pos_x
                my = pos_y + th // 2
                is_erasing = False
                # Text: none
                
            draw_active_arm(frame, mx, my, is_erasing=is_erasing)
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        bg_clip = VideoClip(make_segment_frame).with_duration(segment_total_dur)
        
        # Subtitle starts at writing start (0.5s) and lasts until erasing start (3.5 + narr_dur)
        sub_clip = make_subtitle_clip(narr_text, write_dur + explain_dur, pre_write_dur)
        
        # Combine video layers for this segment
        segment_video = CompositeVideoClip([bg_clip, sub_clip], size=(1280, 720))
        
        # Audio mixing
        chalk_clip = AudioFileClip(sfx_chalk_path)
        chalk_audio = chalk_clip.with_duration(min(write_dur, chalk_clip.duration)).with_effects([MultiplyVolume(0.15)]).with_start(pre_write_dur)
        
        whoosh_clip = AudioFileClip(sfx_whoosh_path)
        whoosh_audio = whoosh_clip.with_duration(min(erase_dur, whoosh_clip.duration)).with_effects([MultiplyVolume(0.10)]).with_start(pre_write_dur + write_dur + explain_dur)
        
        narr_audio = narr_clip.with_start(pre_write_dur + write_dur)
        
        segment_audio = CompositeAudioClip([chalk_audio, whoosh_audio, narr_audio])
        segment_video = segment_video.with_audio(segment_audio)
        
        segments.append(segment_video)

    # 2. Concatenate segments
    print("Concatenating segments...")
    final_video = concatenate_videoclips(segments)
    total_duration = final_video.duration
    
    # 3. Add Logo Overlay
    logo_clip = None
    if os.path.exists(logo_path):
        logo_clip = (ImageClip(logo_path)
                     .resized((45, 45))
                     .with_duration(total_duration)
                     .with_position((1280 - 45 - 20, 720 - 45 - 20)))
        
    if logo_clip:
        final_video = CompositeVideoClip([final_video, logo_clip], size=(1280, 720))
        
    # 4. Add Ambient Lo-Fi BGM (Volume 0.05)
    if os.path.exists(bgm_path):
        from moviepy.audio.fx import AudioLoop
        bgm_audio = AudioFileClip(bgm_path).with_effects([AudioLoop(duration=total_duration), MultiplyVolume(0.05)])
        # Mix the BGM audio with existing audio
        if final_video.audio:
            final_audio = CompositeAudioClip([final_video.audio, bgm_audio])
        else:
            final_audio = bgm_audio
        final_video = final_video.with_audio(final_audio)

    # 5. Render Final Video
    threads = os.cpu_count() or 4
    print(f"Rendering to final path: {output_path} (threads={threads})...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    final_video.write_videofile(
        output_path, fps=30, codec="libx264", audio_codec="aac",
        threads=threads, logger="bar"
    )
    print("Compilation completed successfully!")

    # 6. Database Registration
    print("\n=== Registering in Local SQLite content.db ===")
    sqlite_path = os.path.join(ROOT, "channel", "content.db")
    if os.path.exists(sqlite_path):
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        
        project = "jay_Rhc_whiteboard"
        scene_no = 1
        scene_name = "Jay_School_Whiteboard_Classroom_Video"
        base_image = "assets/characters/jay_writing_board_side_opaque.png"
        
        c_desc = (
            "Whiteboard school classroom video where teacher JAY writes words "
            "('집', '학교', '교실', '창문', '도시', '꽃') on the board, explains them, "
            "and erases them sequentially."
        )
        file_path = "assets/videos/jay_Rhc_whiteboard.mp4"
        duration_sec = total_duration
        
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
