import sqlite3
import re
import os

scenario_path = r"d:\Entertainments\DevEnvironment\autovideo\scenario.txt"
db_path = r"d:\Entertainments\DevEnvironment\autovideo\channel\content.db"

def parse_scenario():
    with open(scenario_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    blocks = re.split(r'\[Scene\s+(\d+)\]', content, flags=re.IGNORECASE)
    scenes = []
    
    for i in range(1, len(blocks), 2):
        seq = int(blocks[i])
        body = blocks[i+1].strip()
        
        kr_match = re.search(r'text:\s*(.*)', body, re.IGNORECASE)
        en_match = re.search(r'text_en:\s*(.*)', body, re.IGNORECASE)
        img_match = re.search(r'image:\s*(.*)', body, re.IGNORECASE)
        mot_match = re.search(r'motion:\s*(.*)', body, re.IGNORECASE)
        
        kr = kr_match.group(1).strip() if kr_match else ""
        en = en_match.group(1).strip() if en_match else ""
        img = img_match.group(1).strip() if img_match else ""
        mot = mot_match.group(1).strip() if mot_match else ""
        
        scenes.append((seq, kr, en, img, mot))
    return scenes

def main():
    if not os.path.exists(db_path):
        print("Database not found! Run seed command first.")
        return
        
    scenes = parse_scenario()
    print(f"Parsed {len(scenes)} scenes from scenario.txt.")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Update Episode metadata for CA-001
    cur.execute("""
        UPDATE episodes 
        SET title_kr = ?, title_en = ?, hook_kr = ?, logline_kr = ?, status = 'scripted'
        WHERE code = 'CA-001'
    """, (
        "몰아보기는 정말 우리 몸에 나쁠까?",
        "Is Binge Watching Bad For You?",
        "침대에 누워 드라마를 몰아보는 일, 정말 우리 몸에 괜찮을까요?",
        "뇌 도파민 회로, 신체 비활동성(정형외과적 디스크 하중/혈전/대사), 안구 피로/수면 분석 및 해결책"
    ))
    
    # 2. Clear old scenes for CA-001
    cur.execute("DELETE FROM scenes WHERE episode = 'CA-001'")
    
    # 3. Seed new scenes
    for seq, kr, en, img, mot in scenes:
        cur.execute("""
            INSERT INTO scenes (episode, seq, script_kr, script_en, image_prompt, veo_prompt, duration_sec)
            VALUES (?, ?, ?, ?, ?, ?, 5.0)
        """, ("CA-001", seq, kr, en, img, mot))
        
    conn.commit()
    conn.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    main()
