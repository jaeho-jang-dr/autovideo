import os
import re

def convert():
    scenario_path = os.path.abspath("child_growth_science/scenario.txt")
    prompts_path = os.path.abspath("child_growth_science/prompts.txt")
    root_prompts_path = os.path.abspath("child_growth_science_prompts.txt")

    print(f"Reading scenario from: {scenario_path}")
    if not os.path.exists(scenario_path):
        print(f"Error: {scenario_path} not found.")
        return

    with open(scenario_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by double newlines or Scene brackets
    scenes_raw = re.split(r'\n\s*\n', content.strip())
    output_lines = []

    for s_raw in scenes_raw:
        if not s_raw.strip():
            continue

        scene_match = re.search(r'\[Scene\s+(\d+)\]', s_raw, re.IGNORECASE)
        if not scene_match:
            continue
        scene_num = scene_match.group(1)

        # Extract image and motion fields
        image_match = re.search(r'image:\s*(.*)', s_raw, re.IGNORECASE)
        motion_match = re.search(r'motion:\s*(.*)', s_raw, re.IGNORECASE)

        if image_match and motion_match:
            img_prompt = image_match.group(1).strip()
            mot_prompt = motion_match.group(1).strip()
            
            # Format: [Scene X] image_prompt :: motion_prompt
            line = f"[Scene {scene_num}] {img_prompt} :: {mot_prompt}"
            output_lines.append(line)
        else:
            print(f"Warning: Failed to parse image or motion for Scene {scene_num}")

    # Write prompts inside project folder
    with open(prompts_path, "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(output_lines) + "\n")
    print(f"Generated prompts file: {prompts_path}")

    # Write prompts in root folder for convenience (matching other videos)
    with open(root_prompts_path, "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(output_lines) + "\n")
    print(f"Generated root prompts file: {root_prompts_path}")

    print(f"Parsed {len(output_lines)} scenes successfully.")

if __name__ == "__main__":
    convert()
