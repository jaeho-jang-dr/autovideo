import uiautomation as auto
import sys

# stdout/stderr의 한글 깨짐 방지
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

def dump_simulation_window():
    print("=" * 60)
    print("  UI Automation Control Tree Dumper (Simulation Window)")
    print("=" * 60)
    
    # 1. 시뮬레이션 창 탐색
    window = None
    # 타이틀 이름으로 윈도우 탐색
    for name in ["Antigravity Approval Simulation Dialog", "Antigravity Approval Simulation"]:
        win = auto.WindowControl(searchDepth=4, Name=name)
        if win.Exists(maxSearchSeconds=0.5):
            window = win
            break
            
    if not window:
        print("[오류] 시뮬레이션 팝업창을 찾을 수 없습니다.")
        print("가상 팝업창(test_gui_popup.py)이 화면에 켜져 있는지 확인해 주세요.")
        return
        
    print(f"✔ 시뮬레이션 창 감지 성공! (HWND: {window.NativeWindowHandle})")
    print("자식 컨트롤 구조를 분석하여 출력합니다:\n")
    
    def walk_tree(control, depth=0):
        indent = "  " * depth
        try:
            control_type = control.ControlTypeName or "Unknown"
            name = control.Name or ""
            class_name = control.ClassName or ""
            automation_id = control.AutomationId or ""
            print(f"{indent}* Type: {control_type} | Name: '{name}' | Class: '{class_name}' | AutoId: '{automation_id}'")
        except Exception as e:
            print(f"{indent}[Error reading control node: {e}]")
            
        try:
            for child in control.GetChildren():
                walk_tree(child, depth + 1)
        except Exception:
            pass
            
    walk_tree(window)
    print("=" * 60)

if __name__ == "__main__":
    dump_simulation_window()
