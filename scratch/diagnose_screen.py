import pyautogui
import time
import os

def main():
    print("Taking diagnostic screenshot...")
    os.makedirs("debug", exist_ok=True)
    img = pyautogui.screenshot()
    img.save("debug/diagnostic_screen.png")
    w, h = img.size
    print(f"Screen resolution: {w}x{h}")
    
    # Scan for blue-ish button pixels and print a few matches
    matches = 0
    for x in range(0, w, 2):
        for y in range(0, h, 2):
            r, g, b = img.getpixel((x, y))
            # Typical google/bootstrap blue is R:66, G:133, B:244 or R:0, G:123, B:255
            # Let's check a wider range to see what colors exist
            if b > 180 and g > 80 and r < 100:
                matches += 1
                if matches <= 20:
                    print(f"Match {matches}: Pixel ({x}, {y}) -> RGB({r}, {g}, {b})")
                    
    print(f"Total blue-ish pixels found: {matches}")

if __name__ == "__main__":
    main()
