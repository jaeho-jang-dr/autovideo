import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    # Read as utf-16le or fallback to utf-8 depending on how it was redirected
    try:
        with open("scratch/source_analysis_headings.txt", "r", encoding="utf-16") as f:
            content = f.read()
    except Exception:
        with open("scratch/source_analysis_headings.txt", "r", encoding="utf-8") as f:
            content = f.read()
            
    # Print the first 200 lines
    lines = content.splitlines()
    print("\n".join(lines[:200]))

if __name__ == '__main__':
    main()
