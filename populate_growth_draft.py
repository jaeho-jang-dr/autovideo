# -*- coding: utf-8 -*-
"""아이키성장 초안(DqJFWK0swds) 완성: 편집페이지에서 제목·설명·썸네일·아동용아님·변경된콘텐츠(예)·카테고리 채우고 저장.
사용: python populate_growth_draft.py <VIDEO_ID>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
ROOT = "D:/Entertainments/DevEnvironment/autovideo"
CG = os.path.join(ROOT, "child_growth_science")
THUMB = os.path.join(CG, "thumb_ko_1280.jpg")
DESC = open(os.path.join(CG, "desc_main_ko.txt"), encoding="utf-8").read()
TITLE = "우리 아이 키 얼마나 클까? | 소아 성장·키 크는 과학 (부모 필독)"
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)
def shot(pg, n):
    try: pg.screenshot(path=os.path.join(SH, n)); log("shot " + n)
    except Exception as e: log("shot fail " + n + " " + str(e)[:50])

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
        no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(9000)

    # 제목
    try:
        tb = pg.locator("#title-textarea #textbox, div[aria-label*='제목'][contenteditable]").first
        tb.click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(400)
        tb.type(TITLE, delay=8); log("제목 입력")
    except Exception as e: log("제목 실패 " + str(e)[:70])
    # 설명
    try:
        db = pg.locator("#description-textarea #textbox, div[aria-label*='설명'][contenteditable]").first
        db.click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(300)
        db.type(DESC, delay=1); log("설명 입력")
    except Exception as e: log("설명 실패 " + str(e)[:70])
    shot(pg, "p1_titledesc.png")
    # 썸네일
    try:
        with pg.expect_file_chooser(timeout=8000) as fc:
            pg.locator("#select-button, ytcp-button:has-text('파일 업로드')").first.click(timeout=6000)
        fc.value.set_files(THUMB); log("썸네일 업로드"); pg.wait_for_timeout(3000)
    except Exception as e: log("썸네일 실패 " + str(e)[:70])
    shot(pg, "p2_thumb.png")
    # 아동용 아님
    try:
        pg.get_by_text("아니요, 아동용이 아닙니다", exact=False).first.click(timeout=6000); log("아동용 아님")
    except Exception as e: log("아동용 실패 " + str(e)[:70])
    # 자세히 보기
    try:
        pg.locator("#toggle-button, ytcp-button:has-text('자세히 보기')").first.click(timeout=5000); pg.wait_for_timeout(1200); log("자세히 보기")
    except Exception as e: log("자세히보기 스킵 " + str(e)[:60])
    # 변경된 콘텐츠 = 예
    altered = False
    try:
        try: pg.get_by_text("변경된 콘텐츠", exact=False).first.scroll_into_view_if_needed(timeout=4000)
        except Exception: pass
        pg.wait_for_timeout(600)
        cands = [
            "ytcp-video-altered-content #radio-yes",
            "ytcp-video-altered-content tp-yt-paper-radio-button:has-text('예')",
            "#altered-content tp-yt-paper-radio-button:has-text('예')",
        ]
        for sel in cands:
            try: pg.locator(sel).first.click(timeout=2500); altered = True; log("변경된콘텐츠 예 " + sel); break
            except Exception: pass
        if not altered:
            try:
                pg.locator("ytcp-video-altered-content").get_by_role("radio", name="예").first.click(timeout=2500); altered = True; log("변경된콘텐츠 예(role)")
            except Exception: pass
        if not altered:
            # 덤프
            try:
                html = pg.locator("ytcp-video-altered-content").first.evaluate("el=>el.outerHTML")
                log("ALTERED_HTML: " + html[:900])
            except Exception as e: log("altered dump 실패 " + str(e)[:60])
    except Exception as e: log("변경콘텐츠 스킵 " + str(e)[:60])
    shot(pg, "p3_altered.png")
    # 카테고리 교육 (이미 설정됐을 수 있음)
    try:
        cur = pg.locator("#category-container, ytcp-form-select#category").first.inner_text(timeout=3000)
        if "교육" not in cur:
            pg.locator("#category-container, ytcp-form-select#category").first.click(timeout=4000); pg.wait_for_timeout(1000)
            for sel in ["tp-yt-paper-item:has-text('교육')", "#text-item-2"]:
                try: pg.locator(sel).first.click(timeout=2500); log("카테고리 교육"); break
                except Exception: pass
            pg.wait_for_timeout(600); pg.keyboard.press("Escape")
        else: log("카테고리 이미 교육")
    except Exception as e: log("카테고리 스킵 " + str(e)[:60])
    # 저장
    saved = False
    for attempt in range(4):
        try:
            btn = pg.locator("ytcp-button#save, #save-button").first
            btn.wait_for(state="visible", timeout=6000)
            btn.click(timeout=5000, force=True); saved = True; log(f"저장(attempt {attempt})"); break
        except Exception as e:
            log(f"저장 실패 {attempt} " + str(e)[:50])
            try:
                pg.eval_on_selector("ytcp-button#save, #save-button", "el=>{const b=el.querySelector('button')||el;b.click();}")
                saved = True; log("JS 저장"); break
            except Exception: pass
            pg.wait_for_timeout(1200)
    pg.wait_for_timeout(4000); shot(pg, "p4_saved.png")
    # 검증
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(7000)
    try:
        title_now = pg.locator("#title-textarea #textbox").first.inner_text(timeout=4000)
        log("TITLE_NOW: " + title_now[:60])
    except Exception: pass
    shot(pg, "p5_verify.png")
    log("POPULATE_DONE altered=" + str(altered) + " saved=" + str(saved))
    pg.wait_for_timeout(2000)
    ctx.close()
print("SCRIPT_END")
