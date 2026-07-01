import os
import sys
import re

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moviepy import AudioFileClip, VideoFileClip
import moviepy.video.fx as fx
from tts_manager import save_tts

scenario_path = r"d:\Entertainments\DevEnvironment\autovideo\child_growth_science\scenario.txt"
output_dir = r"d:\Entertainments\DevEnvironment\autovideo\child_growth_science"
intro_path = r"d:\Entertainments\DevEnvironment\autovideo\assets\intro.mp4"
outro_path = r"d:\Entertainments\DevEnvironment\autovideo\assets\outro.mp4"

def parse_scenario(scenario_path):
    scenes = []
    with open(scenario_path, "r", encoding="utf-8") as f:
        content = f.read()
    raw_blocks = re.split(r'\[Scene\s+(\d+)\]', content, flags=re.IGNORECASE)
    for i in range(1, len(raw_blocks), 2):
        scene_id = int(raw_blocks[i])
        block_text = raw_blocks[i+1]
        text_match = re.search(r'text:\s*(.*)', block_text, re.IGNORECASE)
        text = text_match.group(1).strip() if text_match else ""
        scenes.append({"id": scene_id, "text": text})
    return scenes

scenes = parse_scenario(scenario_path)

timeline = []
current_time = 0.0

if os.path.exists(intro_path):
    intro_dur = VideoFileClip(intro_path).duration
    timeline.append(("Intro", current_time, current_time + intro_dur, intro_dur))
    current_time += intro_dur
else:
    timeline.append(("Intro", 0.0, 0.0, 0.0))

# Analyze up to Scene 25
for scene in scenes[:25]:
    audio_path = f"assets/audio/scene_{scene['id']}.mp3"
    # Ensure audio exists in child_growth_science or global assets
    # For child_growth_science, it might use child_growth_science/assets/audio
    # Let's check child_growth_science/assets/audio/scene_*.mp3 first
    local_audio = os.path.join(output_dir, "assets", "audio", f"scene_{scene['id']}.mp3")
    global_audio = f"assets/audio/scene_{scene['id']}.mp3"
    
    audio_file = local_audio if os.path.exists(local_audio) else global_audio
    
    if not os.path.exists(audio_file):
        # We need to make sure we don't overwrite other project audios, so save to local project path
        save_tts(scene['text'], local_audio, lang='ko')
        audio_file = local_audio
    
    raw_audio = AudioFileClip(audio_file)
    audio_clip = raw_audio.with_effects([fx.MultiplySpeed(1.1)])
    dur = audio_clip.duration
    
    timeline.append((f"Scene {scene['id']}", current_time, current_time + dur, dur))
    current_time += dur
    raw_audio.close()
    audio_clip.close()

print("\n--- Child Growth Video Timeline ---")
for name, start, end, dur in timeline[15:22]:  # Show around Scene 18
    print(f"{name}: {start:.2f}s ~ {end:.2f}s (Duration: {dur:.2f}s)")
print(f"Calculated Duration at Scene 20: {current_time:.2f}s")
