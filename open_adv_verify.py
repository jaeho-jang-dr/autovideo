# -*- coding: utf-8 -*-
"""쇼츠 편집 → 관련 동영상 → '다음' → 고급기능 인증 화면까지 띄우고 브라우저를 열어둔 채 대기.
사용자가 직접 인증 진행하도록 40분간 유지. 사용: python open_adv_verify.py [short_id]"""
import sys, os, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

SID = sys.argv[1] if len(sys.argv) > 1 else "qQscFq0nnAA"
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto(f"https://studio.youtube.com/video/{SID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
    def qr_shown():
        try:
            b = pg.inner_text("body")
            return any(k in b for k in ["코드 스캔", "스마트폰에서", "video-verification", "코드를 스캔"])
        except Exception: return False
    # 트리거 → '다음' 반복 클릭, QR 인증화면 뜰 때까지 (최대 6회)
    for attempt in range(6):
        if qr_shown(): print("QR 인증화면 감지", flush=True); break
        # 트리거(관련 동영상) 클릭 시도
        try:
            pg.locator("ytcp-shorts-content-links-picker ytcp-dropdown-trigger").first.click(timeout=4000); print(f"트리거 {attempt}", flush=True)
        except Exception: pass
        pg.wait_for_timeout(2500)
        if qr_shown(): print("QR 인증화면 감지", flush=True); break
        # '다음' 클릭 시도 (role/text/force)
        clicked = False
        for how in ("role", "text", "force"):
            try:
                if how == "role": pg.get_by_role("button", name="다음", exact=True).first.click(timeout=3000)
                elif how == "text": pg.locator("ytcp-button:has-text('다음')").first.click(timeout=3000)
                else: pg.locator("ytcp-button:has-text('다음')").first.click(timeout=3000, force=True)
                clicked = True; print(f"다음({how})", flush=True); break
            except Exception: pass
        pg.wait_for_timeout(3500)
        if qr_shown(): print("QR 인증화면 감지", flush=True); break
    pg.wait_for_timeout(2000)
    # 새 탭으로 열렸을 수 있으니 활성/마지막 페이지 캡처
    try:
        pages = ctx.pages
        target = pages[-1]
        target.bring_to_front(); target.wait_for_timeout(1500)
        target.screenshot(path="scratch/yt/adv_verify.png", full_page=True)
        print("URL:", target.url, flush=True)
        print("TITLE:", target.title(), flush=True)
    except Exception as e: print("캡처 경고", str(e)[:60], flush=True)
    print("READY_FOR_USER — 브라우저 열어둠(40분). 인증 진행하세요.", flush=True)
    # 사용자가 직접 조작하도록 유지
    for i in range(240):  # 240 * 10s = 40분
        try: ctx.pages  # keepalive
        except Exception: break
        time.sleep(10)
    ctx.close()
print("END", flush=True)
