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
        
        # We need to click on the actual memo title. In the screenshot, there is a list under '스튜디오' on the right:
        # "뼈 소리의 환상과 1000뉴턴의 신경 리셋"
        # We can see the text and click its containing element or button.
        # Let's search all elements matching the text.
        print("Finding elements matching '뼈 소리의 환상'...")
        # Let's try locating it by CSS selectors or xpath
        elements = page.locator("text=뼈 소리의 환상과 1000뉴턴의 신경 리셋").all()
        print(f"Found {len(elements)} matching elements.")
        if elements:
            # Let's click the first one that is visible
            for el in elements:
                if el.is_visible():
                    print("Clicking the visible element...")
                    # We might need to click specifically on the text or container
                    el.click()
                    break
            time.sleep(5)
            page.screenshot(path="debug/notebook_memo_opened_details.png")
            print("Screenshot saved to debug/notebook_memo_opened_details.png")
            
            # Save the page body text after opening
            body_text = page.locator("body").text_content()
            with open("debug/notebook_memo_details_text.txt", "w", encoding="utf-8") as f:
                f.write(body_text)
            print("Extracted memo text details.")
        else:
            print("No elements found matching that text.")
            
        ctx.close()

if __name__ == "__main__":
    main()
