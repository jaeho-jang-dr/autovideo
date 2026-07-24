# -*- coding: utf-8 -*-
import os
import sys
import sqlite3
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

import tts_manager as tm

SCENARIO_PATH = os.path.join(ROOT, "w17_scenario.txt")
AUDIO_DIR = os.path.join(ROOT, "w17", "audio")
DB_PATH = os.path.join(ROOT, "channel", "content.db")

def parse_scenario(path):
    scenes = []
    current_scene = {}
    if not os.path.exists(path):
        print(f"[ERR] Scenario file not found: {path}")
        return scenes
        
    scene_idx = None
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^\[Scene\s+(\d+)\]", line)
        if m:
            if current_scene:
                scenes.append(current_scene)
            scene_idx = int(m.group(1))
            current_scene = {"id": scene_idx, "text": "", "text_en": ""}
            continue
        if line.startswith("text:"):
            current_scene["text"] = line.split(":", 1)[1].strip()
        elif line.startswith("text_en:"):
            current_scene["text_en"] = line.split(":", 1)[1].strip()
            
    if current_scene:
        scenes.append(current_scene)
    return scenes

def main():
    import shutil
    if os.path.exists(AUDIO_DIR):
        shutil.rmtree(AUDIO_DIR)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    scenes = parse_scenario(SCENARIO_PATH)
    if not scenes:
        print("[ERR] No scenes parsed.")
        return

    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    cur = conn.cursor()
    
    # Clean up DB records for w17 audio
    cur.execute("DELETE FROM hangeul_audio_assets WHERE filepath LIKE 'w17/audio/%'")
    conn.commit()

    print(f"Starting pre-rendering voiceovers for {len(scenes)} scenes...")
    for s in scenes:
        s_id = s["id"]
        # Skip empty text scenes (like endscreen card)
        if not s["text"] and not s["text_en"]:
            continue
            
        print(f"--- Processing Scene {s_id} ---")
        
        # 1. Render Korean (SunHi)
        if s["text"]:
            ko_path = os.path.join(AUDIO_DIR, f"scene_{s_id}_ko.mp3")
            success = True
            if not os.path.exists(ko_path) or os.path.getsize(ko_path) == 0:
                print(f"  Rendering KO for scene {s_id}")
                success = tm.save_tts_edge_tts(s["text"], ko_path, lang="ko")
            else:
                print(f"  [Skipped] KO already exists: {ko_path}")
                
            if success:
                # Save to hangeul_audio_assets DB
                rel_path = f"w17/audio/scene_{s_id}_ko.mp3"
                cur.execute("DELETE FROM hangeul_audio_assets WHERE text = ?", (s["text"],))
                cur.execute("INSERT INTO hangeul_audio_assets (text, filepath) VALUES (?, ?)", (s["text"], rel_path))
                conn.commit()
                print(f"  [DB Sync] KO registered: {rel_path}")

        # 2. Render English (Emma)
        if s["text_en"]:
            en_path = os.path.join(AUDIO_DIR, f"scene_{s_id}_en.mp3")
            success = True
            if not os.path.exists(en_path) or os.path.getsize(en_path) == 0:
                print(f"  Rendering EN for scene {s_id}")
                success = tm.save_tts_edge_tts(s["text_en"], en_path, lang="en")
            else:
                print(f"  [Skipped] EN already exists: {en_path}")
                
            if success:
                rel_path = f"w17/audio/scene_{s_id}_en.mp3"
                cur.execute("DELETE FROM hangeul_audio_assets WHERE text = ?", (s["text_en"],))
                cur.execute("INSERT INTO hangeul_audio_assets (text, filepath) VALUES (?, ?)", (s["text_en"], rel_path))
                conn.commit()
                print(f"  [DB Sync] EN registered: {rel_path}")

    conn.close()
    print("[OK] Pre-rendering voiceover DB completed.")

if __name__ == "__main__":
    main()
