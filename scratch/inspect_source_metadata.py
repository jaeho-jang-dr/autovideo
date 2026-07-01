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
    if sources:
        print("Fields in source object:", list(sources[0].keys()))
        print("Sample object:", json.dumps(sources[0], indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
