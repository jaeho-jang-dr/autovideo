# -*- coding: utf-8 -*-
"""쇼츠 편집 페이지의 썸네일/표지 UI 탐침 — 업로드 가능한지 확인용(변경 안 함)."""
import sys, os, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
os.makedirs("scratch/yt", exist_ok=True)
def log(*a): print(*a, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    # 썸네일 에디터 영역 탐색
    for sel in ["ytcp-video-thumbnail-editor","ytcp-video-thumbnail-editor-v2",
                "#thumbnail-container","ytcp-thumbnail-uploader","#still-picker","ytse-shorts-cover-picker"]:
        loc = pg.locator(sel)
        try:
            n = loc.count()
        except Exception:
            n = 0
        log(f"[{sel}] count={n}")
    # 관련 버튼/텍스트 덤프
    for txt in ["파일 업로드","썸네일 업로드","표지","표지 편집","자동","프레임","맞춤 썸네일","Upload file","커버"]:
        try:
            c = pg.get_by_text(txt, exact=False).count()
            if c: log(f"  텍스트 '{txt}' x{c}")
        except Exception: pass
    # input[type=file] 존재?
    try: log("input[type=file] 개수:", pg.locator("input[type=file]").count())
    except Exception: pass
    pg.screenshot(path="scratch/yt/probe_thumb.png", full_page=True)
    log("스크린샷: scratch/yt/probe_thumb.png")
    ctx.close()
print("PROBE_DONE")
