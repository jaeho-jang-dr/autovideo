from PIL import ImageGrab
import os

try:
    img = ImageGrab.grab(all_screens=True)
    output_path = r"C:\Users\antigravity\.gemini\antigravity\brain\f7188fe7-133d-439f-a5c8-42a7cb837176\current_screen.png"
    img.save(output_path)
    print(f"Screen shot saved to {output_path}")
except Exception as e:
    print(f"Failed to grab screen: {e}")
