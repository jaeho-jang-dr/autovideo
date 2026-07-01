import sys
import os

try:
    from PIL import ImageGrab
    print("PIL imported successfully.")
    img = ImageGrab.grab(all_screens=True)
    print(f"Screen grabbed successfully. Size: {img.size}")
    
    # Save the screenshot to check visually
    save_path = os.path.join("scratch", "_screen_debug.png")
    img.save(save_path)
    print(f"Screenshot saved to: {save_path}")
    
except Exception as e:
    print(f"Error occurred during grab: {e}", file=sys.stderr)
