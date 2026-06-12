import os
import sys
import time
from playwright.sync_api import sync_playwright

PROFILE = os.path.abspath("assets/chrome_profile")

def main():
    print("Launching Chrome to search specifically inside source list...", flush=True)
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
        
        # Click on "뼈 소리의 환상과 1000뉴턴의 신경 리셋" under Studio/Notes
        # In the screenshot, it shows a list under Studio:
        # "뼈 소리의 환상과 1000뉴턴의 신경 리셋" with a play/arrow button or document icon.
        # Let's locate the element with the exact text and perform a click.
        # Sometimes there's a specific button or container to click.
        try:
            print("Trying to click on '뼈 소리의 환상과 1000뉴턴의 신경 리셋'...")
            # We will use click text with locator
            # Since the text is split, let's find the element containing this string.
            el = page.locator("div:has-text('뼈 소리의 환상과 1000뉴턴의 신경 리셋')").last
            el.scroll_into_view_if_needed()
            el.click(timeout=5000)
            print("Clicked!")
            time.sleep(5)
            page.screenshot(path="debug/notebook_memo_clicked.png")
            
            # Let's find any text editor or viewer element.
            # Usually notes open in a modal or right side panel.
            body_text = page.locator("body").text_content()
            with open("debug/notebook_memo_content_extracted.txt", "w", encoding="utf-8") as f:
                f.write(body_text)
            print("Content written to debug/notebook_memo_content_extracted.txt")
        except Exception as e:
            print(f"Error: {e}")
            
        ctx.close()

if __name__ == "__main__":
    main()
