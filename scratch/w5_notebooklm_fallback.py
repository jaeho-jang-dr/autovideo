#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""w5_notebooklm_fallback.py — W5 NotebookLM 셸 폴백(Claude).
 0) in_progress 아티팩트(팟캐스트 ko/en, EN 리포트) 완료까지 폴링(최대 ~25분)
 1) 리포트 ko/en 다운로드 → guide md → PDF (web/public/docs)
 2) 팟캐스트 ko/en 다운로드 → R2 (ko=무접미사, en=_en)
 3) 노트 ko/en 재생성 — 제미나이 스텁(플레이스홀더)을 리포트 요약으로 교체
재실행: python scratch/w5_notebooklm_fallback.py
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
WK = 5
DOCS = os.path.join(ROOT, "web", "public", "docs")
POD = os.path.join(ROOT, "scratch", "web_media_offloaded", "audio", "podcasts")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
c = N.make_client("default")

REPORTS = {"ko": "5feede38-cc59-4ad7-b454-b08b550a2e7a",
           "en": "6baf959a-7916-414e-84f7-ce996c4a0a11"}
PODCASTS = {"ko": "eaf32149-1ff3-46d8-837a-9392a6bbcb0e",
            "en": "70525bb3-e5d6-44d7-a1b4-9f88af548441"}
WATCH = [PODCASTS["ko"], PODCASTS["en"], REPORTS["en"]]   # in_progress 가능

HTML_TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
 @page {{ size: A4; margin: 18mm; }}
 body {{ font-family:'Malgun Gothic','맑은 고딕',sans-serif; font-size:12pt; line-height:1.6; color:#222; }}
 h1 {{ font-size:20pt; border-bottom:3px solid #6a4fa0; padding-bottom:6px; }}
 h2 {{ font-size:15pt; color:#4a3a96; margin-top:18px; }}
 h3 {{ font-size:13pt; }} code {{ background:#f3f3ee; padding:1px 4px; }}
 ul {{ margin:4px 0 4px 18px; }}
</style></head><body>{body}</body></html>"""


def aw(v):
    return asyncio.run(v) if inspect.iscoroutine(v) else v


def statuses():
    st = aw(c.get_studio_status(NB))
    arts = st if isinstance(st, list) else st.get("artifacts", st)
    out = {}
    for a in (arts if isinstance(arts, list) else []):
        out[a.get("id") or a.get("artifact_id")] = a.get("status")
    return out


def poll():
    for i in range(50):                       # ~25분
        s = statuses()
        st = {a: s.get(a, "?") for a in WATCH}
        print("  poll:", st, flush=True)
        if all(v == "completed" for v in st.values()):
            return True
        time.sleep(30)
    print("  TIMEOUT — proceeding with whatever is ready")
    return False


def get_report(lang, aid):
    out = os.path.join(ROOT, "scratch", f"hangeul_week_{WK}_guide_{lang}.md")
    try:
        aw(c.download_report(NB, out, artifact_id=aid))
        sz = os.path.getsize(out) if os.path.exists(out) else 0
        print(f"  report {lang}: {sz} bytes")
        return out if sz > 200 else None
    except Exception as e:
        print(f"  report {lang} FAIL: {e}")
        return None


def to_pdf(lang, mdpath):
    if not mdpath or not os.path.exists(mdpath):
        print(f"  pdf {lang}: no md"); return
    body = md.markdown(open(mdpath, encoding="utf-8").read(), extensions=["extra", "sane_lists"])
    html = os.path.join(ROOT, "scratch", f"_guide5_{lang}.html")
    open(html, "w", encoding="utf-8").write(HTML_TPL.format(body=body))
    # ko => _guide.pdf (무접미사), en => _guide_en.pdf  (사이트 규칙과 일치)
    name = f"hangeul_week_{WK}_guide.pdf" if lang == "ko" else f"hangeul_week_{WK}_guide_en.pdf"
    out = os.path.join(DOCS, name)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", "file:///" + html.replace("\\", "/")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    print(f"  pdf {lang}: {os.path.getsize(out)//1024 if os.path.exists(out) else 0}KB -> {name}")


def make_notes(lang, mdpath):
    """리포트 md → 압축 요약 노트(제미나이 스텁 교체)."""
    if not mdpath or not os.path.exists(mdpath):
        print(f"  notes {lang}: no source"); return
    txt = open(mdpath, encoding="utf-8").read()
    lines = txt.splitlines()
    out_lines, body_chars = [], 0
    title = "이중모음과 반모음 활주" if lang == "ko" else "Double Vowels & Semivowel Glides"
    head = (f"# [초급 5주차] {title} — 핵심 요약 노트\n" if lang == "ko"
            else f"# [Beginner Week 5] {title} — Key Summary Notes\n")
    out_lines.append(head)
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#"):                       # 제목 유지
            out_lines.append(ln)
        elif body_chars < 2200:                     # 본문은 앞부분만(요약)
            out_lines.append(ln)
            body_chars += len(s)
    note = "\n".join(out_lines)
    out = os.path.join(DOCS, f"hangeul_week_{WK}_notes_{lang}.md")
    open(out, "w", encoding="utf-8").write(note)
    print(f"  notes {lang}: {len(note)} bytes -> {os.path.basename(out)}")


def r2():
    env = {}
    for ln in open(os.path.join(ROOT, "..", "parkgolftour", ".env"), encoding="utf-8"):
        if ln.startswith("CF_R2_"):
            k, _, v = ln.strip().partition("="); env[k] = v
    return boto3.client("s3", endpoint_url=env["CF_R2_ENDPOINT"], aws_access_key_id=env["CF_R2_ACCESS_KEY_ID"],
                        aws_secret_access_key=env["CF_R2_SECRET_ACCESS_KEY"], region_name="auto")


def get_podcast(lang, aid, s3):
    os.makedirs(POD, exist_ok=True)
    out = os.path.join(POD, f"hangeul_week_{WK}_podcast_{lang}.m4a")
    try:
        aw(c.download_audio(NB, out, artifact_id=aid))
        sz = os.path.getsize(out) if os.path.exists(out) else 0
        if sz < 10000:
            print(f"  podcast {lang}: {sz} bytes (not ready) — skip"); return
        key = f"audio/podcasts/hangeul_week_{WK}_podcast{'' if lang == 'ko' else '_en'}.m4a"
        s3.upload_file(out, "drjayed-media", key, ExtraArgs={"ContentType": "audio/mp4"})
        print(f"  podcast {lang}: {sz//1024//1024}MB -> R2:{key}")
    except Exception as e:
        print(f"  podcast {lang} FAIL: {e}")


def main():
    os.makedirs(DOCS, exist_ok=True)
    print("0) poll in-progress artifacts")
    poll()
    print("1) reports + PDF + notes")
    mds = {lang: get_report(lang, aid) for lang, aid in REPORTS.items()}
    for lang in ("ko", "en"):
        to_pdf(lang, mds.get(lang))
        make_notes(lang, mds.get(lang))
    print("2) podcasts -> R2")
    s3 = r2()
    for lang, aid in PODCASTS.items():
        get_podcast(lang, aid, s3)
    print("DONE")


if __name__ == "__main__":
    main()
