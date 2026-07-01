# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import sqlite3
from moviepy import (
    AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip, concatenate_videoclips
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
sys.stdout.reconfigure(encoding='utf-8')

# Import helper functions if available, or define them locally
def get_letter_path(letter):
    p = os.path.join(ROOT, "assets", "graphics", "letters", f"letter_{letter}.png")
    if os.path.exists(p):
        return p
    # Fallback to web/public
    p_web = os.path.join(ROOT, "web", "public", "images", "letters", f"letter_{letter}.png")
    if os.path.exists(p_web):
        return p_web
    return None

def create_flying_letter(letter_path, start_time, duration, start_pos=(700, 350), direction=1):
    clip_dur = duration - start_time
    if clip_dur <= 0 or not letter_path:
        return None
        
    img = ImageClip(letter_path).with_duration(clip_dur).with_start(start_time)
    img = img.resized(width=80)
    img_w, img_h = img.size
    
    def pos_fn(t):
        p = min(1.0, t / min(2.5, clip_dur))
        # Spiral trajectory floating away
        radius = 50 + 400 * p
        angle = 1.0 + direction * 6.0 * p
        cur_x = start_pos[0] + radius * np.cos(angle) - img_w / 2
        cur_y = start_pos[1] + radius * np.sin(angle) - 150 * p - img_h / 2
        
        cur_x = max(-img_w, min(1280, cur_x))
        cur_y = max(-img_h, min(720, cur_y))
        return (int(cur_x), int(cur_y))
        
    def rot_fn(t):
        return direction * 360 * (t / min(2.5, clip_dur))
        
    return img.with_position(pos_fn).rotated(rot_fn)

def build_videos():
    print("Building Hangeul Consonants and Vowels Flying Videos...")
    
    bg_img_path = os.path.join(ROOT, "assets", "characters", "jay_whiteboard_writing_side_opaque.png")
    if not os.path.exists(bg_img_path):
        print(f"[ERR] Background image not found: {bg_img_path}")
        return 1
        
    pop_sound_path = os.path.join(ROOT, "assets", "audio", "pop.wav")
    whoosh_sound_path = os.path.join(ROOT, "assets", "audio", "whoosh.wav")
    chime_sound_path = os.path.join(ROOT, "assets", "audio", "bell_chime.wav")
    
    has_audio = os.path.exists(pop_sound_path)
    if has_audio:
        pop_audio = AudioFileClip(pop_sound_path)
        whoosh_audio = AudioFileClip(whoosh_sound_path)
        chime_audio = AudioFileClip(chime_sound_path)
    else:
        print("[WARN] Audio assets not found, videos will be silent.")

    # ==========================================
    # 1. CONSONANTS FLYING VIDEO (ㄱ, ㄴ, ㅁ, ㅅ, ㅇ)
    # ==========================================
    consonants_dur = 16.0
    bg_1 = ImageClip(bg_img_path).with_duration(consonants_dur).resized((1280, 720))
    
    # Timeline details:
    # 0.5s: ㄱ drawn -> 1.0s: ㄱ flies out, ㄲ, ㅋ appear and fly
    # 3.5s: ㄴ drawn -> 4.0s: ㄴ flies out, ㄷ, ㅌ, ㄸ, ㄹ fly
    # 6.5s: ㅁ drawn -> 7.0s: ㅁ flies out, ㅂ, ㅍ, ㅃ fly
    # 9.5s: ㅅ drawn -> 10.0s: ㅅ flies out, ㅈ, ㅊ, ㅉ, ㅆ fly
    # 12.5s: ㅇ drawn -> 13.0s: ㅇ flies out, ㅎ fly
    
    timeline_1 = [
        # (Base letter, Start drawing time, Fly out time, [Derived letters])
        ("ㄱ", 0.5, 1.0, ["ㅋ", "ㄲ"]),
        ("ㄴ", 3.5, 4.0, ["ㄷ", "ㅌ", "ㄸ", "ㄹ"]),
        ("ㅁ", 6.5, 7.0, ["ㅂ", "ㅍ", "ㅃ"]),
        ("ㅅ", 9.5, 10.0, ["ㅈ", "ㅊ", "ㅉ", "ㅆ"]),
        ("ㅇ", 12.5, 13.0, ["ㅎ"])
    ]
    
    clips_1 = [bg_1]
    audio_clips_1 = []
    
    for base, draw_t, fly_t, derived in timeline_1:
        # Base letter stays on board from draw_t to fly_t
        base_path = get_letter_path(base)
        if base_path:
            board_clip = (ImageClip(base_path)
                          .with_start(draw_t)
                          .with_duration(fly_t - draw_t)
                          .resized(width=90)
                          .with_position((700 - 45, 350 - 45)))
            clips_1.append(board_clip)
            
            # Base letter flies away from fly_t onwards
            base_fly = create_flying_letter(base_path, fly_t, consonants_dur, direction=1)
            if base_fly:
                clips_1.append(base_fly)
                
            if has_audio:
                audio_clips_1.append(pop_audio.with_start(draw_t))
                audio_clips_1.append(whoosh_audio.with_start(fly_t))
                
        # Derived letters fly out from fly_t onwards in different directions
        for idx, der in enumerate(derived):
            der_path = get_letter_path(der)
            direction = -1 if idx % 2 == 0 else 1
            der_fly = create_flying_letter(der_path, fly_t + 0.2 * idx, consonants_dur, direction=direction)
            if der_fly:
                clips_1.append(der_fly)
            if has_audio:
                audio_clips_1.append(pop_audio.with_start(fly_t + 0.2 * idx))
                
    consonants_video = CompositeVideoClip(clips_1, size=(1280, 720))
    if has_audio:
        consonants_video = consonants_video.with_audio(CompositeAudioClip(audio_clips_1))
        
    consonants_out = os.path.join(ROOT, "assets", "videos", "jay_whiteboard_consonants_flying.mp4")
    print(f"Rendering consonants video to {consonants_out}...")
    consonants_video.write_videofile(
        consonants_out, fps=30, codec="libx264", audio_codec="aac",
        threads=os.cpu_count() or 4, logger="bar"
    )

    # ==========================================
    # 2. VOWELS FLYING VIDEO (ㆍ, ㅡ, ㅣ)
    # ==========================================
    vowels_dur = 12.0
    bg_2 = ImageClip(bg_img_path).with_duration(vowels_dur).resized((1280, 720))
    
    # 0.5s: 아래아 (ㆍ) drawn (using period . symbol representation in DB or graphics) -> 1.0s: flies
    # 3.0s: ㅡ drawn -> 3.5s: flies
    # 5.5s: ㅣ drawn -> 6.0s: flies
    # 8.0s: Derived vowels fly out: ㅏ, ㅑ, ㅓ, ㅕ, ㅗ, ㅛ, ㅜ, ㅠ, ㅐ, ㅔ, ㅒ, ㅖ
    
    timeline_2 = [
        # (Base letter, Start drawing time, Fly out time)
        ("아래아", 0.5, 1.0),
        ("ㅡ", 3.0, 3.5),
        ("ㅣ", 5.5, 6.0)
    ]
    
    clips_2 = [bg_2]
    audio_clips_2 = []
    
    for base, draw_t, fly_t in timeline_2:
        # DB has word_아래아 or letter_아래아, let's fall back to period '.' letter graphic if missing
        letter_name = "아래아" if base == "아래아" else base
        base_path = get_letter_path(letter_name)
        if not base_path and base == "아래아":
            base_path = get_letter_path(".") # fallback to period
            
        if base_path:
            board_clip = (ImageClip(base_path)
                          .with_start(draw_t)
                          .with_duration(fly_t - draw_t)
                          .resized(width=90)
                          .with_position((700 - 45, 350 - 45)))
            clips_2.append(board_clip)
            
            base_fly = create_flying_letter(base_path, fly_t, vowels_dur, direction=-1)
            if base_fly:
                clips_2.append(base_fly)
                
            if has_audio:
                audio_clips_2.append(pop_audio.with_start(draw_t))
                audio_clips_2.append(whoosh_audio.with_start(fly_t))

    # Derived vowels fly out at 8.0s
    derived_vowels = ["ㅏ", "ㅑ", "ㅓ", "ㅕ", "ㅗ", "ㅛ", "ㅜ", "ㅠ", "ㅐ", "ㅔ", "ㅒ", "ㅖ"]
    for idx, v in enumerate(derived_vowels):
        v_path = get_letter_path(v)
        direction = 1 if idx % 2 == 0 else -1
        v_fly = create_flying_letter(v_path, 8.0 + 0.15 * idx, vowels_dur, direction=direction)
        if v_fly:
            clips_2.append(v_fly)
        if has_audio:
            audio_clips_2.append(pop_audio.with_start(8.0 + 0.15 * idx))
            
    vowels_video = CompositeVideoClip(clips_2, size=(1280, 720))
    if has_audio:
        vowels_video = vowels_video.with_audio(CompositeAudioClip(audio_clips_2))
        
    vowels_out = os.path.join(ROOT, "assets", "videos", "jay_whiteboard_vowels_flying.mp4")
    print(f"Rendering vowels video to {vowels_out}...")
    vowels_video.write_videofile(
        vowels_out, fps=30, codec="libx264", audio_codec="aac",
        threads=os.cpu_count() or 4, logger="bar"
    )

    # ==========================================
    # 3. DATABASE REGISTRATION
    # ==========================================
    print("\n=== Registering in Local SQLite content.db ===")
    sqlite_path = os.path.join(ROOT, "channel", "content.db")
    if os.path.exists(sqlite_path):
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        
        # 1. Consonants flying video registration
        cur.execute("SELECT id FROM video_clips WHERE project=? AND scene_no=?", ("jay_consonants_flying", 1))
        row = cur.fetchone()
        
        c_desc = "Consonants ㄱ, ㄴ, ㅁ, ㅅ, ㅇ and their derived letters flying in classroom whiteboard."
        if row:
            cur.execute("""
                UPDATE video_clips
                SET scene_name='Jay_Whiteboard_Consonants_Flying_Video', base_image=?, file_path=?, duration_sec=?, status='success', notes=?
                WHERE id=?
            """, ("assets/characters/jay_whiteboard_writing_side_opaque.png", "assets/videos/jay_whiteboard_consonants_flying.mp4", consonants_dur, c_desc, row[0]))
        else:
            cur.execute("""
                INSERT INTO video_clips (project, scene_no, scene_name, base_image, file_path, duration_sec, status, notes)
                VALUES (?, 1, ?, ?, ?, ?, 'success', ?)
            """, ("jay_consonants_flying", "Jay_Whiteboard_Consonants_Flying_Video", "assets/characters/jay_whiteboard_writing_side_opaque.png", "assets/videos/jay_whiteboard_consonants_flying.mp4", consonants_dur, c_desc))
            
        # 2. Vowels flying video registration
        cur.execute("SELECT id FROM video_clips WHERE project=? AND scene_no=?", ("jay_vowels_flying", 1))
        row = cur.fetchone()
        
        v_desc = "Vowels 아래아, ㅡ, ㅣ and their derived vowels flying in classroom whiteboard."
        if row:
            cur.execute("""
                UPDATE video_clips
                SET scene_name='Jay_Whiteboard_Vowels_Flying_Video', base_image=?, file_path=?, duration_sec=?, status='success', notes=?
                WHERE id=?
            """, ("assets/characters/jay_whiteboard_writing_side_opaque.png", "assets/videos/jay_whiteboard_vowels_flying.mp4", vowels_dur, v_desc, row[0]))
        else:
            cur.execute("""
                INSERT INTO video_clips (project, scene_no, scene_name, base_image, file_path, duration_sec, status, notes)
                VALUES (?, 1, ?, ?, ?, ?, 'success', ?)
            """, ("jay_vowels_flying", "Jay_Whiteboard_Vowels_Flying_Video", "assets/characters/jay_whiteboard_writing_side_opaque.png", "assets/videos/jay_whiteboard_vowels_flying.mp4", vowels_dur, v_desc))
            
        conn.commit()
        cur.close()
        conn.close()
        print("SQLite video clips successfully mapped and saved!")
    else:
        print("[ERR] content.db not found for video clip registration.")

    print("All tasks completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(build_videos())
