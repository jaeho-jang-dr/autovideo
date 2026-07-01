import subprocess
import os
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    notebook_id = "cc6092e5-3322-44e8-b65e-dc0e85c2e3ed"
    r = subprocess.run(
        ["nlm", "source", "list", notebook_id, "--json"],
        capture_output=True,
        env=env
    )
    
    if r.returncode != 0:
        return
        
    sources = json.loads(r.stdout.decode('utf-8'))
    print(f"Total: {len(sources)}")
    for idx, src in enumerate(sources):
        src_id = src.get("id")
        title = src.get("title")
        src_type = src.get("type")
        url = src.get("url", "")
        print(f"[{idx:02d}] ID: {src_id} | Type: {src_type} | Title: {title} | Url: {url}")

if __name__ == '__main__':
    main()
