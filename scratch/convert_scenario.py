import re

def convert():
    print("Converting scenario.txt into scenario_prompts.txt...")
    with open("scenario.txt", "r", encoding="utf-8") as f:
        content = f.read()

    # Split by double newlines to separate scenes
    scenes_raw = re.split(r'\n\s*\n', content.strip())
    
    output_lines = []
    
    for s_raw in scenes_raw:
        if not s_raw.strip():
            continue
        
        # Extract Scene number
        scene_match = re.search(r'\[Scene\s+(\d+)\]', s_raw, re.IGNORECASE)
        if not scene_match:
            continue
        scene_num = scene_match.group(1)
        
        # Extract image prompt
        image_match = re.search(r'image:\s*(.*)', s_raw, re.IGNORECASE)
        # Extract motion prompt
        motion_match = re.search(r'motion:\s*(.*)', s_raw, re.IGNORECASE)
        
        if image_match and motion_match:
            img_prompt = image_match.group(1).strip()
            mot_prompt = motion_match.group(1).strip()
            line = f"[Scene {scene_num}] {img_prompt} :: {mot_prompt}"
            output_lines.append(line)
            print(f"Scene {scene_num} parsed successfully.")
        else:
            print(f"Failed to parse scene properties for Scene {scene_num}")

    with open("scenario_prompts.txt", "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(output_lines) + "\n")
        
    print("Conversion completed successfully! Generated scenario_prompts.txt.")

if __name__ == "__main__":
    convert()
