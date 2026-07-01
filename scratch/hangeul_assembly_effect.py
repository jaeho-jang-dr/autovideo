import os
import numpy as np
import scipy.io.wavfile as wav
from gtts import gTTS
from moviepy import (
    AudioFileClip, concatenate_audioclips, concatenate_videoclips,
    CompositeVideoClip, ImageClip, VideoClip
)
from whiteboard_animator import (
    create_whiteboard_background, create_moving_stickman_clip,
    create_checkmark_clip, create_underline_clip, create_number_badge_clip,
    create_extreme_close_up_writing_clip
)
from hangeul_decomposer import get_jamo_asset_paths

# 1. ASMR Chalk Writing Sound Generator (Using filtered white noise)
def generate_chalk_sfx(output_path, duration=3.0, sample_rate=44100):
    print("Generating synthetic ASMR Chalk Writing SFX...")
    num_samples = int(duration * sample_rate)
    noise = np.random.normal(0, 0.08, num_samples)
    filtered_noise = np.convolve(noise, np.ones(8)/8, mode='same')
    t = np.linspace(0, duration, num_samples)
    modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 5 * t) * np.sin(2 * np.pi * 50 * t)
    scratch_sound = filtered_noise * modulation
    
    envelope = np.ones(num_samples)
    fade_len = int(0.1 * sample_rate)
    envelope[:fade_len] = np.linspace(0, 1, fade_len)
    envelope[-fade_len:] = np.linspace(1, 0, fade_len)
    
    final_sound = scratch_sound * envelope
    scaled_sound = np.int16(final_sound * 32767)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wav.write(output_path, sample_rate, scaled_sound)
    print(f"ASMR Chalk SFX saved to: {output_path}")

# 2. ASMR Pencil Writing Sound Generator
def generate_pencil_sfx(output_path, duration=3.0, sample_rate=44100):
    print("Generating synthetic ASMR Pencil Writing SFX...")
    num_samples = int(duration * sample_rate)
    noise = np.random.normal(0, 0.03, num_samples)
    filtered_noise = np.convolve(noise, np.ones(3)/3, mode='same')
    t = np.linspace(0, duration, num_samples)
    stroke_envelope = np.abs(np.sin(2 * np.pi * 3.5 * t))
    graphite_friction = 0.6 + 0.4 * np.sin(2 * np.pi * 120 * t) * np.sin(2 * np.pi * 12 * t)
    
    scratch_sound = filtered_noise * stroke_envelope * graphite_friction
    envelope = np.ones(num_samples)
    fade_len = int(0.05 * sample_rate)
    envelope[:fade_len] = np.linspace(0, 1, fade_len)
    envelope[-fade_len:] = np.linspace(1, 0, fade_len)
    
    final_sound = scratch_sound * envelope
    scaled_sound = np.int16(final_sound * 32767)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wav.write(output_path, sample_rate, scaled_sound)
    print(f"ASMR Pencil SFX saved to: {output_path}")

# 3. Helper for flying letters from computer monitor screen
def create_flying_letter(letter_path, start_time, duration, screen_pos=(660, 290)):
    clip_dur = duration - start_time
    if clip_dur <= 0:
        return None
        
    img = ImageClip(letter_path).with_duration(clip_dur).with_start(start_time)
    img = img.resized(width=70)
    img_w, img_h = img.size
    
    def pos_fn(t):
        p = t / clip_dur
        # Spiral trajectory: radius expands, angle spins, floats upwards
        radius = 40 + 260 * p
        angle = 1.0 + 5.0 * p
        cur_x = screen_pos[0] + radius * np.cos(angle) - img_w / 2
        cur_y = screen_pos[1] - 30 + radius * np.sin(angle) - 150 * p - img_h / 2
        
        # Clamp to prevent compose_mask crashes
        cur_x = max(-img_w, min(1280, cur_x))
        cur_y = max(-img_h, min(720, cur_y))
        return (int(cur_x), int(cur_y))
        
    def rot_fn(t):
        return 270 * (t / clip_dur)
        
    return img.with_position(pos_fn).rotated(rot_fn)

# 4. Helper for speaking letters flying from stickman's mouth
def create_speaking_letter(letter_path, start_time, duration, mouth_pos=(280, 310)):
    clip_dur = duration - start_time
    if clip_dur <= 0:
        return None
        
    img = ImageClip(letter_path).with_duration(clip_dur).with_start(start_time)
    img_w, img_h = 80, 80
    
    def pos_fn(t):
        p = t / clip_dur
        # Sine wave trajectory floating rightwards
        cur_x = mouth_pos[0] + 550 * p - img_w / 2
        cur_y = mouth_pos[1] - 120 * p + 60 * np.sin(2 * np.pi * 1.2 * t) - img_h / 2
        
        cur_x = max(-img_w, min(1280, cur_x))
        cur_y = max(-img_h, min(720, cur_y))
        return (int(cur_x), int(cur_y))
        
    def rot_fn(t):
        return 30 * np.sin(2 * np.pi * 1.0 * t)
        
    return img.with_position(pos_fn).rotated(rot_fn)

# 5. Main Assembly Effect Renderer
def build_demo_video():
    print("Building HangeulSketch demo video...")
    
    # Create target directories
    os.makedirs("scratch", exist_ok=True)
    chalk_sound_path = "scratch/sfx_chalk_writing.wav"
    pencil_sound_path = "scratch/sfx_pencil_writing.wav"
    
    generate_chalk_sfx(chalk_sound_path, duration=4.32)
    generate_pencil_sfx(pencil_sound_path, duration=4.32)
    
    # Generate Narrations dynamically
    sc1_nar_path = "scratch/sfx_scene_1_narration.mp3"
    sc2_nar_path = "scratch/sfx_scene_2_narration.mp3"
    
    if not os.path.exists(sc1_nar_path):
        gTTS(text="안녕하세요! 한글스케치 나라에 온 것을 환영합니다.", lang="ko").save(sc1_nar_path)
    if not os.path.exists(sc2_nar_path):
        gTTS(text="아, 야, 어, 여", lang="ko").save(sc2_nar_path)
        
    # Load SFX audio clips
    whoosh_audio = AudioFileClip("assets/audio/whoosh.wav")
    pop_audio = AudioFileClip("assets/audio/pop.wav")
    chime_audio = AudioFileClip("assets/audio/bell_chime.wav")
    chalk_audio = AudioFileClip(chalk_sound_path)
    pencil_audio = AudioFileClip(pencil_sound_path)
    
    sc1_narration = AudioFileClip(sc1_nar_path)
    sc2_narration = AudioFileClip(sc2_nar_path)
    
    # ─── SCENE 1: Desk, Computer, King Sejong frame on wall, Flying Letters ───
    scene_1_dur = 4.5
    bg_1 = create_whiteboard_background(scene_1_dur)
    
    # Classroom Frame of King Sejong (Top-Right wall)
    frame_clip = ImageClip("assets/graphics/obj_sejong_frame.png").with_duration(scene_1_dur).resized(height=180).with_position((960, 40))
    # Hunminjeongeum Haeryebon Hanging Scroll (Next to King Sejong frame)
    scroll_clip = ImageClip("assets/graphics/obj_haerye_scroll.png").with_duration(scene_1_dur).resized(height=180).with_position((740, 40))
    # Desk and computer setting
    desk_clip = ImageClip("assets/graphics/obj_desk.png").with_duration(scene_1_dur).resized(width=420).with_position((450, 380))
    chair_clip = ImageClip("assets/graphics/obj_chair.png").with_duration(scene_1_dur).resized(width=140).with_position((320, 390))
    stickman_sit = ImageClip("assets/graphics/stickman_sitting.png").with_duration(scene_1_dur).resized(width=130).with_position((315, 305))
    computer_clip = ImageClip("assets/graphics/obj_computer.png").with_duration(scene_1_dur).resized(width=165).with_position((580, 240))
    
    # Hangeul letters flying from computer screen
    letters_1 = [
        ("assets/graphics/letters/letter_ㄱ.png", 0.2),
        ("assets/graphics/letters/letter_ㄴ.png", 0.6),
        ("assets/graphics/letters/letter_ㄷ.png", 1.0),
        ("assets/graphics/letters/letter_ㄹ.png", 1.4),
        ("assets/graphics/letters/letter_ㅏ.png", 1.8),
        ("assets/graphics/letters/letter_ㅓ.png", 2.2),
        ("assets/graphics/letters/word_한글.png", 2.6)
    ]
    
    flying_clips_1 = []
    for l_path, start_t in letters_1:
        clip = create_flying_letter(l_path, start_t, scene_1_dur)
        if clip:
            flying_clips_1.append(clip)
            
    # Combine Scene 1
    scene_1_video = CompositeVideoClip(
        [bg_1, frame_clip, scroll_clip, desk_clip, chair_clip, stickman_sit, computer_clip] + flying_clips_1,
        size=(1280, 720)
    )
    
    from moviepy import CompositeAudioClip
    scene_1_audio = CompositeAudioClip([chime_audio, sc1_narration.with_start(0.5)])
    scene_1_video = scene_1_video.with_audio(scene_1_audio)
    
    # ─── SCENE 2: Stickman Speaking, King Sejong Frame, Letters Flying from Mouth ───
    scene_2_dur = 4.5
    bg_2 = create_whiteboard_background(scene_2_dur)
    
    # King Sejong Frame on the wall behind
    frame_clip_2 = ImageClip("assets/graphics/obj_sejong_frame.png").with_duration(scene_2_dur).resized(height=180).with_position((560, 40))
    # Hunminjeongeum Haeryebon Hanging Scroll next to it
    scroll_clip_2 = ImageClip("assets/graphics/obj_haerye_scroll.png").with_duration(scene_2_dur).resized(height=180).with_position((780, 40))
    stickman_stand = ImageClip("assets/graphics/stickman_standing.png").with_duration(scene_2_dur).resized(width=160).with_position((180, 260))
    
    # Syllables flying from mouth (Ah, Yah, Eoh, Yeoh)
    letter_ah_path = "assets/graphics/letters/letter_아.png"
    letter_yah_path = "assets/graphics/letters/letter_야.png"
    letter_eoh_path = "assets/graphics/letters/letter_어.png"
    letter_yeoh_path = "assets/graphics/letters/letter_여.png"
    
    if not os.path.exists(letter_ah_path):
        from generate_letters_assets import generate_text_lineart
        generate_text_lineart("아", letter_ah_path, font_size=180, stroke_width=6)
    if not os.path.exists(letter_yah_path):
        from generate_letters_assets import generate_text_lineart
        generate_text_lineart("야", letter_yah_path, font_size=180, stroke_width=6)
    if not os.path.exists(letter_eoh_path):
        from generate_letters_assets import generate_text_lineart
        generate_text_lineart("어", letter_eoh_path, font_size=180, stroke_width=6)
    if not os.path.exists(letter_yeoh_path):
        from generate_letters_assets import generate_text_lineart
        generate_text_lineart("여", letter_yeoh_path, font_size=180, stroke_width=6)
        
    letters_2 = [
        (letter_ah_path, 0.4),
        (letter_yah_path, 1.4),
        (letter_eoh_path, 2.4),
        (letter_yeoh_path, 3.4)
    ]
    
    flying_clips_2 = []
    for l_path, start_t in letters_2:
        clip = create_speaking_letter(l_path, start_t, scene_2_dur)
        if clip:
            flying_clips_2.append(clip)
            
    # Combine Scene 2
    scene_2_video = CompositeVideoClip(
        [bg_2, frame_clip_2, scroll_clip_2, stickman_stand] + flying_clips_2,
        size=(1280, 720)
    )
    # Play pop sound at each letter birth, and play the narration pronouncing them
    pop_at_0 = pop_audio.with_start(0.4)
    pop_at_1 = pop_audio.with_start(1.4)
    pop_at_2 = pop_audio.with_start(2.4)
    pop_at_3 = pop_audio.with_start(3.4)
    scene_2_audio = CompositeAudioClip([pop_at_0, pop_at_1, pop_at_2, pop_at_3, sc2_narration.with_start(0.2)])
    scene_2_video = scene_2_video.with_audio(scene_2_audio)
    
    # ─── SCENE 3: Hangeul Jamo Assembly ('한') ───
    # Duration: 3.5 seconds
    scene_3_dur = 3.5
    bg_3 = create_whiteboard_background(scene_3_dur)
    
    target_x, target_y = 350, 220
    
    # Chosung 'ㅎ'
    img_cho = ImageClip("assets/graphics/letters/letter_ㅎ.png").with_duration(1.8)
    cho_w, cho_h = img_cho.size
    def pos_cho(t):
        p = t / 1.5
        if p >= 1.0: return (target_x, target_y)
        f = 1.0 - (1.0 - p)**3
        cur_x = -150 + (target_x - (-150)) * f
        cur_y = -150 + (target_y - (-150)) * f
        cur_x = max(-cho_w, min(1280, cur_x))
        cur_y = max(-cho_h, min(720, cur_y))
        return (int(cur_x), int(cur_y))
    def rot_cho(t):
        p = t / 1.5
        if p >= 1.0: return 0
        return 180 * (1.0 - (1.0 - (1.0 - p)**3))
    cho_clip = img_cho.with_position(pos_cho).rotated(rot_cho)
    
    # Jungseung 'ㅏ'
    img_jung = ImageClip("assets/graphics/letters/letter_ㅏ.png").with_duration(1.8)
    jung_w, jung_h = img_jung.size
    target_jx = 490
    def pos_jung(t):
        p = t / 1.5
        if p >= 1.0: return (target_jx, target_y)
        f = 1.0 - (1.0 - p)**3
        cur_x = 1400 + (target_jx - 1400) * f
        cur_y = -150 + (target_y - (-150)) * f
        cur_x = max(-jung_w, min(1280, cur_x))
        cur_y = max(-jung_h, min(720, cur_y))
        return (int(cur_x), int(cur_y))
    def rot_jung(t):
        p = t / 1.5
        if p >= 1.0: return 0
        return -180 * (1.0 - (1.0 - (1.0 - p)**3))
    jung_clip = img_jung.with_position(pos_jung).rotated(rot_jung)
    
    # Jongsung 'ㄴ'
    img_jong = ImageClip("assets/graphics/letters/letter_ㄴ.png").with_duration(1.8)
    jong_w, jong_h = img_jong.size
    target_bx, target_by = 400, 380
    def pos_jong(t):
        p = t / 1.5
        if p >= 1.0: return (target_bx, target_by)
        f = 1.0 - (1.0 - p)**3
        cur_x = 420 + (target_bx - 420) * f
        cur_y = 900 + (target_by - 900) * f
        cur_x = max(-jong_w, min(1280, cur_x))
        cur_y = max(-jong_h, min(720, cur_y))
        return (int(cur_x), int(cur_y))
    def rot_jong(t):
        p = t / 1.5
        if p >= 1.0: return 0
        return 90 * (1.0 - (1.0 - (1.0 - p)**3))
    jong_clip = img_jong.with_position(pos_jong).rotated(rot_jong)
    
    combined_cho = ImageClip("assets/graphics/letters/letter_ㅎ.png").with_duration(scene_3_dur - 1.8).with_start(1.8).with_position((target_x, target_y))
    combined_jung = ImageClip("assets/graphics/letters/letter_ㅏ.png").with_duration(scene_3_dur - 1.8).with_start(1.8).with_position((target_jx, target_y))
    combined_jong = ImageClip("assets/graphics/letters/letter_ㄴ.png").with_duration(scene_3_dur - 1.8).with_start(1.8).with_position((target_bx, target_by))
    
    scene_3_video = CompositeVideoClip(
        [bg_3, cho_clip, jung_clip, jong_clip, combined_cho, combined_jung, combined_jong],
        size=(1280, 720)
    )
    scene_3_audio = CompositeAudioClip([whoosh_audio.with_start(0.2), pop_audio.with_start(1.5), chime_audio.with_start(1.5)])
    scene_3_video = scene_3_video.with_audio(scene_3_audio)
    
    # ─── SCENE 4: Extreme Close-up Writing '글' (Pencil Mode, Notebook, Stroke Order) ───
    scene_4_dur = 4.32
    letter_geul_path = "assets/graphics/letters/letter_글.png"
    scene_4_video = create_extreme_close_up_writing_clip(
        letter_geul_path,
        scene_4_dur,
        target_pos=(380, 200),
        tool_type="pencil"
    )
    scene_4_video = scene_4_video.with_audio(pencil_audio)
    
    # ─── SCENE 5: Extreme Close-up Writing '글' (Chalk Mode, Blackboard, Stroke Order) ───
    scene_5_dur = 4.32
    scene_5_video = create_extreme_close_up_writing_clip(
        letter_geul_path,
        scene_5_dur,
        target_pos=(380, 200),
        tool_type="chalk"
    )
    scene_5_video = scene_5_video.with_audio(chalk_audio)
    
    # ─── SCENE 6: Emphasize Combo (Underline, Checkmark, Badge 1) ───
    scene_6_dur = 3.5
    bg_6 = create_whiteboard_background(scene_6_dur)
    
    word_hangeul_path = "assets/graphics/letters/word_한글.png"
    word_clip = (ImageClip(word_hangeul_path)
                 .with_duration(scene_6_dur)
                 .with_position((380, 240)))
                 
    underline = create_underline_clip(
        target_pos=(350, 420),
        target_width=580,
        duration=scene_6_dur,
        start_time=0.5
    )
    checkmark = create_checkmark_clip(
        pos=(880, 160),
        duration=scene_6_dur,
        start_time=1.2
    )
    badge = create_number_badge_clip(
        number_str="1",
        pos=(220, 160),
        duration=scene_6_dur,
        start_time=1.8
    )
    
    scene_6_video = CompositeVideoClip(
        [bg_6, word_clip, underline, checkmark, badge],
        size=(1280, 720)
    )
    scene_6_audio = CompositeAudioClip([pop_audio.with_start(1.8), chime_audio.with_start(1.2)])
    scene_6_video = scene_6_video.with_audio(scene_6_audio)
    
    # ─── CONCATENATE ALL SCENES & RENDER ───
    final_video = concatenate_videoclips([scene_1_video, scene_2_video, scene_3_video, scene_4_video, scene_5_video, scene_6_video])
    
    output_path = "scratch/test_whiteboard_system.mp4"
    threads = os.cpu_count() or 4
    
    print(f"Rendering HangeulSketch demo MP4 to: {output_path}...")
    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=threads,
        logger="bar"
    )
    print("HangeulSketch demo rendering successfully completed!")

if __name__ == "__main__":
    build_demo_video()
