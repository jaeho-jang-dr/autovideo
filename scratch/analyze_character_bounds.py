import cv2
import numpy as np

def analyze_character(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Failed to load {img_path}")
        return
        
    print(f"Image: {img_path}, Shape: {img.shape}")
    
    # Check channels
    if img.shape[2] == 4:
        alpha = img[:, :, 3]
        # Find non-transparent bounding box
        ys, xs = np.where(alpha > 10)
        if len(ys) > 0:
            min_y, max_y = ys.min(), ys.max()
            min_x, max_x = xs.min(), xs.max()
            print(f"  Non-transparent bounding box: Y[{min_y} to {max_y}], X[{min_x} to {max_x}]")
            print(f"  Width: {max_x - min_x}, Height: {max_y - min_y}")
        else:
            print("  Image is fully transparent")
    else:
        print("  Image has no alpha channel")

if __name__ == "__main__":
    analyze_character("home_vocab/jieun_base_front.png")
    analyze_character("home_vocab/injun_base_front.png")
    analyze_character("home_vocab/jieun_casual_front.png")
    analyze_character("home_vocab/injun_navy_front.png")

