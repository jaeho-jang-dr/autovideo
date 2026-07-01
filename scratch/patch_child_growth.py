import os
import sys
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts_manager import save_tts
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, VideoFileClip
import moviepy.video.fx as fx

# Config
SCENARIO_PATH = r"d:\Entertainments\DevEnvironment\autovideo\child_growth_science\scenario.txt"
OUTPUT_DIR = r"d:\Entertainments\DevEnvironment\autovideo\child_growth_science"
ORIGINAL_VIDEO = os.path.join(OUTPUT_DIR, "child_growth.mp4")
PATCHED_VIDEO = os.path.join(OUTPUT_DIR, "child_growth_fixed.mp4")
LOGO_PATH = r"d:\Entertainments\DevEnvironment\autovideo\assets\drjay_ed_logo_circle.png"

# Panning velocity from analyze_motion.py
VX = -0.4167
VY = -0.3906
CUT_START = 140.95
CUT_END = 149.41

# Base colors
BONE_COLOR = (255, 242, 218)      # #FFF2DA
BG_COLOR = (218, 237, 248)        # #DAEDF8
TEXT_COLOR = (44, 62, 80)         # Sleek dark slate #2C3E50

# Font paths
FONT_PATH = r"C:\Windows\Fonts\arialbd.ttf"  # Arial Bold for neat English labels
FONT_FONT = r"C:\Windows\Fonts\malgun.ttf"

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

# Motion compensated image patching per frame
def process_frame(frame, frame_idx):
    # Convert frame array to PIL Image for high-quality text rendering
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)
    
    # Calculate offset
    dx = int(VX * frame_idx)
    dy = int(VY * frame_idx)
    
    # 1. Mask incorrect texts inside bones (i=0 coords + offset)
    bone_masks = [
        (600 + dx, 275 + dy, 720 + dx, 315 + dy), # CAPITATE (top)
        (550 + dx, 325 + dy, 670 + dx, 365 + dy), # CAPITATE (mid-top)
        (580 + dx, 370 + dy, 720 + dx, 410 + dy), # SCAPHOID (mid)
        (500 + dx, 430 + dy, 630 + dx, 490 + dy), # HAMATE (left-mid)
        (580 + dx, 435 + dy, 710 + dx, 495 + dy), # LUNATE (right-mid)
        (540 + dx, 490 + dy, 670 + dx, 550 + dy), # SOAPE IUID (bottom)
    ]
    for box in bone_masks:
        # Fill with soft bone cream color
        draw.rectangle(box, fill=BONE_COLOR)
        
    # 2. Mask incorrect labels at the bottom (CARPAL BONES and confusing lines)
    bottom_box = (440 + dx, 550 + dy, 880 + dx, 720 + dy)
    draw.rectangle(bottom_box, fill=BG_COLOR)
    
    # 3. Render correct carpal bone names directly onto their positions
    # Coordinate adjustments to place labels neatly in/next to bones
    bones = [
        ("Trapezium", 660 + dx, 295 + dy, 13),
        ("Trapezoid", 610 + dx, 345 + dy, 13),
        ("Capitate", 650 + dx, 390 + dy, 13),
        ("Scaphoid", 570 + dx, 390 + dy, 13),
        ("Hamate", 645 + dx, 465 + dy, 13),
        ("Lunate", 570 + dx, 460 + dy, 13),
        ("Triquetrum", 535 + dx, 490 + dy, 12),
        ("Pisiform", 605 + dx, 520 + dy, 12),
    ]
    
    for text, x, y, size in bones:
        try:
            font = ImageFont.truetype(FONT_PATH, size)
        except Exception:
            font = ImageFont.load_default()
        
        # Calculate text width/height to center it on (x, y)
        if hasattr(draw, 'textsize'):
            w, h = draw.textsize(text, font=font)
        else:
            # Pillow 10+ fallback using textbbox
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            w = right - left
            h = bottom - top
        tx = x - w // 2
        ty = y - h // 2
        
        # Draw text with subtle shadow/border or just neat solid dark slate
        # A tiny white border around text for readability on textured bone
        for ox, oy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,-1), (0,1), (-1,0), (1,0)]:
            draw.text((tx + ox, ty + oy), text, fill=(255,255,255), font=font)
        draw.text((tx, ty), text, fill=TEXT_COLOR, font=font)
        
    return np.array(img)

def main():
    # 1. Parse Scene 18 details
    scenes = parse_scenario(SCENARIO_PATH)
    scene_18 = next((s for s in scenes if s['id'] == 18), None)
    if not scene_18:
        print("Error: Scene 18 details not found in scenario.txt")
        return
        
    print(f"Scene 18 parsed: {scene_18['text_en']}")
    
    # 2. Render Scene 18 Fixed Video
    # Load raw audio (already speed matched to 1.1x in original project)
    audio_path = os.path.join(OUTPUT_DIR, "assets", "audio", "scene_18.mp3")
    if not os.path.exists(audio_path):
        # Fallback to global assets audio
        audio_path = r"d:\Entertainments\DevEnvironment\autovideo\assets\audio\scene_18.mp3"
        
    if not os.path.exists(audio_path):
        print(f"Generating TTS for Scene 18...")
        save_tts(scene_18['text'], audio_path, lang='ko')
        
    raw_audio = AudioFileClip(audio_path)
    audio_clip = raw_audio.with_effects([fx.MultiplySpeed(1.1)])
    duration = audio_clip.duration
    
    # Load original Scene 18 video
    scene_video_path = os.path.join(OUTPUT_DIR, "scene_18.mp4")
    if not os.path.exists(scene_video_path):
        print(f"Error: scene_18.mp4 not found at {scene_video_path}")
        return
        
    print(f"Loading scene_18.mp4 from {scene_video_path}...")
    base_clip = VideoFileClip(scene_video_path)
    width, height = base_clip.size
    
    # Apply zoom-crop to remove Veo watermark
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
        
    # Apply frame-by-frame processing for masking and labeling
    # MoviePy's image_transform with a frame index counter
    frame_counter = 0
    def remove_logo_and_label_frame(frame):
        nonlocal frame_counter
        # A. Apply Motion Compensated Masking and Labeling
        processed = process_frame(frame, frame_counter)
        frame_counter += 1
        
        # B. Crop & upscale to remove Veo watermark
        cropped = processed[0:crop_h, 0:crop_w]
        frame_copy = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LANCZOS4)
        
        # C. Overlay Channel Logo
        if overlay_params is not None:
            ox_s, oy_s, ox_e, oy_e, l_rgb, l_alpha = overlay_params
            patch = frame_copy[oy_s:oy_e, ox_s:ox_e]
            blended = (1.0 - l_alpha) * patch + l_alpha * l_rgb
            frame_copy[oy_s:oy_e, ox_s:ox_e] = blended.astype(np.uint8)
            
        return frame_copy
        
    base_clip = base_clip.image_transform(remove_logo_and_label_frame)
    
    # Speed match video duration to TTS duration
    speed_factor = base_clip.duration / duration
    base_clip = base_clip.with_effects([fx.MultiplySpeed(speed_factor)]).with_audio(audio_clip)
    
    # Add subtitle
    wrapped_text = wrap_text(scene_18['text_en'], max_chars=35)
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
    
    # Check if there is an annotation in annotations.json for scene 18
    # Typically child_growth_science might have annotations.json
    annotations_path = os.path.join(OUTPUT_DIR, "annotations.json")
    composite_elements = [base_clip, txt_clip]
    
    if os.path.exists(annotations_path):
        import json
        try:
            with open(annotations_path, "r", encoding="utf-8") as f:
                annotations = json.load(f)
            scene_annotation = annotations.get("18")
            if scene_annotation:
                print(f"Adding annotation overlay for Scene 18: {scene_annotation}")
                ann_text = wrap_text(scene_annotation, max_chars=25)
                # Replicate annotation rendering from make_video.py
                try:
                    ann_txt_clip = TextClip(
                        text=ann_text,
                        font=r'C:\Windows\Fonts\malgunbd.ttf',
                        font_size=26,
                        color='#000000',
                        method='caption',
                        size=(360, None)
                    )
                except Exception:
                    ann_txt_clip = TextClip(
                        text=ann_text,
                        font_size=26,
                        color='#000000',
                        method='caption',
                        size=(360, None)
                    )
                ann_w, ann_h = ann_txt_clip.size
                ann_txt_clip.close()
                
                num_lines = ann_text.count('\n') + 1
                text_padding_y = 12 + num_lines * 10
                box_padding_y = 16 + num_lines * 12
                
                try:
                    ann_txt_clip = TextClip(
                        text=ann_text,
                        font=r'C:\Windows\Fonts\malgunbd.ttf',
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
                box_w = ann_w + 32
                box_h = ann_h + text_padding_y + box_padding_y
                box_img = np.zeros((box_h, box_w, 4), dtype=np.uint8)
                
                # Helper to draw rounded rect on RGBA image
                # Filled light green [224, 245, 224, 200]
                # Border darker green [46, 125, 50, 255]
                # Note: draw_rounded_rect expects BGR, but it works same for RGBA if color matches length
                draw_rounded_rect(box_img, (1, 1), (box_w - 2, box_h - 2), [224, 245, 224, 200], -1, 10)
                draw_rounded_rect(box_img, (1, 1), (box_w - 2, box_h - 2), [46, 125, 50, 255], 2, 10)
                
                ann_bg_clip = ImageClip(box_img).with_duration(duration)
                ann_txt_clip = ann_txt_clip.with_position(('center', 'center')).with_duration(duration)
                ann_composite = CompositeVideoClip([ann_bg_clip, ann_txt_clip], size=(box_w, box_h))
                ann_composite = ann_composite.with_position((45, 45)).with_duration(duration)
                composite_elements.append(ann_composite)
        except Exception as e:
            print(f"Warning: Failed to load annotations: {e}")
            
    video_scene = CompositeVideoClip(composite_elements)
    video_scene = video_scene.with_effects([fx.CrossFadeIn(0.5)])
    
    # Render Scene 18 fixed segment
    scene_18_fixed_path = os.path.join(OUTPUT_DIR, "scene_18_fixed.mp4")
    print(f"Rendering fixed Scene 18 to {scene_18_fixed_path}...")
    video_scene.write_videofile(
        scene_18_fixed_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=os.cpu_count() or 4
    )
    video_scene.close()
    base_clip.close()
    raw_audio.close()
    audio_clip.close()
    
    # 3. Cut Part 1 (0 to CUT_START) from the original video using ffmpeg
    part1_path = os.path.join(OUTPUT_DIR, "child_growth_part1.mp4")
    print("Slicing original video (Part 1)...")
    ffmpeg_cut_p1 = [
        "ffmpeg", "-y",
        "-ss", "0",
        "-to", str(CUT_START),
        "-i", ORIGINAL_VIDEO,
        "-c", "copy",
        part1_path
    ]
    if not run_command(ffmpeg_cut_p1):
        print("Error: Failed to cut original video part 1")
        return
        
    # 4. Cut Part 3 (CUT_END to end) from the original video using ffmpeg
    part3_path = os.path.join(OUTPUT_DIR, "child_growth_part3.mp4")
    print("Slicing original video (Part 3)...")
    ffmpeg_cut_p3 = [
        "ffmpeg", "-y",
        "-ss", str(CUT_END),
        "-i", ORIGINAL_VIDEO,
        "-c", "copy",
        part3_path
    ]
    if not run_command(ffmpeg_cut_p3):
        print("Error: Failed to cut original video part 3")
        return
        
    # 5. Join Part 1, Scene 18 Fixed, and Part 3 together
    concat_list_path = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        p1 = part1_path.replace("\\", "/")
        p2 = scene_18_fixed_path.replace("\\", "/")
        p3 = part3_path.replace("\\", "/")
        f.write(f"file '{p1}'\n")
        f.write(f"file '{p2}'\n")
        f.write(f"file '{p3}'\n")
        
    print("Splicing final video (Joining Part 1 + Fixed Scene 18 + Part 3)...")
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
            os.remove(part3_path)
            os.remove(scene_18_fixed_path)
            os.remove(concat_list_path)
            print("Temporary files cleaned up.")
        except Exception as e:
            print(f"Warning: Could not remove temporary files: {e}")
    else:
        print("\nError: 무손실 ffmpeg concat 실패. MoviePy로 최종 합성을 대체 진행합니다...")
        p1_clip = VideoFileClip(part1_path)
        p2_clip = VideoFileClip(scene_18_fixed_path)
        p3_clip = VideoFileClip(part3_path)
        final_video = concatenate_videoclips([p1_clip, p2_clip, p3_clip], method="compose")
        final_video.write_videofile(
            PATCHED_VIDEO,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=os.cpu_count() or 4
        )
        final_video.close()
        p1_clip.close()
        p2_clip.close()
        p3_clip.close()
        print(f"\nSUCCESS (Fallback): Video patched successfully. Saved to {PATCHED_VIDEO}")

if __name__ == "__main__":
    main()
