import time
import sys
import os

try:
    import pyautogui
except ImportError:
    print("[ERROR] pyautogui가 로드되지 않았습니다. 설치를 먼저 대기합니다.")
    sys.exit(1)

# pyautogui failsafe (Aborts macro if you move mouse to screen corner)
pyautogui.FAILSAFE = True

# Submit button blue range: R(0~95), G(90~195), B(200~255)
def find_submit_button():
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab(all_screens=True)
        w, h = img.size
        # Scan in 5px steps for speed
        for x in range(0, w, 5):
            for y in range(0, h, 5):
                r, g, b = img.getpixel((x, y))
                if r < 95 and (90 <= g <= 195) and (200 <= b <= 255):
                    # Found a blue pixel (part of the Submit button).
                    if x + 10 < w:
                        nr, ng, nb = img.getpixel((x + 10, y))
                        if nr < 95 and (90 <= ng <= 195) and (200 <= nb <= 255):
                            return x + 5, y
        return None
    except Exception as e:
        # Silently log error to console without breaking loop
        return None

def run_loop():
    print("=" * 60)
    print("  Antigravity CLI Submit Auto-Clicker Macro")
    print("=" * 60)
    print("이 매크로는 백그라운드에서 실행되며, 명령어 승인 팝업이 나타나면")
    print("자동으로 'Submit' 버튼을 감지하여 클릭 및 Enter 처리를 수행합니다.")
    print("=" * 60)
    
    last_clicked = 0
    while True:
        pos = find_submit_button()
        if pos:
            now = time.time()
            # Prevent double-clicks within 1 second
            if now - last_clicked > 1:
                cx, cy = pos
                orig_x, orig_y = pyautogui.position()
                
                print(f"[{time.strftime('%H:%M:%S')}] 승인창(Submit) 감지! 마우스 이동 -> 클릭 -> Enter 처리...")
                
                # Precise execution: Move -> Click -> Wait -> Enter -> Restore
                pyautogui.moveTo(cx, cy)
                time.sleep(0.05)
                pyautogui.click(cx, cy)
                time.sleep(0.05)
                pyautogui.press('enter')
                pyautogui.moveTo(orig_x, orig_y)
                
                last_clicked = now
        time.sleep(0.1)


if __name__ == "__main__":
    # Ensure stdout is unbuffered
    sys.stdout.reconfigure(line_buffering=True)
    try:
        run_loop()
    except KeyboardInterrupt:
        print("\n매크로를 종료합니다.")




