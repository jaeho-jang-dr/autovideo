import sys
import os
from PIL import Image

def make_white_transparent(image_path, output_path, threshold=220):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} does not exist.")
        return False
        
    img = Image.open(image_path).convert("RGBA")
    datas = img.getdata()
    
    new_data = []
    for item in datas:
        # item is (r, g, b, a)
        r, g, b, a = item
        # If the pixel is very bright (close to white), make it transparent
        if r > threshold and g > threshold and b > threshold:
            new_data.append((0, 0, 0, 0)) # Fully transparent
        else:
            # Check if it has color saturation (chroma check)
            is_colored = abs(r - g) > 25 or abs(r - b) > 25 or abs(g - b) > 25
            brightness = (r + g + b) / 3
            if is_colored:
                # Keep color but scale alpha for anti-aliasing
                alpha = int(255 * (1.0 - (brightness - threshold) / (255.0 - threshold)))
                alpha = max(0, min(255, alpha))
                new_data.append((r, g, b, alpha))
            else:
                # Standard black stroke optimization
                if brightness < 150:
                    new_data.append((17, 17, 17, 255)) # Clean Ink Black
                else:
                    alpha = int(255 * (1.0 - (brightness - threshold) / (255.0 - threshold)))
                    alpha = max(0, min(255, alpha))
                    new_data.append((17, 17, 17, alpha))
                
    img.putdata(new_data)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Processed image saved to: {output_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_lineart.py <input_path> <output_path> [threshold]")
        sys.exit(1)
        
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    thresh = int(sys.argv[3]) if len(sys.argv) > 3 else 220
    
    make_white_transparent(in_path, out_path, thresh)
