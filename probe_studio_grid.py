# -*- coding: utf-8 -*-
"""소유자(로그인) 스튜디오 Shorts 콘텐츠 그리드 스크린샷 — 16:9 테스트본 채워졌는지 확인."""
import os, time
import autoveo_flow as af
from playwright.sync_api import sync_playwright
os.makedirs("scratch/yt", exist_ok=True)
URL = "https://studio.youtube.com/channel/UC6KCrgUSdSVUd97b7ltJK_g/videos/short"
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto(URL, wait_until="domcontentloaded"); time.sleep(11)
    pg.screenshot(path="scratch/yt/studio_grid_recheck.png")
    print("shot: scratch/yt/studio_grid_recheck.png")
    ctx.close()
print("DONE")
