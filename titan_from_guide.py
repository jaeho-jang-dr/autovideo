#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""titan_from_guide.py — 가이드 이미지를 프롬프트에 붙여 8초 클립을 만든다.

★새로 만든 절차가 아니다. 검증된 것을 **호출만** 한다.
   업로드/프롬프트첨부 = flow_walk_from_ref.attach_media
   설정 칩          = flow_make_group_w24.set_chip
   내려받기         = flow_make_group_w24.fetch_video

★사장님 절차(2026-08-10)
   우상단 + → 미디어 추가 → 25초 후 타일 더보기(⋮) → 프롬프트에 추가
   → 동영상 세팅 확인 → 프롬프트 넣고 실행 → 90초 후 왼편 타일 다운로드

  python titan_from_guide.py --image titan_science/keyframes/s05_guide.png \
                             --prompt-file titan_science/prompts/s05_motion.txt \
                             --out titan_science/keyframes/s05_femur.mp4
"""
import argparse
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from playwright.sync_api import sync_playwright        # noqa: E402
import flow_cdp_pipeline as P                          # noqa: E402
import flow_make_group_w24 as G                        # noqa: E402
import flow_walk_from_ref as W                         # noqa: E402
import autoveo_flow as avf                             # noqa: E402

GEN_WAIT = 180          # 90초 뒤부터 확인, 최대 180초


def log(m):
    print(m, flush=True)


def run(image, prompt, out):
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    P.launch_chrome(os.path.abspath("assets/chrome_profile"))
    time.sleep(3)
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(P.CDP_URL)
        ctx = b.contexts[0]
        pg = next((p for p in ctx.pages if "labs.google" in p.url), None) or ctx.pages[0]
        pg.bring_to_front()
        pg.set_default_timeout(30000)

        log("[1] 새 프로젝트")
        avf.open_new_project(pg)
        pg.wait_for_timeout(3000)

        log("[2] 가이드 이미지 업로드 → 프롬프트에 추가")
        if not W.attach_media(pg, image):
            raise RuntimeError("업로드/프롬프트 첨부 실패")

        log("[3] 동영상 · Veo 3.1 Lite · 16:9 · 8초")
        if not G.set_chip(pg):
            raise RuntimeError("설정 칩 실패")

        log("[4] 프롬프트 → 만들기")
        before = set(pg.evaluate(
            "() => [...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src||'').filter(Boolean)"))
        avf.fill_prompt(pg, prompt)
        pg.wait_for_timeout(1200)
        if not avf.generate(pg):
            raise RuntimeError("'만들기' 클릭 실패")

        log(f"[5] 생성 대기 (최대 {GEN_WAIT}초)")
        src = None
        for i in range(GEN_WAIT // 15):
            pg.wait_for_timeout(15000)
            now = [s for s in pg.evaluate(
                "() => [...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src||'').filter(Boolean)")
                if s not in before]
            if now:
                src = now[0]
                log(f"    {(i+1)*15}s — 새 미디어 확인")
                break
        if not src:
            raise RuntimeError("생성 실패(시간 초과)")

        log("[6] 내려받기")
        if not G.fetch_video(pg, out, src):
            raise RuntimeError("내려받기 실패")
        log(f"✅ {out}  {os.path.getsize(out)//1024}KB")
        return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pr = re.sub(r"\s+", " ", open(a.prompt_file, encoding="utf-8").read()).strip()
    sys.exit(0 if run(a.image, pr, a.out) else 1)
