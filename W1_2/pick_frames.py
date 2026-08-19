# -*- coding: utf-8 -*-
"""프레임 고르기 앱 — 192프레임에서 **쓸 것만 순서대로 골라** 스틸동영상을 만든다.

★사장님 지시(2026-08-13)
  "192프레임 분해해서 내가 클릭하면 선택되고, 선택된 것 표시되게 해 주고,
   또 다시 클릭하면 선택 없어지게 해 주고, 선택한 것이 앞에서부터 번호로 매겨지게."
  "그림 아랫단에 선택할 수 있게 해 주고, 오른편에 큰 그림 보이게 해 주고."

## 왜 필요한가
8초 클립을 3프레임마다 솎아 64컷으로 만들면 **멀쩡한 프레임이 버려지고 뭉개진
프레임이 뽑힌다.** 회전 구간처럼 Flow 가 팔다리를 터뜨리는 대목이 특히 그렇다.
그래서 192장을 다 깔아 놓고 사람이 직접 고른다.

## 쓰는 법
    python W1_2/pick_frames.py forward_roll2          # 8899 포트
    python W1_2/pick_frames.py forward_roll2 8901

  · 아래 격자에서 그림을 클릭 = 고름 (초록 테두리 + 고른 순번이 붙는다)
  · 고른 것을 다시 클릭      = 고르기 취소 (뒤 번호가 자동으로 당겨진다)
  · 오른쪽 큰 창에 마우스가 올라간 그림이 크게 뜬다
  · [저장] 을 누르면 `W1_2/_pick/<키>.picks.json` 에 번호가 저장된다
  · [스틸동영상 만들기] 를 누르면 고른 순서 그대로 `motion6_cuts/<키>` 에 굽는다

번호는 **고른 순서가 아니라 프레임 번호 순**으로 매긴다 — 앞에서부터 1, 2, 3….
"""
import glob
import json
import os
import shutil
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

KEY = sys.argv[1] if len(sys.argv) > 1 else "forward_roll2"
SRC = os.path.join("W1_2/_pick", KEY)
PICKS = os.path.join("W1_2/_pick", KEY + ".picks.json")
OUT_CUT = os.path.join("W1_2/motion6_cuts", KEY)


def load_picks():
    if os.path.exists(PICKS):
        with open(PICKS, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_picks(v):
    with open(PICKS, "w", encoding="utf-8") as f:
        json.dump(sorted(set(v)), f)


def build_cut(picks):
    """고른 프레임을 **번호 순서대로** 스틸동영상 폴더에 굽는다."""
    picks = sorted(set(picks))
    if not picks:
        return 0, "고른 것이 없다"
    if os.path.isdir(OUT_CUT):
        bak = OUT_CUT + "_prev"
        shutil.rmtree(bak, ignore_errors=True)
        shutil.move(OUT_CUT, bak)
    os.makedirs(OUT_CUT, exist_ok=True)
    fs = sorted(glob.glob(os.path.join(SRC, "*.png")))
    by = {}
    for p in fs:
        try:
            by[int(os.path.splitext(os.path.basename(p))[0].split("_")[-1])] = p
        except ValueError:
            pass
    n = 0
    for i, fi in enumerate(picks):
        src = by.get(fi)
        if not src:
            continue
        # 검사판(초록 바탕·이름표)이 아니라 **투명 원본**을 가져와야 한다
        raw = os.path.join(SRC + "_cut", "%s_%03d.png" % (KEY, fi))
        shutil.copy2(raw if os.path.exists(raw) else src,
                     os.path.join(OUT_CUT, "%s_%02d.png" % (KEY, i)))
        n += 1
    return n, "%d컷 → %s" % (n, OUT_CUT)


PAGE = u"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>프레임 고르기 — __KEY__</title><style>
*{box-sizing:border-box} body{margin:0;font:15px/1.5 'Malgun Gothic',sans-serif;
 background:#12141a;color:#e6ebf2;height:100vh;display:flex;flex-direction:column;
 overflow:hidden}
#top{flex:1;display:flex;min-height:0}
#big{flex:1;display:flex;align-items:center;justify-content:center;padding:10px;
 min-width:0;order:2;background:#0e1015}
#big img{max-width:100%;max-height:100%;object-fit:contain}
#side{width:300px;flex:none;order:1;padding:12px;border-right:1px solid #2a2f3a;
 overflow-y:auto}
#bar{padding:8px 12px;background:#181b22;border-top:1px solid #2a2f3a;
 display:flex;gap:8px;align-items:center;flex-wrap:wrap}
#grid{height:46vh;overflow-y:auto;padding:8px;display:grid;gap:5px;
 grid-template-columns:repeat(auto-fill,minmax(var(--tw,100px),1fr));
 align-content:start;background:#161920;border-top:1px solid #2a2f3a}
.it{position:relative;cursor:pointer;border:3px solid #2a2f3a;border-radius:5px;
 overflow:hidden;background:#1b1e26}
.it img{width:100%;display:block}
.it.on{border-color:#3ec46d;box-shadow:0 0 0 2px #3ec46d55}
.it.hi{border-color:#4da3ff}
.no{position:absolute;left:3px;top:3px;background:#3ec46d;color:#06210f;
 font-weight:700;font-size:13px;padding:1px 7px;border-radius:10px}
.fr{position:absolute;right:3px;top:3px;background:#0009;color:#cbd6e4;
 font-size:11px;padding:1px 5px;border-radius:8px}
button{background:#252b36;color:#dfe7f0;border:1px solid #39404e;border-radius:5px;
 padding:6px 13px;cursor:pointer;font:inherit} button:hover{background:#303845}
button.go{background:#3ec46d;color:#06210f;border-color:#3ec46d;font-weight:700}
h3{margin:0 0 8px;font-size:16px} .hint{color:#8a97a8;font-size:13px}
#list{font-size:13px;color:#a9b8c9;word-break:break-all;line-height:1.7}
</style></head><body>
<div id="top">
  <div id="side">
    <h3>__KEY__</h3>
    <div class="hint">아래 격자에서 그림을 <b>클릭</b>하면 골라집니다.<br>
      고른 것을 <b>다시 클릭</b>하면 취소됩니다.<br>
      번호는 <b>프레임 순서</b>대로 다시 매겨집니다.</div>
    <p><b id="cnt">0</b>개 고름</p>
    <div id="list"></div>
  </div>
  <div id="big"><img id="bigimg"></div>
</div>
<div id="bar">
  <span class="hint">크기</span>
  <input id="tw" type="range" min="70" max="260" value="100">
  <button id="clr">전체 취소</button>
  <button id="save">저장</button>
  <button id="mk" class="go">스틸동영상 만들기</button>
  <span id="msg" class="hint"></span>
</div>
<div id="grid"></div>
<script>
let FILES=[], PICK=new Set();
const $=s=>document.querySelector(s);
const fnum=f=>parseInt(f.match(/_(\\d+)\\.png$/)[1],10);

function paint(){
  const g=$("#grid"); g.innerHTML="";
  const ord=[...PICK].sort((a,b)=>a-b);
  FILES.forEach(f=>{
    const n=fnum(f), on=PICK.has(n);
    const d=document.createElement("div");
    d.className="it"+(on?" on":"");
    d.innerHTML='<img loading="lazy" src="img/'+encodeURIComponent(f)+'">'+
      '<div class="fr">'+n+'</div>'+
      (on?'<div class="no">'+(ord.indexOf(n)+1)+'</div>':'');
    d.onclick=()=>{ on?PICK.delete(n):PICK.add(n); paint(); save(); };
    d.onmouseenter=()=>{ $("#bigimg").src="img/"+encodeURIComponent(f);
      document.querySelectorAll(".it.hi").forEach(e=>e.classList.remove("hi"));
      d.classList.add("hi"); };
    g.appendChild(d);
  });
  $("#cnt").textContent=PICK.size;
  $("#list").textContent=ord.join(", ");
}
function save(){ fetch("save",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify([...PICK])}); }
$("#tw").oninput=e=>$("#grid").style.setProperty("--tw",e.target.value+"px");
$("#clr").onclick=()=>{PICK.clear();paint();save();};
$("#save").onclick=()=>{save();$("#msg").textContent="저장했습니다";};
$("#mk").onclick=()=>{ $("#msg").textContent="만드는 중…";
  fetch("build",{method:"POST"}).then(r=>r.json()).then(j=>{
    $("#msg").textContent=j.msg; }); };
fetch("list").then(r=>r.json()).then(j=>{FILES=j.files;PICK=new Set(j.picks);paint();
  if(FILES.length) $("#bigimg").src="img/"+encodeURIComponent(FILES[0]);});
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = self.path.split("?")[0]
        if p in ("/", "/index.html"):
            return self._send(200, "text/html; charset=utf-8",
                              PAGE.replace("__KEY__", KEY).encode("utf-8"))
        if p == "/list":
            files = [os.path.basename(x) for x in
                     sorted(glob.glob(os.path.join(SRC, "*.png")))]
            body = json.dumps({"files": files, "picks": load_picks()}).encode("utf-8")
            return self._send(200, "application/json", body)
        if p.startswith("/img/"):
            fp = os.path.join(SRC, os.path.basename(unquote(p[5:])))
            if os.path.exists(fp):
                with open(fp, "rb") as f:
                    return self._send(200, "image/png", f.read())
        self._send(404, "text/plain", b"nope")

    def do_POST(self):
        p = self.path.split("?")[0]
        if p == "/save":
            n = int(self.headers.get("Content-Length", 0))
            save_picks(json.loads(self.rfile.read(n).decode("utf-8")))
            return self._send(200, "application/json", b'{"ok":1}')
        if p == "/build":
            cnt, msg = build_cut(load_picks())
            print("  [만들기]", msg)
            return self._send(200, "application/json",
                              json.dumps({"n": cnt, "msg": msg},
                                         ensure_ascii=False).encode("utf-8"))
        self._send(404, "text/plain", b"nope")


def main():
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8899
    n = len(glob.glob(os.path.join(SRC, "*.png")))
    if not n:
        print("검사판이 없다 — 먼저 프레임을 뽑아라:", SRC)
        return 1
    url = "http://127.0.0.1:%d/" % port
    print("프레임 고르기 — %s · %d장\n  %s" % (KEY, n, url))
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
