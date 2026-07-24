# -*- coding: utf-8 -*-
"""순수 CDP 동영상 카드 결정판 v2. 편집기 열기=피처'카드' 클릭+Enter, 검증. ws 타임아웃으로 hang 방지.
사용: python cdp_final.py <VID> <검색1> [<검색2>] [--save]"""
import sys, json, time, base64, os
import requests, websocket

ARGS = sys.argv[1:]
SAVE = "--save" in ARGS
if SAVE: ARGS.remove("--save")
VID = ARGS[0]; SEARCHES = ARGS[1:]

def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii", "ignore").decode(), flush=True)

def find_ws(vid):
    for t in requests.get("http://localhost:9222/json").json():
        if t.get("type") == "page" and f"/video/{vid}/edit" in t.get("url", ""):
            return t["webSocketDebuggerUrl"]
    return None

DEEP_JS = r"""
window.__openCardEditor = function(){
  // 피처 패널의 '카드' leaf → 클릭가능 조상 찾아 .click() 직접 호출
  const stack=[document]; let leaf=null;
  while(stack.length){ const root=stack.pop();
    for(const e of root.querySelectorAll('*')){ if(e.shadowRoot) stack.push(e.shadowRoot);
      if(e.children.length===0 && (e.textContent||'').trim()==='카드' && e.offsetParent!==null){
        const r=e.getBoundingClientRect(); if(r.x>900 && r.width>0){ leaf=e; } } } }
  if(!leaf) return {found:false};
  let n=leaf;
  for(let i=0;i<8&&n;i++){
    const tag=(n.tagName||'').toLowerCase();
    if(tag==='ytcp-ve'||tag==='a'||tag==='button'||tag==='ytcp-button'||(n.getAttribute&&n.getAttribute('role')==='button')){ n.click(); return {found:true, tag}; }
    n = n.parentElement || (n.getRootNode&&n.getRootNode().host);
  }
  // 폴백: leaf 자체 click
  leaf.click(); return {found:true, tag:'leaf'};
};
window.__has = function(text){
  const stack=[document];
  while(stack.length){ const root=stack.pop();
    for(const e of root.querySelectorAll('*')){ if(e.shadowRoot) stack.push(e.shadowRoot);
      if(e.children.length===0 && (e.textContent||'').trim()===text && e.offsetParent!==null) return true; } }
  return false;
};
window.__focusInput = function(ph){
  const stack=[document];
  while(stack.length){ const root=stack.pop();
    for(const e of root.querySelectorAll('input,textarea')){
      const a=(e.getAttribute('placeholder')||e.getAttribute('aria-label')||'');
      if(a.indexOf(ph)>=0 && e.offsetParent!==null){ e.focus(); const r=e.getBoundingClientRect(); return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),found:true}; } }
    for(const e of root.querySelectorAll('*')) if(e.shadowRoot) stack.push(e.shadowRoot); }
  return {found:false};
};
window.__saveBtn = function(){
  const stack=[document]; let best=null;
  while(stack.length){ const root=stack.pop();
    for(const e of root.querySelectorAll('button,ytcp-button,[role=button]')){
      const t=(e.textContent||'').trim(); const a=(e.getAttribute('aria-label')||'');
      if((t==='저장'||a==='저장') && e.offsetParent!==null){ const r=e.getBoundingClientRect();
        if(r.width>0&&r.y<160&&r.x>700){ if(!best||r.x>best.x) best={x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)}; } }
      if(e.shadowRoot) stack.push(e.shadowRoot); }
    for(const e of root.querySelectorAll('*')) if(e.shadowRoot) stack.push(e.shadowRoot); }
  return best?{...best,found:true}:{found:false};
};
window.__cardCount = function(){
  let n=0; const stack=[document];
  while(stack.length){ const root=stack.pop();
    for(const e of root.querySelectorAll('*')){ if(e.shadowRoot) stack.push(e.shadowRoot);
      if(e.children.length===0){ const t=(e.textContent||'').trim(); if(t==='동영상 카드'||t==='재생목록 카드') n++; } } }
  return n;
};
"""

class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, max_size=None, timeout=25, suppress_origin=True)
        self.ws.settimeout(25); self._id = 0
    def cmd(self, method, params=None):
        self._id += 1; mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            m = json.loads(self.ws.recv())   # settimeout 걸려있어 무한hang 방지
            if m.get("id") == mid: return m.get("result", {})
    def js(self, expr):
        r = self.cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        return r.get("result", {}).get("value")
    def click(self, x, y):
        for t in ("mouseMoved", "mousePressed", "mouseReleased"):
            p = {"type": t, "x": x, "y": y, "button": "left"}
            if t != "mouseMoved": p["clickCount"] = 1
            self.cmd("Input.dispatchMouseEvent", p)
    def key(self, k):
        self.cmd("Input.dispatchKeyEvent", {"type": "keyDown", "key": k, "code": k, "windowsVirtualKeyCode": 13 if k == "Enter" else 0})
        self.cmd("Input.dispatchKeyEvent", {"type": "keyUp", "key": k, "code": k, "windowsVirtualKeyCode": 13 if k == "Enter" else 0})
    def shot(self, n):
        r = self.cmd("Page.captureScreenshot", {"format": "png"})
        if r.get("data"): open(f"scratch/yt/{n}.png", "wb").write(base64.b64decode(r["data"])); log("shot " + n)

def inject(c): c.cmd("Runtime.evaluate", {"expression": DEEP_JS})

def main():
    ws = find_ws(VID)
    if not ws: log("edit 페이지 없음"); return
    c = CDP(ws)
    c.cmd("Page.enable"); c.cmd("Runtime.enable"); c.cmd("Network.enable")
    c.cmd("Page.navigate", {"url": f"https://studio.youtube.com/video/{VID}/edit"}); time.sleep(8)
    inject(c); log("네비 완료")

    # 편집기 열기: 피처 '카드' 클릭 + Enter, 검증(최대 3회)
    opened = False
    for attempt in range(3):
        inject(c)
        fc = c.js("__openCardEditor()")
        log(f"[{attempt}] 카드편집기 .click() → {fc}")
        time.sleep(4); inject(c)
        if c.js("__has('재생목록 카드')") or c.js("__has('변경사항 저장 안함')"):
            opened = True; log("편집기 열림 확인"); break
        time.sleep(1)
    c.shot("f_editor")
    if not opened: log("편집기 열기 실패"); return

    for i, s in enumerate(SEARCHES):
        log(f"=== 카드{i+1}: {s} ===")
        c.click(268, 130); time.sleep(1.8)   # + 카드
        c.click(272, 134); time.sleep(3)      # 동영상
        inject(c)
        f = c.js("__focusInput('내 동영상 검색')")
        if f and f.get("found"):
            c.click(f["x"], f["y"]); time.sleep(0.4)
            c.cmd("Input.insertText", {"text": s}); log(f"검색 {s}")
        else:
            c.click(284, 117); time.sleep(0.4); c.cmd("Input.insertText", {"text": s}); log("검색(좌표)")
        time.sleep(3.5); c.shot(f"f_{i+1}_search")
        c.click(328, 240); time.sleep(3.5)    # 결과 타일
        c.shot(f"f_{i+1}_picked")
        inject(c); log(f"카드수={c.js('__cardCount()')}")

    if SAVE:
        inject(c); sv = c.js("__saveBtn()")
        if sv and sv.get("found"): log(f"저장 @{sv['x']},{sv['y']}"); c.click(sv["x"], sv["y"])
        else: log("저장 좌표"); c.click(1062, 72)
        w = c.ws; w.settimeout(1.0); end = time.time()+8; rid=None
        while time.time() < end:
            try: msg = json.loads(w.recv())
            except Exception: continue
            if msg.get("method") == "Network.requestWillBeSent":
                u = msg["params"].get("request", {}).get("url", "")
                if "edit_video" in u:
                    rid = msg["params"]["requestId"]; pd = msg["params"]["request"].get("postData")
                    if pd: open("scratch/yt/edit_video_req.json","w",encoding="utf-8").write(pd); log("★ edit_video 캡처")
        w.settimeout(25); time.sleep(3)
        inject(c)
        cnt = c.js("__cardCount()"); unsaved = c.js("__has('변경사항 저장 안함')")
        log(f"저장후 카드수={cnt}  저장안함표시={unsaved}")
        c.shot("f_saved")
        if rid and not os.path.exists("scratch/yt/edit_video_req.json"):
            r = c.cmd("Network.getRequestPostData", {"requestId": rid})
            open("scratch/yt/edit_video_req.json","w",encoding="utf-8").write(r.get("postData","")); log("★ 캡처(getPostData)")
    log("DONE")

if __name__ == "__main__":
    main()
