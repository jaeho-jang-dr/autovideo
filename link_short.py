# -*- coding: utf-8 -*-
"""쇼츠에 '관련 동영상' 링크 설정.
사용: python link_short.py <short_id> <main_title_substr> [--dry] [--search]
  <main_title_substr>: 본 영상 제목의 고유 부분(예: '메스머의 사기극')
  --dry : 선택만 하고 저장 직전에 멈춰 상태 덤프(검증용)
  --search : 기본 그리드 대신 검색창에 substr 입력 후 선택
"""
import sys, os, re
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

SID = sys.argv[1]
SUBSTR = sys.argv[2]
DRY = "--dry" in sys.argv
USE_SEARCH = "--search" in sys.argv
os.makedirs("scratch/yt", exist_ok=True)

def log(*a):
    print(*a, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto(f"https://studio.youtube.com/video/{SID}/edit", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)

    picker = pg.locator("ytcp-shorts-content-links-picker").first
    # 현재 링크 상태(트리거 텍스트)
    try:
        before = picker.inner_text().strip().replace("\n", " ")
    except Exception:
        before = "(읽기 실패)"
    log("BEFORE:", before[:120])

    # 트리거 클릭 → 다이얼로그
    pg.locator("ytcp-shorts-content-links-picker ytcp-dropdown-trigger").first.click(timeout=8000)
    pg.wait_for_timeout(3500)
    dlg = pg.locator("ytcp-video-pick-dialog").first
    dlg.wait_for(state="visible", timeout=10000)

    if USE_SEARCH:
        try:
            sb = pg.get_by_placeholder("내 동영상 검색")
            sb.wait_for(state="visible", timeout=6000)
            sb.click(); sb.type(SUBSTR, delay=90)
            pg.wait_for_timeout(4000)
            log("검색 입력:", SUBSTR)
        except Exception as e:
            log("검색 실패:", str(e)[:80])

    # 그리드 스크롤로 모든 카드 로드(기본 그리드에 없을 수 있음)
    if not USE_SEARCH:
        try:
            for _ in range(5):
                pg.eval_on_selector_all(
                    "ytcp-video-pick-dialog #videos, ytcp-video-pick-dialog-contents .container, ytcp-video-pick-dialog [class*='scroll']",
                    "els => els.forEach(e => { e.scrollTop = e.scrollHeight; })")
                pg.wait_for_timeout(900)
        except Exception as e:
            log("스크롤 경고:", str(e)[:60])

    # substr 로 카드 선택 — 보이는(visible) 엔티티 카드 우선
    card = None
    cards = dlg.locator("ytcp-entity-card").filter(has_text=SUBSTR)
    deadline = 12000
    waited = 0
    while waited < deadline and card is None:
        n = cards.count()
        for i in range(n):
            c = cards.nth(i)
            try:
                if c.is_visible():
                    card = c; break
            except Exception:
                pass
        if card is None:
            pg.wait_for_timeout(800); waited += 800
    if card is None:
        # 폴백: 텍스트 기반(보이는 것)
        txts = dlg.get_by_text(SUBSTR, exact=False)
        for i in range(txts.count()):
            if txts.nth(i).is_visible():
                card = txts.nth(i); break
    if card is None:
        raise RuntimeError(f"카드 못 찾음: {SUBSTR}")
    card.scroll_into_view_if_needed(timeout=4000)
    matched = card.inner_text().strip().replace("\n", " ")
    log("MATCH CARD:", matched[:120])
    card.scroll_into_view_if_needed(timeout=4000)
    card.click(timeout=6000)
    pg.wait_for_timeout(3500)

    # 선택 후 트리거 텍스트 재확인
    try:
        after_sel = picker.inner_text().strip().replace("\n", " ")
    except Exception:
        after_sel = "(읽기 실패)"
    log("AFTER SELECT:", after_sel[:140])
    pg.screenshot(path=f"scratch/yt/link_{SID}_selected.png", full_page=True)

    if DRY:
        log("DRY RUN — 저장 안 함. 8초 후 종료.")
        pg.wait_for_timeout(8000)
        ctx.close()
        raise SystemExit(0)

    # 저장
    saved = False
    save = pg.locator("ytcp-button#save, #save-button, ytcp-button[id='save']").first
    try:
        save.wait_for(state="visible", timeout=8000)
    except Exception:
        save = pg.get_by_role("button", name="저장").first
    for attempt in range(3):
        try:
            save.click(timeout=5000, force=True)
            saved = True; log(f"저장 클릭 성공(attempt {attempt})"); break
        except Exception as e:
            log(f"저장 클릭 실패 {attempt}:", str(e)[:60])
            try:
                pg.eval_on_selector("ytcp-button#save, #save-button",
                    "el => { const b = el.querySelector('button') || el; b.click(); }")
                saved = True; log("JS 폴백 저장"); break
            except Exception as e2:
                log("JS 폴백 실패:", str(e2)[:60])
        pg.wait_for_timeout(1500)
    pg.wait_for_timeout(5000)
    pg.screenshot(path=f"scratch/yt/link_{SID}_saved.png", full_page=True)

    # 저장 검증: 페이지 리로드 후 트리거 텍스트
    pg.goto(f"https://studio.youtube.com/video/{SID}/edit", wait_until="domcontentloaded")
    pg.wait_for_timeout(8000)
    try:
        verify = pg.locator("ytcp-shorts-content-links-picker").first.inner_text().strip().replace("\n", " ")
    except Exception:
        verify = "(읽기 실패)"
    log("VERIFY (reload):", verify[:140])
    ok = SUBSTR in verify
    log("RESULT:", "OK ✔" if ok else "확인 필요 ✗")
    ctx.close()
print("END")
