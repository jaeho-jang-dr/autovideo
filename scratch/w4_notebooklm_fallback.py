#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""w4_notebooklm_fallback.py — 제미나이가 못 한 셸 작업(다운로드/PDF/R2)을 Claude가 폴백.
 1) KO 리포트(a1be35f4=실제 한국어) 재다운로드 → guide_ko.md (Gemini가 영어로 잘못 받았던 것 교정)
 2) guide_{ko,en}.md → web/public/docs/hangeul_week_4_guide_{ko,en}.pdf (markdown→HTML→chrome headless)
 3) 팟캐스트 EN(16cbe7e8)·KO(7362558f) 다운로드 → R2(drjayed-media) audio/podcasts/
재실행: python scratch/w4_notebooklm_fallback.py
"""
import os
import sys
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
c = N.make_client("default")

REPORTS = {"ko": "a1be35f4-d139-412f-8a06-e990fcd0c7b8",
           "en": "c87c9641-931c-4912-898c-0e47cbbaf3db"}
PODCASTS = {"en": "16cbe7e8-1462-4c9c-a49a-aa9a75448c6c",
            "ko": "7362558f-102d-400d-ab18-14c1c973b451"}

HTML_TPL = """<!doctype html><html><head><meta charset="utf-8">
<style>
 @page {{ size: A4; margin: 18mm; }}
 body {{ font-family:'Malgun Gothic','맑은 고딕',sans-serif; font-size:12pt; line-height:1.6; color:#222; }}
 h1 {{ font-size:20pt; border-bottom:3px solid #2a968a; padding-bottom:6px; }}
 h2 {{ font-size:15pt; color:#16645c; margin-top:18px; }}
 h3 {{ font-size:13pt; color:#333; }}
 code {{ background:#f3f3ee; padding:1px 4px; }}
 ul {{ margin:4px 0 4px 18px; }}
</style></head><body>{body}</body></html>"""


def aw(v):
    return asyncio.run(v) if inspect.iscoroutine(v) else v


def get_report(lang, aid):
    out = os.path.join(ROOT, "scratch", f"hangeul_week_4_guide_{lang}.md")
    try:
        aw(c.download_report(NB, out, artifact_id=aid))
        sz = os.path.getsize(out) if os.path.exists(out) else 0
        print(f"  report {lang}: {sz} bytes -> {out}")
        return out if sz > 200 else None
    except Exception as e:
        print(f"  report {lang} FAIL: {e}")
        return out if os.path.exists(out) else None


def to_pdf(lang, mdpath):
    if not mdpath or not os.path.exists(mdpath):
        print(f"  pdf {lang}: no md"); return
    body = md.markdown(open(mdpath, encoding="utf-8").read(), extensions=["extra", "sane_lists"])
    html = os.path.join(ROOT, "scratch", f"_guide_{lang}.html")
    open(html, "w", encoding="utf-8").write(HTML_TPL.format(body=body))
    out = os.path.join(DOCS, f"hangeul_week_4_guide_{lang}.pdf")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", "file:///" + html.replace("\\", "/")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    sz = os.path.getsize(out) if os.path.exists(out) else 0
    print(f"  pdf {lang}: {sz//1024}KB -> {out}")


def r2():
    env = {}
    for ln in open(os.path.join(ROOT, "..", "parkgolftour", ".env"), encoding="utf-8"):
        if ln.startswith("CF_R2_"):
            k, _, v = ln.strip().partition("="); env[k] = v
    return boto3.client("s3", endpoint_url=env["CF_R2_ENDPOINT"], aws_access_key_id=env["CF_R2_ACCESS_KEY_ID"],
                        aws_secret_access_key=env["CF_R2_SECRET_ACCESS_KEY"], region_name="auto")


def get_podcast(lang, aid, s3):
    os.makedirs(POD, exist_ok=True)
    out = os.path.join(POD, f"hangeul_week_4_podcast_{lang}.m4a")
    try:
        aw(c.download_audio(NB, out, artifact_id=aid))
        sz = os.path.getsize(out) if os.path.exists(out) else 0
        if sz < 10000:
            print(f"  podcast {lang}: only {sz} bytes (not ready?) — skip R2"); return
        key = f"audio/podcasts/hangeul_week_4_podcast_{lang}.m4a"
        s3.upload_file(out, "drjayed-media", key, ExtraArgs={"ContentType": "audio/mp4"})
        print(f"  podcast {lang}: {sz//1024//1024}MB -> R2:{key}")
    except Exception as e:
        print(f"  podcast {lang} FAIL: {e}")


def main():
    os.makedirs(DOCS, exist_ok=True)
    print("1) reports (KO re-download to fix language) + PDF")
    mds = {lang: get_report(lang, aid) for lang, aid in REPORTS.items()}
    for lang in ("ko", "en"):
        to_pdf(lang, mds.get(lang) or os.path.join(ROOT, "scratch", f"hangeul_week_4_guide_{lang}.md"))
    print("2) podcasts -> R2")
    s3 = r2()
    for lang, aid in PODCASTS.items():
        get_podcast(lang, aid, s3)
    print("DONE")


if __name__ == "__main__":
    main()
