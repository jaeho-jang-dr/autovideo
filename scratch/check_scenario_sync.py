import re
import os
import sys

# cp949 인코딩 오류 방지
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

SCENARIO_PATH = "scenario.txt"
PROMPTS_PATH = "binge_watching_prompts.txt"

def check_scenario():
    print("=== [Check 1] scenario.txt structure & sequential sync ===")
    if not os.path.exists(SCENARIO_PATH):
        print("[ERR] scenario.txt not found.")
        return False
        
    with open(SCENARIO_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split by [Scene X]
    raw_blocks = re.split(r'\[Scene\s+(\d+)\]', content, flags=re.IGNORECASE)
    if len(raw_blocks) < 3:
        print("[ERR] Failed to split scenes from scenario.txt")
        return False
        
    scene_nums = []
    for i in range(1, len(raw_blocks), 2):
        scene_nums.append(int(raw_blocks[i]))
        
    print(f"Total scenes found in scenario: {len(scene_nums)}")
    
    expected = list(range(1, 97))
    missing = [x for x in expected if x not in scene_nums]
    duplicates = [x for x in scene_nums if scene_nums.count(x) > 1]
    
    if missing:
        print(f"[WARN] Missing scene numbers in scenario: {missing}")
    if duplicates:
        print(f"[WARN] Duplicate scene numbers in scenario: {set(duplicates)}")
        
    # Validate KR/EN text pairs inside block_text
    struct_ok = True
    for i in range(1, len(raw_blocks), 2):
        scene_id = int(raw_blocks[i])
        block_text = raw_blocks[i+1]
        
        has_kr = re.search(r'text:\s*(.*)', block_text, re.IGNORECASE) is not None
        has_en = re.search(r'text_en:\s*(.*)', block_text, re.IGNORECASE) is not None
        
        if not (has_kr and has_en):
            print(f"[WARN] Scene {scene_id} missing text tag(s). (text: {has_kr}, text_en: {has_en})")
            struct_ok = False
            
    if struct_ok and not missing and not duplicates:
        print("[OK] scenario.txt structure is completely valid and clean (1-96).")
        return True
    else:
        print("[FAIL] scenario.txt has structural validation errors.")
        return False

def check_prompts():
    print("\n=== [Check 2] binge_watching_prompts.txt match ===")
    if not os.path.exists(PROMPTS_PATH):
        print("[ERR] prompts file not found.")
        return False
        
    with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    scene_nums = []
    for line in lines:
        m = re.match(r"\[Scene\s+(\d+)\]", line, re.IGNORECASE)
        if m:
            scene_nums.append(int(m.group(1)))
            
    print(f"Total prompt lines found: {len(scene_nums)}")
    
    expected = list(range(1, 97))
    missing = [x for x in expected if x not in scene_nums]
    duplicates = [x for x in scene_nums if scene_nums.count(x) > 1]
    
    if missing:
        print(f"[WARN] Missing prompts scene numbers: {missing}")
    if duplicates:
        print(f"[WARN] Duplicate prompts scene numbers: {set(duplicates)}")
        
    if not missing and not duplicates and len(scene_nums) == 96:
        print("[OK] binge_watching_prompts.txt prompts list is fully valid (1-96).")
        return True
    else:
        print("[FAIL] prompts file has validation errors.")
        return False

if __name__ == "__main__":
    check_scenario()
    check_prompts()
