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
        print("Clicking '[테크닉] 1. Diversified'...")
        page.click("text=1. Diversified")
        time.sleep(5)
        
        # We want to wait for the chat response to finish. Let's wait 30 seconds more.
        print("Waiting for chat response to complete...")
        time.sleep(35)
        
        page.screenshot(path="debug/notebook_chat_result_done.png")
        print("Screenshot saved to debug/notebook_chat_result_done.png")
        
        # Extract the content of the chat response.
        # Chat responses are typically inside div elements with specific classes or roles.
        # Let's dump all text to verify.
        body_text = page.locator("body").text_content()
        with open("debug/notebook_chat_response_done.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
        print("Saved detailed text to debug/notebook_chat_response_done.txt")
        
        ctx.close()

if __name__ == "__main__":
    main()
