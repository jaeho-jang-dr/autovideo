#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_all_audio.py — Generates voice actor (gTTS) audio files for all grammar and curriculum texts,
and registers them in both local SQLite and remote Supabase databases.
"""
import os
import re
import sys
import sqlite3
import json

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SQLITE_DB = os.path.join(ROOT, "channel", "content.db")
GRAMMAR_DATA_FILE = os.path.join(ROOT, "web", "src", "data", "grammarData.ts")
AUDIO_DIR = os.path.join(ROOT, "web", "public", "audio", "jamo")

# Ensure output directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# Try installing gtts if not present
try:
    from gtts import gTTS
except ImportError:
    print("gTTS is not installed. Installing it via pip...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gtts"])
    from gtts import gTTS

def load_env():
    """Loads environment variables from .env if present"""
    env_file = os.path.join(ROOT, ".env")
    if os.path.exists(env_file):
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

load_env()

def extract_grammar_sounds():
    """Extracts sound_play tokens from grammarData.ts using regex"""
    sounds = set()
    if not os.path.exists(GRAMMAR_DATA_FILE):
        print(f"[Warn] Grammar data file not found at {GRAMMAR_DATA_FILE}")
        return sounds

    with open(GRAMMAR_DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Find sound_play: "..." or sound_play: '...'
    matches = re.findall(r'sound_play:\s*["\']([^"\']+)["\']', content)
    for m in matches:
        sounds.add(m.strip())
    print(f"Extracted {len(sounds)} unique sounds from Grammar.")
    return sounds

def extract_curriculum_sounds():
    """Extracts individual target words/letters from SQLite hangeul_curriculum"""
    sounds = set()
    if not os.path.exists(SQLITE_DB):
        print(f"[Warn] SQLite DB not found at {SQLITE_DB}")
        return sounds

    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()
    try:
        cur.execute("SELECT target_letters FROM hangeul_curriculum;")
        rows = cur.fetchall()
        for (target_str,) in rows:
            # Split by comma
            tokens = [t.strip() for t in target_str.split(",")]
            for t in tokens:
                if not t:
                    continue
                # Clean token
                t_clean = t.replace("[", "").replace("]", "").replace("~", "").strip()
                if t_clean.startswith("고 "):
                    t_clean = t_clean.replace("고 ", "")
                if t_clean.startswith("한 "):
                    t_clean = t_clean.replace("한 ", "")
                
                # Check for special expansions like "하나~열" or "일~십"
                if "하나열" in t_clean:
                    for num in ["하나", "둘", "셋", "넷", "다섯", "여섯", "일곱", "여덟", "아홉", "열"]:
                        sounds.add(num)
                elif "일십" in t_clean:
                    for num in ["일", "이", "삼", "사", "오", "육", "칠", "팔", "구", "십"]:
                        sounds.add(num)
                elif t_clean.lower() == "school":
                    sounds.add("학교")
                elif t_clean.lower() == "k-drama":
                    sounds.add("케이드라마")
                elif t_clean.lower() == "k-pop":
                    sounds.add("케이팝")
                else:
                    sounds.add(t_clean)
    except Exception as e:
        print(f"Error querying curriculum: {e}")
    finally:
        conn.close()
    
    print(f"Extracted unique target sounds from Curriculum: {len(sounds)}")
    return sounds

def ensure_tables():
    """Ensures hangeul_audio_assets table exists in SQLite and Supabase"""
    # SQLite
    conn = sqlite3.connect(SQLITE_DB)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS hangeul_audio_assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT UNIQUE NOT NULL,
        filepath TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()
    print("[SQLite] Table hangeul_audio_assets verified.")

    # Supabase (best effort)
    host = os.environ.get("SUPABASE_DB_HOST")
    if not host:
        print("[Supabase] SUPABASE_DB_HOST not set, skipping remote table setup.")
        return

    try:
        import psycopg2
        db_conn = psycopg2.connect(
            host=host,
            port=os.environ.get("SUPABASE_DB_PORT", "5432"),
            user=os.environ.get("SUPABASE_DB_USER"),
            password=os.environ.get("SUPABASE_DB_PASSWORD"),
            dbname=os.environ.get("SUPABASE_DB_NAME", "postgres"),
            sslmode="require",
            connect_timeout=10,
        )
        db_conn.autocommit = True
        cur = db_conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS hangeul_audio_assets (
            id SERIAL PRIMARY KEY,
            text VARCHAR(100) UNIQUE NOT NULL,
            filepath VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        db_conn.close()
        print("[Supabase] Table hangeul_audio_assets verified.")
    except Exception as e:
        print(f"[Supabase] Table setup failed: {e}")

def seed_db(text, filepath):
    """Inserts or updates audio asset mapping in SQLite and Supabase"""
    # SQLite
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO hangeul_audio_assets (text, filepath)
    VALUES (?, ?)
    ON CONFLICT(text) DO UPDATE SET filepath=excluded.filepath;
    """, (text, filepath))
    conn.commit()
    conn.close()

    # Supabase
    host = os.environ.get("SUPABASE_DB_HOST")
    if not host:
        return
    try:
        import psycopg2
        db_conn = psycopg2.connect(
            host=host,
            port=os.environ.get("SUPABASE_DB_PORT", "5432"),
            user=os.environ.get("SUPABASE_DB_USER"),
            password=os.environ.get("SUPABASE_DB_PASSWORD"),
            dbname=os.environ.get("SUPABASE_DB_NAME", "postgres"),
            sslmode="require",
            connect_timeout=5,
        )
        db_conn.autocommit = True
        cur = db_conn.cursor()
        cur.execute("""
        INSERT INTO hangeul_audio_assets (text, filepath)
        VALUES (%s, %s)
        ON CONFLICT(text) DO UPDATE SET filepath=EXCLUDED.filepath;
        """, (text, filepath))
        db_conn.close()
    except Exception as e:
        # Silently pass to keep console clean unless error is fatal
        pass

def main():
    ensure_tables()
    
    grammar_sounds = extract_grammar_sounds()
    curriculum_sounds = extract_curriculum_sounds()
    
    all_sounds = sorted(list(grammar_sounds.union(curriculum_sounds)))
    print(f"\nTotal unique Hangeul sounds to ensure: {len(all_sounds)}")
    
    generated_count = 0
    cached_count = 0
    err_count = 0
    
    for t in all_sounds:
        # File name layout
        filename = f"{t}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        web_path = f"/audio/jamo/{filename}"
        
        # Check cache
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            cached_count += 1
            seed_db(t, web_path)
            continue
            
        print(f" -> Generating voice audio for: '{t}'...")
        try:
            tts = gTTS(text=t, lang='ko')
            tts.save(filepath)
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                generated_count += 1
                seed_db(t, web_path)
            else:
                raise Exception("Zero byte file created.")
        except Exception as e:
            print(f"    [Error] Failed to generate '{t}': {e}")
            err_count += 1
            
    print(f"\nFinished Hangeul Phonics Seed Run:")
    print(f"  - Cached (already exists): {cached_count}")
    print(f"  - Newly Generated (gTTS):  {generated_count}")
    print(f"  - Errors / Failures:      {err_count}")

if __name__ == "__main__":
    main()
