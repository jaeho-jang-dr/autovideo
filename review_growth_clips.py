#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""review_growth_clips.py — 아이 키 성장(v2) 교정 리뷰 (클립 스트립 버전).
상단: 메인 영상(자막 항상 켜짐) / 그 아래: 씬 클립(scene_N.mp4)이 하나하나 나타나는 스트립.
클립 클릭 → 메인 영상이 그 씬으로 이동 + 클립 자체도 미리보기 재생. 우측: 시점별 교정 메모.
실행:  python review_growth_clips.py   →   http://localhost:8903
수집:  child_growth_science/review_growth_feedback.json  +  .md
"""
import os, re, json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
CG = os.path.join(ROOT, "child_growth_science")
CLIPDIR = os.path.join(ROOT, "child_growth")            # 개별 씬 클립 scene_N.mp4
VIDEO = os.path.join(CG, "child_growth_dub.mp4")         # KO=Dae 기본트랙 (v3 · scene9 수정본)
SUBVTT = os.path.join(CG, "child_growth_v3.ko.vtt")
FB_JSON = os.path.join(CG, "review_growth_feedback.json")
FB_MD = os.path.join(CG, "review_growth_feedback.md")
PORT = 8909

def load_scenes():
    p = os.path.join(CG, "child_growth.ko.srt")
    scenes = []
    for i, blk in enumerate(open(p, encoding="utf-8").read().strip().split("\n\n")):
        L = blk.strip().split("\n")
        if len(L) < 3: continue
        m = re.match(r"(\d+):(\d+):([\d,\.]+) --> (\d+):(\d+):([\d,\.]+)", L[1])
        if not m: continue
        f = lambda h, mi, se: int(h)*3600 + int(mi)*60 + float(se.replace(",", "."))
        st = f(m[1], m[2], m[3]); ed = f(m[4], m[5], m[6])
        clip = os.path.join(CLIPDIR, f"scene_{i}.mp4")
        scenes.append({"seq": i, "start": round(st, 2), "end": round(ed, 2),
                       "cap": " ".join(L[2:])[:60], "hasclip": os.path.exists(clip)})
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
    lines = ["# 교정 피드백 — 우리 아이 키 얼마나 클까? (v2 · 클립 리뷰)", "",
             "> review_growth_clips.py 수집. 감독(Claude)이 이 파일을 읽어 해당 씬만 교정한다.", ""]
    for i, f in enumerate(sorted(fb, key=lambda x: x["t"]), 1):
        mm, ss = divmod(int(f["t"]), 60)
        lines.append(f"{i}. **[{mm:02d}:{ss:02d}] 씬{f['scene']}** 「{caps.get(f['scene'],'')}」 — {f['note']}")
    open(FB_MD, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def _serve_file_range(handler, path, ctype="video/mp4"):
    size = os.path.getsize(path)
    rng = handler.headers.get("Range")
    if rng:
        m = re.match(r"bytes=(\d+)-(\d*)", rng)
        s = int(m.group(1)); e = int(m.group(2)) if m.group(2) else size - 1
        e = min(e, size - 1); length = e - s + 1
        handler.send_response(206)
        handler.send_header("Content-Type", ctype)
        handler.send_header("Accept-Ranges", "bytes")
        handler.send_header("Content-Range", f"bytes {s}-{e}/{size}")
        handler.send_header("Content-Length", str(length)); handler.end_headers()
        with open(path, "rb") as f:
            f.seek(s); remain = length
            while remain > 0:
                chunk = f.read(min(1 << 20, remain))
                if not chunk: break
                handler.wfile.write(chunk); remain -= len(chunk)
    else:
        handler.send_response(200)
        handler.send_header("Content-Type", ctype)
        handler.send_header("Accept-Ranges", "bytes")
        handler.send_header("Content-Length", str(size)); handler.end_headers()
        with open(path, "rb") as f:
            while True:
                chunk = f.read(1 << 20)
                if not chunk: break
                handler.wfile.write(chunk)

HTML = r"""<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>교정 리뷰 — 아이 키 성장 (v2 · 클립)</title>
<style>
*{box-sizing:border-box} body{margin:0;font-family:'Malgun Gothic',sans-serif;background:#15171c;color:#e8e8ea;display:flex;height:100vh;overflow:hidden}
.left{flex:1.55;display:flex;flex-direction:column;padding:14px;min-width:0}
.right{flex:1;display:flex;flex-direction:column;border-left:1px solid #2a2d34;background:#1b1e24;min-width:360px}
h1{font-size:15px;margin:0 0 8px;color:#7fe08a;font-weight:700}
video#vid{width:100%;background:#000;border-radius:10px;max-height:46vh}
.striphead{font-size:12px;color:#8b93a0;margin:10px 2px 6px}
.strip{display:flex;flex-wrap:wrap;gap:8px;overflow-y:auto;flex:1;padding:2px;align-content:flex-start}
.clip{width:150px;background:#20242b;border-radius:9px;overflow:hidden;cursor:pointer;border:2px solid transparent;flex:0 0 auto}
.clip:hover{border-color:#3a4552} .clip.cur{border-color:#7fe08a} .clip.has{border-color:#e0603a}
.clip video{width:100%;height:84px;object-fit:cover;background:#000;display:block}
.clip .cl{font-size:11px;padding:4px 6px;color:#c3c7cf;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.clip .cl b{color:#7fe08a}
.clip .noc{height:84px;display:flex;align-items:center;justify-content:center;color:#5a6270;font-size:11px;background:#181b21}
.panel{padding:14px;display:flex;flex-direction:column;height:100%}
.now{font-size:13px;color:#9aa0ab;margin-bottom:6px}.now b{color:#7fe08a}
.cap{font-size:14px;color:#cfd3da;background:#11131a;border-radius:8px;padding:8px 10px;margin-bottom:8px;min-height:38px}
textarea{width:100%;height:80px;background:#11131a;color:#eee;border:1px solid #343842;border-radius:8px;padding:10px;font-size:14px;resize:vertical;font-family:inherit}
.btn{margin-top:8px;background:#2b7f43;color:#fff;border:0;border-radius:8px;padding:10px;font-weight:700;cursor:pointer;font-size:14px}.btn:hover{background:#349955}
.hint{font-size:11px;color:#6b7280;margin-top:4px}
.list{margin-top:14px;overflow-y:auto;flex:1;border-top:1px solid #2a2d34;padding-top:10px}
.item{background:#22262e;border-radius:8px;padding:9px 10px;margin-bottom:8px;font-size:13px;border-left:3px solid #e0603a}
.item .ts{color:#7fe08a;font-weight:700;cursor:pointer}.item .sc{color:#7f8794;font-size:11px}
.item .nt{margin-top:3px;color:#e3e3e6;white-space:pre-wrap}.item .del{float:right;color:#7f8794;cursor:pointer;font-size:12px}
.row{display:flex;align-items:center}.jump{margin-left:auto;font-size:11px;color:#8aa}
</style></head><body>
<div class=left>
  <div class=row><h1>🎬 교정 리뷰 — 우리 아이 키 얼마나 클까? (v2 · 씬 클립)</h1>
    <span class=jump>클립 클릭 → 그 씬으로 이동 · 정지 후 메모</span></div>
  <video id=vid controls preload=metadata crossorigin=anonymous>
    <source src="/video" type="video/mp4">
    <track id=trk kind=subtitles srclang=ko label="한국어" src="/subs" default>
  </video>
  <div class=striphead>▼ 씬 클립 (스크롤하면 하나씩 나타남 · 클릭=그 씬 재생/미리보기 · 주황테=메모있음)</div>
  <div class=strip id=strip></div>
</div>
<div class=right><div class=panel>
  <div class=now>현재 <b id=ct>00:00</b> · <span id=cs>씬0</span></div>
  <div class=cap id=cc></div>
  <textarea id=note placeholder="이 씬에서 고칠 점을 적어주세요. (클립 클릭 → 정지 → 입력 → 추가)
예: '자막 오타', '이 장면 다시 생성', '나레이션 13을 십삼으로'"></textarea>
  <button class=btn onclick=addNote()>➕ 이 시점에 메모 추가  (Ctrl+Enter)</button>
  <div class=hint>메모는 현재 시점·씬과 함께 저장됩니다. 다 끝나면 감독이 모아 해당 씬만 교정합니다.</div>
  <div class=list id=list></div>
</div></div>
<script>
var SCENES=__SCENES__;
var vid=document.getElementById('vid');
function fmt(t){t=Math.floor(t);return String(Math.floor(t/60)).padStart(2,'0')+':'+String(t%60).padStart(2,'0')}
function sceneAt(t){for(var i=0;i<SCENES.length;i++)if(t>=SCENES[i].start&&t<SCENES[i].end)return SCENES[i];return SCENES[SCENES.length-1]||{seq:0,cap:''}}
function buildStrip(){var h='';SCENES.forEach(function(s){
  var inner = s.hasclip ? '<video data-src="/clip/'+s.seq+'" muted preload=none loop playsinline></video>'
                        : '<div class=noc>클립없음</div>';
  h+='<div class=clip data-seq='+s.seq+' onclick="onClip('+s.seq+')" title="'+s.cap.replace(/"/g,'')+'">'
     +inner+'<div class=cl><b>씬'+s.seq+'</b> '+s.cap.replace(/</g,'&lt;')+'</div></div>';
});document.getElementById('strip').innerHTML=h; lazy();}
// 스크롤 시 보이는 클립만 첫 프레임 로드 (하나씩 나타남)
function lazy(){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var v=e.target.querySelector('video[data-src]');if(v&&!v.src){v.src=v.dataset.src;v.preload='metadata';}io.unobserve(e.target);}})},{root:document.getElementById('strip'),rootMargin:'120px'});document.querySelectorAll('.clip').forEach(function(c){io.observe(c)});}
function seek(t){vid.currentTime=t+0.05;vid.pause()}
var lastTile=null;
function onClip(seq){var s=SCENES.find(function(x){return x.seq==seq});if(!s)return;seek(s.start);
  var tile=document.querySelector('.clip[data-seq="'+seq+'"]');
  if(lastTile&&lastTile!==tile){var pv=lastTile.querySelector('video');if(pv){pv.pause();}}
  lastTile=tile; var v=tile.querySelector('video[data-src],video');
  if(v){if(!v.src&&v.dataset.src){v.src=v.dataset.src;} try{v.currentTime=0;v.play();}catch(e){}}
}
function tick(){var t=vid.currentTime,s=sceneAt(t);document.getElementById('ct').textContent=fmt(t);document.getElementById('cs').textContent='씬'+s.seq;document.getElementById('cc').textContent=s.cap||'';
  document.querySelectorAll('.clip').forEach(function(e){e.classList.toggle('cur',+e.dataset.seq==s.seq)});}
function render(fb){var h='';var marked={};fb.forEach(function(f){marked[f.scene]=1;h+='<div class=item><span class=del onclick="del('+f.id+')">✕</span><span class=ts onclick="seek('+f.t+')">⏱ '+fmt(f.t)+'</span> <span class=sc>씬'+f.scene+'</span><div class=nt>'+f.note.replace(/</g,'&lt;')+'</div></div>'});document.getElementById('list').innerHTML=h;document.querySelectorAll('.clip').forEach(function(e){e.classList.toggle('has',marked[+e.dataset.seq])});}
function load(){fetch('/api/feedback').then(function(r){return r.json()}).then(render)}
function addNote(){var n=document.getElementById('note').value.trim();if(!n)return;var t=vid.currentTime,s=sceneAt(t);fetch('/api/feedback',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({t:t,note:n,scene:s.seq})}).then(function(r){return r.json()}).then(function(fb){render(fb);document.getElementById('note').value=''})}
function del(id){fetch('/api/feedback/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id})}).then(function(r){return r.json()}).then(render)}
document.getElementById('note').addEventListener('keydown',function(e){if(e.ctrlKey&&e.key=='Enter')addNote()});
vid.addEventListener('loadedmetadata',function(){try{for(var i=0;i<vid.textTracks.length;i++)vid.textTracks[i].mode='showing';}catch(e){}});
setTimeout(function(){try{if(vid.textTracks[0])vid.textTracks[0].mode='showing';}catch(e){}},1200);
buildStrip(); load(); setInterval(tick,250);
</script></body></html>"""

def make_handler():
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _send(self, code, body, ctype="application/json", extra=None):
            b = body.encode("utf-8") if isinstance(body, str) else body
            self.send_response(code); self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b))); self.send_header("Cache-Control", "no-store")
            if extra:
                for k, v in extra.items(): self.send_header(k, v)
            self.end_headers(); self.wfile.write(b)

        def do_GET(self):
            if self.path == "/" or self.path.startswith("/index"):
                self._send(200, HTML.replace("__SCENES__", json.dumps(SCENES, ensure_ascii=False)), "text/html; charset=utf-8")
            elif self.path == "/video":
                try: _serve_file_range(self, VIDEO)
                except Exception: pass
            elif self.path.startswith("/clip/"):
                try:
                    n = int(self.path.split("/clip/")[1].split("?")[0])
                    cp = os.path.join(CLIPDIR, f"scene_{n}.mp4")
                    if os.path.exists(cp): _serve_file_range(self, cp)
                    else: self._send(404, "{}")
                except Exception: pass
            elif self.path == "/subs":
                data = open(SUBVTT, "rb").read() if os.path.exists(SUBVTT) else b"WEBVTT\n\n"
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
    nclip = sum(1 for s in SCENES if s["hasclip"])
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), make_handler())
    print(f"교정 리뷰(클립) → http://localhost:{PORT}  ({len(SCENES)}씬, 클립 {nclip}개, 영상 {os.path.basename(VIDEO)})")
    print(f"피드백 수집 → {FB_MD}")
    httpd.serve_forever()
