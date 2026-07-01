import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    with open("scratch/all_notebooks.json", "r", encoding="utf-8") as f:
        notebooks = json.load(f)
        
    # Find notebook cc6092e5-3322-44e8-b65e-dc0e85c2e3ed
    nb_id = "cc6092e5-3322-44e8-b65e-dc0e85c2e3ed"
    import subprocess
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(
        ["nlm", "source", "list", nb_id, "--json"],
        capture_output=True,
        env=env
    )
    if r.returncode != 0:
        print("Failed to load sources")
        return
        
    sources = json.loads(r.stdout.decode('utf-8'))
    print(f"Total sources: {len(sources)}")
    
    grammar_keywords = ["문법", "발음", "소리", "자음", "모음", "음운", "phonology", "grammar", "consonants", "vowels", "sound"]
    matches = []
    for idx, src in enumerate(sources):
        title = src.get("title", "")
        # Check if any keyword in title
        is_match = any(kw.lower() in title.lower() for kw in grammar_keywords)
        if is_match:
            matches.append((idx, src))
            
    print(f"Matches count: {len(matches)}")
    for idx, src in matches:
        print(f"[{idx}] ID: {src['id']} | Title: {src['title']}")

if __name__ == '__main__':
    main()
