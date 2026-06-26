import sqlite3
import json
import os
import shutil

def find_file_recursively(base_name, search_dirs):
    for s_dir in search_dirs:
        if not os.path.exists(s_dir):
            continue
        for root, dirs, files in os.walk(s_dir):
            if base_name in files:
                return os.path.join(root, base_name)
    return None

def main():
    db_path = 'channel/content.db'
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found.")
        return

    # 1) Query all required assets (character, letter, object)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, name_kr, name_en, type, file_path, flow_prompt FROM assets WHERE type IN ('character', 'letter', 'object');")
    rows = cur.fetchall()
    
    search_dirs = [
        'assets/graphics',
        'assets/graphics/letters',
        'home_vocab',
        'zolla_dynamite_veo',
        'zolla_hangul',
        'zolla_waltz',
        'vocab_assets',
        'workout_injury_science/assets',
        'chiropractic_science/assets',
        'sleep_science/assets',
        'scratch/vocab_assets',
        'scratch/layers'
    ]
    
    # Destination base directory
    dest_base = 'web/public/images'
    
    assets = []
    copied_count = 0
    not_found_files = []
    
    for r in rows:
        asset_id = r[0]
        name_kr = r[1]
        name_en = r[2]
        asset_type = r[3]
        file_path_db = r[4]
        flow_prompt = r[5]
        
        if not file_path_db:
            continue
            
        file_name = os.path.basename(file_path_db)
        
        # 2) Setup specific destination subfolder based on asset type
        subfolder = "characters"
        if asset_type == "letter":
            subfolder = "letters"
        elif asset_type == "object":
            subfolder = "objects"
            
        dest_dir = os.path.join(dest_base, subfolder)
        os.makedirs(dest_dir, exist_ok=True)
        
        # File search & Copy
        source_path = find_file_recursively(file_name, search_dirs)
        
        if source_path:
            shutil.copy2(source_path, os.path.join(dest_dir, file_name))
            copied_count += 1
            web_url = f"/images/{subfolder}/{file_name}"
        else:
            not_found_files.append(file_name)
            web_url = f"/images/{subfolder}/{file_name}"
            
        assets.append({
            "id": asset_id,
            "name_kr": name_kr,
            "name_en": name_en,
            "type": asset_type,
            "file_path": file_path_db,
            "url": web_url,
            "flow_prompt": flow_prompt
        })
        
    out_dir = 'web/src/data'
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'character_assets.json')
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(assets, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully processed {len(assets)} assets.")
    print(f" -> Copied to web/public: {copied_count} files")
    if not_found_files:
        print(f" -> Warning: {len(not_found_files)} files not found locally: {list(set(not_found_files))[:5]}...")
    
    conn.close()

if __name__ == "__main__":
    main()

