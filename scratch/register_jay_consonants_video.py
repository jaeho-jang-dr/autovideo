# -*- coding: utf-8 -*-
import os
import sys
import shutil
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

def main():
    src_video = os.path.join(ROOT, "jay_whiteboard_consonants_prompt", "scene_1.mp4")
    dest_dir = os.path.join(ROOT, "assets", "videos")
    os.makedirs(dest_dir, exist_ok=True)
    dest_video = os.path.join(dest_dir, "jay_whiteboard_consonants.mp4")
    
    if not os.path.exists(src_video):
        print(f"[ERR] Source video not found: {src_video}")
        return 1
        
    shutil.copyfile(src_video, dest_video)
    print(f"Copied consonants video -> {dest_video}")
    
    sqlite_path = os.path.join(ROOT, "channel", "content.db")
    if os.path.exists(sqlite_path):
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        
        project = "jay_whiteboard_consonants"
        scene_no = 1
        scene_name = "Jay_Whiteboard_Consonants_Video"
        base_image = "assets/characters/jay_whiteboard_writing_side_opaque.png"
        image_prompt = (
            "standing in front of a large white whiteboard, holding a whiteboard marker in his hand, "
            "and writing Hangeul letters on the whiteboard. LEFT side profile view"
        )
        motion_prompt = (
            "Keep the exact same minimalist 2D single-line stickman character named Jay standing at the large whiteboard. "
            "The stickman character actively and slowly writes ONLY the Hangeul consonants 'ㄱ', 'ㄴ', 'ㅁ', 'ㅅ', 'ㅎ' "
            "on the board with slow, clear arm movements. No other characters or letters, only those five consonants. "
            "No watermark, no text, no binary code, no letters, no signatures."
        )
        file_path = "assets/videos/jay_whiteboard_consonants.mp4"
        duration_sec = 8.0
        status = "success"
        
        # Check if exists
        cur.execute("SELECT id FROM video_clips WHERE project=? AND scene_no=?", (project, scene_no))
        row = cur.fetchone()
        
        if row:
            cur.execute("""
                UPDATE video_clips
                SET scene_name=?, base_image=?, image_prompt=?, motion_prompt=?, file_path=?, duration_sec=?, status=?
                WHERE id=?
            """, (scene_name, base_image, image_prompt, motion_prompt, file_path, duration_sec, status, row[0]))
            print(f"Updated local SQLite video_clips record (ID: {row[0]})")
        else:
            cur.execute("""
                INSERT INTO video_clips (project, scene_no, scene_name, base_image, image_prompt, motion_prompt, file_path, duration_sec, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (project, scene_no, scene_name, base_image, image_prompt, motion_prompt, file_path, duration_sec, status))
            print("Inserted new local SQLite video_clips record!")
            
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("[ERR] content.db not found!")
        
    return 0

if __name__ == "__main__":
    main()
