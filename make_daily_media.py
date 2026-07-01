#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_daily_media.py — 일일 강의(요일별)의 노트·PDF·오디오(팟캐스트) 생성 + R2/웹 업로드.

각 일일 강의(episode)에 대해:
 - 노트:  web/public/docs/hangeul_w{wk}d{day}_notes_{ko,en}.md   (씬 대본 기반 학습 노트)
 - PDF:   web/public/docs/hangeul_w{wk}d{day}_guide{,_en}.pdf     (노트 → chrome 헤드리스 인쇄)
 - 팟캐스트: R2 audio/podcasts/hangeul_w{wk}d{day}_podcast{,_en}.m4a  (렌더 영상의 나레이션 오디오)

사용: python make_daily_media.py            # 설정된 모든 일일 강의
"""
import os
import re
import sys
import json
import subprocess
import sqlite3

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")
DOCS = os.path.join(ROOT, "web", "public", "docs")
LOCAL = os.path.join(ROOT, "hangeul_birth_vowels")
os.makedirs(DOCS, exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# (episode, prefix, week, day)
JOBS = [
    ("KO-W01D2", "hangeul_w1d2_flat", 1, 2),
    ("KO-W01D3", "hangeul_w1d3_flat", 1, 3),
    ("KO-W01D4", "hangeul_w1d4_flat", 1, 4),
    ("KO-W01D5", "hangeul_w1d5_flat", 1, 5),
    ("KO-W01D6", "hangeul_w1d6_flat", 1, 6),
    ("KO-W01D7", "hangeul_w1d7_flat", 1, 7),
]


def _ff():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def load_scenes(ep):
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM scenes WHERE episode=? ORDER BY seq", (ep,)).fetchall()
    ttl = con.execute("SELECT title_kr,title_en FROM episodes WHERE code=?", (ep,)).fetchone()
    con.close()
    return rows, ttl


def build_notes(ep, lang):
    rows, ttl = load_scenes(ep)
    title = ttl["title_kr"] if lang == "ko" else ttl["title_en"]
    words = []
    out = [f"# {title}\n"]
    out.append(f"> {'drjay-ed · 훈민정음 일일 강의' if lang=='ko' else 'drjay-ed · Hunminjeongeum daily lesson'}\n")
    out.append(f"## {'학습 노트' if lang=='ko' else 'Study Notes'}\n")
    for s in rows:
        spec = json.loads(s["image_prompt"])
        cap = spec.get("cap_ko") if lang == "ko" else spec.get("cap_en")
        script = s["script_kr"] if lang == "ko" else s["script_en"]
        words += spec.get("words") or []
        out.append(f"### {s['seq']}. {cap}\n")
        out.append(script + "\n")
    uniq = []
    for w in words:
        if w not in uniq:
            uniq.append(w)
    if uniq:
        out.append(f"## {'오늘의 단어' if lang=='ko' else 'Key Words'}\n")
        out.append(" · ".join(uniq) + "\n")
    return "\n".join(out)


_HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 20mm; }}
body {{ font-family: 'Malgun Gothic','Segoe UI',sans-serif; color:#2b2620; line-height:1.6; }}
h1 {{ color:#1f7a44; border-bottom:3px solid #4cae6e; padding-bottom:8px; }}
h2 {{ color:#1f7a44; margin-top:24px; }}
h3 {{ color:#444; margin-top:18px; }}
blockquote {{ color:#888; border-left:3px solid #ddd; padding-left:12px; }}
</style></head><body>{body}</body></html>"""


def md_to_html(md):
    # 아주 가벼운 markdown → HTML (제목/인용/문단)
    html = []
    for ln in md.split("\n"):
        if ln.startswith("### "):
            html.append(f"<h3>{ln[4:]}</h3>")
        elif ln.startswith("## "):
            html.append(f"<h2>{ln[3:]}</h2>")
        elif ln.startswith("# "):
            html.append(f"<h1>{ln[2:]}</h1>")
        elif ln.startswith("> "):
            html.append(f"<blockquote>{ln[2:]}</blockquote>")
        elif ln.strip():
            html.append(f"<p>{ln}</p>")
    return _HTML.format(body="\n".join(html))


def make_pdf(html, out_pdf):
    tmp = out_pdf + ".html"
    open(tmp, "w", encoding="utf-8").write(html)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                    f"--print-to-pdf={out_pdf}", "--print-to-pdf-no-header",
                    "file:///" + tmp.replace("\\", "/")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    try:
        os.remove(tmp)
    except Exception:
        pass
    return os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 2000


# ---------- 슬라이드 덱 PDF (가로, 씬당 1장) ----------
_SLIDE_HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: 1280px 720px; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; font-family:'Malgun Gothic','Segoe UI',sans-serif; color:#2b2620; }}
.slide {{ width:1280px; height:720px; page-break-after:always; padding:64px 80px;
  display:flex; flex-direction:column; justify-content:center; position:relative;
  background:linear-gradient(135deg,#f3faf5,#fff); }}
.slide.cover {{ background:linear-gradient(135deg,#2f9e63,#7fd0a0); color:#fff; align-items:center; text-align:center; }}
.cover h1 {{ font-size:62px; margin:0 0 18px; }}
.cover p {{ font-size:30px; opacity:.95; margin:0; }}
.s-no {{ position:absolute; top:40px; left:80px; font-size:22px; font-weight:800; color:#1f7a44; }}
.s-brand {{ position:absolute; bottom:36px; right:80px; font-size:20px; color:#9a9085; }}
.s-cap {{ font-size:50px; font-weight:800; color:#1f7a44; line-height:1.2; }}
.s-words {{ font-size:120px; font-weight:800; color:#222; margin:8px 0 18px; letter-spacing:6px; }}
.s-body {{ font-size:32px; line-height:1.55; color:#3a352f; }}
</style></head><body>{body}</body></html>"""


def build_slides(ep, lang):
    rows, ttl = load_scenes(ep)
    title = ttl["title_kr"] if lang == "ko" else ttl["title_en"]
    brand = "drjay-ed · 훈민정음" if lang == "ko" else "drjay-ed · Hunminjeongeum"
    slides = [f'<div class="slide cover"><h1>{title}</h1><p>{brand}</p></div>']
    n = len(rows)
    for i, s in enumerate(rows, 1):
        spec = json.loads(s["image_prompt"])
        cap = spec.get("cap_ko") if lang == "ko" else spec.get("cap_en")
        script = s["script_kr"] if lang == "ko" else s["script_en"]
        words = spec.get("words") or []
        whtml = f'<div class="s-words">{" ".join(words[:3])}</div>' if words else ""
        slides.append(
            f'<div class="slide"><span class="s-no">{i} / {n}</span>'
            f'<div class="s-cap">{cap}</div>{whtml}<div class="s-body">{script}</div>'
            f'<span class="s-brand">{brand}</span></div>')
    return _SLIDE_HTML.format(body="\n".join(slides))


def extract_audio(prefix, lang, out_m4a):
    vid = os.path.join(LOCAL, f"{prefix}_{lang}.mp4")
    if not os.path.exists(vid):
        return False
    subprocess.run([_ff(), "-y", "-i", vid, "-vn", "-c:a", "aac", "-b:a", "128k", out_m4a],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return os.path.exists(out_m4a) and os.path.getsize(out_m4a) > 2000


def r2():
    import boto3
    env = {}
    for ln in open(os.path.join(ROOT, "..", "parkgolftour", ".env"), encoding="utf-8"):
        if ln.startswith("CF_R2_"):
            k, _, v = ln.strip().partition("=")
            env[k] = v
    return boto3.client("s3", endpoint_url=env["CF_R2_ENDPOINT"],
                        aws_access_key_id=env["CF_R2_ACCESS_KEY_ID"],
                        aws_secret_access_key=env["CF_R2_SECRET_ACCESS_KEY"], region_name="auto")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="이 문자열을 episode/base에 포함하는 강의만 처리(예: hangeul_w1d6 또는 KO-W01D6)")
    args = ap.parse_args()
    s3 = r2()
    scratch = os.path.join(ROOT, "scratch", "daily_audio")
    os.makedirs(scratch, exist_ok=True)
    # 일일 강의(화~) + 월요일(주차 핵심)을 함께 — (episode, prefix, base, audio_from_video)
    targets = [(ep, prefix, f"hangeul_w{wk}d{day}", True) for ep, prefix, wk, day in JOBS]
    targets.append(("KO-W01", "hangeul_w1_stickman", "hangeul_week_1", False))  # 월요일=주차 핵심
    if args.only:
        targets = [t for t in targets if args.only in t[0] or args.only in t[1] or args.only in t[2]]
    for ep, prefix, base, aud_from_vid in targets:
        done = []
        for lang in ("ko", "en"):
            sfx = "" if lang == "ko" else "_en"
            # 노트(텍스트) PDF — 깔끔/모바일
            notes = build_notes(ep, lang)
            open(os.path.join(DOCS, f"{base}_notes_{lang}.md"), "w", encoding="utf-8").write(notes)
            ok_note = make_pdf(md_to_html(notes), os.path.join(DOCS, f"{base}_guide{sfx}.pdf"))
            # 슬라이드 PDF (가로, 씬당 1장)
            ok_slide = make_pdf(build_slides(ep, lang), os.path.join(DOCS, f"{base}_slides{sfx}.pdf"))
            # 팟캐스트(오디오) — 영상에서 추출(월요일은 기존 NotebookLM 팟캐스트 유지)
            ok_aud = "-"
            if aud_from_vid:
                m4a = os.path.join(scratch, f"{base}_podcast{sfx}.m4a")
                if extract_audio(prefix, lang, m4a):
                    s3.upload_file(m4a, "drjayed-media", f"audio/podcasts/{base}_podcast{sfx}.m4a",
                                   ExtraArgs={"ContentType": "audio/mp4"})
                    ok_aud = "✓"
                else:
                    ok_aud = "✗"
            done.append(f"{lang}:note{'✓' if ok_note else '✗'} slide{'✓' if ok_slide else '✗'} pod{ok_aud}")
        print(f"{base}: " + " | ".join(done))


if __name__ == "__main__":
    main()
