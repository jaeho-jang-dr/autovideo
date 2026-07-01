import os
import sys
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip, VideoClip
import moviepy.video.fx as fx
from moviepy.audio.fx import MultiplyVolume

# Standard 1280x720 canvas
WIDTH, HEIGHT = 1280, 720

def render_text_image(text, font_size=48, color=(255, 255, 255, 255), stroke_color=(0, 0, 0, 255), stroke_width=3):
    font_path = r'C:\Windows\Fonts\malgunbd.ttf'
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()
        
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # Margin padding
    w, h = tw + 40, th + 40
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Center calculation
    tx = (w - tw) // 2 - bbox[0]
    ty = (h - th) // 2 - bbox[1]
    
    draw.text((tx, ty), text, font=font, fill=color, stroke_fill=stroke_color, stroke_width=stroke_width)
    return np.array(img)

def make_full_canvas_clip(image_np, start_time, duration, pos_func=None, rot_func=None, scale_func=None, pulse_func=None, fade_in_duration=None):
    """
    Creates a 1280x720 transparent VideoClip where the image is drawn dynamically.
    Guarantees size alignment (no out-of-bounds errors).
    """
    src_img = image_np.copy()
    # Ensure it has an alpha channel (4 channels) and is in RGBA format
    if len(src_img.shape) == 2:
        src_img = cv2.cvtColor(src_img, cv2.COLOR_GRAY2BGRA)
    elif src_img.shape[2] == 3:
        src_img = cv2.cvtColor(src_img, cv2.COLOR_BGR2BGRA)
        
    # Convert BGRA to RGBA for MoviePy compatibility
    src_img = cv2.cvtColor(src_img, cv2.COLOR_BGRA2RGBA)
    src_h, src_w = src_img.shape[:2]
    
    def make_frame(t):
        canvas = np.zeros((720, 1280, 4), dtype=np.uint8)
        
        # 1. Position
        if pos_func:
            x, y = pos_func(t)
        else:
            x, y = (1280 - src_w) // 2, (720 - src_h) // 2
            
        curr_img = src_img.copy()
        curr_h, curr_w = src_h, src_w
        
        # 2. Scale
        if scale_func:
            factor = scale_func(t)
            if factor != 1.0 and factor > 0:
                new_w, new_h = max(1, int(src_w * factor)), max(1, int(src_h * factor))
                curr_img = cv2.resize(curr_img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                curr_w, curr_h = new_w, new_h
                # Centering offset adjustment
                if pos_func:
                    x = x + (src_w - curr_w) // 2
                    y = y + (src_h - curr_h) // 2
                else:
                    x, y = (1280 - curr_w) // 2, (720 - curr_h) // 2
                    
        # 3. Rotation
        if rot_func:
            angle = rot_func(t)
            cY, cX = curr_h // 2, curr_w // 2
            M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
            curr_img = cv2.warpAffine(curr_img, M, (curr_w, curr_h), borderMode=cv2.BORDER_TRANSPARENT)
            
        # 4. Opacity
        alpha_factor = 1.0
        if pulse_func:
            alpha_factor = pulse_func(t)
            
        if fade_in_duration and t < fade_in_duration:
            alpha_factor *= (t / fade_in_duration)
            
        if alpha_factor != 1.0:
            alphas = curr_img[:, :, 3].astype(float) * alpha_factor
            curr_img[:, :, 3] = np.clip(alphas, 0, 255).astype(np.uint8)
            
        # 5. Composite with boundary clipping
        x1_src, y1_src = 0, 0
        x2_src, y2_src = curr_w, curr_h
        
        x1_dst, y1_dst = int(round(x)), int(round(y))
        x2_dst, y2_dst = x1_dst + curr_w, y1_dst + curr_h
        
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
            
        if (x2_dst > x1_dst) and (y2_dst > y1_dst) and (x2_src > x1_src) and (y2_src > y1_src):
            canvas[y1_dst:y2_dst, x1_dst:x2_dst] = curr_img[y1_src:y2_src, x1_src:x2_src]
            
        return canvas

    return VideoClip(make_frame, duration=duration).with_start(start_time)

def main():
    print("="*60)
    print(" Compiling Word Learning FlatCanvas Video (29.0s)")
    print("="*60)
    
    # 29.0s safely avoids lofi_bgm.mp3's 29.94s limit to prevent MoviePy OSError
    total_duration = 29.0
    interval = 2.9
    
    # 0. Solid Navy Background Canvas
    bg_canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    bg_canvas[:, :] = [47, 25, 10]
    bg_clip = ImageClip(bg_canvas).with_duration(total_duration)
    
    # Grid overlay
    layers_dir = "scratch/layers"
    grid_img = cv2.imread(os.path.join(layers_dir, "grid.png"), cv2.IMREAD_UNCHANGED)
    grid_img = cv2.cvtColor(grid_img, cv2.COLOR_BGRA2RGBA)
    grid_clip = make_full_canvas_clip(grid_img, 0.0, total_duration, fade_in_duration=0.5)

    # 1. BGM Loop
    bgm_path = "assets/audio/lofi_bgm.mp3"
    audio_elements = []
    if os.path.exists(bgm_path):
        bgm = AudioFileClip(bgm_path).with_duration(total_duration).with_effects([MultiplyVolume(0.12)])
        audio_elements.append(bgm)

    # Word definitions
    vocab_list = [
        {"file": "bag.png", "text": "가방", "audio": "bag.mp3"},
        {"file": "bicycle.png", "text": "자전거", "audio": "bicycle.mp3"},
        {"file": "clock.png", "text": "시계", "audio": "clock.mp3"},
        {"file": "book.png", "text": "책", "audio": "book.mp3"},
        {"file": "glasses.png", "text": "안경", "audio": "glasses.mp3"},
        {"file": "shoes.png", "text": "신발", "audio": "shoes.mp3"},
        {"file": "pencil.png", "text": "연필", "audio": "pencil.mp3"},
        {"file": "umbrella.png", "text": "우산", "audio": "umbrella.mp3"},
        {"file": "hat.png", "text": "모자", "audio": "hat.mp3"},
        {"file": "cup.png", "text": "컵", "audio": "cup.mp3"}
    ]

    vocab_dir = "scratch/vocab_assets"
    audio_dir = "scratch/vocab_assets/audio"
    
    # Grid slot positioning math (5 columns, 2 rows)
    # Cols: 160, 400, 640, 880, 1120
    # Rows: 180, 480
    cols_x = [160, 400, 640, 880, 1120]
    rows_y = [180, 480]

    all_clips = [bg_clip, grid_clip]
    pop_timings = []
    whoosh_timings = []

    for i, item in enumerate(vocab_list):
        t_start = interval * i
        
        # Grid positions
        col = i % 5
        row = i // 5
        target_x = cols_x[col]
        target_y = rows_y[row]
        
        # Add Narration Audio (plays at t_start + 1.0s)
        aud_path = os.path.join(audio_dir, item["audio"])
        if os.path.exists(aud_path):
            word_audio = AudioFileClip(aud_path).with_start(t_start + 1.0)
            audio_elements.append(word_audio)

        # Sound timings
        pop_timings.append(t_start + 0.0)         # Object popup
        whoosh_timings.append(t_start + 0.5)      # Text fly-in
        pop_timings.append(t_start + 1.2)         # Text highlight bounce
        whoosh_timings.append(t_start + 2.1)      # Object & text slide to grid

        # ----------------------------------------------------
        # 1. OBJECT LAYER COMPILING
        # ----------------------------------------------------
        obj_path = os.path.join(vocab_dir, item["file"])
        obj_img = cv2.imread(obj_path, cv2.IMREAD_UNCHANGED)
        obj_img = cv2.cvtColor(obj_img, cv2.COLOR_BGRA2RGBA)
        obj_h, obj_w = obj_img.shape[:2]
        
        def obj_pos(t, tx=target_x, ty=target_y, ow=obj_w, oh=obj_h):
            if t < 2.1:
                # Active center position
                x, y = 640, 260
            elif t < 2.6:
                # Slide to grid slot
                ratio = (t - 2.1) / 0.5
                ratio_eased = 0.5 - 0.5 * math.cos(math.pi * ratio)
                x = 640 + (tx - 640) * ratio_eased
                y = 260 + (ty - 260) * ratio_eased
            else:
                # Settle in grid slot
                x, y = tx, ty
            return (x - ow // 2, y - oh // 2)

        def obj_scale(t):
            if t < 0.5:
                # Elastic popup zoom
                ratio = t / 0.5
                val = 1.0 - math.exp(-6.0 * ratio) * math.cos(1.5 * math.pi * ratio)
                return 1.5 * val
            elif t < 2.1:
                return 1.5
            elif t < 2.6:
                # Scale down from 1.5 to 0.9 during slide
                ratio = (t - 2.1) / 0.5
                return 1.5 + (0.9 - 1.5) * ratio
            else:
                return 0.9

        obj_clip = make_full_canvas_clip(
            obj_img, 
            t_start, 
            total_duration - t_start, 
            pos_func=obj_pos, 
            scale_func=obj_scale
        )
        all_clips.append(obj_clip)

        # ----------------------------------------------------
        # 2. TEXT LAYER COMPILING
        # ----------------------------------------------------
        # Render high-res Korean text image
        txt_img = render_text_image(item["text"], font_size=48)
        txt_h, txt_w = txt_img.shape[:2]

        def txt_pos(t, tx=target_x, ty=target_y, tw=txt_w, th=txt_h):
            if t < 0.5:
                # Elastic fly-in from right screen edge (1350) to center bottom (640, 380)
                ratio = t / 0.5
                val = 1.0 - math.exp(-6.0 * ratio) * math.cos(1.5 * math.pi * ratio)
                x = 1350 - (1350 - 640) * val
                y = 380
            elif t < 1.6:
                # Active center bottom
                x, y = 640, 380
            elif t < 2.1:
                # Slide to grid slot (aligned at target_y + 90)
                ratio = (t - 1.6) / 0.5
                ratio_eased = 0.5 - 0.5 * math.cos(math.pi * ratio)
                x = 640 + (tx - 640) * ratio_eased
                y = 380 + (ty + 90 - 380) * ratio_eased
            else:
                x, y = tx, ty + 90
            return (x - tw // 2, y - th // 2)

        def txt_scale(t):
            if t < 0.5:
                return 1.0
            elif t < 0.7:
                return 1.0
            elif t < 1.0:
                # Highlight bounce during TTS (peaks at 1.3 scale)
                phase = (t - 0.7) / 0.3
                return 1.0 + 0.3 * math.sin(math.pi * phase)
            elif t < 1.6:
                return 1.0
            elif t < 2.1:
                # Scale down from 1.0 to 0.6 during slide
                ratio = (t - 1.6) / 0.5
                return 1.0 + (0.6 - 1.0) * ratio
            else:
                return 0.6

        # Text clip starts at t_start + 0.5 (coincides with fly-in whoosh)
        txt_clip = make_full_canvas_clip(
            txt_img, 
            t_start + 0.5, 
            total_duration - (t_start + 0.5), 
            pos_func=txt_pos, 
            scale_func=txt_scale
        )
        all_clips.append(txt_clip)

    # 3. Synchronize SFX Audio Tracks
    pop_path = "assets/audio/pop.wav"
    if os.path.exists(pop_path):
        for pt in pop_timings:
            pop_sfx = AudioFileClip(pop_path).with_start(pt).with_effects([MultiplyVolume(0.50)])
            audio_elements.append(pop_sfx)

    whoosh_path = "assets/audio/whoosh.wav"
    if os.path.exists(whoosh_path):
        for wt in whoosh_timings:
            whoosh_sfx = AudioFileClip(whoosh_path).with_start(wt - 0.1).with_effects([MultiplyVolume(0.40)])
            audio_elements.append(whoosh_sfx)

    # Final Flat Composition Muxing
    layered_video = CompositeVideoClip(all_clips, size=(WIDTH, HEIGHT)).with_duration(total_duration)

    if audio_elements:
        mixed_audio = CompositeAudioClip(audio_elements).with_duration(total_duration)
        layered_video = layered_video.with_audio(mixed_audio)

    # Export configuration
    os.makedirs("line_craft", exist_ok=True)
    temp_720p = "line_craft/vocab_learning.mp4.720p.mp4"
    final_output = "line_craft/vocab_learning.mp4"

    # Clean old files
    for p in [temp_720p, final_output]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

    cpu_cores = os.cpu_count() or 4
    print(f"Compiling word learning video (720p) utilizing {cpu_cores} threads...")
    
    layered_video.write_videofile(
        temp_720p,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=cpu_cores,
        ffmpeg_params=["-threads", str(cpu_cores)]
    )

    # 4K Upscale Render (using Lanczos filter)
    print("Upscaling to 4K (3840x2160) for YouTube premium VP09 codec...")
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
        print("4K upscale completed successfully! [OK]")
        if os.path.exists(temp_720p):
            os.remove(temp_720p)
    except Exception as e:
        print(f"Warning: Ffmpeg upscale failed ({e}). Reverted to 720p.")
        os.rename(temp_720p, final_output)

    print("="*60)
    print(f"SUCCESS: High-quality vocabulary video saved to {final_output}")
    print("="*60)

    # Open video visibly
    video_abs = os.path.abspath(final_output)
    if os.path.exists(video_abs):
        print(f"Opening video visibly: {video_abs}")
        os.startfile(video_abs)

if __name__ == '__main__':
    main()
