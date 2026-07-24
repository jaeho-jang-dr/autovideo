# -*- coding: utf-8 -*-
"""순수 CDP 동영상 카드 자동화(node/Playwright 무관, hang 없음).
shadow DOM 관통 JS로 요소 좌표 탐색 → Input.dispatchMouseEvent 클릭 → edit_video 캡처.
사용: python cdp_card.py <VID> <검색어> [<검색어2> ...] [--save]"""
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

# shadow DOM 관통 헬퍼 (페이지에 주입)
DEEP_JS = r"""
window.__allEls = function(){
  const out=[]; const stack=[document];
  while(stack.length){ const root=stack.pop();
    for(const e of root.querySelectorAll('*')){ out.push(e); if(e.shadowRoot) stack.push(e.shadowRoot); } }
  return out;
};
// 클릭가능 요소를 접근성이름(aria-label 우선, 없으면 정확한 텍스트)으로 탐색 + 화면 안으로
window.__findClickable = function(name, minX, maxX){
  minX=minX||0; maxX=maxX||99999;
  const clickTags=['button','ytcp-button','tp-yt-paper-button','tp-yt-paper-icon-button','ytcp-icon-button'];
  let cand=null;
  for(const e of window.__allEls()){
    const aria=(e.getAttribute&&e.getAttribute('aria-label'))||'';
    const role=(e.getAttribute&&e.getAttribute('role'))||'';
    const tag=(e.tagName||'').toLowerCase();
    const isClick = clickTags.indexOf(tag)>=0 || role==='button' || role==='menuitem' || role==='option';
    const txt=(e.textContent||'').trim();
    const nameMatch = aria===name || (isClick && txt===name);
    if(nameMatch){
      const r=e.getBoundingClientRect();
      if(r.x>=minX&&r.x<=maxX){ cand=e; if(r.width>0&&r.height>0){ e.scrollIntoView({block:'center'}); const r2=e.getBoundingClientRect(); return {x:Math.round(r2.x+r2.width/2), y:Math.round(r2.y+r2.height/2), found:true, tag}; } }
    }
  }
  return {found:false};
};
window.__deepLeafCenter = function(text, minX, maxX){
  minX = minX||0; maxX = maxX||99999;
  for(const e of window.__allEls()){
    if(e.children.length===0){
      const t=(e.textContent||'').trim();
      if(t===text){ const r=e.getBoundingClientRect();
        if(r.width>0&&r.height>0&&r.x>=minX&&r.x<=maxX) return {x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2), found:true}; }
    }
  }
  return {found:false};
};
window.__deepInputFocus = function(ph){
  const stack=[document];
  while(stack.length){
    const root=stack.pop();
    for(const e of root.querySelectorAll('input, textarea')){
      const a=(e.getAttribute('placeholder')||e.getAttribute('aria-label')||'');
      if(a.indexOf(ph)>=0){ e.focus(); const r=e.getBoundingClientRect(); return {x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2), found:true}; }
    }
    for(const e of root.querySelectorAll('*')) if(e.shadowRoot) stack.push(e.shadowRoot);
  }
  return {found:false};
};
window.__firstVideoTile = function(){
  const stack=[document];
  while(stack.length){
    const root=stack.pop();
    for(const e of root.querySelectorAll('*')){
      if(e.shadowRoot) stack.push(e.shadowRoot);
      const tag=(e.tagName||'').toLowerCase();
      if(tag.indexOf('video-select')>=0 || tag.indexOf('video-picker-item')>=0 || tag.indexOf('entity-card')>=0){
        const r=e.getBoundingClientRect();
        if(r.width>60&&r.height>60&&r.y>150) return {x:Math.round(r.x+r.width/2), y:Math.round(r.y+40), found:true, tag};
      }
    }
  }
  return {found:false};
};
"""

class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, max_size=None, timeout=30, suppress_origin=True)
        self._id = 0; self.buf = []
    def send(self, method, params=None):
        self._id += 1; mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid: return msg.get("result", {})
            else: self.buf.append(msg)
    def evaljs(self, expr):
        r = self.send("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        return r.get("result", {}).get("value")
    def click(self, x, y):
        for t in ("mouseMoved", "mousePressed", "mouseReleased"):
            p = {"type": t, "x": x, "y": y, "button": "left"}
            if t != "mouseMoved": p["clickCount"] = 1
            self.send("Input.dispatchMouseEvent", p)
    def type_text(self, s):
        self.send("Input.insertText", {"text": s})
    def shot(self, n):
        r = self.send("Page.captureScreenshot", {"format": "png"})
        if r.get("data"): open(f"scratch/yt/{n}.png","wb").write(base64.b64decode(r["data"])); log("shot "+n)
    def deep(self, text, minx=0, maxx=99999):
        return self.evaljs(f"__deepLeafCenter({json.dumps(text)},{minx},{maxx})")
    def click_clickable(self, name, minx=0, maxx=99999, label=""):
        c = self.evaljs(f"__findClickable({json.dumps(name)},{minx},{maxx})")
        if c and c.get("found"):
            self.click(c["x"], c["y"]); log(f"클릭 '{label or name}' @{c['x']},{c['y']} ({c.get('tag')})"); return True
        # 폴백: leaf 텍스트
        c = self.deep(name, minx, maxx)
        if c and c.get("found"):
            self.click(c["x"], c["y"]); log(f"클릭(txt) '{label or name}' @{c['x']},{c['y']}"); return True
        log(f"못찾음 '{label or name}'"); return False
    def click_deep(self, text, minx=0, maxx=99999, label=""):
        return self.click_clickable(text, minx, maxx, label)

def main():
    ws = find_ws(VID)
    if not ws: log("edit 페이지 없음"); return
    c = CDP(ws)
    c.send("Page.enable"); c.send("Runtime.enable"); c.send("Network.enable")
    # 페이지 새로고침해 깨끗한 상태
    c.send("Page.navigate", {"url": f"https://studio.youtube.com/video/{VID}/edit"}); time.sleep(7)
    c.send("Runtime.evaluate", {"expression": DEEP_JS})
    log("CDP 준비 완료")

    # 1) 카드 편집기 열기 (피처 버튼 aria-label='카드', 화면밖이면 scrollIntoView)
    if not c.click_clickable("카드", 0, 99999, "카드버튼"):
        c.shot("cc_nocard"); return
    time.sleep(4); c.send("Runtime.evaluate", {"expression": DEEP_JS}); c.shot("cc_editor")

    for i, search in enumerate(SEARCHES):
        log(f"=== 카드{i+1}: {search} ===")
        c.send("Runtime.evaluate", {"expression": DEEP_JS})
        c.click_clickable("카드 추가", 0, 700, "+카드"); time.sleep(2)
        c.click(272, 134); time.sleep(3)   # 동영상 옵션(실측)
        c.send("Runtime.evaluate", {"expression": DEEP_JS})
        f = c.evaljs(f"__deepInputFocus('내 동영상 검색')")
        if f and f.get("found"):
            c.click(f["x"], f["y"]); time.sleep(0.4); c.type_text(search); log("검색 "+search)
        else: log("검색창 못찾음")
        time.sleep(3.5); c.shot(f"cc_{i+1}_search")
        # 결과 첫 타일 클릭
        c.send("Runtime.evaluate", {"expression": DEEP_JS})
        c.click(440, 284)   # 실측 첫 타일 위치
        log("결과 클릭"); time.sleep(3.5); c.shot(f"cc_{i+1}_picked")

    # 저장 + edit_video 캡처
    if SAVE:
        c.click_deep("저장", 1250, 1600, "저장") or c.click(1429, 97)
        # edit_video 캡처
        c.ws.settimeout(1.0); end = time.time()+8; rid=None
        while time.time() < end:
            try: msg = json.loads(c.ws.recv())
            except Exception: continue
            if msg.get("method")=="Network.requestWillBeSent":
                p=msg["params"]; u=p.get("request",{}).get("url","")
                if "edit_video" in u:
                    rid=p["requestId"]; pd=p["request"].get("postData")
                    open("scratch/yt/edit_video_url.txt","w",encoding="utf-8").write(u)
                    if pd: open("scratch/yt/edit_video_req.json","w",encoding="utf-8").write(pd); log("★ postData 캡처")
        c.ws.settimeout(30); time.sleep(3); c.shot("cc_saved")
        if rid and not os.path.exists("scratch/yt/edit_video_req.json"):
            r=c.send("Network.getRequestPostData",{"requestId":rid})
            open("scratch/yt/edit_video_req.json","w",encoding="utf-8").write(r.get("postData","")); log("★ getPostData 캡처")
    log("DONE")

if __name__ == "__main__":
    main()
