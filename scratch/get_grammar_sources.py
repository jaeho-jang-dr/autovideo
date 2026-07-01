import subprocess
import os
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    notebook_id = "abfc75cd-00c6-4f12-8c48-000dadb907cd"
    print(f"Listing sources for notebook {notebook_id}...", flush=True)
    
    r = subprocess.run(
        ["nlm", "source", "list", notebook_id, "--json"],
        capture_output=True,
        env=env
    )
    
    if r.returncode != 0:
        print("Failed to list sources:", r.stderr.decode('utf-8', errors='replace'))
        return
        
    try:
        sources = json.loads(r.stdout.decode('utf-8'))
        print(f"Total sources: {len(sources)}")
        
        for idx, src in enumerate(sources):
            src_id = src.get("id")
            title = src.get("title")
            src_type = src.get("type")
            print(f"[{idx}] ID: {src_id} | Type: {src_type} | Title: {title}")
            
            # Download and search content
            print(f"  Downloading content for '{title}'...")
            cr = subprocess.run(
                ["nlm", "source", "content", src_id],
                capture_output=True,
                env=env
            )
            if cr.returncode == 0:
                content_json = json.loads(cr.stdout.decode('utf-8'))
                content = content_json.get("value", {}).get("content", "")
                
                # Save it to scratch
                filename = f"scratch/grammar_source_{src_id}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  Saved to {filename} (length: {len(content)} chars)")
            else:
                print(f"  Failed to get content: {cr.stderr.decode('utf-8', errors='replace')}")
                
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
