# -*- coding: utf-8 -*-
import os
import sys
import sqlite3
import psycopg2
import hashlib
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# Force UTF-8 stdout
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

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

def main():
    env = load_env()
    url = env.get("SUPABASE_URL")
    key = env.get("SUPABASE_KEY")
    
    if not url or not key:
        print("[ERR] SUPABASE_URL or SUPABASE_KEY not found in .env")
        return 1
        
    supabase: Client = create_client(url, key)
    
    key_name = "zolla_handshake"
    name_kr = "졸라커플_악수"
    name_en = "Zolla_Handshake"
    filename = "zolla_handshake.png"
    prompt = ("Using the uploaded reference image, keep the EXACT same two stickman characters — "
              "jjolla-man (black short-hair male stickman) and jjolla-nyeo (orange short-hair female stickman) — "
              "but now draw them shaking hands politely, smiling, loose sketchy hand-drawn black pen line doodle style, "
              "minimalist whiteboard-doodle sketch style, on a solid flat pure white background, no text, no signatures")
              
    local_path = os.path.join(ROOT, "home_vocab", filename)
    if not os.path.exists(local_path):
        print(f"[ERR] File not found at {local_path}")
        return 1
        
    storage_url = f"{url}/storage/v1/object/public/character-base/{filename}"
    
    # 1. Storage Upload
    print(f"Uploading {filename} to Supabase Storage...")
    try:
        try:
            supabase.storage.from_("character-base").remove([filename])
        except Exception:
            pass
        with open(local_path, "rb") as f:
            supabase.storage.from_("character-base").upload(
                path=filename,
                file=f.read(),
                file_options={"content-type": "image/png"}
            )
        print(f"  [STORAGE-UPLOAD] {filename} -> {storage_url}")
    except Exception as e:
        print(f"[ERR] Failed to upload {filename}: {e}")
        return 1
        
    # 2. SQLite Update
    db_path = os.path.join(ROOT, "channel", "content.db")
    if not os.path.exists(db_path):
        print(f"[ERR] SQLite {db_path} not found.")
        return 1
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    print("Updating assets in SQLite Content DB...")
    cur.execute("SELECT id FROM assets WHERE file_path = ?", (f"home_vocab/{filename}",))
    row = cur.fetchone()
    if row:
        cur.execute("""
            UPDATE assets 
            SET name_kr = ?, name_en = ?, flow_prompt = ?
            WHERE file_path = ?
        """, (name_kr, name_en, prompt, f"home_vocab/{filename}"))
        print(f"  [SQLITE-UPDATE] {filename}")
    else:
        cur.execute("""
            INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt)
            VALUES (?, ?, 'character', ?, ?)
        """, (name_kr, name_en, f"home_vocab/{filename}", prompt))
        print(f"  [SQLITE-INSERT] {filename}")
    conn.commit()
    conn.close()
    
    # 3. Supabase Postgres Update
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    try:
        pg_conn = psycopg2.connect(
            host=env["SUPABASE_DB_HOST"],
            port=env.get("SUPABASE_DB_PORT", "5432"),
            user=env["SUPABASE_DB_USER"],
            password=env["SUPABASE_DB_PASSWORD"],
            database=env.get("SUPABASE_DB_NAME", "postgres")
        )
        pg_cur = pg_conn.cursor()
        
        # Reset max id sequence
        pg_cur.execute("SELECT COALESCE(MAX(id), 0) FROM assets;")
        max_id = pg_cur.fetchone()[0]
        pg_cur.execute(f"ALTER TABLE assets ALTER COLUMN id RESTART WITH {max_id + 1};")
    except Exception as e:
        print(f"[ERR] Postgres connection failed: {e}")
        return 1
        
    print("Updating Postgres assets and character_assets tables...")
    emb = model.encode(prompt).tolist()
    emb_str = "[" + ",".join(map(str, emb)) + "]"
    file_path = f"home_vocab/{filename}"
    
    # A. assets
    pg_cur.execute("SELECT id FROM assets WHERE file_path = %s", (file_path,))
    row = pg_cur.fetchone()
    if row:
        pg_cur.execute("""
            UPDATE assets 
            SET name_kr = %s, name_en = %s, flow_prompt = %s, embedding = %s
            WHERE file_path = %s
        """, (name_kr, name_en, prompt, emb_str, file_path))
        print(f"  [PG-ASSETS-UPDATE] {file_path}")
    else:
        pg_cur.execute("""
            INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt, embedding)
            VALUES (%s, %s, 'character', %s, %s, %s)
        """, (name_kr, name_en, file_path, prompt, emb_str))
        print(f"  [PG-ASSETS-INSERT] {file_path}")
        
    # B. character_assets
    char_id = "zollaman"
    view = "front"
    pose = "handshake"
    style = "loose sketchy hand-drawn black pen line doodle style, pure white background"
    tags = ["character-pose", "home_vocab", "line-art", "whiteboard", "zollaman", "zollanyeo", view, pose, key_name]
    method_doc = "POSE_GENERATION_METHOD.md"
    
    pg_cur.execute("""
        INSERT INTO character_assets (key, character_id, view, pose, file_path, storage_url, method, style, tags, method_doc)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
    """, (key_name, char_id, view, pose, file_path, storage_url, "image2img", style, tags, method_doc))
    print(f"  [PG-CHAR_ASSETS-UPSERT] {key_name}")
    
    pg_conn.commit()
    pg_cur.close()
    pg_conn.close()
    print("Database sync complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
