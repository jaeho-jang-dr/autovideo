import cv2
import numpy as np
import json

def analyze_frames(video_path, timestamps):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    results = {}
    
    for ts in timestamps:
        frame_idx = int(ts * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            print(f"Warning: Could not read frame at {ts}s")
            continue
            
        # Convert to RGB to analyze colors
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Calculate mean color
        mean_color = rgb_frame.mean(axis=(0, 1))
        
        # Dominant colors using simplified quantization
        # Reshape to a list of pixels
        pixels = rgb_frame.reshape(-1, 3)
        # Quantize colors to bins of 32 to find dominant tones
        quantized = (pixels // 32) * 32
        unique_colors, counts = np.unique(quantized, axis=0, return_counts=True)
        
        # Get top 5 dominant colors
        top_indices = np.argsort(-counts)[:5]
        dominant_colors = []
        for idx in top_indices:
            color = unique_colors[idx].tolist()
            pct = float(counts[idx]) / len(pixels)
            dominant_colors.append({
                "rgb": color,
                "percentage": round(pct * 100, 2)
            })
            
        results[f"{ts}s"] = {
            "mean_rgb": [round(c, 2) for c in mean_color.tolist()],
            "dominant_colors": dominant_colors
        }
        
    cap.release()
    
    print(json.dumps(results, indent=2))
    with open("debug/color_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    video_path = "debug/How hat fashion has evolved throughout history - Alison L. Goodrum.mp4"
    # Analyze diverse moments in the video representing different chapters
    analyze_frames(video_path, [15.0, 45.0, 95.0, 130.0, 180.0, 210.0, 245.0])
