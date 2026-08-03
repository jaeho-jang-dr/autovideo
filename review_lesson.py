#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""review_lesson.py — 범용 한글강의 교정 리뷰 앱(하나로 모든 주차).
바뀌는 것만 인자: 영상·srt·라벨·포트. 피드백 파일은 영상명에서 자동 생성.
실행: python review_lesson.py <video.mp4> <srt> "<label>" [port]
예:   python review_lesson.py hangeul_birth_vowels/hangeul_w3_stickman_np_ko_burned.mp4 \
                              hangeul_birth_vowels/hangeul_w3_stickman_np.ko.srt \
                              "W3 · 거센소리·된소리 · 명동" 8916
왼쪽: 영상(정지 가능, 번인 자막) / 오른쪽: 씬 타임라인 + 시점별 교정 메모.
"""
import os, re, json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
def _a(i, d=None): return sys.argv[i] if len(sys.argv) > i else d
VIDEO = os.path.abspath(_a(1, "hangeul_birth_vowels/hangeul_w1_stickman_np_ko_burned.mp4"))
SRT   = os.path.abspath(_a(2, os.path.splitext(VIDEO)[0] + ".ko.srt"))
LABEL = _a(3, "한글강의")
PORT  = int(_a(4, "8920"))
# ★사장님 지시(2026-07-13): 한글판=한글 자막만 / 영문판=영문 자막만 (섞지 않는다).
#   짝 언어 자막을 같이 보려면 5번째 인자로 'both' 를 준다.
_is_ko = SRT.endswith(".ko.srt")
_both = (_a(5, "") or "").lower() == "both"
_base = re.sub(r"\.(ko|en)\.srt$", "", SRT) if re.search(r"\.(ko|en)\.srt$", SRT) else os.path.splitext(SRT)[0]
_pair = _base + (".en.srt" if _is_ko else ".ko.srt")
SRT2  = _pair if (_both and os.path.exists(_pair)) else None
LANG1, LABEL1 = ("ko", "한국어") if _is_ko else ("en", "English")
LANG2, LABEL2 = ("en", "English") if _is_ko else ("ko", "한국어")
_stem = os.path.splitext(os.path.basename(VIDEO))[0]
_dir  = os.path.dirname(VIDEO)
FB_JSON = os.path.join(_dir, f"review_{_stem}_feedback.json")
FB_MD   = os.path.join(_dir, f"review_{_stem}_feedback.md")

def load_scenes():
    scenes = []
    if not os.path.exists(SRT): return scenes
    for i, blk in enumerate(open(SRT, encoding="utf-8").read().strip().split("\n\n")):
        L = blk.strip().split("\n")
        if len(L) < 3: continue
        m = re.match(r"(\d+):(\d+):([\d,\.]+) --> (\d+):(\d+):([\d,\.]+)", L[1])
        if not m: continue
        f = lambda h, mi, se: int(h)*3600 + int(mi)*60 + float(se.replace(",", "."))
        scenes.append({"seq": i, "start": round(f(m[1],m[2],m[3]), 2), "end": round(f(m[4],m[5],m[6]), 2),
                       "cap": " ".join(L[2:])[:50]})
    return scenes
SCENES = load_scenes()

def srt_to_vtt(path=None):
    p = path or SRT
    if not p or not os.path.exists(p): return "WEBVTT\n\n"
    txt = open(p, encoding="utf-8").read()
    txt = re.sub(r"(\d\d:\d\d:\d\d),(\d\d\d)", r"\1.\2", txt)   # SRT(,) → VTT(.)
    return "WEBVTT\n\n" + txt

def load_fb():
    if os.path.exists(FB_JSON):
        try: return json.load(open(FB_JSON, encoding="utf-8"))
        except Exception: return []
    return []

def save_fb(fb):
    json.dump(fb, open(FB_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    caps = {s["seq"]: s["cap"] for s in SCENES}
    lines = [f"# 교정 피드백 — 한글강의 {LABEL}", "",
             "> review_lesson.py 수집. 감독(Claude)이 이 파일을 읽어 해당 씬만 교정한다.", ""]
    for i, f in enumerate(sorted(fb, key=lambda x: x["t"]), 1):
        mm, ss = divmod(int(f["t"]), 60)
        lines.append(f"{i}. **[{mm:02d}:{ss:02d}] 씬{f['scene']}** 「{caps.get(f['scene'],'')}」 — {f['note']}")
    open(FB_MD, "w", encoding="utf-8").write("\n".join(lines) + "\n")

HTML = r"""<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>교정 리뷰 — 한글강의 __LABEL__</title>
<style>
*{box-sizing:border-box} body{margin:0;font-family:'Malgun Gothic',sans-serif;background:#090a0f;color:#f1f5f9;display:flex;height:100vh;overflow:hidden}
.left{flex:1.45;display:flex;flex-direction:column;padding:14px;min-width:0}
.right{flex:1;display:flex;flex-direction:column;border-left:1px solid #1e293b;background:#0f172a;min-width:360px}
h1{font-size:15px;margin:0 0 8px;color:#4ade80;font-weight:700}
video{width:100%;background:#020617;border-radius:10px;max-height:58vh}
video::cue{background:rgba(0,0,0,0.85);color:#ffffff;font-size:26px;line-height:1.35;font-family:'Malgun Gothic',sans-serif}
.tl{display:flex;flex-wrap:wrap;gap:5px;margin-top:10px;overflow-y:auto;max-height:28vh}
.chip{font-size:11px;padding:4px 7px;border-radius:7px;background:#1e293b;color:#cbd5e1;cursor:pointer;border:1px solid #334155;white-space:nowrap;max-width:230px;overflow:hidden;text-overflow:ellipsis}
.chip:hover{background:#334155} .chip.cur{background:#22c55e;color:#ffffff;font-weight:700}
.chip.has{border-color:#ea580c}
.panel{padding:14px;display:flex;flex-direction:column;height:100%}
.now{font-size:13px;color:#94a3b8;margin-bottom:6px}
.now b{color:#4ade80}
.cap{font-size:14px;color:#f8fafc;background:#1e293b;border:1px solid #334155;border-radius:8px;padding:8px 10px;margin-bottom:8px;min-height:38px}
textarea{width:100%;height:80px;background:#0f172a;color:#f8fafc;border:1px solid #334155;border-radius:8px;padding:10px;font-size:14px;resize:vertical;font-family:inherit}
.btn{margin-top:8px;background:#16a34a;color:#fff;border:0;border-radius:8px;padding:10px;font-weight:700;cursor:pointer;font-size:14px}
.btn:hover{background:#15803d}
.hint{font-size:11px;color:#94a3b8;margin-top:4px}
.list{margin-top:14px;overflow-y:auto;flex:1;border-top:1px solid #1e293b;padding-top:10px}
.item{background:#1e293b;border-radius:8px;padding:9px 10px;margin-bottom:8px;font-size:13px;border:1px solid #334155;border-left:4px solid #ea580c;color:#f8fafc}
.item .ts{color:#4ade80;font-weight:700;cursor:pointer}
.item .sc{color:#94a3b8;font-size:11px}
.item .nt{margin-top:3px;color:#f8fafc;white-space:pre-wrap}
.item .del{float:right;color:#94a3b8;cursor:pointer;font-size:12px}
.row{display:flex;align-items:center}
.jump{margin-left:auto;font-size:11px;color:#94a3b8}
</style></head><body>
<div class=left>
  <div class=row><h1>🎬 교정 리뷰 — 한글강의 __LABEL__</h1>
    <span class=jump>영상 정지 → 메모 입력 → 추가</span></div>
  <div class=row style="gap:8px;margin:6px 0">
    <span style="font-size:12px;color:#94a3b8">🎧 소리 출력</span>
    <select id=snk style="flex:1;background:#0f172a;color:#f8fafc;border:1px solid #334155;border-radius:6px;padding:5px;font-size:12px">
      <option value="">(기본 장치)</option>
    </select>
    <button class=btn style="width:auto;padding:5px 10px;font-size:12px" onclick=loadSinks()>장치 새로고침</button>
    <button class=btn style="width:auto;padding:5px 10px;font-size:12px" onclick=fixSound()>🔊 소리 복구</button>
  </div>
  <div id=snkst style="font-size:11px;color:#6b8;margin:-2px 0 6px 2px"></div>
  <video id=vid controls preload=metadata crossorigin=anonymous>
    <source src="/video" type="video/mp4">
    <track id=trk kind=subtitles srclang=__LANG1__ label="__LABEL1__" src="/subs" default>
    __TRACK2__
  </video>
  <div class=tl id=tl></div>
</div>
<div class=right><div class=panel>
  <div class=now>현재 <b id=ct>00:00</b> · <span id=cs>씬0</span></div>
  <div class=cap id=cc></div>
  <textarea id=note placeholder="이 시점에서 틀린 점을 적어주세요. (정지 후 입력 → 추가)"></textarea>
  <button class=btn onclick=addNote()>➕ 이 시점에 메모 추가  (Ctrl+Enter)</button>
  <div class=hint>메모는 현재 시점·씬과 함께 자동 저장됩니다.</div>
  <div class=list id=list></div>
</div></div>
<script>
// ── 🎧 소리 출력 = 컴퓨터(윈도우) 사운드 설정을 그대로 따라감 ─────────────
// ★기본 동작: 'default' 싱크에 붙여 **윈도우 기본 출력 장치**를 따라간다.
//   (Chrome이 예전 장치를 붙잡고 스피커로만 내보내는 문제 해결. 이어폰 꽂으면 이어폰으로.)
//   시스템 오디오 설정·서비스는 절대 건드리지 않는다(원격 CRD 환경 — 만지면 소리 끊김).
// 필요하면 아래 드롭다운으로 특정 장치를 강제 지정할 수도 있다.
var SINK_KEY = 'review_sink_id';
async function applySink(id){
  var v = document.getElementById('vid');
  if(typeof v.setSinkId !== 'function') return;          // 미지원 브라우저는 조용히 기본 동작
  try{
    await v.setSinkId(id || 'default');                  // ''/'default' → 윈도우 기본 장치 추종
    localStorage.setItem(SINK_KEY, id || '');
  }catch(e){ console.warn('setSinkId 실패', e); }
}
async function loadSinks(){
  var sel = document.getElementById('snk');
  try{
    try{                                                  // 장치 '이름'을 보려면 권한 필요
      var st = await navigator.mediaDevices.getUserMedia({audio:true});
      st.getTracks().forEach(function(t){t.stop();});
    }catch(e){ /* 거부해도 기본 추종은 동작 */ }
    var devs = await navigator.mediaDevices.enumerateDevices();
    var outs = devs.filter(function(d){return d.kind==='audiooutput';});
    sel.innerHTML = '<option value="">🖥️ 컴퓨터 설정 따라가기 (기본)</option>';
    outs.forEach(function(d){
      if(d.deviceId === 'default') return;                // 기본은 위 항목으로 이미 있음
      var o = document.createElement('option');
      o.value = d.deviceId;
      o.textContent = d.label || ('출력 장치 ' + d.deviceId.slice(0,6));
      sel.appendChild(o);
    });
    // ★사장님 지시: 교정앱 소리는 **항상 시스템(윈도우) 음성 출력 상태를 그대로 따라간다**.
    //   윈도우 기본 출력이 이어폰이면 이어폰, 스피커면 스피커. 장치를 바꾸면 즉시 따라감.
    //   (특정 장치를 강제하고 싶을 때만 아래 드롭다운에서 직접 고르면 그 선택을 기억)
    var saved = localStorage.getItem(SINK_KEY);           // 사용자가 직접 고른 게 있으면 그것만 우선
    var use = (saved && outs.some(function(d){return d.deviceId===saved;})) ? saved : '';
    sel.value = use;
    applySink(use);                                       // '' → 'default' 싱크 = 윈도우 기본 장치 추종
    var cur = outs.filter(function(d){return d.deviceId===use;})[0];
    var dflt = outs.filter(function(d){return d.deviceId==='default';})[0];
    var st = document.getElementById('snkst');
    if(st) st.textContent = use ? ('▶ ' + (cur && cur.label ? cur.label : '선택 장치') + ' (직접 지정)')
                                : ('▶ 컴퓨터 설정 따라감' + (dflt && dflt.label ? ' — ' + dflt.label : ''));
  }catch(e){ console.warn('장치 조회 실패', e); applySink(''); }
}
document.addEventListener('DOMContentLoaded', function(){
  var sel = document.getElementById('snk');
  if(sel) sel.addEventListener('change', function(){ applySink(sel.value); });
  loadSinks();
  // ★이어폰을 꽂거나 빼면 자동으로 새 기본 장치를 따라간다
  if(navigator.mediaDevices){
    navigator.mediaDevices.addEventListener('devicechange', function(){ loadSinks(); });
  }
});
// ───────────────────────────────────────────────────────────────────────
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
vid.addEventListener('loadedmetadata',function(){try{for(var i=0;i<vid.textTracks.length;i++)vid.textTracks[i].mode='showing';}catch(e){}
  // ★소리 보정: 브라우저가 기억한 음소거·0볼륨 때문에 안 들리는 경우가 있다(시스템 설정은 안 건드림)
  try{vid.muted=false;vid.volume=1.0;}catch(e){}});
function fixSound(){                                  // 🔊 버튼 — 언뮤트 + 볼륨 최대 + 기본 출력장치 재부착
  try{vid.muted=false;vid.volume=1.0;}catch(e){}
  try{localStorage.removeItem(SINK_KEY);}catch(e){}
  applySink('');
  var s=document.getElementById('snkst');
  if(s) s.textContent='▶ 소리 복구 실행 — 음소거 해제·볼륨 100%·컴퓨터 기본 출력';
  vid.play().catch(function(){});
}
setTimeout(function(){try{if(vid.textTracks[0])vid.textTracks[0].mode='showing';}catch(e){}},1200);
buildTL(); load(); setInterval(tick,250);
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
        def _serve_video(self):
            size = os.path.getsize(VIDEO); rng = self.headers.get("Range")
            if rng:
                m = re.match(r"bytes=(\d+)-(\d*)", rng)
                s = int(m.group(1)); e = int(m.group(2)) if m.group(2) else size - 1
                e = min(e, size - 1); length = e - s + 1
                self.send_response(206); self.send_header("Content-Type", "video/mp4"); self.send_header("Cache-Control", "no-store")
                self.send_header("Accept-Ranges", "bytes"); self.send_header("Content-Range", f"bytes {s}-{e}/{size}")
                self.send_header("Content-Length", str(length)); self.end_headers()
                with open(VIDEO, "rb") as f:
                    f.seek(s); remain = length
                    while remain > 0:
                        chunk = f.read(min(1 << 20, remain))
                        if not chunk: break
                        self.wfile.write(chunk); remain -= len(chunk)
            else:
                self.send_response(200); self.send_header("Content-Type", "video/mp4"); self.send_header("Cache-Control", "no-store")
                self.send_header("Accept-Ranges", "bytes"); self.send_header("Content-Length", str(size)); self.end_headers()
                with open(VIDEO, "rb") as f:
                    while True:
                        chunk = f.read(1 << 20)
                        if not chunk: break
                        self.wfile.write(chunk)
        def do_GET(self):
            if self.path == "/" or self.path.startswith("/index"):
                t2 = (f'<track id=trk2 kind=subtitles srclang={LANG2} label="{LABEL2}" src="/subs2">'
                      if SRT2 else "")
                html = (HTML.replace("__SCENES__", json.dumps(SCENES, ensure_ascii=False))
                            .replace("__LABEL__", LABEL)
                            .replace("__LANG1__", LANG1).replace("__LABEL1__", LABEL1)
                            .replace("__TRACK2__", t2))
                self._send(200, html, "text/html; charset=utf-8")
            elif self.path == "/video":
                try: self._serve_video()
                except Exception: pass
            elif self.path == "/subs":
                self._send(200, srt_to_vtt().encode("utf-8"), "text/vtt; charset=utf-8")   # 주자막(srt→vtt)
            elif self.path == "/subs2":
                self._send(200, srt_to_vtt(SRT2).encode("utf-8"), "text/vtt; charset=utf-8")  # 짝 언어 자막
            elif self.path == "/api/feedback":
                self._send(200, json.dumps(load_fb(), ensure_ascii=False))
            else:
                self._send(404, "{}")
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or "{}"); fb = load_fb()
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
    print(f"교정 리뷰 [{LABEL}] → http://localhost:{PORT}  ({len(SCENES)}씬, {os.path.basename(VIDEO)})")
    print(f"피드백 → {FB_MD}")
    httpd.serve_forever()
