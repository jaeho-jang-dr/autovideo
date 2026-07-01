import sqlite3
import os

db_path = r"d:\Entertainments\DevEnvironment\autovideo\channel\content.db"
prompts_path = r"d:\Entertainments\DevEnvironment\autovideo\binge_watching_prompts.txt"

def main():
    if not os.path.exists(db_path):
        print("Database not found!")
        return
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    rows = cur.execute("""
        SELECT seq, image_prompt, veo_prompt 
        FROM scenes 
        WHERE episode = 'CA-001' 
        ORDER BY seq
    """).fetchall()
    
    lines = []
    for seq, img, veo in rows:
        veo_clean = veo.replace("::", "").strip()
        if veo_clean.startswith("slow motion"):
            veo_clean = veo_clean.replace("slow motion", "").strip()
        lines.append(f"[Scene {seq}] {img} :: slow motion {veo_clean}")
        
    with open(prompts_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    conn.close()
    print(f"Successfully generated {len(lines)} prompts to {prompts_path}")

if __name__ == "__main__":
    main()
