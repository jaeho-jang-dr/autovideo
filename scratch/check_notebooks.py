import os
import sys
import json
import subprocess

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

print("Listing notebooks...")
out = run_nlm_cmd(["notebook", "list", "--json"])
if out:
    try:
        notebooks = json.loads(out)
        for nb in notebooks:
            title = nb.get("title", "")
            nb_id = nb.get("id", "")
            if "한글" in title or "Hangul" in title or "hangeul" in title.lower():
                print(f"Found Match -> ID: {nb_id}, Title: {title}, Sources: {nb.get('source_count')}")
    except Exception as e:
        print(f"Error parsing: {e}")
