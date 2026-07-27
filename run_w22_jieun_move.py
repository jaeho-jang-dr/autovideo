# -*- coding: utf-8 -*-
"""Generate 8-second 24fps Veo video directly via Google Flow without Nano Banana image pre-generation."""

import os
import sys
import shutil
import time
from playwright.sync_api import sync_playwright

import autoveo_flow as avf

REF_IMAGE = os.path.abspath(r"D:\Entertainments\DevEnvironment\autovideo\W22\jieun_spring_front.png")
OUT_MP4 = os.path.abspath(r"D:\Entertainments\DevEnvironment\autovideo\W22\clips\vid_jieun_move.mp4")
PROFILE = os.path.abspath(r"D:\Entertainments\DevEnvironment\autovideo\assets\chrome_profile")
DL_DIR = os.path.abspath(r"D:\Entertainments\DevEnvironment\autovideo\debug\downloads")

MOTION_PROMPT = (
    "Full body shot of the 2D cartoon anime girl from reference image Jieun (long soft wavy light brown hair, "
    "sky blue dress, light pink cardigan, white sneakers, cream skin, flat cartoon line art style with thick black outlines). "
    "The character dynamically moves her whole body continuously in smooth 24fps animation: turning around 360 degrees, "
    "crouching down, jumping up high with both feet off ground, walking forward, leaning to the side, turning her head "
    "to look around with wide curious eyes, blinking naturally, showing a surprised reaction with eyes widening, "
    "and expressive eyebrow and mouth movements. Full body is completely visible inside the frame at all times, "
    "fixed camera angle, solid pure white #ffffff background, no shadows, no ground shadow, no props, no background objects, "
    "no other characters, no text, no watermark, smooth 8-second continuous animation."
)

class BrowserWrapper:
    def __init__(self, obj, is_cdp):
        self.obj = obj
        self.is_cdp = is_cdp
    def close(self):
        if self.is_cdp:
            try:
                self.obj.disconnect()
                print("  [CDP] CDP connection disconnected.", flush=True)
            except Exception as e:
                print(f"  [CDP] disconnect error: {e}", flush=True)
        else:
            try:
                self.obj.close()
                print("  [BROWSER] Browser context closed.", flush=True)
            except Exception as e:
                print(f"  [BROWSER] close error: {e}", flush=True)

def set_video_mode(page, aspect="16:9"):
    """Exit Agent mode if needed, then select 동영상 (Veo) / aspect."""
    avf.log("  [MODE] Setting composer mode to 동영상 (Veo)...")
    if not page.evaluate(avf.HAS_CHIP_JS):
        avf.click_text(page, "에이전트")
        page.wait_for_timeout(900)
    for t in ("Nano Banana", "crop_16_9", "동영상", "이미지"):
        if avf.click_text(page, t):
            break
    page.wait_for_timeout(1200)
    if avf.click_text(page, "동영상") or avf.click_text(page, "Video"):
        avf.log("  [MODE] Clicked '동영상' tab ✔")
    page.wait_for_timeout(500)
    avf.click_text(page, aspect)
    page.wait_for_timeout(500)
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)

def attach_reference_image(page, image_path):
    """Attempt to attach reference image to composer prompt bar."""
    image_path = os.path.abspath(image_path)
    if not os.path.exists(image_path):
        return False
    avf.log(f"  [ATTACH] Attaching reference image: {image_path}")
    try:
        inputs = page.locator("input[type='file']")
        for i in range(inputs.count()):
            try:
                inputs.nth(i).set_input_files(image_path, timeout=3000)
                avf.log(f"  [ATTACH] Attached file to input[{i}] ✔")
                page.wait_for_timeout(1500)
                return True
            except Exception:
                pass
    except Exception as e:
        avf.log(f"  [ATTACH] Image attach warning: {e}")
    return False

def generate_direct_veo(page, out_mp4):
    avf.log("=== Direct Veo Video Generation ===")
    if not avf.open_new_project(page):
        avf.log("[ERR] Failed to open new project")
        return False
    avf.shot(page, "w22_direct_veo_00_editor")
    
    # 1. Switch model to 동영상 (Veo)
    set_video_mode(page, aspect="16:9")
    avf.shot(page, "w22_direct_veo_01_video_mode")
    
    # 2. Attach reference image if possible
    attach_reference_image(page, REF_IMAGE)
    page.wait_for_timeout(1000)
    
    # 3. Fill prompt and generate video
    avf.log("  [GENERATE] Submitting Veo video generation prompt...")
    if avf.make_video(page, out_mp4, MOTION_PROMPT, "w22_direct_veo"):
        avf.log(f"[OK] Direct Veo video created: {out_mp4}")
        avf.shot(page, "w22_direct_veo_02_done")
        return True
    return False

def main():
    print(f"=== Starting Veo Video Generation for Jieun Dynamic Movement ===", flush=True)
    print(f"Reference Image: {REF_IMAGE}", flush=True)
    print(f"Target Output Path: {OUT_MP4}", flush=True)
    
    if not os.path.exists(REF_IMAGE):
        raise FileNotFoundError(f"Reference image not found: {REF_IMAGE}")
        
    os.makedirs(os.path.dirname(OUT_MP4), exist_ok=True)
    os.makedirs(DL_DIR, exist_ok=True)
    
    avf.PROFILE = PROFILE
    avf.DL_DIR = DL_DIR
    avf.OUT_DIR = os.path.dirname(OUT_MP4)
    
    def launch_or_connect(p):
        import urllib.request
        try:
            urllib.request.urlopen("http://localhost:9222/json", timeout=2)
            print("  [CDP] Detected existing Chrome on localhost:9222! Connecting via CDP...", flush=True)
            c = p.chromium.connect_over_cdp("http://localhost:9222")
            if c.contexts:
                ctx = c.contexts[0]
                pg = ctx.pages[0] if ctx.pages else ctx.new_page()
            else:
                pg = c.new_page()
            return BrowserWrapper(c, True), pg
        except Exception as e:
            print(f"  [CDP] CDP connection not available ({e}). Launching new persistent context...", flush=True)
            avf.force_kill_profile_chrome(PROFILE)
            time.sleep(1)
            c = p.chromium.launch_persistent_context(
                PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
                accept_downloads=True, downloads_path=DL_DIR, slow_mo=150,
                ignore_default_args=["--enable-automation"],
                args=["--start-maximized", "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR", "--disable-gpu"]
            )
            pg = c.pages[0] if c.pages else c.new_page()
            return BrowserWrapper(c, False), pg

    with sync_playwright() as p:
        ctx, pg = launch_or_connect(p)
        
        # Remove existing file prior to generation to ensure we don't report stale success
        if os.path.exists(OUT_MP4):
            try:
                os.remove(OUT_MP4)
            except Exception:
                pass
                
        success = generate_direct_veo(pg, OUT_MP4)
        
        try:
            ctx.close()
        except Exception:
            pass
            
    if success and os.path.exists(OUT_MP4) and os.path.getsize(OUT_MP4) > 0:
        print(f"SUCCESS: Created Veo video at {OUT_MP4} ({os.path.getsize(OUT_MP4)} bytes)", flush=True)
    else:
        print("ERROR: Direct Veo video generation failed.", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
