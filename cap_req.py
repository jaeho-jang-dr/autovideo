# -*- coding: utf-8 -*-
"""youtubei POST 요청의 본문(context) 캡처 → edit_video에 재사용. 사용: python cap_req.py <VID>"""
import time, sys, json
from playwright.sync_api import sync_playwright
VID = sys.argv[1] if len(sys.argv) > 1 else "YTex0QGe17o"
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)
grabbed = {}
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(12000)

    def on_req(req):
        u = req.url
        if "youtubei/v1" in u and req.method == "POST" and "context" not in grabbed:
            try:
                pd = req.post_data
                if pd and '"context"' in pd:
                    grabbed["context"] = json.loads(pd).get("context")
                    grabbed["url"] = u.split("?")[0]
                    grabbed["auth"] = req.headers.get("authorization", "")[:30]
                    grabbed["xorigin"] = req.headers.get("x-origin", "")
            except Exception: pass
    pg.on("request", on_req)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded")
    time.sleep=__import__("time").sleep; time.sleep(8)
    if "context" in grabbed:
        c = grabbed["context"]
        log("URL예: " + grabbed["url"])
        log("auth헤더: " + grabbed["auth"] + " ...")
        log("x-origin: " + grabbed["xorigin"])
        log("context.client keys: " + str(list((c.get("client") or {}).keys())))
        log("context.user: " + json.dumps(c.get("user"), ensure_ascii=False))
        log("context.request: " + json.dumps(c.get("request"), ensure_ascii=False)[:400])
        # 전체 context 저장(재사용)
        open("scratch/yt/ctx.json", "w", encoding="utf-8").write(json.dumps(c, ensure_ascii=False))
        log("→ scratch/yt/ctx.json 저장")
    else:
        log("컨텍스트 캡처 실패")
    ctx.close()
print("DONE")
