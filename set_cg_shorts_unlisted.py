# -*- coding: utf-8 -*-
"""아이 성장 쇼츠 2개(비공개)를 일부공개로 — 각각 제목으로 타겟."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
def log(m): print(m, flush=True)
TARGETS = ["우리 아이 키, 부모", "Predict your child"]
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    for ti in TARGETS:
        pg.goto("https://studio.youtube.com/channel/UC6KCrgUSdSVUd97b7ltJK_g/videos/short", wait_until="domcontentloaded")
        pg.wait_for_timeout(11000)
        row = pg.locator("ytcp-video-row").filter(has_text=ti).first
        ok = False
        for sel in ["ytcp-video-visibility-select", "text=비공개"]:
            try:
                row.locator(sel).first.click(timeout=5000, force=True); ok = True; log(f"[{ti[:10]}] 클릭 {sel}"); break
            except Exception: pass
        if not ok: log(f"[{ti[:10]}] 상태클릭 실패"); continue
        pg.wait_for_timeout(2500)
        try:
            pg.locator("tp-yt-paper-radio-button[name='UNLISTED']").first.click(timeout=5000); log("UNLISTED")
        except Exception:
            try: pg.get_by_text("일부 공개", exact=True).first.click(timeout=4000); log("일부공개텍스트")
            except Exception as e: log("일부공개 실패 " + str(e)[:40])
        pg.wait_for_timeout(1500)
        for sel in ["#save-button", "#done-button", "ytcp-button:has-text('저장')"]:
            try:
                b = pg.locator(sel).first
                if b.is_visible(timeout=1500): b.click(); log("저장"); break
            except Exception: pass
        pg.wait_for_timeout(4000)
    pg.screenshot(path="scratch/yt/cg_shorts_final.png")
    log("DONE"); pg.wait_for_timeout(1500); ctx.close()
print("END")
