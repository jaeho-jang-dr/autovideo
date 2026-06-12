import os
import json
import cv2
import numpy as np

def analyze_video(video_path, output_profile_path="reference_profile.json"):
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return False
        
    print(f"Analyzing reference video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Failed to open video file.")
        return False
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps
    
    print(f"Video specs: {width}x{height}, {fps} FPS, Duration: {duration:.2f}s, Total Frames: {total_frames}")
    
    # 1. Shot Boundary Detection (scene cuts)
    cuts = [0.0] # starts at 0s
    prev_hist = None
    
    frame_idx = 0
    # Downsample frame rate for faster analysis
    step = max(1, int(fps / 5)) # sample 5 times per second
    
    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break
            
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Calculate Hue-Saturation histogram
        hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        
        if prev_hist is not None:
            # Compare histograms using correlation
            corr = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
            time_sec = frame_idx / fps
            
            # If correlation drops significantly, we detect a cut
            # Threshold set to 0.70 for robust transition detection
            # Also ensure at least 1.5 seconds between cuts to avoid noisy sub-cuts
            if corr < 0.70 and (time_sec - cuts[-1]) > 1.5:
                cuts.append(round(time_sec, 2))
                print(f"Detected scene cut at {time_sec:.2f}s (Correlation: {corr:.3f})")
                
        prev_hist = hist
        frame_idx += step
        if frame_idx >= total_frames:
            break
            
    cap.release()
    
    # Append final duration as the end of the last scene
    if cuts[-1] < duration - 1.0:
        cuts.append(round(duration, 2))
    else:
        cuts[-1] = round(duration, 2)
        
    # Build scene timelines
    scenes = []
    for i in range(len(cuts) - 1):
        scenes.append({
            "scene_id": i + 1,
            "start": cuts[i],
            "end": cuts[i+1],
            "duration": round(cuts[i+1] - cuts[i], 2)
        })
        
    # 2. Subtitle Area & Styling Estimation
    # Historically in autovideo, subtitle is centered, bottom margin around 230px, text size 24
    # We profile standard aesthetics matching the reference video style
    subtitle_style = {
        "font_size": 26,
        "color": "white",
        "stroke_color": "black",
        "stroke_width": 2,
        "margin_bottom": 230, # pixels from bottom
        "max_chars_per_line": 35
    }
    
    profile = {
        "video_path": video_path,
        "resolution": {"width": width, "height": height},
        "fps": round(fps, 2),
        "total_duration": round(duration, 2),
        "scene_count": len(scenes),
        "scenes": scenes,
        "subtitle_style": subtitle_style
    }
    
    with open(output_profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
        
    print(f"Analysis completed. Profile saved to {output_profile_path}")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Analyze a reference video for reverse engineering.")
    parser.add_argument("--video", default="dopamine_loop.mp4", help="Path to reference video")
    parser.add_argument("--output", default="reference_profile.json", help="Path to save profile JSON")
    args = parser.parse_args()
    
    analyze_video(args.video, args.output)
