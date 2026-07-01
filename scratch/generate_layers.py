import os
from PIL import Image, ImageDraw, ImageFont

def make_transparent_canvas(width, height):
    return Image.new("RGBA", (width, height), (0, 0, 0, 0))

def get_font(size, bold=True):
    font_path = r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf"
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        return ImageFont.load_default()

def main():
    out_dir = "scratch/layers"
    os.makedirs(out_dir, exist_ok=True)
    
    # -------------------------------------------------------------------------
    # SCENE 1 LAYERS (Flying Car Blueprint Assembly)
    # -------------------------------------------------------------------------
    
    # Layer 5: Blueprint Grid Background (1280x720) - Deep blueprint theme
    grid = make_transparent_canvas(1280, 720)
    draw = ImageDraw.Draw(grid)
    # Draw fine background grid lines (dark blue)
    for x in range(0, 1280, 40):
        draw.line([(x, 0), (x, 720)], fill=(20, 60, 120, 80), width=1)
    for y in range(0, 720, 40):
        draw.line([(0, y), (1280, y)], fill=(20, 60, 120, 80), width=1)
    # Highlight center crosshairs
    draw.line([(640, 0), (640, 720)], fill=(40, 90, 180, 120), width=2)
    draw.line([(0, 360), (1280, 360)], fill=(40, 90, 180, 120), width=2)
    grid.save(os.path.join(out_dir, "grid.png"))
    print("Generated Layer 5: grid.png")

    # Layer 1: Car Body Outline (800x400) - Futuristic sleek chassis
    body = make_transparent_canvas(800, 400)
    draw = ImageDraw.Draw(body)
    # Draw chassis polygon
    chassis_pts = [(100, 250), (150, 180), (300, 130), (550, 130), (700, 200), (750, 250), (680, 310), (180, 310)]
    draw.polygon(chassis_pts, outline=(255, 255, 255, 255), width=4)
    # Cabin lines
    draw.line([(320, 130), (380, 180)], fill=(255, 255, 255, 200), width=3)
    draw.line([(530, 130), (480, 180)], fill=(255, 255, 255, 200), width=3)
    draw.line([(380, 180), (480, 180)], fill=(255, 255, 255, 200), width=3)
    # Jet engine nozzle outline
    draw.rectangle([(50, 210), (100, 260)], outline=(255, 255, 255, 255), width=4)
    body.save(os.path.join(out_dir, "body.png"))
    print("Generated Layer 1: body.png")

    # Layer 2: Wheel Outline (150x150) - Technical segmented circle
    wheel = make_transparent_canvas(150, 150)
    draw = ImageDraw.Draw(wheel)
    # Outer tire
    draw.ellipse([(10, 10), (140, 140)], outline=(3, 169, 244, 255), width=5)
    # Hub cap
    draw.ellipse([(45, 45), (105, 105)], outline=(3, 169, 244, 255), width=3)
    # Spokes (6 spoke system)
    import math
    for i in range(6):
        angle = i * (2 * math.pi / 6)
        x2 = 75 + 65 * math.cos(angle)
        y2 = 75 + 65 * math.sin(angle)
        draw.line([(75, 75), (x2, y2)], fill=(3, 169, 244, 255), width=3)
    wheel.save(os.path.join(out_dir, "wheel.png"))
    print("Generated Layer 2: wheel.png")

    # Layer 3: Jet Wing Outline (250x100) - Aerodynamic aerodynamic thruster wing
    wing = make_transparent_canvas(250, 100)
    draw = ImageDraw.Draw(wing)
    # Aerodynamic trapezoid
    wing_pts = [(10, 50), (180, 10), (240, 40), (150, 90)]
    draw.polygon(wing_pts, outline=(76, 175, 80, 255), width=4)
    # Internal wing rib structures
    draw.line([(60, 38), (100, 72)], fill=(76, 175, 80, 200), width=2)
    draw.line([(120, 24), (140, 68)], fill=(76, 175, 80, 200), width=2)
    wing.save(os.path.join(out_dir, "wing.png"))
    print("Generated Layer 3: wing.png")

    # Layer 4: Target Pointer & Label (200x120) - Tech annotation leader line
    pointer = make_transparent_canvas(250, 120)
    draw = ImageDraw.Draw(pointer)
    # Dotted horizontal line with circular node
    draw.ellipse([(5, 85), (25, 105)], outline=(255, 235, 59, 255), width=3)
    draw.line([(25, 95), (120, 95), (150, 60)], fill=(255, 235, 59, 255), width=3)
    # Label text box
    draw.rectangle([(150, 20), (245, 60)], outline=(255, 235, 59, 255), width=2)
    font_s = get_font(14, bold=True)
    draw.text((160, 28), "THRUSTER", font=font_s, fill=(255, 235, 59, 255))
    pointer.save(os.path.join(out_dir, "pointer.png"))
    print("Generated Layer 4: pointer.png")

    # -------------------------------------------------------------------------
    # SCENE 2 LAYERS (Robotic Gear System)
    # -------------------------------------------------------------------------
    
    # Layer 6: Main Housing Frame (600x600) - Technical chassis layout
    housing = make_transparent_canvas(600, 600)
    draw = ImageDraw.Draw(housing)
    # Large mounting brackets
    draw.rectangle([(50, 50), (550, 550)], outline=(255, 255, 255, 255), width=4)
    draw.ellipse([(100, 100), (500, 500)], outline=(255, 255, 255, 150), width=2)
    # Inner mounting points
    draw.ellipse([(150-20, 150-20), (150+20, 150+20)], outline=(255, 255, 255, 255), width=3)
    draw.ellipse([(450-20, 150-20), (450+20, 150+20)], outline=(255, 255, 255, 255), width=3)
    draw.ellipse([(150-20, 450-20), (150+20, 450+20)], outline=(255, 255, 255, 255), width=3)
    draw.ellipse([(450-20, 450-20), (450+20, 450+20)], outline=(255, 255, 255, 255), width=3)
    housing.save(os.path.join(out_dir, "gear_body.png"))
    print("Generated Layer 6: gear_body.png")

    # Layer 7: Large Gear (300x300) - Main drive gear with 16 teeth
    gear_l = make_transparent_canvas(300, 300)
    draw = ImageDraw.Draw(gear_l)
    cx, cy, r_out, r_in = 150, 150, 120, 95
    # Outer & Inner Circles
    draw.ellipse([(cx - r_out, cy - r_out), (cx + r_out, cy + r_out)], outline=(255, 109, 0, 255), width=4)
    draw.ellipse([(cx - r_in, cy - r_in), (cx + r_in, cy + r_in)], outline=(255, 109, 0, 255), width=3)
    draw.ellipse([(cx - 30, cy - 30), (cx + 30, cy + 30)], outline=(255, 109, 0, 255), width=3) # Hub
    # Draw 16 Gear teeth (Trapezoids pointing outward)
    for i in range(16):
        a_mid = i * (2 * math.pi / 16)
        a_w = 0.08  # tooth width angle
        # 4 points of a gear tooth
        p1 = (cx + r_in * math.cos(a_mid - a_w), cy + r_in * math.sin(a_mid - a_w))
        p2 = (cx + (r_out + 12) * math.cos(a_mid - a_w/2), cy + (r_out + 12) * math.sin(a_mid - a_w/2))
        p3 = (cx + (r_out + 12) * math.cos(a_mid + a_w/2), cy + (r_out + 12) * math.sin(a_mid + a_w/2))
        p4 = (cx + r_in * math.cos(a_mid + a_w), cy + r_in * math.sin(a_mid + a_w))
        draw.line([p1, p2, p3, p4], fill=(255, 109, 0, 255), width=3)
    # Spoke lines
    for i in range(4):
        a = i * (math.pi / 2)
        draw.line([(cx, cy), (cx + r_in * math.cos(a), cy + r_in * math.sin(a))], fill=(255, 109, 0, 255), width=3)
    gear_l.save(os.path.join(out_dir, "gear_large.png"))
    print("Generated Layer 7: gear_large.png")

    # Layer 8: Small Gear (150x150) - Pinion gear with 10 teeth
    gear_s = make_transparent_canvas(150, 150)
    draw = ImageDraw.Draw(gear_s)
    cx, cy, r_out, r_in = 75, 75, 55, 40
    draw.ellipse([(cx - r_out, cy - r_out), (cx + r_out, cy + r_out)], outline=(0, 229, 255, 255), width=3)
    draw.ellipse([(cx - r_in, cy - r_in), (cx + r_in, cy + r_in)], outline=(0, 229, 255, 255), width=2)
    draw.ellipse([(cx - 15, cy - 15), (cx + 15, cy + 15)], outline=(0, 229, 255, 255), width=2)
    # Draw 10 teeth
    for i in range(10):
        a_mid = i * (2 * math.pi / 10)
        a_w = 0.12
        p1 = (cx + r_in * math.cos(a_mid - a_w), cy + r_in * math.sin(a_mid - a_w))
        p2 = (cx + (r_out + 8) * math.cos(a_mid - a_w/2), cy + (r_out + 8) * math.sin(a_mid - a_w/2))
        p3 = (cx + (r_out + 8) * math.cos(a_mid + a_w/2), cy + (r_out + 8) * math.sin(a_mid + a_w/2))
        p4 = (cx + r_in * math.cos(a_mid + a_w), cy + r_in * math.sin(a_mid + a_w))
        draw.line([p1, p2, p3, p4], fill=(0, 229, 255, 255), width=3)
    gear_s.save(os.path.join(out_dir, "gear_small.png"))
    print("Generated Layer 8: gear_small.png")

    # Layer 9: Signal Oscillation Wave (500x200) - Rhythm sine wave
    wave_img = make_transparent_canvas(500, 200)
    draw = ImageDraw.Draw(wave_img)
    points = []
    # Plot sine wave line
    for x in range(0, 500, 10):
        y = 100 + 60 * math.sin(x * 0.05)
        points.append((x, y))
    draw.line(points, fill=(0, 230, 118, 255), width=4)
    # Core reference center line
    draw.line([(0, 100), (500, 100)], fill=(0, 230, 118, 100), width=1)
    wave_img.save(os.path.join(out_dir, "signal_wave.png"))
    print("Generated Layer 9: signal_wave.png")

    # Layer 10: Spec Data Box Overlay (300x120) - Tech hud overlay
    hud = make_transparent_canvas(300, 120)
    draw = ImageDraw.Draw(hud)
    # HUD outer frame
    draw.rectangle([(10, 10), (290, 110)], fill=(255, 235, 59, 30), outline=(255, 235, 59, 255), width=3)
    # Corner ticks
    draw.line([(5, 10), (5, 30)], fill=(255, 235, 59, 255), width=4)
    draw.line([(295, 10), (295, 30)], fill=(255, 235, 59, 255), width=4)
    draw.line([(5, 110), (5, 90)], fill=(255, 235, 59, 255), width=4)
    draw.line([(295, 110), (295, 90)], fill=(255, 235, 59, 255), width=4)
    # Status Text
    font_h = get_font(15, bold=True)
    draw.text((25, 25), "DRIVE STATS:", font=font_h, fill=(255, 235, 59, 255))
    draw.text((25, 50), "GEAR RATIO: 1:3.16", font=font_h, fill=(255, 235, 59, 255))
    draw.text((25, 75), "RPM STATUS: 1200 [OK]", font=font_h, fill=(255, 235, 59, 255))
    hud.save(os.path.join(out_dir, "spec_label.png"))
    print("Generated Layer 10: spec_label.png")
    
    print("="*60)
    print("SUCCESS: Generated all 10 custom 2D layer assets under scratch/layers!")
    print("="*60)

if __name__ == '__main__':
    main()
