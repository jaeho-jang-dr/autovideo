import os
import sys
import glob
from gtts import gTTS
import pyJianYingDraft as draft

def find_draft_directory():
    """
    Finds the default CapCut/Jianying draft directory path on Windows.
    """
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\Default")
    
    # Standard installation paths for CapCut (Global) and Jianying (Chinese)
    paths_to_try = [
        os.path.join(user_profile, r"AppData\Local\CapCut\User Data\Projects\com.lveditor.draft"),
        os.path.join(user_profile, r"AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft"),
        os.path.join(os.getcwd(), "scratch", "mock_drafts")
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            print(f"[Info] Found CapCut draft directory: {path}")
            return path
            
    # Fallback to local mock directory
    fallback_path = paths_to_try[-1]
    os.makedirs(fallback_path, exist_ok=True)
    print(f"[Warning] CapCut draft directory not found in AppData. Using fallback local path: {fallback_path}")
    return fallback_path

def main():
    # Configure console output for UTF-8 (prevents encoding errors with Chinese/Korean chars)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        
    print("="*60)
    print(" CapCut/Jianying Automation POC: Generating Test Project")
    print("="*60)

    # 1. Determine draft directory
    draft_dir = find_draft_directory()

    # 2. Select Video Asset (test_merged.mp4 or other mp4)
    video_path = None
    if os.path.exists("test_merged.mp4"):
        video_path = os.path.abspath("test_merged.mp4")
    else:
        mp4_files = glob.glob("*.mp4")
        if mp4_files:
            video_path = os.path.abspath(mp4_files[0])
            
    if not video_path:
        print("[Error] No MP4 files found in the workspace root folder.")
        print("        Please make sure a test video like 'test_merged.mp4' exists in the workspace.")
        return
    
    print(f"[Info] Selected video source: {video_path}")

    # 3. Create dummy TTS Audio via gTTS
    temp_tts_path = os.path.abspath("scratch/temp_poc_tts.mp3")
    os.makedirs(os.path.dirname(temp_tts_path), exist_ok=True)
    
    try:
        tts = gTTS(text="캡컷 자동화 피오씨 테스트입니다. 타임라인에 비디오와 자막, 효과음이 정상 정렬되는지 확인하세요.", lang="ko")
        tts.save(temp_tts_path)
        print(f"[Info] Generated temporary TTS file: {temp_tts_path}")
    except Exception as e:
        print(f"[Warning] Failed to generate TTS via gTTS: {e}. Attempting to use existing MP3.")
        mp3_files = glob.glob("assets/**/*.mp3", recursive=True)
        if mp3_files:
            temp_tts_path = os.path.abspath(mp3_files[0])
            print(f"[Info] Fallback TTS path to: {temp_tts_path}")
        else:
            print("[Error] No MP3 audio source available.")
            return

    # 4. Search for a sound effect (SFX)
    sfx_path = None
    sfx_candidates = glob.glob("assets/**/*.wav", recursive=True) + glob.glob("assets/**/*.mp3", recursive=True)
    # Exclude the temporary file we just generated
    sfx_candidates = [f for f in sfx_candidates if "temp_poc_tts" not in f]
    
    if sfx_candidates:
        sfx_path = os.path.abspath(sfx_candidates[0])
        print(f"[Info] Selected sound effect (SFX): {sfx_path}")
    else:
        # Use TTS file as fallback for SFX
        sfx_path = temp_tts_path
        print(f"[Warning] No audio assets found in assets/. Using TTS as SFX placeholder: {sfx_path}")

    # 5. Initialize CapCut Draft Folder and Project
    draft_folder = draft.DraftFolder(draft_dir)
    draft_name = "Autovideo_POC_Test"
    
    # Create project: 1920x1080 resolution, 30 fps
    try:
        project = draft_folder.create_draft(draft_name, width=1920, height=1080, fps=30, allow_replace=True)
        print(f"[Info] Created draft project: '{draft_name}'")
    except Exception as e:
        print(f"[Error] Failed to create draft folder in CapCut directory: {e}")
        return

    # 6. Add Materials to Project Assets
    try:
        v_material = draft.VideoMaterial(video_path)
        a_material = draft.AudioMaterial(temp_tts_path)
        sfx_material = draft.AudioMaterial(sfx_path)
        
        project.add_material(v_material)
        project.add_material(a_material)
        project.add_material(sfx_material)
        print("[Info] Successfully registered materials to the project.")
    except Exception as e:
        print(f"[Error] Failed to register materials: {e}")
        return

    # 7. Add Clips to Timelines (Segments)
    # Define time constants (SEC = 1,000,000 microseconds)
    # Target length: 12 seconds
    total_duration = 12 * draft.SEC
    
    try:
        # Create Tracks first
        project.add_track(draft.TrackType.video)
        project.add_track(draft.TrackType.audio, track_name="TTS")
        project.add_track(draft.TrackType.text)
        project.add_track(draft.TrackType.audio, track_name="SFX")
        print("[Info] Successfully created timeline tracks (video, TTS audio, text, SFX audio).")

        # A. Video Segment (0s -> 12s)
        # Apply 1.25x scaling zoom to simulate watermark crop
        clip_sett = draft.ClipSettings(scale_x=1.25, scale_y=1.25)
        v_seg = draft.VideoSegment(
            v_material, 
            draft.Timerange(0, total_duration), 
            clip_settings=clip_sett
        )
        project.add_segment(v_seg)
        print("[Info] Added Video Segment (0s -> 12s) with 1.25x scaling.")

        # B. Narration TTS (2s -> 8s)
        a_seg = draft.AudioSegment(
            a_material, 
            draft.Timerange(2 * draft.SEC, 6 * draft.SEC) # Duration: 6 seconds
        )
        project.add_segment(a_seg, track_name="TTS")
        print("[Info] Added TTS Narration Segment (2s -> 8s).")

        # C. Stylized Korean Subtitle (2s -> 8s, aligned with TTS)
        txt_style = draft.TextStyle(size=12.0, color=(1.0, 1.0, 1.0), bold=True)
        txt_border = draft.TextBorder(color=(0.0, 0.0, 0.0), width=8.0)
        
        # Position can be controlled via ClipSettings inside TextSegment
        # We put malgun gothic font (FontType.고딕)
        txt_seg = draft.TextSegment(
            "자동 배치된 캡컷 자막 피오씨",
            draft.Timerange(2 * draft.SEC, 6 * draft.SEC),
            font=draft.FontType.고딕,
            style=txt_style,
            border=txt_border
        )
        project.add_segment(txt_seg)
        print("[Info] Added Stylized Korean Subtitle (2s -> 8s).")

        # D. Sound Effect (SFX) Pop (0.5s -> 1.5s, starts near beginning)
        sfx_seg = draft.AudioSegment(
            sfx_material,
            draft.Timerange(int(0.5 * draft.SEC), 1 * draft.SEC) # Duration: 1 second
        )
        project.add_segment(sfx_seg, track_name="SFX")
        print("[Info] Added Sound Effect Pop Segment (0.5s -> 1.5s).")

    except Exception as e:
        print(f"[Error] Failed to build timeline segments: {e}")
        import traceback
        traceback.print_exc()
        return

    # 8. Save Draft
    try:
        project.save()
        print("="*60)
        print("[Success] CapCut Draft successfully built and saved!")
        print(f"[Success] Path: {os.path.join(draft_dir, draft_name)}")
        print("="*60)
        print("\n>>> NEXT STEP FOR USER:")
        print("1. Open the CapCut PC / Jianying Desktop application.")
        print(f"2. Look for the project named '{draft_name}' in the Drafts list.")
        print("3. Double-click to open it and verify the timeline alignment, scale crop, and subtitles.")
        print("="*60)
    except Exception as e:
        print(f"[Error] Failed to save project files: {e}")

if __name__ == '__main__':
    main()
