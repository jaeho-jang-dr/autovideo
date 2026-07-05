# -*- coding: utf-8 -*-
"""세종 본편(6lGedBJ5xx4, 일부공개)을 공개(Public)로. 콘텐츠 목록 상태 텍스트 클릭."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
def log(m): print(m, flush=True)
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto("https://studio.youtube.com/channel/UC6KCrgUSdSVUd97b7ltJK_g/videos/upload", wait_until="domcontentloaded")
    pg.wait_for_timeout(11000)
    # 세종(일부공개) 행
    row = pg.locator("ytcp-video-row").filter(has_text="세종대왕").first
    ok = False
    for sel in ["ytcp-video-visibility-select", "text=일부 공개"]:
        try:
            row.locator(sel).first.click(timeout=5000, force=True); ok = True; log("상태클릭 " + sel); break
        except Exception: pass
    log("클릭 " + str(ok))
    pg.wait_for_timeout(2500); pg.screenshot(path="scratch/yt/pub_1.png")
    try:
        pg.locator("tp-yt-paper-radio-button[name='PUBLIC']").first.click(timeout=5000); log("PUBLIC 선택")
    except Exception:
        try: pg.get_by_text("공개", exact=True).first.click(timeout=4000); log("공개 텍스트")
        except Exception as e: log("공개 실패 " + str(e)[:50])
    pg.wait_for_timeout(1500); pg.screenshot(path="scratch/yt/pub_2.png")
    for sel in ["#save-button", "#done-button", "ytcp-button:has-text('게시')", "ytcp-button:has-text('저장')"]:
        try:
            b = pg.locator(sel).first
            if b.is_visible(timeout=1500): b.click(); log("저장/게시 " + sel); break
        except Exception: pass
    pg.wait_for_timeout(5000); pg.screenshot(path="scratch/yt/pub_3.png")
    log("DONE"); pg.wait_for_timeout(1500); ctx.close()
print("END")
