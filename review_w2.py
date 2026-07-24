#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""review_growth.py — child_growth 전용 교정 리뷰 도구 (review_server.py의 srt/자체서빙 버전).
왼쪽: 영상 재생(정지 가능) / 오른쪽: 씬 타임라인 + 시점별 교정 메모 입력·저장.
씬은 자막(srt)에서 읽고, 영상은 이 서버가 HTTP Range로 직접 서빙(Astro 불필요).
실행:  python review_growth.py
열기:  http://localhost:8901
수집:  child_growth_science/review_growth_feedback.json  +  .md  (감독이 읽어 교정)
"""
import os, re, json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
CG = os.path.join(ROOT, "hangeul_birth_vowels")
VIDEO = os.path.join(CG, "hangeul_w2_stickman_np_ko_burned.mp4")   # 한글자막 박힌 KO(선희) — 리뷰용
FB_JSON = os.path.join(CG, "review_w2_feedback.json")
FB_MD = os.path.join(CG, "review_w2_feedback.md")
PORT = 8913

def load_scenes():
    p = os.path.join(CG, "hangeul_w2_stickman_np.ko.srt")
    scenes = []
    for i, blk in enumerate(open(p, encoding="utf-8").read().strip().split("\n\n")):
        L = blk.strip().split("\n")
        if len(L) < 3: continue
        m = re.match(r"(\d+):(\d+):([\d,\.]+) --> (\d+):(\d+):([\d,\.]+)", L[1])
        if not m: continue
        f = lambda h, mi, se: int(h)*3600 + int(mi)*60 + float(se.replace(",", "."))
        st = f(m[1], m[2], m[3]); ed = f(m[4], m[5], m[6])
        scenes.append({"seq": i, "start": round(st, 2), "end": round(ed, 2), "cap": " ".join(L[2:])[:50]})
    return scenes

SCENES = load_scenes()

def load_fb():
    if os.path.exists(FB_JSON):
        try: return json.load(open(FB_JSON, encoding="utf-8"))
        except Exception: return []
    return []

def save_fb(fb):
    json.dump(fb, open(FB_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    caps = {s["seq"]: s["cap"] for s in SCENES}
    lines = ["# 교정 피드백 — 한글강의 W2 (선희 나레이션)", "",
             "> review_growth.py 수집. 감독(Claude)이 이 파일을 읽어 해당 씬만 교정한다.", ""]
    for i, f in enumerate(sorted(fb, key=lambda x: x["t"]), 1):
        mm, ss = divmod(int(f["t"]), 60)
        lines.append(f"{i}. **[{mm:02d}:{ss:02d}] 씬{f['scene']}** 「{caps.get(f['scene'],'')}」 — {f['note']}")
    open(FB_MD, "w", encoding="utf-8").write("\n".join(lines) + "\n")

HTML = r"""<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>교정 리뷰 — 한글강의 W2</title>
<style>
*{box-sizing:border-box} body{margin:0;font-family:'Malgun Gothic',sans-serif;background:#15171c;color:#e8e8ea;display:flex;height:100vh;overflow:hidden}
.left{flex:1.45;display:flex;flex-direction:column;padding:14px;min-width:0}
.right{flex:1;display:flex;flex-direction:column;border-left:1px solid #2a2d34;background:#1b1e24;min-width:360px}
h1{font-size:15px;margin:0 0 8px;color:#7fe08a;font-weight:700}
video{width:100%;background:#000;border-radius:10px;max-height:58vh}
.tl{display:flex;flex-wrap:wrap;gap:5px;margin-top:10px;overflow-y:auto;max-height:28vh}
.chip{font-size:11px;padding:4px 7px;border-radius:7px;background:#262a31;color:#b9bcc4;cursor:pointer;border:1px solid transparent;white-space:nowrap;max-width:230px;overflow:hidden;text-overflow:ellipsis}
.chip:hover{background:#30343c} .chip.cur{background:#7fe08a;color:#123;font-weight:700}
.chip.has{border-color:#e0603a}
.panel{padding:14px;display:flex;flex-direction:column;height:100%}
.now{font-size:13px;color:#9aa0ab;margin-bottom:6px}
.now b{color:#7fe08a}
.cap{font-size:14px;color:#cfd3da;background:#11131a;border-radius:8px;padding:8px 10px;margin-bottom:8px;min-height:38px}
textarea{width:100%;height:80px;background:#11131a;color:#eee;border:1px solid #343842;border-radius:8px;padding:10px;font-size:14px;resize:vertical;font-family:inherit}
.btn{margin-top:8px;background:#2b7f43;color:#fff;border:0;border-radius:8px;padding:10px;font-weight:700;cursor:pointer;font-size:14px}
.btn:hover{background:#349955}
.hint{font-size:11px;color:#6b7280;margin-top:4px}
.list{margin-top:14px;overflow-y:auto;flex:1;border-top:1px solid #2a2d34;padding-top:10px}
.item{background:#22262e;border-radius:8px;padding:9px 10px;margin-bottom:8px;font-size:13px;border-left:3px solid #e0603a}
.item .ts{color:#7fe08a;font-weight:700;cursor:pointer}
.item .sc{color:#7f8794;font-size:11px}
.item .nt{margin-top:3px;color:#e3e3e6;white-space:pre-wrap}
.item .del{float:right;color:#7f8794;cursor:pointer;font-size:12px}
.row{display:flex;align-items:center}
.jump{margin-left:auto;font-size:11px;color:#8aa}
</style></head><body>
<div class=left>
  <div class=row><h1>🎬 교정 리뷰 — 한글강의 W2 · 한글의 탄생과 단모음 (선희)</h1>
    <span class=jump>영상 정지 → 메모 입력 → 추가</span></div>
  <video id=vid controls preload=metadata crossorigin=anonymous>
    <source src="/video" type="video/mp4">
    <track id=trk kind=subtitles srclang=ko label="한국어" src="/subs" default>
  </video>
  <div class=tl id=tl></div>
</div>
<div class=right><div class=panel>
  <div class=now>현재 <b id=ct>00:00</b> · <span id=cs>씬0</span></div>
  <div class=cap id=cc></div>
  <textarea id=note placeholder="이 시점 나레이션에서 틀린 점을 적어주세요. (정지 후 입력 → 추가)
예: '센티미터 발음이 이상함', '13을 십삼으로 읽어줘'"></textarea>
  <button class=btn onclick=addNote()>➕ 이 시점에 메모 추가  (Ctrl+Enter)</button>
  <div class=hint>메모는 현재 시점·씬과 함께 자동 저장됩니다. 다 끝나면 감독이 모아서 한 번에 교정합니다.</div>
  <div class=list id=list></div>
</div></div>
<script>
var SCENES=__SCENES__;
var vid=document.getElementById('vid');
function fmt(t){t=Math.floor(t);return String(Math.floor(t/60)).padStart(2,'0')+':'+String(t%60).padStart(2,'0')}
function sceneAt(t){for(var i=0;i<SCENES.length;i++)if(t>=SCENES[i].start&&t<SCENES[i].end)return SCENES[i];return SCENES[SCENES.length-1]||{seq:0,cap:''}}
function buildTL(){var h='';SCENES.forEach(function(s){h+='<span class=chip data-seq='+s.seq+' onclick="seek('+s.start+')" title="'+s.cap.replace(/"/g,'')+'">씬'+s.seq+'</span>'});document.getElementById('tl').innerHTML=h}
function seek(t){vid.currentTime=t+0.05;vid.pause()}
function tick(){var t=vid.currentTime,s=sceneAt(t);document.getElementById('ct').textContent=fmt(t);document.getElementById('cs').textContent='씬'+s.seq;document.getElementById('cc').textContent=s.cap||'';document.querySelectorAll('.chip').forEach(function(e){e.classList.toggle('cur',+e.dataset.seq==s.seq)})}
function render(fb){var h='';var marked={};fb.forEach(function(f){marked[f.scene]=1;h+='<div class=item><span class=del onclick="del('+f.id+')">✕</span><span class=ts onclick="seek('+f.t+')">⏱ '+fmt(f.t)+'</span> <span class=sc>씬'+f.scene+'</span><div class=nt>'+f.note.replace(/</g,'&lt;')+'</div></div>'});document.getElementById('list').innerHTML=h;document.querySelectorAll('.chip').forEach(function(e){e.classList.toggle('has',marked[+e.dataset.seq])})}
function load(){fetch('/api/feedback').then(function(r){return r.json()}).then(render)}
function addNote(){var n=document.getElementById('note').value.trim();if(!n)return;var t=vid.currentTime,s=sceneAt(t);fetch('/api/feedback',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({t:t,note:n,scene:s.seq})}).then(function(r){return r.json()}).then(function(fb){render(fb);document.getElementById('note').value=''})}
function del(id){fetch('/api/feedback/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id})}).then(function(r){return r.json()}).then(render)}
document.getElementById('note').addEventListener('keydown',function(e){if(e.ctrlKey&&e.key=='Enter')addNote()});
// 자막 항상 켜기
vid.addEventListener('loadedmetadata',function(){try{for(var i=0;i<vid.textTracks.length;i++)vid.textTracks[i].mode='showing';}catch(e){}});
setTimeout(function(){try{if(vid.textTracks[0])vid.textTracks[0].mode='showing';}catch(e){}},1200);
buildTL(); load(); setInterval(tick,250);
</script></body></html>"""

def make_handler():
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _send(self, code, body, ctype="application/json", extra=None):
            b = body.encode("utf-8") if isinstance(body, str) else body
            self.send_response(code); self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Cache-Control", "no-store")
            if extra:
                for k, v in extra.items(): self.send_header(k, v)
            self.end_headers(); self.wfile.write(b)

        def _serve_video(self):
            size = os.path.getsize(VIDEO)
            rng = self.headers.get("Range")
            if rng:
                m = re.match(r"bytes=(\d+)-(\d*)", rng)
                s = int(m.group(1)); e = int(m.group(2)) if m.group(2) else size - 1
                e = min(e, size - 1); length = e - s + 1
                self.send_response(206)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Range", f"bytes {s}-{e}/{size}")
                self.send_header("Content-Length", str(length))
                self.end_headers()
                with open(VIDEO, "rb") as f:
                    f.seek(s); remain = length
                    while remain > 0:
                        chunk = f.read(min(1 << 20, remain))
                        if not chunk: break
                        self.wfile.write(chunk); remain -= len(chunk)
            else:
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Length", str(size))
                self.end_headers()
                with open(VIDEO, "rb") as f:
                    while True:
                        chunk = f.read(1 << 20)
                        if not chunk: break
                        self.wfile.write(chunk)

        def do_GET(self):
            if self.path == "/" or self.path.startswith("/index"):
                self._send(200, HTML.replace("__SCENES__", json.dumps(SCENES, ensure_ascii=False)), "text/html; charset=utf-8")
            elif self.path == "/video":
                try: self._serve_video()
                except Exception: pass
            elif self.path == "/subs":
                vtt = os.path.join(CG, "child_growth.ko.vtt")
                data = open(vtt, "rb").read() if os.path.exists(vtt) else b"WEBVTT\n\n"
                self._send(200, data, "text/vtt; charset=utf-8")
            elif self.path == "/api/feedback":
                self._send(200, json.dumps(load_fb(), ensure_ascii=False))
            else:
                self._send(404, "{}")

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or "{}")
            fb = load_fb()
            if self.path == "/api/feedback":
                nid = (max([f["id"] for f in fb]) + 1) if fb else 1
                fb.append({"id": nid, "t": round(float(data["t"]), 2), "note": data["note"], "scene": data.get("scene", 0)})
                save_fb(fb)
            elif self.path == "/api/feedback/delete":
                fb = [f for f in fb if f["id"] != data.get("id")]; save_fb(fb)
            self._send(200, json.dumps(fb, ensure_ascii=False))
    return H

if __name__ == "__main__":
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), make_handler())
    print(f"교정 리뷰 도구 → http://localhost:{PORT}  ({len(SCENES)}씬, 영상 {os.path.basename(VIDEO)})")
    print(f"피드백 수집 → {FB_MD}")
    httpd.serve_forever()
