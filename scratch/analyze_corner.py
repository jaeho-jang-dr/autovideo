import cv2
import numpy as np

def analyze():
    img = cv2.imread("scratch/scene_1_cropped_corner.png")
    if img is None:
        print("Cropped corner image not found.")
        return
        
    h, w, c = img.shape
    print(f"Loaded corner image. Size: {w}x{h}")
    
    # Let's find regions with high local contrast or variance
    # Or, convert to grayscale and check pixel values
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Print average pixel value of the corner
    mean_val = np.mean(gray)
    min_val = np.min(gray)
    max_val = np.max(gray)
    print(f"Grayscale stats - Mean: {mean_val:.2f}, Min: {min_val}, Max: {max_val}")
    
    # Save a grayscale representation to check
    cv2.imwrite("scratch/scene_1_corner_gray.png", gray)
    
    # Find contours of non-background pixels.
    # Assuming background is very bright (near 255) or very uniform.
    # Let's do a threshold to isolate the logo.
    # If background is bright, logo might be darker gray.
    # If background is dark, logo might be brighter.
    # Let's check variance.
    # Print some pixel values from a grid to understand the colors
    print("Corner pixel grid sample (y, x) -> [B, G, R]:")
    for y in range(0, h, h // 5):
        row_str = ""
        for x in range(0, w, w // 5):
            row_str += f"({y},{x}): {img[y, x].tolist()}  "
        print(row_str)

if __name__ == "__main__":
    analyze()
