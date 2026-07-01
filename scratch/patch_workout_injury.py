import os
import sys
import re
import glob
import subprocess
from PIL import Image
import numpy as np
import cv2

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts_manager import save_tts
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, VideoFileClip
import moviepy.video.fx as fx

# Config
SCENARIO_PATH = r"d:\Entertainments\DevEnvironment\autovideo\workout_injury_science\scenario.txt"
OUTPUT_DIR = r"d:\Entertainments\DevEnvironment\autovideo\workout_injury_science"
ORIGINAL_VIDEO = os.path.join(OUTPUT_DIR, "workout_injury.mp4")
PATCHED_VIDEO = os.path.join(OUTPUT_DIR, "workout_injury_fixed.mp4")
LOGO_PATH = r"d:\Entertainments\DevEnvironment\autovideo\assets\drjay_ed_logo_circle.png"
OUTRO_PATH = r"d:\Entertainments\DevEnvironment\autovideo\assets\outro.mp4"

# Timeline timestamps from timeline analysis
# Scene 60 starts at 506.08s
CUT_TIMESTAMP = 506.08

def parse_scenario(scenario_path):
    scenes = []
    with open(scenario_path, "r", encoding="utf-8") as f:
        content = f.read()
    raw_blocks = re.split(r'\[Scene\s+(\d+)\]', content, flags=re.IGNORECASE)
    for i in range(1, len(raw_blocks), 2):
        scene_id = int(raw_blocks[i])
        block_text = raw_blocks[i+1]
        text_match = re.search(r'text:\s*(.*)', block_text, re.IGNORECASE)
        text_en_match = re.search(r'text_en:\s*(.*)', block_text, re.IGNORECASE)
        text = text_match.group(1).strip() if text_match else ""
        text_en = text_en_match.group(1).strip() if text_en_match else ""
        scenes.append({
            "id": scene_id,
            "text": text,
            "text_en": text_en
        })
    return scenes

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

def wrap_text(text, max_chars=35):
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

def run_command(cmd_args):
    print(f"Running: {' '.join(cmd_args)}")
    result = subprocess.run(cmd_args, capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"Error executing command: {result.stderr}")
        return False
    return True

def main():
    # 1. Parse Scene 60 details
    scenes = parse_scenario(SCENARIO_PATH)
    scene_60 = next((s for s in scenes if s['id'] == 60), None)
    if not scene_60:
        print("Error: Scene 60 details not found in scenario.txt")
        return
        
    print(f"Scene 60 parsed: {scene_60['text_en']}")
    
    # 2. Render Scene 60 Fixed Video (Zoom-crop, subtitle, logo, audio speed up)
    # Generate audio
    audio_path = os.path.join(OUTPUT_DIR, "assets", "audio", "scene_60.mp3")
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    if os.path.exists(audio_path):
        os.remove(audio_path)
    print("Generating TTS for Scene 60...")
    save_tts(scene_60['text'], audio_path, lang='ko')
    
    # Apply audio 1.1x speed
    raw_audio = AudioFileClip(audio_path)
    audio_clip = raw_audio.with_effects([fx.MultiplySpeed(1.1)])
    duration = audio_clip.duration
    
    # Load video
    scene_video_path = os.path.join(OUTPUT_DIR, "scene_60.mp4")
    if not os.path.exists(scene_video_path):
        print(f"Error: scene_60.mp4 not found at {scene_video_path}. Please generate it first.")
        return
        
    print(f"Loading scene_60.mp4 from {scene_video_path}...")
    base_clip = VideoFileClip(scene_video_path)
    width, height = base_clip.size
    
    # Apply zoom-crop and logo overlay
    crop_w = int(width * 0.78)
    crop_h = int(height * 0.78)
    
    logo_clip = None
    if os.path.exists(LOGO_PATH):
        logo_img = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)
        if logo_img is not None and logo_img.shape[2] == 4:
            logo_clip = cv2.cvtColor(logo_img, cv2.COLOR_BGRA2RGBA)
            
    logo_size = 45
    overlay_params = None
    if logo_clip is not None:
        resized_logo = cv2.resize(logo_clip, (logo_size, logo_size), interpolation=cv2.INTER_AREA)
        logo_rgb = resized_logo[:, :, :3]
        logo_alpha = resized_logo[:, :, 3:4] / 255.0
        
        margin = 25
        ox_start = width - logo_size - margin
        oy_start = height - logo_size - margin
        ox_end = width - margin
        oy_end = height - margin
        overlay_params = (ox_start, oy_start, ox_end, oy_end, logo_rgb, logo_alpha)
        
    def remove_logo_frame(frame):
        # Crop & upscale to remove Veo watermark
        cropped = frame[0:crop_h, 0:crop_w]
        frame_copy = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LANCZOS4)
        
        # Overlay Channel Logo (45x45 mini size)
        if overlay_params is not None:
            ox_s, oy_s, ox_e, oy_e, l_rgb, l_alpha = overlay_params
            patch = frame_copy[oy_s:oy_e, ox_s:ox_e]
            blended = (1.0 - l_alpha) * patch + l_alpha * l_rgb
            frame_copy[oy_s:oy_e, ox_s:ox_e] = blended.astype(np.uint8)
        return frame_copy
        
    base_clip = base_clip.image_transform(remove_logo_frame)
    
    # Speed match video duration to TTS duration
    speed_factor = base_clip.duration / duration
    base_clip = base_clip.with_effects([fx.MultiplySpeed(speed_factor)]).with_audio(audio_clip)
    
    # Add subtitle
    wrapped_text = wrap_text(scene_60['text_en'], max_chars=35)
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
            size=(width - 100, 200)
        )
    except Exception:
        txt_clip = TextClip(
            text=wrapped_text,
            font_size=24,
            color='white',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(width - 100, 200)
        )
        
    txt_clip = txt_clip.with_position(('center', height - 230)).with_duration(duration)
    
    video_scene = CompositeVideoClip([base_clip, txt_clip])
    video_scene = video_scene.with_effects([fx.CrossFadeIn(0.5)])
    
    # Render Scene 60 fixed segment
    scene_60_fixed_path = os.path.join(OUTPUT_DIR, "scene_60_fixed.mp4")
    print(f"Rendering fixed Scene 60 to {scene_60_fixed_path}...")
    video_scene.write_videofile(
        scene_60_fixed_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=os.cpu_count() or 4
    )
    video_scene.close()
    base_clip.close()
    raw_audio.close()
    audio_clip.close()
    
    # 3. Cut Part 1 (0 to CUT_TIMESTAMP) from the original video using ffmpeg
    part1_path = os.path.join(OUTPUT_DIR, "workout_injury_part1.mp4")
    print("Slicing original video (Part 1)...")
    ffmpeg_cut = [
        "ffmpeg", "-y",
        "-ss", "0",
        "-to", str(CUT_TIMESTAMP),
        "-i", ORIGINAL_VIDEO,
        "-c", "copy",
        part1_path
    ]
    if not run_command(ffmpeg_cut):
        print("Error: Failed to cut original video part 1")
        return
        
    # 4. Concat Scene 60 fixed and Outro into Part 2
    # Outro should be loaded as VideoFileClip
    print("Composing Part 2 (Scene 60 Fixed + Outro)...")
    part2_clips = []
    
    # Add Scene 60 fixed
    part2_clips.append(VideoFileClip(scene_60_fixed_path))
    
    # Add Outro
    if os.path.exists(OUTRO_PATH):
        part2_clips.append(VideoFileClip(OUTRO_PATH))
    else:
        print(f"Warning: Outro not found at {OUTRO_PATH}")
        
    part2_merged = concatenate_videoclips(part2_clips, method="compose")
    part2_path = os.path.join(OUTPUT_DIR, "workout_injury_part2.mp4")
    print(f"Rendering Part 2 to {part2_path}...")
    part2_merged.write_videofile(
        part2_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=os.cpu_count() or 4
    )
    part2_merged.close()
    for clip in part2_clips:
        clip.close()
        
    # 5. Join Part 1 and Part 2 together
    # Create concat list
    concat_list_path = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        # FFMPEG concat demuxer paths must use forward slashes or escape backslashes
        p1 = part1_path.replace("\\", "/")
        p2 = part2_path.replace("\\", "/")
        f.write(f"file '{p1}'\n")
        f.write(f"file '{p2}'\n")
        
    print("Splicing final video (Joining Part 1 + Part 2)...")
    ffmpeg_concat = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        PATCHED_VIDEO
    ]
    if run_command(ffmpeg_concat):
        print(f"\nSUCCESS: Video patched successfully. Saved to {PATCHED_VIDEO}")
        # Clean up temp files
        try:
            os.remove(part1_path)
            os.remove(part2_path)
            os.remove(scene_60_fixed_path)
            os.remove(concat_list_path)
            print("Temporary files cleaned up.")
        except Exception as e:
            print(f"Warning: Could not remove temporary files: {e}")
    else:
        print("\nError: 무손실 ffmpeg concat 실패. MoviePy로 최종 합성을 대체 진행합니다...")
        # Fallback to MoviePy concat
        part1 = VideoFileClip(part1_path)
        part2 = VideoFileClip(part2_path)
        final_video = concatenate_videoclips([part1, part2], method="compose")
        final_video.write_videofile(
            PATCHED_VIDEO,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=os.cpu_count() or 4
        )
        final_video.close()
        part1.close()
        part2.close()
        print(f"\nSUCCESS (Fallback): Video patched successfully. Saved to {PATCHED_VIDEO}")

if __name__ == "__main__":
    main()
