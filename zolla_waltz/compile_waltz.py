# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import cv2
from PIL import Image
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
import moviepy.video.fx as fx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# Force UTF-8 stdout
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WALTZ_DIR = os.path.join(ROOT, "zolla_waltz")
BGM_PATH = os.path.join(ROOT, "assets", "audio", "waltz_bgm.wav")
LOGO_PATH = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
OUT_VIDEO_PATH = os.path.join(WALTZ_DIR, "zolla_waltz.mp4")

# Scene durations: total 150 seconds (2m 30s) across 25 scenes
SCENE_DURATIONS = [6, 5, 7, 6, 6, 6, 5, 6, 7, 6, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 5, 6, 7, 6, 6]

def apply_zoom_crop(clip):
    """
    Applies the Dolly Zoom-Crop technique (78% crop + Lanczos-4 interpolation)
    to remove watermarks while preserving 16:9 aspect ratio.
    """
    def effect(get_frame, t):
        frame = get_frame(t)
        h, w = frame.shape[:2]
        # Crop to 78% of original size centered
        crop_h, crop_w = int(h * 0.78), int(w * 0.78)
        y1 = (h - crop_h) // 2
        x1 = (w - crop_w) // 2
        cropped = frame[y1:y1+crop_h, x1:x1+crop_w]
        # Resize back to original size using Lanczos4
        resized = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LANCZOS4)
        return resized
    return clip.transform(effect)

def apply_logo_overlay(clip, logo_rgb, logo_alpha):
    """
    Overlays the circular channel logo (45x45 px) in the bottom-right corner.
    """
    def effect(get_frame, t):
        frame = get_frame(t).copy() # copy to avoid read-only buffer error
        h, w = frame.shape[:2]
        # Position: bottom-right corner with 20px margins
        x0 = w - 45 - 20
        y0 = h - 45 - 20
        # Alpha blending
        roi = frame[y0:y0+45, x0:x0+45]
        blended = (1.0 - logo_alpha) * roi + logo_alpha * logo_rgb
        frame[y0:y0+45, x0:x0+45] = blended.astype(np.uint8)
        return frame
    return clip.transform(effect)

def main():
    print("Step 1: Loading channel logo and preparing overlay...")
    if not os.path.exists(LOGO_PATH):
        print(f"[ERR] Logo not found at {LOGO_PATH}")
        return 1
        
    logo_img = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)
    if logo_img is None or logo_img.shape[2] != 4:
        print("[ERR] Logo must be a transparent 4-channel PNG.")
        return 1
        
    # Convert BGRA to RGBA and resize to 45x45
    logo_rgba = cv2.cvtColor(logo_img, cv2.COLOR_BGRA2RGBA)
    logo_resized = cv2.resize(logo_rgba, (45, 45), interpolation=cv2.INTER_AREA)
    logo_rgb = logo_resized[:, :, :3]
    logo_alpha = logo_resized[:, :, 3:4] / 255.0

    print("Step 2: Processing and concatenating video clips...")
    processed_clips = []
    
    for i in range(1, 26):
        clip_path = os.path.join(WALTZ_DIR, f"scene_{i}.mp4")
        if not os.path.exists(clip_path):
            print(f"[ERR] Missing video clip: {clip_path}")
            return 1
            
        print(f"  Processing scene_{i}.mp4 (Target: {SCENE_DURATIONS[i-1]}s)...")
        clip = VideoFileClip(clip_path).without_audio()
        
        # A. Apply 78% Zoom-Crop to remove watermark
        clip = apply_zoom_crop(clip)
        
        # B. Apply logo overlay
        clip = apply_logo_overlay(clip, logo_rgb, logo_alpha)
        
        # C. Match target duration by adjusting speed
        current_dur = clip.duration
        target_dur = SCENE_DURATIONS[i-1]
        speed_factor = current_dur / target_dur
        
        clip = clip.with_effects([fx.MultiplySpeed(speed_factor)]).with_duration(target_dur)
        processed_clips.append(clip)
        
    print("\nConcatenating all clips...")
    final_video = concatenate_videoclips(processed_clips)
    
    print("\nStep 3: Loading and applying BGM...")
    if not os.path.exists(BGM_PATH):
        print(f"[ERR] BGM not found at {BGM_PATH}")
        return 1
    bgm_clip = AudioFileClip(BGM_PATH)
    
    # Trim or loop BGM to match video duration exactly
    if bgm_clip.duration >= final_video.duration:
        bgm_clip = bgm_clip.with_duration(final_video.duration)
    else:
        from moviepy.audio.fx import AudioLoop
        bgm_clip = bgm_clip.with_effects([AudioLoop(duration=final_video.duration)])
    final_video = final_video.with_audio(bgm_clip)
    
    # 4K Upscale: We compile at original resolution first, then let ffmpeg upscale it to 4K if requested.
    # But wait, let's write out a high-quality 1080p video as the target.
    # The guidelines say: "최종 컴파일 렌더링 시에는 시스템의 모든 CPU 자원을 100% 동원하도록 os.cpu_count() 코드를 활용해 최대 병렬 스레드를 할당해 컴파일한다."
    threads = os.cpu_count() or 4
    
    print(f"\nStep 4: Rendering final video with {threads} threads...")
    # Render final output video
    final_video.write_videofile(
        OUT_VIDEO_PATH,
        codec="libx264",
        audio_codec="aac",
        threads=threads,
        preset="medium",
        bitrate="8000k"
    )
    
    # Close clips
    for c in processed_clips:
        c.close()
    final_video.close()
    bgm_clip.close()
    
    print(f"\n[SUCCESS] Final waltz video compiled and saved to: {OUT_VIDEO_PATH}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
