import os
import sys
import time
from playwright.sync_api import sync_playwright

PROFILE = os.path.abspath("assets/chrome_profile")

def main():
    print("Launching Chrome to query directly via chat...", flush=True)
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
        
        # We will directly query the chat asking for: "뼈 소리의 환상과 1000뉴턴의 신경 리셋" 에 관한 구체적인 본문 내용
        print("Locating chat input...")
        chat_input = page.locator("textarea, div[role='textbox'][contenteditable='true']").last
        chat_input.click()
        
        # We ask for a comprehensive summary of "뼈 소리의 환상과 1000뉴턴의 신경 리셋" and "우두둑 소리의 진실"
        query = "'뼈 소리의 환상과 1000뉴턴의 신경 리셋' 메모와 '우두둑 소리의 진실' 메모의 전체 핵심 내용을 도수치료시 뼈 소리가 나는 기전과 신경학적 효과(1000뉴턴의 추력, 신경 리셋, 통증 억제 기전 등) 위주로 아주 상세하게 요약해줘."
        chat_input.fill(query)
        page.keyboard.press("Enter")
        
        print("Waiting for response (40s)...")
        time.sleep(40)
        
        page.screenshot(path="debug/notebook_detail_query_result.png")
        print("Saved screenshot of detailed response.")
        
        body_text = page.locator("body").text_content()
        with open("debug/notebook_detail_query_text.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
        print("Saved query response text.")
        
        ctx.close()

if __name__ == "__main__":
    main()
