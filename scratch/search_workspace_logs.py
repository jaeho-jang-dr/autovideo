import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

def main():
    print(f"Scanning workspace files under {ROOT}...")
    found = []
    
    extensions = ('.py', '.txt', '.md', '.json', '.log', '.sh', '.bat', '.ps1')
    
    # Avoid scanning big virtual envs or git directories
    exclude_dirs = {'.git', 'venv', 'node_modules', 'tempmediaStorage', '__pycache__'}
    
    for root_dir, dirs, files in os.walk(ROOT):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if not file.endswith(extensions):
                continue
                
            file_path = os.path.join(root_dir, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_no, line in enumerate(f, 1):
                        if "jay_whiteboard_consonants" in line:
                            rel_path = os.path.relpath(file_path, ROOT)
                            found.append((rel_path, line_no, line.strip()))
            except Exception:
                pass
                
    print(f"\nFound {len(found)} matches in workspace:")
    for path, line_no, line in found[:50]:
        print(f"  {path}:{line_no} -> {line[:200]}")

if __name__ == "__main__":
    main()
