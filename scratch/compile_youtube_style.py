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

def generate_vignette_background():
    """Generates a beautiful light gray radial gradient (vignette) background."""
    w, h = 1280, 720
    img = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Coordinates grid
    cx, cy = w / 2, h / 2
    max_d = math.hypot(cx, cy)
    
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            # Normalised distance [0, 1]
            factor = d / max_d
            # Gradient: center #F4F4F4 (244, 244, 244) to border #D0D0D0 (208, 208, 208)
            val = 244 - (244 - 208) * factor
            img[y, x] = [int(val), int(val), int(val)]
            
    os.makedirs("scratch/layers", exist_ok=True)
    img_path = "scratch/layers/youtube_vignette.png"
    cv2.imwrite(img_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    print(f"Generated vignette background: {img_path}")

def render_dual_text_image(ko_text, en_text, font_size=24, text_color=(28, 28, 28, 255)):
    """Renders a clean multi-line text label (Korean on top, English below) with no border box."""
    font_path_ko = r'C:\Windows\Fonts\malgunbd.ttf'
    font_path_en = r'C:\Windows\Fonts\arialbd.ttf'
    try:
        font_ko = ImageFont.truetype(font_path_ko, font_size)
        font_en = ImageFont.truetype(font_path_en, int(font_size * 0.75))
    except Exception:
        font_ko = ImageFont.load_default()
        font_en = ImageFont.load_default()
        
    # Get sizes
    bbox_ko = font_ko.getbbox(ko_text)
    tw_ko = bbox_ko[2] - bbox_ko[0]
    th_ko = bbox_ko[3] - bbox_ko[1]
    
    bbox_en = font_en.getbbox(en_text)
    tw_en = bbox_en[2] - bbox_en[0]
    th_en = bbox_en[3] - bbox_en[1]
    
    w = max(tw_ko, tw_en) + 40
    line_gap = 6
    h = th_ko + th_en + line_gap + 20
    
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Center Korean text on line 1
    tx_ko = (w - tw_ko) // 2 - bbox_ko[0]
    ty_ko = 5 - bbox_ko[1]
    draw.text((tx_ko, ty_ko), ko_text, font=font_ko, fill=text_color)
    
    # Center English text on line 2
    tx_en = (w - tw_en) // 2 - bbox_en[0]
    ty_en = 5 + th_ko + line_gap - bbox_en[1]
    draw.text((tx_en, ty_en), en_text, font=font_en, fill=(100, 100, 100, 255))
    
    return np.array(img)

def make_full_canvas_clip(image_np, start_time, duration, pos_func=None, scale_func=None, pulse_func=None, fade_in_duration=None):
    """Creates a 1280x720 transparent VideoClip with dynamic placement & boundary clipping."""
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
        curr_w, curr_h = src_w, src_h
        
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
                    
        alpha_factor = 1.0
        if pulse_func:
            alpha_factor = pulse_func(t)
            
        if fade_in_duration and t < fade_in_duration:
            alpha_factor *= (t / fade_in_duration)
            
        if alpha_factor != 1.0:
            alphas = curr_img[:, :, 3].astype(float) * alpha_factor
            curr_img[:, :, 3] = np.clip(alphas, 0, 255).astype(np.uint8)
            
        # Clip composite boundaries safely
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
    print(" Compiling YouTube Stickman Style Video (20.0s)")
    print("="*60)
    
    # We have 6 vocabulary items. Total duration: 18.0s (3.0s interval)
    total_duration = 18.0
    interval = 3.0
    
    # 0. Background Vignette
    generate_vignette_background()
    bg_img = cv2.imread("scratch/layers/youtube_vignette.png", cv2.IMREAD_UNCHANGED)
    bg_img = cv2.cvtColor(bg_img, cv2.COLOR_BGRA2RGBA)
    bg_clip = ImageClip(bg_img[:, :, :3]).with_duration(total_duration)
    
    # 1. BGM Loop
    bgm_path = "assets/audio/lofi_bgm.mp3"
    audio_elements = []
    if os.path.exists(bgm_path):
        bgm = AudioFileClip(bgm_path).with_duration(total_duration).with_effects([MultiplyVolume(0.12)])
        audio_elements.append(bgm)

    # Assets & coordinates definitions
    vocab_dir = "scratch/vocab_assets"
    audio_dir = "scratch/vocab_assets/audio"
    
    # Stickman & Translation Icon are permanent assets that fade-in at the beginning
    stickman_img = cv2.imread(os.path.join(vocab_dir, "stickman.png"), cv2.IMREAD_UNCHANGED)
    stickman_img = cv2.cvtColor(stickman_img, cv2.COLOR_BGRA2RGBA)
    stickman_clip = make_full_canvas_clip(
        stickman_img, 0.0, total_duration,
        pos_func=lambda t: (640 - 75, 400 - 125), # Centred at (640, 400), stickman is 300x500 so at 0.5x scale it is 150x250
        scale_func=lambda t: 0.5, # 50% smaller
        fade_in_duration=0.6
    )
    
    trans_img = cv2.imread(os.path.join(vocab_dir, "translation_icon.png"), cv2.IMREAD_UNCHANGED)
    trans_img = cv2.cvtColor(trans_img, cv2.COLOR_BGRA2RGBA)
    trans_clip = make_full_canvas_clip(
        trans_img, 0.0, total_duration,
        pos_func=lambda t: (640 - 50, 240 - 50), # Centred at (640, 240) above head
        scale_func=lambda t: 0.5 * (1.0 + 0.08 * math.sin(math.pi * t / 2.0)), # 50% smaller with slow floating scale pulse
        fade_in_duration=0.6
    )
    
    vocab_list = [
        {"file": "window.png", "text_ko": "창문", "text_en": "WINDOW", "audio": "window.mp3", "cx": 200, "cy": 320}, 
        {"file": "fan.png", "text_ko": "선풍기", "text_en": "FAN", "audio": "fan.mp3", "cx": 420, "cy": 240},
        {"file": "bag.png", "text_ko": "가방", "text_en": "BAG", "audio": "bag.mp3", "cx": 420, "cy": 560},
        {"file": "chair.png", "text_ko": "의자", "text_en": "CHAIR", "audio": "chair.mp3", "cx": 860, "cy": 340},
        {"file": "bottle.png", "text_ko": "물병", "text_en": "BOTTLE", "audio": "bottle.mp3", "cx": 680, "cy": 580},
        {"file": "phone.png", "text_ko": "스마트폰", "text_en": "PHONE", "audio": "phone.mp3", "cx": 1080, "cy": 600}
    ]

    all_clips = [bg_clip, stickman_clip, trans_clip]
    pop_timings = []
    whoosh_timings = []
    chime_timings = []

    for i, item in enumerate(vocab_list):
        t_start = interval * i
        cx, cy = item["cx"], item["cy"]
        
        # Audio track mapping
        aud_path = os.path.join(audio_dir, item["audio"])
        if os.path.exists(aud_path):
            word_audio = AudioFileClip(aud_path).with_start(t_start + 1.0)
            audio_elements.append(word_audio)

        pop_timings.append(t_start + 0.0)
        whoosh_timings.append(t_start + 0.5)
        chime_timings.append(t_start + 1.0)

        # ----------------------------------------------------
        # 1. OBJECT LAYER ( 나타나기 - 70% 줄여 0.3x 크기로 팝업 )
        # ----------------------------------------------------
        obj_img = cv2.imread(os.path.join(vocab_dir, item["file"]), cv2.IMREAD_UNCHANGED)
        obj_img = cv2.cvtColor(obj_img, cv2.COLOR_BGRA2RGBA)
        obj_h, obj_w = obj_img.shape[:2]
        
        # Calculate target scale (0.3x instead of 0.9x -> 70% reduction)
        obj_clip = make_full_canvas_clip(
            obj_img,
            t_start,
            total_duration - t_start,
            pos_func=lambda t, target_x=cx, target_y=cy, w=obj_w, h=obj_h: (target_x - w // 2, target_y - h // 2),
            scale_func=lambda t: 0.3 * (1.0 - math.exp(-6.0 * (t/0.5)) * math.cos(1.5 * math.pi * (t/0.5))) if t < 0.5 else 0.3
        )
        all_clips.append(obj_clip)

        # ----------------------------------------------------
        # 2. DUAL LANGUAGE TEXT LABEL ( 날라오기 - 한글 발음 반듯하게 )
        # ----------------------------------------------------
        # 글자 크기는 같게 유지 (font_size=24)
        txt_img = render_dual_text_image(item["text_ko"], item["text_en"])
        txt_h, txt_w = txt_img.shape[:2]
        
        # Text label goes directly above the scaled object center
        txt_cy = cy - int((obj_h * 0.3) // 2) - (txt_h // 2) - 10
        
        # 글자는 날라온다: 오른쪽에서 왼쪽 수평 이동 날아오기 효과
        def make_txt_pos(tx=cx, ty=txt_cy, tw=txt_w, th=txt_h):
            return lambda t: (
                (((tx + 120) - 120 * (1.0 - math.exp(-6.0 * (t/0.5)) * math.cos(1.5 * math.pi * (t/0.5)))) if t < 0.5 else tx) - tw // 2,
                ty - th // 2
            )

        # Bounce highlight when narration plays (반듯한 자막 크기 강조)
        def make_txt_scale():
            return lambda t: (1.0 + 0.15 * math.sin(math.pi * ((t - 0.5) / 0.6))) if (0.5 <= t < 1.1) else 1.0

        txt_clip = make_full_canvas_clip(
            txt_img,
            t_start + 0.5,
            total_duration - (t_start + 0.5),
            pos_func=make_txt_pos(),
            scale_func=make_txt_scale()
        )
        all_clips.append(txt_clip)

    # 3. Synchronize Sound FX
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

    # Final Muxing
    layered_video = CompositeVideoClip(all_clips, size=(WIDTH, HEIGHT)).with_duration(total_duration)

    if audio_elements:
        mixed_audio = CompositeAudioClip(audio_elements).with_duration(total_duration)
        layered_video = layered_video.with_audio(mixed_audio)

    # Export & transcode
    os.makedirs("line_craft", exist_ok=True)
    temp_720p = "line_craft/vocab_youtube.mp4.720p.mp4"
    final_output = "line_craft/vocab_youtube.mp4"

    for p in [temp_720p, final_output]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

    cpu_cores = os.cpu_count() or 4
    print(f"Compiling stickman learning video (720p) utilizing {cpu_cores} threads...")
    
    layered_video.write_videofile(
        temp_720p,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=cpu_cores,
        ffmpeg_params=["-threads", str(cpu_cores)]
    )

    # 4K Upscale
    print("Upscaling to 4K (3840x2160)...")
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
        os.startfile(video_abs)

if __name__ == '__main__':
    main()
