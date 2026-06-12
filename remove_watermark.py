import os
import argparse
import cv2
import numpy as np
from moviepy import VideoFileClip

def inpaint_frame(frame, mask):
    # frame: numpy array (RGB) from MoviePy
    # cv2.inpaint expects BGR, so we convert RGB->BGR, inpaint, then BGR->RGB
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    inpainted_bgr = cv2.inpaint(frame_bgr, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    return cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)

def remove_watermark(input_path, output_path, bbox=None):
    if not os.path.exists(input_path):
        print(f"Error: Input video not found: {input_path}")
        return False
        
    print(f"Processing watermark removal: {input_path} -> {output_path}")
    clip = VideoFileClip(input_path)
    width, height = clip.size
    
    # Create mask (same size as frame, 1 channel)
    mask = np.zeros((height, width), dtype=np.uint8)
    
    if bbox:
        x, y, w, h = bbox
        # Ensure values are within bounds
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        w = max(1, min(w, width - x))
        h = max(1, min(h, height - y))
        mask[y:y+h, x:x+w] = 255
    else:
        # Default: Bottom-right corner (ratio-based: right 20%, bottom 12%)
        # This covers standard AI generator watermarks
        x_start = int(width * 0.80)
        x_end = int(width * 0.98)
        y_start = int(height * 0.88)
        y_end = int(height * 0.98)
        mask[y_start:y_end, x_start:x_end] = 255
        
    # Process each frame using MoviePy's image_transform (replacement for fl_image in MoviePy 2.x)
    processed_clip = clip.image_transform(lambda frame: inpaint_frame(frame, mask))
    
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
