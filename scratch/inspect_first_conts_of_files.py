import os
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    src_dir = "scratch/grammar_sources"
    files = sorted(os.listdir(src_dir))
    
    # Print first 800 chars of top 5 files
    for idx, f in enumerate(files[:5]):
        filepath = os.path.join(src_dir, f)
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
        print(f"\n=========================================")
        print(f"File: {f}")
        print(content[:800])
        print("...")

if __name__ == '__main__':
    main()
