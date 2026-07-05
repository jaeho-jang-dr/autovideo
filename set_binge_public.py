# -*- coding: utf-8 -*-
"""정주행 본편(wJUAiZW5fW0, 일부공개) → 공개 전환. 4K 처리 완료 확인 후 실행."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

def log(m): print(m, flush=True)

def to_public(pg, row_filter_texts):
    pg.goto("https://studio.youtube.com/channel/UC6KCrgUSdSVUd97b7ltJK_g/videos/upload",
            wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    row = pg.locator("ytcp-video-row")
    for t in row_filter_texts:
        row = row.filter(has_text=t)
    row = row.first
    ok = False
    for sel in ["ytcp-video-visibility-select", "text=일부 공개"]:
        try:
            row.locator(sel).first.click(timeout=5000, force=True); ok = True; log(f"  상태클릭 {sel}"); break
        except Exception: pass
    if not ok: log("  상태클릭 실패"); return False
    pg.wait_for_timeout(2500)
    try:
        pg.locator("tp-yt-paper-radio-button[name='PUBLIC']").first.click(timeout=6000); log("  PUBLIC 라디오 선택")
    except Exception:
        try: pg.get_by_text("공개", exact=True).first.click(timeout=4000); log("  공개 텍스트 클릭")
        except Exception as e: log("  공개 선택 실패 " + str(e)[:50]); return False
    pg.wait_for_timeout(1500)
    saved = False
    for sel in ["#save-button", "#done-button", "ytcp-button:has-text('게시')", "ytcp-button:has-text('저장')"]:
        try:
            b = pg.locator(sel).first
            if b.is_visible(timeout=1500): b.click(); log(f"  저장 클릭 {sel}"); saved = True; break
        except Exception: pass
    pg.wait_for_timeout(5000)
    return saved

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    log("[정주행 본편] 공개 전환")
    r = to_public(pg, ["정주행", "일부 공개"])
    os.makedirs("scratch/yt", exist_ok=True)
    pg.screenshot(path="scratch/yt/binge_public_after.png")
    log("결과 저장됨: " + ("성공(저장클릭)" if r else "저장 실패-스샷확인"))
    ctx.close()
log("DONE")
