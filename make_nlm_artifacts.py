#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_nlm_artifacts.py — 강의 1개의 NotebookLM 6아티팩트(팟캐스트·슬라이드·노트 ×한/영)를
nlm services API로 직접 생성·다운로드. (제미나이 위임 불필요 — drjang00 로그인된 nlm 인증 사용.)

사용:
  python make_nlm_artifacts.py <base> <src_ko.txt> <src_en.txt> [outdir]
    base    : 파일 베이스 (예: w2d1) → dl_<base>_{podcast,slides,notes}{,_en}.{m4a,pdf,md}
    src_ko/en : 소스 텍스트 파일(강의 대본)
    outdir  : 다운로드 위치(기본 scratch/nlm)

플로우(언어별): notebook_create → source_add(text, wait) → studio create audio/slide_deck/report
           → studio_status 폴링(3개 completed) → download_async(audio/slides) + download(report)
출력: 각 파일 경로 + STUDIO_DONE. 이후 place 단계(web docs 복사 + 노트 md→pdf + 팟캐스트 R2)는 호출부에서.
"""
import os
import sys
import time
import asyncio

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from notebooklm_tools.mcp.tools._utils import get_client
from notebooklm_tools.services import notebooks, sources, studio, downloads

# (artifact_type, create-kwargs)
ART = [
    ("audio", {"audio_format": "deep_dive", "audio_length": "default"}),
    ("slide_deck", {"slide_format": "detailed_deck"}),
    ("report", {"report_format": "Study Guide"}),
]
LANGS = ["ko", "en"]
TARGETS = {"audio", "slide_deck", "report"}


def _nb_id(res):
    if isinstance(res, dict):
        return res.get("notebook_id") or res.get("id")
    return getattr(res, "notebook_id", None) or getattr(res, "id", None)


def build(base, srcmap, outdir):
    client = get_client()
    nbs = {}
    # 1) create notebook + add source + kick off 3 artifacts (per lang)
    for lang in LANGS:
        text = open(srcmap[lang], encoding="utf-8").read()
        nb = _nb_id(notebooks.create_notebook(client, title=f"drjayed {base} {lang}"))
        print(f"[{lang}] notebook {nb}", flush=True)
        sources.add_source(client, nb, "text", text=text, title=f"{base} {lang}",
                           wait=True, wait_timeout=300)
        for atype, kw in ART:
            studio.create_artifact(client, nb, atype, language=lang, **kw)
            print(f"  [{lang}] queued {atype}", flush=True)
        nbs[lang] = nb

    # 2) poll until all 3 completed (per lang)
    for lang, nb in nbs.items():
        deadline = time.time() + 1500
        while time.time() < deadline:
            st = studio.get_studio_status(client, nb)
            arts = st["artifacts"] if isinstance(st, dict) else st.artifacts
            comp = {a.get("type") for a in arts if a.get("status") == "completed"}
            if TARGETS <= comp:
                print(f"[{lang}] all 3 completed", flush=True)
                break
            time.sleep(20)
        else:
            print(f"[{lang}] TIMEOUT — completed={comp}", flush=True)

    # 3) download
    for lang, nb in nbs.items():
        sfx = "" if lang == "ko" else "_en"
        ap = f"{outdir}/dl_{base}_podcast{sfx}.m4a"
        sp = f"{outdir}/dl_{base}_slides{sfx}.pdf"
        rp = f"{outdir}/dl_{base}_notes{sfx}.md"
        try:
            asyncio.run(downloads.download_async(client, nb, "audio", ap))
            print(f"[{lang}] podcast -> {ap}", flush=True)
        except Exception as e:
            print(f"[{lang}] podcast FAIL {e}", flush=True)
        try:
            asyncio.run(downloads.download_async(client, nb, "slide_deck", sp, slide_deck_format="pdf"))
            print(f"[{lang}] slides -> {sp}", flush=True)
        except Exception as e:
            print(f"[{lang}] slides FAIL {e}", flush=True)
        try:
            downloads.download_sync(client, nb, "report", rp)
            print(f"[{lang}] notes -> {rp}", flush=True)
        except Exception as e:
            print(f"[{lang}] notes FAIL {e}", flush=True)
    print("STUDIO_DONE", flush=True)


if __name__ == "__main__":
    base = sys.argv[1]
    src_ko = sys.argv[2]
    src_en = sys.argv[3]
    outdir = sys.argv[4] if len(sys.argv) > 4 else "scratch/nlm"
    build(base, {"ko": src_ko, "en": src_en}, outdir)
