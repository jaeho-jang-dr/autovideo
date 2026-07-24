# -*- coding: utf-8 -*-
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR_DIR = os.path.join(ROOT, "assets", "characters")
BG_DIR = os.path.join(ROOT, "w17", "backgrounds")
DB_PATH = os.path.join(ROOT, "channel", "content.db")

BAD_POSES = ["explain_polite", "comparing", "slang_phone", "study_book", "bowing_advanced"]
BAD_BGS = ["w17_bg_tohamsan_trail", "w17_bg_seokguram_entrance", "w17_bg_seokguram_grotto"]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. 포즈 지우기
    print("Cleaning up bad poses...")
    for pose in BAD_POSES:
        p_trans = os.path.join(CHAR_DIR, f"teacher_jay_{pose}.png")
        p_opaque = os.path.join(CHAR_DIR, f"teacher_jay_{pose}_opaque.png")
        for p in [p_trans, p_opaque]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                    print(f"  Deleted local file: {p}")
                except Exception as e:
                    print(f"  [ERR] Failed to delete {p}: {e}")
                    
        # DB에서 삭제
        cur.execute("DELETE FROM assets WHERE name_en = ?", (f"teacher_jay_{pose}",))
        cur.execute("DELETE FROM assets WHERE name_en = ?", (f"teacher_jay_{pose}_opaque",))
        conn.commit()
        print(f"  [DB Cleanup] Removed assets for {pose}")

    # 2. 배경 지우기
    print("Cleaning up bad backgrounds...")
    for bg in BAD_BGS:
        bg_p = os.path.join(BG_DIR, f"{bg}.png")
        if os.path.exists(bg_p):
            try:
                os.remove(bg_p)
                print(f"  Deleted local file: {bg_p}")
            except Exception as e:
                print(f"  [ERR] Failed to delete {bg_p}: {e}")
                
        # DB에서 삭제
        cur.execute("DELETE FROM assets WHERE name_en = ?", (bg,))
        conn.commit()
        print(f"  [DB Cleanup] Removed assets for {bg}")
        
    conn.close()
    
    # 3. viewer.html 재생성 (이전 에셋들만 남음)
    import subprocess
    try:
        subprocess.run(["python", "scratch/build_web_viewer.py"], check=True)
        print("Regenerated viewer.html to only show verified assets.")
    except Exception as e:
        print(f"Failed to rebuild viewer.html: {e}")
        
    print("[OK] Bad assets cleanup completed successfully.")

if __name__ == "__main__":
    main()
