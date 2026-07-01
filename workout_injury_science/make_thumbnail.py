import os
import cv2
from PIL import Image, ImageDraw, ImageFont

# Path configuration
video_path = r"D:\Entertainments\DevEnvironment\autovideo\workout_injury_science\scene_0.mp4"
output_path = r"D:\Entertainments\DevEnvironment\autovideo\workout_injury_science\scene_0_thumbnail.png"
font_path = r"C:\Windows\Fonts\malgunbd.ttf"

def draw_rounded_rectangle(draw, xy, corner_radius, fill, outline, width=1):
    draw.rounded_rectangle(xy, radius=corner_radius, fill=fill, outline=outline, width=width)

def extract_frame_from_video(vid_path):
    # Load video using OpenCV
    cap = cv2.VideoCapture(vid_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file {vid_path}")
        return None
        
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Read the middle frame (usually the title text is fully rendered here)
    middle_frame_idx = total_frames // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_idx)
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Error: Cannot extract frame from video")
        return None
        
    # Convert BGR (OpenCV default) to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame_rgb)

def main():
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return

    print("Extracting background frame from Google Flow-generated scene_0.mp4...")
    img = extract_frame_from_video(video_path)
    if img is None:
        print("Failed to extract frame. Exiting.")
        return

    # Resize to standard 16:9 thumbnail size (1280x720)
    img = img.convert("RGBA")
    img = img.resize((1280, 720), Image.Resampling.LANCZOS)
    
    # Create overlay drawing context
    draw = ImageDraw.Draw(img)
    
    # 2. Configure fonts
    try:
        title_font = ImageFont.truetype(font_path, 54)  # Large main title
        subtitle_font = ImageFont.truetype(font_path, 32)  # Medium subtitle
    except IOError:
        print("Warning: Bold Malgun Gothic font not found, falling back to default.")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # 3. Text content
    title_text = "내가 운동만 하면 아픈 이유?"
    subtitle_text = "헬스 중독자들이 절대 피할 수 없는 '통증의 과학'"
    
    # 4. Measure text sizes for layout using textbbox
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]
    
    sub_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_h = sub_bbox[3] - sub_bbox[1]
    
    # Padding and Box Dimension
    padding_x = 45
    padding_y = 30
    gap = 15
    
    box_w = max(title_w, sub_w) + (padding_x * 2)
    box_h = title_h + sub_h + (padding_y * 2) + gap
    
    # Positioning the box (Centered horizontally, slightly elevated vertically)
    box_x1 = (1280 - box_w) // 2
    box_y1 = 60  # Near the top to let the background character show clearly in the middle/bottom
    box_x2 = box_x1 + box_w
    box_y2 = box_y1 + box_h
    
    # 5. Draw the sprout green text box matching our video layout style
    # Fill: Sprout green (RGBA: [224, 245, 224, 215])
    # Border: Darker green (RGBA: [46, 125, 50, 255]), thickness=4
    draw_rounded_rectangle(
        draw, 
        (box_x1, box_y1, box_x2, box_y2), 
        corner_radius=20, 
        fill=(224, 245, 224, 215), 
        outline=(46, 125, 50, 255), 
        width=4
    )
    
    # 6. Draw Text (Crisp pure black #000000 for maximum readability)
    title_x = box_x1 + (box_w - title_w) // 2
    title_y = box_y1 + padding_y - 5
    draw.text((title_x, title_y), title_text, font=title_font, fill=(0, 0, 0, 255))
    
    sub_x = box_x1 + (box_w - sub_w) // 2
    sub_y = title_y + title_h + gap + 10
    draw.text((sub_x, sub_y), subtitle_text, font=subtitle_font, fill=(0, 0, 0, 255))
    
    # Save output
    final_img = img.convert("RGB")
    final_img.save(output_path, "PNG")
    print(f"Success: Korean Thumbnail saved successfully to {output_path}")

if __name__ == "__main__":
    main()
