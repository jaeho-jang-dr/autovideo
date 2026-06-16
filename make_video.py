import os
import sys
import argparse
import glob
import re
import subprocess
from tts_manager import save_tts
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, VideoFileClip
import moviepy.video.fx as fx
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

def parse_scenario(scenario_path):
    scenes = []
    if not os.path.exists(scenario_path):
        print(f"Error: Scenario path not found: {scenario_path}")
        return scenes
        
    with open(scenario_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split by scenes [Scene X]
    raw_blocks = re.split(r'\[Scene\s+(\d+)\]', content, flags=re.IGNORECASE)
    
    for i in range(1, len(raw_blocks), 2):
        scene_id = int(raw_blocks[i])
        block_text = raw_blocks[i+1]
        
        # Extract text, text_en & motion
        text_match = re.search(r'text:\s*(.*)', block_text, re.IGNORECASE)
        text_en_match = re.search(r'text_en:\s*(.*)', block_text, re.IGNORECASE)
        motion_match = re.search(r'motion:\s*(.*)', block_text, re.IGNORECASE)
        
        text = text_match.group(1).strip() if text_match else ""
        text_en = text_en_match.group(1).strip() if text_en_match else ""
        motion = motion_match.group(1).strip() if motion_match else ""
        
        scenes.append({
            "id": scene_id,
            "text": text,
            "text_en": text_en,
            "motion": motion,
            "image": f"assets/images/scene_{scene_id}.png" 
        })
    return scenes

# Text wrap helper
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

# --- SRT (soft subtitle) helpers ---------------------------------------------
def format_srt_time(sec):
    """초(float) -> SRT 타임코드 'HH:MM:SS,mmm'."""
    if sec < 0:
        sec = 0
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def write_srt(path, cues):
    """cues = [(start_sec, end_sec, text), ...] -> UTF-8(BOM 없음) SRT 저장."""
    out = []
    idx = 0
    for start, end, text in cues:
        if not text or not text.strip():
            continue
        idx += 1
        out.append(str(idx))
        out.append(f"{format_srt_time(start)} --> {format_srt_time(end)}")
        out.append(text.strip())
        out.append("")
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"Wrote {idx} subtitle cues -> {path}")

# Ken Burns Zoom Effect Helper for static images
def make_zoom(clip, duration, zoom_ratio=0.03):
    def effect(get_frame, t):
        frame = get_frame(t)
        img = Image.fromarray(frame)
        width, height = img.size
        factor = 1.0 + (zoom_ratio * t)
        new_w, new_h = int(width / factor), int(height / factor)
        left = (width - new_w) // 2
        top = (height - new_h) // 2
        right = left + new_w
        bottom = top + new_h
        img_cropped = img.crop((left, top, right, bottom))
        img_resized = img_cropped.resize((width, height), Image.Resampling.LANCZOS)
        return np.array(img_resized)
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

def apply_shake(clip, intensity=10):
    """삼각함수를 사용해 프레임을 흔들어 흔들림 효과를 적용합니다."""
    def effect(get_frame, t):
        frame = get_frame(t)
        h, w = frame.shape[:2]
        dx = int(intensity * np.sin(2 * np.pi * 8 * t))
        dy = int(intensity * np.cos(2 * np.pi * 6 * t))
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        return cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)
    return clip.transform(effect)

def apply_pulse(clip, min_alpha=0.7, frequency=2.0):
    """리드미컬하게 밝기를 변화시켜 점멸 효과를 적용합니다."""
    def effect(get_frame, t):
        frame = get_frame(t)
        factor = min_alpha + (1.0 - min_alpha) * (0.5 + 0.5 * np.sin(2 * np.pi * frequency * t))
        pulsed = np.clip(frame.astype(float) * factor, 0, 255).astype(np.uint8)
        return pulsed
    return clip.transform(effect)

def apply_staccato_rotation(clip, max_angle=5, steps_per_sec=4):
    """시간을 이산적으로 흘려 끊어지는 듯한 회전(staccato) 효과를 적용합니다."""
    def effect(get_frame, t):
        frame = get_frame(t)
        h, w = frame.shape[:2]
        qt = np.floor(t * steps_per_sec) / steps_per_sec
        angle = max_angle * np.sin(2 * np.pi * 0.5 * qt)
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        return cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)
    return clip.transform(effect)

def apply_zoom_bounce(clip, zoom_ratio=0.05):
    """씬 진입 초반에 튕기듯 줌인되었다가 완만해지는 바운스 효과를 적용합니다."""
    def effect(get_frame, t):
        frame = get_frame(t)
        img = Image.fromarray(frame)
        width, height = img.size
        if t < 1.0:
            factor = 1.0 + zoom_ratio * np.sin(np.pi * t) * np.exp(-3.0 * t)
        else:
            factor = 1.0 + (zoom_ratio * 0.1)
        new_w, new_h = int(width / factor), int(height / factor)
        left = (width - new_w) // 2
        top = (height - new_h) // 2
        right = left + new_w
        bottom = top + new_h
        img_cropped = img.crop((left, top, right, bottom))
        img_resized = img_cropped.resize((width, height), Image.Resampling.LANCZOS)
        return np.array(img_resized)
    return clip.transform(effect)

def generate_thumbnail(bg_image_path, title_text, subtitle_text, output_path):
    """Scene 0 이미지를 기반으로 규격에 맞는 한국어 썸네일을 자동 생성합니다."""
    if not os.path.exists(bg_image_path):
        print(f"Warning: Background image for thumbnail not found: {bg_image_path}")
        return
        
    try:
        img = Image.open(bg_image_path).convert("RGBA")
        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        
        font_path = r"C:\Windows\Fonts\malgunbd.ttf"
        try:
            title_font = ImageFont.truetype(font_path, 54)
            subtitle_font = ImageFont.truetype(font_path, 32)
        except IOError:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        title_h = title_bbox[3] - title_bbox[1]
        
        sub_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        sub_w = sub_bbox[2] - sub_bbox[0]
        sub_h = sub_bbox[3] - sub_bbox[1]
        
        padding_x, padding_y, gap = 45, 30, 15
        box_w = max(title_w, sub_w) + (padding_x * 2)
        box_h = title_h + sub_h + (padding_y * 2) + gap
        
        box_x1 = (1280 - box_w) // 2
        box_y1 = 60
        box_x2 = box_x1 + box_w
        box_y2 = box_y1 + box_h
        
        draw.rounded_rectangle(
            (box_x1, box_y1, box_x2, box_y2),
            radius=20,
            fill=(224, 245, 224, 215),
            outline=(46, 125, 50, 255),
            width=4
        )
        
        title_x = box_x1 + (box_w - title_w) // 2
        title_y = box_y1 + padding_y - 5
        draw.text((title_x, title_y), title_text, font=title_font, fill=(0, 0, 0, 255))
        
        sub_x = box_x1 + (box_w - sub_w) // 2
        sub_y = title_y + title_h + gap + 10
        draw.text((sub_x, sub_y), subtitle_text, font=subtitle_font, fill=(0, 0, 0, 255))
        
        final_img = img.convert("RGB")
        final_img.save(output_path, "PNG")
        print(f"SUCCESS: Auto-generated Korean thumbnail saved to {output_path}")
    except Exception as e:
        print(f"Warning: Failed to generate thumbnail: {e}")

def main():
    parser = argparse.ArgumentParser(description="Compile scene clips and narration into final video.")
    parser.add_argument("--scenario", required=True, help="Path to scenario.txt")
    parser.add_argument("--output", required=True, help="Output path (e.g. chiropractic_science/chiropractic_science.mp4)")
    parser.add_argument("--remove-watermark", action="store_true", default=True, help="Remove video watermark using OpenCV Inpainting")
    parser.add_argument("--no-remove-watermark", action="store_false", dest="remove_watermark", help="Do not remove video watermark")
    parser.add_argument("--logo-path", default="assets/drjay_ed_logo_circle.png", help="Path to channel logo overlay image")
    parser.add_argument("--intro", default="assets/intro.mp4", help="Path to intro video clip")
    parser.add_argument("--outro", default="assets/outro.mp4", help="Path to outro video clip or image")
    parser.add_argument("--outro-card", default="assets/outro_template.png", help="Path to outro static end-screen template card")
    parser.add_argument("--outro-card-duration", type=float, default=10.0, help="Duration in seconds for the outro static card")
    parser.add_argument("--annotations", default="", help="Path to annotations.json containing scene medical text overlays")
    parser.add_argument("--profile", default="", help="Path to style profile JSON file")
    parser.add_argument("--no-burn-subs", action="store_true", help="Do not burn the bottom subtitle into the video (use --srt-en/--srt-ko for toggleable CC instead)")
    parser.add_argument("--srt-en", default="", help="Path to write an English .srt subtitle (timed from text_en)")
    parser.add_argument("--srt-ko", default="", help="Path to write a Korean .srt subtitle (timed from the narration text)")
    parser.add_argument("--embed-subs", action="store_true", help="After rendering, mux en/ko SRT into the mp4 as soft (toggleable) CC tracks; auto-writes <out>.en.srt / <out>.ko.srt if --srt paths are not given")
    args = parser.parse_args()

    # Load profile if provided
    profile_data = {}
    if args.profile and os.path.exists(args.profile):
        import json
        try:
            with open(args.profile, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
            print(f"Loaded style profile from {args.profile}")
        except Exception as e:
            print(f"Error loading profile from {args.profile}: {e}")

    # Load profile dynamic settings for motion effects
    dyn_settings = profile_data.get("dynamic_settings", {})
    shake_intensity = dyn_settings.get("shake_intensity", 10)
    pulse_min_alpha = dyn_settings.get("pulse_min_alpha", 0.7)
    pulse_freq = dyn_settings.get("pulse_frequency", 2.0)
    rot_max_angle = dyn_settings.get("rotation_max_angle", 5)
    rot_steps = dyn_settings.get("rotation_steps_per_sec", 4)
    zoom_bounce_ratio = dyn_settings.get("zoom_bounce_ratio", 0.05)

    # Ensure output folders exist
    os.makedirs("assets/audio", exist_ok=True)
    
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Parse scenes
    scenes = parse_scenario(args.scenario)
    if not scenes:
        print("No scenes parsed. Exiting.")
        sys.exit(1)

    # Load annotations
    annotations = {}
    if args.annotations and os.path.exists(args.annotations):
        import json
        try:
            with open(args.annotations, "r", encoding="utf-8") as f:
                annotations = json.load(f)
            print(f"Loaded {len(annotations)} annotations for visual overlay.")
        except Exception as e:
            print(f"Error loading annotations from {args.annotations}: {e}")

    # Clean audio cache to prevent narration mismatch
    print("Clearing gTTS audio cache to force regeneration...")
    for file in glob.glob("assets/audio/scene_*.mp3"):
        try:
            os.remove(file)
        except Exception as e:
            print(f"Warning: Failed to delete audio cache {file}: {e}")

    # Load channel logo once
    logo_clip = None
    if args.logo_path and os.path.exists(args.logo_path):
        logo_img = cv2.imread(args.logo_path, cv2.IMREAD_UNCHANGED)
        if logo_img is not None and logo_img.shape[2] == 4:
            # Convert BGRA to RGBA to match MoviePy frame format
            logo_clip = cv2.cvtColor(logo_img, cv2.COLOR_BGRA2RGBA)
            print(f"Loaded logo for overlay: {args.logo_path} (Size: {logo_clip.shape})")

    clips = []
    scene_timings = []  # (text_ko, text_en, duration) in render order — for SRT export
    print("Starting video composition process...")

    for scene in scenes:
        audio_path = f"assets/audio/scene_{scene['id']}.mp3"
        
        # If this is Scene 0, automatically trigger thumbnail generation
        if scene['id'] == 0:
            print("Scene 0 (Intro) detected. Checking for thumbnail auto-generation...")
            text_ko = scene['text']
            intro_title, intro_subtitle = "", ""
            parts = re.split(r'([?!\.])', text_ko)
            if len(parts) >= 2:
                intro_title = parts[0] + parts[1]
                intro_subtitle = "".join(parts[2:]).strip()
            else:
                intro_title = text_ko
                
            if not intro_subtitle:
                intro_subtitle = "drjay-ed 채널과 함께하는 지식의 과학"
                
            # Locate background image for thumbnail
            thumb_bg = ""
            for p in [scene['image'], os.path.join(output_dir, "scene_0.png")]:
                if os.path.exists(p):
                    thumb_bg = p
                    break
            
            if thumb_bg:
                thumb_out = os.path.join(output_dir, "scene_0_thumbnail_korean.png")
                generate_thumbnail(thumb_bg, intro_title, intro_subtitle, thumb_out)
            else:
                print("Warning: scene_0.png or image file not found. Skipping thumbnail auto-generation.")
        
        # Generate TTS (한국어 나레이션 고정)
        print(f"Generating TTS for Scene {scene['id']} (ko)...")
        save_tts(scene['text'], audio_path, lang='ko')
        
        # Load audio and apply 1.1x speed MultiplySpeed
        raw_audio = AudioFileClip(audio_path)
        audio_clip = raw_audio.with_effects([fx.MultiplySpeed(1.1)])
        duration = audio_clip.duration
        
        # Clips are stored in the same folder as the output video (e.g., chiropractic_science/scene_X.mp4)
        video_path = os.path.join(output_dir, f"scene_{scene['id']}.mp4")
        if os.path.exists(video_path):
            print(f"Loading video clip for Scene {scene['id']} from {video_path}...")
            base_clip = VideoFileClip(video_path)
            
            if args.remove_watermark:
                print(f"Applying zoom-crop to remove watermark and overlaying mini logo for Scene {scene['id']}...")
                width, height = base_clip.size
                
                # 1. Dolly Zoom: Crop top-left (78% of width and height gives 998x561, exactly 16:9)
                crop_w = int(width * 0.78)
                crop_h = int(height * 0.78)
                
                # 2. Resize logo to 45x45 (25% of the original size)
                logo_size = 45
                overlay_params = None
                if logo_clip is not None:
                    resized_logo = cv2.resize(logo_clip, (logo_size, logo_size), interpolation=cv2.INTER_AREA)
                    logo_rgb = resized_logo[:, :, :3]
                    logo_alpha = resized_logo[:, :, 3:4] / 255.0
                    
                    # Align in the bottom-right corner with a 25px margin
                    margin = 25
                    ox_start = width - logo_size - margin
                    oy_start = height - logo_size - margin
                    ox_end = width - margin
                    oy_end = height - margin
                    
                    overlay_params = (ox_start, oy_start, ox_end, oy_end, logo_rgb, logo_alpha)
                
                def remove_logo_frame(frame):
                    # Step A: Crop and Upscale to push watermark completely out of frame
                    cropped = frame[0:crop_h, 0:crop_w]
                    frame_copy = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LANCZOS4)
                    
                    # Step B: Overlay Channel Logo (45x45 mini size)
                    if overlay_params is not None:
                        ox_s, oy_s, ox_e, oy_e, l_rgb, l_alpha = overlay_params
                        patch = frame_copy[oy_s:oy_e, ox_s:ox_e]
                        blended = (1.0 - l_alpha) * patch + l_alpha * l_rgb
                        frame_copy[oy_s:oy_e, ox_s:ox_e] = blended.astype(np.uint8)
                        
                    return frame_copy
                
                base_clip = base_clip.image_transform(remove_logo_frame)
                
            # Speed match video clip duration to TTS duration
            speed_factor = base_clip.duration / duration
            base_clip = base_clip.with_effects([fx.MultiplySpeed(speed_factor)]).with_duration(duration).with_audio(audio_clip)
            img_width, img_height = base_clip.size
        else:
            print(f"Fallback to static image for Scene {scene['id']}...")
            img_path = scene['image']
            fallback_path = os.path.join(output_dir, f"scene_{scene['id']}.png")
            
            target_img = ""
            if os.path.exists(img_path):
                target_img = img_path
            elif os.path.exists(fallback_path):
                target_img = fallback_path
                
            if not target_img:
                # If even the image is missing, create a black canvas
                print(f"Warning: Neither {img_path} nor {fallback_path} found. Creating placeholder.")
                img_width, img_height = 1280, 720
                # Blank black frame fallback
                base_clip = ImageClip(np.zeros((720, 1280, 3), dtype=np.uint8)).with_duration(duration).with_audio(audio_clip)
            else:
                img = Image.open(target_img)
                img_width, img_height = img.size
                base_clip = ImageClip(target_img).with_duration(duration).with_audio(audio_clip)
                base_clip = make_zoom(base_clip, duration)
        
        # Apply dynamic motion effects if tags exist in scene['motion']
        motion_str = scene.get('motion', '').lower()
        if "[shake]" in motion_str:
            print(f"Applying [shake] motion filter for Scene {scene['id']}")
            base_clip = apply_shake(base_clip, shake_intensity)
        if "[pulse]" in motion_str:
            print(f"Applying [pulse] motion filter for Scene {scene['id']}")
            base_clip = apply_pulse(base_clip, pulse_min_alpha, pulse_freq)
        if "[rotation]" in motion_str:
            print(f"Applying [rotation] motion filter for Scene {scene['id']}")
            base_clip = apply_staccato_rotation(base_clip, rot_max_angle, rot_steps)
        if "[zoom_bounce]" in motion_str:
            print(f"Applying [zoom_bounce] motion filter for Scene {scene['id']}")
            base_clip = apply_zoom_bounce(base_clip, zoom_bounce_ratio)

        # Subtitle style variables loading from profile
        sub_color = 'white'
        sub_bg = None
        sub_stroke = 'black'
        sub_stroke_w = 2
        max_chars = 60
        
        if profile_data and "subtitle_style" in profile_data:
            sub_style = profile_data["subtitle_style"]
            sub_color = sub_style.get("color", "white")
            sub_bg = sub_style.get("bg_color", None)
            sub_stroke = sub_style.get("stroke_color", "black")
            if sub_stroke == "none":
                sub_stroke = None
            sub_stroke_w = sub_style.get("stroke_width", 2)
            max_chars = sub_style.get("max_chars_per_line", 60)

        # Fonts (used by both the bottom subtitle and the Korean annotation overlay)
        font_path = r'C:\Windows\Fonts\malgun.ttf'
        font_path_bold = r'C:\Windows\Fonts\malgunbd.ttf'

        composite_elements = [base_clip]

        # Bottom subtitle (영어 자막) — burned ONLY when --no-burn-subs is not set.
        # For toggleable YouTube CC (en/ko/off) we skip burning and export SRT instead.
        if not args.no_burn_subs and scene['text_en'].strip():
            wrapped_text = wrap_text(scene['text_en'], max_chars=max_chars)
            try:
                txt_clip = TextClip(
                    text=wrapped_text,
                    font=font_path,
                    font_size=24,
                    color=sub_color,
                    bg_color=sub_bg,
                    stroke_color=sub_stroke,
                    stroke_width=sub_stroke_w,
                    method='caption',
                    size=(img_width - 120, None)
                )
            except Exception as e:
                print(f"Font loading fallback due to: {e}")
                txt_clip = TextClip(
                    text=wrapped_text,
                    font_size=24,
                    color=sub_color,
                    bg_color=sub_bg,
                    stroke_color=sub_stroke,
                    stroke_width=sub_stroke_w,
                    method='caption',
                    size=(img_width - 120, None)
                )

            # Calculate dynamic position based on text height to prevent clipping
            txt_w, txt_h = txt_clip.size
            # Align at the bottom with a 70px margin (safe zone)
            y_pos = img_height - txt_h - 70
            txt_clip = txt_clip.with_position(('center', y_pos)).with_duration(duration)
            composite_elements.append(txt_clip)

        # Check if this scene has a medical annotation overlay
        scene_annotation = annotations.get(str(scene['id']))
        
        if scene_annotation:
            print(f"Adding annotation overlay for Scene {scene['id']}: {scene_annotation}")
            ann_text = wrap_text(scene_annotation, max_chars=25)
            # Measure size first using bold font and larger size 26
            try:
                temp_clip = TextClip(
                    text=ann_text,
                    font=font_path_bold,
                    font_size=26,
                    color='#000000',  # Crisp pure black for maximum contrast
                    method='caption',
                    size=(360, None)
                )
            except Exception:
                temp_clip = TextClip(
                    text=ann_text,
                    font_size=26,
                    color='#000000',
                    method='caption',
                    size=(360, None)
                )
            ann_w, ann_h = temp_clip.size
            temp_clip.close()

            # Calculate proportional padding based on the number of lines
            num_lines = ann_text.count('\n') + 1
            text_padding_y = 12 + num_lines * 10  # 1 line: 22, 2 lines: 32, 3 lines: 42
            box_padding_y = 16 + num_lines * 12   # 1 line: 28, 2 lines: 40, 3 lines: 52
            
            # Recreate TextClip with proportional height padding to prevent Hangul bottom clipping
            try:
                ann_txt_clip = TextClip(
                    text=ann_text,
                    font=font_path_bold,
                    font_size=26,
                    color='#000000',
                    method='caption',
                    size=(ann_w, ann_h + text_padding_y)
                )
            except Exception:
                ann_txt_clip = TextClip(
                    text=ann_text,
                    font_size=26,
                    color='#000000',
                    method='caption',
                    size=(ann_w, ann_h + text_padding_y)
                )

            # Proportional padding around text (horizontal 32px, vertical based on line count)
            box_w = ann_w + 32
            box_h = ann_h + text_padding_y + box_padding_y

            box_img = np.zeros((box_h, box_w, 4), dtype=np.uint8)
            # Fill sprout green (RGBA: [224, 245, 224, 200])
            draw_rounded_rect(box_img, (1, 1), (box_w - 2, box_h - 2), [224, 245, 224, 200], -1, 10)
            # Border darker green (RGBA: [46, 125, 50, 255])
            draw_rounded_rect(box_img, (1, 1), (box_w - 2, box_h - 2), [46, 125, 50, 255], 2, 10)

            ann_bg_clip = ImageClip(box_img).with_duration(duration)
            ann_txt_clip = ann_txt_clip.with_position(('center', 'center')).with_duration(duration)

            ann_composite = CompositeVideoClip([ann_bg_clip, ann_txt_clip], size=(box_w, box_h))
            ann_composite = ann_composite.with_position((45, 45)).with_duration(duration)
            composite_elements.append(ann_composite)
            
        video_scene = CompositeVideoClip(composite_elements)
        video_scene = video_scene.with_effects([fx.CrossFadeIn(0.5)])
        
        clips.append(video_scene)
        scene_timings.append((scene['text'], scene['text_en'], duration))
        print(f"Scene {scene['id']} prepared. Duration: {duration:.2f}s")

    print("Preparing final clips assembly...")
    final_clips = []
    
    # 1. Add Intro (if exists, but skipped if Scene 0 is present in the scenario)
    intro_dur = 0.0
    has_scene_0 = any(s['id'] == 0 for s in scenes)
    
    if has_scene_0:
        print("Scene 0 is present in the scenario. Skipping separate --intro video attach.")
    else:
        if args.intro and os.path.exists(args.intro):
            print(f"Including Intro: {args.intro}")
            intro_vclip = VideoFileClip(args.intro)
            intro_dur = intro_vclip.duration
            final_clips.append(intro_vclip)
        
    # 2. Add scenes (includes Scene 0 if present)
    final_clips.extend(clips)
    
    # 3. Add Outro (if exists)
    if args.outro and os.path.exists(args.outro):
        print(f"Including Outro: {args.outro}")
        if args.outro.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            final_clips.append(VideoFileClip(args.outro))
        else:
            print(f"Outro target is an image. Building 8-second static outro with fades...")
            outro_duration = 8.0
            outro_img_clip = ImageClip(args.outro).with_duration(outro_duration)
            outro_img_clip = make_zoom(outro_img_clip, outro_duration, zoom_ratio=0.01)
            outro_clip = CompositeVideoClip([outro_img_clip])
            outro_clip = outro_clip.with_effects([fx.CrossFadeIn(0.5), fx.CrossFadeOut(0.5)])
            final_clips.append(outro_clip)

    # 4. Add Outro Card (Static End Screen for YouTube recommendations, 10 seconds silent)
    if args.outro_card and os.path.exists(args.outro_card) and args.outro_card_duration > 0:
        print(f"Including Outro Static Card: {args.outro_card} for {args.outro_card_duration}s")
        card_clip = ImageClip(args.outro_card).with_duration(args.outro_card_duration)
        card_clip = CompositeVideoClip([card_clip])
        card_clip = card_clip.with_effects([fx.CrossFadeIn(0.3)])
        final_clips.append(card_clip)

    print("Merging all scenes into final video...")
    final_video = concatenate_videoclips(final_clips, method="compose")
    cpu_cores = os.cpu_count() or 4
    print(f"Utilizing all {cpu_cores} CPU threads for compilation...")
    final_video.write_videofile(
        args.output,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=cpu_cores,
        ffmpeg_params=["-threads", str(cpu_cores)]
    )
    print(f"SUCCESS: {args.output} has been rendered successfully!")

    # --- Export toggleable subtitles (SRT) + optionally embed as soft CC tracks ---
    if args.srt_en or args.srt_ko or args.embed_subs:
        cues_ko, cues_en = [], []
        t = intro_dur
        for ko, en, dur in scene_timings:
            cues_ko.append((t, t + dur, ko))
            cues_en.append((t, t + dur, en))
            t += dur

        base, _ = os.path.splitext(args.output)
        srt_en_path = args.srt_en or (base + ".en.srt" if args.embed_subs else "")
        srt_ko_path = args.srt_ko or (base + ".ko.srt" if args.embed_subs else "")
        if srt_en_path:
            write_srt(srt_en_path, cues_en)
        if srt_ko_path:
            write_srt(srt_ko_path, cues_ko)

        if args.embed_subs:
            # Mux subtitle tracks into the mp4 as soft (mov_text) tracks, OFF by default,
            # so viewers can pick Korean / English / off (YouTube CC + VLC etc.).
            sub_inputs = []  # (iso639-2 lang, display title, path)
            if srt_ko_path and os.path.exists(srt_ko_path):
                sub_inputs.append(("kor", "한국어", srt_ko_path))
            if srt_en_path and os.path.exists(srt_en_path):
                sub_inputs.append(("eng", "English", srt_en_path))

            if sub_inputs:
                tmp_out = args.output + ".subs.mp4"
                cmd = ["ffmpeg", "-y", "-i", args.output]
                for _, _, p in sub_inputs:
                    cmd += ["-i", p]
                cmd += ["-map", "0:v", "-map", "0:a?"]
                for i in range(len(sub_inputs)):
                    cmd += ["-map", str(i + 1)]
                cmd += ["-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text"]
                for i, (lang, title, _) in enumerate(sub_inputs):
                    cmd += [f"-metadata:s:s:{i}", f"language={lang}",
                            f"-metadata:s:s:{i}", f"title={title}",
                            f"-disposition:s:{i}", "0"]
                cmd.append(tmp_out)
                print(f"Embedding soft subtitle tracks (OFF by default): {[l for l, _, _ in sub_inputs]}")
                try:
                    subprocess.run(cmd, check=True)
                    os.replace(tmp_out, args.output)
                    print(f"SUCCESS: embedded toggleable CC (ko/en/off) into {args.output}")
                except Exception as e:
                    print(f"Warning: subtitle embedding failed ({e}). Sidecar SRTs remain available.")
                    if os.path.exists(tmp_out):
                        os.remove(tmp_out)

if __name__ == "__main__":
    main()

