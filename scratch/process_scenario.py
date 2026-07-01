import re
import os

raw_path = r"d:\Entertainments\DevEnvironment\autovideo\scratch\extracted_script_raw.txt"
scenario_path = r"d:\Entertainments\DevEnvironment\autovideo\scenario.txt"

def main():
    if not os.path.exists(raw_path):
        print("Raw script not found!")
        return
        
    with open(raw_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # We want to extract only the part starting from "Scene 1" up to the end
    # Let's locate the first "Scene 1"
    match = re.search(r'(Scene 1\nScript KR:.*)', content, re.DOTALL | re.IGNORECASE)
    if not match:
        # Fallback to search without newline if it looks slightly different
        match = re.search(r'(Scene 1.*)', content, re.DOTALL | re.IGNORECASE)
        
    if match:
        script_body = match.group(1).strip()
        
        # We need to format it to standard scenario.txt format:
        # [Scene N]
        # text: <Script KR>
        # image: <Image Prompt>
        # motion: <Motion Prompt>
        
        # Let's parse each scene block
        # Blocks are divided by Scene \d+
        scenes = re.split(r'Scene\s+(\d+)\n?', script_body, flags=re.IGNORECASE)
        
        formatted_blocks = []
        for i in range(1, len(scenes), 2):
            scene_num = scenes[i]
            body = scenes[i+1].strip()
            
            # Extract fields
            kr_match = re.search(r'Script KR:\s*(.*?)(?=\nScript EN:|\nImage Prompt:|\nMotion Prompt:|$)', body, re.DOTALL | re.IGNORECASE)
            en_match = re.search(r'Script EN:\s*(.*?)(?=\nScript KR:|\nImage Prompt:|\nMotion Prompt:|$)', body, re.DOTALL | re.IGNORECASE)
            img_match = re.search(r'Image Prompt:\s*(.*?)(?=\nScript KR:|\nScript EN:|\nMotion Prompt:|$)', body, re.DOTALL | re.IGNORECASE)
            mot_match = re.search(r'Motion Prompt:\s*(.*?)(?=\nScript KR:|\nScript EN:|\nImage Prompt:|$)', body, re.DOTALL | re.IGNORECASE)
            
            kr_text = kr_match.group(1).strip() if kr_match else ""
            en_text = en_match.group(1).strip() if en_match else ""
            img_prompt = img_match.group(1).strip() if img_match else ""
            mot_prompt = mot_match.group(1).strip() if mot_match else ""
            
            # Clean up quotes if present in the subagent response
            if img_prompt.startswith('"') and img_prompt.endswith('"'):
                img_prompt = img_prompt[1:-1]
            if mot_prompt.startswith('"') and mot_prompt.endswith('"'):
                mot_prompt = mot_prompt[1:-1]
                
            # Let's build the block
            # For make_video.py, it expects:
            # [Scene N]
            # text: <Korean script> (as make_video uses text: for Korean TTS and subtitles)
            # image: <Image Path> (it automatically maps this in make_video.py but we will write it cleanly)
            # motion: <Motion Prompt>
            
            # Let's write the formatted version
            block = f"[Scene {scene_num}]\n"
            block += f"text: {kr_text}\n"
            block += f"text_en: {en_text}\n" # Include English script for reference/DB seeding
            block += f"image: {img_prompt}\n"
            block += f"motion: {mot_prompt}\n"
            formatted_blocks.append(block)
            
        final_scenario = "\n".join(formatted_blocks)
        with open(scenario_path, "w", encoding="utf-8") as out:
            out.write(final_scenario)
        print(f"Successfully processed and wrote scenario to {scenario_path} (Total scenes: {len(formatted_blocks)})")
    else:
        print("Could not locate Scene 1 block!")

if __name__ == "__main__":
    main()
