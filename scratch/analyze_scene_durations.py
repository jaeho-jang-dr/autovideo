import os
import sys
import re

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moviepy import AudioFileClip, VideoFileClip
import moviepy.video.fx as fx
from tts_manager import save_tts

scenario_path = r"d:\Entertainments\DevEnvironment\autovideo\workout_injury_science\scenario.txt"
output_dir = r"d:\Entertainments\DevEnvironment\autovideo\workout_injury_science"
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

# Calculate durations
timeline = []
current_time = 0.0

if os.path.exists(intro_path):
    intro_dur = VideoFileClip(intro_path).duration
    timeline.append(("Intro", current_time, current_time + intro_dur, intro_dur))
    current_time += intro_dur
else:
    timeline.append(("Intro", 0.0, 0.0, 0.0))

for scene in scenes:
    audio_path = f"assets/audio/scene_{scene['id']}.mp3"
    # Calculate audio duration (gTTS with speed 1.1x)
    if not os.path.exists(audio_path):
        save_tts(scene['text'], audio_path, lang='ko')
    
    raw_audio = AudioFileClip(audio_path)
    audio_clip = raw_audio.with_effects([fx.MultiplySpeed(1.1)])
    dur = audio_clip.duration
    
    timeline.append((f"Scene {scene['id']}", current_time, current_time + dur, dur))
    current_time += dur
    raw_audio.close()
    audio_clip.close()

if os.path.exists(outro_path):
    outro_dur = VideoFileClip(outro_path).duration
    timeline.append(("Outro", current_time, current_time + outro_dur, outro_dur))
    current_time += outro_dur
else:
    timeline.append(("Outro", current_time, current_time, 0.0))

print("\n--- Video Timeline ---")
for name, start, end, dur in timeline[-5:]:  # Show last 5 segments
    print(f"{name}: {start:.2f}s ~ {end:.2f}s (Duration: {dur:.2f}s)")
print(f"Calculated Total Duration: {current_time:.2f}s")
