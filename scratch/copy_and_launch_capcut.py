import os
import shutil
import subprocess

def main():
    print("="*60)
    print(" Force Creating CapCut Draft Folder and Launching")
    print("="*60)
    
    # 1. Target draft directory (standard CapCut path)
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\antigravity")
    draft_dir = os.path.join(user_profile, r"AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
    
    print(f"[Info] Target draft path: {draft_dir}")
    
    # Create the directory structure if it doesn't exist
    if not os.path.exists(draft_dir):
        print(f"[Info] Target directory does not exist. Creating folder tree...")
        os.makedirs(draft_dir, exist_ok=True)
        print("[Success] Created directory tree.")
    else:
        print("[Info] Target directory already exists.")
        
    # 2. Source project
    src_project = os.path.abspath("scratch/mock_drafts/Autovideo_POC_Test")
    if not os.path.exists(src_project):
        print(f"[Error] Source project does not exist at: {src_project}")
        print("        Please run scratch/test_capcut_draft.py first.")
        return
        
    # 3. Copy project
    target_project = os.path.join(draft_dir, "Autovideo_POC_Test")
    print(f"[Info] Copying project folder...")
    print(f"  From: {src_project}")
    print(f"  To: {target_project}")
    
    try:
        if os.path.exists(target_project):
            shutil.rmtree(target_project)
        shutil.copytree(src_project, target_project)
        print("[Success] Project successfully copied to CapCut Draft folder!")
        
        # 4. Launch CapCut Desktop
        exe_path = os.path.join(user_profile, r"AppData\Local\CapCut\Apps\CapCut.exe")
        
        # Find version-specific executable (e.g. Apps/8.7.0.3685/CapCut.exe)
        version_exe = None
        apps_dir = os.path.join(user_profile, r"AppData\Local\CapCut\Apps")
        if os.path.exists(apps_dir):
            for item in os.listdir(apps_dir):
                item_path = os.path.join(apps_dir, item)
                if os.path.isdir(item_path) and item[0].isdigit():
                    v_exe = os.path.join(item_path, "CapCut.exe")
                    if os.path.exists(v_exe):
                        version_exe = v_exe
                        break
                        
        target_exe = version_exe if version_exe else exe_path
        if os.path.exists(target_exe):
            print(f"[Info] Selected CapCut executable: {target_exe}")
            print(f"[Info] Launching CapCut Desktop via PowerShell Start-Process...")
            work_dir = os.path.dirname(target_exe)
            cmd = f"powershell -Command \"Start-Process '{target_exe}' -WorkingDirectory '{work_dir}'\""
            subprocess.run(cmd, shell=True)
            print("[Success] CapCut launch command executed!")
        else:
            print("[Warning] CapCut executable not found. Please run CapCut manually.")
            
    except Exception as e:
        print(f"[Error] An error occurred: {e}")
        
    print("="*60)

if __name__ == '__main__':
    main()
