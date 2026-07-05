# -*- coding: utf-8 -*-
"""아이키성장 초안을 '초안 수정' 마법사(ytcp-uploads-dialog 스코프)로 완성→일부공개 게시.
사용: python draft_wizard_publish.py <VIDEO_ID>"""
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
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(40000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(8000)
    for sel in ["ytcp-button:has-text('초안 수정')", "text=초안 수정"]:
        try: pg.locator(sel).first.click(timeout=5000); log("초안 수정 클릭"); break
        except Exception: pass
    pg.wait_for_timeout(5000)
    dlg = pg.locator("ytcp-uploads-dialog")
    try: dlg.wait_for(state="visible", timeout=10000); log("마법사 다이얼로그 감지")
    except Exception as e: log("다이얼로그 대기 실패 " + str(e)[:50])
    shot(pg, "w0_wizard.png")

    # 제목 (다이얼로그 스코프)
    try:
        tb = dlg.locator("#title-textarea #textbox").first
        tb.click(timeout=8000); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(400)
        tb.type(TITLE, delay=8); log("제목 입력")
    except Exception as e: log("제목 실패 " + str(e)[:70])
    # 설명
    try:
        db = dlg.locator("#description-textarea #textbox").first
        db.click(timeout=8000); pg.wait_for_timeout(300); db.type(DESC, delay=1); log("설명 입력")
    except Exception as e: log("설명 실패 " + str(e)[:70])
    shot(pg, "w1_titledesc.png")
    # 썸네일
    try:
        with pg.expect_file_chooser(timeout=8000) as fc:
            dlg.locator("#select-button, ytcp-button:has-text('파일 업로드')").first.click(timeout=6000)
        fc.value.set_files(THUMB); log("썸네일 업로드"); pg.wait_for_timeout(3000)
    except Exception as e: log("썸네일 실패 " + str(e)[:70])
    shot(pg, "w2_thumb.png")
    # 아동용 아님
    try:
        dlg.get_by_text("아니요, 아동용이 아닙니다", exact=False).first.click(timeout=6000); log("아동용 아님")
    except Exception as e: log("아동용 실패 " + str(e)[:70])
    # 자세히 보기
    try:
        dlg.locator("#toggle-button, ytcp-button:has-text('자세히 보기')").first.click(timeout=5000); pg.wait_for_timeout(1200); log("자세히 보기")
    except Exception as e: log("자세히보기 스킵 " + str(e)[:60])
    # 변경된 콘텐츠 = 예
    altered = False
    try:
        try: dlg.get_by_text("변경된 콘텐츠", exact=False).first.scroll_into_view_if_needed(timeout=4000)
        except Exception: pass
        pg.wait_for_timeout(500)
        for sel in ["#altered-content tp-yt-paper-radio-button:has-text('예')",
                    "ytcp-video-altered-content tp-yt-paper-radio-button:has-text('예')"]:
            try: dlg.locator(sel).first.click(timeout=2500); altered = True; log("변경콘텐츠 예 " + sel); break
            except Exception: pass
        if not altered:
            try: dlg.locator("ytcp-video-altered-content").get_by_role("radio", name="예").first.click(timeout=2500); altered = True; log("변경콘텐츠 예(role)")
            except Exception as e: log("변경콘텐츠 예 실패 " + str(e)[:50])
    except Exception as e: log("변경콘텐츠 스킵 " + str(e)[:60])
    # 카테고리 (이미 교육이면 스킵)
    try:
        cur = ""
        try: cur = dlg.locator("#category-container, ytcp-form-select#category").first.inner_text(timeout=2500)
        except Exception: pass
        if "교육" not in cur:
            dlg.locator("#category-container, ytcp-form-select#category").first.click(timeout=4000); pg.wait_for_timeout(1200)
            for sel in ["tp-yt-paper-item:has-text('교육')", "ytcp-text-menu tp-yt-paper-item:has-text('교육')"]:
                try:
                    it = pg.locator(sel).first; it.wait_for(state="visible", timeout=3000); it.click(timeout=2500); log("카테고리 교육"); break
                except Exception: pass
            pg.wait_for_timeout(1000)
            try:
                if pg.locator("tp-yt-paper-listbox").filter(has=pg.locator(":scope")).count() > 0: pg.keyboard.press("Escape")
            except Exception: pass
        else: log("카테고리 이미 교육")
    except Exception as e: log("카테고리 스킵 " + str(e)[:60])
    pg.wait_for_timeout(800); shot(pg, "w3_details.png")

    # 다음 x3
    for i in range(3):
        ok = False
        for sel in ["#next-button", "ytcp-button:has-text('다음')"]:
            try: dlg.locator(sel).first.click(timeout=6000); ok = True; log(f"다음{i+1}"); break
            except Exception: pass
        if not ok: log(f"다음{i+1} 실패"); shot(pg, f"w_next{i+1}_fail.png")
        pg.wait_for_timeout(2500)
    shot(pg, "w4_visibility.png")
    # 일부 공개
    try:
        r = dlg.get_by_role("radio", name="일부 공개").first
        r.wait_for(state="visible", timeout=8000); r.click(timeout=5000); log("일부공개 선택")
    except Exception as e:
        try: dlg.locator("tp-yt-paper-radio-button[name='UNLISTED']").first.click(timeout=4000); log("일부공개(대체)")
        except Exception as e2: log("일부공개 실패 " + str(e)[:60])
    pg.wait_for_timeout(1000); shot(pg, "w5_unlisted.png")
    # 저장/게시
    saved = False
    for attempt in range(3):
        try:
            dlg.locator("#done-button, ytcp-button:has-text('저장'), ytcp-button:has-text('게시')").first.click(timeout=8000, force=True)
            saved = True; log(f"저장(attempt {attempt})"); break
        except Exception as e:
            log(f"저장 실패 {attempt} " + str(e)[:50])
            try: pg.eval_on_selector("#done-button", "el=>{const b=el.querySelector('button')||el;b.click();}"); saved = True; log("JS 저장"); break
            except Exception: pass
            pg.wait_for_timeout(1500)
    pg.wait_for_timeout(6000); shot(pg, "w6_saved.png")

    # 검증
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(7000)
    try:
        t = pg.locator("#title-textarea #textbox").first.inner_text(timeout=4000); log("TITLE_NOW: " + t[:50])
    except Exception: pass
    try:
        body = pg.inner_text("body")
        for k in ["일부 공개", "비공개", "임시본", "초안"]:
            if k in body: log("상태포함: " + k)
    except Exception: pass
    shot(pg, "w7_verify.png")
    log("WIZARD_DONE altered=" + str(altered) + " saved=" + str(saved))
    pg.wait_for_timeout(2000)
    ctx.close()
print("SCRIPT_END")
