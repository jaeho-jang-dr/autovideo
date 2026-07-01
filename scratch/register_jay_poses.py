# -*- coding: utf-8 -*-
import os
import sys
import shutil
import sqlite3
import psycopg2
from supabase import create_client, Client

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

def load_env(p=os.path.join(ROOT, ".env")):
    d = {}
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    d[k.strip()] = v.strip().strip('"').strip("'")
    return d

POSES = [
    {
        "key": "jay_writing_book",
        "name_kr": "Jay_글쓰기_정면",
        "name_en": "Jay_Writing_Book",
        "view": "front",
        "pose": "writing_book",
        "flow_prompt": "sitting at a wooden desk, holding a pencil in his hand, and writing in an open book. front view",
        "src_filename": "jay_writing_book.png",
        "is_opaque": False
    },
    {
        "key": "jay_writing_book_opaque",
        "name_kr": "Jay_글쓰기_정면_불투명",
        "name_en": "Jay_Writing_Book_Opaque",
        "view": "front",
        "pose": "writing_book",
        "flow_prompt": "sitting at a wooden desk, holding a pencil in his hand, and writing in an open book. front view. Flat beige background #F5F5F0",
        "src_filename": "jay_writing_book_opaque.png",
        "is_opaque": True
    },
    {
        "key": "jay_writing_book_side",
        "name_kr": "Jay_글쓰기_옆모습",
        "name_en": "Jay_Writing_Book_Side",
        "view": "side",
        "pose": "writing_book",
        "flow_prompt": "sitting at a wooden desk, holding a pencil in his hand, and writing in an open book. LEFT side profile view",
        "src_filename": "jay_writing_book_side.png",
        "is_opaque": False
    },
    {
        "key": "jay_writing_book_side_opaque",
        "name_kr": "Jay_글쓰기_옆모습_불투명",
        "name_en": "Jay_Writing_Book_Side_Opaque",
        "view": "side",
        "pose": "writing_book",
        "flow_prompt": "sitting at a wooden desk, holding a pencil in his hand, and writing in an open book. LEFT side profile view. Flat beige background #F5F5F0",
        "src_filename": "jay_writing_book_side_opaque.png",
        "is_opaque": True
    },
    {
        "key": "jay_writing_board_side",
        "name_kr": "Jay_칠판글쓰기_옆모습",
        "name_en": "Jay_Writing_Board_Side",
        "view": "side",
        "pose": "writing_board",
        "flow_prompt": "standing in front of a green chalkboard, holding a piece of chalk in his hand, and writing on the chalkboard. LEFT side profile view",
        "src_filename": "jay_writing_board_side.png",
        "is_opaque": False
    },
    {
        "key": "jay_writing_board_side_opaque",
        "name_kr": "Jay_칠판글쓰기_옆모습_불투명",
        "name_en": "Jay_Writing_Board_Side_Opaque",
        "view": "side",
        "pose": "writing_board",
        "flow_prompt": "standing in front of a green chalkboard, holding a piece of chalk in his hand, and writing on the chalkboard. LEFT side profile view. Flat beige background #F5F5F0",
        "src_filename": "jay_writing_board_side_opaque.png",
        "is_opaque": True
    },
    {
        "key": "jay_working_desk_side",
        "name_kr": "Jay_일하는책상_옆모습",
        "name_en": "Jay_Working_Desk_Side",
        "view": "side",
        "pose": "working_desk",
        "flow_prompt": "sitting at a wooden desk with a laptop on it. The stickman and his desk are relatively small, showing a wider view of the room. On the back wall, there is a clock and a window. On the front wall, there is a door. There is also a bookshelf. LEFT side profile view",
        "src_filename": "jay_working_desk_side.png",
        "is_opaque": False
    },
    {
        "key": "jay_working_desk_side_opaque",
        "name_kr": "Jay_일하는책상_옆모습_불투명",
        "name_en": "Jay_Working_Desk_Side_Opaque",
        "view": "side",
        "pose": "working_desk",
        "flow_prompt": "sitting at a wooden desk with a laptop on it. The stickman and his desk are relatively small, showing a wider view of the room. On the back wall, there is a clock and a window. On the front wall, there is a door. There is also a bookshelf. LEFT side profile view. Flat beige background #F5F5F0",
        "src_filename": "jay_working_desk_side_opaque.png",
        "is_opaque": True
    },
    {
        "key": "jay_whiteboard_writing_side",
        "name_kr": "Jay_화이트보드글쓰기_옆모습",
        "name_en": "Jay_Whiteboard_Writing_Side",
        "view": "side",
        "pose": "writing_board",
        "flow_prompt": "standing in front of a large white whiteboard, holding a whiteboard marker in his hand, and writing Hangeul letters on the whiteboard. LEFT side profile view",
        "src_filename": "jay_whiteboard_writing_side.png",
        "is_opaque": False
    },
    {
        "key": "jay_whiteboard_writing_side_opaque",
        "name_kr": "Jay_화이트보드글쓰기_옆모습_불투명",
        "name_en": "Jay_Whiteboard_Writing_Side_Opaque",
        "view": "side",
        "pose": "writing_board",
        "flow_prompt": "standing in front of a large white whiteboard, holding a whiteboard marker in his hand, and writing Hangeul letters on the whiteboard. LEFT side profile view. Flat beige background #F5F5F0",
        "src_filename": "jay_whiteboard_writing_side_opaque.png",
        "is_opaque": True
    }
]

def main():
    env = load_env()
    
    # 1. Copy Files to assets/characters/
    print("=== Copying files to assets/characters/ ===")
    os.makedirs(os.path.join(ROOT, "assets", "characters"), exist_ok=True)
    
    for pose in POSES:
        src = os.path.join(ROOT, "home_vocab", pose["src_filename"])
        dest = os.path.join(ROOT, "assets", "characters", pose["src_filename"])
        
        if not os.path.exists(src):
            print(f"[WARN] Source file not found: {src}")
            continue
            
        shutil.copyfile(src, dest)
        print(f"Copied {pose['src_filename']} -> assets/characters/")

    # 2. Register in Local SQLite Database
    print("\n=== Registering in Local SQLite content.db ===")
    sqlite_path = os.path.join(ROOT, "channel", "content.db")
    if os.path.exists(sqlite_path):
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        
        for pose in POSES:
            file_path = f"assets/characters/{pose['src_filename']}"
            # Check if exists
            cur.execute("SELECT id FROM assets WHERE name_en=?", (pose["name_en"],))
            row = cur.fetchone()
            
            if row:
                cur.execute("""
                    UPDATE assets 
                    SET name_kr=?, type='character', file_path=?, flow_prompt=?
                    WHERE id=?
                """, (pose["name_kr"], file_path, pose["flow_prompt"], row[0]))
                print(f"Updated local SQLite asset: {pose['name_en']} (ID: {row[0]})")
            else:
                cur.execute("""
                    INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt)
                    VALUES (?, ?, 'character', ?, ?)
                """, (pose["name_kr"], pose["name_en"], file_path, pose["flow_prompt"]))
                print(f"Inserted new local SQLite asset: {pose['name_en']}")
                
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("[WARN] Local content.db not found!")

    # 3. Register in Supabase Database (Storage & PostgreSQL)
    print("\n=== Registering in Supabase ===")
    url = env.get("SUPABASE_URL")
    key = env.get("SUPABASE_KEY")
    
    if not url or not key:
        print("[INFO] Supabase credentials not found. Skipping Supabase upload.")
        return 0
        
    try:
        supabase: Client = create_client(url, key)
        
        # Connect PostgreSQL
        conn = psycopg2.connect(
            host=env["SUPABASE_DB_HOST"],
            port=env["SUPABASE_DB_PORT"],
            user=env["SUPABASE_DB_USER"],
            password=env["SUPABASE_DB_PASSWORD"],
            database=env["SUPABASE_DB_NAME"]
        )
        cur = conn.cursor()
        
        for pose in POSES:
            local_path = os.path.join(ROOT, "assets", "characters", pose["src_filename"])
            if not os.path.exists(local_path):
                continue
                
            bucket_filename = pose["src_filename"]
            storage_url = f"{url}/storage/v1/object/public/character-base/{bucket_filename}"
            
            # Upload Storage
            try:
                try:
                    supabase.storage.from_("character-base").remove([bucket_filename])
                except Exception:
                    pass
                with open(local_path, "rb") as f:
                    supabase.storage.from_("character-base").upload(
                        path=bucket_filename,
                        file=f.read(),
                        file_options={"content-type": "image/png"}
                    )
                print(f"Uploaded to Supabase Storage: {bucket_filename}")
            except Exception as e:
                print(f"[ERR] Storage upload failed for {bucket_filename}: {e}")
                continue
                
            # Upsert DB
            db_file_path = f"assets/characters/{pose['src_filename']}"
            all_tags = ["character-base", "reference", "home_vocab", "line-art", "korean", "jay", pose["view"], pose["pose"], pose["key"]]
            if pose["is_opaque"]:
                all_tags.append("opaque")
            else:
                all_tags.append("transparent")
                
            style = "minimalist 2D line art, thin black outlines"
            
            cur.execute("""
                INSERT INTO character_assets (key, character_id, view, pose, file_path, storage_url, method, style, tags, method_doc)
                VALUES (%s, 'jay', %s, %s, %s, %s, 'reference2img', %s, %s, 'POSE_GENERATION_METHOD.md')
                ON CONFLICT (key) DO UPDATE SET
                    character_id = EXCLUDED.character_id,
                    view = EXCLUDED.view,
                    pose = EXCLUDED.pose,
                    file_path = EXCLUDED.file_path,
                    storage_url = EXCLUDED.storage_url,
                    method = EXCLUDED.method,
                    style = EXCLUDED.style,
                    tags = EXCLUDED.tags,
                    method_doc = EXCLUDED.method_doc;
            """, (pose["key"], pose["view"], pose["pose"], db_file_path, storage_url, style, all_tags))
            print(f"Upserted Supabase DB record for key: {pose['key']}")
            
        conn.commit()
        cur.close()
        conn.close()
        print("Supabase registration successfully completed!")
    except Exception as e:
        print(f"[ERR] Supabase connection or query failed: {e}")

if __name__ == "__main__":
    main()
