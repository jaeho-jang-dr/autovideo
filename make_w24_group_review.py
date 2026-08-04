# -*- coding: utf-8 -*-
"""W24 그룹 클립 검토 페이지 — 영상 + 실측 수치를 나란히 놓고 **사장님이 눈으로 확인**한다.
   (사장님 지시 2026-08-04: "다 만들고 나서 내가 보게 해줘, 내 눈으로 확인하는 것이 제일 좋겠다")

   W24/bgv.html 의 격자 방식을 그대로 따른다. 불합격/보류를 위로 올려서 먼저 보이게 한다.
   탈락한 시도(_reject_*)도 같이 실어 비교할 수 있게 한다.

   사용: python make_w24_group_review.py [--port 8899] [--no-serve]
"""
import argparse
import contextlib
import glob
import io
import os
import re
import socket
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

import verify_w24_group_clip as V
from gen_w24_group_prompts import ACTS, CM

CLIPS = "W24/group_clips"
OUT = "W24/_view/groups.html"


def free_port(start=8899):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("빈 포트 없음")


def verdict(key):
    """검사기를 그대로 돌려 (합격여부, 출력줄) 을 받는다 — 수치를 페이지에 그대로 싣는다."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ok = V.check(key)
    lines = [re.sub(r"^\s+", "", ln) for ln in buf.getvalue().splitlines()
             if ln.strip() and not ln.startswith("===")]
    return ok, lines


def card(no, key, refs, scenes, ok, lines, rejects):
    """no = 사장님이 부르실 번호. 화면에서 크게 보이게 앞에 붙인다."""
    cls = "ok" if ok else "ng"
    badge = "합격" if ok else "불합격 · 보류"
    rows = "".join(f"<div class=m>{ln}</div>" for ln in lines)
    rj = "".join(
        f'<div class=r><b>탈락 {i + 1}</b>'
        f'<video src="/{p}" loop muted controls playsinline></video></div>'
        for i, p in enumerate(rejects))
    rjbox = f"<details><summary>탈락한 시도 {len(rejects)}개</summary><div class=rg>{rj}</div></details>" if rejects else ""
    return (f'<div class="c {cls}" id="n{no}"><b><span class=no>{no}</span>{key}'
            f'<span class=bg>{badge}</span></b>'
            f'<div class=s>{len(refs)}인 · {", ".join(refs)} · 씬 {scenes}</div>'
            f'<video src="/{CLIPS}/{key}.mp4" loop muted controls playsinline></video>'
            f'{rows}{rjbox}</div>')


CSS = """body{margin:0;background:#0b0d12;color:#e8ecf4;font-family:Malgun Gothic}
.w{max-width:1600px;margin:0 auto;padding:16px}h1{font-size:19px}
h2{font-size:15px;color:#9fb0c8;border-top:1px solid #222a38;padding-top:14px;margin-top:22px}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:12px}
.c{border:1px solid #1e2532;border-radius:9px;background:#10141c;padding:9px}
.c.ng{border-color:#7d2b2b;background:#160f11}
.c b{font-size:13px;color:#63d2a4;display:block;margin-bottom:3px}
.no{display:inline-block;min-width:26px;height:22px;line-height:22px;text-align:center;background:#2b3a52;color:#dbe6f5;border-radius:6px;font-size:13px;margin-right:7px}
.c.ng .no{background:#5a2020;color:#ffd9d9}
.c.ng b{color:#ff8b8b}
.bg{float:right;font-size:11px;padding:1px 7px;border-radius:9px;background:#163d2c;color:#7de2b0}
.c.ng .bg{background:#3d1616;color:#ff9a9a}
.s{font-size:11px;color:#7f8ea6;margin-bottom:6px}
video{width:100%;border-radius:6px;background:#000}
.m{font-size:11px;color:#b9c6da;margin-top:3px;font-family:Consolas,monospace}
details{margin-top:7px}summary{font-size:11px;color:#8fa0b8;cursor:pointer}
.rg{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px}
.r b{font-size:11px;color:#8fa0b8}"""


def main_files(port, serve):
    """★'만들어진 것 다 보자' — 검사 없이 폴더의 mp4 를 최신순으로 전부 깐다(빠르다).
    64컷 검사는 클립당 10~20초라 34개면 10분이 넘는다. 먼저 눈으로 보고 필요한 것만 검사한다."""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fs = sorted(glob.glob(f"{CLIPS}/*.mp4"), key=os.path.getmtime, reverse=True)
    cards = []
    for i, p in enumerate(fs, 1):
        b = os.path.basename(p)
        key = b[:-4]
        tag = ("폐기(옛 얼굴)" if b.startswith("_reject_oldface_") else
               "폐기(옛 머리)" if b.startswith("_reject_hair_") else
               "얼굴 확정 시험" if b.startswith("_facetest_") else
               "탈락" if b.startswith("_reject_") else "정식")
        cls = "ok" if tag == "정식" else "ng"
        mb = os.path.getsize(p) // 1024
        when = __import__("time").strftime("%m-%d %H:%M", __import__("time").localtime(os.path.getmtime(p)))
        cards.append(f'<div class="c {cls}" id="n{i}"><b><span class=no>{i}</span>{key}'
                     f'<span class=bg>{tag}</span></b>'
                     f'<div class=s>{when} · {mb}KB</div>'
                     f'<video src="/{p}" loop muted controls playsinline></video></div>')
    html = (f"<!doctype html><meta charset=utf-8><title>W24 그룹 클립 전체</title>"
            f"<style>{CSS}</style><div class=w>"
            f"<h1>W24 그룹 클립 — 만들어진 것 전부 {len(fs)}개 (최신순)</h1>"
            f"<div class=s>초록=정식 · 빨강=폐기/탈락. 번호로 불러 주십시오.</div>"
            f"<div class=g>{''.join(cards)}</div></div>"
            "<script>const io=new IntersectionObserver(e=>e.forEach(x=>"
            "x.isIntersecting?x.target.play().catch(()=>0):x.target.pause()),{threshold:.3});"
            "document.querySelectorAll('video').forEach(v=>io.observe(v));</script>")
    open(OUT, "w", encoding="utf-8").write(html)
    print(f"  → {OUT}  ({len(fs)}개)")
    if serve:
        serve_page(port)
    return 0


def serve_page(port):
    p = port or free_port()
    subprocess.Popen([sys.executable, "-m", "http.server", str(p), "--bind", "127.0.0.1"],
                     cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{p}/{OUT}"
    subprocess.Popen(["cmd", "/c", "start", "", url], shell=False)
    print(f"  브라우저: {url}")


def main(port, serve):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    res = []
    for key, _g, refs, scenes, _a in ACTS:
        if not os.path.exists(f"{CLIPS}/{key}.mp4"):
            continue
        ok, lines = verdict(key)
        rej = sorted(glob.glob(f"{CLIPS}/_reject_{key}_*.mp4"))
        res.append((ok, key, refs, scenes, lines, rej))
    # ★번호는 **손봐야 할 것부터 1번**. 사장님이 번호로 부르시면 바로 찾도록 화면 순서와 같게 둔다.
    res.sort(key=lambda r: r[0])
    okc, ngc = [], []
    for i, (ok, key, refs, scenes, lines, rej) in enumerate(res, 1):
        (okc if ok else ngc).append(card(i, key, refs, scenes, ok, lines, rej))
        print(f"  {i:>2}. {'합격' if ok else '불합격'}  {key}", flush=True)
    html = (f"<!doctype html><meta charset=utf-8><title>W24 그룹 클립 검토</title>"
            f"<style>{CSS}</style><div class=w>"
            f"<h1>W24 그룹 동작 클립 검토 — 합격 {len(okc)} · 불합격 {len(ngc)}</h1>"
            f"<div class=s>검사: 64컷 인원수 일정 · 컷 사이 키 편차 4% 이내 · "
            f"규격 키 비율 ±6%p · 발끝 안 잘림</div>"
            + (f"<h2>손봐야 할 것 {len(ngc)}</h2><div class=g>{''.join(ngc)}</div>" if ngc else "")
            + (f"<h2>합격 {len(okc)}</h2><div class=g>{''.join(okc)}</div>" if okc else "")
            + "</div><script>const io=new IntersectionObserver(e=>e.forEach(x=>"
              "x.isIntersecting?x.target.play().catch(()=>0):x.target.pause()),{threshold:.3});"
              "document.querySelectorAll('video').forEach(v=>io.observe(v));</script>")
    open(OUT, "w", encoding="utf-8").write(html)
    print(f"\n  → {OUT}  (합격 {len(okc)} · 불합격 {len(ngc)})")
    if serve:
        p = port or free_port()
        subprocess.Popen([sys.executable, "-m", "http.server", str(p), "--bind", "127.0.0.1"],
                         cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        url = f"http://127.0.0.1:{p}/{OUT}"
        subprocess.Popen(["cmd", "/c", "start", "", url], shell=False)
        print(f"  브라우저: {url}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--no-serve", action="store_true")
    ap.add_argument("--files", action="store_true", help="검사 없이 폴더의 mp4 전부 나열(빠름)")
    a = ap.parse_args()
    fn = main_files if a.files else main
    raise SystemExit(fn(a.port, not a.no_serve))
