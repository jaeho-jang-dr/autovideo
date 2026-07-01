# -*- coding: utf-8 -*-
import os
import sys
import sqlite3
import psycopg2
from sentence_transformers import SentenceTransformer

# Force UTF-8 stdout
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

# 25 Jieun Character poses mapping
CHARACTER_POSES = [
    ("character_waking_up", "지은_기상", "Jieun_Waking", "character_waking_up.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform waking up and stretching in bed, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text, no signatures"),
    ("character_packing", "지은_준비", "Jieun_Packing", "character_packing.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform placing books into a backpack on a study desk, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_washing", "지은_세수", "Jieun_Washing", "character_washing.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair washing face at a bathroom sink, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_eating", "지은_식사", "Jieun_Eating", "character_eating.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform eating breakfast at a dining table, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_walking", "지은_등교", "Jieun_Walking", "character_walking.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform walking out of a door towards a street, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_sleeping", "지은_취침", "Jieun_Sleeping", "character_sleeping.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair lying in bed sleeping, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_brushing_teeth", "지은_양치", "Jieun_BrushingTeeth", "character_brushing_teeth.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair brushing teeth with a toothbrush, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_studying", "지은_공부", "Jieun_Studying", "character_studying.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform sitting at a desk studying and writing, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_reading", "지은_독서", "Jieun_Reading", "character_reading.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair holding and reading a book, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_sitting", "지은_휴식", "Jieun_Sitting", "character_sitting.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform sitting on a chair resting, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_running", "지은_달리기", "Jieun_Running", "character_running.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform running in a hurry, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_pointing", "지은_지시", "Jieun_Pointing", "character_pointing.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair pointing forward with her hand, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_cheering", "지은_환호", "Jieun_Cheering", "character_cheering.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform cheering with arms raised in joy, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_bowing", "지은_인사", "Jieun_Bowing", "character_bowing.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform bowing politely, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_thinking", "지은_생각", "Jieun_Thinking", "character_thinking.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair thinking with a hand on her chin, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_raising_hand", "지은_질문", "Jieun_RaisingHand", "character_raising_hand.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform raising her hand to speak, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_drawing", "지은_그리기", "Jieun_Drawing", "character_drawing.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair drawing on a sketchbook, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_drinking", "지은_음용", "Jieun_Drinking", "character_drinking.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair holding a cup and drinking water, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_cleaning", "지은_청소", "Jieun_Cleaning", "character_cleaning.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair holding a broom sweeping the floor, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_opening_door", "지은_개문", "Jieun_OpeningDoor", "character_opening_door.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair holding a door handle to open it, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_shoes", "지은_신발신기", "Jieun_Shoes", "character_shoes.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair bending down to put on sneakers, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_waiting", "지은_대기", "Jieun_Waiting", "character_waiting.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform waiting at a bus stop, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_waving", "지은_작별", "Jieun_Waving", "character_waving.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform waving her hand to say goodbye, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_clapping", "지은_박수", "Jieun_Clapping", "character_clapping.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair clapping hands happily, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text"),
    ("character_jumping", "지은_도약", "Jieun_Jumping", "character_jumping.png", 
     "Minimalist 2D line art of a simple Korean schoolgirl stickman character named Jieun with long hair and a school uniform jumping in the air in excitement, thick black outlines, clean whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), no text")
]

def update_sqlite():
    db_path = "channel/content.db"
    if not os.path.exists(db_path):
        print(f"[ERR] SQLite {db_path} not found.")
        sys.exit(1)
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print("Updating assets in SQLite Content DB...")
    
    for key, name_kr, name_en, file_path, prompt in CHARACTER_POSES:
        # Check if asset already exists
        cur.execute("SELECT id FROM assets WHERE file_path = ?", (file_path,))
        row = cur.fetchone()
        
        if row:
            # Update existing
            cur.execute("""
                UPDATE assets 
                SET name_kr = ?, name_en = ?, flow_prompt = ?
                WHERE file_path = ?
            """, (name_kr, name_en, prompt, file_path))
            print(f"  [SQLITE-UPDATE] {file_path}")
        else:
            # Insert new
            cur.execute("""
                INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt)
                VALUES (?, ?, 'character', ?, ?)
            """, (name_kr, name_en, file_path, prompt))
            print(f"  [SQLITE-INSERT] {file_path}")
            
    conn.commit()
    conn.close()
    print("SQLite Update Complete.")

def update_supabase_and_embeddings():
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Establish connection to Supabase Postgres
    try:
        conn = psycopg2.connect(
            host="aws-1-ap-northeast-2.pooler.supabase.com",
            port=5432,
            user="postgres.dggxjxgnsecspiubaeie",
            password="sRlfjrl77!!",
            database="postgres"
        )
        cur = conn.cursor()
        
        # Reset the ID identity sequence to avoid unique constraint violation
        cur.execute("SELECT COALESCE(MAX(id), 0) FROM assets;")
        max_id = cur.fetchone()[0]
        cur.execute(f"ALTER TABLE assets ALTER COLUMN id RESTART WITH {max_id + 1};")
        print(f"  [SUPABASE-SEQ-RESET] Set sequence to restart with {max_id + 1}")
    except Exception as e:
        print(f"[ERR] Supabase DB connection/init failed: {e}")
        return
        
    print("Upserting assets to remote Supabase DB and inserting pgvector embeddings...")
    
    for key, name_kr, name_en, file_path, prompt in CHARACTER_POSES:
        # Generate 384d embedding
        emb = model.encode(prompt).tolist()
        emb_str = "[" + ",".join(map(str, emb)) + "]"
        
        # Check if exists in Supabase
        cur.execute("SELECT id FROM assets WHERE file_path = %s", (file_path,))
        row = cur.fetchone()
        
        if row:
            # Update
            cur.execute("""
                UPDATE assets 
                SET name_kr = %s, name_en = %s, flow_prompt = %s, embedding = %s
                WHERE file_path = %s
            """, (name_kr, name_en, prompt, emb_str, file_path))
            print(f"  [SUPABASE-UPDATE + VECTOR] {file_path}")
        else:
            # Insert
            cur.execute("""
                INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt, embedding)
                VALUES (%s, %s, 'character', %s, %s, %s)
            """, (name_kr, name_en, file_path, prompt, emb_str))
            print(f"  [SUPABASE-INSERT + VECTOR] {file_path}")
        
    conn.commit()
    cur.close()
    conn.close()
    print("Supabase Postgres Update Complete.")

if __name__ == "__main__":
    update_sqlite()
    update_supabase_and_embeddings()
