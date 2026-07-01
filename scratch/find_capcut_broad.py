import os
import sys
import string
import shutil
import subprocess

def locate_draft_dir_globally():
    """
    Scans logical drives (C:, D:, etc.) for the 'com.lveditor.draft' directory.
    To avoid performance issues, we limit the search depth for non-user directories.
    """
    # 1. Determine local drives to search (typically C and D)
    drives = []
    for letter in string.ascii_uppercase:
        drive_path = f"{letter}:\\"
        if os.path.exists(drive_path):
            drives.append(drive_path)
            
    print(f"[Info] Found active drives: {drives}")
    
    # Common target folders to search specifically
    common_subfolders = [
        "AppData/Local/CapCut",
        "AppData/Local/JianyingPro",
        "CapCut",
        "JianyingPro",
        "Jianying",
        "Program Files/CapCut",
        "Program Files/JianyingPro",
        "Program Files (x86)/CapCut",
        "Program Files (x86)/JianyingPro",
    ]
    
    # 2. Check common directories first
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\Default")
    paths_to_check = []
    
    # Add paths relative to USERPROFILE
    for sub in common_subfolders:
        paths_to_check.append(os.path.join(user_profile, sub.replace("/", "\\")))
        
    # Add paths relative to each drive root
    for d in drives:
        for sub in common_subfolders:
            paths_to_check.append(os.path.join(d, sub.replace("/", "\\")))
            
    # Remove duplicates and filter existing directories
    dirs_to_scan = list(set([p for p in paths_to_check if os.path.exists(p)]))
    print(f"[Info] Scanning {len(dirs_to_scan)} potential CapCut base directories...")
    
    for base in dirs_to_scan:
        for root, dirs, files in os.walk(base):
            if "com.lveditor.draft" in dirs:
                found_path = os.path.join(root, "com.lveditor.draft")
                return found_path
                
    # 3. Fallback: Broad search on active drives (limited depth for efficiency)
    print("[Info] Performing broader search (depth-limited scan)...")
    for d in drives:
        print(f"  Scanning drive {d}...")
        try:
            # We list top-level directories
            for entry in os.scandir(d):
                if entry.is_dir():
                    # Skip system/huge directories to save time
                    if entry.name.lower() in ["windows", "system volume information", "$recycle.bin", "recovery", "programdata", "msocache"]:
                        continue
                    # Quick search inside this directory
                    for root, dirs, files in os.walk(entry.path):
                        # Limit depth to 4 levels
                        depth = root.replace(entry.path, "").count(os.sep)
                        if depth > 4:
                            # Skip scanning deeper subdirectories
                            dirs[:] = [] 
                            continue
                        if "com.lveditor.draft" in dirs:
                            return os.path.join(root, "com.lveditor.draft")
        except Exception as e:
            print(f"  [Warning] Failed to scan {d}: {e}")
            
    return None

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        
    print("="*60)
    print(" CapCut Broad Draft Finder & Copier")
    print("="*60)
    
    draft_dir = locate_draft_dir_globally()
    
    if not draft_dir:
        print("[Error] Could not locate 'com.lveditor.draft' folder anywhere on this PC.")
        print("        Please launch CapCut/Jianying, open a draft, and check Settings -> Draft location.")
        return
        
    print(f"[Success] Found CapCut draft folder at: {draft_dir}")
    
    # Source project
    src_project = os.path.abspath("scratch/mock_drafts/Autovideo_POC_Test")
    if not os.path.exists(src_project):
        print(f"[Error] Source project does not exist at: {src_project}")
        return

    # Copy to target draft directory
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
        
        # Try to search for executable in the same base path
        base_capcut = os.path.abspath(os.path.join(draft_dir, "..", "..", ".."))
        print(f"[Info] Searching for executable in: {base_capcut}")
        launched = False
        for root, dirs, files in os.walk(base_capcut):
            for f in files:
                if f in ["CapCut.exe", "JianyingPro.exe"]:
                    exe_path = os.path.join(root, f)
                    print(f"[Info] Found executable: {exe_path}. Launching...")
                    subprocess.Popen([exe_path])
                    launched = True
                    print("[Success] Launched CapCut!")
                    break
            if launched:
                break
                
        if not launched:
            print("[Info] Please launch CapCut Desktop manually to review the project 'Autovideo_POC_Test'.")
            
    except Exception as e:
        print(f"[Error] An error occurred: {e}")

if __name__ == '__main__':
    main()
