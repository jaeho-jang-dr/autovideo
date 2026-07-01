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

# Force UTF-8 console output
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
    print("=== Start School Classroom Whiteboard Veo Video Compilation ===")
    
    sfx_chalk_path = os.path.join(ROOT, "scratch", "sfx_chalk_writing.wav")
    sfx_whoosh_path = os.path.join(ROOT, "assets", "audio", "whoosh.wav")
    bgm_path = os.path.join(ROOT, "assets", "audio", "lofi_bgm.mp3")
    logo_path = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
    output_path = os.path.join(ROOT, "assets", "videos", "jay_Rhc_whiteboard.mp4")
    
    words_data = [
        {"word": "강", "narr": "첫 번째 단어는 강입니다. 산을 지나 바다로 흘러가는 강물입니다."},
        {"word": "물", "narr": "두 번째 단어는 물입니다. 생명을 자라나게 하는 소중한 물입니다."},
        {"word": "꽃", "narr": "세 번째 단어는 꽃입니다. 들판에 아름답게 피어난 한 송이 꽃입니다."},
        {"word": "불", "narr": "네 번째 단어는 불입니다. 주위를 따뜻하고 밝게 비춰주는 불입니다."},
        {"word": "차", "narr": "마지막 단어는 차입니다. 도로 위를 씽씽 달리는 멋진 자동차입니다."}
    ]
    
    segments = []
    
    for idx, item in enumerate(words_data):
        scene_no = idx + 1
        word = item["word"]
        narr_text = item["narr"]
        
        # 1. Load generated Veo clip
        clip_path = os.path.join(ROOT, "jay_Rhc_whiteboard", f"scene_{scene_no}.mp4")
        if not os.path.exists(clip_path):
            print(f"[ERR] Veo clip not found at: {clip_path}")
            return 1
            
        print(f"Processing segment {scene_no}/5: '{word}' using {clip_path}...")
        video_clip = VideoFileClip(clip_path)
        clip_dur = video_clip.duration # Usually ~8.0s
        
        # 2. TTS Voice synthesis
        temp_dir = os.path.join(ROOT, "scratch", "temp_audio")
        os.makedirs(temp_dir, exist_ok=True)
        tts_path = os.path.join(temp_dir, f"narr_veo_{idx}.mp3")
        if os.path.exists(tts_path):
            try:
                os.remove(tts_path)
            except Exception:
                pass
        gTTS(text=narr_text, lang="ko").save(tts_path)
        
        # Apply 1.1x speed conversion to TTS
        narr_clip = AudioFileClip(tts_path).with_effects([fx.MultiplySpeed(1.1)])
        narr_dur = narr_clip.duration
        
        # 3. Compile Subtitles
        # Start subtitle at 1.0s, last for narration duration
        sub_clip = make_subtitle_clip(narr_text, narr_dur, 1.0)
        
        # Combine video layers for this scene segment
        segment_video = CompositeVideoClip([video_clip, sub_clip], size=(1280, 720))
        
        # 4. Audio Mixing
        # Chalk SFX starts at 0.5s during the writing animation phase (lasts 3.0s)
        chalk_audio = None
        if os.path.exists(sfx_chalk_path):
            chalk_clip = AudioFileClip(sfx_chalk_path)
            chalk_audio = chalk_clip.with_duration(min(3.0, chalk_clip.duration)).with_effects([MultiplyVolume(0.15)]).with_start(0.5)
            
        # Whoosh SFX at the end of the scene before transitioning (starts around 6.5s)
        whoosh_audio = None
        if os.path.exists(sfx_whoosh_path):
            whoosh_clip = AudioFileClip(sfx_whoosh_path)
            whoosh_audio = whoosh_clip.with_duration(min(1.0, whoosh_clip.duration)).with_effects([MultiplyVolume(0.10)]).with_start(max(0.0, clip_dur - 1.2))
            
        # Synthesized narration audio starts at 1.0s
        narr_audio = narr_clip.with_start(1.0)
        
        audio_components = [narr_audio]
        if chalk_audio:
            audio_components.append(chalk_audio)
        if whoosh_audio:
            audio_components.append(whoosh_audio)
            
        segment_audio = CompositeAudioClip(audio_components)
        segment_video = segment_video.with_audio(segment_audio)
        
        segments.append(segment_video)
        
    # Concatenate all 5 segments (total ~40 seconds)
    print("Concatenating segments...")
    final_video = concatenate_videoclips(segments)
    total_duration = final_video.duration
    
    # 5. Logo Badge Overlay (45x45px bottom right corner)
    logo_clip = None
    if os.path.exists(logo_path):
        logo_clip = (ImageClip(logo_path)
                     .resized((45, 45))
                     .with_duration(total_duration)
                     .with_position((1280 - 45 - 20, 720 - 45 - 20)))
    if logo_clip:
        final_video = CompositeVideoClip([final_video, logo_clip], size=(1280, 720))
        
    # 6. Ambient Lo-Fi BGM (Volume 0.05)
    if os.path.exists(bgm_path):
        from moviepy.audio.fx import AudioLoop
        bgm_audio = AudioFileClip(bgm_path).with_effects([AudioLoop(duration=total_duration), MultiplyVolume(0.05)])
        if final_video.audio:
            final_audio = CompositeAudioClip([final_video.audio, bgm_audio])
        else:
            final_audio = bgm_audio
        final_video = final_video.with_audio(final_audio)
        
    # 7. Render final video in 4K resolution (3840x2160) for YouTube VP09 codec benefit
    threads = os.cpu_count() or 4
    print(f"Upscaling and rendering final 4K video to: {output_path} (threads={threads})...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # moviepy resized resolution parameter
    final_video_4k = final_video.resized((3840, 2160))
    
    final_video_4k.write_videofile(
        output_path, fps=30, codec="libx264", audio_codec="aac",
        threads=threads, logger="bar"
    )
    print("Compilation and 4K rendering completed successfully!")
    
    # 8. Database Registration
    print("\n=== Registering in Local SQLite content.db ===")
    sqlite_path = os.path.join(ROOT, "channel", "content.db")
    if os.path.exists(sqlite_path):
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        
        project = "jay_Rhc_whiteboard"
        scene_no = 1
        scene_name = "Jay_School_Whiteboard_Classroom_Veo_Video"
        base_image = "assets/characters/jay_whiteboard_base_word_1.png"
        c_desc = (
            "Whiteboard classroom video utilizing Google Flow (Veo) clips where JAY "
            "naturally writes words ('강', '물', '꽃', '불', '차') and explains them."
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
        print("Database sync completed successfully!")
    else:
        print("[ERR] content.db not found.")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
