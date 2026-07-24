# -*- coding: utf-8 -*-
"""CDP Network 도메인으로 edit_video 페이로드 캡처(Playwright 요청이벤트 대신 순수 CDP).
피커가 이미 열려있다고 가정 → 결과 클릭 + 저장."""
import time, base64, json
from playwright.sync_api import sync_playwright

reqs = {}
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii", "ignore").decode(), flush=True)

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pg = [p for p in ctx.pages if p.url.endswith("/edit")][-1]
    cdp = ctx.new_cdp_session(pg)
    cdp.send("Network.enable")

    captured = {"id": None}
    def on_will_send(params):
        try:
            u = params.get("request", {}).get("url", "")
            if "edit_video" in u and params["request"].get("method") == "POST":
                captured["id"] = params["requestId"]
                pd = params["request"].get("postData")
                if pd:
                    open("scratch/yt/edit_video_req.json", "w", encoding="utf-8").write(pd)
                    open("scratch/yt/edit_video_url.txt", "w", encoding="utf-8").write(u)
                    log("★ edit_video postData 캡처")
        except Exception as e: log("cap " + str(e)[:40])
    cdp.on("Network.requestWillBeSent", on_will_send)

    def shot(n):
        try:
            d = cdp.send("Page.captureScreenshot", {"format": "png"})
            open(f"scratch/yt/{n}.png", "wb").write(base64.b64decode(d["data"])); log("shot " + n)
        except Exception as e: log("shot " + str(e)[:25])

    # 결과 클릭 (좌표) — CDP Input 사용(Playwright actionability 배제)
    cdp.send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": 440, "y": 284, "button": "left", "clickCount": 1})
    cdp.send("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": 440, "y": 284, "button": "left", "clickCount": 1})
    log("결과 클릭(CDP)"); time.sleep(4); shot("cdp_picked")
    # 저장 클릭 (CDP)
    cdp.send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": 1429, "y": 97, "button": "left", "clickCount": 1})
    cdp.send("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": 1429, "y": 97, "button": "left", "clickCount": 1})
    log("저장 클릭(CDP)"); time.sleep(7); shot("cdp_saved")

    # postData 못 받았으면 getRequestPostData
    import os
    if not os.path.exists("scratch/yt/edit_video_req.json") and captured["id"]:
        try:
            r = cdp.send("Network.getRequestPostData", {"requestId": captured["id"]})
            open("scratch/yt/edit_video_req.json", "w", encoding="utf-8").write(r.get("postData", ""))
            log("★ getRequestPostData 캡처")
        except Exception as e: log("getPostData " + str(e)[:40])
print("DONE")
