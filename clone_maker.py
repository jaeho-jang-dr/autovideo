import os
import sys
import json
from gtts import gTTS
from moviepy import AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, VideoFileClip
import moviepy.video.fx as fx

# Ensure directories
os.makedirs("assets/audio", exist_ok=True)
os.makedirs("assets/videos", exist_ok=True)

# 10-scene script for the cloned video (matching dopamine/brain topic style)
SCENES = [
    {
        "id": 1,
        "text": "스마트폰을 켜는 순간, 뇌 속에서 강력한 신경물질인 도파민이 마구 뿜어져 나오기 시작합니다.",
        "image": "assets/images/scene_1.png"
    },
    {
        "id": 2,
        "text": "이 도파민은 뇌의 보상체계를 자극해 우리를 즉각적인 쾌락에 빠지게 만듭니다.",
        "image": "assets/images/scene_2.png"
    },
    {
        "id": 3,
        "text": "하지만 이런 강력하고 자극적인 즉각 보상은 우리의 집중력과 자제력을 파괴합니다.",
        "image": "assets/images/scene_3.png"
    },
    {
        "id": 4,
        "text": "뇌 과학자들은 단 하루 동안만이라도 스마트폰을 멀리하는 도파민 단식을 제안합니다.",
        "image": "assets/images/scene_4.png"
    },
    {
        "id": 5,
        "text": "도파민 단식은 지쳐 있던 뇌의 전두엽을 쉬게 하고 정상적인 신경회로를 회복시킵니다.",
        "image": "assets/images/scene_5.png"
    },
    {
        "id": 6,
        "text": "단 며칠 만에 산만하던 머리가 맑아지고 무너진 집중력이 되살아나는 신비로운 경험을 하게 되죠.",
        "image": "assets/images/scene_6.png"
    },
    {
        "id": 7,
        "text": "명상과 가벼운 산책은 자극에 찌든 도파민 수용체를 정화하는 데 큰 도움을 줍니다.",
        "image": "assets/images/scene_7.png"
    },
    {
        "id": 8,
        "text": "지속가능하고 건강한 도파민 분비를 유도해 인간 본연의 의지력을 복구하는 것입니다.",
        "image": "assets/images/scene_8.png"
    },
    {
        "id": 9,
        "text": "오늘부터 스마트폰 알림을 끄고 당신의 뇌에게 고요한 안식을 선물해 주는 것은 어떨까요?",
        "image": "assets/images/scene_9.png"
    },
    {
        "id": 10,
        "text": "구독과 좋아요를 하시면 매주 흥미진진하고 지혜로운 뇌 과학 지식을 만나실 수 있습니다.",
        "image": "assets/images/scene_10.png"
    }
]

def wrap_text(text, max_chars=30):
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        if len(' '.join(current_line + [word])) <= max_chars:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return '\n'.join(lines)

def parse_scenario_file(path):
    scenes = []
    if not os.path.exists(path):
        print(f"Error: Scenario file not found: {path}")
        return scenes
        
    import re
    current_scene = {}
    scene_pat = re.compile(r"\[Scene\s+(\d+)\]", re.IGNORECASE)
    
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            m = scene_pat.match(line_str)
            if m:
                if current_scene and "text" in current_scene:
                    scenes.append(current_scene)
                current_scene = {"id": int(m.group(1))}
            elif ":" in line_str:
                parts = line_str.split(":", 1)
                key = parts[0].strip().lower()
                val = parts[1].strip()
                if key in ("text", "image", "motion"):
                    current_scene[key] = val
                    
        if current_scene and "text" in current_scene:
            scenes.append(current_scene)
    return scenes

def make_cloned_video(profile_path="reference_profile.json", output_path="cloned_video.mp4", scenario_path=None):
    if not os.path.exists(profile_path):
        print(f"Error: Profile file not found: {profile_path}")
        return False
        
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)
        
    ref_scenes = profile.get("scenes", [])
    if not ref_scenes and profile_path != "reference_profile.json":
        if os.path.exists("reference_profile.json"):
            try:
                with open("reference_profile.json", "r", encoding="utf-8") as ref_f:
                    ref_profile = json.load(ref_f)
                    ref_scenes = ref_profile.get("scenes", [])
                    print("Loaded scene timings from reference_profile.json fallback.")
            except Exception as e:
                print(f"Warning: Could not load fallback reference_profile.json: {e}")
                
    sub_style = profile.get("subtitle_style", {})
    
    # Load scenario scenes
    if scenario_path:
        scenes_data = parse_scenario_file(scenario_path)
        if not scenes_data:
            print("Error: Loaded scenario data is empty.")
            return False
    else:
        scenes_data = SCENES
        
    # Check if we have enough video assets
    num_scenes = min(len(scenes_data), len(ref_scenes))
    print(f"Cloning {num_scenes} scenes based on reference profile...")
    
    # Pre-flight check for videos
    missing = []
    for idx in range(num_scenes):
        scene_cfg = scenes_data[idx]
        scene_id = scene_cfg["id"]
        video_file = f"assets/videos/scene_{scene_id}.mp4"
        if not os.path.exists(video_file):
            missing.append(video_file)
            
    if missing:
        print("Warning: The following motion video assets are missing:")
        for m in missing:
            print(f"  - {m}")
        print("Falling back to copying hypnosis videos or existing scene clips to proceed with compilation.")
        
    clips = []
    
    for idx in range(num_scenes):
        scene_cfg = scenes_data[idx]
        ref_scene = ref_scenes[idx]
        
        # Reference duration for this scene
        target_duration = ref_scene["duration"]
        scene_id = scene_cfg["id"]
        
        # 1. Generate TTS
        audio_path = f"assets/audio/scene_{scene_id}.mp3"
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass
        tts = gTTS(text=scene_cfg["text"], lang="ko")
        tts.save(audio_path)
        
        # Load audio
        audio_clip = AudioFileClip(audio_path)
        # Scale audio to exactly match target_duration
        speed_factor = audio_clip.duration / target_duration
        audio_clip = audio_clip.with_effects([fx.MultiplySpeed(speed_factor)])
        
        # 2. Load Video Clip
        video_file = f"assets/videos/scene_{scene_id}.mp4"
        if not os.path.exists(video_file):
            # Fallback: search for any available mp4 inside assets/videos/
            fallback_found = False
            for root, dirs, files in os.walk("assets/videos"):
                for file in files:
                    if file.endswith(".mp4") and not file.startswith("scene_1_clean"):
                        video_file = os.path.join(root, file)
                        fallback_found = True
                        break
                if fallback_found:
                    break
                    
        print(f"Loading video: {video_file} for Scene {scene_id} (Target: {target_duration}s)...")
        base_clip = VideoFileClip(video_file)
        
        # Scale video speed to exactly match target_duration
        v_speed_factor = base_clip.duration / target_duration
        base_clip = base_clip.with_effects([fx.MultiplySpeed(v_speed_factor)]).with_audio(audio_clip)
        
        img_width, img_height = base_clip.size
        
        # 3. Apply Subtitle
        wrapped_text = wrap_text(scene_cfg["text"], max_chars=sub_style.get("max_chars_per_line", 35))
        
        # Create subtitle text clip
        font_size = sub_style.get("font_size", 26)
        color = sub_style.get("color", "white")
        stroke_color = sub_style.get("stroke_color", "black")
        stroke_width = sub_style.get("stroke_width", 2)
        margin_bottom = sub_style.get("margin_bottom", 230)
        
        txt_clip = TextClip(
            text=wrapped_text,
            font=r"C:\Windows\Fonts\malgun.ttf",
            font_size=font_size,
            color=color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            method="caption",
            size=(img_width - 100, 200)
        )
        
        # Positioning
        y_pos = img_height - margin_bottom
        txt_clip = txt_clip.with_position(("center", y_pos)).with_duration(target_duration)
        
        # Combine
        scene_clip = CompositeVideoClip([base_clip, txt_clip])
        scene_clip = scene_clip.with_effects([fx.CrossFadeIn(0.5)])
        
        clips.append(scene_clip)
        print(f"Prepared Scene {scene_id} - Duration: {target_duration}s")
        
    print("Concatenating all cloned scenes...")
    final_video = concatenate_videoclips(clips, method="compose")
    
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )
    
    print(f"SUCCESS: Cloned video rendered at {output_path}")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create cloned video using style profile.")
    parser.add_argument("--profile", default="reference_profile.json", help="Path to style profile JSON")
    parser.add_argument("--scenario", default=None, help="Path to scenario txt file (optional)")
    parser.add_argument("--output", default="cloned_video.mp4", help="Path to output video mp4")
    args = parser.parse_args()
    
    make_cloned_video(profile_path=args.profile, output_path=args.output, scenario_path=args.scenario)
