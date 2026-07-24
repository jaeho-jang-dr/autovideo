# -*- coding: utf-8 -*-
"""모바일 웹(m.youtube.com)에서 내 쇼츠 표지(썸네일) 편집 경로가 있는지 탐침."""
import sys, os, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")
os.makedirs("scratch/yt", exist_ok=True)
def log(*a): print(*a, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        user_agent=IPHONE_UA, viewport={"width":414,"height":896}, is_mobile=True, has_touch=True,
        locale="ko-KR", ignore_default_args=["--enable-automation"],
        args=["--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    # 내 동영상 페이지로
    pg.goto(f"https://m.youtube.com/watch?v={VID}", wait_until="domcontentloaded")
    pg.wait_for_timeout(7000)
    pg.screenshot(path="scratch/yt/m_watch.png")
    # 편집/수정 관련 텍스트 탐색
    found=[]
    for txt in ["수정","동영상 수정","편집","썸네일","표지","Edit","Edit video","Thumbnail","맞춤 미리보기 이미지","분석","동영상 관리"]:
        try:
            c=pg.get_by_text(txt, exact=False).count()
            if c: found.append(f"{txt} x{c}")
        except Exception: pass
    log("모바일 텍스트:", found)
    log("input[type=file]:", pg.locator("input[type=file]").count())
    ctx.close()
print("MPROBE_DONE")
