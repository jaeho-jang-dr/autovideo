import os
import sys
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import asyncio
import edge_tts
from gtts import gTTS
import shutil

# Standard MoviePy 2.x imports
from moviepy import ImageClip, AudioFileClip, VideoClip, CompositeVideoClip, VideoFileClip, concatenate_videoclips, concatenate_audioclips
from moviepy.audio.fx import MultiplyVolume
from moviepy.video.fx import MultiplySpeed

# Standard 1280x720 canvas
WIDTH, HEIGHT = 1280, 720

def create_articulation_audio(first_part, second_part, filename):
    """Generates a natural-sounding Korean pronunciation using edge-tts (ko-KR-SunHiNeural)
    by concatenating an elongated first part (long vowel) and a crisp second part (short plosive/batchim)."""
    temp_dir = "scratch/temp_audio"
    os.makedirs(temp_dir, exist_ok=True)
    
    p1_temp = os.path.join(temp_dir, f"{filename}_p1.temp.mp3")
    p2_temp = os.path.join(temp_dir, f"{filename}_p2.temp.mp3")
    p1_slow = os.path.join(temp_dir, f"{filename}_p1.slow.mp3")
    p2_fast = os.path.join(temp_dir, f"{filename}_p2.fast.mp3")
    final_path = os.path.join(temp_dir, f"{filename}.mp3")
    
    # Clean old temp files
    for p in [p1_temp, p2_temp, p1_slow, p2_fast, final_path]:
        if os.path.exists(p):
            try: os.remove(p)
            except Exception: pass
            
    # Generate TTS using edge-tts (beautiful female voice: ko-KR-SunHiNeural)
    async def generate_tts(text, path):
        communicate = edge_tts.Communicate(text, "ko-KR-SunHiNeural")
        await communicate.save(path)
        
    try:
        asyncio.run(generate_tts(first_part, p1_temp))
        asyncio.run(generate_tts(second_part, p2_temp))
    except Exception as e:
        print(f"[Audio Error] Edge TTS failed: {e}. Falling back to gTTS.")
        # Fallback to gTTS
        tts1 = gTTS(text=first_part, lang="ko")
        tts1.save(p1_temp)
        tts2 = gTTS(text=second_part, lang="ko")
        tts2.save(p2_temp)
    
    # Process audio speed in MoviePy
    try:
        # P1 (long): slow down to 0.70x
        clip1 = AudioFileClip(p1_temp)
        clip1_slow = clip1.with_effects([MultiplySpeed(0.70)])
        clip1_slow.write_audiofile(p1_slow, fps=44100, logger=None)
        p1_dur = clip1_slow.duration
        clip1.close()
        clip1_slow.close()
        
        # P2 (short): speed up to 1.15x for a crisp plosive/nasal cutoff
        clip2 = AudioFileClip(p2_temp)
        clip2_fast = clip2.with_effects([MultiplySpeed(1.15)])
        clip2_fast.write_audiofile(p2_fast, fps=44100, logger=None)
        p2_dur = clip2_fast.duration
        clip2.close()
        clip2_fast.close()
        
        # Combine using MoviePy concatenate_audioclips
        c1 = AudioFileClip(p1_slow)
        c2 = AudioFileClip(p2_fast)
        combined = concatenate_audioclips([c1, c2])
        combined.write_audiofile(final_path, fps=44100, logger=None)
        
        c1.close()
        c2.close()
        combined.close()
        print(f"[Audio] Created long-short TTS: {final_path} ('{first_part}'[0.70x, {p1_dur:.2f}s] + '{second_part}'[1.15x, {p2_dur:.2f}s])")
    except Exception as e:
        print(f"[Audio Warning] Concatenation failed: {e}. Falling back to single TTS.")
        # Fallback
        tts = gTTS(text=first_part + second_part, lang="ko")
        tts.save(final_path)
        p1_dur = 1.8
        p2_dur = 0.6
        
    return final_path, p1_dur, p2_dur

def draw_bezier_points(p0, p1, p2, p3, steps=15):
    """Calculates points along a cubic Bezier curve."""
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
        points.append((x, y))
    return points

def draw_accent_arrow(draw, start_p, end_p, fill_color, outline_color):
    """Draws a premium yellow accent arrow from start_p to end_p."""
    x1, y1 = start_p
    x2, y2 = end_p
    
    angle = math.atan2(y2 - y1, x2 - x1)
    # Draw shaft
    draw.line([start_p, end_p], fill=fill_color, width=6)
    draw.line([(x1 + 3*math.sin(angle), y1 - 3*math.cos(angle)), (x2 + 3*math.sin(angle), y2 - 3*math.cos(angle))], fill=outline_color, width=1)
    draw.line([(x1 - 3*math.sin(angle), y1 + 3*math.cos(angle)), (x2 - 3*math.sin(angle), y2 + 3*math.cos(angle))], fill=outline_color, width=1)
    
    # Draw head
    head_len = 10
    head_angle = math.pi / 6 # 30 degrees
    hp1 = (x2 - head_len * math.cos(angle - head_angle), y2 - head_len * math.sin(angle - head_angle))
    hp2 = (x2 - head_len * math.cos(angle + head_angle), y2 - head_len * math.sin(angle + head_angle))
    
    draw.polygon([end_p, hp1, hp2], fill=fill_color, outline=outline_color, width=2)

def draw_dotted_line(draw, points, fill, width=2, dash_len=4, gap_len=4):
    """Draws a dotted line connecting a series of points."""
    all_pts = []
    for idx in range(len(points) - 1):
        p1 = points[idx]
        p2 = points[idx+1]
        dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
        steps = int(dist / (dash_len + gap_len))
        if steps == 0:
            all_pts.append((p1, p2))
            continue
        for s in range(steps):
            t_start = (s * (dash_len + gap_len)) / dist
            t_end = (s * (dash_len + gap_len) + dash_len) / dist
            ps = (p1[0] + t_start*(p2[0]-p1[0]), p1[1] + t_start*(p2[1]-p1[1]))
            pe = (p1[0] + t_end*(p2[0]-p1[0]), p1[1] + t_end*(p2[1]-p1[1]))
            all_pts.append((ps, pe))
            
    for ps, pe in all_pts:
        draw.line([ps, pe], fill=fill, width=width)

def get_accent_wave(t, y_center, is_vibrating=True):
    """Generates sine wave coordinates representing vocal cord vibration."""
    coords = []
    w = 60
    amplitude = 6 if is_vibrating else 0
    frequency = 0.5
    for x in range(w):
        y = y_center + int(amplitude * math.sin(frequency * x + t * 45))
        coords.append((x, y))
    return coords

def draw_rounded_rect(draw, coords, r, fill=None, outline=None, width=1):
    """Helper to draw rounded rectangle using PIL."""
    x1, y1, x2, y2 = coords
    draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=fill, outline=outline, width=width)

def make_face_profile_frame(char, t, duration, audio_start, p1_dur, p2_dur):
    """Generates the outer face side-profile line drawing dynamically."""
    width, height = 280, 280
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate jaw_drop
    jaw_drop = 0.1
    is_voicing = (audio_start <= t <= (audio_start + p1_dur + p2_dur))
    t_rel = t - audio_start if is_voicing else 0.0
    
    if is_voicing:
        if char == "ㄱ":
            if t_rel < p1_dur:
                jaw_drop = 0.15 + 0.1 * math.sin(t_rel * math.pi / p1_dur)
            else:
                t_p2 = t_rel - p1_dur
                p = t_p2 / p2_dur
                jaw_drop = 0.25 + 0.55 * math.sin(p * math.pi)
        elif char == "ㄴ":
            if t_rel < p1_dur:
                jaw_drop = 0.15
            else:
                t_p2 = t_rel - p1_dur
                p = t_p2 / p2_dur
                jaw_drop = 0.15 + 0.2 * math.sin(p * math.pi)
        elif char == "ㅁ":
            if t_rel < p1_dur:
                jaw_drop = 0.15
            else:
                t_p2 = t_rel - p1_dur
                p = t_p2 / p2_dur
                jaw_drop = 0.15 * (1.0 - math.sin(p * math.pi / 2))
    else:
        if t > (audio_start + p1_dur + p2_dur):
            if char == "ㄱ": jaw_drop = 0.2
            elif char == "ㄴ": jaw_drop = 0.15
            elif char == "ㅁ": jaw_drop = 0.0
            
    dy = int(jaw_drop * 35) # Max drop of 35 pixels
    dx = int(jaw_drop * 8)  # Shifts back slightly as it opens
    
    # Outer profile points
    # Upper head (static)
    points = [
        (50, 40), (120, 40), (135, 60), (145, 95), (180, 125), (155, 145), (167, 158), (145, 166)
    ]
    
    # Lower head (jaw drop)
    if jaw_drop < 0.02:
        lower_lip = (167, 164)
        chin_crease = (148, 195)
        chin_tip = (156, 215)
        jaw_line = (110, 235)
    else:
        lower_lip = (167 - dx//2, 164 + dy)
        chin_crease = (148 - dx, 195 + dy)
        chin_tip = (156 - dx, 215 + dy)
        jaw_line = (110 - dx, 235 + dy)
        
    lower_points = [
        lower_lip, chin_crease, chin_tip, jaw_line, (115, 270), (50, 270)
    ]
    
    all_points = points + lower_points
    
    # Fill white
    draw.polygon(all_points, fill=(255, 255, 255, 255))
    # Draw black outline
    draw.line(all_points[1:-1], fill=(28, 28, 28, 255), width=3, joint="round")
    
    # 3. Draw vertical jaw drop arrow (during "역" for ㄱ)
    if char == "ㄱ" and is_voicing and (t >= audio_start + p1_dur):
        arrow_x = 148
        arrow_y1 = 140
        arrow_y2 = 180
        accent_color = (255, 215, 0, 255)
        draw_accent_arrow(draw, (arrow_x, arrow_y1), (arrow_x, arrow_y2), accent_color, (28, 28, 28, 255))
        
    # Label
    font_sub = ImageFont.truetype(r'C:\Windows\Fonts\malgunbd.ttf', 16)
    draw.text((width // 2 - 45, height - 25), "외측 프로필", font=font_sub, fill=(100, 100, 100, 255))
    
    return np.array(img)

def make_oral_profile_frame(char, t, duration, audio_start, p1_dur, p2_dur):
    """Generates the inner oral cavity cross-section line drawing dynamically."""
    width, height = 280, 280
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    outline_color = (28, 28, 28, 255)
    accent_color = (255, 215, 0, 255)
    
    # Calculate jaw_drop
    jaw_drop = 0.1
    is_voicing = (audio_start <= t <= (audio_start + p1_dur + p2_dur))
    t_rel = t - audio_start if is_voicing else 0.0
    
    if is_voicing:
        if char == "ㄱ":
            if t_rel < p1_dur:
                jaw_drop = 0.15 + 0.1 * math.sin(t_rel * math.pi / p1_dur)
            else:
                t_p2 = t_rel - p1_dur
                p = t_p2 / p2_dur
                jaw_drop = 0.25 + 0.55 * math.sin(p * math.pi)
        elif char == "ㄴ":
            if t_rel < p1_dur:
                jaw_drop = 0.15
            else:
                t_p2 = t_rel - p1_dur
                p = t_p2 / p2_dur
                jaw_drop = 0.15 + 0.2 * math.sin(p * math.pi)
        elif char == "ㅁ":
            if t_rel < p1_dur:
                jaw_drop = 0.15
            else:
                t_p2 = t_rel - p1_dur
                p = t_p2 / p2_dur
                jaw_drop = 0.15 * (1.0 - math.sin(p * math.pi / 2))
    else:
        if t > (audio_start + p1_dur + p2_dur):
            if char == "ㄱ": jaw_drop = 0.2
            elif char == "ㄴ": jaw_drop = 0.15
            elif char == "ㅁ": jaw_drop = 0.0
            
    dy = int(jaw_drop * 20)
    dx = int(jaw_drop * 4)
    
    # Raised/lowered uvula (velum) points
    is_nasal = (char in ["ㄴ", "ㅁ"])
    if is_nasal and is_voicing and (t_rel >= p1_dur):
        uvula_points = [(140, 137), (150, 142), (155, 175), (145, 175), (138, 145)]
    else:
        uvula_points = [(140, 137), (160, 140), (165, 155), (155, 155), (142, 142)]
        
    upper_wall = [
        (40, 60), (45, 80), (35, 100), (52, 122), (48, 130),
        (52, 132), (110, 132), (140, 137)
    ] + uvula_points + [
        (165, 260), (220, 260), (220, 60)
    ]
    
    nasal_path = [
        (55, 105), (70, 85), (120, 75), (160, 95), (165, 135)
    ]
    
    upper_teeth = [(50, 130), (52, 138), (56, 130)]
    
    # Tongue bezier control points
    p0 = (56 - dx, 152 + dy)
    if is_voicing:
        if char == "ㄱ" and (t_rel >= p1_dur):
            p1 = (75 - dx, 145 + dy)
            p2 = (125, 115) # Velar touch
            p3 = (150, 200 + dy)
        elif char == "ㄴ" and (t_rel >= p1_dur):
            p1 = (55, 115) # Alveolar touch
            p2 = (100 - dx, 155 + dy)
            p3 = (140, 200 + dy)
        else:
            p1 = (70 - dx, 130 + dy)
            p2 = (110 - dx, 145 + dy)
            p3 = (140, 200 + dy)
    else:
        p1 = (70 - dx, 150 + dy)
        p2 = (110 - dx, 160 + dy)
        p3 = (140, 200 + dy)
        
    tongue_points = draw_bezier_points(p0, p1, p2, p3, steps=15)
    lower_teeth = [(50 - dx, 148 + dy), (52 - dx, 140 + dy), (56 - dx, 146 + dy)]
    
    lower_jaw_points = [
        (48 - dx, 146 + dy), # Lower lip
        (35 - dx, 200 + dy), # Chin
        (75 - dx, 250 + dy), # Jaw bottom
        (90, 260),
        (30, 260)
    ]
    
    # Render layers
    draw.polygon(upper_wall, fill=(255, 255, 255, 255))
    draw.line(upper_wall[:-3], fill=outline_color, width=3, joint="round")
    draw.line(nasal_path, fill=outline_color, width=3, joint="round")
    draw.line([(175, 137), (175, 260)], fill=outline_color, width=3)
    draw.polygon(upper_teeth, fill=(255, 255, 255, 255), outline=outline_color, width=2)
    
    lower_profile = tongue_points + [(155, 260), (30, 260)] + lower_jaw_points[::-1]
    draw.polygon(lower_profile, fill=(255, 255, 255, 255))
    
    draw.line(tongue_points, fill=outline_color, width=3, joint="round")
    draw.line(lower_jaw_points[:-1], fill=outline_color, width=3, joint="round")
    draw.polygon(lower_teeth, fill=(255, 255, 255, 255), outline=outline_color, width=2)
    
    # 4. Draw larynx wave
    larynx_x, larynx_y = 115, 220
    wave_coords = get_accent_wave(t, larynx_y, is_voicing)
    for idx in range(len(wave_coords) - 1):
        wx1, wy1 = wave_coords[idx]
        wx2, wy2 = wave_coords[idx+1]
        draw.line([(larynx_x + wx1, wy1), (larynx_x + wx2, wy2)], fill=accent_color, width=4)
        
    # Draw overlays/effects based on sound
    if is_voicing and (t_rel >= p1_dur):
        if char == "ㄱ":
            # Yellow arrow showing tongue back raising
            draw_accent_arrow(draw, (115, 175), (145, 140), accent_color, outline_color)
            # Dotted air stream line blocked at velum
            draw_dotted_line(draw, [(125, 210), (135, 170), (140, 145)], fill=outline_color, width=3)
            # Blockage yellow impact dot
            draw.ellipse([(136, 141), (144, 149)], fill=accent_color, outline=outline_color, width=2)
        elif char == "ㄴ":
            # Yellow arrow showing tongue tip rising to gums
            draw_accent_arrow(draw, (85, 170), (62, 126), accent_color, outline_color)
            # Nasal airflow dotted line
            draw_dotted_line(draw, [(125, 210), (135, 160), (145, 125), (115, 90), (60, 95)], fill=outline_color, width=3)
            # Air outflow arrow from nose
            draw_accent_arrow(draw, (60, 95), (35, 95), accent_color, outline_color)
        elif char == "ㅁ":
            # Lip contact highlight circle
            draw.ellipse([(44 - dx, 138 + dy), (54 - dx, 148 + dy)], fill=accent_color, outline=outline_color, width=2)
            # Nasal airflow dotted line
            draw_dotted_line(draw, [(125, 210), (135, 160), (145, 125), (115, 90), (60, 95)], fill=outline_color, width=3)
            # Air outflow arrow from nose
            draw_accent_arrow(draw, (60, 95), (35, 95), accent_color, outline_color)
            
    # Label
    font_sub = ImageFont.truetype(r'C:\Windows\Fonts\malgunbd.ttf', 16)
    draw.text((width // 2 - 30, height - 25), "구강 단면", font=font_sub, fill=(100, 100, 100, 255))
    
    return np.array(img)

def render_left_box(char_name, explanation, font_title, font_body):
    """Renders the left annotation box with Korean explanation text."""
    box_w, box_h = 360, 500
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    draw_rounded_rect(draw, (5, 5, box_w - 5, box_h - 5), 15, (255, 255, 255, 255), outline=(28, 28, 28, 255), width=3)
    
    draw.text((30, 30), char_name, font=font_title, fill=(28, 28, 28, 255))
    draw.line([(30, 85), (box_w - 30, 85)], fill=(120, 120, 120, 255), width=2)
    
    y_offset = 110
    for line in explanation.split("\n"):
        draw.text((30, y_offset), line, font=font_body, fill=(50, 50, 50, 255))
        y_offset += 24
        
    return np.array(img)

def render_dynamic_lineart(title):
    """Generates simple dynamic line art illustrations in B&W for all 12 cards, 
    ensuring 100% style consistency with 3px outlines."""
    card_w, card_h = 160, 160
    img = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    black = (28, 28, 28, 255)
    draw_rounded_rect(draw, (2, 2, card_w - 2, card_h - 2), 12, (255, 255, 255, 255), outline=black, width=2)
    cx, cy = card_w // 2, card_h // 2 - 10
    
    if title == "가방":
        draw_rounded_rect(draw, (cx - 28, cy - 20, cx + 28, cy + 28), 10, fill=None, outline=black, width=3)
        draw.arc([(cx - 14, cy - 30), (cx + 14, cy - 18)], start=180, end=360, fill=black, width=3)
        draw_rounded_rect(draw, (cx - 20, cy + 4, cx + 20, cy + 24), 5, fill=None, outline=black, width=2)
        draw.line([(cx - 20, cy + 4), (cx + 20, cy + 4)], fill=black, width=2)
    elif title == "공":
        draw.ellipse([(cx - 30, cy - 30), (cx + 30, cy + 30)], outline=black, width=3)
        draw.arc([(cx - 45, cy - 30), (cx + 15, cy + 30)], start=315, end=135, fill=black, width=2)
        draw.arc([(cx - 15, cy - 30), (cx + 45, cy + 30)], start=135, end=315, fill=black, width=2)
    elif title == "기차":
        draw.rectangle([(cx - 35, cy - 15), (cx + 10, cy + 20)], outline=black, width=3)
        draw.rectangle([(cx + 10, cy - 30), (cx + 30, cy + 20)], outline=black, width=3)
        draw.ellipse([(cx - 22, cy + 20), (cx - 7, cy + 35)], outline=black, width=2)
        draw.ellipse([(cx + 8, cy + 20), (cx + 23, cy + 35)], outline=black, width=2)
        draw.line([(cx - 15, cy - 25), (cx - 15, cy - 15)], fill=black, width=3)
        draw.ellipse([(cx - 20, cy - 35), (cx - 12, cy - 27)], outline=black, width=1)
        draw.ellipse([(cx - 26, cy - 43), (cx - 16, cy - 33)], outline=black, width=1)
    elif title == "강":
        draw.arc([(cx - 30, cy - 15), (cx, cy - 5)], start=0, end=180, fill=black, width=3)
        draw.arc([(cx, cy - 25), (cx + 30, cy - 15)], start=180, end=360, fill=black, width=3)
        draw.arc([(cx - 30, cy + 5), (cx, cy + 15)], start=0, end=180, fill=black, width=3)
        draw.arc([(cx, cy - 5), (cx + 30, cy + 5)], start=180, end=360, fill=black, width=3)
    elif title == "나무":
        draw.rectangle([(cx - 6, cy + 5), (cx + 6, cy + 25)], outline=black, width=3)
        draw.polygon([(cx, cy - 35), (cx - 28, cy - 10), (cx + 28, cy - 10)], outline=black, width=3)
        draw.polygon([(cx, cy - 15), (cx - 32, cy + 10), (cx + 32, cy + 10)], outline=black, width=3)
    elif title == "눈":
        draw.arc([(cx - 35, cy - 25), (cx + 35, cy + 15)], start=200, end=340, fill=black, width=3)
        draw.arc([(cx - 35, cy - 15), (cx + 35, cy + 25)], start=20, end=160, fill=black, width=3)
        draw.ellipse([(cx - 12, cy - 12), (cx + 12, cy + 12)], outline=black, width=2)
        draw.ellipse([(cx - 5, cy - 5), (cx + 5, cy + 5)], fill=black)
    elif title == "나비":
        draw.line([(cx, cy - 25), (cx, cy + 20)], fill=black, width=3)
        draw.ellipse([(cx - 28, cy - 22), (cx, cy - 2)], outline=black, width=3)
        draw.ellipse([(cx - 22, cy - 2), (cx, cy + 14)], outline=black, width=3)
        draw.ellipse([(cx, cy - 22), (cx + 28, cy - 2)], outline=black, width=3)
        draw.ellipse([(cx, cy - 2), (cx + 22, cy + 14)], outline=black, width=3)
        draw.arc([(cx - 10, cy - 35), (cx, cy - 25)], start=180, end=360, fill=black, width=2)
        draw.arc([(cx, cy - 35), (cx + 10, cy - 25)], start=180, end=360, fill=black, width=2)
    elif title == "노래":
        draw.ellipse([(cx - 20, cy + 10), (cx - 7, cy + 20)], fill=black)
        draw.ellipse([(cx + 8, cy + 10), (cx + 21, cy + 20)], fill=black)
        draw.line([(cx - 7, cy - 15), (cx - 7, cy + 15)], fill=black, width=3)
        draw.line([(cx + 21, cy - 15), (cx + 21, cy + 15)], fill=black, width=3)
        draw.polygon([(cx - 7, cy - 15), (cx + 21, cy - 15), (cx + 21, cy - 9), (cx - 7, cy - 9)], fill=black)
    elif title == "모자":
        draw.arc([(cx - 25, cy - 20), (cx + 25, cy + 10)], start=180, end=360, fill=black, width=3)
        draw.line([(cx - 38, cy + 10), (cx + 38, cy + 10)], fill=black, width=3)
        draw.rectangle([(cx - 24, cy + 4), (cx + 24, cy + 10)], fill=black)
    elif title == "물병":
        draw_rounded_rect(draw, (cx - 18, cy - 10, cx + 18, cy + 28), 6, fill=None, outline=black, width=3)
        draw.rectangle([(cx - 8, cy - 25), (cx + 8, cy - 10)], outline=black, width=3)
        draw.rectangle([(cx - 10, cy - 30), (cx + 10, cy - 25)], fill=black)
        draw.line([(cx - 15, cy + 10), (cx + 15, cy + 10)], fill=black, width=1)
    elif title == "문":
        draw.rectangle([(cx - 22, cy - 32), (cx + 22, cy + 25)], outline=black, width=3)
        draw.line([(cx, cy - 32), (cx, cy + 25)], fill=black, width=1)
        draw.ellipse([(cx + 8, cy - 3), (cx + 13, cy + 2)], fill=black)
        draw.ellipse([(cx - 13, cy - 3), (cx - 8, cy + 2)], fill=black)
    elif title == "말":
        points = [(cx - 20, cy - 20), (cx + 15, cy - 20), (cx + 22, cy - 8), (cx + 8, cy + 5), (cx + 8, cy + 25), (cx - 15, cy + 25)]
        draw.polygon(points, fill=None, outline=black, width=3)
        draw.polygon([(cx - 8, cy - 20), (cx - 14, cy - 32), (cx - 2, cy - 20)], fill=black)
        draw.ellipse([(cx - 2, cy - 12), (cx + 2, cy - 8)], fill=black)
        draw.line([(cx - 16, cy - 10), (cx - 19, cy + 15)], fill=black, width=2)
        
    font_card = ImageFont.truetype(r'C:\Windows\Fonts\malgunbd.ttf', 18)
    bbox = font_card.getbbox(title)
    tw = bbox[2] - bbox[0]
    draw.text(((card_w - tw) // 2, card_h - 35), title, font=font_card, fill=black)
    
    return np.array(img)

def composite_full_scene(char, progress, t, title_text, left_box_img, face_profile, oral_profile, vocab_cards):
    """Composites the final B&W styled video canvas frame."""
    frame = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8)
    frame[:, :] = [243, 243, 232] # BGR color for #E8F3F3 (seamless background matching screenshot)
    
    # 1. Draw left explanation box (x: 50, width: 360, y: 110)
    lh, lw = left_box_img.shape[:2]
    ly, lx = (HEIGHT - lh) // 2, 50
    left_alpha = left_box_img[:, :, 3] / 255.0
    for c in range(3):
        frame[ly:ly+lh, lx:lx+lw, c] = (1.0 - left_alpha) * frame[ly:ly+lh, lx:lx+lw, c] + left_alpha * left_box_img[:, :, c]
        
    # 2. Draw outer face profile in the center (x: 520, width: 280, y: 100)
    face_h, face_w = face_profile.shape[:2]
    ly_face, lx_face = 100, 520
    face_alpha = face_profile[:, :, 3] / 255.0
    for c in range(3):
        frame[ly_face:ly_face+face_h, lx_face:lx_face+face_w, c] = (1.0 - face_alpha) * frame[ly_face:ly_face+face_h, lx_face:lx_face+face_w, c] + face_alpha * face_profile[:, :, c]
        
    # 3. Draw inner oral cavity profile on the right (x: 880, width: 280, y: 100)
    oral_h, oral_w = oral_profile.shape[:2]
    ly_oral, lx_oral = 100, 880
    oral_alpha = oral_profile[:, :, 3] / 255.0
    for c in range(3):
        frame[ly_oral:ly_oral+oral_h, lx_oral:lx_oral+oral_w, c] = (1.0 - oral_alpha) * frame[ly_oral:ly_oral+oral_h, lx_oral:lx_oral+oral_w, c] + oral_alpha * oral_profile[:, :, c]
        
    # 4. Draw bottom vocabulary cards (4 cards laid out horizontally)
    card_positions = [
        (480, 460), # Card 1
        (670, 460), # Card 2
        (860, 460), # Card 3
        (1050, 460) # Card 4
    ]
    
    for i, card_img in enumerate(vocab_cards):
        cx_pos, cy_pos = card_positions[i]
        
        delay = i * 0.18
        if progress > delay:
            t_pop = (progress - delay) / 0.35
            if t_pop < 1.0:
                scale = 1.0 - math.exp(-6.0 * t_pop) * math.cos(1.5 * math.pi * t_pop)
            else:
                scale = 1.0
                
            ch_orig, cw_orig = card_img.shape[:2]
            ch, cw = max(1, int(ch_orig * scale)), max(1, int(cw_orig * scale))
            card_resized = cv2.resize(card_img, (cw, ch), interpolation=cv2.INTER_LANCZOS4)
            
            px = cx_pos + (cw_orig - cw) // 2
            py = cy_pos + (ch_orig - ch) // 2
            
            card_alpha = card_resized[:, :, 3] / 255.0
            
            x1, y1 = max(0, px), max(0, py)
            x2, y2 = min(WIDTH, px+cw), min(HEIGHT, py+ch)
            
            src_x1, src_y1 = x1 - px, y1 - py
            src_x2, src_y2 = src_x1 + (x2 - x1), src_y1 + (y2 - y1)
            
            if (x2 > x1) and (y2 > y1):
                part_alpha = card_alpha[src_y1:src_y2, src_x1:src_x2]
                for c in range(3):
                    frame[y1:y2, x1:x2, c] = (1.0 - part_alpha) * frame[y1:y2, x1:x2, c] + part_alpha * card_resized[src_y1:src_y2, src_x1:src_x2, c]
                    
    return frame

def main():
    print("="*60)
    print("  한글 조음 발음 다이내믹 시각화 컴파일러 ('ㄱ', 'ㄴ', 'ㅁ') - 100% 라인선화 재시공")
    print("="*60)
    
    font_p_title = r'C:\Windows\Fonts\malgunbd.ttf'
    font_p_body = r'C:\Windows\Fonts\malgun.ttf'
    try:
        font_title = ImageFont.truetype(font_p_title, 32)
        font_body = ImageFont.truetype(font_p_body, 16)
    except IOError:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        
    consonants = [
        {
            "char": "ㄱ",
            "name": "기 ~ 역 ~ (Gi-yeok)",
            "p1_tts": "기이이이이",
            "p2_tts": "역",
            "explanation": "혀뿌리를 올려 목구멍을 막고,\n공기를 모았다가 터뜨려\n소리를 냅니다.\n\n[주요 동작]\n- '기': 입술 양옆 신장 (미소)\n- '역': 턱 개방 및 공기 분출\n- 구강 단면: 설근(혀뿌리)이\n  연구개에 닿아 기류 차단 후\n  갑작스럽게 파열(release) 발생",
            "words": [("가방", ""), ("공", ""), ("기차", ""), ("강", "")]
        },
        {
            "char": "ㄴ",
            "name": "니 ~ 은 ~ (Ni-eun)",
            "p1_tts": "니이이이이",
            "p2_tts": "은",
            "explanation": "혀끝을 윗잇몸에 대어\n공기를 완전히 차단하고,\n콧구멍을 통해 기류를 방출하며\n소리를 냅니다.\n\n[주요 동작]\n- '니': 입술 양옆 신장 (미소)\n- '은': 입술 힘 빼고 중립\n- 구강 단면: 혀끝(설첨)이\n  윗잇몸(치조)에 닿아 기류 차단,\n  비강(코)으로 기류 방출",
            "words": [("나무", ""), ("눈", ""), ("나비", ""), ("노래", "")]
        },
        {
            "char": "ㅁ",
            "name": "미 ~ 음 ~ (Mi-eum)",
            "p1_tts": "미이이이이",
            "p2_tts": "음",
            "explanation": "두 입술을 가볍게 닫아\n입으로 나가는 공기를 막고,\n코로 숨을 흘려보내며\n소리를 냅니다.\n\n[주요 동작]\n- '미': 입술 양옆 신장 (미소)\n- '음': 두 입술을 수평 폐쇄\n- 구강 단면: 양순(두 입술) 접촉,\n  비강(코)으로 공기 통과",
            "words": [("모자", ""), ("물병", ""), ("문", ""), ("말", "")]
        }
    ]
    
    os.makedirs("scratch", exist_ok=True)
    os.makedirs("line_craft", exist_ok=True)
    
    # 1. Create long-short composite TTS audios
    print("\n[Step 1] 장단음 결합 TTS 오디오 생성 진행 중...")
    for item in consonants:
        item["audio_path"], item["p1_dur"], item["p2_dur"] = create_articulation_audio(
            item["p1_tts"], item["p2_tts"], f"slow_long_short_{item['char']}"
        )
        
    # 2. Composite and build video clips
    print("\n[Step 2] 100% 프로그램식 조음 드로잉 렌더링 시작...")
    clips = []
    
    for idx, item in enumerate(consonants):
        print(f"  -> 자음 '{item['char']}' 렌더링 준비 중...")
        
        # (1) Render left explanation box
        left_box = render_left_box(item["name"], item["explanation"], font_title, font_body)
        
        # (2) Render vocabulary cards dynamically (100% line drawing)
        vocab_cards = []
        for word_title, _ in item["words"]:
            vocab_cards.append(render_dynamic_lineart(word_title))
                
        # Determine duration based on TTS audio duration
        audio_clip = AudioFileClip(item["audio_path"])
        audio_start = 0.6 # Silence padding before speech
        scene_dur = audio_clip.duration + audio_start + 1.2 # Silence padding after speech
        
        # Define video frame generator
        def make_video_frame(t, char=item['char'], duration=scene_dur, start=audio_start, 
                             p1_d=item['p1_dur'], p2_d=item['p2_dur'],
                             left=left_box, cards=vocab_cards):
            progress = t / duration
            
            # Generate Profile 1: Outer face side view
            face_frame = make_face_profile_frame(char, t, duration, start, p1_d, p2_d)
            
            # Generate Profile 2: Inner oral cavity side view
            oral_frame = make_oral_profile_frame(char, t, duration, start, p1_d, p2_d)
            
            # Composite full scene
            full_frame = composite_full_scene(char, progress, t, char, left, face_frame, oral_frame, cards)
            return full_frame
            
        # Compile VideoClip and sync audio
        video_clip = VideoClip(make_video_frame, duration=scene_dur)
        synced_audio = audio_clip.with_start(audio_start)
        video_clip = video_clip.with_audio(synced_audio)
        clips.append(video_clip)
        
    # 3. Concatenate all 3 consonants scenes
    final_video = concatenate_videoclips(clips, method="compose")
    
    # 4. Render 720p output
    temp_720p = "line_craft/articulation_test.mp4.720p.mp4"
    final_output = "line_craft/articulation_test.mp4"
    
    for p in [temp_720p, final_output]:
        if os.path.exists(p):
            try: os.remove(p)
            except Exception: pass
            
    cpu_cores = os.cpu_count() or 4
    print(f"\n[Step 3] 720p 임시 비디오 컴파일 중 (스레드: {cpu_cores})...")
    final_video.write_videofile(
        temp_720p,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=cpu_cores,
        ffmpeg_params=["-threads", str(cpu_cores)]
    )
    
    # 5. Upscale to 4K using FFmpeg Lanczos-4
    print("\n[Step 4] FFmpeg Lanczos 필터 활용 4K (3840x2160) 업스케일 진행 중...")
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
        print("  -> 4K 업스케일 완료! [OK]")
        if os.path.exists(temp_720p):
            os.remove(temp_720p)
    except Exception as e:
        print(f"[Warning] FFmpeg 4K 업스케일 실패: {e}. 720p 파일로 대체합니다.")
        os.rename(temp_720p, final_output)
        
    print("="*60)
    print(f"성공: 자음 조음 학습 테스트 비디오가 재빌드되었습니다: {final_output}")
    print("="*60)
    
    # 6. Auto-play video using windows default player
    video_abs = os.path.abspath(final_output)
    if os.path.exists(video_abs):
        print("\n[Step 5] 동영상 실행 중...")
        os.startfile(video_abs)

if __name__ == '__main__':
    main()
