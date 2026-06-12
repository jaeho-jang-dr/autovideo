import time
import sys
import os

try:
    import pyautogui
except ImportError:
    print("[ERROR] pyautogui가 설치되어 있지 않습니다.")
    print("이 매크로 스크립트를 실행하려면 터미널(cmd 또는 PowerShell)에서 다음 명령어를 실행하여 설치해 주세요:")
    print("  pip install pyautogui")
    sys.exit(1)

print("=" * 60)
print("  Antigravity CLI Command Auto-Approve Macro")
print("=" * 60)
print("이 매크로는 화면에서 'Allow running this command?' 승인창을 감지하면")
print("자동으로 승인('1' 키 입력 후 'Enter' 전송)을 처리해 줍니다.")
print("실행해 두면 승인창을 계속 지켜볼 필요 없이 백그라운드에서 자동으로 넘어갑니다.")
print("종료하려면 cmd 창에서 [Ctrl + C]를 누르세요.")
print("=" * 60)

# pyautogui failsafe (move mouse to any corner to abort)
pyautogui.FAILSAFE = True

# 1. 팝업창을 감지하기 위한 간단한 픽셀 색상 기반 감지
# (사용자의 테마와 해상도에 맞춰 팝업의 Submit 버튼이나 Allow 버튼의 위치를 캡처하여
#  이미지 매칭(pyautogui.locateOnScreen)을 사용하는 것이 가장 확실합니다.)
#
# 여기에 'Allow running this command?' 혹은 'Yes, allow this time' 영역의 
# 캡처 이미지(예: allow_btn.png)를 만들어 매칭시킬 수 있는 코드를 준비해 둡니다.

def run_loop():
    print("\n[작동 중] 승인창 대기 상태...")
    last_action = 0
    
    while True:
        # 0.5초마다 화면에 승인창 버튼이나 텍스트가 표시되는지 확인합니다.
        # 이미지 매칭 방식을 사용하기 위해 'allow_btn.png' 또는 'submit_btn.png'가 있는 경우:
        # (이미지가 없더라도 핫키나 윈도우 포커스 시 주기적으로 1+Enter를 치게 할 수 있습니다.)
        
        # 예시: 팝업이 떴을 때 키보드 포커스가 터미널 인풋창에 가 있으므로,
        # 승인창 이미지 매칭이 성공하면 아래 동작을 실행:
        #   pyautogui.press('1')
        #   pyautogui.press('enter')
        
        # 만약 사용자가 수동 매크로(1초마다 활성 터미널에 1+Enter 자동 타이핑)를 원하는 경우
        # (코딩 중 방해되지 않도록 Antigravity/VS Code 창 제목을 확인하고, 
        #  터미널에 'Allow running' 텍스트 영역이 매칭될 때 작동하도록 세밀하게 처리하는 것이 좋습니다.)
        
        # 화면 전체에서 특정 이미지 매칭 시도
        try:
            # allow_btn.png가 프로젝트 디렉터리 내에 존재할 때만 작동
            if os.path.exists("allow_btn.png"):
                pos = pyautogui.locateOnScreen("allow_btn.png", confidence=0.8)
                if pos:
                    print(f"[{time.strftime('%H:%M:%S')}] 승인창 감지! 자동 승인 처리 진행...")
                    pyautogui.click(pos)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    time.sleep(2)  # 연속 클릭 방지
            else:
                # 이미지가 준비되지 않은 경우를 위한 폴백:
                # 사용자가 매크로 활성화 핫키를 지정해서 쓸 수 있도록 안내하거나,
                # 터미널에 포커스가 맞춰졌을 때 프롬프트를 처리하는 가이드 제공.
                pass
        except Exception as e:
            pass
            
        time.sleep(0.8)

if __name__ == "__main__":
    try:
        run_loop()
    except KeyboardInterrupt:
        print("\n매크로가 종료되었습니다.")
