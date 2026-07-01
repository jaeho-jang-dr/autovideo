import os
import sys
import winreg
import shutil
import subprocess

def search_registry(key_root, sub_key):
    """
    Search registry keys for CapCut/Jianying/剪映
    """
    results = []
    try:
        with winreg.OpenKey(key_root, sub_key) as key:
            info = winreg.QueryInfoKey(key)
            for i in range(info[0]): # number of subkeys
                try:
                    name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, name) as subkey:
                        try:
                            display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            if any(x in display_name.lower() for x in ["capcut", "jianying", "剪映"]):
                                install_loc, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                                results.append((display_name, install_loc))
                        except WindowsError:
                            pass
                except WindowsError:
                    pass
    except WindowsError:
        pass
    return results

def get_installed_paths():
    roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    paths = []
    for root, sub_key in roots:
        res = search_registry(root, sub_key)
        if res:
            paths.extend(res)
    return paths

def locate_draft_dir_recursively(base_dir):
    """
    Look for com.lveditor.draft directory under base_dir recursively but quickly.
    """
    if not os.path.exists(base_dir):
        return None
    for root, dirs, files in os.walk(base_dir):
        if "com.lveditor.draft" in dirs:
            return os.path.join(root, "com.lveditor.draft")
    return None

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        
    print("="*60)
    print(" CapCut Draft Locator and Copier")
    print("="*60)
    
    # 1. Search in registry
    installations = get_installed_paths()
    print("[Registry] Search results:")
    for name, loc in installations:
        print(f"  - Name: {name}, Location: {loc}")
        
    # 2. Try common base directories
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\Default")
    base_paths = [
        os.path.join(user_profile, r"AppData\Local\CapCut"),
        os.path.join(user_profile, r"AppData\Local\JianyingPro"),
    ]
    
    # Also add install paths from registry if found
    for name, loc in installations:
        if loc and os.path.exists(loc):
            base_paths.append(loc)
            
    draft_dir = None
    for base in base_paths:
        if os.path.exists(base):
            print(f"[Info] Scanning subdirectories in: {base}")
            found = locate_draft_dir_recursively(base)
            if found:
                draft_dir = found
                print(f"[Success] Found draft directory: {draft_dir}")
                break
                
    if not draft_dir:
        # Check standard AppData Local directly, maybe just CapCut or JianyingPro exists
        capcut_local = os.path.join(user_profile, r"AppData\Local")
        # Try to scan just CapCut and JianyingPro directories specifically to save time
        for name in ["CapCut", "JianyingPro"]:
            p = os.path.join(capcut_local, name)
            if os.path.exists(p):
                print(f"[Info] Scanning standard path: {p}")
                found = locate_draft_dir_recursively(p)
                if found:
                    draft_dir = found
                    print(f"[Success] Found draft directory: {draft_dir}")
                    break

    if not draft_dir:
        print("[Error] Could not find the actual 'com.lveditor.draft' directory on this PC.")
        print("        CapCut or Jianying might not be installed, or has not been run at least once.")
        return

    # 3. Source project
    src_project = os.path.abspath("scratch/mock_drafts/Autovideo_POC_Test")
    if not os.path.exists(src_project):
        print(f"[Error] Source project does not exist at: {src_project}")
        print("        Please run scratch/test_capcut_draft.py first.")
        return

    # 4. Copy to target draft directory
    target_project = os.path.join(draft_dir, "Autovideo_POC_Test")
    print(f"[Info] Copying project...")
    print(f"  From: {src_project}")
    print(f"  To: {target_project}")
    
    try:
        if os.path.exists(target_project):
            shutil.rmtree(target_project)
        shutil.copytree(src_project, target_project)
        print("[Success] Project successfully copied to CapCut Draft folder!")
        print("="*60)
        
        # 5. Attempt to launch CapCut Desktop if executable is found
        executable_paths = [
            os.path.join(user_profile, r"AppData\Local\CapCut\Apps\CapCut.exe"),
            os.path.join(user_profile, r"AppData\Local\JianyingPro\Apps\JianyingPro.exe")
        ]
        # Also look in installations registry locations
        for name, loc in installations:
            if loc:
                for root, dirs, files in os.walk(loc):
                    for f in files:
                        if f in ["CapCut.exe", "JianyingPro.exe"]:
                            executable_paths.append(os.path.join(root, f))
                            
        launched = False
        for exe in executable_paths:
            if os.path.exists(exe):
                print(f"[Info] Found CapCut executable: {exe}")
                print(f"[Info] Launching CapCut Desktop application...")
                subprocess.Popen([exe])
                launched = True
                print("[Success] CapCut has been successfully launched!")
                break
                
        if not launched:
            print("[Info] Could not automatically find the CapCut executable. Please launch CapCut manually.")
            print("        The project 'Autovideo_POC_Test' is now available in your drafts list!")
            
    except Exception as e:
        print(f"[Error] An error occurred during copy or launch: {e}")

if __name__ == '__main__':
    main()
