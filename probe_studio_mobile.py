# -*- coding: utf-8 -*-
"""모바일 UA로 studio.youtube.com 편집 페이지 열어 쇼츠 표지 업로드 UI 있는지 탐침."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
UA = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Mobile Safari/537.36")
os.makedirs("scratch/yt", exist_ok=True)
def log(*a): print(*a, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        user_agent=UA, viewport={"width":412,"height":915}, is_mobile=True, has_touch=True,
        locale="ko-KR", ignore_default_args=["--enable-automation"],
        args=["--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(35000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded")
    pg.wait_for_timeout(10000)
    log("URL:", pg.url)
    for txt in ["썸네일","표지","파일 업로드","업로드","프레임","자동","모바일 앱","커버","맞춤","동영상 표지"]:
        try:
            c = pg.get_by_text(txt, exact=False).count()
            if c: log(f"  텍스트 '{txt}' x{c}")
        except Exception: pass
    try: log("input[type=file]:", pg.locator("input[type=file]").count())
    except Exception: pass
    # 썸네일 에디터 관련 커스텀 엘리먼트
    for sel in ["ytcp-video-thumbnail-editor","#thumbnail-container","ytcp-thumbnail-uploader",
                "#file-loader","ytse-cover-editor"]:
        try:
            n=pg.locator(sel).count()
            if n: log(f"  [{sel}] x{n}")
        except Exception: pass
    pg.screenshot(path="scratch/yt/studio_mobile.png", full_page=True)
    log("shot: scratch/yt/studio_mobile.png")
    ctx.close()
print("DONE")
