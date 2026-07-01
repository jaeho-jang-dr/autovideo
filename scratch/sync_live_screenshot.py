import os
import time
import shutil

SRC = r"d:\Entertainments\DevEnvironment\autovideo\debug\_live.png"
DST = r"C:\Users\antigravity\.gemini\antigravity\brain\ea11ac2b-77b0-4d5a-98ea-c249b22ddb89\live_screenshot.png"
MONITOR = r"C:\Users\antigravity\.gemini\antigravity\brain\ea11ac2b-77b0-4d5a-98ea-c249b22ddb89\live_monitor.md"

def update_monitor():
    now_str = time.strftime("%H:%M:%S")
    content = f"""# Google Flow 실시간 모니터링 보드 (Live Monitor)

현재 백그라운드에서 구글 Flow 크롬 브라우저가 기동하여 에셋을 생성하고 있습니다.
윈도우 세션 격리로 인해 브라우저 창이 직접 바탕화면에 보이지 않더라도, 아래 실시간 화면 캡처를 통해 작업 상태를 즉시 모니터링하실 수 있습니다.

---

## 📸 실시간 구글 Flow 컴포저 화면 (최근 갱신: {now_str})
![실시간 구글 Flow 화면](file:///{DST.replace('\\', '/')})

> [!NOTE]
> * **현재 작업**: 에셋을 순차적으로 자동 입력(`Ctrl+V`) 및 생성 중입니다.
> * **화면 자동 갱신**: 3초마다 자동으로 캡처된 화면이 이 문서에 갱신됩니다. 문서 창을 열어 두시면 실시간 진행 상황을 보실 수 있습니다.
"""
    with open(MONITOR, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    print("Syncing live screenshots...", flush=True)
    last_mtime = 0
    while True:
        if os.path.exists(SRC):
            try:
                mtime = os.path.getmtime(SRC)
                if mtime != last_mtime:
                    shutil.copy2(SRC, DST)
                    update_monitor()
                    last_mtime = mtime
                    print(f"[{time.strftime('%H:%M:%S')}] Screenshot synchronized.", flush=True)
            except Exception as e:
                print(f"Error copying: {e}", flush=True)
        time.sleep(2)

if __name__ == '__main__':
    main()
