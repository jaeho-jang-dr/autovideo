# -*- coding: utf-8 -*-
"""DqJFWK0swds(게시된 일부공개): 설명(v3 챕터)로 갱신 + 동영상 언어=한국어 설정 후 저장.
사용: python update_growth_lang_desc.py <VIDEO_ID>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
CG = "D:/Entertainments/DevEnvironment/autovideo/child_growth_science"
DESC = open(os.path.join(CG, "desc_main_ko.txt"), encoding="utf-8").read()
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
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(9000)

    # 설명 갱신 (기존 내용 지우고 v3)
    try:
        db = pg.locator("#description-textarea #textbox").first
        db.click(timeout=8000); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(400)
        db.type(DESC, delay=1); log("설명 갱신")
    except Exception as e: log("설명 실패 " + str(e)[:70])
    shot(pg, "u1_desc.png")

    # 자세히 보기
    try:
        pg.locator("#toggle-button, ytcp-button:has-text('자세히 보기')").first.click(timeout=5000); pg.wait_for_timeout(1200); log("자세히 보기")
    except Exception as e: log("자세히보기 스킵 " + str(e)[:50])

    # 동영상 언어 = 한국어
    try:
        try: pg.get_by_text("동영상 언어", exact=False).first.scroll_into_view_if_needed(timeout=4000)
        except Exception: pass
        pg.wait_for_timeout(500)
        opened = False
        for sel in ["#language-select", "ytcp-form-select#language", "#original-language",
                    "ytcp-form-select:near(:text('동영상 언어'))"]:
            try: pg.locator(sel).first.click(timeout=3000); opened = True; log("언어 드롭다운 " + sel); break
            except Exception: pass
        if not opened:
            # 라벨 옆 form-select 추정
            try:
                lab = pg.get_by_text("동영상 언어", exact=False).first
                b = lab.bounding_box()
                pg.mouse.click(b["x"] + 60, b["y"] + 40); opened = True; log("언어 드롭다운(좌표)")
            except Exception as e: log("언어 드롭다운 실패 " + str(e)[:50])
        pg.wait_for_timeout(1200); shot(pg, "u2_langopen.png")
        if opened:
            picked = False
            for sel in ["tp-yt-paper-item:has-text('한국어')", "ytcp-text-menu tp-yt-paper-item:has-text('한국어')"]:
                try:
                    it = pg.locator(sel).first; it.wait_for(state="visible", timeout=3000); it.click(timeout=2500); picked = True; log("한국어 선택"); break
                except Exception: pass
            if not picked:
                # 검색형 드롭다운이면 타이핑
                try:
                    pg.keyboard.type("한국어", delay=40); pg.wait_for_timeout(1200)
                    pg.locator("tp-yt-paper-item:has-text('한국어')").first.click(timeout=2500); picked = True; log("한국어 선택(타이핑)")
                except Exception as e: log("한국어 선택 실패 " + str(e)[:50])
            pg.wait_for_timeout(800)
    except Exception as e: log("언어 설정 스킵 " + str(e)[:60])
    shot(pg, "u3_lang.png")

    # 저장
    saved = False
    for attempt in range(4):
        try:
            btn = pg.locator("ytcp-button#save, #save-button").first
            btn.wait_for(state="visible", timeout=6000)
            btn.click(timeout=5000, force=True); saved = True; log(f"저장(attempt {attempt})"); break
        except Exception as e:
            log(f"저장 실패 {attempt} " + str(e)[:50])
            try: pg.eval_on_selector("ytcp-button#save, #save-button", "el=>{const b=el.querySelector('button')||el;b.click();}"); saved = True; log("JS 저장"); break
            except Exception: pass
            pg.wait_for_timeout(1200)
    pg.wait_for_timeout(5000); shot(pg, "u4_saved.png")

    # 검증
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(7000)
    try:
        d = pg.locator("#description-textarea #textbox").first.inner_text(timeout=4000)
        log("DESC_HAS_CHAPTERS: " + str("4:55" in d and "7:33" in d))
    except Exception: pass
    shot(pg, "u5_verify.png")
    log("UPDATE_DONE saved=" + str(saved))
    pg.wait_for_timeout(2000); ctx.close()
print("SCRIPT_END")
