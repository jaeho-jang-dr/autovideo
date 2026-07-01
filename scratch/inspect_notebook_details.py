import subprocess
import os
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    r = subprocess.run(
        ["nlm", "notebook", "list", "--json"],
        capture_output=True,
        env=env
    )
    
    if r.returncode != 0:
        return
        
    notebooks = json.loads(r.stdout.decode('utf-8'))
    for nb in notebooks:
        nb_id = nb.get("id")
        title = nb.get("title", "")
        cnt = nb.get("source_count", 0)
        
        if nb_id == "cc6092e5-3322-44e8-b65e-dc0e85c2e3ed" or "한글" in title or "문법" in title:
            print(f"MATCH -> ID: {nb_id} | Sources: {cnt} | Title: {title}")

if __name__ == '__main__':
    main()
