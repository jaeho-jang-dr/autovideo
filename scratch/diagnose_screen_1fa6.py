from PIL import ImageGrab
import os

try:
    img = ImageGrab.grab(all_screens=True)
    output_path = r"C:\Users\antigravity\.gemini\antigravity-cli\brain\1fa6c20c-c4f7-4761-b6a2-494cc46fb69d\current_screen.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print("Screenshot successfully saved to: " + output_path)
except Exception as e:
    print("Failed to grab screen: " + str(e))
