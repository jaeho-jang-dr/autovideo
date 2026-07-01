import os
from PIL import Image, ImageDraw, ImageFont

def generate_underline():
    # Width=800, Height=60
    img = Image.new("RGBA", (800, 60), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw a gold yellow (#FFD700) rounded underline
    # Line starting from (10, 30) to (790, 30) with width 14
    draw.line([(20, 30), (780, 30)], fill=(255, 215, 0, 255), width=12, joint="round")
    
    out_path = "assets/graphics/effect_underline.png"
    img.save(out_path, "PNG")
    print(f"Generated Underline effect asset: {out_path}")

def generate_particle():
    # Small 64x64 canvas for dust particle
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw 4 small random gray/black dots
    draw.ellipse([20, 20, 26, 26], fill=(17, 17, 17, 255))
    draw.ellipse([35, 15, 38, 18], fill=(50, 50, 50, 255))
    draw.ellipse([15, 35, 19, 39], fill=(80, 80, 80, 255))
    draw.ellipse([40, 40, 43, 43], fill=(100, 100, 100, 255))
    
    out_path = "assets/graphics/obj_particle.png"
    img.save(out_path, "PNG")
    print(f"Generated Particle effect asset: {out_path}")

def generate_number_badges():
    # Setup fonts
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    if not os.path.exists(font_path):
        font_path = "arial.ttf"
    try:
        font = ImageFont.truetype(font_path, 80)
    except IOError:
        font = ImageFont.load_default()
        
    badges = [
        ("1", (255, 215, 0, 255)),   # Gold Yellow
        ("2", (135, 206, 235, 255)),  # Sky Blue
        ("3", (255, 140, 0, 255))     # Dark Orange
    ]
    
    for num_str, bg_color in badges:
        size = 128
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 1. Draw outer ink outline circle
        draw.ellipse([4, 4, size-4, size-4], fill=bg_color, outline=(17, 17, 17, 255), width=5)
        
        # 2. Draw digit centered
        try:
            bbox = draw.textbbox((0, 0), num_str, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
        except AttributeError:
            w, h = draw.textsize(num_str, font=font)
            bbox = [0, 0, w, h]
            
        x = (size - w) / 2 - bbox[0]
        y = (size - h) / 2 - bbox[1] - 4 # Micro offset for typography visual center
        
        # Draw digit in Ink Black
        draw.text((x, y), num_str, fill=(17, 17, 17, 255), font=font)
        
        out_path = f"assets/graphics/badge_{num_str}.png"
        img.save(out_path, "PNG")
        print(f"Generated Number Badge asset: {out_path}")

if __name__ == "__main__":
    os.makedirs("assets/graphics", exist_ok=True)
    generate_underline()
    generate_particle()
    generate_number_badges()
