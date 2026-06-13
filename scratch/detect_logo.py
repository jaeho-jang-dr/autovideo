import cv2
import numpy as np

def detect():
    img = cv2.imread("scratch/scene_1_cropped_corner.png")
    if img is None:
        print("Image not found.")
        return
    
    # Background color is roughly BGR=[201, 219, 226]
    # Let's compute color distance from this background color for each pixel
    bg_color = np.array([201, 219, 226], dtype=np.float32)
    diff = np.linalg.norm(img.astype(np.float32) - bg_color, axis=2)
    
    # Threshold the diff to find pixels that are significantly different from the background
    # (these are likely the logo or watermark text)
    threshold_val = 15.0
    logo_mask = (diff > threshold_val).astype(np.uint8) * 255
    
    # Save the mask to see where the logo is
    cv2.imwrite("scratch/logo_mask.png", logo_mask)
    print("Saved scratch/logo_mask.png")
    
    # Let's find coordinates of different pixels in the cropped image (320x144)
    # The cropped image is extracted from y in [h*0.8 : h], x in [w*0.75 : w]
    # h = 720, w = 1280
    # crop_y start = 576, crop_x start = 960
    ys, xs = np.where(logo_mask > 0)
    if len(xs) > 0 and len(ys) > 0:
        min_x, max_x = np.min(xs), np.max(xs)
        min_y, max_y = np.min(ys), np.max(ys)
        print(f"In cropped coord (320x144): X range: [{min_x}, {max_x}], Y range: [{min_y}, {max_y}]")
        print(f"In global coord (1280x720): X range: [{min_x + 960}, {max_x + 960}], Y range: [{min_y + 576}, {max_y + 576}]")
        
        # Draw bounding box on cropped image for validation
        annotated = img.copy()
        cv2.rectangle(annotated, (min_x, min_y), (max_x, max_y), (0, 0, 255), 2)
        cv2.imwrite("scratch/logo_detected.png", annotated)
        print("Saved scratch/logo_detected.png")
    else:
        print("No logo pixels detected using color distance threshold.")

if __name__ == "__main__":
    detect()
