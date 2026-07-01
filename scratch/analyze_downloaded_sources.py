import os
import re
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    src_dir = "scratch/grammar_sources"
    files = sorted(os.listdir(src_dir))
    
    print(f"Analyzing {len(files)} grammar sources:")
    for f in files:
        if not f.endswith(".md"):
            continue
        filepath = os.path.join(src_dir, f)
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
            
        # Find headings
        headings = re.findall(r"^(#+)\s+(.*)$", content, re.MULTILINE)
        print(f"\n=========================================")
        print(f"File: {f}")
        print(f"Length: {len(content)} chars")
        print(f"Headings (first 6):")
        for lvl, title in headings[:6]:
            print(f"  {lvl} {title}")

if __name__ == '__main__':
    main()
