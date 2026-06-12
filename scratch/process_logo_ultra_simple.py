from PIL import Image, ImageDraw
import os

def process_ultra_simple():
    src_path = r"C:\Users\antigravity\.gemini\antigravity\brain\4cd55d9c-1adb-4786-a194-85a1ba5fa899\drjay_ed_logo_ultra_simple_1781251760706.png"
    if not os.path.exists(src_path):
        print("Source image not found.")
        return
        
    img = Image.open(src_path).convert("RGBA")
    
    # 1. Background transparency (R,G,B > 240 to transparent)
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    
    # 2. Crop to Square centered on the circle
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    cropped = img.crop((left, top, right, bottom))
    
    # Resize to 108x108
    target_size = (108, 108)
    resized = cropped.resize(target_size, Image.Resampling.LANCZOS)
    
    # 3. Create circular mask
    mask = Image.new("L", target_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([0, 0, 108, 108], fill=255)
    
    # Apply mask
    circle_logo = Image.new("RGBA", target_size, (0, 0, 0, 0))
    circle_logo.paste(resized, (0, 0), mask=mask)
    
    # 4. Draw a clean border
    draw_border = ImageDraw.Draw(circle_logo)
    draw_border.ellipse([1, 1, 106, 106], outline=(32, 32, 96, 255), width=2)
    
    os.makedirs("assets", exist_ok=True)
    circle_logo.save("assets/drjay_ed_logo_circle.png")
    print("Successfully processed and saved ultra-simple circular logo to assets/drjay_ed_logo_circle.png")

if __name__ == "__main__":
    process_ultra_simple()
