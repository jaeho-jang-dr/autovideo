import os
import sqlite3
import psycopg2
from dotenv import load_dotenv

# Load Supabase Postgres credentials
load_dotenv()

DB_HOST = os.getenv("SUPABASE_DB_HOST", "aws-1-ap-northeast-2.pooler.supabase.com")
DB_PORT = os.getenv("SUPABASE_DB_PORT", "5432")
DB_USER = os.getenv("SUPABASE_DB_USER", "postgres.dggxjxgnsecspiubaeie")
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "sRlfjrl77!!")
DB_NAME = os.getenv("SUPABASE_DB_NAME", "postgres")

def get_supabase_conn():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        return conn
    except Exception as e:
        print(f"[Supabase Connect Error] {e}")
        return None

def main():
    print("=" * 60)
    print(" Seeding Zolla Letters & Objects to SQLite & Supabase")
    print("=" * 60)
    
    # 1) Scan local file assets
    letters_dir = "assets/graphics/letters"
    graphics_dir = "assets/graphics"
    
    assets_to_seed = []
    
    # Scan letters
    if os.path.exists(letters_dir):
        for f in os.listdir(letters_dir):
            if f.endswith(".png"):
                base_name = f[:-4]
                file_path = f"graphics/letters/{f}"
                
                if base_name.startswith("letter_"):
                    char = base_name.replace("letter_", "")
                    assets_to_seed.append({
                        "name_kr": char,
                        "name_en": f"Letter_{char}",
                        "type": "letter",
                        "file_path": file_path,
                        "flow_prompt": f"Minimalist line-art vector icon of Hangeul vowel or consonant character '{char}', clean black outlines on flat light beige background"
                    })
                elif base_name.startswith("word_"):
                    word = base_name.replace("word_", "")
                    assets_to_seed.append({
                        "name_kr": word,
                        "name_en": f"Word_{word}",
                        "type": "letter",
                        "file_path": file_path,
                        "flow_prompt": f"Minimalist line-art vector icon of Hangeul word '{word}', clean black outlines on flat light beige background"
                    })
                    
    # Scan objects
    if os.path.exists(graphics_dir):
        for f in os.listdir(graphics_dir):
            if f.startswith("obj_") and f.endswith(".png"):
                base_name = f[:-4]
                obj_name = base_name.replace("obj_", "")
                file_path = f"graphics/{f}"
                
                # Mapped Korean names
                ko_names = {
                    "blackboard": "칠판",
                    "notebook": "공책",
                    "pencil": "연필",
                    "sejong_frame": "세종대왕 액자",
                    "haerye_scroll": "해례본 스크롤",
                    "bed": "침대",
                    "blanket": "이불",
                    "pillow": "베개",
                    "chair": "의자",
                    "desk": "책상",
                    "door_closed": "문(닫힘)",
                    "door_open": "문(열림)",
                    "computer": "컴퓨터",
                    "chalk": "분필",
                    "particle": "입자"
                }
                
                assets_to_seed.append({
                    "name_kr": ko_names.get(obj_name, obj_name),
                    "name_en": obj_name.capitalize(),
                    "type": "object",
                    "file_path": file_path,
                    "flow_prompt": f"Minimalist line-art vector icon of {obj_name}, clean black outlines on flat light beige background"
                })

    print(f"Scanned {len(assets_to_seed)} assets from assets/graphics/ directory.")
    
    # 2) Seed SQLite
    sqlite_path = "channel/content.db"
    if os.path.exists(sqlite_path):
        conn_lite = sqlite3.connect(sqlite_path)
        cur_lite = conn_lite.cursor()
        
        sqlite_inserted = 0
        for item in assets_to_seed:
            # Check duplication
            cur_lite.execute("SELECT id FROM assets WHERE file_path=?;", (item["file_path"],))
            row = cur_lite.fetchone()
            if not row:
                cur_lite.execute(
                    "INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?, ?, ?, ?, ?);",
                    (item["name_kr"], item["name_en"], item["type"], item["file_path"], item["flow_prompt"])
                )
                sqlite_inserted += 1
        
        conn_lite.commit()
        conn_lite.close()
        print(f"[SQLite] Successfully seeded {sqlite_inserted} new assets.")
    else:
        print("[SQLite] Warning: channel/content.db not found.")
        
    # 3) Seed Supabase PostgreSQL
    conn_pg = get_supabase_conn()
    if conn_pg:
        cur_pg = conn_pg.cursor()
        pg_inserted = 0
        
        for item in assets_to_seed:
            # Check duplication
            cur_pg.execute("SELECT id FROM assets WHERE file_path=%s;", (item["file_path"],))
            row = cur_pg.fetchone()
            if not row:
                cur_pg.execute(
                    "INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (%s, %s, %s, %s, %s);",
                    (item["name_kr"], item["name_en"], item["type"], item["file_path"], item["flow_prompt"])
                )
                pg_inserted += 1
                
        conn_pg.commit()
        cur_pg.close()
        conn_pg.close()
        print(f"[Supabase PG] Successfully seeded {pg_inserted} new assets.")
    else:
        print("[Supabase PG] Failed to connect, skipping PostgreSQL seed.")

if __name__ == "__main__":
    main()
