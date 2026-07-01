#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
compile_zolla_video.py — Zolla Stickman FlatCanvas Hangeul Vowels Video Compiler (Thrive with Darlett Style).
Reads the approved database character PNG assets directly, scaling them proportionally,
and applying safe-margin blackboard layouts with dynamic camera walking (pan & zoom).
"""
import os
import sys
import re
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import subprocess

from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip, VideoClip, concatenate_videoclips
from moviepy.audio.fx import MultiplyVolume

# Standard 1280x720 canvas (Virtual: 1440x810 for camera walking margins)
V_WIDTH, V_HEIGHT = 1440, 810
WIDTH, HEIGHT = 1280, 720

SCENARIO_FILE = "hangeul_birth_vowels/scenario_zolla.txt"
OUTPUT_FILE = "hangeul_birth_vowels/hangeul_birth_vowels_zolla.mp4"

LOGO_PATH = "assets/drjay_ed_logo_circle.png"
BGM_PATH = "assets/audio/lofi_bgm.mp3"
TTS_CACHE_DIR = "hangeul_birth_vowels/tts_cache"
os.makedirs(TTS_CACHE_DIR, exist_ok=True)

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Helper: Read image from path supporting unicode characters on Windows
def cv2_imread_unicode(path, flags=cv2.IMREAD_UNCHANGED):
    try:
        with open(path, "rb") as f:
            file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
        return cv2.imdecode(file_bytes, flags)
    except Exception as e:
        print(f"Error reading unicode path {path}: {e}")
        return None

# ----------------------------------------------------
# 2. SCENARIO PARSER
# ----------------------------------------------------
def parse_scenario(path):
    if not os.path.exists(path):
        print(f"Error: Scenario file {path} not found.")
        return []
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    scenes_raw = re.split(r"\[Scene\s+(\d+)\]", content)
    scenes = []
    
    for i in range(1, len(scenes_raw), 2):
        seq = int(scenes_raw[i])
        body = scenes_raw[i+1].strip()
        
        text_match = re.search(r"text:\s*(.*)", body)
        image_match = re.search(r"image:\s*(.*)", body)
        
        text = text_match.group(1).strip() if text_match else ""
        image_desc = image_match.group(1).strip() if image_match else ""
        
        scenes.append({
            "seq": seq,
            "text": text,
            "image": image_desc
        })
    return scenes

# ----------------------------------------------------
# 3. TTS AUDIO GENERATOR (Korean)
# ----------------------------------------------------
def generate_tts_for_scene(seq, text):
    cache_path = os.path.join(TTS_CACHE_DIR, f"scene_{seq}.mp3")
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
        return cache_path
        
    print(f"[TTS] Generating Korean audio overview for Scene {seq}...")
    try:
        cmd = [
            "edge-tts",
            "--voice", "ko-KR-SunHiNeural",
            "--text", text,
            "--write-media", cache_path
        ]
        subprocess.run(cmd, check=True)
        return cache_path
    except Exception as e:
        print(f"[TTS Error] edge-tts failed: {e}. Falling back to gTTS...")
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang="ko")
            tts.save(cache_path)
            return cache_path
        except Exception as e2:
            print(f"[TTS Critical] gTTS also failed: {e2}")
            return None

# ----------------------------------------------------
# 4. SCENE IMAGE ASSET RESOLVER
# ----------------------------------------------------
def resolve_asset_path(keyword):
    mapping = {
        "desk": "assets/graphics/obj_desk.png",
        "chair": "assets/graphics/obj_chair.png",
        "scroll": "assets/graphics/obj_haerye_scroll.png",
        "sejong": "assets/graphics/obj_sejong_frame.png",
        "blackboard": "assets/graphics/obj_blackboard.png",
        "notebook": "assets/graphics/obj_notebook.png",
        "pencil": "assets/graphics/obj_pencil.png",
        "mirror": "assets/graphics/obj_mirror.png",
        "clock": "web/public/images/objects/clock.png",
        "arrow": "assets/graphics/effect_arrow.png",
        "checkmark": "assets/graphics/effect_checkmark.png",
        "underline": "assets/graphics/effect_underline.png",
        "badge_1": "assets/graphics/badge_1.png",
        "badge_2": "assets/graphics/badge_2.png",
        "badge_3": "assets/graphics/badge_3.png",
        "ㅏ": "assets/graphics/letters/letter_ㅏ.png",
        "ㅓ": "assets/graphics/letters/letter_ㅓ.png",
        "ㅗ": "assets/graphics/letters/letter_ㅗ.png",
        "ㅜ": "assets/graphics/letters/letter_ㅜ.png",
        "ㅡ": "assets/graphics/letters/letter_ㅡ.png",
        "ㅣ": "assets/graphics/letters/letter_ㅣ.png",
        "ㅐ": "assets/graphics/letters/letter_ㅐ.png",
        "ㅔ": "assets/graphics/letters/letter_ㅔ.png",
        "ㅑ": "assets/graphics/letters/letter_ㅑ.png",
        "ㅕ": "assets/graphics/letters/letter_ㅕ.png",
        "요": "assets/graphics/letters/letter_ㅛ.png",
        "ㅛ": "assets/graphics/letters/letter_ㅛ.png",
        "유": "assets/graphics/letters/letter_ㅠ.png",
        "ㅠ": "assets/graphics/letters/letter_ㅠ.png",
        "ㄱ": "assets/graphics/letters/letter_ㄱ.png",
        "ㄴ": "assets/graphics/letters/letter_ㄴ.png",
        "아": "assets/graphics/letters/letter_아.png",
        "어": "assets/graphics/letters/letter_어.png",
        "아이": "assets/graphics/letters/letter_아.png",
        "오이": "assets/graphics/letters/letter_아.png",
        "우유": "assets/graphics/letters/letter_아.png",
        "여우": "assets/graphics/letters/letter_아.png",
    }
    keyword_lower = keyword.lower()
    for key, path in mapping.items():
        if key in keyword_lower:
            if os.path.exists(path):
                return path
    return None

def generate_wood_texture():
    wood = np.zeros((V_HEIGHT, V_WIDTH, 4), dtype=np.uint8)
    wood[:, :] = [45, 60, 80, 255] # Base brown BGR
    
    plank_h = 90
    for y in range(0, V_HEIGHT, plank_h):
        cv2.line(wood, (0, y), (V_WIDTH, y), (30, 40, 55, 255), 2, cv2.LINE_AA)
        for offset in [15, 35, 60, 75]:
            cv2.line(wood, (0, y + offset), (V_WIDTH, y + offset), (40, 53, 72, 255), 1, cv2.LINE_AA)
            
    return cv2.cvtColor(wood, cv2.COLOR_BGRA2RGBA)

# Helper: overlay transparent RGBA image over BGRA frame in OpenCV
def overlay_alpha(background_bgra, overlay_rgba, x, y):
    h_ov, w_ov = overlay_rgba.shape[:2]
    h_bg, w_bg = background_bgra.shape[:2]

    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(w_bg, x + w_ov), min(h_bg, y + h_ov)

    x1_src = x1 - x
    y1_src = y1 - y
    x2_src = x1_src + (x2 - x1)
    y2_src = y1_src + (y2 - y1)

    if x2 > x1 and y2 > y1:
        overlay_crop = overlay_rgba[y1_src:y2_src, x1_src:x2_src]
        bg_crop = background_bgra[y1:y2, x1:x2]
        
        alpha = (overlay_crop[:, :, 3] / 255.0)[:, :, np.newaxis]
        overlay_rgb = overlay_crop[:, :, :3]
        
        background_bgra[y1:y2, x1:x2, :3] = (alpha * overlay_rgb + (1.0 - alpha) * bg_crop[:, :, :3]).astype(np.uint8)

# ----------------------------------------------------
# 5. UNIFIED LAYERED FRAME SYNTHESIZER
# ----------------------------------------------------
def build_scene_clip(scene, default_duration=8.0):
    seq = scene["seq"]
    text = scene["text"]
    image_desc = scene["image"]
    
    tts_path = generate_tts_for_scene(seq, text)
    if tts_path:
        tts_audio = AudioFileClip(tts_path)
        duration = tts_audio.duration + 2.0  # Narration pacing buffer
    else:
        tts_audio = None
        duration = default_duration

    # Blackboard safe-margin layer
    bb_path = "assets/graphics/obj_blackboard.png"
    bb_w, bb_h = 1200, 620
    bb_x, bb_y = (V_WIDTH - bb_w) // 2, (V_HEIGHT - bb_h) // 2
    if os.path.exists(bb_path):
        bb_img = cv2_imread_unicode(bb_path, cv2.IMREAD_UNCHANGED)
        bb_img = cv2.resize(bb_img, (bb_w, bb_h))
        bb_img = cv2.cvtColor(bb_img, cv2.COLOR_BGRA2RGBA)
    else:
        bb_img = np.zeros((bb_h, bb_w, 4), dtype=np.uint8)
        bb_img[:, :] = [30, 45, 35, 255]

    desk_path = resolve_asset_path("desk") if "desk" in image_desc.lower() else None
    chair_path = resolve_asset_path("chair") if "chair" in image_desc.lower() else None
    scroll_path = resolve_asset_path("scroll") if "scroll" in image_desc.lower() else None
    sejong_path = resolve_asset_path("sejong") if "sejong" in image_desc.lower() else None
    clock_path = resolve_asset_path("clock") if ("clock" in image_desc.lower() or "시계" in image_desc) else None
    
    # Letters
    letter_keywords = ["ㅏ", "ㅓ", "ㅗ", "ㅜ", "ㅡ", "ㅣ", "ㅐ", "ㅔ", "ㅑ", "ㅕ", "요", "ㅛ", "유", "ㅠ", "ㄱ", "ㄴ", "아", "어", "오", "우", "아이", "오이", "우유", "여우", "퐁당퐁당", "풍덩풍덩"]
    detected_letters = [lk for lk in letter_keywords if lk in image_desc]
    cleaned_letters = []
    for lk in sorted(detected_letters, key=len, reverse=True):
        if not any(lk in existing for existing in cleaned_letters):
            cleaned_letters.append(lk)
    letters_list = [(lk, resolve_asset_path(lk)) for lk in cleaned_letters if resolve_asset_path(lk)]

    underline_path = resolve_asset_path("underline") if "underline" in image_desc.lower() else None
    arrow_path = resolve_asset_path("arrow") if "arrow" in image_desc.lower() else None
    checkmark_path = resolve_asset_path("checkmark") if "checkmark" in image_desc.lower() else None
    badge_path = None
    for b in ["badge_1", "badge_2", "badge_3"]:
        if b in image_desc.lower():
            badge_path = resolve_asset_path(b)
            break

    wood_bg = generate_wood_texture()

    def make_frame(t):
        frame = wood_bg.copy()
        frame_cv = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGRA)
        
        # Render Blackboard with proper Alpha compositing (No black solid box)
        overlay_alpha(frame_cv, bb_img, bb_x, bb_y)

        # Helper scale anims with safety clamp
        def elastic_scale(t_val, base=1.0):
            if t_val < 0.6:
                ratio = t_val / 0.6
                val = 1.0 - math.exp(-6.0 * ratio) * math.cos(1.5 * math.pi * ratio)
                return max(0.001, base * val)
            return base

        def pulse_scale(t_val, base=1.0):
            if t_val < 0.6:
                return elastic_scale(t_val, base)
            pulse = 0.04 * math.sin(2.0 * math.pi * (t_val - 0.6) / 1.5)
            return max(0.001, base * (1.0 + pulse))

        # Overlay Decos
        # 1. Sejong Frame
        if sejong_path:
            sj = cv2_imread_unicode(sejong_path, cv2.IMREAD_UNCHANGED)
            if sj is not None:
                sc = elastic_scale(t, 0.4)
                if sc > 0.001:
                    sj_resized = cv2.resize(sj, (0,0), fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4)
                    sh, sw = sj_resized.shape[:2]
                    sx, sy = 1200 - sw // 2, 220 - sh // 2
                    overlay_alpha(frame_cv, sj_resized, sx, sy)

        # 2. Haerye Scroll
        if scroll_path:
            sc_img = cv2_imread_unicode(scroll_path, cv2.IMREAD_UNCHANGED)
            if sc_img is not None:
                sc = elastic_scale(t, 0.45)
                if sc > 0.001:
                    sc_resized = cv2.resize(sc_img, (0,0), fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4)
                    sh, sw = sc_resized.shape[:2]
                    sx, sy = 240 - sw // 2, 280 - sh // 2
                    overlay_alpha(frame_cv, sc_resized, sx, sy)

        # 3. Clock
        if clock_path:
            clk = cv2_imread_unicode(clock_path, cv2.IMREAD_UNCHANGED)
            if clk is not None:
                shake_y = int(2.0 * math.sin(2.0 * math.pi * t / 0.5))
                rot_ang = 3.0 * math.sin(2.0 * math.pi * t / 1.0)
                sc = elastic_scale(t, 0.35)
                if sc > 0.001:
                    clk_res = cv2.resize(clk, (0,0), fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4)
                    ch, cw = clk_res.shape[:2]
                    M = cv2.getRotationMatrix2D((cw//2, ch//2), rot_ang, 1.0)
                    clk_rot = cv2.warpAffine(clk_res, M, (cw, ch), borderMode=cv2.BORDER_TRANSPARENT)
                    sx, sy = 720 - cw // 2, 175 + shake_y - ch // 2
                    overlay_alpha(frame_cv, clk_rot, sx, sy)

        # 4. Chair
        if chair_path:
            ch_img = cv2_imread_unicode(chair_path, cv2.IMREAD_UNCHANGED)
            if ch_img is not None:
                sc = elastic_scale(t, 0.6)
                if sc > 0.001:
                    ch_res = cv2.resize(ch_img, (0,0), fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4)
                    h, w = ch_res.shape[:2]
                    overlay_alpha(frame_cv, ch_res, 620 - w // 2, 595 - h // 2)

        # 5. Desk
        if desk_path:
            dk_img = cv2_imread_unicode(desk_path, cv2.IMREAD_UNCHANGED)
            if dk_img is not None:
                sc = elastic_scale(t, 0.65)
                if sc > 0.001:
                    dk_res = cv2.resize(dk_img, (0,0), fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4)
                    h, w = dk_res.shape[:2]
                    overlay_alpha(frame_cv, dk_res, 740 - w // 2, 625 - h // 2)

        # 6. Load approved database character assets (PNG) directly
        # Determine front vs side based on scenario keywords
        char_filename = "jay_base_front.png"
        if "studying" in image_desc.lower() or "thinking" in image_desc.lower() or "side" in image_desc.lower() or "profile" in image_desc.lower():
            char_filename = "jay_base_side.png"
            
        char_path = os.path.join("web/public/images/characters", char_filename)
        char_img = cv2_imread_unicode(char_path, cv2.IMREAD_UNCHANGED)
        
        if char_img is not None:
            # Scale down to an elegant proportional size (0.45 height factor of blackboard)
            sc = 0.45
            char_res = cv2.resize(char_img, (0,0), fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4)
            ch, cw = char_res.shape[:2]
            
            # Breathing motion (up/down oscillation)
            shake_y = int(3.0 * math.sin(2.0 * math.pi * t / 2.5))
            
            # Safe blackboard layout coordinates (no overlap)
            cx, cy = 350, 480
            if "studying" in image_desc.lower():
                cx, cy = 600, 490
            elif "right" in image_desc.lower():
                cx, cy = 1080, 480
            elif "left" in image_desc.lower():
                cx, cy = 350, 480
                
            overlay_alpha(frame_cv, char_res, cx - cw // 2, cy + shake_y - ch // 2)

        # 7. Letters / Words
        N = len(letters_list)
        center_x, center_y = 800, 340
        if N > 0:
            spacing = 130
            start_x = center_x - (N - 1) * spacing // 2
            for idx, (lk, path) in enumerate(letters_list):
                if path:
                    img_let = cv2_imread_unicode(path, cv2.IMREAD_UNCHANGED)
                    if img_let is not None:
                        if idx % 4 == 0:
                            dx, dy = -450, -300
                        elif idx % 4 == 1:
                            dx, dy = 450, -300
                        elif idx % 4 == 2:
                            dx, dy = -450, 300
                        else:
                            dx, dy = 450, 300
                            
                        progress = min(1.0, t / 1.2)
                        ease = (1.0 - progress) ** 3
                        pos_x = int(start_x + idx * spacing + dx * ease)
                        pos_y = int(center_y + dy * ease)
                        
                        s_factor = pulse_scale(t, 1.2 if N==1 else 1.0)
                        if s_factor > 0.001:
                            let_res = cv2.resize(img_let, (0,0), fx=s_factor, fy=s_factor, interpolation=cv2.INTER_LANCZOS4)
                            lh, lw = let_res.shape[:2]
                            overlay_alpha(frame_cv, let_res, pos_x - lw // 2, pos_y - lh // 2)

        # 8. Effects
        if underline_path:
            ul = cv2_imread_unicode(underline_path, cv2.IMREAD_UNCHANGED)
            if ul is not None:
                sc = pulse_scale(t, 0.8)
                if sc > 0.001:
                    ul_res = cv2.resize(ul, (0,0), fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4)
                    h, w = ul_res.shape[:2]
                    overlay_alpha(frame_cv, ul_res, center_x - w // 2, (center_y + 80) - h // 2)

        if arrow_path:
            ar = cv2_imread_unicode(arrow_path, cv2.IMREAD_UNCHANGED)
            if ar is not None:
                sc = pulse_scale(t, 0.6)
                if sc > 0.001:
                    ar_res = cv2.resize(ar, (0,0), fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4)
                    h, w = ar_res.shape[:2]
                    overlay_alpha(frame_cv, ar_res, (center_x - 180) - w // 2, center_y - h // 2)

        if checkmark_path:
            ck = cv2_imread_unicode(checkmark_path, cv2.IMREAD_UNCHANGED)
            if ck is not None:
                sc = pulse_scale(t, 0.7)
                if sc > 0.001:
                    ck_res = cv2.resize(ck, (0,0), fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4)
                    h, w = ck_res.shape[:2]
                    overlay_alpha(frame_cv, ck_res, (center_x + 90) - w // 2, (center_y - 70) - h // 2)

        if badge_path:
            bdg = cv2_imread_unicode(badge_path, cv2.IMREAD_UNCHANGED)
            if bdg is not None:
                sc = pulse_scale(t, 0.7)
                if sc > 0.001:
                    bdg_res = cv2.resize(bdg, (0,0), fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4)
                    h, w = bdg_res.shape[:2]
                    overlay_alpha(frame_cv, bdg_res, 1020 - w // 2, 230 - h // 2)

        frame_rgba = cv2.cvtColor(frame_cv, cv2.COLOR_BGRA2RGBA)

        # 4) VIRTUAL CAMERA WALKING
        zoom = 1.0
        if t < 1.5:
            zoom = 1.0 + 0.07 * (1.0 - math.cos(math.pi * t / 1.5)) / 2.0
        elif t < duration - 1.5:
            zoom = 1.07 + 0.005 * math.sin(2.0 * math.pi * t / 2.0)
        else:
            rem_t = duration - t
            zoom = 1.0 + 0.07 * (1.0 - math.cos(math.pi * rem_t / 1.5)) / 2.0

        cam_cx, cam_cy = V_WIDTH // 2, V_HEIGHT // 2
        if t < 1.5:
            r = t / 1.5
            ease_r = (1.0 - math.cos(r * math.pi)) / 2.0
            cam_cx = int(V_WIDTH // 2 + (800 - V_WIDTH // 2) * 0.4 * ease_r)
            cam_cy = int(V_HEIGHT // 2 + (380 - V_HEIGHT // 2) * 0.4 * ease_r)
        elif t < duration - 1.5:
            drift_x = int(5.0 * math.sin(2.0 * math.pi * t / 3.0))
            drift_y = int(3.0 * math.cos(2.0 * math.pi * t / 4.0))
            cam_cx = int(V_WIDTH // 2 + (800 - V_WIDTH // 2) * 0.4) + drift_x
            cam_cy = int(V_HEIGHT // 2 + (380 - V_HEIGHT // 2) * 0.4) + drift_y
        else:
            rem_t = duration - t
            r = rem_t / 1.5
            ease_r = (1.0 - math.cos(r * math.pi)) / 2.0
            cam_cx = int(V_WIDTH // 2 + (800 - V_WIDTH // 2) * 0.4 * ease_r)
            cam_cy = int(V_HEIGHT // 2 + (380 - V_HEIGHT // 2) * 0.4 * ease_r)

        crop_w = int(V_WIDTH / zoom)
        crop_h = int(V_HEIGHT / zoom)
        
        x1 = max(0, cam_cx - crop_w // 2)
        y1 = max(0, cam_cy - crop_h // 2)
        x2 = min(V_WIDTH, x1 + crop_w)
        y2 = min(V_HEIGHT, y1 + crop_h)
        
        if x2 - x1 < crop_w:
            x1 = max(0, x2 - crop_w)
        if y2 - y1 < crop_h:
            y1 = max(0, y2 - crop_h)

        cropped = frame_rgba[y1:y2, x1:x2]
        final_frame = cv2.resize(cropped, (WIDTH, HEIGHT), interpolation=cv2.INTER_LANCZOS4)
        return final_frame

    return VideoClip(make_frame, duration=duration).with_start(0.0)

# ----------------------------------------------------
# 6. MAIN PIPELINE
# ----------------------------------------------------
def main():
    print("=" * 64)
    print("  Zolla Stickman FlatCanvas Hangeul Vowels Video Compilation Pipeline")
    print("  Reverse-engineered Thrive with Darlett Style")
    print("=" * 64)
    
    scenes = parse_scenario(SCENARIO_FILE)
    if not scenes:
        print("[Abort] No scenes found to compile.")
        sys.exit(1)
        
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke-test", action="store_true", help="Compile only first 2 scenes for validation")
    ap.add_argument("--upscale", action="store_true", help="Enable 4K upscaling via optimized ffmpeg Lanczos filter")
    args = ap.parse_args()
    
    if args.smoke_test:
        print("[Smoke Test] Limiting compile to first 2 scenes...")
        scenes = scenes[:2]
        
    scene_clips = []
    print(f"Building {len(scenes)} FlatCanvas scenes...")
    for idx, scene in enumerate(scenes):
        print(f" -> Compiling Scene {scene['seq']} / {len(scenes)}...")
        clip = build_scene_clip(scene)
        scene_clips.append(clip)
        
    print("\nConcatenating all scene clips into one timeline...")
    final_video = concatenate_videoclips(scene_clips, method="compose")
    
    if os.path.exists(BGM_PATH):
        print(f"Applying BGM loop: {BGM_PATH}...")
        bgm_clip = AudioFileClip(BGM_PATH)
        if bgm_clip.duration < final_video.duration:
            loops = int(math.ceil(final_video.duration / bgm_clip.duration))
            bgm_clips = []
            for i in range(loops):
                t_start = i * bgm_clip.duration
                bgm_clips.append(bgm_clip.with_start(t_start))
            bgm_full = CompositeAudioClip(bgm_clips).with_duration(final_video.duration)
        else:
            bgm_full = bgm_clip.with_duration(final_video.duration)
            
        bgm_full = bgm_full.with_effects([MultiplyVolume(0.08)])
        if final_video.audio:
            final_video.audio = CompositeAudioClip([final_video.audio, bgm_full])
        else:
            final_video.audio = bgm_full

    subtitle_clips = []
    current_time = 0.0
    for scene in scenes:
        seq = scene["seq"]
        text = scene["text"]
        clip_duration = scene_clips[seq - 1].duration if seq <= len(scene_clips) else 8.0
        
        try:
            sub_txt = text
            words = sub_txt.split(" ")
            lines = []
            cur_line = []
            for w in words:
                cur_line.append(w)
                if len(" ".join(cur_line)) > 30:
                    lines.append(" ".join(cur_line))
                    cur_line = []
            if cur_line:
                lines.append(" ".join(cur_line))
            sub_formatted = "\n".join(lines)

            sub_clip = TextClip(
                text=sub_formatted,
                font="C:\\Windows\\Fonts\\malgun.ttf",
                font_size=28,
                color="white",
                bg_color="rgba(15, 12, 10, 220)",
                size=(920, None),
                text_align="center"
            ).with_duration(clip_duration).with_position(("center", 580)).with_start(current_time)
            subtitle_clips.append(sub_clip)
        except Exception as e:
            print(f"[Sub Check] Subtitle TextClip skipped for Scene {seq}: {e}")
            
        current_time += clip_duration

    if subtitle_clips:
        final_video = CompositeVideoClip([final_video] + subtitle_clips, size=(WIDTH, HEIGHT))

    threads = os.cpu_count() or 4
    
    if args.upscale:
        print(f"\nRendering final video (720p intermediate) to {OUTPUT_FILE}.720p.mp4 (Threads: {threads})...")
        temp_720p = OUTPUT_FILE + ".720p.mp4"
        final_video.write_videofile(
            temp_720p,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=threads,
            preset="fast"
        )
        
        print(f"\n[Upscale] Scaling final video to 4K (3840x2160) via optimized ffmpeg Lanczos filter...")
        cmd = [
            "ffmpeg", "-y",
            "-i", temp_720p,
            "-vf", "scale=3840:2160:flags=lanczos",
            "-vcodec", "libx264",
            "-crf", "18",
            "-preset", "medium",
            "-acodec", "copy",
            OUTPUT_FILE
        ]
        subprocess.run(cmd, check=True)
        
        if os.path.exists(temp_720p):
            os.remove(temp_720p)
    else:
        print(f"\n[No-Upscale] Skipping 4K upscaling for draft. Rendering 720p directly to {OUTPUT_FILE} (Threads: {threads})...")
        final_video.write_videofile(
            OUTPUT_FILE,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=threads,
            preset="fast"
        )
        
    web_dest = "web/public/docs/hangeul_birth_vowels_zolla.mp4"
    print(f"\n[Copying to Web Assets] -> {web_dest}")
    
    cmd_compress = [
        "ffmpeg", "-y",
        "-i", OUTPUT_FILE,
        "-vf", "scale=1280:720",
        "-vcodec", "libx264",
        "-crf", "30",
        "-maxrate", "1.2M",
        "-bufsize", "2.4M",
        "-preset", "fast",
        "-acodec", "aac",
        "-b:a", "96k",
        web_dest
    ]
    subprocess.run(cmd_compress, check=True)
    
    print("\n" + "=" * 64)
    if args.upscale:
        print("  🎉 Zolla FlatCanvas Video successfully rendered & upscaled!")
        print(f"   - 4K Master: {OUTPUT_FILE}")
    else:
        print("  🎉 Zolla FlatCanvas Video successfully rendered (Draft)!")
        print(f"   - 720p Master: {OUTPUT_FILE}")
    print(f"   - Web Optimized: {web_dest}")
    print("=" * 64)

if __name__ == "__main__":
    main()
