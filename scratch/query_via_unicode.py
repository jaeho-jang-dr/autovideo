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
        
        print("Clicking '[테크닉] 1. Diversified'...")
        page.click("text=1. Diversified")
        time.sleep(5)
        
        print("Locating chat input...")
        chat_input = page.locator("textarea, div[role='textbox'][contenteditable='true']").last
        chat_input.click()
        
        # Fixed Unicode escape string (replaced \ucsetsb with \uc14b)
        query = (
            "\ubf08 \uc18c\ub9ac\uc758 \ud658\uc0c1\uacfc 1000\ub274\ud134\uc758 \uc2e0\uacbd "
            "\ub9ac\uc14b \ubc0f \uc6b0\ub450\ub451 \uc18c\ub9ac\uc758 \uc9c4\uc2e4 \uba54\ubaa8\uc758 "
            "\ud575\uc2ec \ub0b4\uc6a9\uc744 \ub3c4\uc218\uce58\ub8cc\uc2dc \ubf08 \uc18c\ub9ac\uac00 "
            "\ub098\ub294 \uae30\uc804\uacfc \uc2e0\uacbd\ud559\uc801 \ud6a8\uacfc(1000\ub274\ud134\uc758 "
            "\ucd94\ub825, \uc2e0\uacbd \ub9ac\uc14b, \ud1b5\uc99d \uc5b5\uc81c \uae30\uc804 \ubc0f "
            "\uad00\uc808 \uc218\uc6a9\uae30 \uc790\uadf9) \uc704\uc8fc\ub85c \uc544\uc8fc "
            "\uc0c1\uc138\ud558\uac8c \uc694\uc57d\ud574\uc998."
        )
        
        print("Typing question...")
        chat_input.fill(query)
        page.keyboard.press("Enter")
        
        print("Waiting for response (45s)...")
        time.sleep(45)
        
        page.screenshot(path="debug/notebook_unicode_query_result.png")
        print("Saved screenshot of response.")
        
        body_text = page.locator("body").text_content()
        with open("debug/notebook_unicode_query_text.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
        print("Saved query response text.")
        
        ctx.close()

if __name__ == "__main__":
    main()
