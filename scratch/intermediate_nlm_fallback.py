#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""intermediate_nlm_fallback.py — 중급 W9~15 NotebookLM 셸 폴백(제너릭).
각 주차 scratch/gemini_w{w}_report.md 에서 artifact UUID 추출 → studio_status로 type(audio/report)·title·언어 자동 분류
→ 완료까지 폴링 → 리포트 다운로드(md→PDF→요약노트), 팟캐스트 다운로드→R2.
ko=무접미사, en=_en 규칙(사이트와 일치). 재실행: python scratch/intermediate_nlm_fallback.py [week ...]
"""
import os
import sys
import re
import time
import asyncio
import inspect
import subprocess

sys.path.insert(0, r"C:/Users/antigravity/.notebooklm/bin")
import nlm_common as N
import markdown as md
import boto3

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB = "cc6092e5-3322-44e8-b65e-dc0e85c2e3ed"
DOCS = os.path.join(ROOT, "web", "public", "docs")
POD = os.path.join(ROOT, "scratch", "web_media_offloaded", "audio", "podcasts")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
c = N.make_client("default")

HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
@page{{size:A4;margin:18mm}} body{{font-family:'Malgun Gothic',sans-serif;font-size:12pt;line-height:1.6;color:#222}}
h1{{font-size:20pt;border-bottom:3px solid #2a6a9a;padding-bottom:6px}} h2{{font-size:15pt;color:#1a4a7a;margin-top:18px}}
ul{{margin:4px 0 4px 18px}}</style></head><body>{body}</body></html>"""

TITLE = {9: ("우리 동네와 위치 표현", "Neighborhood & Locations"), 10: ("상점 구매와 가격 묻기", "Shopping & Asking Prices"),
         11: ("식당 이용과 맛 표현", "Food Ordering & Dining"), 12: ("교통수단과 지하철 환승", "Transportation & Subway"),
         13: ("길 찾기와 위치 안내", "Directions & Wayfinding"), 14: ("나의 하루 일과와 동작", "Daily Routines & Verbs"),
         15: ("날씨와 아름다운 사계절", "Weather & Four Seasons")}


def aw(v):
    return asyncio.run(v) if inspect.iscoroutine(v) else v


def all_status():
    st = aw(c.get_studio_status(NB))
    arts = st if isinstance(st, list) else st.get("artifacts", st)
    m = {}
    for a in (arts if isinstance(arts, list) else []):
        aid = a.get("id") or a.get("artifact_id")
        m[aid] = {"type": a.get("artifact_type") or a.get("type"),
                  "status": a.get("status"), "title": a.get("title") or ""}
    return m


def is_ko(s):
    return any("가" <= ch <= "힣" for ch in (s or ""))


def classify(ids, smap):
    """4개 id → {podcast_ko, podcast_en, report_ko, report_en}."""
    out = {}
    for aid in ids:
        info = smap.get(aid)
        if not info:
            continue
        typ = (info["type"] or "").lower()
        kind = "podcast" if "audio" in typ else ("report" if "report" in typ else None)
        if not kind:
            continue
        lang = "ko" if is_ko(info["title"]) else "en"
        out.setdefault(f"{kind}_{lang}", aid)
    return out


def r2():
    env = {}
    for ln in open(os.path.join(ROOT, "..", "parkgolftour", ".env"), encoding="utf-8"):
        if ln.startswith("CF_R2_"):
            k, _, v = ln.strip().partition("="); env[k] = v
    return boto3.client("s3", endpoint_url=env["CF_R2_ENDPOINT"], aws_access_key_id=env["CF_R2_ACCESS_KEY_ID"],
                        aws_secret_access_key=env["CF_R2_SECRET_ACCESS_KEY"], region_name="auto")


def to_pdf(w, lang, mdpath):
    body = md.markdown(open(mdpath, encoding="utf-8").read(), extensions=["extra", "sane_lists"])
    html = os.path.join(ROOT, "scratch", f"_ig_{w}_{lang}.html")
    open(html, "w", encoding="utf-8").write(HTML.format(body=body))
    name = f"hangeul_week_{w}_guide.pdf" if lang == "ko" else f"hangeul_week_{w}_guide_en.pdf"
    out = os.path.join(DOCS, name)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", "file:///" + html.replace("\\", "/")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    print(f"    pdf {lang}: {os.path.getsize(out)//1024 if os.path.exists(out) else 0}KB")


def make_notes(w, lang, mdpath):
    txt = open(mdpath, encoding="utf-8").read().splitlines()
    tko, ten = TITLE[w]
    head = f"# [중급 {w-8}주차] {tko} — 핵심 요약 노트\n" if lang == "ko" else f"# [Intermediate Week {w-8}] {ten} — Key Summary Notes\n"
    out_lines, body = [head], 0
    for ln in txt:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#"):
            out_lines.append(ln)
        elif body < 2200:
            out_lines.append(ln); body += len(s)
    out = os.path.join(DOCS, f"hangeul_week_{w}_notes_{lang}.md")
    open(out, "w", encoding="utf-8").write("\n".join(out_lines))
    print(f"    notes {lang}: {os.path.getsize(out)} bytes")


def process_week(w, s3):
    rep = os.path.join(ROOT, "scratch", f"gemini_w{w}_report.md")
    if not os.path.exists(rep):
        print(f"  W{w}: no report"); return
    ids = [u for u in dict.fromkeys(UUID.findall(open(rep, encoding="utf-8").read())) if u != NB]
    smap = all_status()
    cls = classify(ids, smap)
    print(f"  W{w}: ids={len(ids)} classified={list(cls.keys())}")
    # poll until the 4 are completed (max ~12 min/week)
    for _ in range(24):
        smap = all_status()
        st = {k: smap.get(v, {}).get("status") for k, v in cls.items()}
        if all(v == "completed" for v in st.values()) and len(cls) == 4:
            break
        time.sleep(30)
    # reports -> md/pdf/notes
    for lang in ("ko", "en"):
        aid = cls.get(f"report_{lang}")
        if not aid:
            continue
        mdp = os.path.join(ROOT, "scratch", f"hangeul_week_{w}_guide_{lang}.md")
        try:
            aw(c.download_report(NB, mdp, artifact_id=aid))
            if os.path.exists(mdp) and os.path.getsize(mdp) > 200:
                to_pdf(w, lang, mdp); make_notes(w, lang, mdp)
        except Exception as e:
            print(f"    report {lang} FAIL: {e}")
    # podcasts -> R2
    for lang in ("ko", "en"):
        aid = cls.get(f"podcast_{lang}")
        if not aid:
            continue
        os.makedirs(POD, exist_ok=True)
        out = os.path.join(POD, f"hangeul_week_{w}_podcast_{lang}.m4a")
        try:
            aw(c.download_audio(NB, out, artifact_id=aid))
            sz = os.path.getsize(out) if os.path.exists(out) else 0
            if sz < 10000:
                print(f"    podcast {lang}: {sz}B not ready"); continue
            key = f"audio/podcasts/hangeul_week_{w}_podcast{'' if lang == 'ko' else '_en'}.m4a"
            s3.upload_file(out, "drjayed-media", key, ExtraArgs={"ContentType": "audio/mp4"})
            print(f"    podcast {lang}: {sz//1024//1024}MB -> R2")
        except Exception as e:
            print(f"    podcast {lang} FAIL: {e}")


def main():
    weeks = [int(a) for a in sys.argv[1:]] or list(range(9, 16))
    os.makedirs(DOCS, exist_ok=True)
    s3 = r2()
    for w in weeks:
        process_week(w, s3)
    print("DONE")


if __name__ == "__main__":
    main()
