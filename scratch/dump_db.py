import sqlite3
import json
import sys

def dump_db():
    conn = sqlite3.connect('channel/content.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    dump_data = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [row[1] for row in cursor.fetchall()]
        
        cursor.execute(f"SELECT * FROM {table};")
        rows = cursor.fetchall()
        
        dump_data[table] = {
            "columns": columns,
            "rows": [list(row) for row in rows]
        }
        
    with open('scratch/db_dump.json', 'w', encoding='utf-8') as f:
        json.dump(dump_data, f, ensure_ascii=False, indent=2)
        
    print("Database dumped successfully to scratch/db_dump.json")

if __name__ == "__main__":
    dump_db()
