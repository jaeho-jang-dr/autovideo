import sqlite3
import sys

# Set standard output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def inspect():
    conn = sqlite3.connect('channel/content.db')
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print("Tables:", tables)
    
    # Keyword search across tables
    keywords = ['gonstead', 'sitting', 'chiropract', 'diversified', 'jieun', 'injoon']
    print("\n--- Keyword Search Results ---")
    for table in tables:
        # Get columns
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Check text columns
        text_cols = []
        for col in columns:
            cursor.execute(f"SELECT typeof({col}) FROM {table} LIMIT 1;")
            res = cursor.fetchone()
            if res and res[0] in ('text', 'blob'):
                text_cols.append(col)
                
        if not text_cols:
            continue
            
        # Build query
        where_clauses = []
        for col in text_cols:
            for kw in keywords:
                where_clauses.append(f"LOWER({col}) LIKE '%{kw}%'")
                
        if where_clauses:
            query = f"SELECT * FROM {table} WHERE " + " OR ".join(where_clauses)
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                if rows:
                    print(f"Table {table} matched (count: {len(rows)}):")
                    for row in rows[:5]:
                        print("  ", row)
            except Exception as e:
                pass
    
    print("\n--- Listing video_projects ---")
    cursor.execute("SELECT * FROM video_projects;")
    for row in cursor.fetchall():
        print("Project:", row)

if __name__ == "__main__":
    inspect()


if __name__ == "__main__":
    inspect()
