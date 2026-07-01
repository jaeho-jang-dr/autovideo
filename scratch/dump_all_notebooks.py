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
        print("Failed to list notebooks")
        return
        
    try:
        notebooks = json.loads(r.stdout.decode('utf-8'))
        print(f"Total notebooks in account: {len(notebooks)}")
        # Save to file
        with open("scratch/all_notebooks.json", "w", encoding="utf-8") as f:
            json.dump(notebooks, f, indent=2, ensure_ascii=False)
        print("Saved to scratch/all_notebooks.json")
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
