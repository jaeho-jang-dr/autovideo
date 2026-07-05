# -*- coding: utf-8 -*-
"""브라우저를 열어 유지 — 사용자가 전화번호 인증하도록."""
import sys, os, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
FLAG = "scratch/keep_open.stop"
if os.path.exists(FLAG):
    os.remove(FLAG)
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.set_default_timeout(30000)
    try:
        pg.goto("https://studio.youtube.com/video/6lGedBJ5xx4/edit", wait_until="domcontentloaded")
    except Exception:
        pass
    pg.wait_for_timeout(3000)
    p2 = ctx.new_page()
    try:
        p2.goto("https://www.youtube.com/verify", wait_until="domcontentloaded")
    except Exception:
        pass
    print("BROWSER_OPEN", flush=True)
    for _ in range(720):
        time.sleep(5)
        if os.path.exists(FLAG):
            print("STOP", flush=True)
            break
    ctx.close()
print("KEEP_END")
