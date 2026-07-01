"""
flow_login_probe.py — labs.google/fx/tools/flow 로그인/컴포저 진입 상태를 빠르게 진단.
autoveo_flow.py 와 동일한 chrome_profile 영속 컨텍스트를 사용하되, 아무것도 생성하지 않고
현재 상태만 캡처/보고 후 종료한다. (긴 본 실행 전 로그인 벽 여부 확인용)
"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE = "https://labs.google/fx/tools/flow"
PROFILE = os.path.abspath("assets/chrome_profile")
DL_DIR = os.path.abspath(os.path.join("debug", "downloads"))
PROMPT_SELECTOR = "div[role='textbox'][contenteditable='true']"
os.makedirs("debug", exist_ok=True)
os.makedirs(DL_DIR, exist_ok=True)


def log(m):
    print(f"[probe {time.strftime('%H:%M:%S')}] {m}", flush=True)


with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
        accept_downloads=True, downloads_path=DL_DIR,
        ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--disable-blink-features=AutomationControlled",
              "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    try:
        log(f"goto {BASE}")
        page.goto(BASE, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(6000)
        log(f"URL = {page.url}")
        log(f"TITLE = {page.title()[:120]}")

        # 로그인 여부
        if "accounts.google.com" in page.url:
            log("STATE = LOGIN_WALL (accounts.google.com)")
            # 화면에 보이는 주요 텍스트/입력요소 진단
            for sel, label in [
                ("input[type='email']", "email_input"),
                ("input[type='password']", "password_input"),
                ("div[data-email='drjang00@gmail.com']", "account_tile_drjang"),
                ("text=drjang00@gmail.com", "account_text_drjang"),
                ("text=계정 선택", "account_chooser_kr"),
                ("text=Choose an account", "account_chooser_en"),
            ]:
                try:
                    vis = page.locator(sel).first.is_visible(timeout=800)
                except Exception:
                    vis = False
                log(f"  {label}: {'VISIBLE' if vis else '-'}")
        else:
            # 컴포저(프롬프트 입력창) 진입 가능?
            composer = False
            for _ in range(8):
                try:
                    if page.locator(PROMPT_SELECTOR).first.is_visible(timeout=500):
                        composer = True
                        break
                except Exception:
                    pass
                page.wait_for_timeout(1000)
            if composer:
                log("STATE = LOGGED_IN_COMPOSER_READY (textbox visible on landing)")
            else:
                # '새 프로젝트' 버튼이 보이는 대시보드 상태인지 확인
                newproj = False
                for sel in ["text=새 프로젝트", "text=New project", "button:has-text('새 프로젝트')"]:
                    try:
                        if page.locator(sel).first.is_visible(timeout=800):
                            newproj = True
                            break
                    except Exception:
                        pass
                if newproj:
                    log("STATE = LOGGED_IN_DASHBOARD (need to click 새 프로젝트)")
                else:
                    log("STATE = UNKNOWN (logged-in url but no composer/dashboard markers)")
        page.screenshot(path=os.path.abspath(os.path.join("debug", "probe_login.png")))
        log("saved debug/probe_login.png")
    except Exception as e:
        log(f"ERROR: {e}")
        try:
            page.screenshot(path=os.path.abspath(os.path.join("debug", "probe_error.png")))
        except Exception:
            pass
    finally:
        page.wait_for_timeout(1500)
        ctx.close()
        log("closed.")
