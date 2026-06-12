import os
import sys
import time
from playwright.sync_api import sync_playwright

PROFILE = os.path.abspath("assets/chrome_profile")

def main():
    print("Launching Chrome...", flush=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        
        print("Navigating to NotebookLM...")
        page.goto("https://notebooklm.google.com", timeout=60000)
        time.sleep(5)
        
        # Click the specific notebook
        print("Looking for '[테크닉] 1. Diversified'...")
        target_selector = "text=1. Diversified"
        
        try:
            loc = page.locator(target_selector).first
            if loc.is_visible(timeout=5000):
                print("Found notebook link. Clicking...")
                loc.click()
            else:
                print("Not found by text selector. Trying general click...")
                # Fallback to search by text
                page.click("text=[테크닉] 1. Diversified — HVLA 수기 교정")
        except Exception as e:
            print(f"Error clicking via locator: {e}")
            # Try scrolling or other means if needed
            ctx.close()
            return
            
        time.sleep(10) # Wait for inside load
        print(f"Inside URL: {page.url}")
        page.screenshot(path="debug/notebook_inside.png")
        print("Screenshot saved to debug/notebook_inside.png")
        
        # We need to extract the actual content. Let's dump all text from main areas.
        # Inside NotebookLM, there is a source guide or document list. Let's wait a bit and dump text.
        body_text = page.locator("body").text_content()
        with open("debug/notebook_inside_body.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
        print("Saved inside body text to debug/notebook_inside_body.txt")
        
        ctx.close()

if __name__ == "__main__":
    main()
