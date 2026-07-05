# -*- coding: utf-8 -*-
"""초안 정밀 수정: 아동용 아님 + AI 사용 예 + 카테고리 교육 + 제목 띄어쓰기 + 저장."""
import sys, os; sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
TITLE="세종대왕과 한글 창제 이야기 | 훈민정음은 어떻게 태어났을까? (King Sejong & Hangeul · 5 languages)"
SH="scratch/yt"
def log(m): print(m,flush=True)
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(af.PROFILE,channel="chrome",headless=False,locale="ko-KR",no_viewport=True,ignore_default_args=["--enable-automation"],args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg=ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto("https://studio.youtube.com/video/6lGedBJ5xx4/edit",wait_until="domcontentloaded"); pg.wait_for_timeout(9000)

    # 제목 띄어쓰기 수정 (insert_text로 공백 보존)
    try:
        tb=pg.locator("[contenteditable='true'][aria-label*='제목']").first
        tb.click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(500)
        pg.keyboard.insert_text(TITLE); log("제목 재설정")
    except Exception as e: log("제목 실패 "+str(e)[:80])
    pg.wait_for_timeout(800)

    # 자세히 보기 펼치기
    try: pg.locator("ytcp-button:has-text('자세히 보기'),#toggle-button").first.click(timeout=6000); pg.wait_for_timeout(2000); log("자세히보기")
    except Exception as e: log("자세히보기 실패 "+str(e)[:60])

    # 아동용 아님 (정확한 이름)
    try:
        r=pg.get_by_role("radio",name="아동용이 아닙니다",exact=False).first
        r.scroll_into_view_if_needed(); pg.wait_for_timeout(400); r.click(); log("→ 아동용 아님 클릭")
    except Exception as e: log("아동용아님 실패 "+str(e)[:70])
    # AI 사용 예
    try:
        r=pg.get_by_role("radio",name="AI가 사용되었습니다",exact=False).first
        r.scroll_into_view_if_needed(); pg.wait_for_timeout(400); r.click(); log("→ AI 사용 예 클릭")
    except Exception as e: log("AI예 실패 "+str(e)[:70])
    pg.wait_for_timeout(800); pg.screenshot(path=SH+"/g1_radios.png")

    # 카테고리 → 교육 (현재값 인물/블로그 클릭해 드롭다운 열기)
    try:
        trg=pg.get_by_text("인물/블로그",exact=True).first
        trg.scroll_into_view_if_needed(); trg.click(); pg.wait_for_timeout(1200)
        opt=pg.get_by_text("교육",exact=True).first
        opt.click(timeout=5000); log("→ 카테고리 교육"); pg.wait_for_timeout(800)
    except Exception as e: log("카테고리 실패 "+str(e)[:70])
    pg.screenshot(path=SH+"/g2_cat.png")

    # 저장
    try:
        pg.locator("#save-button, ytcp-button:has-text('저장')").first.click(timeout=8000); log("저장"); pg.wait_for_timeout(5000)
    except Exception as e: log("저장 실패 "+str(e)[:70])
    pg.screenshot(path=SH+"/g3_saved.png")
    log("FIX2_DONE"); pg.wait_for_timeout(2500); ctx.close()
print("END")
