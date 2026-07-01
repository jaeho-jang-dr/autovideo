import os
import sys
import json
import glob
import shutil
import subprocess
from gtts import gTTS
import pyJianYingDraft as draft

def find_draft_directory():
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\antigravity")
    return os.path.join(user_profile, r"AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")

def find_recent_template_folder(draft_dir):
    """
    Finds the most recently created standard CapCut project folder (excluding our POC test folder).
    """
    folders = glob.glob(os.path.join(draft_dir, "*"))
    valid_folders = []
    for f in folders:
        if os.path.isdir(f):
            basename = os.path.basename(f)
            # Skip recycle bin, mock drafts, and our POC test folder
            if basename in [".recycle_bin", "Autovideo_POC_Test"]:
                continue
            # Ensure it contains draft_content.json (a real project)
            if os.path.exists(os.path.join(f, "draft_content.json")):
                valid_folders.append(f)
                
    if not valid_folders:
        return None
        
    # Sort by modification time (most recent first)
    valid_folders.sort(key=os.path.getmtime, reverse=True)
    return valid_folders[0]

def update_root_meta_info(draft_dir, project_name, project_path, draft_id):
    """
    Registers the project under root_meta_info.json so CapCut UI can show it.
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
                
        # Create new entry dictionary using standard CapCut format
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
            "tm_duration": 0
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
    print(" CapCut 8.7+ Compatible Draft Generator")
    print("="*60)

    draft_dir = find_draft_directory()
    if not os.path.exists(draft_dir):
        print(f"[Error] CapCut draft folder does not exist at: {draft_dir}")
        return

    # 1. Locate the native template folder created by user/CapCut
    template_folder = find_recent_template_folder(draft_dir)
    if not template_folder:
        print("[Error] No recent native CapCut project found to clone as template.")
        print("        Please open CapCut PC, click '[+ New Project]' once, then close it.")
        return
        
    print(f"[Info] Using native CapCut 8.7 template folder: {template_folder}")

    # 2. Setup output folder
    target_project_name = "Autovideo_POC_Test"
    target_folder = os.path.join(draft_dir, target_project_name)
    
    # 3. Clone all metadata files from template to target to satisfy 8.7 signature checks
    try:
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder)
        os.makedirs(target_folder, exist_ok=True)
        
        # Copy everything except draft_content.json (which we will rebuild)
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
        print(f"[Error] Failed to clone native project shell: {e}")
        return

    # 4. Generate the pyJianYingDraft logic
    # Select video (test_merged.mp4)
    video_path = os.path.abspath("test_merged.mp4")
    if not os.path.exists(video_path):
        print("[Error] test_merged.mp4 not found in root.")
        return
        
    # Generate mock TTS
    temp_tts_path = os.path.abspath("scratch/temp_poc_tts.mp3")
    os.makedirs(os.path.dirname(temp_tts_path), exist_ok=True)
    tts = gTTS(text="캡컷 최신 버전 자동화 검증을 시작합니다. 타임라인이 안전하게 렌더링되는지 확인하십시오.", lang="ko")
    tts.save(temp_tts_path)
    
    # Find sound effect
    sfx_path = os.path.abspath("assets/intro_audio.wav")
    if not os.path.exists(sfx_path):
        sfx_path = temp_tts_path

    # Initialize pyJianYingDraft (using target folder path directly)
    draft_folder = draft.DraftFolder(draft_dir)
    
    try:
        # Re-create draft project to generate the draft_content.json file
        project = draft_folder.create_draft(target_project_name, width=1920, height=1080, fps=30, allow_replace=True)
        
        v_material = draft.VideoMaterial(video_path)
        a_material = draft.AudioMaterial(temp_tts_path)
        sfx_material = draft.AudioMaterial(sfx_path)
        
        project.add_material(v_material)
        project.add_material(a_material)
        project.add_material(sfx_material)
        
        project.add_track(draft.TrackType.video)
        project.add_track(draft.TrackType.audio, track_name="TTS")
        project.add_track(draft.TrackType.text)
        project.add_track(draft.TrackType.audio, track_name="SFX")
        
        total_duration = 12 * draft.SEC
        
        # A. Video (with 1.25x scaling)
        clip_sett = draft.ClipSettings(scale_x=1.25, scale_y=1.25)
        v_seg = draft.VideoSegment(v_material, draft.Timerange(0, total_duration), clip_settings=clip_sett)
        project.add_segment(v_seg)
        
        # B. TTS Narration
        a_seg = draft.AudioSegment(a_material, draft.Timerange(2 * draft.SEC, 6 * draft.SEC))
        project.add_segment(a_seg, track_name="TTS")
        
        # C. Stylized text
        txt_style = draft.TextStyle(size=12.0, color=(1.0, 1.0, 1.0), bold=True)
        txt_border = draft.TextBorder(color=(0.0, 0.0, 0.0), width=8.0)
        txt_seg = draft.TextSegment("8.7 최신 버전 우회 자막 자동화", draft.Timerange(2 * draft.SEC, 6 * draft.SEC), font=draft.FontType.고딕, style=txt_style, border=txt_border)
        project.add_segment(txt_seg)
        
        # D. Sound Effect Pop
        sfx_seg = draft.AudioSegment(sfx_material, draft.Timerange(int(0.5 * draft.SEC), 1 * draft.SEC))
        project.add_segment(sfx_seg, track_name="SFX")
        
        project.save()
        print("[Info] Generated updated draft_content.json")
    except Exception as e:
        print(f"[Error] Failed to generate timeline using pyJianYingDraft: {e}")
        return

    # 5. Fix up draft_meta_info.json in the target project folder
    target_meta_path = os.path.join(target_folder, "draft_meta_info.json")
    draft_id = ""
    try:
        with open(target_meta_path, "r", encoding="utf-8") as f:
            meta_data = json.load(f)
            
        draft_id = meta_data.get("draft_id", "Autovideo_POC_Test_ID")
        # Update fields to match target name and path
        meta_data["draft_name"] = target_project_name
        meta_data["draft_fold_path"] = target_folder.replace(os.sep, "/")
        
        with open(target_meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False)
            
        print("[Info] Successfully aligned target draft_meta_info.json fields.")
    except Exception as e:
        print(f"[Error] Failed to update target draft_meta_info.json: {e}")
        return

    # 6. Update the global index (root_meta_info.json)
    update_root_meta_info(draft_dir, target_project_name, target_folder, draft_id)

    # 7. Launch CapCut Desktop (Version specific)
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
        print(f"[Info] Launching CapCut Desktop via PowerShell...")
        work_dir = os.path.dirname(target_exe)
        cmd = f"powershell -Command \"Start-Process '{target_exe}' -WorkingDirectory '{work_dir}'\""
        subprocess.run(cmd, shell=True)
        print("[Success] Launch command successfully executed!")
    else:
        print("[Warning] Could not locate CapCut.exe launcher.")

if __name__ == '__main__':
    main()
