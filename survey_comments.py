# -*- coding: utf-8 -*-
"""채널 전체 댓글 스캔(읽기 전용). Studio 댓글 수신함에서 스레드 덤프.
사용: python survey_comments.py"""
import sys, os, time, json
from playwright.sync_api import sync_playwright
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(20000)
    # 채널 ID 추출
    pg.goto("https://studio.youtube.com", wait_until="domcontentloaded"); time.sleep(9)
    url = pg.url; log("studio url: " + url)
    cid = None
    if "/channel/" in url:
        cid = url.split("/channel/")[1].split("/")[0]
    if not cid:
        # studio 페이지 내 /channel/UC 링크 탐색
        try:
            href = pg.locator("a[href*='/channel/UC']").first.get_attribute("href", timeout=4000)
            if href and "/channel/" in href: cid = href.split("/channel/")[1].split("/")[0].split("?")[0]
        except Exception: pass
    if not cid:
        # youtube.com 채널 페이지 canonical에서
        pg.goto("https://www.youtube.com/@drjay-ed", wait_until="domcontentloaded"); time.sleep(5)
        try:
            cid = pg.eval_on_selector("link[rel=canonical]", "el => el.href").split("/channel/")[1].split("/")[0]
        except Exception:
            try: cid = pg.eval_on_selector("meta[itemprop=identifier]", "el => el.content")
            except Exception: pass
    log("channel id: " + str(cid))
    if not cid:
        pg.screenshot(path=os.path.join(SH, "survey_nocid.png")); ctx.close(); sys.exit("채널ID 못 찾음")

    # 댓글 수신함 (게시된 모든 댓글 탭)
    pg.goto(f"https://studio.youtube.com/channel/{cid}/comments/inbox", wait_until="domcontentloaded"); time.sleep(7)
    for _ in range(6): pg.mouse.wheel(0, 1200); time.sleep(1.5)
    try:
        pg.screenshot(path=os.path.join(SH, "survey_inbox.png"), full_page=True); log("shot survey_inbox")
    except Exception as e:
        log("full_page shot failed, fallback viewport: " + str(e)[:80])
        pg.screenshot(path=os.path.join(SH, "survey_inbox.png")); log("shot survey_inbox (viewport)")

    threads = pg.locator("ytcp-comment-thread-renderer").all() or pg.locator("ytcp-comment-thread").all()
    log(f"=== 스레드 수: {len(threads)} ===")
    out = []
    for i, t in enumerate(threads):
        try:
            txt = t.inner_text().replace("\n", " | ")[:400]
        except Exception as e:
            txt = "err " + str(e)[:40]
        replied = ("답글 1개" in txt) or ("답글" in txt and "개" in txt) or False
        log(f"[{i}] {txt}")
        out.append({"i": i, "text": txt})
    json.dump(out, open(os.path.join(SH, "survey_comments.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("saved survey_comments.json")
    ctx.close()
print("DONE")
