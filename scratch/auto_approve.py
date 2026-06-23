"""
Antigravity CLI 자동 승인 매크로 v7 (최종)
============================================
전략: UIA로 감지 → 마우스 순간이동 클릭(~50ms) → 즉시 원위치 복원
Electron/Chromium은 진짜 마우스 이벤트만 처리하므로 이것이 유일한 방법.
마우스 순간이동 시간: ~50ms (체감 불가)
"""
import time
import sys
import ctypes
from ctypes import wintypes

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    import uiautomation as auto
except ImportError:
    print("[오류] pip install uiautomation")
    input("Enter...")
    sys.exit(1)

# ── Win32 ──
user32 = ctypes.windll.user32
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP   = 0x0004

# ── 설정 ──
LOOP_INTERVAL  = 1.5
SEARCH_TIMEOUT = 0.3
SEARCH_DEPTH   = 25
COOLDOWN       = 2.5
DANGER_PATTERNS = ["rm -rf", "format", "del /s", "shutdown", "powercfg", "mkfs", "dd if="]


def ts():
    return time.strftime('%H:%M:%S')


def flash_click(screen_x, screen_y):
    """마우스를 순간이동시켜 클릭하고 즉시 원위치로 복원한다. 총 ~50ms."""
    # 1. 현재 위치 저장
    saved = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(saved))
    
    # 2. 순간이동
    user32.SetCursorPos(screen_x, screen_y)
    
    # 3. 마우스 다운/업 (mouse_event — 가장 빠르고 확실한 방법)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.02)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
    # 4. 즉시 복원
    time.sleep(0.02)
    user32.SetCursorPos(saved.x, saved.y)


def find_antigravity_window():
    for sub in ["Antigravity", "antigravity"]:
        try:
            w = auto.WindowControl(searchDepth=3, SubName=sub)
            if w.Exists(maxSearchSeconds=0.2):
                return w
        except Exception:
            pass
    return None


def find_allow():
    ag = find_antigravity_window()
    root = ag if ag else None
    
    for name in ["Yes, allow this time", "Yes, allow"]:
        try:
            c = (root or auto).Control(searchDepth=SEARCH_DEPTH, Name=name)
            if c.Exists(maxSearchSeconds=SEARCH_TIMEOUT):
                return c, name
        except Exception:
            pass
    
    try:
        c = (root or auto).Control(searchDepth=SEARCH_DEPTH, SubName="allow this time")
        if c.Exists(maxSearchSeconds=SEARCH_TIMEOUT):
            return c, "allow this time"
    except Exception:
        pass
    
    return None, None


def find_submit():
    ag = find_antigravity_window()
    root = ag if ag else None
    
    for name in ["Submit"]:
        try:
            c = (root or auto).ButtonControl(searchDepth=SEARCH_DEPTH, Name=name)
            if c.Exists(maxSearchSeconds=SEARCH_TIMEOUT):
                return c, name
        except Exception:
            pass
        try:
            c = (root or auto).Control(searchDepth=SEARCH_DEPTH, Name=name)
            if c.Exists(maxSearchSeconds=SEARCH_TIMEOUT):
                return c, name
        except Exception:
            pass
    
    return None, None


def get_center(ctrl):
    """컨트롤의 화면 중앙 좌표를 반환한다."""
    try:
        r = ctrl.BoundingRectangle
        return int((r.left + r.right) / 2), int((r.top + r.bottom) / 2)
    except Exception:
        return None, None


def check_danger():
    try:
        for c in auto.GetRootControl().GetChildren():
            for ch in c.GetChildren():
                t = ch.Name or ""
                for p in DANGER_PATTERNS:
                    if p in t:
                        print(f"[{ts()}] ⚠ 위험: '{p}' 차단!")
                        return True
    except Exception:
        pass
    return False


def run_loop():
    print("=" * 60)
    print("  Antigravity 자동 승인 매크로 v7 (최종)")
    print("=" * 60)
    print("  마우스 순간이동 클릭 (~50ms) + 즉시 원위치 복원")
    print("  종료: Ctrl+C")
    print("=" * 60)
    print(f"[{ts()}] 대기 중...\n")

    count = 0
    while True:
        try:
            # 1. "Yes, allow this time" 감지 및 클릭
            ac, an = find_allow()
            if ac:
                if check_danger():
                    time.sleep(5)
                    continue
                
                ax, ay = get_center(ac)
                if ax and ay:
                    print(f"[{ts()}] 🔍 '{an}' 감지 → ({ax},{ay})")
                    flash_click(ax, ay)
                    print(f"[{ts()}]   → 클릭 완료")
                    time.sleep(0.5)
                    
                    # 2. "Submit" 감지 및 클릭
                    sc, sn = find_submit()
                    if sc:
                        sx, sy = get_center(sc)
                        if sx and sy:
                            print(f"[{ts()}] 🔍 '{sn}' 감지 → ({sx},{sy})")
                            flash_click(sx, sy)
                            count += 1
                            print(f"[{ts()}] ✅ 승인 완료! (누적 {count}회)\n")
                
                time.sleep(COOLDOWN)
                continue
            
            # Submit만 단독 감지
            sc, sn = find_submit()
            if sc:
                if check_danger():
                    time.sleep(5)
                    continue
                sx, sy = get_center(sc)
                if sx and sy:
                    print(f"[{ts()}] 🔍 '{sn}' 단독 → ({sx},{sy})")
                    flash_click(sx, sy)
                    count += 1
                    print(f"[{ts()}] ✅ 승인 완료! (누적 {count}회)\n")
                time.sleep(COOLDOWN)
                continue
        
        except Exception as e:
            print(f"[{ts()}] [에러] {e}")
        
        time.sleep(LOOP_INTERVAL)


if __name__ == "__main__":
    try:
        run_loop()
    except KeyboardInterrupt:
        print(f"\n[{ts()}] 종료.")
