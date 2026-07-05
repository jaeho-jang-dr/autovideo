# -*- coding: utf-8 -*-
"""v2(Mo1AIPoLjhU) → 일부공개, 기존(vvHZ27l9jr4) → 비공개. 콘텐츠 목록에서 처리."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
def log(m): print(m, flush=True)

# (설명 텍스트로 두 영상 구분: 둘 다 제목 같으니 업로드 시각 순서 = v2가 위(최신))
# 목록 첫 행(nth 0)=v2(최신), 둘째(nth 1)=기존
JOBS = [(0, "UNLISTED", "v2 최신"), (1, "PRIVATE", "기존")]

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    for idx, target, label in JOBS:
        pg.goto("https://studio.youtube.com/channel/UC6KCrgUSdSVUd97b7ltJK_g/videos/upload", wait_until="domcontentloaded")
        pg.wait_for_timeout(10000)
        row = pg.locator("ytcp-video-row").filter(has_text="우리 아이 키").nth(idx)
        # 현재 상태 텍스트 클릭(비공개 또는 일부 공개)
        ok = False
        for sel in ["ytcp-video-visibility-select", "text=비공개", "text=일부 공개", "text=초안"]:
            try:
                row.locator(sel).first.click(timeout=4000, force=True); ok = True; log(f"[{label}] 상태클릭 {sel}"); break
            except Exception: pass
        if not ok: log(f"[{label}] 상태클릭 실패"); continue
        pg.wait_for_timeout(2500)
        try:
            pg.locator(f"tp-yt-paper-radio-button[name='{target}']").first.click(timeout=5000); log(f"[{label}] → {target}")
        except Exception as e: log(f"[{label}] 라디오 실패 " + str(e)[:50])
        pg.wait_for_timeout(1500)
        for sel in ["#save-button", "#done-button", "ytcp-button:has-text('저장')"]:
            try:
                b = pg.locator(sel).first
                if b.is_visible(timeout=1500): b.click(); log(f"[{label}] 저장"); break
            except Exception: pass
        pg.wait_for_timeout(5000)
    pg.screenshot(path="scratch/yt/cg_swap.png")
    log("DONE"); pg.wait_for_timeout(1500); ctx.close()
print("END")
