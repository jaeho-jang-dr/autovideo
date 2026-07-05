# -*- coding: utf-8 -*-
"""세종 쇼츠 2개를 공개(Public)로. 아직 일부공개/비공개인 세종 쇼츠 행 대상."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
def log(m): print(m, flush=True)
TARGETS = ["한글은 누가 만들", "Who invented Hangeul"]
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    for ti in TARGETS:
        pg.goto("https://studio.youtube.com/channel/UC6KCrgUSdSVUd97b7ltJK_g/videos/short", wait_until="domcontentloaded")
        pg.wait_for_timeout(10000)
        row = pg.locator("ytcp-video-row").filter(has_text=ti).first
        # 이미 공개면 스킵
        try:
            txt = row.inner_text(timeout=4000)
            if "공개" in txt and "일부 공개" not in txt and "비공개" not in txt:
                log(f"[{ti[:10]}] 이미 공개 — 스킵"); continue
        except Exception: pass
        ok = False
        for sel in ["ytcp-video-visibility-select", "text=일부 공개", "text=비공개"]:
            try:
                row.locator(sel).first.click(timeout=4000, force=True); ok = True; log(f"[{ti[:10]}] 상태클릭 {sel}"); break
            except Exception: pass
        if not ok: log(f"[{ti[:10]}] 상태클릭 실패"); continue
        pg.wait_for_timeout(2500)
        try:
            pg.locator("tp-yt-paper-radio-button[name='PUBLIC']").first.click(timeout=5000); log("PUBLIC")
        except Exception:
            try: pg.get_by_text("공개", exact=True).first.click(timeout=4000); log("공개 텍스트")
            except Exception as e: log("공개 실패 " + str(e)[:40])
        pg.wait_for_timeout(1500)
        for sel in ["#save-button", "#done-button", "ytcp-button:has-text('게시')", "ytcp-button:has-text('저장')"]:
            try:
                b = pg.locator(sel).first
                if b.is_visible(timeout=1500): b.click(); log("저장"); break
            except Exception: pass
        pg.wait_for_timeout(4000)
    pg.screenshot(path="scratch/yt/sejong_shorts_pub.png")
    log("DONE"); pg.wait_for_timeout(1500); ctx.close()
print("END")
