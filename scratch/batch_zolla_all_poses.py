# -*- coding: utf-8 -*-
import os
import sys
import sqlite3
import psycopg2
import subprocess
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

def setup_file_logging():
    log_file_path = os.path.join(ROOT, "scratch", "batch_zolla_all_poses.log")
    try:
        log_file = open(log_file_path, "w", encoding="utf-8", buffering=1)
        sys.stdout = log_file
        sys.stderr = log_file
    except Exception as e:
        print(f"Failed to setup file logging: {e}")

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

def get_prompts(path):
    items = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "|" not in line:
                continue
            k, p = line.split("|", 1)
            items.append((k.strip(), p.strip()))
    return items

def upload_and_register(key_name, char_id, filename, prompt, env, model, supabase):
    local_path = os.path.join(ROOT, "home_vocab", filename)
    if not os.path.exists(local_path):
        print(f"  [ERR] Local file not found: {local_path}")
        return False
        
    url = env.get("SUPABASE_URL")
    storage_url = f"{url}/storage/v1/object/public/character-base/{filename}"
    
    # 1. Supabase Storage Upload
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
        print(f"  [STORAGE-OK] Uploaded {filename}")
    except Exception as e:
        print(f"  [STORAGE-ERR] Upload failed: {e}")
        return False
        
    # 2. SQLite Update
    db_path = os.path.join(ROOT, "channel", "content.db")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM assets WHERE file_path = ?", (f"home_vocab/{filename}",))
        row = cur.fetchone()
        name_kr = char_id + "_" + key_name.replace(f"{char_id}_", "")
        name_en = key_name.replace(f"{char_id}_", "").title()
        
        if row:
            cur.execute("""
                UPDATE assets SET name_kr = ?, name_en = ?, flow_prompt = ?
                WHERE file_path = ?
            """, (name_kr, name_en, prompt, f"home_vocab/{filename}"))
        else:
            cur.execute("""
                INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt)
                VALUES (?, ?, 'character', ?, ?)
            """, (name_kr, name_en, f"home_vocab/{filename}", prompt))
        conn.commit()
        conn.close()
        print(f"  [SQLITE-OK] Registered {filename}")
    except Exception as e:
        print(f"  [SQLITE-ERR] SQLite update failed: {e}")
        
    # 3. Supabase Postgres Update (assets & character_assets)
    try:
        emb = model.encode(prompt).tolist()
        emb_str = "[" + ",".join(map(str, emb)) + "]"
        file_path = f"home_vocab/{filename}"
        
        pg_conn = psycopg2.connect(
            host=env["SUPABASE_DB_HOST"],
            port=env.get("SUPABASE_DB_PORT", "5432"),
            user=env["SUPABASE_DB_USER"],
            password=env["SUPABASE_DB_PASSWORD"],
            database=env.get("SUPABASE_DB_NAME", "postgres")
        )
        pg_cur = pg_conn.cursor()
        
        # Reset identity
        pg_cur.execute("SELECT COALESCE(MAX(id), 0) FROM assets;")
        max_id = pg_cur.fetchone()[0]
        pg_cur.execute(f"ALTER TABLE assets ALTER COLUMN id RESTART WITH {max_id + 1};")
        
        # A. assets
        pg_cur.execute("SELECT id FROM assets WHERE file_path = %s", (file_path,))
        row = pg_cur.fetchone()
        name_kr = char_id + "_" + key_name.replace(f"{char_id}_", "")
        name_en = key_name.replace(f"{char_id}_", "").title()
        
        if row:
            pg_cur.execute("""
                UPDATE assets SET name_kr = %s, name_en = %s, flow_prompt = %s, embedding = %s
                WHERE file_path = %s
            """, (name_kr, name_en, prompt, emb_str, file_path))
        else:
            pg_cur.execute("""
                INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt, embedding)
                VALUES (%s, %s, 'character', %s, %s, %s)
            """, (name_kr, name_en, file_path, prompt, emb_str))
            
        # B. character_assets
        view = "side" if "running" in key_name or "walking" in key_name or "sleeping" in key_name else "front"
        pose = key_name.replace(f"{char_id}_", "")
        style = "loose sketchy hand-drawn black pen line doodle style, pure white background"
        tags = ["character-pose", "home_vocab", "line-art", "whiteboard", char_id, view, pose, key_name]
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
        
        pg_conn.commit()
        pg_cur.close()
        pg_conn.close()
        print(f"  [PG-OK] Synced {key_name}")
    except Exception as e:
        print(f"  [PG-ERR] Postgres sync failed: {e}")
        return False
        
    return True

def main():
    # 백그라운드 기동 시 로그 파일 자동 리다이렉션
    setup_file_logging()
    
    env = load_env()
    url = env.get("SUPABASE_URL")
    key = env.get("SUPABASE_KEY")
    if not url or not key:
        print("[ERR] SUPABASE_URL/KEY not found in .env")
        return 1
        
    supabase = create_client(url, key)
    
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # 2 prompt files
    tasks = []
    # A. Zollaman poses
    zollaman_file = os.path.join(ROOT, "home_vocab", "zollaman_pose_prompts.txt")
    for k, p in get_prompts(zollaman_file):
        tasks.append((k, "zollaman", "zollaman_base", k + ".png", p))
    # B. Zollanyeo poses
    zollanyeo_file = os.path.join(ROOT, "home_vocab", "zollanyeo_pose_prompts.txt")
    for k, p in get_prompts(zollanyeo_file):
        tasks.append((k, "zollanyeo", "zollanyeo_base", k + ".png", p))
        
    print(f"Found total {len(tasks)} pose tasks to process.")
    
    python_path = (subprocess.check_output(["where", "python"]).decode("utf-8").split("\n")[0].strip())
    if not python_path:
        python_path = "python"
        
    success_cnt = 0
    fail_cnt = 0
    skip_cnt = 0
    
    for idx, (key_name, char_id, ref_key, filename, prompt_phrase) in enumerate(tasks, 1):
        local_path = os.path.join(ROOT, "home_vocab", filename)
        print(f"\n[{idx}/{len(tasks)}] Processing {key_name} (ref={ref_key})")
        
        # Check if local file already exists (Idempotence check)
        if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
            print(f"  [SKIP] Local file {filename} already exists. Syncing metadata only...")
            if upload_and_register(key_name, char_id, filename, prompt_phrase, env, model, supabase):
                skip_cnt += 1
            else:
                fail_cnt += 1
            continue
            
        # Run flow_pose.py script
        cmd = [
            python_path, "scratch/flow_pose.py",
            "--ref-key", ref_key,
            "--out-key", key_name,
            "--prompt", prompt_phrase
        ]
        
        print(f"  [RUN] {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            if res.returncode == 0:
                print("  [SUCCESS] flow_pose.py finished.")
                if upload_and_register(key_name, char_id, filename, prompt_phrase, env, model, supabase):
                    success_cnt += 1
                else:
                    fail_cnt += 1
            else:
                print(f"  [FAIL] flow_pose.py returned exit code {res.returncode}")
                print(f"  [STDOUT] {res.stdout[-400:]}")
                print(f"  [STDERR] {res.stderr[-400:]}")
                fail_cnt += 1
        except Exception as e:
            print(f"  [ERR] Subprocess execution failed: {e}")
            fail_cnt += 1
            
    print("\n==============================================")
    print(f"Batch Pose Processing Complete:")
    print(f"  Success: {success_cnt}")
    print(f"  Skipped: {skip_cnt}")
    print(f"  Failed:  {fail_cnt}")
    print("==============================================")
    return 0 if fail_cnt == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
