import subprocess
import os
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    print("Listing notebooks...", flush=True)
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
        for idx, nb in enumerate(notebooks):
            nb_id = nb.get("id")
            title = nb.get("title")
            cnt = nb.get("source_count", 0)
            print(f"[{idx}] ID: {nb_id} | Sources: {cnt} | Title: {title}")
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
