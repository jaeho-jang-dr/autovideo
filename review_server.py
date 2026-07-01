#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
review_server.py — 영상 교정 리뷰 도구. 영상을 보며 정지한 시점에 교정 메모를 입력하면
서버가 (타임스탬프 + 씬번호 + 메모)를 파일로 수집한다. Claude(감독)가 그 파일을 읽어 정확히 교정.

왼쪽: 영상 플레이어 / 오른쪽: 씬 타임라인 + 피드백 입력·목록.
영상은 Astro 데브서버(localhost:4321/docs/...)에서 range 지원으로 서빙. 이 서버는 HTML + 피드백 저장만.

실행:  python review_server.py --episode KO-W02 --prefix hangeul_w2_stickman --log scratch/_render_w2_ko.log
열기:  http://localhost:8900
수집:  hangeul_birth_vowels/review_<EP>_feedback.json  +  .md  (감독이 읽음)
"""
import os
import re
import sys
import json
import argparse
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")


def load_scenes(ep, logpath):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT seq, image_prompt, duration_sec, script_kr FROM scenes WHERE episode=? ORDER BY seq", (ep,)).fetchall()
    con.close()
    caps = {}
    for r in rows:
        try:
            caps[r["seq"]] = json.loads(r["image_prompt"]).get("cap_ko", "")
        except Exception:
            caps[r["seq"]] = ""
    # 실제 렌더 길이(로그) 우선, 없으면 DB 계획 길이
    durs = {}
    if logpath and os.path.exists(os.path.join(ROOT, logpath)):
        txt = open(os.path.join(ROOT, logpath), encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r"S\s*(\d+):\s*dur=([0-9.]+)s", txt):
            durs[int(m.group(1))] = float(m.group(2))
    scenes, t = [], 0.0
    for r in rows:
        d = durs.get(r["seq"], r["duration_sec"] or 12)
        scenes.append({"seq": r["seq"], "start": round(t, 2), "end": round(t + d, 2),
                       "cap": caps.get(r["seq"], ""), "dur": round(d, 1)})
        t += d
    return scenes


def make_handler(cfg):
    fb_json = os.path.join(ROOT, "hangeul_birth_vowels", f"review_{cfg['ep']}_feedback.json")
    fb_md = os.path.join(ROOT, "hangeul_birth_vowels", f"review_{cfg['ep']}_feedback.md")

    def load_fb():
        if os.path.exists(fb_json):
            try:
                return json.load(open(fb_json, encoding="utf-8"))
            except Exception:
                return []
        return []

    def scene_at(t):
        for s in cfg["scenes"]:
            if s["start"] <= t < s["end"]:
                return s["seq"], s["cap"]
        return (cfg["scenes"][-1]["seq"], cfg["scenes"][-1]["cap"]) if cfg["scenes"] else (0, "")

    def save_fb(fb):
        json.dump(fb, open(fb_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        lines = [f"# 교정 피드백 — {cfg['ep']} ({cfg['title']})", "",
                 "> review_server.py 수집. 감독(Claude)이 이 파일을 읽어 교정한다.", ""]
        for i, f in enumerate(fb, 1):
            mm, ss = divmod(int(f["t"]), 60)
            lines.append(f"{i}. **[{mm:02d}:{ss:02d}] S{f['scene']} 「{f['cap']}」** — {f['note']}")
        open(fb_md, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    HTML = r"""<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>교정 리뷰 — __TITLE__</title>
<style>
*{box-sizing:border-box} body{margin:0;font-family:'Malgun Gothic',sans-serif;background:#15171c;color:#e8e8ea;display:flex;height:100vh;overflow:hidden}
.left{flex:1.45;display:flex;flex-direction:column;padding:14px;min-width:0}
.right{flex:1;display:flex;flex-direction:column;border-left:1px solid #2a2d34;background:#1b1e24;min-width:340px}
h1{font-size:15px;margin:0 0 8px;color:#cdb27a;font-weight:700}
video{width:100%;background:#000;border-radius:10px;max-height:60vh}
.tl{display:flex;flex-wrap:wrap;gap:5px;margin-top:10px;overflow-y:auto;max-height:26vh}
.chip{font-size:11px;padding:4px 7px;border-radius:7px;background:#262a31;color:#b9bcc4;cursor:pointer;border:1px solid transparent;white-space:nowrap}
.chip:hover{background:#30343c} .chip.cur{background:#cdb27a;color:#1a1a1a;font-weight:700}
.panel{padding:14px;display:flex;flex-direction:column;height:100%}
.now{font-size:13px;color:#9aa0ab;margin-bottom:6px}
.now b{color:#cdb27a}
textarea{width:100%;height:80px;background:#11131a;color:#eee;border:1px solid #343842;border-radius:8px;padding:10px;font-size:14px;resize:vertical;font-family:inherit}
.btn{margin-top:8px;background:#cdb27a;color:#1a1a1a;border:0;border-radius:8px;padding:10px;font-weight:700;cursor:pointer;font-size:14px}
.btn:hover{background:#d8bf8a}
.hint{font-size:11px;color:#6b7280;margin-top:4px}
.list{margin-top:14px;overflow-y:auto;flex:1;border-top:1px solid #2a2d34;padding-top:10px}
.item{background:#22262e;border-radius:8px;padding:9px 10px;margin-bottom:8px;font-size:13px;border-left:3px solid #cdb27a}
.item .ts{color:#cdb27a;font-weight:700;cursor:pointer}
.item .sc{color:#7f8794;font-size:11px}
.item .nt{margin-top:3px;color:#e3e3e6;white-space:pre-wrap}
.item .del{float:right;color:#7f8794;cursor:pointer;font-size:12px}
.langs{margin-left:auto;display:flex;gap:6px}
.lang{font-size:12px;padding:3px 9px;border-radius:6px;background:#262a31;color:#b9bcc4;cursor:pointer;border:1px solid transparent}
.lang.cur{background:#3a3f49;color:#fff;border-color:#cdb27a}
.row{display:flex;align-items:center}
</style></head><body>
<div class=left>
  <div class=row><h1>🎬 교정 리뷰 — __TITLE__</h1>
    <div class=langs><span class="lang cur" data-l=ko onclick="setLang('ko')">한국어</span><span class=lang data-l=en onclick="setLang('en')">English</span></div></div>
  <video id=vid controls preload=metadata></video>
  <div class=tl id=tl></div>
</div>
<div class=right><div class=panel>
  <div class=now>현재 <b id=ct>00:00</b> · <span id=cs>S1</span> <span id=cc style=color:#9aa0ab></span></div>
  <textarea id=note placeholder="이 시점에서 고칠 점을 적어주세요. (영상 정지 후 입력 → 추가)
예: 'ㄴ 빨간점이 입술 위치에 있다. 잇몸 쪽으로 옮겨'"></textarea>
  <button class=btn onclick=addNote()>➕ 이 시점에 메모 추가  (Ctrl+Enter)</button>
  <div class=hint>메모는 자동으로 현재 시점·씬과 함께 저장됩니다. 감독이 모아서 한 번에 교정합니다.</div>
  <div class=list id=list></div>
</div></div>
<script>
var SCENES=__SCENES__, VID={ko:'__VKO__',en:'__VEN__'}, lang='ko';
var vid=document.getElementById('vid');
function fmt(t){t=Math.floor(t);return String(Math.floor(t/60)).padStart(2,'0')+':'+String(t%60).padStart(2,'0')}
function sceneAt(t){for(var i=0;i<SCENES.length;i++)if(t>=SCENES[i].start&&t<SCENES[i].end)return SCENES[i];return SCENES[SCENES.length-1]||{seq:0,cap:''}}
function setLang(l){lang=l;document.querySelectorAll('.lang').forEach(function(e){e.classList.toggle('cur',e.dataset.l==l)});var t=vid.currentTime;vid.src=VID[l];vid.currentTime=t||0}
function buildTL(){var h='';SCENES.forEach(function(s){h+='<span class=chip data-seq='+s.seq+' onclick="seek('+s.start+')">S'+s.seq+' '+s.cap+'</span>'});document.getElementById('tl').innerHTML=h}
function seek(t){vid.currentTime=t+0.05;vid.pause()}
function tick(){var t=vid.currentTime,s=sceneAt(t);document.getElementById('ct').textContent=fmt(t);document.getElementById('cs').textContent='S'+s.seq;document.getElementById('cc').textContent=s.cap||'';document.querySelectorAll('.chip').forEach(function(e){e.classList.toggle('cur',+e.dataset.seq==s.seq)})}
function render(fb){var h='';fb.forEach(function(f){h+='<div class=item><span class=del onclick="del('+f.id+')">✕</span><span class=ts onclick="seek('+f.t+')">⏱ '+fmt(f.t)+'</span> <span class=sc>S'+f.scene+' '+f.cap+'</span><div class=nt>'+f.note.replace(/</g,'&lt;')+'</div></div>'});document.getElementById('list').innerHTML=h}
function load(){fetch('/api/feedback').then(function(r){return r.json()}).then(render)}
function addNote(){var n=document.getElementById('note').value.trim();if(!n)return;var t=vid.currentTime,s=sceneAt(t);fetch('/api/feedback',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({t:t,note:n,scene:s.seq,cap:s.cap})}).then(function(r){return r.json()}).then(function(fb){render(fb);document.getElementById('note').value=''})}
function del(id){fetch('/api/feedback/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id})}).then(function(r){return r.json()}).then(render)}
document.getElementById('note').addEventListener('keydown',function(e){if(e.ctrlKey&&e.key=='Enter')addNote()});
vid.src=VID.ko; buildTL(); load(); setInterval(tick,250);
</script></body></html>"""

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype="application/json"):
            b = body.encode("utf-8") if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            if self.path == "/" or self.path.startswith("/index"):
                html = (HTML.replace("__TITLE__", cfg["title"])
                        .replace("__SCENES__", json.dumps(cfg["scenes"], ensure_ascii=False))
                        .replace("__VKO__", cfg["vko"]).replace("__VEN__", cfg["ven"]))
                self._send(200, html, "text/html; charset=utf-8")
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
                fb.append({"id": nid, "t": round(float(data["t"]), 2), "note": data["note"],
                           "scene": data.get("scene", 0), "cap": data.get("cap", "")})
                save_fb(fb)
            elif self.path == "/api/feedback/delete":
                fb = [f for f in fb if f["id"] != data.get("id")]
                save_fb(fb)
            self._send(200, json.dumps(fb, ensure_ascii=False))

    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", default="KO-W02")
    ap.add_argument("--prefix", default="hangeul_w2_stickman")
    ap.add_argument("--log", default="scratch/_render_w2_ko.log")
    ap.add_argument("--port", type=int, default=8900)
    ap.add_argument("--astro", default="http://localhost:4321")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    title = con.execute("SELECT title_kr FROM episodes WHERE code=?", (args.episode,)).fetchone()
    con.close()
    def vurl(lang):   # 캐시 무력화: 파일 수정시각을 버전으로 붙여 항상 새 영상 로드
        p = os.path.join(ROOT, "web", "public", "docs", f"{args.prefix}_{lang}.mp4")
        ver = int(os.path.getmtime(p)) if os.path.exists(p) else 0
        return f"{args.astro}/docs/{args.prefix}_{lang}.mp4?v={ver}"
    cfg = {"ep": args.episode, "title": title[0] if title else args.episode,
           "scenes": load_scenes(args.episode, args.log),
           "vko": vurl("ko"), "ven": vurl("en")}
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(cfg))
    print(f"리뷰 도구 → http://localhost:{args.port}   (영상: {cfg['title']}, {len(cfg['scenes'])}씬)")
    print(f"피드백 수집 → hangeul_birth_vowels/review_{args.episode}_feedback.md")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
