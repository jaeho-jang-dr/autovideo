import os
import sys
import argparse
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--character-id", default="injun")
    ap.add_argument("--view", required=True, choices=["front", "side", "back"])
    ap.add_argument("--pose", default="standing")
    ap.add_argument("--file-path", required=True)
    ap.add_argument("--method", default="reference2img")
    ap.add_argument("--tags", nargs="+", default=[])
    args = ap.parse_args()

    env = load_env()
    url = env.get("SUPABASE_URL")
    key = env.get("SUPABASE_KEY")  # service_role key
    
    if not url or not key:
        print("[ERR] SUPABASE_URL or SUPABASE_KEY not found in .env")
        return 1
        
    supabase: Client = create_client(url, key)
    
    local_path = os.path.join(ROOT, args.file_path)
    if not os.path.exists(local_path):
        print(f"[ERR] File not found at {local_path}")
        return 1
        
    bucket_filename = os.path.basename(args.file_path)
    storage_url = f"{url}/storage/v1/object/public/character-base/{bucket_filename}"
    
    # 1. Upload to Supabase Storage ('character-base' bucket)
    print(f"Uploading {local_path} to Storage as {bucket_filename}...")
    try:
        # Remove if exists
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
        
        # Combine default tags with provided tags
        all_tags = list(set(["character-base", "reference", "home_vocab", "line-art", "korean", args.character_id, args.view, args.pose, args.key] + args.tags))
        method_doc = "POSE_GENERATION_METHOD.md"
        style = "minimalist 2D line art, thick black outlines"
        
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
        """, (args.key, args.character_id, args.view, args.pose, args.file_path, storage_url, args.method, style, all_tags, method_doc))
        
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
