# -*- coding: utf-8 -*-
"""Studio 댓글 수신함에서 특정 댓글에 ❤️하트 + 답글. (재게시 방지: 이미 답글 있으면 스킵)
사용: python reply_comment.py "<작성자핸들>" "<답글텍스트>"
예:  python reply_comment.py "@JinSung-vb6ut" "따뜻한 응원 정말 감사합니다 ^^"
"""
import sys, os, time
from playwright.sync_api import sync_playwright
CID = "UC6KCrgUSdSVUd97b7ltJK_g"
HANDLE = sys.argv[1]; REPLY = sys.argv[2]
TAG = "".join(ch for ch in HANDLE if ch.isalnum())[:10]
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)
def shot(pg, n):
    try: pg.screenshot(path=os.path.join(SH, f"reply_{TAG}_{n}.png")); log("shot " + n)
    except Exception as e: log("shot fail " + str(e)[:40])

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(20000)
    pg.goto(f"https://studio.youtube.com/channel/{CID}/comments/inbox", wait_until="domcontentloaded"); time.sleep(8)

    # 대상 댓글 컨테이너
    cont = pg.locator("ytcp-comment").filter(has_text=HANDLE).first
    cont.scroll_into_view_if_needed(); time.sleep(1.5); shot(pg, "0_found")

    # 이미 답글 있으면 스킵(재게시 방지)
    try:
        t = cont.inner_text()
        import re
        m = re.search(r"답글\s*(\d+)\s*개", t)
        if m and int(m.group(1)) > 0:
            log(f"이미 답글 {m.group(1)}개 → 스킵"); shot(pg, "9_skip"); ctx.close(); sys.exit(0)
    except Exception: pass

    # ❤️ 하트(최고) — aria='하트'일 때만(이미 눌렀으면 '하트 취소'라 건드리지 않음)
    hearted = False
    try:
        hb = cont.locator("ytcp-icon-button[aria-label='하트']").first
        if hb.count() > 0 and hb.is_visible():
            hb.click(); hearted = True; log("❤️ 하트 클릭"); time.sleep(1.5)
    except Exception as e: log("하트 실패 " + str(e)[:50])
    shot(pg, "1_hearted")

    # 답글 열기
    opened = False
    try:
        cont.locator("#reply-button").first.click(); opened = True; log("답글 버튼 클릭"); time.sleep(1.5)
    except Exception as e: log("답글버튼 실패 " + str(e)[:50])
    shot(pg, "2_replybox")

    # 답글 입력창에 텍스트
    typed = False
    for sel in ("#textarea #contenteditable-root", "#contenteditable-root",
                "ytcp-social-suggestions-textbox #textarea", "#textarea", "textarea"):
        try:
            box = cont.locator(sel).first
            if box.count() > 0 and box.is_visible():
                box.click(); time.sleep(0.4); pg.keyboard.type(REPLY, delay=8); typed = True
                log("입력: " + sel); break
        except Exception: pass
    if not typed:
        # 컨테이너 밖(다이얼로그)일 수 있음 — 페이지 전역에서
        for sel in ("#contenteditable-root", "#textarea"):
            try:
                box = pg.locator(sel).last
                if box.is_visible(): box.click(); time.sleep(0.4); pg.keyboard.type(REPLY, delay=8); typed = True; log("입력(전역): " + sel); break
            except Exception: pass
    time.sleep(1); shot(pg, "3_typed")

    # 제출 '답글' 버튼 (제출용 — reply 편집기 안의 활성화된 답글/댓글 버튼)
    submitted = False
    try:
        for sel in ("ytcp-comment-button#submit-button button",
                    "#submit-button button", "#submit-button"):
            try:
                sb = cont.locator(sel).first
                if sb.count() > 0 and sb.is_visible() and sb.is_enabled(): sb.click(); submitted = True; log("제출: " + sel); break
            except Exception: pass
        if not submitted:
            # 텍스트 '답글' 버튼 중 활성화된 것(원래 reply-button 제외 위해 마지막)
            btns = pg.get_by_role("button", name="답글")
            for i in range(btns.count()-1, -1, -1):
                bt = btns.nth(i)
                if bt.is_visible() and bt.is_enabled(): bt.click(); submitted = True; log("제출(텍스트답글)"); break
    except Exception as e: log("제출 실패 " + str(e)[:50])
    time.sleep(3); shot(pg, "4_submitted")
    log(f"=== {HANDLE}: hearted={hearted} opened={opened} typed={typed} submitted={submitted} ===")
    ctx.close()
print("DONE")
