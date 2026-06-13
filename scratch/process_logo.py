from PIL import Image, ImageDraw, ImageOps
import os

def process():
    src_path = r"C:\Users\antigravity\.gemini\antigravity\brain\4cd55d9c-1adb-4786-a194-85a1ba5fa899\drjay_ed_logo_1781251623725.png"
    if not os.path.exists(src_path):
        print("Source image not found.")
        return
        
    # 1. Load and Remove White Background
    img = Image.open(src_path).convert("RGBA")
    datas = img.getdata()
    
    newData = []
    for item in datas:
        # If pixel is near-white, make it transparent
        if item[0] > 235 and item[1] > 235 and item[2] > 235:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    
    os.makedirs("assets", exist_ok=True)
    
    # ==========================================
    # VERSION 1: Circle Badge (108x108)
    # ==========================================
    # Resize keeping aspect ratio, crop to center
    size_circle = (108, 108)
    # To prevent distortion, crop to square first
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    cropped_square = img.crop((left, top, right, bottom))
    
    # Resize to 108x108
    resized_square = cropped_square.resize(size_circle, Image.Resampling.LANCZOS)
    
    # Create circular mask
    mask_circle = Image.new("L", size_circle, 0)
    draw_mask = ImageDraw.Draw(mask_circle)
    draw_mask.ellipse([0, 0, 108, 108], fill=255)
    
    # Apply mask to create circular image
    circle_logo = Image.new("RGBA", size_circle, (0, 0, 0, 0))
    circle_logo.paste(resized_square, (0, 0), mask=mask_circle)
    
    # Draw a clean circular border (Navy Blue & Yellow/Red theme)
    draw_border = ImageDraw.Draw(circle_logo)
    # Outer circle border
    draw_border.ellipse([1, 1, 106, 106], outline=(32, 32, 96, 255), width=3) # Navy blue
    
    circle_logo.save("assets/drjay_ed_logo_circle.png")
    print("Saved CIRCULAR logo badge to assets/drjay_ed_logo_circle.png")
    
    # ==========================================
    # VERSION 2: Capsule/Pill Badge (176x108)
    # ==========================================
    size_capsule = (176, 108)
    # Resize image to fit inside 176x108 with margins
    img_fit = img.copy()
    img_fit.thumbnail((160, 92), Image.Resampling.LANCZOS)
    
    # Paste resized onto a transparent 176x108 canvas
    canvas_capsule = Image.new("RGBA", size_capsule, (0, 0, 0, 0))
    dx = (176 - img_fit.width) // 2
    dy = (108 - img_fit.height) // 2
    canvas_capsule.paste(img_fit, (dx, dy))
    
    # Create capsule mask (rounded rectangle with radius = height/2 = 54)
    mask_capsule = Image.new("L", size_capsule, 0)
    draw_capsule_mask = ImageDraw.Draw(mask_capsule)
    draw_capsule_mask.rounded_rectangle([0, 0, 176, 108], radius=54, fill=255)
    
    # Apply capsule mask
    capsule_logo = Image.new("RGBA", size_capsule, (0, 0, 0, 0))
    capsule_logo.paste(canvas_capsule, (0, 0), mask=mask_capsule)
    
    # Draw border on the capsule
    draw_capsule_border = ImageDraw.Draw(capsule_logo)
    draw_capsule_border.rounded_rectangle([1, 1, 174, 106], radius=53, outline=(32, 32, 96, 255), width=3)
    
    capsule_logo.save("assets/drjay_ed_logo_capsule.png")
    print("Saved CAPSULE logo badge to assets/drjay_ed_logo_capsule.png")

if __name__ == "__main__":
    process()
