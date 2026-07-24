# -*- coding: utf-8 -*-
"""UI로 카드 1장 저장하며 실제 edit_video 요청 페이로드를 캡처(요청 즉시 파일 저장).
사용: python cap_editvideo.py <VID> "<검색어>" """
import time, sys, json, base64
from playwright.sync_api import sync_playwright

VID = sys.argv[1]; SEARCH = sys.argv[2]
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii", "ignore").decode(), flush=True)

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(8000)
    cdp = ctx.new_cdp_session(pg)
    def shot(n):
        try:
            d = cdp.send("Page.captureScreenshot", {"format": "png"})
            open(f"scratch/yt/{n}.png", "wb").write(base64.b64decode(d["data"]))
            log("shot " + n)
        except Exception: pass

    def on_req(req):
        try:
            if "edit_video" in req.url and req.method == "POST":
                open("scratch/yt/edit_video_req.json", "w", encoding="utf-8").write(req.post_data or "")
                open("scratch/yt/edit_video_url.txt", "w", encoding="utf-8").write(req.url)
                log("★ edit_video 캡처 완료")
        except Exception as e: log("cap err " + str(e)[:40])
    pg.on("request", on_req)

    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); time.sleep(6)
    pg.get_by_role("button", name="카드", exact=True).first.click(timeout=6000); time.sleep(4)
    log("편집기 열림")
    pg.get_by_role("button", name="카드 추가").first.click(timeout=6000); time.sleep(2)
    pg.mouse.click(272, 134); time.sleep(4)
    sb = pg.get_by_placeholder("내 동영상 검색")
    sb.first.click(timeout=6000); sb.first.fill(SEARCH); time.sleep(3.5)
    log("검색 완료")
    pg.mouse.click(440, 284); log("결과 클릭"); time.sleep(4)
    shot("cap_picked")
    pg.mouse.click(1429, 97); log("저장 클릭"); time.sleep(6)
    shot("cap_saved")
    ctx.close()
print("DONE")
