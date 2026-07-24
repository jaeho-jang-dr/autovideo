# -*- coding: utf-8 -*-
"""순수 Python CDP 클라이언트(node/Playwright 무관). edit_video 페이로드 캡처 + 좌표 클릭.
사용: python cdp_ws.py capture   (피커에 결과 떠있는 상태에서 결과클릭+저장하며 캡처)"""
import sys, json, time, base64
import requests
import websocket

def find_edit_ws():
    tabs = requests.get("http://localhost:9222/json").json()
    for t in tabs:
        if t.get("type") == "page" and t.get("url", "").endswith("/edit"):
            return t["webSocketDebuggerUrl"]
    for t in tabs:
        if "/edit" in t.get("url", ""):
            return t["webSocketDebuggerUrl"]
    return None

class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, max_size=None, timeout=30, suppress_origin=True)
        self._id = 0
    def send(self, method, params=None):
        self._id += 1; mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                return msg.get("result", {})
    def click(self, x, y):
        self.send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
        self.send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1})
        self.send("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1})
    def shot(self, name):
        r = self.send("Page.captureScreenshot", {"format": "png"})
        if r.get("data"):
            open(f"scratch/yt/{name}.png", "wb").write(base64.b64decode(r["data"])); print("shot " + name, flush=True)
    def drain_for_editvideo(self, seconds):
        """seconds 동안 이벤트 수신하며 edit_video 요청 postData 확보."""
        self.ws.settimeout(1.0)
        end = time.time() + seconds
        req_id = None
        while time.time() < end:
            try:
                msg = json.loads(self.ws.recv())
            except Exception:
                continue
            if msg.get("method") == "Network.requestWillBeSent":
                p = msg["params"]; url = p.get("request", {}).get("url", "")
                if "edit_video" in url and p["request"].get("method") == "POST":
                    req_id = p["requestId"]
                    pd = p["request"].get("postData")
                    open("scratch/yt/edit_video_url.txt", "w", encoding="utf-8").write(url)
                    if pd:
                        open("scratch/yt/edit_video_req.json", "w", encoding="utf-8").write(pd)
                        print("★ postData 캡처(inline)", flush=True); return req_id
        self.ws.settimeout(30)
        return req_id

def main():
    ws_url = find_edit_ws()
    if not ws_url:
        print("edit 페이지 없음"); return
    c = CDP(ws_url)
    c.send("Network.enable")
    c.send("Page.enable")
    print("CDP 연결 OK", flush=True)
    c.shot("ws_before")
    # 결과 클릭
    c.click(440, 284); print("결과 클릭", flush=True); time.sleep(3.5)
    c.shot("ws_picked")
    # 저장 클릭 + edit_video 캡처
    c.click(1429, 97); print("저장 클릭", flush=True)
    rid = c.drain_for_editvideo(8)
    time.sleep(3)
    c.shot("ws_saved")
    # inline 못받았으면 getRequestPostData
    import os
    if rid and not os.path.exists("scratch/yt/edit_video_req.json"):
        try:
            r = c.send("Network.getRequestPostData", {"requestId": rid})
            open("scratch/yt/edit_video_req.json", "w", encoding="utf-8").write(r.get("postData", ""))
            print("★ postData 캡처(getRequestPostData)", flush=True)
        except Exception as e:
            print("getPostData 실패", str(e)[:50], flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
