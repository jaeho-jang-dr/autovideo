import os
import sys
import time
from playwright.sync_api import sync_playwright

PROFILE = os.path.abspath("assets/chrome_profile")

def main():
    print("Launching Chrome to check NotebookLM...", flush=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        
        # Navigate to NotebookLM
        print("Navigating to https://notebooklm.google.com ...")
        page.goto("https://notebooklm.google.com", timeout=60000)
        time.sleep(5)
        
        # Take a screenshot to see the list of notebooks
        os.makedirs("debug", exist_ok=True)
        page.screenshot(path="debug/notebooklm_home.png")
        print("Screenshot saved to debug/notebooklm_home.png")
        
        # Print page title and current URL
        print(f"URL: {page.url}")
        print(f"Title: {page.title()}")
        
        # Let's wait a bit and dump some texts to see if we can find 'diversified technique'
        html = page.content()
        if "diversified" in html.lower() or "technique" in html.lower() or "도수" in html:
            print("Found notebook reference in HTML!")
            
        ctx.close()

if __name__ == "__main__":
    main()
