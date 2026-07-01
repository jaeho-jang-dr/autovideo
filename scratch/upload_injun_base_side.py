import os
import sys
import psycopg2
from supabase import create_client, Client

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    key = env.get("SUPABASE_KEY")  # service_role key
    
    if not url or not key:
        print("[ERR] SUPABASE_URL or SUPABASE_KEY not found in .env")
        return 1
        
    supabase: Client = create_client(url, key)
    
    local_path = os.path.join(ROOT, "home_vocab", "injun_base_side.png")
    if not os.path.exists(local_path):
        print(f"[ERR] File not found at {local_path}")
        return 1
        
    bucket_filename = "injun_base_side.png"
    storage_url = f"{url}/storage/v1/object/public/character-base/{bucket_filename}"
    
    # 1. Upload to Supabase Storage ('character-base' bucket)
    print(f"Uploading {local_path} to Storage...")
    try:
        # Remove if exists
        try:
            supabase.storage.from_("character-base").remove([bucket_filename])
            print("Removed old file from storage.")
        except Exception:
            pass
            
        with open(local_path, "rb") as f:
            supabase.storage.from_("character-base").upload(
                path=bucket_filename,
                file=f.read(),
                file_options={"content-type": "image/png"}
            )
        print(f"Successfully uploaded to Storage. URL: {storage_url}")
    except Exception as e:
        print(f"[ERR] Storage upload failed: {e}")
        return 1
        
    # 2. Insert/Upsert Record into character_assets Table in PostgreSQL
    print("Upserting record to character_assets table...")
    try:
        conn = psycopg2.connect(
            host=env["SUPABASE_DB_HOST"],
            port=env["SUPABASE_DB_PORT"],
            user=env["SUPABASE_DB_USER"],
            password=env["SUPABASE_DB_PASSWORD"],
            database=env["SUPABASE_DB_NAME"]
        )
        cur = conn.cursor()
        
        tags = ["character-base", "reference", "home_vocab", "line-art", "korean", "injun", "side", "standing", "injun_base_side"]
        method_doc = "CHARACTER_ASSET_METHOD.md"
        style = "minimalist 2D line art, thick black outlines, light beige background (#F5F5F0)"
        
        cur.execute("""
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
        """, ("injun_base_side", "injun", "side", "standing", "home_vocab/injun_base_side.png", storage_url, "text2img", style, tags, method_doc))
        
        conn.commit()
        cur.close()
        conn.close()
        print("Successfully updated PostgreSQL database record!")
    except Exception as e:
        print(f"[ERR] DB update failed: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
