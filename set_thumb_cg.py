# -*- coding: utf-8 -*-
"""메인 영상 썸네일을 커스텀 B로 설정 (전화인증 후)."""
import sys, os; sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
THUMB="D:/Entertainments/DevEnvironment/autovideo/child_growth_science/thumb_ko_1280x720.jpg"
def log(m): print(m,flush=True)
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(af.PROFILE,channel="chrome",headless=False,locale="ko-KR",no_viewport=True,ignore_default_args=["--enable-automation"],args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg=ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto("https://studio.youtube.com/video/vvHZ27l9jr4/edit",wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
    try: pg.get_by_text("썸네일",exact=True).first.scroll_into_view_if_needed(); pg.wait_for_timeout(1200)
    except Exception: pass
    done=False
    # 방법1: 숨은 input 직접
    try:
        loc=pg.locator("ytcp-thumbnail-uploader input[type='file']").first
        if loc.count()>0: loc.set_input_files(THUMB); log("input set"); done=True
    except Exception as e: log("input 실패 "+str(e)[:60])
    # 방법2: '파일 업로드' 타일 → filechooser (인증됐으면 파일창 뜸)
    if not done:
        try:
            with pg.expect_file_chooser(timeout=12000) as fc:
                pg.get_by_text("파일 업로드",exact=True).first.click(timeout=6000)
            fc.value.set_files(THUMB); log("파일업로드 set"); done=True
        except Exception as e: log("파일업로드 실패 "+str(e)[:70])
    pg.wait_for_timeout(5000); pg.screenshot(path="scratch/yt/tb1_set.png")
    # 저장
    try:
        sv=pg.locator("#save-button, ytcp-button:has-text('저장')").first
        sv.click(timeout=8000); log("저장"); pg.wait_for_timeout(6000)
    except Exception as e: log("저장 실패 "+str(e)[:60])
    pg.screenshot(path="scratch/yt/tb2_saved.png")
    log("THUMB_DONE"); pg.wait_for_timeout(2500); ctx.close()
print("END")
