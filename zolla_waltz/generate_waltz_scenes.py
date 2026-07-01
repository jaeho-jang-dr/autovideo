# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import re
import cv2
import traceback
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)
os.chdir(ROOT)

import autoveo_flow as af

# Force UTF-8 stdout
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCENARIO_FILE = os.path.join(ROOT, "zolla_waltz", "scenario.txt")
WALTZ_DIR = os.path.join(ROOT, "zolla_waltz")
PROGRESS_FILE = os.path.join(WALTZ_DIR, "progress_scenes.json")

def extract_last_frame(video_path, output_path):
    """Extracts the last frame of a video using OpenCV and saves as PNG."""
    if not os.path.exists(video_path):
        print(f"[ERR] Video file not found for frame extraction: {video_path}")
        return False
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERR] Cannot open video: {video_path}")
        return False
        
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    success = False
    frame = None
    target_idx = frame_count - 1
    
    while target_idx >= 0 and not success:
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_idx)
        ret, temp_frame = cap.read()
        if ret and temp_frame is not None:
            frame = temp_frame
            success = True
            break
        target_idx -= 1
        
    cap.release()
    
    if not success or frame is None:
        print(f"[ERR] Failed to extract last frame from {video_path}")
        return False
        
    cv2.imwrite(output_path, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 1])
    print(f"[FRAME-EXTRACTED] Last frame of {os.path.basename(video_path)} -> {os.path.basename(output_path)}")
    return True

def parse_scenario():
    scenes = {}
    pattern = re.compile(r"\[Scene\s+(\d+)\]\s+(.*)", re.IGNORECASE)
    with open(SCENARIO_FILE, "r", encoding="utf-8") as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                scenes[int(m.group(1))] = m.group(2).strip()
    return scenes

class BrowserWrapper:
    def __init__(self, obj, is_cdp):
        self.obj = obj
        self.is_cdp = is_cdp
    def close(self):
        if self.is_cdp:
            try:
                self.obj.disconnect()
            except Exception as e:
                print(f"[CDP] disconnect error: {e}")
        else:
            try:
                self.obj.close()
            except Exception as e:
                print(f"[BROWSER] close error: {e}")

def setup_file_logging():
    log_file_path = os.path.join(WALTZ_DIR, "generate_scenes.log")
    try:
        log_file = open(log_file_path, "w", encoding="utf-8", buffering=1)
        sys.stdout = log_file
        sys.stderr = log_file
    except Exception as e:
        print(f"Failed to setup file logging: {e}")

def main():
    # Setup file logging
    setup_file_logging()
    
    # Set OUT_DIR inside autoveo_flow module so it saves there
    af.OUT_DIR = WALTZ_DIR
    os.makedirs(WALTZ_DIR, exist_ok=True)
    
    scenes = parse_scenario()
    print(f"Loaded {len(scenes)} scenes from scenario.txt")
    
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                progress = json.load(f)
            print(f"Loaded progress: {len(progress)} scenes recorded.")
        except Exception as e:
            print(f"Progress load error: {e}")
            
    todo = sorted(scenes.keys())
    
    with sync_playwright() as p:
        def launch_browser():
            import urllib.request
            try:
                urllib.request.urlopen("http://localhost:9222/json", timeout=2)
                print("  [CDP] localhost:9222 active. Connecting...")
                c = p.chromium.connect_over_cdp("http://localhost:9222")
                pg = c.contexts[0].pages[0] if c.contexts and c.contexts[0].pages else c.new_page()
                return BrowserWrapper(c, True), pg
            except Exception:
                print("  [CDP] localhost:9222 inactive. Starting fresh browser context...")
                c = p.chromium.launch_persistent_context(
                    af.PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
                    accept_downloads=True, downloads_path=af.DL_DIR,
                    ignore_default_args=["--enable-automation"],
                    args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                          "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
                pg = c.pages[0] if c.pages else c.new_page()
                return BrowserWrapper(c, False), pg

        ctx, page = launch_browser()
        idx = 0
        attempts = {}
        while idx < len(todo):
            n = todo[idx]
            out_path = os.path.join(WALTZ_DIR, f"scene_{n}.mp4")
            
            # Idempotence check
            if progress.get(str(n)) == "success" and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                print(f"[SKIP] Scene {n} already exists and succeeded.")
                # Verify that last frame is extracted for next scene if needed
                next_ref = os.path.join(WALTZ_DIR, f"scene_{n}_last.png")
                if n < len(todo) and not os.path.exists(next_ref):
                    extract_last_frame(out_path, next_ref)
                idx += 1
                continue
                
            # Determine reference image
            if n == 1:
                ref_img = os.path.join(ROOT, "home_vocab", "zolla_handshake.png")
            else:
                ref_img = os.path.join(WALTZ_DIR, f"scene_{n-1}_last.png")
                # Make sure previous scene last frame is extracted
                if not os.path.exists(ref_img):
                    prev_video = os.path.join(WALTZ_DIR, f"scene_{n-1}.mp4")
                    if not extract_last_frame(prev_video, ref_img):
                        print(f"[ERR] Cannot extract last frame of scene {n-1}. Retrying previous scene...")
                        idx = max(0, idx - 1)
                        continue
            
            print(f"\n[{n}/{len(todo)}] Generating Scene {n}...")
            print(f"  Reference image: {os.path.basename(ref_img)}")
            print(f"  Prompt: {scenes[n][:90]}...")
            
            try:
                try:
                    success = af.make_scene_upload(page, n, ref_img, scenes[n])
                    
                    if success:
                        progress[str(n)] = "success"
                        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                            json.dump(progress, f, indent=2, ensure_ascii=False)
                        # Extract last frame for the next scene
                        next_ref = os.path.join(WALTZ_DIR, f"scene_{n}_last.png")
                        extract_last_frame(out_path, next_ref)
                        idx += 1
                    else:
                        print(f"[FAIL] Scene {n} generation failed. Retrying same scene...")
                        attempts[n] = attempts.get(n, 0) + 1
                        if attempts[n] >= 3:
                            attempts[n] = 0
                            raise af.BrowserRebootException(f"3 consecutive failures on scene {n}")
                        time.sleep(3)
                except Exception as e:
                    if isinstance(e, af.BrowserRebootException):
                        raise e
                    print(f"[ERR] General error in Scene {n}: {e}")
                    traceback.print_exc()
                    af.shot(page, f"s{n}_error")
                    progress[str(n)] = "fail"
                    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                        json.dump(progress, f, indent=2, ensure_ascii=False)
                    attempts[n] = attempts.get(n, 0) + 1
                    if attempts[n] >= 3:
                        attempts[n] = 0
                        raise af.BrowserRebootException(f"3 consecutive failures on scene {n} (via general error)")
                    idx += 1
            except af.BrowserRebootException as re_err:
                print(f"[REBOOT] Browser reboot requested: {re_err}. Closing chrome, waiting 5s...")
                try:
                    ctx.close()
                except Exception:
                    pass
                af.force_kill_profile_chrome()
                time.sleep(5)
                ctx, page = launch_browser()
                
        print("\nAll waltz scenes generated successfully!")
        try:
            ctx.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
