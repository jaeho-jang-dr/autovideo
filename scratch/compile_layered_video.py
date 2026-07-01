import os
import sys
import math
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, VideoFileClip, CompositeAudioClip, VideoClip
import moviepy.video.fx as fx
from moviepy.audio.fx import MultiplyVolume

# Standard 1280x720 blueprint canvas
WIDTH, HEIGHT = 1280, 720

def wrap_text(text, max_chars=30):
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        if len(' '.join(current_line + [word])) <= max_chars:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return '\n'.join(lines)

def apply_text_bounce(clip, duration):
    """Bounces text size in the first 0.3 seconds."""
    def effect(get_frame, t):
        frame = get_frame(t)
        img = Image.fromarray(frame)
        w, h = img.size
        if t < 0.3:
            if t < 0.15:
                scale = (t / 0.15) * 1.1
            else:
                scale = 1.1 - ((t - 0.15) / 0.15) * 0.1
        else:
            scale = 1.0
        
        if scale == 1.0:
            return frame
            
        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
        resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        paste_x = (w - new_w) // 2
        paste_y = (h - new_h) // 2
        canvas.paste(resized_img, (paste_x, paste_y))
        return np.array(canvas)
        
    return clip.transform(effect)

def draw_rounded_rect(img, pt1, pt2, color, thickness, radius):
    x1, y1 = pt1
    x2, y2 = pt2
    w = x2 - x1
    h = y2 - y1
    r = min(radius, w // 2, h // 2)
    if thickness < 0: # Filled
        cv2.rectangle(img, (x1 + r, y1), (x2 - r, y2), color, -1)
        cv2.rectangle(img, (x1, y1 + r), (x2, y2 - r), color, -1)
        cv2.circle(img, (x1 + r, y1 + r), r, color, -1)
        cv2.circle(img, (x2 - r, y1 + r), r, color, -1)
        cv2.circle(img, (x1 + r, y2 - r), r, color, -1)
        cv2.circle(img, (x2 - r, y2 - r), r, color, -1)
    else: # Border
        cv2.line(img, (x1 + r, y1), (x2 - r, y1), color, thickness)
        cv2.line(img, (x1 + r, y2), (x2 - r, y2), color, thickness)
        cv2.line(img, (x1, y1 + r), (x1, y2 - r), color, thickness)
        cv2.line(img, (x2, y1 + r), (x2, y2 - r), color, thickness)
        cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)
        cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)

def make_annotation_overlay(text, duration):
    font_path_bold = r'C:\Windows\Fonts\malgunbd.ttf'
    ann_text = wrap_text(text, max_chars=25)
    
    # Calculate size
    try:
        temp_clip = TextClip(text=ann_text, font=font_path_bold, font_size=24, color='#000000', method='caption', size=(320, None))
    except Exception:
        temp_clip = TextClip(text=ann_text, font_size=24, color='#000000', method='caption', size=(320, None))
    ann_w, ann_h = temp_clip.size
    temp_clip.close()

    num_lines = ann_text.count('\n') + 1
    text_padding_y = 12 + num_lines * 10
    box_padding_y = 16 + num_lines * 12
    
    try:
        ann_txt_clip = TextClip(text=ann_text, font=font_path_bold, font_size=24, color='#000000', method='caption', size=(ann_w, ann_h + text_padding_y))
    except Exception:
        ann_txt_clip = TextClip(text=ann_text, font_size=24, color='#000000', method='caption', size=(ann_w, ann_h + text_padding_y))

    box_w = ann_w + 32
    box_h = ann_h + text_padding_y + box_padding_y

    box_img = np.zeros((box_h, box_w, 4), dtype=np.uint8)
    draw_rounded_rect(box_img, (1, 1), (box_w - 2, box_h - 2), [224, 245, 224, 200], -1, 10)
    draw_rounded_rect(box_img, (1, 1), (box_w - 2, box_h - 2), [46, 125, 50, 255], 2, 10)

    ann_bg_clip = ImageClip(box_img).with_duration(duration)
    ann_txt_clip = ann_txt_clip.with_position(('center', 'center')).with_duration(duration)

    ann_composite = CompositeVideoClip([ann_bg_clip, ann_txt_clip], size=(box_w, box_h))
    return ann_composite.with_position((45, 45)).with_duration(duration)

def make_full_canvas_clip(image_path, start_time, duration, pos_func=None, rot_func=None, scale_func=None, pulse_func=None, fade_in_duration=None):
    """
    Creates a 1280x720 transparent VideoClip where the image is drawn dynamically.
    This guarantees that the MoviePy clip boundaries are always exactly 1280x720,
    avoiding broadcast/shape mismatched errors when moving/scaling clips outside boundaries.
    """
    # Load the source image (with alpha channel)
    src_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if src_img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")
    
    # Ensure it has an alpha channel (4 channels)
    if len(src_img.shape) == 2:
        src_img = cv2.cvtColor(src_img, cv2.COLOR_GRAY2BGRA)
    elif src_img.shape[2] == 3:
        src_img = cv2.cvtColor(src_img, cv2.COLOR_BGR2BGRA)
        
    # Convert BGRA to RGBA for MoviePy compatibility
    src_img = cv2.cvtColor(src_img, cv2.COLOR_BGRA2RGBA)
    src_h, src_w = src_img.shape[:2]
    
    def make_frame(t):
        # Fresh blank transparent canvas (720 rows, 1280 cols, 4 channels)
        canvas = np.zeros((720, 1280, 4), dtype=np.uint8)
        
        # 1. Base position calculation
        if pos_func:
            x, y = pos_func(t)
        else:
            # Default to center of 1280x720 canvas
            x, y = (1280 - src_w) // 2, (720 - src_h) // 2
            
        curr_img = src_img.copy()
        curr_h, curr_w = src_h, src_w
        
        # 2. Scale transform
        if scale_func:
            factor = scale_func(t)
            if factor != 1.0 and factor > 0:
                new_w, new_h = max(1, int(src_w * factor)), max(1, int(src_h * factor))
                curr_img = cv2.resize(curr_img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                curr_w, curr_h = new_w, new_h
                # Adjust x, y so scaling is relative to the center of the asset
                if not pos_func:
                    x, y = (1280 - curr_w) // 2, (720 - curr_h) // 2
                else:
                    x = x + (src_w - curr_w) // 2
                    y = y + (src_h - curr_h) // 2
                    
        # 3. Rotation transform
        if rot_func:
            angle = rot_func(t)
            cY, cX = curr_h // 2, curr_w // 2
            M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
            curr_img = cv2.warpAffine(curr_img, M, (curr_w, curr_h), borderMode=cv2.BORDER_TRANSPARENT)
            
        # 4. Opacity/Alpha effects (pulsing or fading)
        alpha_factor = 1.0
        if pulse_func:
            alpha_factor = pulse_func(t)
            
        if fade_in_duration and t < fade_in_duration:
            alpha_factor *= (t / fade_in_duration)
            
        if alpha_factor != 1.0:
            # Multiply alpha channel by alpha_factor
            alphas = curr_img[:, :, 3].astype(float) * alpha_factor
            curr_img[:, :, 3] = np.clip(alphas, 0, 255).astype(np.uint8)
            
        # 5. Composite current image onto the 1280x720 canvas with strict boundary clipping
        x1_src, y1_src = 0, 0
        x2_src, y2_src = curr_w, curr_h
        
        x1_dst, y1_dst = int(round(x)), int(round(y))
        x2_dst, y2_dst = x1_dst + curr_w, y1_dst + curr_h
        
        # Clip coordinates
        if x1_dst < 0:
            x1_src += -x1_dst
            x1_dst = 0
        if y1_dst < 0:
            y1_src += -y1_dst
            y1_dst = 0
        if x2_dst > 1280:
            x2_src -= (x2_dst - 1280)
            x2_dst = 1280
        if y2_dst > 720:
            y2_src -= (y2_dst - 720)
            y2_dst = 720
            
        # Draw on canvas if overlap is non-empty
        if (x2_dst > x1_dst) and (y2_dst > y1_dst) and (x2_src > x1_src) and (y2_src > y1_src):
            canvas[y1_dst:y2_dst, x1_dst:x2_dst] = curr_img[y1_src:y2_src, x1_src:x2_src]
            
        return canvas

    return VideoClip(make_frame, duration=duration).with_start(start_time)

def main():
    print("="*60)
    print(" Building Custom 2D Layer-Animated Video (Corrected Wheel Well Alignment)")
    print("="*60)
    
    # 0. Load TTS durations first to compute dynamic timeline durations
    tts_path_1 = "scratch/line_craft_assets/tts_1.mp3"
    tts_path_2 = "scratch/line_craft_assets/tts_2.mp3"
    
    if not os.path.exists(tts_path_1) or not os.path.exists(tts_path_2):
        print("Error: TTS narration files are missing!")
        sys.exit(1)
        
    tts_clip_1 = AudioFileClip(tts_path_1)
    tts_clip_2 = AudioFileClip(tts_path_2)
    tts_1_dur = tts_clip_1.duration
    tts_2_dur = tts_clip_2.duration
    tts_clip_1.close()
    tts_clip_2.close()
    
    print(f"TTS 1 Duration: {tts_1_dur:.2f}s")
    print(f"TTS 2 Duration: {tts_2_dur:.2f}s")
    
    # Define Scene timings based on voice durations
    tts_1_start = 1.5
    sc1_duration = tts_1_start + tts_1_dur + 0.2  # 1.5 + 6.3 + 0.2 = 8.0s
    
    tts_2_start_rel = 1.0
    sc2_duration = tts_2_start_rel + tts_2_dur + 0.9  # 1.0 + 6.09 + 0.9 = 8.0s
    
    total_duration = sc1_duration + sc2_duration  # 16.0s
    print(f"Scene 1 Duration: {sc1_duration:.2f}s")
    print(f"Scene 2 Duration: {sc2_duration:.2f}s")
    print(f"Total Video Duration: {total_duration:.2f}s")
    
    # Background Solid Navy Canvas
    bg_canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    bg_canvas[:, :] = [47, 25, 10] # Navy/blue tone
    bg_clip = ImageClip(bg_canvas).with_duration(total_duration)

    # 1. BGM Audio Loop
    bgm_path = "assets/audio/lofi_bgm.mp3"
    audio_elements = []
    if os.path.exists(bgm_path):
        bgm = AudioFileClip(bgm_path).with_duration(total_duration).with_effects([MultiplyVolume(0.12)])
        audio_elements.append(bgm)

    # Narrations
    tts_1 = AudioFileClip(tts_path_1).with_start(tts_1_start)
    audio_elements.append(tts_1)
    
    tts_2 = AudioFileClip(tts_path_2).with_start(sc1_duration + tts_2_start_rel)
    audio_elements.append(tts_2)

    # Transition Whoosh SFX (spans across the scene cut boundary)
    whoosh_path = "assets/audio/whoosh.wav"
    if os.path.exists(whoosh_path):
        whoosh = AudioFileClip(whoosh_path).with_start(sc1_duration - 0.3).with_effects([MultiplyVolume(0.45)])
        audio_elements.append(whoosh)

    # Pop SFXs (perfect sync alignment with start/end visual events)
    pop_path = "assets/audio/pop.wav"
    pop_timings = [
        0.5,                         # Scene 1: Body popup
        1.5,                         # Scene 1: Front wheel rolls
        1.8,                         # Scene 1: Rear wheel rolls
        2.3,                         # Scene 1: Front wheel lands
        2.6,                         # Scene 1: Rear wheel lands
        3.2,                         # Scene 1: Arrow flies
        3.5,                         # Scene 1: Arrow impact vibration
        sc1_duration + 0.2,          # Scene 2: Housing popup
        sc1_duration + 0.8,          # Scene 2: Large gear rolls
        sc1_duration + 1.2,          # Scene 2: Small gear rolls
        sc1_duration + 1.6,          # Scene 2: Large gear engagement
        sc1_duration + 2.0,          # Scene 2: Small gear engagement
        sc1_duration + 2.5,          # Scene 2: HUD box slides
        sc1_duration + 3.0           # Scene 2: HUD box settles
    ]
    if os.path.exists(pop_path):
        for pt in pop_timings:
            pop_sfx = AudioFileClip(pop_path).with_start(pt).with_effects([MultiplyVolume(0.50)])
            audio_elements.append(pop_sfx)

    # -------------------------------------------------------------------------
    # SCENE 1 LAYER ANIMATIONS (0.0s to sc1_duration)
    # -------------------------------------------------------------------------
    layers_dir = "scratch/layers"
    
    # Grid background (fades in)
    grid_c = make_full_canvas_clip(os.path.join(layers_dir, "grid.png"), 0.0, sc1_duration, fade_in_duration=0.5)
    
    # Car Body (zoom_bounce popup at 0.5s)
    def body_scale(t):
        if t < 0.8:
            return 1.0 + 0.12 * np.sin(np.pi * t / 0.8) * np.exp(-3.5 * t)
        return 1.0
    body_c = make_full_canvas_clip(os.path.join(layers_dir, "body.png"), 0.5, sc1_duration - 0.5, scale_func=body_scale)

    # Jet Wing (appears at 1.0s, fade in)
    wing_c = make_full_canvas_clip(os.path.join(layers_dir, "wing.png"), 1.0, sc1_duration - 1.0, pos_func=lambda t: (710, 280), fade_in_duration=0.4)

    # Front Wheel (rolls in from left x=-200 to x=850, y=480)
    # Symmetrically aligns with the front of the cabin window & car hood
    def wheel_f_pos(t):
        if t < 0.8:
            ratio = t / 0.8
            x = -200 + (850 - (-200)) * ratio
        else:
            x = 850
        return (x, 480)
    def wheel_f_rot(t):
        ratio = min(t / 0.8, 1.0)
        return ratio * 900.0 # 2.5 full rotations matching longer distance
    wheel_f_c = make_full_canvas_clip(os.path.join(layers_dir, "wheel.png"), 1.5, sc1_duration - 1.5, pos_func=wheel_f_pos, rot_func=wheel_f_rot)

    # Rear Wheel (rolls in from left x=-200 to x=450, y=480)
    # Symmetrically aligns with the rear of the cabin window & engine exhaust nozzle
    def wheel_r_pos(t):
        if t < 0.8:
            ratio = t / 0.8
            x = -200 + (450 - (-200)) * ratio
        else:
            x = 450
        return (x, 480)
    def wheel_r_rot(t):
        ratio = min(t / 0.8, 1.0)
        return ratio * 540.0 # 1.5 rotations matching distance
    wheel_r_c = make_full_canvas_clip(os.path.join(layers_dir, "wheel.png"), 1.8, sc1_duration - 1.8, pos_func=wheel_r_pos, rot_func=wheel_r_rot)

    # Arrow Pointer (flies in from x=1350, y=50 to x=800, y=180 between 3.2s and 3.5s, then vibrates on impact)
    def arrow_pos(t):
        if t < 0.3:
            ratio = t / 0.3
            x = 1350 + (800 - 1350) * ratio
            y = 50 + (180 - 50) * ratio
        elif t < 0.5:
            # Dampened vibration simulating high-speed impact stick
            phase = (t - 0.3) / 0.2
            decay = np.exp(-5.0 * phase)
            vib = 6 * np.sin(2 * np.pi * 35 * (t - 0.3)) * decay
            x = 800 + vib
            y = 180 + vib
        else:
            x = 800
            y = 180
        return (x, y)
    pointer_c = make_full_canvas_clip(os.path.join(layers_dir, "pointer.png"), 3.2, sc1_duration - 3.2, pos_func=arrow_pos)

    # Target info box overlay
    ann_1 = make_annotation_overlay("비행 자동차 구조 설계도", sc1_duration).with_start(0.0)

    # Bottom Subtitle 1 (Hardburned)
    font_path = r'C:\Windows\Fonts\malgun.ttf'
    sub_text_1 = "미래의 자동차가 칠판 위에 한 땀 한 땀 아름다운 선으로 그려지고 있습니다."
    sub_wrap_1 = wrap_text(sub_text_1, max_chars=40)
    sub_clip_1 = TextClip(text=sub_wrap_1, font=font_path, font_size=24, color='white', stroke_color='black', stroke_width=2, method='caption', size=(WIDTH - 120, None))
    sub_h1 = sub_clip_1.size[1]
    sub_clip_1 = sub_clip_1.with_position(('center', HEIGHT - sub_h1 - 70)).with_duration(tts_1_dur).with_start(tts_1_start)
    sub_clip_1 = apply_text_bounce(sub_clip_1, tts_1_dur)

    # -------------------------------------------------------------------------
    # SCENE 2 LAYER ANIMATIONS (sc1_duration to total_duration)
    # -------------------------------------------------------------------------
    # Grid background (same)
    grid_c2 = make_full_canvas_clip(os.path.join(layers_dir, "grid.png"), sc1_duration, sc2_duration)

    # Main Housing (elastic zoom_bounce popup at sc1_duration + 0.2s)
    def housing_scale(t):
        if t < 0.8:
            return 1.0 + 0.12 * np.sin(np.pi * t / 0.8) * np.exp(-3.5 * t)
        return 1.0
    housing_c = make_full_canvas_clip(os.path.join(layers_dir, "gear_body.png"), sc1_duration + 0.2, sc2_duration - 0.2, scale_func=housing_scale)

    # Large Gear (rolls in from top-left x=100, y=-200 to x=490, y=210 between 0.8s and 1.6s, then rotates 30deg/s)
    def gear_l_pos(t):
        if t < 0.8:
            ratio = t / 0.8
            x = 100 + (490 - 100) * ratio
            y = -200 + (210 - (-200)) * ratio
        else:
            x = 490
            y = 210
        return (x, y)
    def gear_l_rot(t):
        if t < 0.8:
            ratio = t / 0.8
            return ratio * 360.0
        else:
            return 360.0 + (t - 0.8) * 30.0
    gear_l_c = make_full_canvas_clip(os.path.join(layers_dir, "gear_large.png"), sc1_duration + 0.8, sc2_duration - 0.8, pos_func=gear_l_pos, rot_func=gear_l_rot)

    # Small Gear (rolls in from top-right x=1000, y=-150 to x=770, y=285 between 1.2s and 2.0s, then rotates -57deg/s)
    def gear_s_pos(t):
        if t < 0.8:
            ratio = t / 0.8
            x = 1000 + (770 - 1000) * ratio
            y = -150 + (285 - (-150)) * ratio
        else:
            x = 770
            y = 285
        return (x, y)
    def gear_s_rot(t):
        if t < 0.8:
            ratio = t / 0.8
            return ratio * -360.0
        else:
            return -360.0 + (t - 0.8) * -57.0
    gear_s_c = make_full_canvas_clip(os.path.join(layers_dir, "gear_small.png"), sc1_duration + 1.2, sc2_duration - 1.2, pos_func=gear_s_pos, rot_func=gear_s_rot)

    # Signal Wave (rhythmic brightness pulsing, with a 0.5s fade in)
    def wave_pulse(t):
        return 0.3 + 0.7 * (0.5 + 0.5 * np.sin(2 * np.pi * 1.8 * t))
    wave_c = make_full_canvas_clip(os.path.join(layers_dir, "signal_wave.png"), sc1_duration + 2.0, sc2_duration - 2.0, pos_func=lambda t: (390, 480), pulse_func=wave_pulse, fade_in_duration=0.5)

    # Spec Hud Box (fly-in from x=1350, y=100 to x=100, y=100 with elastic settling)
    def hud_pos(t):
        if t < 0.5:
            ratio = t / 0.5
            val = 1.0 - np.exp(-6.0 * ratio) * np.cos(1.5 * np.pi * ratio)
            x = 1350 - (1350 - 100) * val
        else:
            x = 100
        return (x, 100)
    hud_c = make_full_canvas_clip(os.path.join(layers_dir, "spec_label.png"), sc1_duration + 2.5, sc2_duration - 2.5, pos_func=hud_pos)

    # Target info box overlay
    ann_2 = make_annotation_overlay("로봇 손 관절 기어 메커니즘", sc2_duration).with_start(sc1_duration)

    # Bottom Subtitle 2 (Hardburned)
    sub_text_2 = "정밀한 기계 부품과 톱니바퀴들이 유기적으로 맞물려 움직이기 시작합니다."
    sub_wrap_2 = wrap_text(sub_text_2, max_chars=40)
    sub_clip_2 = TextClip(text=sub_wrap_2, font=font_path, font_size=24, color='white', stroke_color='black', stroke_width=2, method='caption', size=(WIDTH - 120, None))
    sub_h2 = sub_clip_2.size[1]
    sub_clip_2 = sub_clip_2.with_position(('center', HEIGHT - sub_h2 - 70)).with_duration(tts_2_dur).with_start(sc1_duration + tts_2_start_rel)
    sub_clip_2 = apply_text_bounce(sub_clip_2, tts_2_dur)

    # -------------------------------------------------------------------------
    # FINAL FLAT ASSEMBLY & EXPORT
    # -------------------------------------------------------------------------
    # Composite all layers flat on a single timeline to bypass nested CompositeVideoClip bugs
    all_clips = [
        bg_clip,
        grid_c, body_c, wing_c, wheel_f_c, wheel_r_c, pointer_c, ann_1, sub_clip_1,
        grid_c2, housing_c, gear_l_c, gear_s_c, wave_c, hud_c, ann_2, sub_clip_2
    ]
    
    layered_video = CompositeVideoClip(all_clips, size=(WIDTH, HEIGHT)).with_duration(total_duration)

    # Add audio track mix
    if audio_elements:
        mixed_audio = CompositeAudioClip(audio_elements).with_duration(total_duration)
        layered_video = layered_video.with_audio(mixed_audio)

    # Output path Setup
    os.makedirs("line_craft", exist_ok=True)
    temp_720p = "line_craft/line_craft_final.mp4.720p.mp4"
    final_output = "line_craft/line_craft_final.mp4"

    # Clean previous temp files
    for p in [temp_720p, final_output]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

    cpu_cores = os.cpu_count() or 4
    print(f"Compiling 2D layer-composite video (720p) utilizing {cpu_cores} threads...")
    
    layered_video.write_videofile(
        temp_720p,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=cpu_cores,
        ffmpeg_params=["-threads", str(cpu_cores)]
    )

    # Upscale to 4K via optimized FFmpeg Lanczos filter & AAC Audio transcoding (fixed sound output)
    print("Muxing and upscaling final video to 4K (3840x2160) via ffmpeg Lanczos filter...")
    upscale_cmd = [
        "ffmpeg", "-y",
        "-i", temp_720p,
        "-vf", "scale=3840:2160:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        final_output
    ]
    try:
        import subprocess
        subprocess.run(upscale_cmd, check=True)
        print("4K upscale and AAC audio encoding completed successfully! [OK]")
        if os.path.exists(temp_720p):
            os.remove(temp_720p)
    except Exception as e:
        print(f"Warning: ffmpeg upscale/transcode failed ({e}). Reverting to original 720p.")
        os.rename(temp_720p, final_output)

    print("="*60)
    print(f"SUCCESS: High-quality layered video saved to {final_output}")
    print("="*60)

if __name__ == '__main__':
    main()
