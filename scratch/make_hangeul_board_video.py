# -*- coding: utf-8 -*-
"""
make_hangeul_board_video.py — Whiteboard-style video generator for 40 Hangeul letters.
====================================================================================
This script compiles a complete video containing:
- 1 Intro Scene: Stickman welcomes users and introduces Hangeul (consonants + vowels).
- 19 Consonant Scenes: Teacher introduces each consonant and writes it with chalk on a blackboard.
- 21 Vowel Scenes: Teacher introduces each vowel and writes it with chalk on a blackboard.
- 1 Outro Scene: Wrap up, encouragement, and call to subscribe.

It uses:
- gTTS for voice narrations (ko-KR, speed matched @1.1x).
- MoviePy v2.x for advanced compositing, animations, and transitions.
- Pillow/NumPy for custom wipe-reveal masks and chalk particle dynamics.
- Mixed audio: Narration + Chalk ASMR writing SFX + Transition Pop SFX + Ambient Lofi BGM.
"""

import os
import re
import sys
import math
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import (
    AudioFileClip, ColorClip, ImageClip, CompositeVideoClip, VideoClip,
    concatenate_videoclips, CompositeAudioClip
)
from moviepy.audio.fx import MultiplyVolume
import moviepy.video.fx as fx

# Force UTF-8 encoding for console logs
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ──────────────────────── CONFIGURATION ────────────────────────
OUTPUT_DIR = "scratch/hangeul_board"
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
VIDEO_DIR = os.path.join(OUTPUT_DIR, "video")
FINAL_OUTPUT = "assets/video/hangeul_40_blackboard.mp4"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(os.path.dirname(FINAL_OUTPUT), exist_ok=True)

# Assets Paths
BLACKBOARD_PATH = "assets/graphics/obj_blackboard.png"
CHALK_PATH = "assets/graphics/obj_chalk.png"
PARTICLE_PATH = "assets/graphics/obj_particle.png"
STICKMAN_PATH = "assets/graphics/stickman_standing.png"
WHOOSH_SFX_PATH = "assets/audio/whoosh.wav"
POP_SFX_PATH = "assets/audio/pop.wav"
LOFI_BGM_PATH = "assets/audio/lofi_bgm.mp3"

CONSONANTS = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
VOWELS = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]

# Hangeul Pronunciations
CONSONANT_NAMES = {
    "ㄱ": "기역", "ㄲ": "쌍기역", "ㄴ": "니은", "ㄷ": "디귿", "ㄸ": "쌍디귿",
    "ㄹ": "리을", "ㅁ": "미음", "ㅂ": "비읍", "ㅃ": "쌍비읍", "ㅅ": "시옷",
    "ㅆ": "쌍시옷", "ㅇ": "이응", "ㅈ": "지읒", "ㅉ": "쌍지읒", "ㅊ": "치읓",
    "ㅋ": "키읔", "ㅌ": "티읕", "ㅍ": "피읖", "ㅎ": "히읗"
}

VOWEL_NAMES = {
    "ㅏ": "아", "ㅐ": "애", "ㅑ": "야", "ㅒ": "얘", "ㅓ": "어",
    "ㅔ": "에", "ㅕ": "여", "ㅖ": "예", "ㅗ": "오", "ㅘ": "와",
    "ㅙ": "왜", "ㅚ": "외", "ㅛ": "요", "ㅜ": "우", "ㅝ": "워",
    "ㅞ": "웨", "ㅟ": "위", "ㅠ": "유", "ㅡ": "으", "ㅢ": "의",
    "ㅣ": "이"
}

# ──────────────────────── AUDIO GENERATION ────────────────────────

def generate_chalk_sfx(output_path, duration=3.0, sample_rate=44100):
    """Generates synthetic ASMR chalk writing friction sound using filtered noise."""
    import scipy.io.wavfile as wav
    num_samples = int(duration * sample_rate)
    noise = np.random.normal(0, 0.05, num_samples)
    filtered = np.convolve(noise, np.ones(6)/6, mode='same')
    t = np.linspace(0, duration, num_samples)
    modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 7 * t) * np.sin(2 * np.pi * 60 * t)
    sound = filtered * modulation
    
    # Fade in / out envelopes
    fade = int(0.05 * sample_rate)
    envelope = np.ones(num_samples)
    envelope[:fade] = np.linspace(0, 1, fade)
    envelope[-fade:] = np.linspace(1, 0, fade)
    
    final_sound = np.int16(sound * envelope * 32767)
    wav.write(output_path, sample_rate, final_sound)

def build_all_tts():
    """Builds gTTS audio files for all Hangeul letters, intro, and outro."""
    print("Generating Hangeul TTS voice assets...")
    
    # Intro
    intro_path = os.path.join(AUDIO_DIR, "scene_intro.mp3")
    gTTS("안녕하세요! 오늘은 한국어의 기초인 한글 자모 40자를 함께 알아보겠습니다. 자음 19자와 모음 21자를 칠판에 써볼 테니 잘 듣고 따라해 보세요!", lang="ko").save(intro_path)
    
    # Consonants
    for idx, c in enumerate(CONSONANTS):
        path = os.path.join(AUDIO_DIR, f"scene_c_{idx}.mp3")
        pronunciation = CONSONANT_NAMES[c]
        gTTS(f"{c}. {pronunciation}.", lang="ko").save(path)
        
    # Vowels
    for idx, v in enumerate(VOWELS):
        path = os.path.join(AUDIO_DIR, f"scene_v_{idx}.mp3")
        pronunciation = VOWEL_NAMES[v]
        gTTS(f"{v}. {pronunciation}.", lang="ko").save(path)
        
    # Outro
    outro_path = os.path.join(AUDIO_DIR, "scene_outro.mp3")
    gTTS("수고하셨습니다! 한글 자모 40자를 모두 배워보았습니다. 꾸준히 연습하여 한글 박사가 되어보세요. 구독과 좋아요를 눌러주시면 더 재미있는 지식으로 찾아뵙겠습니다. 감사합니다!", lang="ko").save(outro_path)
    
    print("TTS synthesis successfully completed.")

# ──────────────────────── SCENE BUILDER ────────────────────────

def create_writing_chalk_clip(letter_path, duration, start_pos=(520, 200), size=(1280, 720)):
    """Creates a custom letter wipe-reveal effect and animates the chalk to follow it."""
    letter_clip = ImageClip(letter_path).with_duration(duration)
    # Target size is 280x280 for the letter
    letter_clip = letter_clip.resized(width=280)
    w_w, w_h = letter_clip.size
    
    write_dur = min(2.0, duration - 0.5) # Finish writing in max 2 seconds
    
    # 1. Custom Wipe Reveal Mask using built-in alpha mask transform
    if letter_clip.mask:
        def reveal_mask_effect(get_frame, t):
            mask_frame = get_frame(t) # shape: (w_h, w_w) or (w_h, w_w, 1)
            out = mask_frame.copy()
            if t <= 0.3:
                out[:] = 0.0
                return out
            
            progress = min(1.0, (t - 0.3) / write_dur)
            reveal_h = int(w_h * progress)
            reveal_w = int(w_w * progress)
            
            geom_mask = np.zeros(mask_frame.shape, dtype=np.float32)
            if progress < 0.5:
                geom_mask[:max(1, reveal_h), :] = 1.0
            else:
                geom_mask[:, :max(1, reveal_w)] = 1.0
                geom_mask[:reveal_h, :] = 1.0
                
            out = np.minimum(out, geom_mask)
            return out

        letter_revealed = letter_clip.with_mask(letter_clip.mask.transform(reveal_mask_effect))
    else:
        letter_revealed = letter_clip
        
    letter_revealed = letter_revealed.with_position(start_pos)
    
    # 2. Chalk Animation following the reveal point
    chalk_clip = ImageClip(CHALK_PATH).with_duration(0.3 + write_dur)
    # Scale chalk appropriately
    chalk_clip = chalk_clip.resized(width=60)
    c_w, c_h = chalk_clip.size
    
    def make_chalk_pos(t):
        if t <= 0.3:
            # Rest at start pos
            return (start_pos[0] - 10, start_pos[1] - 40)
            
        progress = min(1.0, (t - 0.3) / write_dur)
        # Simple trace coordinate logic: diagonal writing path
        # with high frequency hand tremor simulation (ASMR effect)
        wobble_x = 12 * np.sin(2 * np.pi * 8 * t)
        wobble_y = 12 * np.cos(2 * np.pi * 8 * t)
        
        # Move chalk tip to trace the letter area
        tx = start_pos[0] + w_w * progress + wobble_x
        ty = start_pos[1] + w_h * (0.5 + 0.3 * np.sin(2 * np.pi * 2 * t)) + wobble_y
        
        # Bounding box limits
        tx = max(start_pos[0], min(start_pos[0] + w_w, tx))
        ty = max(start_pos[1], min(start_pos[1] + w_h, ty))
        
        # Position is top-left of chalk image. 
        # Tip of chalk is at its bottom-left corner (approx c_w*0.1, c_h*0.9)
        return (int(tx - c_w * 0.1), int(ty - c_h * 0.9))
        
    chalk = chalk_clip.with_position(make_chalk_pos)
    return letter_revealed, chalk, write_dur

def build_educational_scene(letter_char, narration_audio_path, letter_img_path, duration):
    """Composites a blackboard lesson scene: Blackboard, Teacher, Writing Chalk, Audio."""
    # 1. Background (Blackboard scaled to 1280x720)
    bg = ImageClip(BLACKBOARD_PATH).with_duration(duration).resized(new_size=(1280, 720))
    
    # 2. Teacher (Stickman standing on the left side)
    teacher = ImageClip(STICKMAN_PATH).with_duration(duration)
    # Teacher stands at x=100, y=200
    teacher = teacher.resized(height=400).with_position((100, 240))
    
    # 3. Writing Letter & Chalk Clip
    letter_clip, chalk_clip, write_duration = create_writing_chalk_clip(letter_img_path, duration)
    
    # 4. Pop-up Text Badge of the letter name (e.g., "기역" / "아") in the top corner
    font_path = "C:\\Windows\\Fonts\\malgunbd.ttf" if os.path.exists("C:\\Windows\\Fonts\\malgunbd.ttf") else "arial.ttf"
    
    # Create the text asset label on the fly
    pron_name = CONSONANT_NAMES.get(letter_char) or VOWEL_NAMES.get(letter_char)
    label_path = os.path.join(OUTPUT_DIR, f"label_{letter_char}.png")
    
    from generate_letters_assets import generate_text_lineart
    # Sprout Green style background text badge
    generate_text_lineart(f"{letter_char} ({pron_name})", label_path, font_size=60, stroke_width=3)
    
    # Badge clip starting 0.5s after writing finishes (elastic fade-in effect)
    badge_start = 0.3 + write_duration + 0.3
    badge = (ImageClip(label_path)
             .with_duration(duration - badge_start)
             .with_start(badge_start)
             .resized(height=70)
             .with_position((880, 80)))
    
    # 5. Composite all visual layers
    scene_video = CompositeVideoClip(
        [bg, teacher, letter_clip, chalk_clip, badge],
        size=(1280, 720)
    )
    
    # 6. Audio Mixing (Narration, Chalk writing ASMR, Pop SFX)
    # Generate temporary chalk writing SFX matching exactly the writing duration
    temp_chalk_sfx = os.path.join(AUDIO_DIR, f"temp_chalk_{letter_char}.wav")
    generate_chalk_sfx(temp_chalk_sfx, duration=write_duration)
    
    audio_narr = AudioFileClip(narration_audio_path).with_effects([fx.MultiplySpeed(1.1)])
    audio_chalk = AudioFileClip(temp_chalk_sfx).with_start(0.3).with_effects([MultiplyVolume(0.15)])
    
    whoosh_audio = AudioFileClip(WHOOSH_SFX_PATH).with_effects([MultiplyVolume(0.08)])
    pop_audio = AudioFileClip(POP_SFX_PATH).with_start(badge_start).with_effects([MultiplyVolume(0.15)])
    
    mixed_audio = CompositeAudioClip([
        whoosh_audio,
        audio_chalk,
        audio_narr.with_start(0.4), # Narration starts slightly after whoosh
        pop_audio
    ])
    
    scene_video = scene_video.with_audio(mixed_audio)
    return scene_video

def build_intro_outro_scene(audio_path, is_intro=True):
    """Composites the intro/outro video scene with teacher and blackboard."""
    audio_narr = AudioFileClip(audio_path).with_effects([fx.MultiplySpeed(1.1)])
    duration = audio_narr.duration + 1.0 # 1s margin
    
    bg = ImageClip(BLACKBOARD_PATH).with_duration(duration).resized(new_size=(1280, 720))
    teacher = ImageClip(STICKMAN_PATH).with_duration(duration).resized(height=400).with_position((180, 240))
    
    # Intro/Outro visual title cards
    title_text = "한글 자모 40자 공부방" if is_intro else "한글 자모 마스터 완료!"
    sub_text = "자음 19자 + 모음 21자" if is_intro else "구독과 좋아요는 큰 힘이 됩니다!"
    
    card_path = os.path.join(OUTPUT_DIR, f"title_card_{'intro' if is_intro else 'outro'}.png")
    
    # Build text badge
    img = Image.new("RGBA", (800, 250), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_path = "C:\\Windows\\Fonts\\malgunbd.ttf" if os.path.exists("C:\\Windows\\Fonts\\malgunbd.ttf") else "arial.ttf"
    
    try:
        title_font = ImageFont.truetype(font_path, 50)
        sub_font = ImageFont.truetype(font_path, 28)
    except IOError:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        
    # Draw rounded rect green plate
    draw.rounded_rectangle((10, 10, 790, 240), radius=15, fill=(224, 245, 224, 220), outline=(46, 125, 50, 255), width=3)
    
    # Measure & center text
    try:
        t_box = draw.textbbox((0, 0), title_text, font=title_font)
        s_box = draw.textbbox((0, 0), sub_text, font=sub_font)
        t_w, t_h = t_box[2] - t_box[0], t_box[3] - t_box[1]
        s_w, s_h = s_box[2] - s_box[0], s_box[3] - s_box[1]
    except AttributeError:
        t_w, t_h = draw.textsize(title_text, font=title_font)
        s_w, s_h = draw.textsize(sub_text, font=sub_font)
        
    draw.text(((800 - t_w)//2, 45), title_text, fill=(17, 17, 17, 255), font=title_font)
    draw.text(((800 - s_w)//2, 135), sub_text, fill=(46, 125, 50, 255), font=sub_font)
    img.save(card_path, "PNG")
    
    card = ImageClip(card_path).with_duration(duration).resized(width=680).with_position((480, 180))
    
    # Elastic bounce fade-in
    card = card.with_effects([fx.CrossFadeIn(0.5)])
    
    scene_video = CompositeVideoClip([bg, teacher, card], size=(1280, 720))
    
    whoosh = AudioFileClip(WHOOSH_SFX_PATH).with_effects([MultiplyVolume(0.10)])
    mixed_audio = CompositeAudioClip([whoosh, audio_narr.with_start(0.4)])
    
    scene_video = scene_video.with_audio(mixed_audio)
    return scene_video

# ──────────────────────── MAIN COMPILER ────────────────────────

def main():
    print("=" * 60)
    print("  Hangeul Blackboard Video Compiler — v1.0")
    print("=" * 60)
    
    # 1. Synthesize Speech audio files
    build_all_tts()
    
    # List of all scene clips
    clips = []
    
    # 2. Compile Intro Scene
    print("\nBuilding Intro Scene...")
    intro_audio = os.path.join(AUDIO_DIR, "scene_intro.mp3")
    clips.append(build_intro_outro_scene(intro_audio, is_intro=True))
    
    # 3. Compile Consonant Scenes (19)
    print("\nBuilding Consonant Scenes...")
    for idx, c in enumerate(CONSONANTS):
        print(f"  [{idx+1}/19] Consonant '{c}'...")
        narr_path = os.path.join(AUDIO_DIR, f"scene_c_{idx}.mp3")
        let_img = f"assets/graphics/letters/letter_{c}.png"
        
        # Audio length determines scene duration
        temp_aud = AudioFileClip(narr_path).with_effects([fx.MultiplySpeed(1.1)])
        scene_dur = temp_aud.duration + 1.2 # extra cushion time
        temp_aud.close()
        
        clips.append(build_educational_scene(c, narr_path, let_img, scene_dur))
        
    # 4. Compile Vowel Scenes (21)
    print("\nBuilding Vowel Scenes...")
    for idx, v in enumerate(VOWELS):
        print(f"  [{idx+1}/21] Vowel '{v}'...")
        narr_path = os.path.join(AUDIO_DIR, f"scene_v_{idx}.mp3")
        let_img = f"assets/graphics/letters/letter_{v}.png"
        
        temp_aud = AudioFileClip(narr_path).with_effects([fx.MultiplySpeed(1.1)])
        scene_dur = temp_aud.duration + 1.2
        temp_aud.close()
        
        clips.append(build_educational_scene(v, narr_path, let_img, scene_dur))
        
    # 5. Compile Outro Scene
    print("\nBuilding Outro Scene...")
    outro_audio = os.path.join(AUDIO_DIR, "scene_outro.mp3")
    clips.append(build_intro_outro_scene(outro_audio, is_intro=False))
    
    # 6. Concatenate all scenes into final video
    print(f"\nMerging {len(clips)} scenes into final timeline...")
    final_video = concatenate_videoclips(clips, method="compose")
    
    # 7. Background Music (Lofi BGM) overlay
    print("Mixing background lofi BGM...")
    if os.path.exists(LOFI_BGM_PATH):
        bgm_clip = AudioFileClip(LOFI_BGM_PATH)
        video_dur = final_video.duration
        
        # Loop BGM to cover the entire video timeline
        loops = int(math.ceil(video_dur / bgm_clip.duration))
        bgm_clips = []
        for i in range(loops):
            bgm_clips.append(bgm_clip.with_start(i * bgm_clip.duration))
            
        full_bgm = CompositeAudioClip(bgm_clips).with_duration(video_dur)
        # Multiply volume by 0.05 to prevent BGM overpowering TTS narration
        full_bgm = full_bgm.with_effects([MultiplyVolume(0.05)])
        
        # Merge BGM into original narration tracks
        mixed_audio = CompositeAudioClip([final_video.audio, full_bgm])
        final_video = final_video.with_audio(mixed_audio)
        print("Lofi BGM mixed successfully ✔")
    else:
        print("Warning: Lofi BGM file not found. Rendering without background music.")
        
    # 8. Render final MP4 using maximum CPU threads
    threads = os.cpu_count() or 4
    print(f"\nRendering final video to: {FINAL_OUTPUT}...")
    print(f"Using {threads} CPU threads for high-speed compilation.")
    
    final_video.write_videofile(
        FINAL_OUTPUT,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=threads,
        logger="bar"
    )
    
    print("\n=" * 60)
    print("  Hangeul Blackboard Video compilation successfully completed!")
    print(f"  Target File: {FINAL_OUTPUT}")
    print("=" * 60)

    # Cleanup temporary WAV files
    print("Cleaning up temporary WAV files...")
    for f in os.listdir(AUDIO_DIR):
        if f.endswith(".wav"):
            try:
                os.remove(os.path.join(AUDIO_DIR, f))
            except Exception:
                pass
    print("Cleanup finished.")

if __name__ == "__main__":
    main()
