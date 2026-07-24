# -*- coding: utf-8 -*-
"""동영상을 일부공개로 전환. 사용: python yt_unlist.py <VIDEO_ID>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
os.makedirs("scratch/yt", exist_ok=True)
def log(m): print(m, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(40000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)

    # 1) 공개 상태 카드 펼치기
    opened = False
    for sel in ["#visibility-container", "ytcp-video-metadata-visibility",
                "#visibility ytcp-dropdown-trigger", "ytcp-video-visibility-select",
                "div.ytcp-video-metadata-visibility:has-text('공개 상태')",
                "tp-yt-paper-radio-button"]:
        try:
            pg.locator(sel).first.click(timeout=4000); opened = True; log("카드 클릭 " + sel); break
        except Exception:
            pass
    pg.wait_for_timeout(2500)
    pg.screenshot(path=f"scratch/yt/ul_{VID}_1.png")

    # 2) 일부공개 라디오 선택
    picked = False
    for sel in ["tp-yt-paper-radio-button[name='UNLISTED']", "#unlisted-radio-button",
                "tp-yt-paper-radio-button:has-text('일부 공개')",
                "ytcp-visibility-option:has-text('일부 공개')",
                "#radioContainer:has-text('일부 공개')", "text=일부 공개"]:
        try:
            pg.locator(sel).first.click(timeout=4000); picked = True; log("일부공개 선택 " + sel); break
        except Exception:
            pass
    pg.wait_for_timeout(2000)
    pg.screenshot(path=f"scratch/yt/ul_{VID}_2.png")

    # 3) 저장
    saved = False
    for sel in ["#save-button", "ytcp-button#save", "ytcp-button:has-text('저장')",
                "#done-button", "tp-yt-paper-button:has-text('저장')"]:
        try:
            pg.locator(sel).first.click(timeout=4000); saved = True; log("저장 " + sel); break
        except Exception:
            pass
    pg.wait_for_timeout(5000)
    pg.screenshot(path=f"scratch/yt/ul_{VID}_3.png")
    body = pg.inner_text("body")
    ok = ("일부 공개" in body) or ("일부공개" in body)
    log(f"UNLIST_DONE {VID} opened={opened} picked={picked} saved={saved} nowUnlisted={ok}")
    ctx.close()
