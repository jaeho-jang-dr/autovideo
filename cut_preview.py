# -*- coding: utf-8 -*-
"""컷랑 프레임컷 상영기 — 64컷 스틸 애니메이션을 한 페이지에 모아 재생한다 (2026-07-27).

`W23/poses/injun_w23_<key>_<n>.png` 시퀀스를 시퀀스별 미리보기 mp4 로 묶고,
격자 HTML 로 전부 동시에 돌린다. 컷 번호가 비어 있어도(폐기 컷 격리) concat 목록으로 처리한다.

속도: 원본 8초 동영상에서 3프레임 간격으로 64컷을 뽑았으므로 **8fps 가 실제 속도**다.

사용:
  python cut_preview.py                 # 전부 만들고 브라우저로 상영
  python cut_preview.py --fps 12        # 조금 빠르게
  python cut_preview.py --only greet_wave
"""
import argparse
import glob
import http.server
import os
import re
import socket
import socketserver
import subprocess
import sys
import threading
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
SRC_DIR = "W23/poses"
OUT_DIR = "W23/preview"
HEIGHT = 480


def log(m):
    print(m, flush=True)


def sequences():
    """키 → 프레임 파일 목록(번호순). 번호가 비어 있어도 있는 것만 순서대로 쓴다."""
    seqs = {}
    for p in glob.glob(f"{SRC_DIR}/injun_w23_*_*.png"):
        name = os.path.basename(p)[:-4]
        m = re.match(r"injun_w23_(.+)_(\d+)$", name)
        if m:
            seqs.setdefault(m.group(1), []).append((int(m.group(2)), p.replace("\\", "/")))
    return {k: [p for _, p in sorted(v)] for k, v in sorted(seqs.items()) if len(v) >= 4}


def build(key, frames, fps):
    out = f"{OUT_DIR}/{key}_anim.mp4"
    lst = f"{OUT_DIR}/_{key}_concat.txt"
    with open(lst, "w", encoding="utf-8") as f:
        for p in frames:
            f.write(f"file '{os.path.abspath(p)}'\nduration {1/fps:.4f}\n")
        f.write(f"file '{os.path.abspath(frames[-1])}'\n")   # concat 은 마지막 파일을 한 번 더 요구한다
    # ★컷은 알파 PNG 다 → 흰 배경에 얹어야 검게 나온다. 세로 HEIGHT 기준으로 축소(폭은 짝수 보정).
    from PIL import Image
    sw, sh = Image.open(frames[0]).size
    tw, th = (int(sw * HEIGHT / sh) // 2) * 2, HEIGHT
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
           "-filter_complex",
           f"color=white:s={tw}x{th}[bg];[0:v]scale={tw}:{th}[fg];"
           f"[bg][fg]overlay=shortest=1,format=yuv420p",
           "-r", str(fps), "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", out]
    r = subprocess.run(cmd, capture_output=True)
    os.remove(lst)
    if r.returncode != 0 or not os.path.exists(out):
        log(f"  ★{key} 실패: {r.stderr.decode('utf-8', 'replace')[-300:]}")
        return None
    return out


DEPRECATED = {"windmill_up": "폐기 — 다리 3개"}


def write_html(items, fps):
    items = sorted(items, key=lambda it: (it[0] in DEPRECATED, it[0]))
    cells = "\n".join(
        f'<figure{" class=dead" if k in DEPRECATED else ""}>'
        f'<video src="{os.path.basename(v)}" autoplay loop muted playsinline></video>'
        f'<figcaption>{k} <span>{DEPRECATED.get(k, str(n) + "컷")}</span></figcaption></figure>'
        for k, v, n in items)
    html = f"""<!doctype html><meta charset="utf-8"><title>W23 컷랑 스틸컷 애니 상영</title>
<style>
 body{{margin:0;background:#111;color:#eee;font:14px/1.5 'Malgun Gothic',sans-serif}}
 h1{{font-size:18px;padding:14px 18px;margin:0;border-bottom:1px solid #333}}
 h1 small{{color:#8ab;font-weight:400;margin-left:10px}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;padding:16px}}
 figure{{margin:0;background:#fff;border-radius:8px;overflow:hidden}}
 video{{width:100%;display:block;background:#fff}}
 figcaption{{background:#1b1b1b;padding:7px 10px;font-size:13px;display:flex;justify-content:space-between}}
 figcaption span{{color:#7c9}}
 .dead{{opacity:.55}} .dead figcaption span{{color:#e66}}
</style>
<h1>W23 컷랑 스틸컷 애니 — 전체 상영 <small>{len(items)}종 · {fps}fps(실제 속도)</small></h1>
<div class="grid">{cells}</div>
"""
    p = f"{OUT_DIR}/index.html"
    open(p, "w", encoding="utf-8").write(html)
    return p


THUMB_H = 150


def build_thumbs(key, frames):
    """왼편 프레임 목록용 작은 썸네일(흰 배경 JPEG). 원본 1024x1280 PNG 는 무거워 직접 못 깐다."""
    from PIL import Image
    d = f"{OUT_DIR}/thumbs/{key}"
    os.makedirs(d, exist_ok=True)
    idx = []
    for p in frames:
        n = int(re.findall(r"_(\d+)\.png$", p)[0])
        out = f"{d}/{n}.jpg"
        idx.append((n, p))
        if os.path.exists(out):
            continue
        im = Image.open(p).convert("RGBA")
        im.thumbnail((THUMB_H * 2, THUMB_H), Image.LANCZOS)
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, (0, 0), im)
        bg.save(out, quality=82)
    return idx


def write_view(seq_index, fps):
    """시퀀스 하나씩 정밀 검사 — 왼편 전체 프레임 / 오른편 애니 + 큰 정지컷."""
    data = {k: [n for n, _ in v] for k, v in seq_index.items()}
    keys = sorted(data, key=lambda k: (k in DEPRECATED, k))
    tabs = "".join(f'<button data-k="{k}"{" class=dead" if k in DEPRECATED else ""}>{k}</button>'
                   for k in keys)
    html = """<!doctype html><meta charset="utf-8"><title>W23 프레임컷 정밀 검사</title>
<style>
 *{box-sizing:border-box} body{margin:0;background:#111;color:#eee;font:13px/1.5 'Malgun Gothic',sans-serif}
 header{padding:8px 12px;border-bottom:1px solid #333;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
 header b{margin-right:8px;font-size:15px}
 header button{background:#222;color:#bbb;border:1px solid #383838;border-radius:14px;padding:4px 11px;cursor:pointer}
 header button:hover{background:#2c2c2c;color:#fff}
 header button.on{background:#2f6f4f;border-color:#3d8a63;color:#fff}
 header button.dead{color:#a55}
 main{display:grid;grid-template-columns:1fr 620px;gap:12px;padding:12px;align-items:start}
 .frames{display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:6px}
 .fr{position:relative;background:#fff;border-radius:5px;overflow:hidden;border:2px solid transparent;cursor:pointer}
 .fr img{width:100%;display:block}
 .fr i{position:absolute;left:0;top:0;background:#000a;color:#fff;font-style:normal;font-size:11px;padding:1px 5px;border-radius:0 0 5px 0}
 .fr.on{border-color:#4ade80}
 .fr.bad{border-color:#e5484d}
 .fr.bad i{background:#e5484d}
 aside{position:sticky;top:12px;display:flex;flex-direction:column;gap:10px}
 aside video,aside .big{width:100%;background:#fff;border-radius:8px;display:block}
 .big{min-height:300px;object-fit:contain}
 .bar{display:flex;gap:8px;align-items:center;color:#9ab}
 .bar button{background:#222;color:#ddd;border:1px solid #383838;border-radius:6px;padding:4px 10px;cursor:pointer}
 .hint{color:#777}
</style>
<header><b>W23 프레임컷 정밀 검사</b><span class="hint">← → 프레임 이동 · X 로 불량 표시 · 썸네일 클릭</span><br>TABS</header>
<main>
 <div class="frames" id="fs"></div>
 <aside>
  <video id="vid" autoplay loop muted playsinline></video>
  <div class="bar"><button id="prev">◀</button><span id="lab"></span><button id="next">▶</button>
   <button id="mark">불량 표시 (X)</button><span id="badlist" class="hint"></span></div>
  <img class="big" id="big">
 </aside>
</main>
<script>
const DATA = __DATA__;
let key = Object.keys(DATA)[0], cur = 0, bad = {};
const $ = s => document.querySelector(s);
function render(){
  document.querySelectorAll('header button').forEach(b=>b.classList.toggle('on', b.dataset.k===key));
  $('#vid').src = key + '_anim.mp4';
  const fs = DATA[key];
  $('#fs').innerHTML = fs.map((n,i)=>
    `<div class="fr" data-i="${i}"><img loading="lazy" src="thumbs/${key}/${n}.jpg"><i>${n}</i></div>`).join('');
  sel(0);
}
function sel(i){
  const fs = DATA[key]; cur = (i + fs.length) % fs.length;
  document.querySelectorAll('.fr').forEach((e,j)=>{
    e.classList.toggle('on', j===cur);
    e.classList.toggle('bad', !!(bad[key]||{})[fs[j]]);
  });
  const n = fs[cur];
  $('#big').src = '../poses/injun_w23_' + key + '_' + n + '.png';
  $('#lab').textContent = `${key}  ${cur+1}/${fs.length}  (컷 #${n})`;
  const b = Object.keys(bad[key]||{});
  $('#badlist').textContent = b.length ? '불량: ' + b.join(', ') : '';
  const el = document.querySelectorAll('.fr')[cur]; if(el) el.scrollIntoView({block:'nearest'});
}
function toggleBad(){
  const n = DATA[key][cur]; bad[key] = bad[key]||{};
  if(bad[key][n]) delete bad[key][n]; else bad[key][n]=1;
  sel(cur);
}
document.addEventListener('click', e=>{
  const t = e.target.closest('header button'); if(t){ key = t.dataset.k; render(); return; }
  const f = e.target.closest('.fr'); if(f) sel(+f.dataset.i);
});
$('#prev').onclick = ()=>sel(cur-1); $('#next').onclick = ()=>sel(cur+1); $('#mark').onclick = toggleBad;
document.addEventListener('keydown', e=>{
  if(e.key==='ArrowLeft') sel(cur-1);
  else if(e.key==='ArrowRight') sel(cur+1);
  else if(e.key.toLowerCase()==='x') toggleBad();
});
render();
</script>
"""
    import json
    html = html.replace("TABS", tabs).replace("__DATA__", json.dumps(data))
    p = f"{OUT_DIR}/view.html"
    open(p, "w", encoding="utf-8").write(html)
    return p


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=int, default=8, help="8 = 원본과 같은 속도")
    ap.add_argument("--only")
    ap.add_argument("--no-serve", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)

    seqs = sequences()
    if a.only:
        seqs = {k: v for k, v in seqs.items() if a.only in k}
    if not seqs:
        sys.exit("시퀀스 없음")

    items, seq_index = [], {}
    for k, frames in seqs.items():
        log(f"[{len(items)+1}/{len(seqs)}] {k} — {len(frames)}컷")
        v = build(k, frames, a.fps) if not os.path.exists(f"{OUT_DIR}/{k}_anim.mp4") else f"{OUT_DIR}/{k}_anim.mp4"
        if v:
            items.append((k, v, len(frames)))
            seq_index[k] = build_thumbs(k, frames)
    if not items:
        sys.exit("만들어진 미리보기 없음")

    page = write_html(items, a.fps)
    view = write_view(seq_index, a.fps)
    log(f"✅ {len(items)}종 · 전체상영 {page} · 정밀검사 {view}")
    if a.no_serve:
        sys.exit(0)

    port = free_port()
    httpd = socketserver.TCPServer(("127.0.0.1", port), http.server.SimpleHTTPRequestHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{port}/{OUT_DIR}/view.html"
    log(f"🌐 {url}  (Ctrl+C 로 종료)")
    webbrowser.open(url)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
