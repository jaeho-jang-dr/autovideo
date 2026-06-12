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
        time.sleep(10)
        
        # Click the search/chat input box to send a question
        print("Searching for the chat input...")
        # Inside NotebookLM, chat input is usually a textarea or div with role='textbox' or class/placeholder containing '질문' or 'Ask'
        chat_input = page.locator("textarea, div[role='textbox'][contenteditable='true']").last
        chat_input.click()
        
        question = "뼈 소리의 환상과 1000뉴턴의 신경 리셋 메모나 에세이의 전문 텍스트를 출력해줘. 관절 도수치료시 뻑 소리가 나는 원리와 기전에 대한 상세한 한글 설명이 필요해."
        print(f"Typing question: {question}")
        chat_input.fill(question)
        page.keyboard.press("Enter")
        
        print("Waiting for response (~25s)...")
        time.sleep(25)
        
        page.screenshot(path="debug/notebook_chat_result.png")
        print("Screenshot saved to debug/notebook_chat_result.png")
        
        body_text = page.locator("body").text_content()
        with open("debug/notebook_chat_response.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
        print("Saved body text containing chat response.")
        
        ctx.close()

if __name__ == "__main__":
    main()
