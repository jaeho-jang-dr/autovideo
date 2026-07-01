import os
import sys
import time
from playwright.sync_api import sync_playwright

PROFILE = os.path.abspath("assets/chrome_profile")
BASE = "https://labs.google/fx/tools/flow"

print("Starting Google Flow Login Helper...", flush=True)
print("This script will open Chrome on your screen. Please complete Google Login if prompted.", flush=True)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        PROFILE,
        channel="chrome",
        headless=False,
        locale="ko-KR",
        no_viewport=True,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(BASE)
    
    print("Navigated to Google Flow. Watching page status...", flush=True)
    
    # 90초 동안 대기하면서 사용자가 로그인을 완료하여 labs.google 주소로 이동하는지 관찰
    start_time = time.time()
    login_success = False
    while time.time() - start_time < 90:
        current_url = page.url
        if "labs.google" in current_url and "accounts.google" not in current_url:
            print(f"Login Detected! Currently at: {current_url}", flush=True)
            login_success = True
            break
        time.sleep(1)
        
    if login_success:
        print("Success! Login session saved. Closing browser in 3 seconds...", flush=True)
        time.sleep(3)
    else:
        print("Timeout or login not completed.", flush=True)
        
    context.close()
