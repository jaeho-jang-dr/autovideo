# -*- coding: utf-8 -*-
"""
Antigravity 승인창 자동 클릭 스크립트 (Windows 전용 - 픽셀 감지 롤백 버전)
========================================================================
이 스크립트는 Electron의 내부 UIA 트리 접근성 차단 문제를 우회하기 위해,
화면 픽셀 캡처 방식으로 파란색 'Submit' 버튼을 감지하여 클릭 및 Enter 처리를 수행합니다.

설치:
    pip install pyautogui pillow

실행 (사용자의 실제 화면 세션 CMD/PowerShell 창에서 직접 실행):
    python scratch/auto_approve.py

종료: Ctrl+C
"""

import time
import sys

try:
    import pyautogui
    from PIL import ImageGrab
except ImportError:
    print("pyautogui 및 pillow 패키지가 필요합니다:  pip install pyautogui pillow")
    sys.exit(1)

# Fail-safe 활성화 (마우스를 화면 네 구석으로 강제 이동 시 매크로 중단)
pyautogui.FAILSAFE = True

# 감지 주기 (초)
POLL_INTERVAL = 0.2

# 구글/Antigravity 블루 계열 Submit 버튼의 픽셀 색상 기준
# R: 0 ~ 95, G: 90 ~ 200, B: 200 ~ 255
def find_submit_button_coords():
    try:
        # 윈도우 다중 모니터를 포괄하기 위해 all_screens=True 필수 사용 (Session 0 우회)
        img = ImageGrab.grab(all_screens=True)
        w, h = img.size
        
        # 속도를 위해 6픽셀 간격으로 빠르게 스캔
        for x in range(0, w, 6):
            for y in range(0, h, 6):
                r, g, b = img.getpixel((x, y))
                # 블루 계열 색조 필터링
                if r < 95 and (90 <= g <= 200) and (200 <= b <= 255):
                    # 연속되는 블루 픽셀 패턴을 확인하여 노이즈 필터링
                    if x + 15 < w:
                        nr, ng, nb = img.getpixel((x + 15, y))
                        if nr < 95 and (90 <= ng <= 200) and (200 <= nb <= 255):
                            # 버튼의 중심부 근처 좌표 반환
                            return x + 5, y
        return None
    except Exception:
        return None

def main():
    # 콘솔 실시간 출력 버퍼링 해제
    sys.stdout.reconfigure(line_buffering=True)
    print("=" * 60)
    print("  Antigravity 화면 캡처 자동 승인 매크로 시작")
    print("  (실제 모니터 화면에서 작동하며 마우스를 직접 움직여 클릭합니다)")
    print("  종료하려면 마우스를 화면 구석 끝으로 급히 이동시키거나 Ctrl+C를 누르세요.")
    print("=" * 60)
    
    approved_count = 0
    last_click_time = 0
    
    while True:
        try:
            pos = find_submit_button_coords()
            if pos:
                now = time.time()
                # 1.5초 이내 중복 클릭 방지
                if now - last_click_time > 1.5:
                    cx, cy = pos
                    orig_x, orig_y = pyautogui.position()
                    
                    print(f"[{time.strftime('%H:%M:%S')}] 파란색 Submit 버튼 감지! 좌표: ({cx}, {cy})")
                    
                    # 1. 마우스 순간 이동 및 클릭
                    pyautogui.moveTo(cx, cy)
                    time.sleep(0.05)
                    pyautogui.click(cx, cy)
                    time.sleep(0.05)
                    
                    # 2. Enter 키로 승인 전송
                    pyautogui.press('enter')
                    
                    # 3. 마우스 커서 원래 위치로 0.05초 만에 신속 복원
                    pyautogui.moveTo(orig_x, orig_y)
                    
                    approved_count += 1
                    last_click_time = now
                    print(f"[처리] 자동 승인 완료 ✔ (누적 {approved_count}회)")
                    
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n매크로를 종료합니다.")
            break
        except Exception as e:
            print(f"[오류 발생] {e}")
            time.sleep(1.0)

if __name__ == "__main__":
    main()
