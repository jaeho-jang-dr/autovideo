import time
import uiautomation as auto

def main():
    print("="*60)
    print(" CapCut Project Double-Clicker (UI Automation)")
    print("="*60)
    
    # 1. Search for the CapCut Window
    capcut_win = None
    root = auto.GetRootControl()
    
    for win in root.GetChildren():
        title = win.Name
        if title and ("capcut" in title.lower() or "jianying" in title.lower() or "剪映" in title):
            capcut_win = win
            print(f"[Info] Found CapCut Window: '{title}'")
            break
            
    if not capcut_win:
        print("[Error] CapCut window not found. Please make sure the CapCut PC app is open and visible.")
        return
        
    # 2. Activate and focus the CapCut window
    try:
        capcut_win.SetActive()
        capcut_win.SetFocus()
        capcut_win.ShowWindow(auto.ShowWindowMode.Maximize) # Maximize to ensure it is visible
        time.sleep(1.5)
        print("[Info] Activated and focused CapCut window.")
    except Exception as e:
        print(f"[Warning] Failed to activate window: {e}")
        
    # 3. Find the project element recursively
    target_element = None
    
    def search_target(control, depth=0):
        nonlocal target_element
        if target_element is not None:
            return
        if depth > 12:
            return
            
        name = control.Name
        if name and ("autovid" in name.lower() or "autovide" in name.lower() or "poc_test" in name.lower()):
            target_element = control
            print(f"[Info] Found element: {control.ControlTypeName} -> '{name}' (Depth: {depth})")
            return
            
        for child in control.GetChildren():
            search_target(child, depth + 1)

    print("[Info] Scanning UI Automation tree for draft name...")
    search_target(capcut_win)
    
    if not target_element:
        print("[Error] Could not find the 'Autovideo_POC_Test' project in the UI tree.")
        # Dump top-level to diagnose
        print("[Info] Diagnosing UI Tree. Top level children:")
        for child in capcut_win.GetChildren():
            print(f"  - {child.ControlTypeName}: '{child.Name}'")
        return
        
    # 4. Double click
    try:
        rect = target_element.BoundingRectangle
        print(f"[Info] Target bounds: Left={rect.left}, Top={rect.top}, Right={rect.right}, Bottom={rect.bottom}")
        
        # UI Automation double click
        print(f"[Action] Double-clicking project: '{target_element.Name}'")
        target_element.DoubleClick()
        print("[Success] Project opened successfully!")
        
    except Exception as e:
        print(f"[Error] Failed to click target: {e}")
        
    print("="*60)

if __name__ == '__main__':
    main()
