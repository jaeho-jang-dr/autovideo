# -*- coding: utf-8 -*-
import os
import sys
import time
from playwright.sync_api import sync_playwright

def safe_str(s):
    if not isinstance(s, str):
        s = str(s)
    return s.encode('ascii', errors='backslashreplace').decode('ascii')

def main():
    print("Playwright 디버깅 시작...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 콘솔 로그 및 페이지 에러 수집 (안전하게 인코딩 처리)
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {safe_str(err)}"))
        page.on("console", lambda msg: print(f"[CONSOLE {msg.type.upper()}] {safe_str(msg.text)}"))
        
        url = "https://drjayed.com/groove?v=16"
        print(f"Page loading: {url}")
        page.goto(url)
        page.wait_for_timeout(2000)
        
        # 스크린샷 1 (초기 로드 상태)
        page.screenshot(path="scratch/debug_groove_init.png")
        print("초기 화면 스크린샷 저장 완료 (scratch/debug_groove_init.png)")
        
        # 자판 버튼 존재 확인
        pads = page.locator("button.pad")
        print(f"발견된 자판 패드 수: {pads.count()}")
        for i in range(pads.count()):
            txt = pads.nth(i).inner_text()
            cls = pads.nth(i).get_attribute('class')
            print(f"패드 {i}: {safe_str(txt)} (classes: {safe_str(cls)})")
            
        # 1. 자음 'ㄱ' 클릭
        try:
            print("\nClicking consonant Giyeok...")
            btn_giyeok = page.locator("button.pad.cho:has-text('\u3131')").first
            btn_giyeok.click()
            page.wait_for_timeout(500)
            
            syllable = page.locator("#display-syllable").inner_text()
            print(f"Current syllable: {safe_str(syllable)}")
        except Exception as e:
            print(f"Giyeok click failed: {safe_str(e)}")
            
        # 2. 모음 'ㅣ' 클릭
        try:
            print("\nClicking vowel I...")
            btn_i = page.locator("button.pad.jung:has-text('\u3163')").first
            btn_i.click()
            page.wait_for_timeout(500)
            
            syllable = page.locator("#display-syllable").inner_text()
            print(f"Current syllable: {safe_str(syllable)}")
        except Exception as e:
            print(f"I click failed: {safe_str(e)}")
            
        # 3. 모음 '•' 클릭
        try:
            print("\nClicking vowel 아래아...")
            btn_dot = page.locator("button.pad.jung:has-text('\u2022')").first
            btn_dot.click()
            page.wait_for_timeout(500)
            
            syllable = page.locator("#display-syllable").inner_text()
            print(f"Current syllable: {safe_str(syllable)}")
        except Exception as e:
            print(f"아래아 click failed: {safe_str(e)}")

        # 스크린샷 2 (클릭 후 상태)
        page.screenshot(path="scratch/debug_groove_clicked.png")
        print("클릭 완료 후 스크린샷 저장 완료 (scratch/debug_groove_clicked.png)")
        
        browser.close()

if __name__ == "__main__":
    main()
