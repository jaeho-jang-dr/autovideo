import sqlite3
import os
import re

db_path = r"channel/content.db"
scenario_path = r"turtle_neck_science/scenario.txt"
prompts_path = r"turtle_neck_science/prompts_for_veo.txt"

def parse_scenario(path):
    scenes = []
    if not os.path.exists(path):
        return scenes
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    raw_blocks = re.split(r'\[Scene\s+(\d+)\]', content, flags=re.IGNORECASE)
    for i in range(1, len(raw_blocks), 2):
        scene_id = int(raw_blocks[i])
        block_text = raw_blocks[i+1]
        
        text_match = re.search(r'text:\s*(.*)', block_text, re.IGNORECASE)
        text_en_match = re.search(r'text_en:\s*(.*)', block_text, re.IGNORECASE)
        
        text = text_match.group(1).strip() if text_match else ""
        text_en = text_en_match.group(1).strip() if text_en_match else ""
        
        scenes.append({
            "seq": scene_id,
            "script_kr": text,
            "script_en": text_en
        })
    return scenes

def parse_prompts(path):
    prompts = {}
    if not os.path.exists(path):
        return prompts
        
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = re.match(r'\[Scene\s+(\d+)\]\s*(.*)', line, re.IGNORECASE)
        if match:
            scene_id = int(match.group(1))
            prompt_content = match.group(2).strip()
            
            # Split by :: or :: ::
            parts = re.split(r'::\s*::|::', prompt_content)
            img_prompt = parts[0].strip()
            veo_prompt = parts[1].strip() if len(parts) > 1 else ""
            
            prompts[scene_id] = {
                "image_prompt": img_prompt,
                "veo_prompt": veo_prompt
            }
    return prompts

def main():
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return
        
    scenes_data = parse_scenario(scenario_path)
    prompts_data = parse_prompts(prompts_path)
    
    if not scenes_data:
        print("Error: No scenes parsed from scenario.txt")
        return
        
    print(f"Parsed {len(scenes_data)} scenes from scenario.txt")
    print(f"Parsed {len(prompts_data)} prompts from prompts_for_veo.txt")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Update episode meta
    cur.execute("""
        UPDATE episodes 
        SET title_kr = '스마트폰과 거북목, 인류의 다음 진화?',
            title_en = 'Text Neck: A New Human Spine?',
            status = 'scripted',
            style_profile = 'assets/profiles/black_box_sub.json'
        WHERE code = 'MD-003';
    """)
    print("Updated episode MD-003 status to 'scripted'")
    
    # 2. Delete existing scenes for MD-003 to prevent duplicates
    cur.execute("DELETE FROM scenes WHERE episode = 'MD-003';")
    print("Cleared existing scenes for MD-003")
    
    # 3. Insert new scenes
    inserted_count = 0
    for scene in scenes_data:
        seq = scene["seq"]
        script_kr = scene["script_kr"]
        script_en = scene["script_en"]
        
        prompt = prompts_data.get(seq, {"image_prompt": "", "veo_prompt": ""})
        image_prompt = prompt["image_prompt"]
        veo_prompt = prompt["veo_prompt"]
        
        # Estimate duration: approx 5-8 seconds based on word counts
        duration = max(5.0, len(script_kr) * 0.15)
        
        cur.execute("""
            INSERT INTO scenes (episode, seq, script_kr, script_en, image_prompt, veo_prompt, duration_sec)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, ("MD-003", seq, script_kr, script_en, image_prompt, veo_prompt, duration))
        inserted_count += 1
        
    conn.commit()
    conn.close()
    print(f"Successfully seeded {inserted_count} scenes into SQLite database for MD-003 [OK]")

if __name__ == "__main__":
    main()
