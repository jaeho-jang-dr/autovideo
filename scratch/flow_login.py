"""
flow_login.py — labs.google/fx/tools/flow OAuth 로그인 1회 돌파 후 세션을 프로필에 영속화.

두 가지 모드:
  (기본) 자동: 계정선택/이메일/동의/미확인앱을 자동 통과. 비밀번호 화면을 만나면
        --password 가 있으면 입력, 없으면 --wait-manual 초 동안 창을 열어두고
        사용자가 직접 비밀번호/2FA 를 입력하도록 폴링 대기한다.
  진행상황은 debug/login_status.txt 에 1줄로 계속 기록(외부 모니터링용).

옵션:
  --password "<pw>"     비밀번호 자동 입력(사용자가 명시 제공 시)
  --wait-manual N       비밀번호/추가인증 화면에서 사용자 수동 입력을 N초까지 대기(기본 0)
"""
import os
import sys
import time
import argparse
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
STATUS_FILE = os.path.abspath("debug/login_status.txt")
os.makedirs("debug", exist_ok=True)
os.makedirs(DL_DIR, exist_ok=True)


def log(m):
    print(f"[login {time.strftime('%H:%M:%S')}] {m}", flush=True)


def status(s):
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {s}")
    except Exception:
        pass
    log(f"STATUS={s}")


def vis(page, sel, t=600):
    try:
        return page.locator(sel).first.is_visible(timeout=t)
    except Exception:
        return False


def click_if(page, selectors, label):
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=500):
                loc.click(timeout=3000)
                log(f"  clicked [{label}] via {sel}")
                page.wait_for_timeout(2500)
                return True
        except Exception:
            pass
    return False


def composer_ready(page):
    return vis(page, PROMPT_SELECTOR, 500) or vis(page, "text=새 프로젝트", 500) or \
        vis(page, "text=New project", 500)


def on_password(page):
    return "/challenge/pwd" in page.url or vis(page, "input[type='password']", 400)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--password", default=None)
    ap.add_argument("--wait-manual", type=int, default=0)
    args = ap.parse_args()

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
            accept_downloads=True, downloads_path=DL_DIR,
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                  "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        st = "UNKNOWN"
        account_clicked = False
        pw_entered = False
        manual_deadline = None
        try:
            status("STARTING")
            log(f"goto {BASE}")
            page.goto(BASE, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)

            hard_deadline = time.time() + 120 + max(0, args.wait_manual)
            last_shot = 0
            while time.time() < hard_deadline:
                url = page.url

                # 0) 성공 판정
                if "labs.google" in url and composer_ready(page):
                    st = "LOGIN_OK"
                    break

                # 주기적 스냅샷(모니터링)
                if time.time() - last_shot > 8:
                    try:
                        page.screenshot(path=os.path.abspath("debug/login_progress.png"))
                    except Exception:
                        pass
                    last_shot = time.time()

                if "accounts.google.com" in url:
                    # 1) 비밀번호 화면 (계정 타일 클릭보다 먼저 판정 — 오클릭 방지)
                    if on_password(page):
                        if args.password and not pw_entered:
                            log("  password field -> typing provided password")
                            try:
                                pw = page.locator("input[type='password']").first
                                pw.click(); pw.fill(args.password)
                                pw_entered = True
                                click_if(page, ["#passwordNext", "button:has-text('다음')",
                                                "button:has-text('Next')"], "password_next")
                                continue
                            except Exception as e:
                                log(f"  password fill error: {e}")
                        else:
                            # 수동 입력 대기 모드
                            if args.wait_manual > 0:
                                if manual_deadline is None:
                                    manual_deadline = time.time() + args.wait_manual
                                    status("PASSWORD_REQUIRED_WAITING_MANUAL")
                                    log("  >>> 사용자: 열린 Chrome 창에 비밀번호/2FA 를 직접 입력해 주세요. <<<")
                                if time.time() > manual_deadline:
                                    st = "PASSWORD_TIMEOUT"
                                    break
                                page.wait_for_timeout(3000)
                                continue
                            else:
                                st = "PASSWORD_REQUIRED"
                                break

                    # 2) 이메일 입력 화면
                    if vis(page, "input[type='email']", 400):
                        log("  email field -> entering account email")
                        try:
                            em = page.locator("input[type='email']").first
                            em.click(); em.fill("drjang00@gmail.com")
                            click_if(page, ["#identifierNext", "button:has-text('다음')",
                                            "button:has-text('Next')"], "email_next")
                            continue
                        except Exception as e:
                            log(f"  email fill error: {e}")

                    # 3) 계정 선택 타일 (chooser 단계에서 1회만)
                    if (not account_clicked) and "accountchooser" in url:
                        if click_if(page, [
                            "div[data-email='drjang00@gmail.com']",
                            "[data-identifier='drjang00@gmail.com']",
                            "li:has-text('drjang00@gmail.com')",
                        ], "account_tile"):
                            account_clicked = True
                            continue

                    # 4) 미확인 앱 경고 -> 고급 -> 이동
                    if click_if(page, ["text=고급", "text=Advanced"], "advanced"):
                        click_if(page, ["text=안전하지 않음", "text=labs.google(으)로 이동",
                                        "text=Go to labs.google", "a:has-text('이동')"], "proceed_unsafe")
                        continue

                    # 5) OAuth 동의/계속/허용
                    if click_if(page, [
                        "button:has-text('계속')", "button:has-text('Continue')",
                        "button:has-text('허용')", "button:has-text('Allow')",
                        "button:has-text('다음')", "button:has-text('Next')",
                        "#submit_approve_access",
                    ], "consent"):
                        continue

                    page.wait_for_timeout(2500)
                    continue

                # labs.google 로딩 대기
                page.wait_for_timeout(2500)

            page.screenshot(path=os.path.abspath("debug/login_final.png"))
            log(f"FINAL URL = {page.url}")
            status(st)
        except Exception as e:
            log(f"ERROR: {e}")
            try:
                page.screenshot(path=os.path.abspath("debug/login_error.png"))
            except Exception:
                pass
            st = "ERROR"; status(st)
        finally:
            ctx.close()
            log("closed (cookies persisted to profile).")
        sys.exit(0 if st == "LOGIN_OK" else (2 if st in ("PASSWORD_REQUIRED", "PASSWORD_TIMEOUT") else 1))


if __name__ == "__main__":
    main()
