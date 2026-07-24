# -*- coding: utf-8 -*-
"""동영상 언어(기본 언어) 설정. update_growth_lang_desc 로직 범용화.
사용: python set_video_lang.py <VID> <언어명>   예: python set_video_lang.py RL7QZ37HVXI 영어"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]; LANG = sys.argv[2]
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    # 자세히 보기
    try:
        pg.locator("#toggle-button, ytcp-button:has-text('자세히 보기')").first.click(timeout=5000); pg.wait_for_timeout(1400); log("자세히 보기")
    except Exception as e: log("자세히보기 스킵 " + str(e)[:50])
    # 동영상 언어 드롭다운
    try:
        try: pg.get_by_text("동영상 언어", exact=False).first.scroll_into_view_if_needed(timeout=4000)
        except Exception: pass
        pg.wait_for_timeout(600)
        opened = False
        for sel in ["#language-select", "ytcp-form-select#language", "#original-language",
                    "ytcp-form-select:near(:text('동영상 언어'))"]:
            try: pg.locator(sel).first.click(timeout=3000); opened = True; log("언어 드롭다운 " + sel); break
            except Exception: pass
        if not opened:
            try:
                lab = pg.get_by_text("동영상 언어", exact=False).first; b = lab.bounding_box()
                pg.mouse.click(b["x"] + 60, b["y"] + 40); opened = True; log("언어 드롭다운(좌표)")
            except Exception as e: log("드롭다운 실패 " + str(e)[:50])
        pg.wait_for_timeout(1300); pg.screenshot(path=f"{SH}/svl_open.png")
        if opened:
            picked = False
            for sel in [f"tp-yt-paper-item:has-text('{LANG}')", f"ytcp-text-menu tp-yt-paper-item:has-text('{LANG}')"]:
                try:
                    it = pg.locator(sel).first; it.wait_for(state="visible", timeout=3000); it.click(timeout=2500); picked = True; log(f"{LANG} 선택"); break
                except Exception: pass
            if not picked:
                try:
                    pg.keyboard.type(LANG, delay=40); pg.wait_for_timeout(1200)
                    pg.locator(f"tp-yt-paper-item:has-text('{LANG}')").first.click(timeout=2500); picked = True; log(f"{LANG} 선택(타이핑)")
                except Exception as e: log("선택 실패 " + str(e)[:50])
            pg.wait_for_timeout(800)
    except Exception as e: log("언어 설정 스킵 " + str(e)[:60])
    pg.screenshot(path=f"{SH}/svl_lang.png")
    # 저장
    saved = False
    for attempt in range(4):
        try:
            btn = pg.locator("ytcp-button#save, #save-button").first
            btn.wait_for(state="visible", timeout=6000); btn.click(timeout=5000, force=True); saved = True; log(f"저장(attempt {attempt})"); break
        except Exception: pg.wait_for_timeout(1500)
    pg.wait_for_timeout(4000); pg.screenshot(path=f"{SH}/svl_done.png")
    log(f"SETLANG_DONE {VID} -> {LANG} saved={saved}")
    ctx.close()
