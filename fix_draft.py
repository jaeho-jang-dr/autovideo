# -*- coding: utf-8 -*-
"""업로드된 초안(6lGedBJ5xx4) 메타데이터 수정: 제목/설명/썸네일/아동용/카테고리/변경된콘텐츠/비공개."""
import sys, os, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
ROOT="D:/Entertainments/DevEnvironment/autovideo"
VID="6lGedBJ5xx4"
THUMB=os.path.join(ROOT,"sejong_film/main/thumbnails/thumbnail_KO_B_1280x720.jpg")
DESC=open(os.path.join(ROOT,"sejong_film/main/pkg/yt_description.txt"),encoding="utf-8").read()
TITLE="세종대왕과 한글 창제 이야기 | 훈민정음은 어떻게 태어났을까? (King Sejong & Hangeul · 5 languages)"
SH=os.path.join(ROOT,"scratch","yt"); os.makedirs(SH,exist_ok=True)
def log(m): print(m,flush=True)
def shot(pg,n):
    try: pg.screenshot(path=os.path.join(SH,n)); log("shot "+n)
    except Exception as e: log("shot fail "+str(e)[:50])

with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(af.PROFILE,channel="chrome",headless=False,locale="ko-KR",
        no_viewport=True,ignore_default_args=["--enable-automation"],args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg=ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit",wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
    shot(pg,"f0_open.png")

    # 제목: 기존(엉킴) 지우고 다시
    try:
        tb=pg.locator("[contenteditable='true'][aria-label*='제목']").first
        tb.click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(500)
        tb.type(TITLE,delay=8); log("제목 수정")
    except Exception as e: log("제목 실패 "+str(e)[:80])
    # 설명
    try:
        db=pg.locator("[contenteditable='true'][aria-label*='설명해']").first
        db.click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(400)
        db.type(DESC,delay=2); log("설명 입력")
    except Exception as e: log("설명 실패 "+str(e)[:80])
    pg.wait_for_timeout(1000); shot(pg,"f1_titledesc.png")

    # 썸네일: 숨은 file input 직접
    try:
        fi=pg.locator("input[type='file']")
        cnt=fi.count(); done=False
        for i in range(cnt):
            try: fi.nth(i).set_input_files(THUMB); done=True; log(f"썸네일 input#{i}"); break
            except Exception: pass
        if not done: log("썸네일 input 없음")
        pg.wait_for_timeout(2500)
    except Exception as e: log("썸네일 실패 "+str(e)[:80])
    shot(pg,"f2_thumb.png")

    # 아동용 아님
    try:
        r=pg.get_by_role("radio",name="아니요, 아동용이 아닙니다").first
        r.scroll_into_view_if_needed(); r.click(); log("아동용 아님")
    except Exception as e: log("아동용 실패 "+str(e)[:80])
    # 자세히 보기 펼치기
    try:
        sm=pg.locator("ytcp-button:has-text('자세히 보기'), #toggle-button").first
        sm.scroll_into_view_if_needed(); sm.click(); pg.wait_for_timeout(2000); log("자세히보기 펼침")
    except Exception as e: log("자세히보기 실패 "+str(e)[:70])
    pg.wait_for_timeout(800); shot(pg,"f3_more.png")

    # 변경된 콘텐츠(합성/수정) = 예
    try:
        # '변경된 콘텐츠' 섹션의 예 라디오
        r=pg.get_by_role("radio",name="예").first
        r.scroll_into_view_if_needed(); r.click(); log("변경된콘텐츠 예")
    except Exception as e: log("변경콘텐츠 예 실패 "+str(e)[:70])
    # 카테고리 = 교육
    try:
        cat=pg.locator("#category-container, ytcp-form-select#category").first
        cat.scroll_into_view_if_needed(); cat.click(); pg.wait_for_timeout(1000)
        pg.get_by_text("교육",exact=True).first.click(timeout=5000); log("카테고리 교육"); pg.wait_for_timeout(600)
    except Exception as e: log("카테고리 실패 "+str(e)[:70])
    shot(pg,"f4_altered_cat.png")

    # 저장
    try:
        sv=pg.locator("#save-button, ytcp-button:has-text('저장')").first
        sv.scroll_into_view_if_needed(); sv.click(timeout=8000); log("저장 클릭"); pg.wait_for_timeout(5000)
    except Exception as e: log("저장 실패 "+str(e)[:70])
    shot(pg,"f5_saved.png")
    log("FIX_DONE")
    pg.wait_for_timeout(3000); ctx.close()
print("SCRIPT_END")
