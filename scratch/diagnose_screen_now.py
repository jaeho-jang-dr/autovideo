from PIL import ImageGrab
import os

try:
    img = ImageGrab.grab(all_screens=True)
    output_path = r"C:\Users\antigravity\.gemini\antigravity\brain\99ee31f7-6993-45ae-8bf1-d0bca2012f45\current_screen.png"
    img.save(output_path)
    print(f"Screenshot successfully saved to: {output_path}")
except Exception as e:
    print(f"Failed to grab screen: {e}")
