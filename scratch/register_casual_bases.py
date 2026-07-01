# -*- coding: utf-8 -*-
"""
지은 평상복 베이스 3종 사진(front, side, back)을 DB에 등록.
- Supabase: character-base 버킷 업로드 + character_assets upsert
- 로컬 content.db 미러: assets upsert
- 자격증명은 .env 에서만 로드. 멱등.

사용: python scratch/register_casual_bases.py
"""
import os
import sys
import sqlite3
import hashlib

import psycopg2

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUCKET = "character-base"
METHOD_DOC = "POSE_GENERATION_METHOD.md"
STYLE = ("minimalist 2D line art, thick clean black outlines, whiteboard marker style, "
         "light beige background (#F5F5F0)")

CASUAL_BASES = [
    {
        "key": "jieun_casual_front",
        "kr": "지은_평상복_정면",
        "view": "front",
        "pose": "standing",
        "file": "home_vocab/jieun_casual_front.png",
        "prompt": "standing, casual clothes (t-shirt, pants, sneakers), front view"
    },
    {
        "key": "jieun_casual_side",
        "kr": "지은_평상복_측면",
        "view": "side",
        "pose": "standing",
        "file": "home_vocab/jieun_casual_side.png",
        "prompt": "standing, casual clothes (t-shirt, pants, sneakers), left side profile view"
    },
    {
        "key": "jieun_casual_back",
        "kr": "지은_평상복_뒷모습",
        "view": "back",
        "pose": "standing",
        "file": "home_vocab/jieun_casual_back.png",
        "prompt": "standing, casual clothes (t-shirt, pants, sneakers), back view"
    }
]

def load_env(p=None):
    p = p or os.path.join(ROOT, ".env")
    d = {}
    if not os.path.exists(p):
        print(f"[WARN] .env 파일이 없습니다: {p}")
        return d
    with open(p, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                d[k.strip()] = v.strip().strip('"').strip("'")
    return d

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()

def save_supabase(env):
    url = env.get("SUPABASE_URL")
    if not url:
        print("[FAIL] SUPABASE_URL가 .env에 정의되어 있지 않습니다.")
        return

    conn = psycopg2.connect(
        host=env["SUPABASE_DB_HOST"], port=env.get("SUPABASE_DB_PORT", "5432"),
        user=env["SUPABASE_DB_USER"], password=env["SUPABASE_DB_PASSWORD"],
        dbname=env.get("SUPABASE_DB_NAME", "postgres"), sslmode="require", connect_timeout=20)
    cur = conn.cursor()

    from supabase import create_client
    sb = create_client(url, env["SUPABASE_KEY"])

    for p in CASUAL_BASES:
        local = os.path.join(ROOT, p["file"])
        base = os.path.basename(p["file"])
        public = f"{url}/storage/v1/object/public/{BUCKET}/{base}"
        try:
            try:
                sb.storage.from_(BUCKET).remove([base])
            except Exception:
                pass
            with open(local, "rb") as fh:
                sb.storage.from_(BUCKET).upload(
                    path=base, file=fh.read(),
                    file_options={"content-type": "image/png", "upsert": "true"})
            print(f"  [storage] {base} 업로드 완료")
        except Exception as ex:
            print(f"  [ERR] upload {base}: {ex}")

        tags = sorted({"jieun", "female", "pose", "casual", "평상복", p["view"], p["pose"], p["key"]})
        cur.execute("""
            INSERT INTO character_assets
              (key,character_id,view,pose,file_path,storage_url,method,style,tags,method_doc)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (key) DO UPDATE SET character_id=EXCLUDED.character_id,view=EXCLUDED.view,
              pose=EXCLUDED.pose,file_path=EXCLUDED.file_path,storage_url=EXCLUDED.storage_url,
              method=EXCLUDED.method,style=EXCLUDED.style,tags=EXCLUDED.tags,method_doc=EXCLUDED.method_doc;
        """, (p["key"], "jieun", p["view"], p["pose"], p["file"], public,
              "reference2img", STYLE, tags, METHOD_DOC))
        conn.commit()
        print(f"  [character_assets] {p['key']} ({p['pose']}/{p['view']}) 등록 완료")

    cur.close()
    conn.close()

def save_local():
    db = os.path.join(ROOT, "channel", "content.db")
    if not os.path.exists(db):
        print(f"[WARN] 로컬 content.db를 찾을 수 없습니다: {db}")
        return
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    names = [p["key"] for p in CASUAL_BASES]
    # Delete first to ensure we overwrite cleanly if it exists
    cur.execute(f"DELETE FROM assets WHERE name_en IN ({','.join('?' * len(names))})", names)
    cur.executemany(
        "INSERT INTO assets(name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
        [(p["kr"], p["key"], "character", os.path.basename(p["file"]), p["prompt"]) for p in CASUAL_BASES])
    conn.commit()
    na = cur.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
    conn.close()
    print(f"  [local assets] +{len(CASUAL_BASES)} (총 {na})")

def main():
    for p in CASUAL_BASES:
        path = os.path.join(ROOT, p["file"])
        if not os.path.exists(path):
            raise SystemExit(f"[FAIL] 파일 없음: {p['file']}")
    env = load_env()
    print("== Supabase ==")
    save_supabase(env)
    print("== 로컬 content.db 미러 ==")
    save_local()
    print("\n[OK] 평상복 베이스 3종 저장 완료 (Supabase + 로컬)")

if __name__ == "__main__":
    main()
