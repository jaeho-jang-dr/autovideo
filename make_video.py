import os
import sys
import argparse
import glob
import re
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, VideoFileClip
import moviepy.video.fx as fx
from PIL import Image
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
        
        # Extract text:
        text_match = re.search(r'text:\s*(.*)', block_text, re.IGNORECASE)
        if text_match:
            text = text_match.group(1).strip()
            scenes.append({
                "id": scene_id,
                "text": text,
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

def main():
    parser = argparse.ArgumentParser(description="Compile scene clips and narration into final video.")
    parser.add_argument("--scenario", required=True, help="Path to scenario.txt")
    parser.add_argument("--output", required=True, help="Output path (e.g. chiropractic_science/chiropractic_science.mp4)")
    parser.add_argument("--remove-watermark", action="store_true", default=True, help="Remove video watermark using OpenCV Inpainting")
    parser.add_argument("--no-remove-watermark", action="store_false", dest="remove_watermark", help="Do not remove video watermark")
    parser.add_argument("--logo-path", default="assets/drjay_ed_logo_circle.png", help="Path to channel logo overlay image")
    args = parser.parse_args()

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
    print("Starting video composition process...")

    for scene in scenes:
        audio_path = f"assets/audio/scene_{scene['id']}.mp3"
        
        # Generate TTS (Always female gTTS)
        print(f"Generating TTS for Scene {scene['id']}...")
        tts = gTTS(text=scene['text'], lang='ko')
        tts.save(audio_path)
        
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
            base_clip = base_clip.with_effects([fx.MultiplySpeed(speed_factor)]).with_audio(audio_clip)
            img_width, img_height = base_clip.size
        else:
            print(f"Fallback to static image for Scene {scene['id']}...")
            img_path = scene['image']
            if not os.path.exists(img_path):
                # If even the image is missing, create a black canvas
                print(f"Warning: Image {img_path} not found. Creating placeholder.")
                img_width, img_height = 1280, 720
                # Blank black frame fallback
                base_clip = ImageClip(np.zeros((720, 1280, 3), dtype=np.uint8)).with_duration(duration).with_audio(audio_clip)
            else:
                img = Image.open(img_path)
                img_width, img_height = img.size
                base_clip = ImageClip(img_path).with_duration(duration).with_audio(audio_clip)
                base_clip = make_zoom(base_clip, duration)
        
        # Subtitle creation
        wrapped_text = wrap_text(scene['text'], max_chars=35)
        font_path = r'C:\Windows\Fonts\malgun.ttf'
        
        try:
            txt_clip = TextClip(
                text=wrapped_text,
                font=font_path,
                font_size=24,
                color='white',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(img_width - 100, 200)
            )
        except Exception as e:
            print(f"Font loading fallback due to: {e}")
            txt_clip = TextClip(
                text=wrapped_text,
                font_size=24,
                color='white',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(img_width - 100, 200)
            )
            
        txt_clip = txt_clip.with_position(('center', img_height - 230)).with_duration(duration)
        video_scene = CompositeVideoClip([base_clip, txt_clip])
        video_scene = video_scene.with_effects([fx.CrossFadeIn(0.5)])
        
        clips.append(video_scene)
        print(f"Scene {scene['id']} prepared. Duration: {duration:.2f}s")

    print("Merging all scenes into final video...")
    final_video = concatenate_videoclips(clips, method="compose")
    final_video.write_videofile(
        args.output,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )
    print(f"SUCCESS: {args.output} has been rendered successfully!")

if __name__ == "__main__":
    main()

