import os
import asyncio
import edge_tts
from moviepy import (
    AudioFileClip, concatenate_audioclips, concatenate_videoclips,
    CompositeVideoClip, ImageClip
)
from whiteboard_animator import (
    create_whiteboard_background, create_door_clip,
    create_moving_stickman_clip, create_writing_chalkboard_clip
)

# 1. Edge-TTS Audio Generator
async def generate_audio_assets():
    print("Synthesizing Edge-TTS voices...")
    os.makedirs("scratch", exist_ok=True)
    
    # Scene 1 script (English)
    scene_1_text = "Hello learners! Welcome to K Lingo Journey. Today, let's explore Hangeul, the scientific alphabet."
    communicate_1 = edge_tts.Communicate(scene_1_text, "en-US-EmmaMultilingualNeural")
    await communicate_1.save("scratch/scene_1_audio.mp3")
    
    # Scene 2 script (Korean/English mix)
    scene_2_text = "Look at this blackboard. Let's write the first letter: 기역! G, G, G."
    communicate_2 = edge_tts.Communicate(scene_2_text, "en-US-EmmaMultilingualNeural")
    await communicate_2.save("scratch/scene_2_audio.mp3")
    
    print("TTS synthesis completed.")

def compile_video():
    print("Compiling Whiteboard/Line-Art video...")
    
    # Load audio clips to measure exact durations
    audio_1 = AudioFileClip("scratch/scene_1_audio.mp3")
    audio_2 = AudioFileClip("scratch/scene_2_audio.mp3")
    
    dur_1 = audio_1.duration
    dur_2 = audio_2.duration
    
    print(f"Scene 1 duration: {dur_1:.2f}s, Scene 2 duration: {dur_2:.2f}s")
    
    # ─── SCENE 1: Intro (Door open, Stickman enters classroom) ───
    bg_1 = create_whiteboard_background(dur_1)
    
    # Door clip (opens 1.0 seconds in)
    door = create_door_clip(dur_1, 1.0, 
                            "assets/graphics/obj_door_closed.png", 
                            "assets/graphics/obj_door_open.png", 
                            pos=(950, 200))
    
    # Blackboard in classroom (static background object)
    blackboard = (ImageClip("assets/graphics/obj_blackboard.png")
                  .with_duration(dur_1)
                  .with_position((150, 80)))
                  
    # Stickman walks in from the left (t=1.5s to end)
    stickman = create_moving_stickman_clip(
        dur_1 - 1.5, 
        "assets/graphics/stickman_standing.png",
        start_x=-200, end_x=450, y=300,
        fade_in_dur=0.5, fade_out_dur=0.0
    ).with_start(1.5)
    
    scene_1_video = CompositeVideoClip([bg_1, door, blackboard, stickman], size=(1280, 720))
    scene_1_video = scene_1_video.with_audio(audio_1)
    
    # ─── SCENE 2: Hangeul Writing (Drawing 'ㄱ' with pencil) ───
    bg_2 = create_whiteboard_background(dur_2)
    
    # Blackboard remains static
    blackboard_2 = (ImageClip("assets/graphics/obj_blackboard.png")
                    .with_duration(dur_2)
                    .with_position((150, 80)))
                    
    # Stickman stands pointing at blackboard
    stickman_2 = (ImageClip("assets/graphics/stickman_standing.png")
                  .with_duration(dur_2)
                  .with_position((450, 300)))
                  
    # Writing 'ㄱ' on the blackboard
    # Blackboard center is roughly (150+w/2, 80+h/2). Letter size is 256x256.
    # Put it at (350, 160) inside the blackboard.
    writing = create_writing_chalkboard_clip(
        "assets/graphics/letters/letter_ㄱ.png",
        dur_2,
        "assets/graphics/obj_pencil.png",
        start_pos=(350, 160)
    )
    
    scene_2_video = CompositeVideoClip([bg_2, blackboard_2, stickman_2, writing], size=(1280, 720))
    scene_2_video = scene_2_video.with_audio(audio_2)
    
    # ─── CONCATENATE ALL SCENES ───
    final_video = concatenate_videoclips([scene_1_video, scene_2_video])
    
    # Ensure assets/video output directory exists
    os.makedirs("assets/video", exist_ok=True)
    output_path = "assets/video/korean_school_guide.mp4"
    
    # Render final MP4 using maximum CPU threads
    import os as os_sys
    threads = os_sys.cpu_count() or 4
    
    print(f"Rendering final MP4 to {output_path} with {threads} CPU threads...")
    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=threads,
        logger="bar"
    )
    print("Video rendering successfully finished.")

if __name__ == "__main__":
    # Run async TTS first
    asyncio.run(generate_audio_assets())
    # Compile video
    compile_video()
