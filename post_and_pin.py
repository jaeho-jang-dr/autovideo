# -*- coding: utf-8 -*-
"""영상에 댓글 달고 고정. 사용: python post_and_pin.py <VID> <comment_txt>"""
import sys, time
from playwright.sync_api import sync_playwright
VID = sys.argv[1]; COMMENT = open(sys.argv[2], encoding="utf-8").read().strip()
HOOK = COMMENT.split("\n")[0][:18]
def log(m): print(m, flush=True)
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(15000)
    pg.goto(f"https://www.youtube.com/watch?v={VID}", wait_until="domcontentloaded"); time.sleep(6)
    for _ in range(3): pg.mouse.wheel(0, 700); time.sleep(2.2)
    # 댓글 게시
    posted = False
    try:
        pg.locator("#placeholder-area, #simplebox-placeholder").first.click(); time.sleep(1.5)
        pg.locator("#contenteditable-root").first.click(); time.sleep(0.5)
        pg.keyboard.type(COMMENT, delay=3); time.sleep(1)
        for sel in ("#submit-button", "ytd-button-renderer#submit-button button", "button[aria-label*='댓글']"):
            try:
                btn = pg.locator(sel).first
                if btn.is_visible(timeout=2000) and btn.is_enabled(): btn.click(); posted = True; break
            except Exception: pass
    except Exception as e: log("게시실패 " + str(e)[:40])
    time.sleep(4)
    # 고정
    pinned = False
    try:
        cmt = pg.locator("ytd-comment-thread-renderer").filter(has_text=HOOK).first
        cmt.scroll_into_view_if_needed(); time.sleep(1); cmt.hover(); time.sleep(1)
        cmt.locator("ytd-menu-renderer").first.locator("button, yt-icon-button").first.click(force=True); time.sleep(1.5)
        for t in ("맨 위에 고정", "고정"):
            try:
                it = pg.get_by_text(t, exact=False).first
                if it.is_visible(timeout=1500): it.click(); break
            except Exception: pass
        time.sleep(1.5)
        for t in ("고정", "확인"):
            try:
                btn = pg.get_by_role("button", name=t).first
                if btn.is_visible(timeout=1500): btn.click(); pinned = True; break
            except Exception: pass
    except Exception as e: log("고정실패 " + str(e)[:40])
    time.sleep(3)
    log(f"=== {VID}: 게시={'OK' if posted else 'NO'} 고정={'OK' if pinned else 'NO'} ===")
print("DONE")
