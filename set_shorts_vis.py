# -*- coding: utf-8 -*-
"""게시된 비공개 쇼츠들을 일부공개로 변경 (콘텐츠 목록 공개상태 드롭다운)."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
def log(m): print(m, flush=True)
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    for idx in range(2):
        pg.goto("https://studio.youtube.com/channel/UC6KCrgUSdSVUd97b7ltJK_g/videos/short", wait_until="domcontentloaded")
        pg.wait_for_timeout(9000)
        row = pg.locator("ytcp-video-row").nth(idx)
        # 공개상태 셀(드롭다운) 클릭
        clicked = False
        for sel in ["ytcp-video-visibility-select", "#visibility-column", ":text('비공개')"]:
            try:
                el = row.locator(sel).first
                el.scroll_into_view_if_needed(); el.click(timeout=5000); clicked = True; break
            except Exception: pass
        log(f"[{idx}] 공개상태 클릭 {clicked}")
        pg.wait_for_timeout(2500); pg.screenshot(path=f"scratch/yt/sv_{idx}_1.png")
        # 일부 공개 선택 (드롭다운 옵션 또는 모달 라디오)
        try:
            pg.locator("tp-yt-paper-radio-button[name='UNLISTED']").first.click(timeout=4000); log(f"[{idx}] UNLISTED 라디오")
        except Exception:
            try: pg.get_by_text("일부 공개", exact=True).first.click(timeout=4000); log(f"[{idx}] 일부공개 텍스트")
            except Exception as e: log(f"[{idx}] 일부공개 실패 "+str(e)[:50])
        pg.wait_for_timeout(1500)
        # 저장(모달이면)
        for sel in ["#save-button", "#done-button", "ytcp-button:has-text('저장')"]:
            try:
                b = pg.locator(sel).first
                if b.is_visible(timeout=1500): b.click(); log(f"[{idx}] 저장"); break
            except Exception: pass
        pg.wait_for_timeout(4000); pg.screenshot(path=f"scratch/yt/sv_{idx}_2.png")
    log("SHORTS_VIS_DONE"); pg.wait_for_timeout(2000); ctx.close()
print("END")
