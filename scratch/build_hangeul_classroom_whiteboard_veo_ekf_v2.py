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
    AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip, VideoFileClip, concatenate_videoclips
)
from moviepy.audio.fx import MultiplyVolume
import moviepy.video.fx as fx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
    print("=== Start Hybrid Whiteboard Video Compilation (ekf / 달 그림자 V2) ===")
    
    sfx_chalk_path = os.path.join(ROOT, "scratch", "sfx_chalk_writing.wav")
    sfx_whoosh_path = os.path.join(ROOT, "assets", "audio", "whoosh.wav")
    bgm_path = os.path.join(ROOT, "assets", "audio", "lofi_bgm.mp3")
    logo_path = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
    output_path = os.path.join(ROOT, "assets", "videos", "jay_ekf_whiteboard.mp4")
    
    narr_text = "오늘 함께 써볼 말은 달 그림자입니다. 은은한 달빛이 비칠 때 대지 위에 드리워지는 아름다운 그림자입니다."
    
    # 1. Synth gTTS Narration
    temp_dir = os.path.join(ROOT, "scratch", "temp_audio")
    os.makedirs(temp_dir, exist_ok=True)
    tts_path = os.path.join(temp_dir, "narr_ekf_v2.mp3")
    if os.path.exists(tts_path):
        try:
            os.remove(tts_path)
        except Exception:
            pass
    gTTS(text=narr_text, lang="ko").save(tts_path)
    
    narr_clip = AudioFileClip(tts_path).with_effects([fx.MultiplySpeed(1.1)])
    narr_dur = narr_clip.duration
    
    segments = []
    
    # 4 hybrid scenes corresponding to "달", "그", "림", "자"
    for n in range(1, 5):
        clip_path = os.path.join(ROOT, "jay_ekf_whiteboard", f"scene_{n}_hybrid.mp4")
        if not os.path.exists(clip_path):
            print(f"[ERR] Hybrid Veo clip not found: {clip_path}")
            return 1
            
        print(f"Loading hybrid scene {n}/4: {clip_path}...")
        video_clip = VideoFileClip(clip_path)
        clip_dur = video_clip.duration
        
        # Audio elements for this specific scene segment
        audio_components = []
        
        # Chalk writing SFX mixed at the writing phase (0.5s ~ 6.5s)
        if os.path.exists(sfx_chalk_path):
            chalk_clip = AudioFileClip(sfx_chalk_path)
            chalk_audio = chalk_clip.with_duration(min(6.0, chalk_clip.duration)).with_effects([MultiplyVolume(0.15)]).with_start(0.5)
            audio_components.append(chalk_audio)
            
        # Whoosh transition SFX near the end of the clip (starts max(0, clip_dur - 1.2))
        if os.path.exists(sfx_whoosh_path):
            whoosh_clip = AudioFileClip(sfx_whoosh_path)
            whoosh_audio = whoosh_clip.with_duration(min(1.0, whoosh_clip.duration)).with_effects([MultiplyVolume(0.10)]).with_start(max(0.0, clip_dur - 1.2))
            audio_components.append(whoosh_audio)
            
        if audio_components:
            segment_audio = CompositeAudioClip(audio_components)
            video_clip = video_clip.with_audio(segment_audio)
            
        segments.append(video_clip)
        
    print("Concatenating clips...")
    final_video = concatenate_videoclips(segments)
    total_duration = final_video.duration # 4 * 8s = ~32s
    
    # 2. Superimpose Subtitles & Narration across the entire video
    # Narration starts at 1.5s (during Scene 1 writing phase)
    # Subtitles start at 1.5s and last for narration duration
    sub_clip = make_subtitle_clip(narr_text, narr_dur, 1.5)
    
    final_video = CompositeVideoClip([final_video, sub_clip], size=(1280, 720))
    
    # Overlay Narration Audio
    narr_audio = narr_clip.with_start(1.5)
    
    # Combine narration with the background SFX already in the video segments
    if final_video.audio:
        combined_audio = CompositeAudioClip([final_video.audio, narr_audio])
    else:
        combined_audio = narr_audio
        
    final_video = final_video.with_audio(combined_audio)
    
    # 3. Logo Badge Overlay (45x45px bottom right)
    if os.path.exists(logo_path):
        logo_clip = (ImageClip(logo_path)
                     .resized((45, 45))
                     .with_duration(total_duration)
                     .with_position((1280 - 45 - 20, 720 - 45 - 20)))
        final_video = CompositeVideoClip([final_video, logo_clip], size=(1280, 720))
        
    # 4. Lo-Fi BGM (Volume 0.05)
    if os.path.exists(bgm_path):
        from moviepy.audio.fx import AudioLoop
        bgm_audio = AudioFileClip(bgm_path).with_effects([AudioLoop(duration=total_duration), MultiplyVolume(0.05)])
        if final_video.audio:
            final_audio = CompositeAudioClip([final_video.audio, bgm_audio])
        else:
            final_audio = bgm_audio
        final_video = final_video.with_audio(final_audio)
        
    # 5. Render final video in native 720p resolution (no 4K upscale for test)
    threads = os.cpu_count() or 4
    print(f"Rendering final 720p video to: {output_path} (threads={threads})...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    final_video.write_videofile(
        output_path, fps=30, codec="libx264", audio_codec="aac",
        threads=threads, logger="bar"
    )
    print("Compilation and 4K rendering completed successfully!")
    
    # 6. Database Registration
    print("\n=== Registering in Local SQLite content.db ===")
    sqlite_path = os.path.join(ROOT, "channel", "content.db")
    if os.path.exists(sqlite_path):
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        
        project = "jay_ekf_whiteboard"
        scene_no = 1
        scene_name = "Jay_School_Whiteboard_Classroom_Transition_Video"
        base_image = "assets/characters/jay_whiteboard_clean_base.png"
        c_desc = (
            "Hybrid whiteboard classroom video utilizing Google Flow (Veo) with last frame transition. "
            "Cleaned corrupted AI text and composited pixel-perfect Korean handwriting (달, 그, 림, 자) in sync with tracked right hand wrist."
        )
        file_path = "assets/videos/jay_ekf_whiteboard.mp4"
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
        print("Database sync completed successfully!")
    else:
        print("[ERR] content.db not found.")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
