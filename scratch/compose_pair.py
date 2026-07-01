# -*- coding: utf-8 -*-
import os
import sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

# Import transparentize helper
from gen_assets_flow import make_bg_transparent

def main():
    injun_src = os.path.join(ROOT, "home_vocab", "injun_navy_front_opaque.png")
    if not os.path.exists(injun_src):
        injun_src = os.path.join(ROOT, "home_vocab", "injun_navy_front.png")
        
    # Prefer using _dbref_jieun_base_front.png if exists (original beige base)
    jieun_src = os.path.join(ROOT, "home_vocab", "_dbref_jieun_base_front.png")
    if not os.path.exists(jieun_src):
        jieun_src = os.path.join(ROOT, "home_vocab", "jieun_base_front.png")
        
    print(f"Source Injun: {injun_src}")
    print(f"Source Jieun: {jieun_src}")
    
    if not os.path.exists(injun_src) or not os.path.exists(jieun_src):
        print("[ERR] Source files do not exist.")
        return 1
        
    # Temporary transparent files to determine bbox
    temp_injun = os.path.join(ROOT, "scratch", "temp_injun_trans.png")
    temp_jieun = os.path.join(ROOT, "scratch", "temp_jieun_trans.png")
    
    print("Generating temporary transparent images for bounding box analysis...")
    make_bg_transparent(injun_src, temp_injun, tol=28)
    make_bg_transparent(jieun_src, temp_jieun, tol=28)
    
    img_injun = Image.open(temp_injun).convert("RGBA")
    img_jieun = Image.open(temp_jieun).convert("RGBA")
    
    # Get thresholded bboxes
    alpha_injun = img_injun.split()[-1]
    alpha_jieun = img_jieun.split()[-1]
    
    alpha_injun_bin = alpha_injun.point(lambda p: 255 if p > 30 else 0)
    alpha_jieun_bin = alpha_jieun.point(lambda p: 255 if p > 30 else 0)
    
    bbox_injun = alpha_injun_bin.getbbox()
    bbox_jieun = alpha_jieun_bin.getbbox()
    
    if not bbox_injun or not bbox_jieun:
        print("[ERR] Could not determine character bounding boxes.")
        # Cleanup
        try:
            os.remove(temp_injun)
            os.remove(temp_jieun)
        except:
            pass
        return 1
        
    left_injun, _, right_injun, _ = bbox_injun
    left_jieun, _, right_jieun, _ = bbox_jieun
    
    w_injun = right_injun - left_injun
    w_jieun = right_jieun - left_jieun
    
    print(f"Injun horizontal span: {left_injun} to {right_injun} (width: {w_injun})")
    print(f"Jieun horizontal span: {left_jieun} to {right_jieun} (width: {w_jieun})")
    
    # Crop horizontally, keeping full vertical range (0 to 720) to preserve Y-alignment
    crop_injun = img_injun.crop((left_injun, 0, right_injun, 720))
    crop_jieun = img_jieun.crop((left_jieun, 0, right_jieun, 720))
    
    # Layout configuration
    gap = 80
    total_w = w_injun + gap + w_jieun
    start_x = (1280 - total_w) // 2
    
    x_injun = start_x
    x_jieun = start_x + w_injun + gap
    
    print(f"Compositing positions -> Injun X: {x_injun}, Jieun X: {x_jieun}")
    
    # Create final transparent image
    img_trans = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    img_trans.paste(crop_injun, (x_injun, 0), crop_injun)
    img_trans.paste(crop_jieun, (x_jieun, 0), crop_jieun)
    
    out_trans = os.path.join(ROOT, "home_vocab", "injun_jieun_pair.png")
    img_trans.save(out_trans)
    print(f"Transparent pair saved to: {out_trans}")
    
    # Create final opaque (beige background) image
    img_opaque = Image.new("RGBA", (1280, 720), (245, 245, 240, 255))
    img_opaque.paste(crop_injun, (x_injun, 0), crop_injun)
    img_opaque.paste(crop_jieun, (x_jieun, 0), crop_jieun)
    
    out_opaque = os.path.join(ROOT, "home_vocab", "injun_jieun_pair_opaque.png")
    img_opaque.convert("RGB").save(out_opaque)
    print(f"Opaque pair saved to: {out_opaque}")
    
    # Cleanup temp files
    try:
        os.remove(temp_injun)
        os.remove(temp_jieun)
    except Exception:
        pass
        
    print("[SUCCESS] Compose Pair finished.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
