import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    with open("scratch/all_notebooks.json", "r", encoding="utf-8") as f:
        notebooks = json.load(f)
        
    print("Notebooks with 15-30 sources:")
    for nb in notebooks:
        title = nb.get("title", "")
        cnt = nb.get("source_count", 0)
        nb_id = nb.get("id")
        if 15 <= cnt <= 30:
            print(f"ID: {nb_id} | Sources: {cnt} | Title: {title}")

if __name__ == '__main__':
    main()
