import os
import sys
from PIL import Image, ImageDraw, ImageFont

def generate_text_lineart(text, output_path, font_size=180, stroke_width=6):
    """Generates a transparent PNG image of a text rendered in clean black line-art style with stroke."""
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    if not os.path.exists(font_path):
        font_path = "arial.ttf"
        
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()
        
    # Helper draw to measure text
    dummy_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    dummy_draw = ImageDraw.Draw(dummy_img)
    
    try:
        bbox = dummy_draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except AttributeError:
        w, h = dummy_draw.textsize(text, font=font)
        bbox = [0, 0, w, h]
        
    # Add margins to accommodate stroke thickness
    margin = stroke_width * 2 + 15
    size_w = int(w + margin * 2)
    size_h = int(h + margin * 2)
    
    # Create final transparent canvas
    img = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate offset
    x = margin - bbox[0]
    y = margin - bbox[1]
    
    # Draw outline text (Clean Ink Black)
    draw.text((x, y), text, fill=(17, 17, 17, 255), font=font, stroke_width=stroke_width, stroke_fill=(17, 17, 17, 255))
    
    # Ensure directory exists and save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Generated text lineart asset: {output_path} ('{text}')")
    return output_path

def generate_hangeul_assets():
    # Targets for basic letters
    consonants = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    vowels = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
    
    target_dir = "assets/graphics/letters"
    
    # Generate consonants & vowels
    for letter in consonants + vowels:
        file_path = os.path.join(target_dir, f"letter_{letter}.png")
        generate_text_lineart(letter, file_path, font_size=180, stroke_width=6)

    # Pre-generate common educational words
    words = ["하늘", "땅", "사람", "기역", "니은", "디귿", "리을", "미음", "비읍", "시옷", "이응", "지읒", "치읓", "키읔", "티읕", "피읖", "히읗"]
    for word in words:
        file_path = os.path.join(target_dir, f"word_{word}.png")
        generate_text_lineart(word, file_path, font_size=120, stroke_width=4)

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--text":
        custom_text = sys.argv[2]
        out_file = f"assets/graphics/letters/word_{custom_text}.png"
        generate_text_lineart(custom_text, out_file, font_size=120, stroke_width=4)
    else:
        # Default runs full asset generation
        generate_hangeul_assets()
