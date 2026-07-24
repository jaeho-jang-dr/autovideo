#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""subs_helper.py — 자막 수동 업로드 도우미 앱.

사장님이 클릭만 하면:
  ① 그 언어 자막 텍스트가 **클립보드에 복사**됨
  ② 유튜브 스튜디오의 **그 영상 자막 페이지가 새 탭으로 열림**
  ③ 유튜브에서 연필(수정) → 기존 자막 지우고 → Ctrl+V 붙여넣기 → 게시
파일 탐색기에서 파일 찾을 필요 없음.

사용: python subs_helper.py [port]
"""
import os, sys, json, re, io
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8930

# ── 영상별 자막 정의 ──────────────────────────────────────────
# (주차, 판, video_id, 패키지 폴더, {유튜브언어명: srt파일})
VIDEOS = [
    dict(week="W13", edition="영어편", vid="XT0jYFhrsxY", pkg="hangeul_birth_vowels/w13pkg",
         title="Korean Directions (Jeju)",
         subs={"일본어": "en_ja.srt", "중국어(중국)": "en_zh.srt", "스페인어": "en_es.srt"}),
    dict(week="W13", edition="한글편", vid="zsfOc4R4IbA", pkg="hangeul_birth_vowels/w13pkg",
         title="길 찾기 한국어 (성산일출봉)",
         subs={"영어": "ko_en.srt", "일본어": "ko_ja.srt", "중국어(중국)": "ko_zh.srt", "스페인어": "ko_es.srt"},
         done=True),
    dict(week="W12", edition="한글편", vid="pM7eN6Qt6s4", pkg="hangeul_birth_vowels/w12pkg",
         title="지하철·버스 한국어",
         subs={"영어": "ko_en.srt", "일본어": "ko_ja.srt", "중국어(중국)": "ko_zh.srt", "스페인어": "ko_es.srt"}),
    dict(week="W12", edition="영어편", vid="VPgmXo5jXtY", pkg="hangeul_birth_vowels/w12pkg",
         title="Korean Subway & Bus",
         subs={"일본어": "en_ja.srt", "중국어(중국)": "en_zh.srt", "스페인어": "en_es.srt"}),
]

def read_srt(pkg, f):
    p = os.path.join(pkg, f)
    if not os.path.exists(p):
        return None
    return open(p, encoding="utf-8").read()

def stats(txt):
    if not txt:
        return dict(blocks=0, hangeul=0, sample="")
    blocks = txt.count(" --> ")
    han = len([l for l in txt.split("\n") if re.search(r"[가-힣]", l)])
    sample = ""
    for l in txt.split("\n"):
        if re.search(r"[가-힣]", l) and len(l.strip()) > 10:
            sample = l.strip()[:70]; break
    return dict(blocks=blocks, hangeul=han, sample=sample)

HTML = """<!doctype html><html lang=ko><head><meta charset=utf-8>
<title>자막 업로드 도우미</title>
<style>
*{box-sizing:border-box} body{margin:0;background:#0f1721;color:#e8f0f5;font-family:"Malgun Gothic",sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:24px}
h1{font-size:22px;margin:0 0 6px} .sub{color:#8fa8b8;font-size:14px;margin-bottom:22px}
.vid{background:#16222e;border:1px solid #24384a;border-radius:12px;padding:18px;margin-bottom:18px}
.vh{display:flex;align-items:center;gap:10px;margin-bottom:14px}
.badge{background:#1f9ea8;color:#fff;padding:3px 10px;border-radius:20px;font-size:13px;font-weight:700}
.badge.done{background:#2e7d4f}
.vt{font-size:16px;font-weight:700} .vi{color:#7e98a8;font-size:12px;margin-left:auto}
table{width:100%;border-collapse:collapse}
th{text-align:left;color:#7e98a8;font-size:12px;font-weight:400;padding:6px 8px;border-bottom:1px solid #24384a}
td{padding:9px 8px;border-bottom:1px solid #1d2c3a;vertical-align:middle}
.lang{font-weight:700;font-size:15px}
.meta{color:#7e98a8;font-size:12px}
.smp{color:#9fd8c8;font-size:12px;font-family:Consolas,monospace}
.btn{background:#1f9ea8;color:#fff;border:0;border-radius:8px;padding:9px 16px;font-size:14px;font-weight:700;cursor:pointer;white-space:nowrap}
.btn:hover{background:#28b8c4} .btn.ok{background:#2e7d4f}
.btn2{background:#2b3d4f;color:#cfe3ee;border:0;border-radius:8px;padding:9px 14px;font-size:13px;cursor:pointer;margin-left:6px}
.btn2:hover{background:#37506a}
.steps{background:#12202c;border-left:4px solid #1f9ea8;padding:14px 16px;border-radius:8px;margin-bottom:22px;font-size:14px;line-height:1.9}
.steps b{color:#7fe3ec}
.toast{position:fixed;right:22px;bottom:22px;background:#2e7d4f;color:#fff;padding:14px 20px;border-radius:10px;font-weight:700;opacity:0;transition:.25s;font-size:15px}
.toast.show{opacity:1}
.warn{color:#ffb86b}
</style></head><body><div class=wrap>
<h1>📋 자막 업로드 도우미</h1>
<div class=sub>버튼 하나로 <b>자막이 클립보드에 복사</b>되고 <b>유튜브 자막 페이지가 열립니다.</b> 파일 찾을 필요 없어요.</div>

<div class=steps>
<b>①</b> 아래에서 올릴 언어의 <b>[복사 + 유튜브 열기]</b> 클릭 &nbsp;→&nbsp;
<b>②</b> 유튜브에서 그 언어 줄의 <b>연필(수정)</b> 클릭 &nbsp;→&nbsp;
<b>③</b> 기존 자막 <b>전체 선택(Ctrl+A) 후 삭제</b> &nbsp;→&nbsp;
<b>④</b> <b>Ctrl+V</b> 붙여넣기 &nbsp;→&nbsp;
<b>⑤</b> <b>게시</b> 클릭
<br><span class=warn>※ 자막 편집기가 "파일 업로드" 방식이면 → [파일 위치 열기]로 파일을 직접 올리세요.</span>
</div>

__BODY__
</div>
<div class=toast id=t>클립보드에 복사됨!</div>
<script>
async function go(vid, key, url){
  const r = await fetch('/srt?k=' + encodeURIComponent(key));
  const txt = await r.text();
  try { await navigator.clipboard.writeText(txt); }
  catch(e){ const ta=document.createElement('textarea'); ta.value=txt; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove(); }
  const t=document.getElementById('t'); t.textContent='✅ 자막 복사됨 — 유튜브에서 Ctrl+V'; t.className='toast show';
  setTimeout(()=>t.className='toast',2600);
  window.open(url, '_blank');
}
async function copyOnly(key){
  const r = await fetch('/srt?k=' + encodeURIComponent(key));
  const txt = await r.text();
  try { await navigator.clipboard.writeText(txt); } catch(e){}
  const t=document.getElementById('t'); t.textContent='✅ 클립보드에 복사됨'; t.className='toast show';
  setTimeout(()=>t.className='toast',2000);
}
function openFolder(k){ fetch('/folder?k=' + encodeURIComponent(k)); }
</script></body></html>"""


def build_body():
    out = []
    for v in VIDEOS:
        done = v.get("done")
        rows = []
        for lang, f in v["subs"].items():
            key = f"{v['vid']}|{f}"
            txt = read_srt(v["pkg"], f)
            s = stats(txt)
            if not txt:
                rows.append(f"<tr><td class=lang>{lang}</td><td class=meta>파일 없음: {f}</td><td></td><td></td></tr>")
                continue
            url = f"https://studio.youtube.com/video/{v['vid']}/translations"
            rows.append(
                f"<tr><td class=lang>{lang}</td>"
                f"<td><div class=meta>{f} · {s['blocks']}블록 · 한글 {s['hangeul']}줄</div>"
                f"<div class=smp>{s['sample']}</div></td>"
                f"<td style='text-align:right'>"
                f"<button class=btn onclick=\"go('{v['vid']}','{key}','{url}')\">복사 + 유튜브 열기</button>"
                f"<button class=btn2 onclick=\"copyOnly('{key}')\">복사만</button>"
                f"<button class=btn2 onclick=\"openFolder('{key}')\">파일 위치</button>"
                f"</td></tr>")
        badge = "<span class='badge done'>완료</span>" if done else f"<span class=badge>{v['week']}</span>"
        out.append(
            f"<div class=vid><div class=vh>{badge}"
            f"<span class=vt>{v['edition']} — {v['title']}</span>"
            f"<span class=vi>{v['vid']}</span></div>"
            f"<table><tr><th style='width:130px'>언어</th><th>자막 파일</th><th></th></tr>"
            + "".join(rows) + "</table></div>")
    return "\n".join(out)


def handler():
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass

        def _send(self, code, body, ctype="text/html; charset=utf-8"):
            if isinstance(body, str):
                body = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/" or self.path.startswith("/index"):
                self._send(200, HTML.replace("__BODY__", build_body()))
            elif self.path.startswith("/srt"):
                from urllib.parse import urlparse, parse_qs
                q = parse_qs(urlparse(self.path).query)
                key = q.get("k", [""])[0]
                vid, f = key.split("|", 1)
                v = next((x for x in VIDEOS if x["vid"] == vid), None)
                txt = read_srt(v["pkg"], f) if v else ""
                self._send(200, txt or "", "text/plain; charset=utf-8")
            elif self.path.startswith("/folder"):
                from urllib.parse import urlparse, parse_qs
                import subprocess
                q = parse_qs(urlparse(self.path).query)
                key = q.get("k", [""])[0]
                vid, f = key.split("|", 1)
                v = next((x for x in VIDEOS if x["vid"] == vid), None)
                if v:
                    p = os.path.abspath(os.path.join(v["pkg"], f))
                    subprocess.Popen(["explorer", "/select,", p])
                self._send(200, "ok", "text/plain")
            else:
                self._send(404, "{}")
    return H


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), handler())
    print(f"자막 업로드 도우미: http://localhost:{PORT}/", flush=True)
    srv.serve_forever()
