import os
import sys
import time
from playwright.sync_api import sync_playwright

PROFILE = os.path.abspath("assets/chrome_profile")

def main():
    print("Launching Chrome to wait for the complete answer...", flush=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        
        print("Navigating to NotebookLM...")
        page.goto("https://notebooklm.google.com", timeout=60000)
        time.sleep(5)
        
        print("Clicking '[테크닉] 1. Diversified'...")
        page.click("text=1. Diversified")
        time.sleep(5)
        
        # We will wait another 30 seconds for the chat answer to be complete
        print("Waiting for chat answer to finish generating...")
        time.sleep(35)
        
        page.screenshot(path="debug/notebook_unicode_query_done.png")
        print("Saved done screenshot.")
        
        body_text = page.locator("body").text_content()
        with open("debug/notebook_unicode_query_done_text.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
        print("Saved finalized text.")
        
        ctx.close()

if __name__ == "__main__":
    main()
