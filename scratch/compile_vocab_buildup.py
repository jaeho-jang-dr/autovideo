import os
import sys
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip, VideoClip
from moviepy.audio.fx import MultiplyVolume

# Standard 1280x720 canvas
WIDTH, HEIGHT = 1280, 720

def generate_blackboard():
    """Generates a beautiful forest-green chalkboard background with dotted grid lines and double border."""
    img = Image.new("RGBA", (1280, 720), (20, 38, 28, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer white/cream border
    draw.rectangle([(12, 12), (1268, 708)], outline=(240, 240, 230, 255), width=3)
    # Inner thin border
    draw.rectangle([(18, 18), (1262, 702)], outline=(240, 240, 230, 120), width=1)
    
    # Helper to draw dotted lines
    def draw_dotted_line(p1, p2, color, width=2, gap=14):
        x1, y1 = p1
        x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        dx, dy = dx / dist, dy / dist
        curr = 0
        while curr < dist:
            ex = x1 + dx * curr
            ey = y1 + dy * curr
            dash_len = min(gap // 2, dist - curr)
            draw.line([(ex, ey), (ex + dx * dash_len, ey + dy * dash_len)], fill=color, width=width)
            curr += gap

    # Vertical dividers at grid midpoints
    div_x = [265, 515, 765, 1015]
    for x in div_x:
        draw_dotted_line((x, 85), (x, 690), (240, 240, 230, 80), width=2)
        
    # Horizontal divider
    draw_dotted_line((25, 360), (1255, 360), (240, 240, 230, 80), width=2)
    
    # Blackboard Title
    font_path = r'C:\Windows\Fonts\malgunbd.ttf'
    try:
        font_title = ImageFont.truetype(font_path, 30)
    except IOError:
        font_title = ImageFont.load_default()
        
    title_text = "★ 그림 글자 공부 ★"
    bbox = font_title.getbbox(title_text)
    tw = bbox[2] - bbox[0]
    tx = (1280 - tw) // 2
    ty = 35
    draw.text((tx, ty), title_text, font=font_title, fill=(255, 255, 200, 255))
    
    os.makedirs("scratch/layers", exist_ok=True)
    img_path = "scratch/layers/vocab_board.png"
    img.save(img_path)
    print(f"Generated chalkboard layout background: {img_path}")

def render_text_image(text, font_size=36, bg_color=(28, 52, 38, 230), border_color=(140, 230, 120, 255), text_color=(255, 255, 255, 255)):
    """Renders a word label badge with rounded corners, border, and text."""
    font_path = r'C:\Windows\Fonts\malgunbd.ttf'
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()
        
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # Rounded box padding
    pad_w, pad_h = 24, 12
    w, h = tw + pad_w * 2, th + pad_h * 2
    
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded rectangle badge
    draw.rounded_rectangle(
        [(2, 2), (w - 3, h - 3)], 
        radius=10, 
        fill=bg_color, 
        outline=border_color, 
        width=2
    )
    
    # Center text inside badge
    tx = (w - tw) // 2 - bbox[0]
    ty = (h - th) // 2 - bbox[1]
    draw.text((tx, ty), text, font=font, fill=text_color)
    
    return np.array(img)

def make_full_canvas_clip(image_np, start_time, duration, pos_func=None, rot_func=None, scale_func=None, pulse_func=None, fade_in_duration=None):
    """
    Creates a 1280x720 transparent VideoClip where the image is drawn dynamically.
    Guarantees size alignment (no out-of-bounds errors).
    """
    src_img = image_np.copy()
    if len(src_img.shape) == 2:
        src_img = cv2.cvtColor(src_img, cv2.COLOR_GRAY2BGRA)
    elif src_img.shape[2] == 3:
        src_img = cv2.cvtColor(src_img, cv2.COLOR_BGR2BGRA)
        
    src_img = cv2.cvtColor(src_img, cv2.COLOR_BGRA2RGBA)
    src_h, src_w = src_img.shape[:2]
    
    def make_frame(t):
        canvas = np.zeros((720, 1280, 4), dtype=np.uint8)
        
        if pos_func:
            x, y = pos_func(t)
        else:
            x, y = (1280 - src_w) // 2, (720 - src_h) // 2
            
        curr_img = src_img.copy()
        curr_h, curr_w = src_h, src_w
        
        if scale_func:
            factor = scale_func(t)
            if factor != 1.0 and factor > 0:
                new_w, new_h = max(1, int(src_w * factor)), max(1, int(src_h * factor))
                curr_img = cv2.resize(curr_img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                curr_w, curr_h = new_w, new_h
                if pos_func:
                    x = x + (src_w - curr_w) // 2
                    y = y + (src_h - curr_h) // 2
                else:
                    x, y = (1280 - curr_w) // 2, (720 - curr_h) // 2
                    
        if rot_func:
            angle = rot_func(t)
            cY, cX = curr_h // 2, curr_w // 2
            M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
            curr_img = cv2.warpAffine(curr_img, M, (curr_w, curr_h), borderMode=cv2.BORDER_TRANSPARENT)
            
        alpha_factor = 1.0
        if pulse_func:
            alpha_factor = pulse_func(t)
            
        if fade_in_duration and t < fade_in_duration:
            alpha_factor *= (t / fade_in_duration)
            
        if alpha_factor != 1.0:
            alphas = curr_img[:, :, 3].astype(float) * alpha_factor
            curr_img[:, :, 3] = np.clip(alphas, 0, 255).astype(np.uint8)
            
        # Composite with boundary clipping
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
    print(" Compiling BuildUp Word Learning Video (29.0s)")
    print("="*60)
    
    total_duration = 29.0
    interval = 2.9
    
    # 0. Generate Blackboard background
    generate_blackboard()
    bg_img = cv2.imread("scratch/layers/vocab_board.png", cv2.IMREAD_UNCHANGED)
    bg_img = cv2.cvtColor(bg_img, cv2.COLOR_BGRA2RGBA)
    bg_clip = ImageClip(bg_img[:, :, :3]).with_duration(total_duration)
    
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
    
    # Symmetrical grid layout coordinates (5 columns, 2 rows)
    cols_x = [140, 390, 640, 890, 1140]
    rows_y = [220, 500]

    all_clips = [bg_clip]
    pop_timings = []
    whoosh_timings = []
    chime_timings = []

    for i, item in enumerate(vocab_list):
        t_start = interval * i
        
        # Grid coordinates
        col = i % 5
        row = i // 5
        cx = cols_x[col]
        cy = rows_y[row]
        
        # Target centers for object and text inside this cell
        obj_target_x = cx - 55
        txt_target_x = cx + 55
        
        # Add Narration Audio (plays at t_start + 1.0s)
        aud_path = os.path.join(audio_dir, item["audio"])
        if os.path.exists(aud_path):
            word_audio = AudioFileClip(aud_path).with_start(t_start + 1.0)
            audio_elements.append(word_audio)

        # Sound effect timings
        pop_timings.append(t_start + 0.0)         # Object popup
        whoosh_timings.append(t_start + 0.5)      # Text fly-in
        chime_timings.append(t_start + 1.0)       # Highlight Ding / Chime

        # ----------------------------------------------------
        # 1. OBJECT LAYER COMPILING
        # ----------------------------------------------------
        obj_path = os.path.join(vocab_dir, item["file"])
        obj_img = cv2.imread(obj_path, cv2.IMREAD_UNCHANGED)
        obj_img = cv2.cvtColor(obj_img, cv2.COLOR_BGRA2RGBA)
        obj_h, obj_w = obj_img.shape[:2]
        
        obj_clip = make_full_canvas_clip(
            obj_img, 
            t_start, 
            total_duration - t_start, 
            pos_func=lambda t, tx=obj_target_x, ty=cy, ow=obj_w, oh=obj_h: (tx - ow // 2, ty - oh // 2), 
            scale_func=lambda t: 0.7 * (1.0 - math.exp(-6.0 * (t/0.5)) * math.cos(1.5 * math.pi * (t/0.5))) if t < 0.5 else 0.7
        )
        all_clips.append(obj_clip)

        # ----------------------------------------------------
        # 2. TEXT LAYER COMPILING
        # ----------------------------------------------------
        # Render clean text badge with rounded corners
        txt_img = render_text_image(item["text"])
        txt_h, txt_w = txt_img.shape[:2]

        # Text flies in horizontally from the right side of its column
        def make_txt_pos(tx=txt_target_x, ty=cy, tw=txt_w, th=txt_h):
            return lambda t: (
                (((tx + 150) - 150 * (1.0 - math.exp(-6.0 * (t/0.5)) * math.cos(1.5 * math.pi * (t/0.5)))) if t < 0.5 else tx) - tw // 2,
                ty - th // 2
            )

        # Text bounce when narration plays (starts at t_start + 1.0s, which is t=0.5s relative to text clip)
        def make_txt_scale():
            return lambda t: (1.0 + 0.25 * math.sin(math.pi * ((t - 0.5) / 0.6))) if (0.5 <= t < 1.1) else 1.0

        # Text clip starts at t_start + 0.5s
        txt_clip = make_full_canvas_clip(
            txt_img, 
            t_start + 0.5, 
            total_duration - (t_start + 0.5), 
            pos_func=make_txt_pos(), 
            scale_func=make_txt_scale()
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
            whoosh_sfx = AudioFileClip(whoosh_path).with_start(wt - 0.1).with_effects([MultiplyVolume(0.35)])
            audio_elements.append(whoosh_sfx)

    chime_path = "assets/audio/bell_chime.wav"
    if os.path.exists(chime_path):
        for ct in chime_timings:
            chime_sfx = AudioFileClip(chime_path).with_start(ct).with_effects([MultiplyVolume(0.30)])
            audio_elements.append(chime_sfx)

    # Final Flat Composition Muxing
    layered_video = CompositeVideoClip(all_clips, size=(WIDTH, HEIGHT)).with_duration(total_duration)

    if audio_elements:
        mixed_audio = CompositeAudioClip(audio_elements).with_duration(total_duration)
        layered_video = layered_video.with_audio(mixed_audio)

    # Export configuration
    os.makedirs("line_craft", exist_ok=True)
    temp_720p = "line_craft/vocab_buildup.mp4.720p.mp4"
    final_output = "line_craft/vocab_buildup.mp4"

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
