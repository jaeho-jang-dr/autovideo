# -*- coding: utf-8 -*-
"""정주행 본편(wJUAiZW5fW0) 재생 가능 화질(업스케일/HD/4K 처리 완료) 확인."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = "wJUAiZW5fW0"
def log(m): print(m, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu", "--autoplay-policy=no-user-gesture-required"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto(f"https://www.youtube.com/watch?v={VID}", wait_until="domcontentloaded")
    pg.wait_for_timeout(7000)
    # 광고/재생 유도
    try: pg.keyboard.press("k")
    except Exception: pass
    pg.wait_for_timeout(4000)
    os.makedirs("scratch/yt", exist_ok=True)
    info = {}
    for attempt in range(6):
        try:
            info = pg.evaluate("""() => {
              const p = document.getElementById('movie_player');
              if (!p || !p.getAvailableQualityLevels) return {ready:false};
              return {
                ready:true,
                levels: p.getAvailableQualityLevels(),
                current: p.getPlaybackQuality ? p.getPlaybackQuality() : '',
                data: p.getVideoData ? p.getVideoData() : {}
              };
            }""")
            if info.get("ready") and info.get("levels"):
                break
        except Exception as e:
            info = {"err": str(e)[:80]}
        pg.wait_for_timeout(3000)
    log("=== 화질 조회 결과 ===")
    log(str(info))
    lv = info.get("levels", []) if isinstance(info, dict) else []
    has4k = any(x in lv for x in ["hd2160","highres"])
    has1440 = "hd1440" in lv
    has1080 = "hd1080" in lv
    log(f"4K(2160)={has4k}  1440={has1440}  1080={has1080}  전체={lv}")
    pg.screenshot(path="scratch/yt/binge_quality.png")
    ctx.close()
log("DONE")
