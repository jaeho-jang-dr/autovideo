# -*- coding: utf-8 -*-
"""로그인 안 한(공개) 상태로 채널 Shorts 셀프를 열어 실제 시청자가 보는 표지 확인."""
import os, time
from playwright.sync_api import sync_playwright
os.makedirs("scratch/yt", exist_ok=True)

URL = "https://www.youtube.com/@drjay-ed/shorts"
with sync_playwright() as pw:
    # 비영속(임시 프로필) → 로그아웃 상태 = 공개 시청자 시점
    br = pw.chromium.launch(channel="chrome", headless=False,
        args=["--lang=ko-KR","--no-first-run","--disable-gpu"])
    ctx = br.new_context(locale="ko-KR", viewport={"width":1400,"height":1600})
    pg = ctx.new_page(); pg.set_default_timeout(40000)
    pg.goto(URL, wait_until="domcontentloaded"); time.sleep(8)
    # 쿠키 동의 뜨면 넘기기 시도
    for t in ["모두 수락","동의","Accept all","Reject all","모두 거부"]:
        try:
            b=pg.get_by_role("button", name=t).first
            if b.is_visible(timeout=1500): b.click(); time.sleep(2); break
        except Exception: pass
    time.sleep(3)
    pg.mouse.wheel(0, 400); time.sleep(2)
    pg.screenshot(path="scratch/yt/public_shorts.png")
    print("URL:", pg.url)
    print("shot: scratch/yt/public_shorts.png")
    ctx.close(); br.close()
print("DONE")
