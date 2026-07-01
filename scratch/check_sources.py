import os
import sys
import json
import subprocess

# Reconfigure stdout to output utf-8 safely
sys.stdout.reconfigure(encoding='utf-8')

def run_nlm_cmd(args):
    cmd = ["nlm"] + args
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        shell=True
    )
    if result.returncode != 0:
        print(f"Failed: {result.stderr}")
        return None
    return result.stdout.strip()

notebook_id = "cc6092e5-3322-44e8-b65e-dc0e85c2e3ed"
print(f"Listing sources for notebook {notebook_id}...")
out = run_nlm_cmd(["source", "list", notebook_id, "--json"])
if out:
    try:
        sources = json.loads(out)
        print(f"Total sources: {len(sources)}")
        for src in sources:
            title = src.get("title", "")
            src_id = src.get("id", "")
            # Encode to ascii/ignore if needed, but since stdout is utf-8, it should print nicely
            print(f"Source -> ID: {src_id}, Title: {title}")
    except Exception as e:
        print(f"Error parsing: {e}")
        print(out[:1000])
