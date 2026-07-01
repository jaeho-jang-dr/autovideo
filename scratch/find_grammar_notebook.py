import subprocess
import os
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    print("Fetching all notebooks from NotebookLM to search for grammar...", flush=True)
    r = subprocess.run(
        ["nlm", "notebook", "list", "--json"],
        capture_output=True,
        env=env
    )
    
    if r.returncode != 0:
        print("Failed to list notebooks:", r.stderr.decode('utf-8', errors='replace'))
        return
        
    try:
        notebooks = json.loads(r.stdout.decode('utf-8'))
        print(f"Total notebooks found: {len(notebooks)}")
        
        keywords = ["문법", "grammar", "한글", "hangeul", "korean", "발음", "쓰기", "조음"]
        matches = []
        for nb in notebooks:
            title = nb.get("title", "")
            nb_id = nb.get("id")
            
            # Check if any keyword matches
            has_kw = any(kw in title.lower() for kw in keywords)
            if has_kw:
                matches.append(nb)
                
        print(f"\n--- Found {len(matches)} matching notebooks ---")
        for idx, m in enumerate(matches):
            print(f"[{idx}] ID: {m.get('id')} | Title: {m.get('title')} | Updated: {m.get('updated_at')}")
            
    except Exception as e:
        print("Error parsing notebooks:", e)

if __name__ == '__main__':
    main()
