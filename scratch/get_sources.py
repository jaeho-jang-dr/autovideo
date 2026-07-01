import subprocess
import os
import json
import sys

def main():
    # Force output encoding to utf-8 for safe printing
    sys.stdout.reconfigure(encoding='utf-8')
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    notebook_id = "cc6092e5-3322-44e8-b65e-dc0e85c2e3ed"
    
    # 1. List sources
    r = subprocess.run(
        ["nlm", "source", "list", notebook_id, "--json"],
        capture_output=True,
        env=env
    )
    
    if r.returncode != 0:
        print("Error listing sources:", r.stderr.decode('utf-8', errors='replace'))
        return
        
    try:
        sources = json.loads(r.stdout.decode('utf-8'))
        print(f"Total sources: {len(sources)}")
        
        # We will look for keywords in titles
        keywords = ["36", "커리큘럼", "주차", "curriculum", "syllabus", "주간", "week", "계획", "진도", "강의", "학습"]
        matching_sources = []
        
        for src in sources:
            title = src.get("title", "")
            src_id = src.get("id")
            src_type = src.get("type")
            
            # Check if title contains any keyword
            has_keyword = any(kw in title.lower() for kw in keywords)
            if has_keyword or src_type == "generated_text":
                matching_sources.append(src)
                
        print(f"Found {len(matching_sources)} potential curriculum sources.")
        for idx, src in enumerate(matching_sources):
            print(f"[{idx}] ID: {src.get('id')} | Type: {src.get('type')} | Title: {src.get('title')}")
            
        # Download contents of these sources and search for "36" or week structures inside content
        for src in matching_sources:
            src_id = src.get("id")
            title = src.get("title")
            print(f"\nChecking content of '{title}' (ID: {src_id})...")
            
            cr = subprocess.run(
                ["nlm", "source", "content", src_id],
                capture_output=True,
                env=env
            )
            if cr.returncode == 0:
                content_json = json.loads(cr.stdout.decode('utf-8'))
                content = content_json.get("value", {}).get("content", "")
                
                # Check if content has 36 weeks or W1-W36 mentions
                indicators = ["w1", "w36", "36주", "36 w", "week 1", "week 36", "커리큘럼"]
                has_indicator = any(ind in content.lower() for ind in indicators)
                
                if has_indicator:
                    print(f"!!! MATCH FOUND !!! Source '{title}' seems to contain the curriculum.")
                    filename = f"scratch/found_curriculum_{src_id}.md"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Saved content to {filename} (length: {len(content)} characters)")
            else:
                print(f"Failed to get content for {src_id}: {cr.stderr.decode('utf-8', errors='replace')}")
                
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
