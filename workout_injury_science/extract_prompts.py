import re

with open("workout_injury_science/scenario.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Split by scenes
raw_blocks = re.split(r'\[Scene\s+(\d+)\]', content, flags=re.IGNORECASE)

prompts = []
for i in range(1, len(raw_blocks), 2):
    scene_id = int(raw_blocks[i])
    block_text = raw_blocks[i+1]
    
    # Extract image prompt
    image_match = re.search(r'image:\s*(.*)', block_text, re.IGNORECASE)
    if image_match:
        img_prompt = image_match.group(1).strip()
        prompts.append(f"[Scene {scene_id}] {img_prompt}")

with open("workout_injury_science/prompts_for_veo.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(prompts))

print(f"Extracted {len(prompts)} prompts to workout_injury_science/prompts_for_veo.txt")
