# -*- coding: utf-8 -*-
"""이미 게시된 내 댓글을 '고정'만 한다(재게시 금지).
사용: python pin_only.py <VID> "<HOOK 부분문자열>"
단계별 스크린샷 + 최종 검증(재로드 후 '고정함' 배지)."""
import sys, os, time
from playwright.sync_api import sync_playwright

VID = sys.argv[1]; HOOK = sys.argv[2]
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii", "ignore").decode(), flush=True)
def shot(pg, n):
    try: pg.screenshot(path=os.path.join(SH, f"pin_{VID}_{n}.png")); log("shot " + n)
    except Exception as e: log("shot fail " + str(e)[:40])

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(15000)
    pg.goto(f"https://www.youtube.com/watch?v={VID}", wait_until="domcontentloaded"); time.sleep(6)
    # 댓글이 로드될 때까지 스크롤(unlisted 갓업로드는 느림)
    for _ in range(8):
        if pg.locator("ytd-comment-thread-renderer").count() > 0: break
        pg.mouse.wheel(0, 800); time.sleep(2)
    time.sleep(2)
    cmt = pg.locator("ytd-comment-thread-renderer").filter(has_text=HOOK).first
    if cmt.count() == 0:
        cmt = pg.locator("ytd-comment-thread-renderer").first
    cmt.scroll_into_view_if_needed(timeout=8000); time.sleep(1.5)
    cmt.hover(); time.sleep(1); shot(pg, "1_comment")

    # 이미 고정됐는지 확인
    try:
        txt = cmt.inner_text()
        if ("고정함" in txt) or ("님이 고정" in txt) or ("Pinned" in txt):
            log("=== 이미 고정됨 → 스킵 ==="); shot(pg, "9_already"); ctx.close(); print("DONE"); sys.exit(0)
    except Exception: pass

    # ⋮ 메뉴 열기 — 실제 버튼 bounding box 중심을 마우스 클릭(프로브에서 검증됨)
    opened = False
    try:
        bb = cmt.locator("#action-menu button, ytd-menu-renderer #button, #action-menu yt-icon-button").first.bounding_box()
        if bb:
            cx, cy = bb["x"] + bb["width"]/2, bb["y"] + bb["height"]/2
            pg.mouse.move(cx, cy); time.sleep(0.4); pg.mouse.click(cx, cy)
            log(f"⋮ 클릭 ({round(cx)},{round(cy)})"); opened = True
    except Exception as e: log("⋮ 실패 " + str(e)[:50])
    time.sleep(1.8); shot(pg, "2_menu")

    # 메뉴 항목 '고정' (실제 메뉴는 '고정' 단어. 📌 압정 아이콘)
    clicked_pin = False
    for sel in ("ytd-menu-service-item-renderer:has-text('고정')",
                "tp-yt-paper-item:has-text('고정')"):
        try:
            it = pg.locator(sel).first
            if it.is_visible(timeout=1500): it.click(); clicked_pin = True; log("메뉴 '고정' 클릭: " + sel[:40]); break
        except Exception: pass
    time.sleep(1.5); shot(pg, "3_confirm_dialog")

    # 확인 다이얼로그의 '고정' 버튼
    confirmed = False
    for t in ("고정", "확인", "PIN"):
        try:
            btn = pg.get_by_role("button", name=t).first
            if btn.is_visible(timeout=1500): btn.click(); confirmed = True; log("확인 클릭: " + t); break
        except Exception: pass
    if not confirmed:
        # yt paper dialog 폴백
        for sel in ("yt-confirm-dialog-renderer #confirm-button", "#confirm-button button", "#confirm-button"):
            try:
                btn = pg.locator(sel).first
                if btn.is_visible(timeout=1500): btn.click(); confirmed = True; log("확인 폴백: " + sel); break
            except Exception: pass
    time.sleep(3); shot(pg, "4_after")

    # 검증: 재로드 후 '고정함' 배지
    pg.goto(f"https://www.youtube.com/watch?v={VID}", wait_until="domcontentloaded"); time.sleep(6)
    pg.mouse.wheel(0, 700); time.sleep(2.5)
    try: pg.locator("ytd-comment-thread-renderer").first.scroll_into_view_if_needed(timeout=6000); time.sleep(1.5)
    except Exception: pass
    verified = False
    try:
        top = pg.locator("ytd-comment-thread-renderer").first.inner_text()
        verified = ("고정함" in top) or ("님이 고정" in top) or ("Pinned" in top)
    except Exception: pass
    shot(pg, "5_verify")
    log(f"=== {VID}: menu={opened} pin={clicked_pin} confirm={confirmed} verified={verified} ===")
    ctx.close()
print("DONE")
