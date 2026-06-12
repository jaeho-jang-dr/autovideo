import os
import argparse
import cv2
import numpy as np
from moviepy import VideoFileClip


def remove_watermark(input_path, output_path, bbox=None):
    if not os.path.exists(input_path):
        print(f"Error: Input video not found: {input_path}")
        return False
        
    print(f"Processing watermark removal: {input_path} -> {output_path}")
    clip = VideoFileClip(input_path)
    width, height = clip.size
    
    if bbox:
        x, y, w, h = bbox
        # Ensure values are within bounds
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        w = max(1, min(w, width - x))
        h = max(1, min(h, height - y))
        
        mask = np.zeros((height, width), dtype=np.uint8)
        mask[y:y+h, x:x+w] = 255
        
        def inpaint_frame(frame):
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            inpainted_bgr = cv2.inpaint(frame_bgr, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
            return cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)
            
        processed_clip = clip.image_transform(inpaint_frame)
    else:
        # Default: Bottom-right corner (ratio-based: X 78%~93%, Y 79%~96%)
        # Using Solid Fill method to match surrounding background color perfectly
        x_start = int(width * 0.78)
        x_end = int(width * 0.93)
        y_start = int(height * 0.79)
        y_end = int(height * 0.96)
        
        def remove_logo_frame(frame):
            sample_y_start = max(0, y_start - 10)
            sample_y_end = y_start
            sample_x_start = x_start
            sample_x_end = x_end
            
            sample_area = frame[sample_y_start:sample_y_end, sample_x_start:sample_x_end]
            if sample_area.size > 0:
                bg_color = np.median(sample_area, axis=(0, 1)).astype(np.uint8)
            else:
                bg_color = frame[y_start, x_start]
                
            frame_copy = frame.copy()
            frame_copy[y_start:y_end, x_start:x_end] = bg_color
            return frame_copy
            
        processed_clip = clip.image_transform(remove_logo_frame)
    
    # Save video with original audio (if any) and fps
    # Using MoviePy 2.x API parameters
    processed_clip.write_videofile(
        output_path,
        fps=clip.fps or 24,
        codec="libx264",
        audio_codec="aac" if clip.audio else None,
        logger=None # Silence verbose output
    )
    
    clip.close()
    processed_clip.close()
    print("Watermark removed successfully!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove video watermark using OpenCV Inpainting.")
    parser.add_argument("--input", required=True, help="Path to input video file")
    parser.add_argument("--output", required=True, help="Path to save output video file")
    parser.add_argument("--bbox", type=int, nargs=4, metavar=("X", "Y", "W", "H"), help="Bounding box coordinates: x y w h")
    args = parser.parse_args()
    
    remove_watermark(args.input, args.output, args.bbox)
