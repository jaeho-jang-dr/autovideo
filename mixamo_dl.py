# -*- coding: utf-8 -*-
"""mixamo_dl.py — Mixamo 로그인 확인 + 동작 FBX 자동 다운로드.
사용: python mixamo_dl.py check              # 로그인 상태 확인(스샷)
      python mixamo_dl.py get "Walking" walk # 동작 검색→선택→FBX 다운로드
"""
import sys, os, time, glob
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

MODE = sys.argv[1] if len(sys.argv) > 1 else "check"
QUERY = sys.argv[2] if len(sys.argv) > 2 else "Walking"
NAME = sys.argv[3] if len(sys.argv) > 3 else "anim"
SH = "scratch/mx"; os.makedirs(SH, exist_ok=True)
DL = os.path.abspath("scratch/mocap"); os.makedirs(DL, exist_ok=True)
def log(m): print(m, flush=True)


with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="en-US", no_viewport=True, accept_downloads=True,
        ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.set_default_timeout(45000)
    log("→ mixamo.com 접속")
    pg.goto("https://www.mixamo.com/#/", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    pg.screenshot(path=f"{SH}/1_home.png")
    body = pg.inner_text("body")[:400]
    logged = ("Animations" in body or "Characters" in body or "Account" in body) and "Sign In" not in body[:200]
    log(f"로그인 추정: {logged}")
    log("본문 일부: " + body.replace("\n", " ")[:200])

    if MODE == "check":
        log(f"스샷 → {SH}/1_home.png")
        ctx.close(); sys.exit(0)

    # 동작 검색
    try:
        pg.goto("https://www.mixamo.com/#/?page=1&type=Motion", wait_until="domcontentloaded")
        pg.wait_for_timeout(6000)
        # 검색창
        for sel in ["input[placeholder*='Search']", "input[type='search']", "input.form-control"]:
            try:
                pg.locator(sel).first.fill(QUERY, timeout=4000); log("검색어 입력 "+sel); break
            except Exception: pass
        pg.keyboard.press("Enter"); pg.wait_for_timeout(6000)
        pg.keyboard.press("Escape")                     # 장르 필터 드롭다운 닫기
        pg.wait_for_timeout(1500)
        pg.screenshot(path=f"{SH}/2_search.png")
        # ★동작 타일(캡션 정확 일치)을 클릭 → 캐릭터에 로드. 여러 번 시도.
        def click_tile():
            for loc in [pg.get_by_text(QUERY, exact=True),
                        pg.locator(f"figure:has-text('{QUERY}')"),
                        pg.locator(".product-tile").filter(has_text=QUERY)]:
                try:
                    el = loc.first; el.scroll_into_view_if_needed(timeout=3000)
                    el.click(timeout=3000); return True
                except Exception: pass
            return False
        # 로드 확인: 다운로드 모달이 애니(Skin/Frames) 설정을 보이면 성공, T-pose면 재시도
        got_anim = False
        for attempt in range(3):
            pg.keyboard.press("Escape"); pg.wait_for_timeout(500)
            if not click_tile(): log(f"타일 클릭 실패 시도{attempt}"); continue
            log(f"타일 클릭 성공 시도{attempt}")
            pg.wait_for_timeout(11000)                  # 3D 로드 대기
            pg.screenshot(path=f"{SH}/3_selected.png")
            # DOWNLOAD 열기
            for sel in ["button:has-text('DOWNLOAD')", "button:has-text('Download')"]:
                try: pg.locator(sel).first.click(timeout=4000); break
                except Exception: pass
            pg.wait_for_timeout(3500)
            pg.screenshot(path=f"{SH}/4_dlmodal.png")
            seg = pg.inner_text("body").split("DOWNLOAD SETTINGS")[-1][:200]
            if "Frames" in seg or "Skin" in seg:
                got_anim = True; log("✔ 동작 로드됨(모달=애니 설정)"); break
            log(f"⚠ 시도{attempt}: T-pose 모달 — 취소 후 재시도")
            for c in ["button:has-text('CANCEL')", "button:has-text('Cancel')"]:
                try: pg.locator(c).first.click(timeout=3000); break
                except Exception: pass
            pg.wait_for_timeout(1500)
        if not got_anim:
            log("동작 로드 최종 실패"); ctx.close(); sys.exit(1)
        # 모달: Format=FBX, Download
        with pg.expect_download(timeout=90000) as di:
            for sel in ["button:has-text('Download')", ".modal button.primary", "button.btn-primary"]:
                try:
                    pg.locator(sel).last.click(timeout=5000); log("모달 Download 클릭 "+sel); break
                except Exception: pass
        dl = di.value
        out = os.path.join(DL, f"{NAME}.fbx")
        dl.save_as(out)
        log(f"✔ 다운로드 완료 → {out}")
    except Exception as e:
        log("에러: " + str(e)[:200])
        pg.screenshot(path=f"{SH}/err.png")
    ctx.close()
