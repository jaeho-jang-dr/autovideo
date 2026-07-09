# -*- coding: utf-8 -*-
"""영상을 재생목록에 추가 (없으면 생성). 사용: python playlist_add.py <VID> <재생목록명> [create]"""
import sys, time
from playwright.sync_api import sync_playwright
VID = sys.argv[1]; PL = sys.argv[2]; CREATE = (len(sys.argv) > 3 and sys.argv[3] == "create")
def log(m): print(m, flush=True)
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(12000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); time.sleep(7)
    pg.locator("ytcp-video-metadata-playlists ytcp-dropdown-trigger, ytcp-dropdown-trigger").first.click(); time.sleep(2)
    done = False
    if CREATE:
        pg.get_by_text("새 재생목록", exact=True).last.click(); time.sleep(1.5)
        try: pg.get_by_role("menuitem", name="새 재생목록").first.click()
        except Exception: pg.locator("tp-yt-paper-item:has-text('새 재생목록')").first.click()
        time.sleep(2.5)
        pg.locator("ytcp-dialog #textbox, tp-yt-paper-dialog #textbox").first.click(); time.sleep(0.3)
        pg.keyboard.type(PL, delay=12); time.sleep(1)
        for getc in (lambda: pg.locator("#create-button").first, lambda: pg.get_by_role("button", name="만들기").first):
            try:
                c = getc()
                if c.is_visible(timeout=1500) and c.is_enabled(): c.click(); done = True; log("생성"); break
            except Exception: pass
        time.sleep(3)
    else:
        # 검색 후 체크
        try:
            pg.get_by_placeholder("재생목록 검색").fill(PL, timeout=3000); time.sleep(1.5)
        except Exception: pass
        try:
            pg.get_by_text(PL, exact=True).first.click(); done = True; log("체크"); time.sleep(1)
        except Exception as e: log("체크실패 " + str(e)[:40])
    # 완료 + 저장
    try: pg.get_by_text("완료", exact=True).first.click(); time.sleep(2)
    except Exception: pass
    saved = False
    for gets in (lambda: pg.locator("#save-button").first, lambda: pg.get_by_role("button", name="저장").first):
        try:
            s = gets()
            if s.is_visible(timeout=1500) and s.is_enabled(): s.click(); saved = True; break
        except Exception: pass
    time.sleep(4)
    log(f"=== {VID} → {PL}: 처리={done} 저장={'OK' if saved else 'NO(이미저장/변경없음)'} ===")
print("DONE")
