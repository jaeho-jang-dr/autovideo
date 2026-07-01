# -*- coding: utf-8 -*-
import os
import sys
import shutil
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

def main():
    src_video = os.path.join(ROOT, "jay_working_desk_video_prompt", "scene_1.mp4")
    dest_dir = os.path.join(ROOT, "assets", "videos")
    os.makedirs(dest_dir, exist_ok=True)
    dest_video = os.path.join(dest_dir, "jay_working_desk_side.mp4")
    
    if not os.path.exists(src_video):
        print(f"[ERR] Source video not found: {src_video}")
        return 1
        
    shutil.copyfile(src_video, dest_video)
    print(f"Copied video -> {dest_video}")
    
    sqlite_path = os.path.join(ROOT, "channel", "content.db")
    if os.path.exists(sqlite_path):
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        
        project = "jay_working_desk"
        scene_no = 1
        scene_name = "Jay_Working_Desk_Side_Video"
        base_image = "assets/characters/jay_working_desk_side_opaque.png"
        image_prompt = (
            "sitting at a wooden desk with a laptop on it. The stickman and his desk are relatively small, "
            "showing a wider view of the room. On the back wall, there is a clock and a window. "
            "On the front wall, there is a door. There is also a bookshelf. LEFT side profile view"
        )
        motion_prompt = (
            "Keep the exact same minimalist 2D single-line stickman character named Jay sitting at the desk. "
            "The clock ticking on the back wall rotates its hands continuously. The stickman character actively "
            "types on the laptop keyboard with fast, busy hand movements. No watermark, no text, no binary code, "
            "no letters, no signatures."
        )
        file_path = "assets/videos/jay_working_desk_side.mp4"
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
