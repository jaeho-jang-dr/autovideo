import os
import sys
import json
import glob
import shutil
import subprocess
import pyJianYingDraft as draft

def find_draft_directory():
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\antigravity")
    return os.path.join(user_profile, r"AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")

def find_recent_template_folder(draft_dir):
    """
    Finds the native draft folder '0618' or most recently modified native draft.
    """
    folders = glob.glob(os.path.join(draft_dir, "*"))
    valid_folders = []
    for f in folders:
        if os.path.isdir(f):
            basename = os.path.basename(f)
            # Skip recycle bin and output folders
            if basename in [".recycle_bin", "Autovideo_POC_Test", "Line_Craft_Test"]:
                continue
            # Ensure it contains draft_content.json (a real project)
            if os.path.exists(os.path.join(f, "draft_content.json")):
                valid_folders.append(f)
                
    if not valid_folders:
        return None
        
    # Prefer folder named '0618' if it exists
    for f in valid_folders:
        if os.path.basename(f) == "0618":
            return f
            
    # Fallback to most recently modified
    valid_folders.sort(key=os.path.getmtime, reverse=True)
    return valid_folders[0]

def update_root_meta_info(draft_dir, project_name, project_path, draft_id):
    """
    Registers the project under root_meta_info.json so CapCut UI displays it.
    """
    root_meta_path = os.path.join(draft_dir, "root_meta_info.json")
    if not os.path.exists(root_meta_path):
        print("[Warning] root_meta_info.json not found in draft root.")
        return
        
    try:
        with open(root_meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        store = data.get("all_draft_store", [])
        
        # Check if project entry already exists
        exists_idx = -1
        for i, item in enumerate(store):
            if item.get("draft_name") == project_name:
                exists_idx = i
                break
                
        new_entry = {
            "cloud_draft_cover": False,
            "cloud_draft_sync": False,
            "draft_cloud_last_action_download": False,
            "draft_cloud_purchase_info": "",
            "draft_cloud_template_id": "",
            "draft_cloud_tutorial_info": "",
            "draft_cloud_videocut_purchase_info": "",
            "draft_cover": f"{project_path.replace(os.sep, '/')}/draft_cover.jpg",
            "draft_fold_path": project_path.replace(os.sep, "/"),
            "draft_id": draft_id,
            "draft_is_ai_shorts": False,
            "draft_is_cloud_temp_draft": False,
            "draft_is_invisible": False,
            "draft_is_web_article_video": False,
            "draft_json_file": f"{project_path.replace(os.sep, '/')}/draft_content.json",
            "draft_name": project_name,
            "draft_new_version": "",
            "draft_root_path": draft_dir,
            "draft_timeline_materials_size": 4084,
            "draft_type": "",
            "draft_web_article_video_enter_from": "",
            "streaming_edit_draft_ready": True,
            "tm_draft_cloud_completed": "",
            "tm_draft_cloud_entry_id": -1,
            "tm_draft_cloud_modified": 0,
            "tm_draft_cloud_parent_entry_id": -1,
            "tm_draft_cloud_space_id": -1,
            "tm_draft_cloud_user_id": -1,
            "tm_draft_create": 1781744155276696,
            "tm_draft_modified": 1781744168977254,
            "tm_draft_removed": 0,
            "tm_duration": 16000000 # 16 seconds in microseconds
        }
        
        if exists_idx != -1:
            store[exists_idx] = new_entry
            print(f"[Info] Updated existing entry for '{project_name}' in root_meta_info.json")
        else:
            store.append(new_entry)
            print(f"[Info] Added new entry for '{project_name}' to root_meta_info.json")
            
        data["all_draft_store"] = store
        
        with open(root_meta_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            
    except Exception as e:
        print(f"[Error] Failed to update root_meta_info.json: {e}")

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        
    print("="*60)
    print(" Compiling CapCut 8.7+ Project for 2D Line Craft Video")
    print("="*60)

    draft_dir = find_draft_directory()
    if not os.path.exists(draft_dir):
        print(f"[Error] CapCut draft folder does not exist at: {draft_dir}")
        return

    # 1. Locate template folder
    template_folder = find_recent_template_folder(draft_dir)
    if not template_folder:
        print("[Error] No recent native CapCut project found to clone as template.")
        return
        
    print(f"[Info] Using template folder: {template_folder}")

    # 2. Setup output folder
    target_project_name = "Line_Craft_Test"
    target_folder = os.path.join(draft_dir, target_project_name)
    
    # 3. Clone template shell
    try:
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder)
        os.makedirs(target_folder, exist_ok=True)
        
        for item in os.listdir(template_folder):
            s = os.path.join(template_folder, item)
            d = os.path.join(target_folder, item)
            if item == "draft_content.json":
                continue
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
                
        print("[Info] Successfully cloned native project shell.")
    except Exception as e:
        print(f"[Error] Failed to clone template: {e}")
        return

    # 4. Resolve absolute paths of assets
    v_path_1 = os.path.abspath("line_craft/scene_1.mp4")
    v_path_2 = os.path.abspath("line_craft/scene_2.mp4")
    
    tts_path_1 = os.path.abspath("scratch/line_craft_assets/tts_1.mp3")
    tts_path_2 = os.path.abspath("scratch/line_craft_assets/tts_2.mp3")
    
    sfx_path = os.path.abspath("assets/audio/whoosh.wav")

    # Confirm assets exist
    for p in [v_path_1, v_path_2, tts_path_1, tts_path_2, sfx_path]:
        if not os.path.exists(p):
            print(f"[Error] Required asset does not exist: {p}")
            return

    # Initialize pyJianYingDraft
    draft_folder = draft.DraftFolder(draft_dir)
    
    try:
        # Create draft to generate draft_content.json
        project = draft_folder.create_draft(target_project_name, width=1920, height=1080, fps=30, allow_replace=True)
        
        # Add materials
        v_mat_1 = draft.VideoMaterial(v_path_1)
        v_mat_2 = draft.VideoMaterial(v_path_2)
        
        tts_mat_1 = draft.AudioMaterial(tts_path_1)
        tts_mat_2 = draft.AudioMaterial(tts_path_2)
        
        sfx_mat = draft.AudioMaterial(sfx_path)
        
        project.add_material(v_mat_1)
        project.add_material(v_mat_2)
        project.add_material(tts_mat_1)
        project.add_material(tts_mat_2)
        project.add_material(sfx_mat)
        
        # Add tracks
        project.add_track(draft.TrackType.video)
        project.add_track(draft.TrackType.audio, track_name="TTS")
        project.add_track(draft.TrackType.text)
        project.add_track(draft.TrackType.audio, track_name="SFX")
        
        # Timeline Segment setup (SEC = 1,000,000 microseconds)
        # 1. Videos (scale=1.25, duration=8s each)
        clip_sett = draft.ClipSettings(scale_x=1.25, scale_y=1.25)
        
        v_seg_1 = draft.VideoSegment(v_mat_1, draft.Timerange(0, 8 * draft.SEC), clip_settings=clip_sett)
        v_seg_2 = draft.VideoSegment(v_mat_2, draft.Timerange(8 * draft.SEC, 8 * draft.SEC), clip_settings=clip_sett)
        
        project.add_segment(v_seg_1)
        project.add_segment(v_seg_2)
        
        # 2. TTS Narration
        # tts_1: 2s -> 6s (duration 4s)
        # tts_2: 10s -> 14s (duration 4s)
        tts_seg_1 = draft.AudioSegment(tts_mat_1, draft.Timerange(2 * draft.SEC, 4 * draft.SEC))
        tts_seg_2 = draft.AudioSegment(tts_mat_2, draft.Timerange(10 * draft.SEC, 4 * draft.SEC))
        
        project.add_segment(tts_seg_1, track_name="TTS")
        project.add_segment(tts_seg_2, track_name="TTS")
        
        # 3. Subtitles aligned with TTS
        txt_style = draft.TextStyle(size=12.0, color=(1.0, 1.0, 1.0), bold=True)
        txt_border = draft.TextBorder(color=(0.0, 0.0, 0.0), width=8.0)
        
        sub_text_1 = "미래의 자동차가 칠판 위에 한 땀 한 땀 아름다운 선으로 그려지고 있습니다."
        sub_text_2 = "정밀한 기계 부품과 톱니바퀴들이 유기적으로 맞물려 움직이기 시작합니다."
        
        txt_seg_1 = draft.TextSegment(sub_text_1, draft.Timerange(2 * draft.SEC, 4 * draft.SEC), font=draft.FontType.고딕, style=txt_style, border=txt_border)
        txt_seg_2 = draft.TextSegment(sub_text_2, draft.Timerange(10 * draft.SEC, 4 * draft.SEC), font=draft.FontType.고딕, style=txt_style, border=txt_border)
        
        project.add_segment(txt_seg_1)
        project.add_segment(txt_seg_2)
        
        # 4. SFX Transition (whoosh.wav) at 8 seconds mark (duration 0.6s)
        sfx_seg = draft.AudioSegment(sfx_mat, draft.Timerange(int(7.5 * draft.SEC), int(0.6 * draft.SEC)))
        project.add_segment(sfx_seg, track_name="SFX")
        
        project.save()
        print("[Info] Generated draft_content.json successfully.")
        
    except Exception as e:
        print(f"[Error] Failed to build timeline: {e}")
        import traceback
        traceback.print_exc()
        return

    # 5. Fix up draft_meta_info.json in the target project folder
    target_meta_path = os.path.join(target_folder, "draft_meta_info.json")
    draft_id = ""
    try:
        with open(target_meta_path, "r", encoding="utf-8") as f:
            meta_data = json.load(f)
            
        draft_id = meta_data.get("draft_id", "Line_Craft_Test_ID")
        meta_data["draft_name"] = target_project_name
        meta_data["draft_fold_path"] = target_folder.replace(os.sep, "/")
        
        with open(target_meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False)
            
        print("[Info] Successfully aligned draft_meta_info.json.")
    except Exception as e:
        print(f"[Error] Failed to update draft_meta_info.json: {e}")
        return

    # 6. Update global index (root_meta_info.json)
    update_root_meta_info(draft_dir, target_project_name, target_folder, draft_id)
    print("[Success] Project fully registered inside CapCut!")

    # 7. Launch CapCut Desktop
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\antigravity")
    apps_dir = os.path.join(user_profile, r"AppData\Local\CapCut\Apps")
    version_exe = None
    if os.path.exists(apps_dir):
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            if os.path.isdir(item_path) and item[0].isdigit():
                v_exe = os.path.join(item_path, "CapCut.exe")
                if os.path.exists(v_exe):
                    version_exe = v_exe
                    break
                    
    target_exe = version_exe if version_exe else os.path.join(apps_dir, "CapCut.exe")
    if os.path.exists(target_exe):
        print(f"[Info] Launching CapCut Desktop...")
        work_dir = os.path.dirname(target_exe)
        cmd = f"powershell -Command \"Start-Process '{target_exe}' -WorkingDirectory '{work_dir}'\""
        subprocess.run(cmd, shell=True)
        print("[Success] CapCut started successfully!")
    else:
        print("[Warning] CapCut.exe not found.")

if __name__ == '__main__':
    main()
