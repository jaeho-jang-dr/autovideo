# -*- coding: utf-8 -*-
"""Shorts 초안을 재개해서 일부공개로 게시. 제목으로 행 식별.
사용: python resume_draft.py "<제목일부>" [unlisted|public]"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

TITLE_PART = sys.argv[1]
VIS = sys.argv[2] if len(sys.argv) > 2 else "unlisted"
VISNAME = {"unlisted": "일부 공개", "private": "비공개", "public": "공개"}[VIS]
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)
def shot(pg, n):
    try: pg.screenshot(path=f"{SH}/rd_{n}.png")
    except Exception: pass

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto("https://studio.youtube.com/", wait_until="domcontentloaded"); pg.wait_for_timeout(7000)
    pg.get_by_text("콘텐츠", exact=True).first.click(timeout=8000); pg.wait_for_timeout(4000)
    pg.get_by_role("tab", name="Shorts").first.click(timeout=8000); pg.wait_for_timeout(4000)
    shot(pg, "1shorts")
    # 초안 행 찾기 → '초안 수정' 클릭
    row = pg.locator("ytcp-video-row", has_text=TITLE_PART).first
    row.scroll_into_view_if_needed(); pg.wait_for_timeout(500)
    clicked = False
    for sel in ["ytcp-button:has-text('초안 수정')", "button:has-text('초안 수정')", ":text('초안 수정')"]:
        try: row.locator(sel).first.click(timeout=4000); clicked = True; log("초안수정 "+sel); break
        except Exception: pass
    if not clicked:
        try: pg.get_by_text("초안 수정", exact=False).first.click(timeout=5000); clicked = True; log("초안수정(page)")
        except Exception as e: log("초안수정 실패 "+str(e)[:60])
    pg.wait_for_timeout(6000); shot(pg, "2wizard")
    # 다이얼로그 내부 링크에서 실제 쇼츠 ID 캡처
    VID = ""
    try:
        href = pg.locator("ytcp-uploads-dialog a[href*='/shorts/'], ytcp-uploads-dialog a[href*='youtu.be/'], a[href*='youtube.com/shorts/']").first.get_attribute("href", timeout=3000)
        import re as _re
        m = _re.search(r"(?:shorts/|youtu\.be/|v=)([A-Za-z0-9_-]{9,})", href or "")
        if m: VID = m.group(1); log("VIDEO_ID="+VID)
    except Exception: pass
    # 마법사: '일부 공개' 라디오가 실제 보일 때까지 '다음' (최대 5회)
    reached = False
    for i in range(5):
        try:
            if pg.get_by_role("radio", name=VISNAME, exact=True).first.is_visible(timeout=1500): reached = True; log("공개상태 도달"); break
        except Exception: pass
        try: pg.locator("#next-button, ytcp-button:has-text('다음')").first.click(timeout=6000); pg.wait_for_timeout(2800); log(f"다음{i+1}")
        except Exception: pass
    shot(pg, "3vis")
    # 일부공개 선택
    try:
        pg.get_by_role("radio", name=VISNAME, exact=True).first.click(timeout=6000); log(VISNAME)
    except Exception:
        try: pg.get_by_text(VISNAME, exact=True).first.click(timeout=4000); log(VISNAME+"(text)")
        except Exception as e: log("공개선택 실패 "+str(e)[:50])
    pg.wait_for_timeout(1500)
    # 저장 (force + JS 폴백)
    saved = False
    try:
        btn = pg.locator("#done-button").first; btn.wait_for(state="visible", timeout=10000)
        for _ in range(3):
            try: btn.click(timeout=5000, force=True); saved = True; break
            except Exception:
                try: pg.eval_on_selector("#done-button", "el=>{(el.querySelector('button')||el).click();}"); saved = True; break
                except Exception: pg.wait_for_timeout(1500)
        log("저장" if saved else "저장 실패")
    except Exception as e: log("저장 예외 "+str(e)[:60])
    pg.wait_for_timeout(6000); shot(pg, "4done")
    # 확인
    try:
        pg.wait_for_selector(":text('처리 중'), :text('동영상 처리'), ytcp-video-row", timeout=15000); log("게시확인")
    except Exception: log("게시확인 스킵")
    shot(pg, "5final"); pg.wait_for_timeout(2000); ctx.close()
print("END")
