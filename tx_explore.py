# -*- coding: utf-8 -*-
"""번역/자막 페이지 탐색: 원본언어·언어행·버튼 구조 덤프. 사용: python tx_explore.py <VID>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
os.makedirs("scratch/yt", exist_ok=True)
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
        no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(40000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
    pg.screenshot(path="scratch/yt/tx0_page.png", full_page=True)
    print("URL:", pg.url, flush=True)
    body = ""
    try: body = pg.inner_text("body")
    except Exception: pass
    for kw in ["원본", "언어 추가", "동영상의 언어", "제목 및 설명", "자막", "한국어", "영어", "English", "Korean", "게시됨", "초안", "추가"]:
        if kw in body: print("HIT:", kw, flush=True)
    # 버튼/추가 요소 후보
    for sel in ["ytgn-video-translation-language-row", "ytcp-video-translations",
                "tp-yt-paper-listbox", "ytcp-form-select", "ytcp-button:has-text('언어 추가')",
                "#add-translations-button", "#add-language-button", "[aria-label*='언어']"]:
        try: print(f"COUNT {sel}: {pg.locator(sel).count()}", flush=True)
        except Exception: pass
    # 언어행 텍스트 나열
    try:
        rows = pg.locator("ytgn-video-translation-language-row, [class*='language-row'], tr").all()
        print("행 후보 수:", len(rows), flush=True)
        for r in rows[:15]:
            try:
                t = r.inner_text()[:60].replace("\n", " | ")
                if t.strip(): print("ROW:", t, flush=True)
            except Exception: pass
    except Exception as e: print("행 덤프 실패", str(e)[:60], flush=True)
    pg.wait_for_timeout(3000); ctx.close()
print("END")
