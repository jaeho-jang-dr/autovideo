import sqlite3

def main():
    conn = sqlite3.connect('channel/content.db')
    cur = conn.cursor()
    
    print("=== Categories ===")
    cur.execute("SELECT * FROM categories")
    for row in cur.fetchall():
        print(row)
        
    print("\n=== Episodes containing Korean or Hangul ===")
    cur.execute("SELECT code, category, title_kr, title_en, status FROM episodes WHERE title_kr LIKE '%한글%' OR title_kr LIKE '%한국어%' OR title_en LIKE '%Korean%' OR title_en LIKE '%Hangul%' OR code LIKE 'KO%'")
    rows = cur.fetchall()
    print(f"Found {len(rows)} episodes:")
    for row in rows:
        print(row)
        
    print("\n=== All Web Lessons ===")
    cur.execute("SELECT * FROM web_lessons")
    web_rows = cur.fetchall()
    print(f"Found {len(web_rows)} web lessons:")
    for row in web_rows[:20]:
        print(row)
        
    print("\n=== SQLite Version & Metadata ===")
    cur.execute("SELECT * FROM channel_meta")
    for row in cur.fetchall():
        print(row)

if __name__ == '__main__':
    main()
