import os
import sys
import time
from playwright.sync_api import sync_playwright

PROFILE = os.path.abspath("assets/chrome_profile")

def main():
    print("Launching Chrome to get chat content text...", flush=True)
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
        
        # We want to extract the text inside the chat panel. 
        # Let's inspect the chat panel contents. 
        # Typically the chat bubbles are inside divs with role="presentation" or text contents.
        # Let's get text from all elements that contain the chat answers.
        print("Extracting chat panel text...")
        # We can look for divs under the chatting area
        chat_area = page.locator("div[role='log'], div[aria-label='chat'], div[class*='chat']").all()
        for idx, el in enumerate(chat_area):
            try:
                txt = el.text_content()
                if txt and len(txt) > 200:
                    print(f"Chat area {idx} text length: {len(txt)}")
                    with open(f"debug/notebook_chat_panel_{idx}.txt", "w", encoding="utf-8") as f:
                        f.write(txt)
            except Exception:
                pass
                
        # Also just save the whole text content of the page but properly handled in Python to avoid console encode errors.
        full_text = page.locator("body").text_content()
        with open("debug/notebook_full_raw_text.txt", "w", encoding="utf-8") as f:
            f.write(full_text)
            
        ctx.close()

if __name__ == "__main__":
    main()
