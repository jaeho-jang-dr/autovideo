# -*- coding: utf-8 -*-
"""mixamo_login.py — Playwright 프로필로 Mixamo(Adobe) 구글 SSO 로그인 시도.
프로필에 drjang00 구글 세션(유튜브용)이 있으면 자동 로그인 → 세션 저장(이후 다운로드 자동)."""
import sys, os, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

SH = "scratch/mx"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="en-US", no_viewport=True,
        ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.set_default_timeout(40000)
    pg.goto("https://www.mixamo.com/#/", wait_until="domcontentloaded")
    pg.wait_for_timeout(6000)
    # Log In 클릭
    for sel in ["text=Log In", "a:has-text('Log in')", "button:has-text('Log In')", "a[href*='auth']"]:
        try:
            pg.locator(sel).first.click(timeout=5000); log("Log In 클릭 "+sel); break
        except Exception: pass
    pg.wait_for_timeout(8000); pg.screenshot(path=f"{SH}/L1_adobe.png")
    log("URL: " + pg.url)
    log("본문: " + pg.inner_text("body").replace("\n"," ")[:250])
    # Adobe 로그인 페이지에서 "Continue with Google"
    for sel in ["button:has-text('Google')", "[data-provider='google']", "text=Continue with Google",
                "button[aria-label*='Google']", ".google", "[class*='google']"]:
        try:
            pg.locator(sel).first.click(timeout=5000); log("Google 로그인 클릭 "+sel); break
        except Exception: pass
    pg.wait_for_timeout(7000); pg.screenshot(path=f"{SH}/L2_google.png")
    log("URL2: " + pg.url)
    # 구글 계정 선택(drjang00)
    for sel in ["div[data-identifier='drjang00@gmail.com']", "text=drjang00@gmail.com",
                "[data-email='drjang00@gmail.com']", "li:has-text('drjang00')"]:
        try:
            pg.locator(sel).first.click(timeout=6000); log("계정 선택 drjang00 "+sel); break
        except Exception: pass
    pg.wait_for_timeout(9000); pg.screenshot(path=f"{SH}/L3_after.png")
    log("최종 URL: " + pg.url)
    body = pg.inner_text("body")[:300]
    ok = "Log In" not in body and ("Animations" in body or "Account" in body or "mixamo" in pg.url)
    log("로그인 성공 추정: " + str(ok))
    log("최종 본문: " + body.replace("\n"," ")[:200])
    pg.wait_for_timeout(2000)
    ctx.close()
