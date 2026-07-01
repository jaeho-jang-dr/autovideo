import subprocess
import os
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    nb_id = "cc6092e5-3322-44e8-b65e-dc0e85c2e3ed"
    r = subprocess.run(
        ["nlm", "source", "list", nb_id, "--json"],
        capture_output=True,
        env=env
    )
    if r.returncode != 0:
        print("Failed to load source list")
        return
        
    sources = json.loads(r.stdout.decode('utf-8'))
    
    grammar_keywords = ["문법", "발음", "소리", "자음", "모음", "음운", "phonology", "grammar", "consonants", "vowels", "sound"]
    matching_sources = []
    for src in sources:
        title = src.get("title", "")
        if any(kw.lower() in title.lower() for kw in grammar_keywords):
            matching_sources.append(src)
            
    print(f"Downloading {len(matching_sources)} matching sources...")
    
    os.makedirs("scratch/grammar_sources", exist_ok=True)
    
    for idx, src in enumerate(matching_sources):
        src_id = src.get("id")
        title = src.get("title")
        print(f"[{idx+1}/{len(matching_sources)}] Downloading content for '{title}' (ID: {src_id})...")
        
        cr = subprocess.run(
            ["nlm", "source", "content", src_id],
            capture_output=True,
            env=env
        )
        if cr.returncode == 0:
            try:
                content_json = json.loads(cr.stdout.decode('utf-8'))
                content = content_json.get("value", {}).get("content", "")
                
                # Sanitize title for filename
                clean_title = "".join(c for c in title if c.isalnum() or c in " _-").strip()[:50]
                filename = f"scratch/grammar_sources/src_{idx:02d}_{clean_title}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  Saved to {filename} ({len(content)} chars)")
            except Exception as e:
                print(f"  Error parsing content: {e}")
        else:
            print(f"  Failed to download: {cr.stderr.decode('utf-8', errors='replace')}")

if __name__ == '__main__':
    main()
