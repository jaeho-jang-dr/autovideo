# -*- coding: utf-8 -*-
"""투명컷 검사·표시앱 — 큰 창에서 **사장님이 직접 표시**한다.

★사장님 지시(2026-08-13)
  "투명컷은 하고 나서 내 검사를 받는다."
  "왼편도 가능한 한 크게 보이게, 마우스로 내려 가면서 볼 수 있게."
  "**내가 큰 창에서 표시할 수 있게 해줘.**"

## 쓰는 법
왼쪽 목록에서 고르면 오른쪽 큰 창에 뜬다. **큰 그림 위를 클릭하면 그 자리에 표가
찍히고** 메모를 적을 수 있다. 표는 바로 저장되므로 창을 닫아도 남는다.
감독(Claude)은 `W1_2/_inspect/marks.md` 를 읽어 표시된 곳만 고친다.

  · 그림 클릭      = 그 자리에 표 찍기 (번호가 붙는다)
  · 표 옆 메모칸   = 무엇이 잘못됐는지 한 줄
  · 표 클릭        = 지우기
  · ← / →          = 앞·뒤 컷
  · 배경 단추      = 체커·흰색·검정·초록 (투명한 곳이 어떻게 비치는지 바꿔 본다)
  · ○ 문제없음     = 이 컷은 통과로 표시

    python W1_2/mark_cuts.py            # 8899 포트로 띄운다
    python W1_2/mark_cuts.py 8901       # 포트 지정
"""
import glob
import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SRC = "W1_2/_inspect"                  # inspect_cuts.py 가 구운 검사판
MARKS = os.path.join(SRC, "marks.json")
REPORT = os.path.join(SRC, "marks.md")


def load_marks():
    if os.path.exists(MARKS):
        with open(MARKS, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_marks(d):
    with open(MARKS, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    # 감독이 읽을 보고서
    lines = ["# 투명컷 검사 — 사장님 표시", "",
             "> `mark_cuts.py` 수집. 감독(Claude)은 여기 적힌 것만 고친다.", ""]
    n = 0
    for name in sorted(d):
        rec = d[name]
        if rec.get("ok") and not rec.get("marks"):
            continue
        if not rec.get("marks"):
            continue
        n += 1
        lines.append("## %d. %s" % (n, name))
        for i, m in enumerate(rec["marks"], 1):
            lines.append("  %d) 가로 %.0f%% · 세로 %.0f%%  — %s"
                         % (i, m["x"] * 100, m["y"] * 100, m.get("note") or "(메모 없음)"))
        lines.append("")
    ok = [k for k, v in d.items() if v.get("ok")]
    lines.append("---")
    lines.append("문제없음으로 넘긴 것 %d개" % len(ok))
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


PAGE = u"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>투명컷 검사 — 표시하기</title><style>
*{box-sizing:border-box} body{margin:0;font:15px/1.5 'Malgun Gothic',sans-serif;
 background:#12141a;color:#e6ebf2;height:100vh;display:flex;overflow:hidden}
/* 왼쪽 = 작은 프레임 격자. 휠로 내려간다. 오른쪽 = 큰 창. */
/* ★한 줄에 6개 (사장님 지시 2026-08-13 "한 줄에 6개 정도 크기면 적당하다") */
#leftcol{width:var(--lw,560px);flex:none;display:flex;flex-direction:column;
 border-right:1px solid #2a2f3a;min-height:0}
#lhead{padding:6px 8px;background:#181b22;border-bottom:1px solid #2a2f3a;
 display:flex;gap:6px;align-items:center;font-size:13px;color:#9fb0c4}
#lhead input[type=range]{flex:1}
#left{flex:1;overflow-y:auto;padding:6px;display:grid;gap:6px;
 grid-template-columns:repeat(6,1fr);align-content:start}
#left .it{cursor:pointer;border:2px solid #2a2f3a;border-radius:5px;background:#1b1e26;
 overflow:hidden}
#left .it.sel{border-color:#4da3ff;box-shadow:0 0 0 2px #4da3ff55}
#left .it.done{border-color:#3ec46d} #left .it.bad{border-color:#ff5f5f}
#left img{width:100%;display:block;background:#fff}
#left .nm{font-size:10px;line-height:1.25;padding:2px 3px;color:#8fa0b4;
 word-break:break-all;max-height:26px;overflow:hidden}
#right{flex:1;display:flex;flex-direction:column;min-width:0}
#bar{padding:8px 12px;background:#181b22;border-bottom:1px solid #2a2f3a;
 display:flex;gap:8px;align-items:center;flex-wrap:wrap}
#bar b{font-size:17px} button{background:#252b36;color:#dfe7f0;border:1px solid #39404e;
 border-radius:5px;padding:5px 11px;cursor:pointer;font:inherit}
button:hover{background:#303845} button.on{background:#4da3ff;color:#0a0d12;border-color:#4da3ff}
#stage{flex:1;overflow:auto;display:flex;align-items:flex-start;justify-content:center;padding:12px}
#wrap{position:relative;display:inline-block}
#wrap img{display:block;max-width:100%;height:auto}
.mk{position:absolute;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;
 background:rgba(255,40,40,.85);border:2px solid #fff;color:#fff;font-weight:700;
 display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:14px}
#notes{background:#181b22;border-top:1px solid #2a2f3a;padding:8px 12px;max-height:180px;
 overflow:auto} #notes .row{display:flex;gap:8px;align-items:center;margin-bottom:5px}
#notes .row span{width:28px;text-align:center;color:#ff8a8a;font-weight:700}
#notes input{flex:1;background:#12151b;border:1px solid #333b48;color:#e6ebf2;
 border-radius:4px;padding:5px 8px;font:inherit}
.hint{color:#8a97a8;font-size:13px}
</style></head><body>
<div id="leftcol">
 <div id="lhead"><span>크기</span><input id="tw" type="range" min="360" max="1000" value="560">
  <span id="cnt"></span></div>
 <div id="left"></div>
</div>
<div id="right">
 <div id="bar">
   <b id="title">—</b>
   <span class="hint" id="pos"></span>
   <span style="flex:1"></span>
   <span class="hint">배경</span>
   <button data-bg="checker" class="on">체커</button>
   <button data-bg="#ffffff">흰색</button>
   <button data-bg="#000000">검정</button>
   <button data-bg="#2e7d32">초록</button>
   <button id="ok">○ 문제없음</button>
   <button id="clr">표 지우기</button>
 </div>
 <div id="stage"><div id="wrap"></div></div>
 <div id="notes"><div class="hint">큰 그림을 클릭하면 그 자리에 표가 찍힙니다. 아래에 무엇이 잘못됐는지 적어 주세요.</div></div>
</div>
<script>
const CK="url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2232%22 height=%2232%22><rect width=%2216%22 height=%2216%22 fill=%22%23ffffff%22/><rect x=%2216%22 y=%2216%22 width=%2216%22 height=%2216%22 fill=%22%23ffffff%22/><rect x=%2216%22 width=%2216%22 height=%2216%22 fill=%22%2378bdff%22/><rect y=%2216%22 width=%2216%22 height=%2216%22 fill=%22%2378bdff%22/></svg>')";
let FILES=[], DATA={}, cur=0;
const $=s=>document.querySelector(s);

function paintLeft(){
  const L=$("#left"); L.innerHTML="";
  FILES.forEach((f,i)=>{
    const d=document.createElement("div");
    const rec=DATA[f]||{};
    d.className="it"+(i===cur?" sel":"")+(rec.ok?" done":"")+((rec.marks||[]).length?" bad":"");
    d.innerHTML='<img loading="lazy" src="img/'+encodeURIComponent(f)+'"><div class="nm">'+
      f.replace(/^[pc]_/,"").replace(/\.png$/,"")+'</div>';
    d.onclick=()=>{cur=i;render();};
    L.appendChild(d);
  });
  $("#cnt").textContent=FILES.length+"장";
  const sel=L.querySelector(".sel"); if(sel) sel.scrollIntoView({block:"nearest"});
}
// 슬라이더는 왼쪽 칸 너비를 바꾼다 — 칸 수는 6개로 고정이라 그림이 같이 커진다
$("#tw").oninput=e=>{ $("#leftcol").style.setProperty("--lw", e.target.value+"px"); };
function render(){
  const f=FILES[cur]; const rec=DATA[f]||(DATA[f]={marks:[],ok:false});
  $("#title").textContent=f.replace(/\.png$/,"");
  $("#pos").textContent=(cur+1)+" / "+FILES.length;
  const w=$("#wrap"); w.innerHTML="";
  const im=new Image(); im.src="img/"+encodeURIComponent(f);
  im.onclick=e=>{
    const r=im.getBoundingClientRect();
    rec.marks.push({x:(e.clientX-r.left)/r.width, y:(e.clientY-r.top)/r.height, note:""});
    rec.ok=false; save(); render(); paintLeft();
  };
  w.appendChild(im);
  rec.marks.forEach((m,i)=>{
    const b=document.createElement("div"); b.className="mk"; b.textContent=i+1;
    b.style.left=(m.x*100)+"%"; b.style.top=(m.y*100)+"%";
    b.title="클릭하면 지웁니다";
    b.onclick=ev=>{ev.stopPropagation(); rec.marks.splice(i,1); save(); render(); paintLeft();};
    w.appendChild(b);
  });
  const N=$("#notes"); N.innerHTML="";
  if(!rec.marks.length){
    N.innerHTML='<div class="hint">큰 그림을 클릭하면 그 자리에 표가 찍힙니다.</div>';
  }
  rec.marks.forEach((m,i)=>{
    const row=document.createElement("div"); row.className="row";
    row.innerHTML='<span>'+(i+1)+'</span>';
    const inp=document.createElement("input");
    inp.value=m.note||""; inp.placeholder="무엇이 잘못됐나요 (예: 팔과 몸 사이가 안 뚫렸다)";
    inp.oninput=()=>{m.note=inp.value;}; inp.onchange=save;
    row.appendChild(inp); N.appendChild(row);
  });
  paintLeft();
}
function save(){
  fetch("save",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify(DATA)});
}
document.querySelectorAll("[data-bg]").forEach(b=>b.onclick=()=>{
  document.querySelectorAll("[data-bg]").forEach(x=>x.classList.remove("on"));
  b.classList.add("on");
  const v=b.dataset.bg;
  $("#wrap").style.background = v==="checker" ? CK : v;
});
$("#wrap").style.background=CK;
$("#ok").onclick=()=>{const f=FILES[cur];DATA[f]={marks:[],ok:true};save();
  if(cur<FILES.length-1)cur++; render();};
$("#clr").onclick=()=>{const f=FILES[cur];DATA[f]={marks:[],ok:false};save();render();};
document.onkeydown=e=>{
  if(e.target.tagName==="INPUT")return;
  if(e.key==="ArrowRight"&&cur<FILES.length-1){cur++;render();}
  if(e.key==="ArrowLeft"&&cur>0){cur--;render();}
};
fetch("list").then(r=>r.json()).then(j=>{FILES=j.files;DATA=j.marks||{};render();});
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
            return self._send(200, "text/html; charset=utf-8", PAGE.encode("utf-8"))
        if p == "/list":
            files = [os.path.basename(x) for x in
                     sorted(glob.glob(os.path.join(SRC, "*.png")))]
            body = json.dumps({"files": files, "marks": load_marks()},
                              ensure_ascii=False).encode("utf-8")
            return self._send(200, "application/json; charset=utf-8", body)
        if p.startswith("/img/"):
            name = unquote(p[5:])
            fp = os.path.join(SRC, os.path.basename(name))
            if os.path.exists(fp):
                with open(fp, "rb") as f:
                    return self._send(200, "image/png", f.read())
        self._send(404, "text/plain", b"nope")

    def do_POST(self):
        if self.path.split("?")[0] == "/save":
            n = int(self.headers.get("Content-Length", 0))
            try:
                save_marks(json.loads(self.rfile.read(n).decode("utf-8")))
                return self._send(200, "application/json", b'{"ok":1}')
            except Exception as e:
                return self._send(500, "text/plain", str(e).encode("utf-8"))
        self._send(404, "text/plain", b"nope")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
    n = len(glob.glob(os.path.join(SRC, "*.png")))
    if not n:
        print("검사판이 없다 — 먼저 `python W1_2/inspect_cuts.py --no-view` 를 돌려라")
        return 1
    url = "http://127.0.0.1:%d/" % port
    print("투명컷 검사·표시앱 — %d장\n  %s" % (n, url))
    print("  큰 그림을 클릭해 표를 찍고 메모를 적으십시오.")
    print("  표시한 것은 %s 로 저장됩니다." % REPORT)
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
