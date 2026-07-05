# -*- coding: utf-8 -*-
"""아이성장 본편 v2(일부공개)+쇼츠2개(일부공개) → 공개. 구버전 vvHZ(비공개)는 건드리지 않음."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
def log(m): print(m, flush=True)

def to_public(pg, tab, row_filter_texts):
    pg.goto(f"https://studio.youtube.com/channel/UC6KCrgUSdSVUd97b7ltJK_g/videos/{tab}", wait_until="domcontentloaded")
    pg.wait_for_timeout(10000)
    row = pg.locator("ytcp-video-row")
    for t in row_filter_texts:
        row = row.filter(has_text=t)
    row = row.first
    ok = False
    for sel in ["ytcp-video-visibility-select", "text=일부 공개"]:
        try:
            row.locator(sel).first.click(timeout=5000, force=True); ok = True; log(f"  상태클릭 {sel}"); break
        except Exception: pass
    if not ok: log("  상태클릭 실패"); return
    pg.wait_for_timeout(2500)
    try:
        pg.locator("tp-yt-paper-radio-button[name='PUBLIC']").first.click(timeout=5000); log("  PUBLIC 선택")
    except Exception:
        try: pg.get_by_text("공개", exact=True).first.click(timeout=4000); log("  공개 텍스트")
        except Exception as e: log("  공개 실패 " + str(e)[:40])
    pg.wait_for_timeout(1500)
    for sel in ["#save-button", "#done-button", "ytcp-button:has-text('게시')", "ytcp-button:has-text('저장')"]:
        try:
            b = pg.locator(sel).first
            if b.is_visible(timeout=1500): b.click(); log("  저장"); break
        except Exception: pass
    pg.wait_for_timeout(5000)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    # 본편 v2: 제목+일부공개 (구버전 비공개는 제외됨)
    log("[본편 v2]"); to_public(pg, "upload", ["우리 아이 키", "일부 공개"])
    # 쇼츠 2개
    log("[KO 쇼츠]"); to_public(pg, "short", ["부모 키로 예상"])
    log("[EN 쇼츠]"); to_public(pg, "short", ["Predict your child"])
    pg.screenshot(path="scratch/yt/growth_public.png")
    log("DONE"); pg.wait_for_timeout(1500); ctx.close()
print("END")
