import json
from datetime import datetime
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    with open("scratch/all_notebooks.json", "r", encoding="utf-8") as f:
        notebooks = json.load(f)
        
    print("Top 20 most recently updated notebooks:")
    # Sort by updated_at desc
    sorted_nbs = sorted(notebooks, key=lambda x: x.get("updated_at", ""), reverse=True)
    for idx, nb in enumerate(sorted_nbs[:30]):
        nb_id = nb.get("id")
        title = nb.get("title")
        cnt = nb.get("source_count", 0)
        updated = nb.get("updated_at")
        print(f"[{idx}] ID: {nb_id} | Sources: {cnt} | Updated: {updated} | Title: {title}")

if __name__ == '__main__':
    main()
