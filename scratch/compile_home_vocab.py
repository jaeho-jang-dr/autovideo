import os
import sys
import math
import cv2
import argparse
import sqlite3
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Add workspace root to sys.path so we can import tts_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
os.environ["EDGE_ACTIVE_VOICE"] = "sunhi" # Force female SunHi voice
from tts_manager import save_tts_edge_tts

from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip, VideoClip
from moviepy.audio.fx import MultiplyVolume

# Standard 1280x720 canvas
WIDTH, HEIGHT = 1280, 720
BG_COLOR = (245, 245, 240) # #F5F5F0

def get_audio_duration(path):
    if not os.path.exists(path):
        return 0.0
    try:
        ac = AudioFileClip(path)
        dur = ac.duration
        ac.close()
        return dur
    except Exception:
        return 0.0

def fetch_scenes_from_db(episode_code):
    """Queries categories, episodes, scenes, assets, and scene_objects from SQLite."""
    db_path = "channel/content.db"
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found!")
        sys.exit(1)
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Verify episode exists
    cur.execute("SELECT code FROM episodes WHERE code = ?", (episode_code,))
    if not cur.fetchone():
        print(f"Error: Episode {episode_code} not found in database!")
        conn.close()
        sys.exit(1)
        
    # Fetch scenes
    cur.execute("""
        SELECT seq, script_kr, script_en, duration_sec 
        FROM scenes 
        WHERE episode = ? 
        ORDER BY seq
    """, (episode_code,))
    scenes_rows = cur.fetchall()
    
    scenes_data = []
    for seq, script_kr, script_en, duration_sec in scenes_rows:
        # Fetch object layout for this scene
        cur.execute("""
            SELECT o.cx, o.cy, o.scale, o.z_order, o.is_point, o.motion_type, a.name_kr, a.name_en, a.type, a.file_path
            FROM scene_objects o
            JOIN assets a ON o.asset_id = a.id
            WHERE o.episode = ? AND o.scene_seq = ?
            ORDER BY o.z_order
        """, (episode_code, seq))
        objects_rows = cur.fetchall()
        
        objects_list = []
        character_file = None
        for cx, cy, scale, z_order, is_point, motion_type, name_kr, name_en, asset_type, file_path in objects_rows:
            # We assume character assets are placed under home_vocab/ as well
            if asset_type == 'character':
                character_file = file_path
            else:
                objects_list.append({
                    "file": file_path,
                    "text_ko": name_kr,
                    "text_en": name_en.upper(),
                    "cx": cx,
                    "cy": cy,
                    "scale": scale,
                    "z_order": z_order,
                    "is_point": bool(is_point),
                    "motion": motion_type
                })
                
        scenes_data.append({
            "scene_id": seq,
            "character": character_file or "character_waking_up.png",
            "narration": script_kr,
            "narration_en": script_en,
            "duration": duration_sec,
            "objects": objects_list
        })
        
    conn.close()
    return scenes_data

def generate_vocab_background():
    """Generates a beautiful warm beige (#F5F5F0) background."""
    w, h = 1280, 720
    img = np.full((h, w, 3), BG_COLOR, dtype=np.uint8)
    
    os.makedirs("home_vocab/layers", exist_ok=True)
    img_path = "home_vocab/layers/bg_f5f5f0.png"
    cv2.imwrite(img_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    return img_path

def render_dual_text_image(ko_text, en_text, font_size=28, is_point=False):
    """Renders a clean multi-line text label (Korean on top, English below) with no border box."""
    font_path_ko = r'C:\Windows\Fonts\malgunbd.ttf'
    font_path_en = r'C:\Windows\Fonts\arialbd.ttf'
    try:
        font_ko = ImageFont.truetype(font_path_ko, font_size)
        font_en = ImageFont.truetype(font_path_en, int(font_size * 0.75))
    except Exception:
        font_ko = ImageFont.load_default()
        font_en = ImageFont.load_default()
        
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
    
    # Text colors: Korean (bold black or point color), English (gray)
    text_color_ko = (143, 188, 143, 255) if is_point else (28, 28, 28, 255) # Point color = Sprout Green (#8FBC8F)
    text_color_en = (140, 140, 140, 255)
    
    # Center Korean text on line 1
    tx_ko = (w - tw_ko) // 2 - bbox_ko[0]
    ty_ko = 5 - bbox_ko[1]
    draw.text((tx_ko, ty_ko), ko_text, font=font_ko, fill=text_color_ko)
    
    # Center English text on line 2
    tx_en = (w - tw_en) // 2 - bbox_en[0]
    ty_en = 5 + th_ko + line_gap - bbox_en[1]
    draw.text((tx_en, ty_en), en_text, font=font_en, fill=text_color_en)
    
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

def render_thumbnail(output_path):
    """Generates the standard Korean thumbnail for the episode."""
    w, h = 1280, 720
    img = Image.new("RGB", (w, h), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([20, 20, w - 20, h - 20], outline=(143, 188, 143), width=10)
    
    font_path_ko = r'C:\Windows\Fonts\malgunbd.ttf'
    try:
        font_main = ImageFont.truetype(font_path_ko, 75)
        font_sub = ImageFont.truetype(font_path_ko, 40)
    except Exception:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    draw.rectangle([80, 80, 750, 180], fill=(143, 188, 143))
    draw.text((100, 95), "한글단어교실", font=font_sub, fill=(255, 255, 255))
    
    draw.text((80, 230), "집에서 편", font=font_main, fill=(28, 28, 28))
    draw.text((80, 340), "아침부터 등교까지!", font=font_sub, fill=(100, 100, 100))
    
    char_path = "home_vocab/character_waking_up.png"
    if os.path.exists(char_path):
        try:
            char_img = Image.open(char_path).convert("RGBA")
            char_img = char_img.resize((350, 350), Image.Resampling.LANCZOS)
            img.paste(char_img, (820, 180), char_img)
        except Exception as e:
            print(f"Warning embedding char in thumbnail: {e}")
            
    img.save(output_path)
    print(f"Thumbnail successfully saved to {output_path}")

def build_scene_narrations(scenes_data):
    """Pre-generates TTS files for both scene descriptions and individual words."""
    os.makedirs("home_vocab/audio", exist_ok=True)
    
    print("="*60)
    print(" Generating TTS Audio Files (Edge-TTS)...")
    print("="*60)
    
    for scene in scenes_data:
        s_id = scene["scene_id"]
        # 1. Scene narration (InJoon male voice)
        scene_audio_path = f"home_vocab/audio/scene_{s_id}_narr.mp3"
        if os.path.exists(scene_audio_path):
            os.remove(scene_audio_path)
        os.environ["EDGE_ACTIVE_VOICE"] = "injoon"
        save_tts_edge_tts(scene["narration"], scene_audio_path, lang="ko")
        print(f"Generated scene {s_id} narration (InJoon): {scene_audio_path}")
        
        # 2. Word individual pronunciations (SunHi female voice for schoolgirl Jieun)
        for i, obj in enumerate(scene["objects"]):
            word_audio_path = f"home_vocab/audio/scene_{s_id}_word_{i}.mp3"
            if os.path.exists(word_audio_path):
                os.remove(word_audio_path)
            os.environ["EDGE_ACTIVE_VOICE"] = "sunhi"
            save_tts_edge_tts(obj["text_ko"], word_audio_path, lang="ko")
            print(f"  Generated word audio for '{obj['text_ko']}' (SunHi): {word_audio_path}")
            
    print("TTS Generation Completed.")

def compile_video(scenes_data, is_publish=False):
    print("="*60)
    print(" Compiling Interactive 2D Line-Art Video")
    print("="*60)
    
    generate_vocab_background()
    bg_img = cv2.imread("home_vocab/layers/bg_f5f5f0.png", cv2.IMREAD_UNCHANGED)
    bg_img = cv2.cvtColor(bg_img, cv2.COLOR_BGRA2RGBA)
    
    pop_path = "assets/audio/pop.wav"
    whoosh_path = "assets/audio/whoosh.wav"
    chime_path = "assets/audio/bell_chime.wav"
    bgm_path = "assets/audio/lofi_bgm.mp3"
    
    scene_start_time = 0.0
    all_clips = []
    audio_elements = []
    word_cadence = 3.0
    
    for scene in scenes_data:
        s_id = scene["scene_id"]
        narr_path = f"home_vocab/audio/scene_{s_id}_narr.mp3"
        narr_dur = get_audio_duration(narr_path)
        if narr_dur <= 0:
            narr_dur = 5.0
            
        obj_count = len(scene["objects"])
        scene_duration = narr_dur + 1.0 + (obj_count * word_cadence) + 1.0
        
        scene_graphics = []
        
        # 1. Background clip (z_order = 0)
        scene_bg = ImageClip(bg_img[:, :, :3]).with_duration(scene_duration).with_start(scene_start_time)
        scene_graphics.append((0, scene_bg))
        
        # 2. Narration Audio
        narr_audio = AudioFileClip(narr_path).with_start(scene_start_time).with_effects([MultiplyVolume(1.0)])
        audio_elements.append(narr_audio)
        
        # 3. Character Layer (z_order = 2)
        char_file = f"home_vocab/{scene['character']}"
        if not os.path.exists(char_file):
            dummy = np.zeros((100, 100, 4), dtype=np.uint8)
            char_img = dummy
        else:
            char_img = cv2.imread(char_file, cv2.IMREAD_UNCHANGED)
            char_img = cv2.cvtColor(char_img, cv2.COLOR_BGRA2RGBA)
            
        char_clip = make_full_canvas_clip(
            char_img,
            scene_start_time,
            scene_duration,
            pos_func=lambda t: (300 - 75, 450 - 125),
            scale_func=lambda t: 0.5,
            fade_in_duration=0.6
        )
        scene_graphics.append((2, char_clip))
        
        # 4. Objects Layers (z_order = 3, or customized)
        obj_start_offset = narr_dur + 0.5
        
        for i, obj in enumerate(scene["objects"]):
            t_obj_start = scene_start_time + obj_start_offset + (i * word_cadence)
            cx, cy = obj["cx"], obj["cy"]
            z_val = obj.get("z_order", 3)
            
            obj_file = f"home_vocab/{obj['file']}"
            if not os.path.exists(obj_file):
                dummy = np.zeros((50, 50, 4), dtype=np.uint8)
                obj_img = dummy
            else:
                obj_img = cv2.imread(obj_file, cv2.IMREAD_UNCHANGED)
                obj_img = cv2.cvtColor(obj_img, cv2.COLOR_BGRA2RGBA)
                
            obj_h, obj_w = obj_img.shape[:2]
            
            if os.path.exists(pop_path):
                pop_sfx = AudioFileClip(pop_path).with_start(t_obj_start).with_effects([MultiplyVolume(0.40)])
                audio_elements.append(pop_sfx)
                
            obj_clip = make_full_canvas_clip(
                obj_img,
                t_obj_start,
                (scene_start_time + scene_duration) - t_obj_start,
                pos_func=lambda t, target_x=cx, target_y=cy, w=obj_w, h=obj_h: (target_x - w // 2, target_y - h // 2),
                scale_func=lambda t: 0.3 * (1.0 - math.exp(-6.0 * (t/0.5)) * math.cos(1.5 * math.pi * (t/0.5))) if t < 0.5 else 0.3
            )
            scene_graphics.append((z_val, obj_clip))
            
            # 5. Dual Language Text Label (z_order = 4)
            t_txt_start = t_obj_start + 0.5
            
            txt_img = render_dual_text_image(obj["text_ko"], obj["text_en"], is_point=obj["is_point"])
            txt_h, txt_w = txt_img.shape[:2]
            
            txt_cy = cy - int((obj_h * 0.3) // 2) - (txt_h // 2) - 10
            
            if os.path.exists(whoosh_path):
                whoosh_sfx = AudioFileClip(whoosh_path).with_start(t_txt_start - 0.1).with_effects([MultiplyVolume(0.30)])
                audio_elements.append(whoosh_sfx)
                
            def make_txt_pos(tx=cx, ty=txt_cy, tw=txt_w, th=txt_h):
                return lambda t: (
                    (((tx + 120) - 120 * (1.0 - math.exp(-6.0 * (t/0.5)) * math.cos(1.5 * math.pi * (t/0.5)))) if t < 0.5 else tx) - tw // 2,
                    ty - th // 2
                )
                
            t_word_narr = t_obj_start + 1.0
            def make_txt_scale(t_word_ref=t_word_narr, t_scene_ref=t_txt_start):
                return lambda t: (1.0 + 0.15 * math.sin(math.pi * ((t - 0.5) / 0.6))) if (0.5 <= t < 1.1) else 1.0
                
            txt_clip = make_full_canvas_clip(
                txt_img,
                t_txt_start,
                (scene_start_time + scene_duration) - t_txt_start,
                pos_func=make_txt_pos(),
                scale_func=make_txt_scale()
            )
            scene_graphics.append((4, txt_clip))
            
            if os.path.exists(chime_path):
                chime_sfx = AudioFileClip(chime_path).with_start(t_word_narr).with_effects([MultiplyVolume(0.25)])
                audio_elements.append(chime_sfx)
                
            word_audio_file = f"home_vocab/audio/scene_{s_id}_word_{i}.mp3"
            word_narr = AudioFileClip(word_audio_file).with_start(t_word_narr).with_effects([MultiplyVolume(1.0)])
            audio_elements.append(word_narr)
            
        scene_graphics.sort(key=lambda x: x[0])
        for z, clip in scene_graphics:
            all_clips.append(clip)
            
        scene_start_time += scene_duration
        
    total_video_duration = scene_start_time
    
    # 6. BGM Loop
    if os.path.exists(bgm_path):
        from moviepy.audio.fx import AudioLoop
        bgm = AudioFileClip(bgm_path).with_effects([AudioLoop(duration=total_video_duration), MultiplyVolume(0.10)])
        audio_elements.append(bgm)
        
    layered_video = CompositeVideoClip(all_clips, size=(WIDTH, HEIGHT)).with_duration(total_video_duration)
    
    if audio_elements:
        mixed_audio = CompositeAudioClip(audio_elements).with_duration(total_video_duration)
        layered_video = layered_video.with_audio(mixed_audio)
        
    os.makedirs("home_vocab", exist_ok=True)
    temp_720p = "home_vocab/home_vocab_temp_720p.mp4"
    final_4k = "home_vocab/home_vocab_4k.mp4"
    final_720p_sns = "home_vocab/home_vocab_sns_720p.mp4"
    
    for p in [temp_720p, final_4k, final_720p_sns]:
        if os.path.exists(p):
            try: os.remove(p)
            except Exception: pass
            
    cpu_cores = os.cpu_count() or 4
    print(f"Compiling draft video (720p) utilizing {cpu_cores} threads...")
    layered_video.write_videofile(
        temp_720p,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=cpu_cores,
        ffmpeg_params=["-threads", str(cpu_cores)]
    )
    
    if is_publish:
        # Publish Mode: Build 4K upscale, SNS copy and Thumbnail
        print("Publish Mode enabled. Building high quality masters...")
        
        print("Upscaling to 4K Master (3840x2160)...")
        upscale_cmd = [
            "ffmpeg", "-y",
            "-i", temp_720p,
            "-vf", "scale=3840:2160:flags=lanczos",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            final_4k
        ]
        
        print("Generating SNS 720p Low-bitrate Copy...")
        sns_cmd = [
            "ffmpeg", "-y",
            "-i", temp_720p,
            "-c:v", "libx264",
            "-preset", "fast",
            "-b:v", "1500k",
            "-maxrate", "1800k",
            "-bufsize", "3600k",
            "-c:a", "aac",
            "-b:a", "128k",
            final_720p_sns
        ]
        
        import subprocess
        try:
            subprocess.run(upscale_cmd, check=True)
            print("4K upscale completed. [OK]")
        except Exception as e:
            print(f"4K upscale failed: {e}. Reverting to 720p master.")
            shutil.copyfile(temp_720p, final_4k)
            
        try:
            subprocess.run(sns_cmd, check=True)
            print("SNS 720p copy completed. [OK]")
        except Exception as e:
            print(f"SNS copy failed: {e}. Reverting to raw 720p.")
            shutil.copyfile(temp_720p, final_720p_sns)
            
        # Generate Korean Thumbnail
        thumbnail_path = "home_vocab/home_vocab_thumbnail.png"
        render_thumbnail(thumbnail_path)
        
        # Clean up temp
        if os.path.exists(temp_720p):
            os.remove(temp_720p)
            
        print("="*60)
        print(" SUCCESS: Compilation Completed (Publish Mode)!")
        print(f"  - 4K Master: {final_4k}")
        print(f"  - SNS 720p: {final_720p_sns}")
        print(f"  - Thumbnail: {thumbnail_path}")
        print("="*60)
    else:
        # Test/Draft Mode: Keep 720p temp as the primary test video
        print("Draft Mode enabled. Keeping 720p draft only (Skipped 4K/SNS/Thumbnail).")
        shutil.copyfile(temp_720p, final_720p_sns) # Map draft to sns file path for easy check
        if os.path.exists(temp_720p):
            os.remove(temp_720p)
            
        print("="*60)
        print(" SUCCESS: Draft Compilation Completed!")
        print(f"  - Draft 720p: {final_720p_sns}")
        print("="*60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoVideo DB-driven Compiler")
    parser.add_argument("--code", default="KO-001", help="Episode code to compile")
    parser.add_argument("--publish", action="store_true", help="Compile 4K and SNS targets for release")
    args = parser.parse_args()
    
    # 1. Fetch scene layout from SQLite database
    print(f"Loading data from database for episode {args.code}...")
    scenes_data = fetch_scenes_from_db(args.code)
    
    # 2. Build TTS files
    build_scene_narrations(scenes_data)
    
    # 3. Run composition render
    compile_video(scenes_data, is_publish=args.publish)
