# -*- coding: utf-8 -*-
"""Azure 포털 로그인 → Speech 리소스 사용량 확인. 비밀번호는 출력/스크린샷 값에 노출 안 함(패스워드칸은 점표시)."""
import os, sys, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

env = {}
for l in open(".env", encoding="utf-8"):
    if "=" in l and not l.strip().startswith("#"):
        k, v = l.split("=", 1); env[k.strip()] = v.strip()
EMAIL = env.get("AZURE_ACCOUNT_EMAIL", ""); PW = env.get("AZURE_ACCOUNT_PW", "")
SH = "scratch/az"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)
def shot(pg, n):
    try: pg.screenshot(path=os.path.join(SH, n)); log("shot " + n)
    except Exception as e: log("shot fail " + str(e)[:40])

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
        no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto("https://portal.azure.com", wait_until="domcontentloaded"); pg.wait_for_timeout(8000)
    log("URL: " + pg.url); shot(pg, "0_start.png")

    def cur():
        try: return pg.inner_text("body")
        except Exception: return ""

    # 이메일
    try:
        em = pg.locator("input[type='email'], #i0116").first
        if em.is_visible(timeout=5000):
            em.fill(EMAIL); log("이메일 입력")
            pg.locator("#idSIButton9, input[type='submit']").first.click(timeout=6000); pg.wait_for_timeout(4000)
    except Exception as e: log("이메일 단계 스킵 " + str(e)[:50])
    shot(pg, "1_afteremail.png")

    # 패스키(얼굴/지문/PIN) 화면이면 '다른 방법으로 로그인'/'뒤로'로 빠져나가 비밀번호 사용 시도
    try:
        body0 = cur()
        if any(k in body0 for k in ["얼굴, 지문", "보안 키", "PIN 또는", "디바이스에 보안 창"]):
            log("패스키 화면 감지 — 비밀번호 방식으로 전환 시도")
            for t in ["다른 방법으로 로그인", "다른 로그인 옵션", "로그인 옵션", "비밀번호 사용", "비밀번호"]:
                try:
                    el = pg.get_by_text(t, exact=False).first
                    if el.is_visible(timeout=2500): el.click(); log("클릭: " + t); pg.wait_for_timeout(2500); break
                except Exception: pass
            shot(pg, "1b_switch.png")
            # 로그인 방법 선택 목록에서 '비밀번호' 선택
            for t in ["비밀번호", "Password"]:
                try:
                    el = pg.get_by_text(t, exact=False).first
                    if el.is_visible(timeout=2500): el.click(); log("방법선택: " + t); pg.wait_for_timeout(2500); break
                except Exception: pass
            shot(pg, "1c_pickpw.png")
    except Exception as e: log("패스키 전환 스킵 " + str(e)[:50])

    # 비밀번호
    try:
        pwd = pg.locator("input[type='password'], #i0118").first
        if pwd.is_visible(timeout=6000):
            pwd.fill(PW); log("비밀번호 입력(값 비노출)")
            pg.locator("#idSIButton9, input[type='submit']").first.click(timeout=6000); pg.wait_for_timeout(4500)
        else:
            log("비밀번호 입력칸 여전히 없음(패스키 강제) — 사용자 직접 로그인 필요")
    except Exception as e: log("비번 단계 스킵 " + str(e)[:50])
    shot(pg, "2_afterpw.png")

    # 2FA / 추가 인증 감지
    body = cur()
    twofa_kw = ["코드를 입력", "인증", "Authenticator", "확인 코드", "전화", "verify", "보안 정보",
                "요청을 승인", "Approve", "번호를 입력"]
    if any(k in body for k in twofa_kw):
        log("⚠️ 2FA/추가인증 화면 감지 — 사용자 폰 승인 필요할 수 있음")
        shot(pg, "2fa.png")

    # '로그인 상태 유지하시겠습니까?' → 예
    try:
        if "로그인 상태를 유지" in body or "Stay signed in" in body or pg.get_by_text("로그인 상태를 유지", exact=False).first.is_visible(timeout=3000):
            pg.locator("#idSIButton9").first.click(timeout=5000); log("로그인 상태 유지: 예"); pg.wait_for_timeout(4000)
    except Exception: pass
    shot(pg, "3_staysignedin.png")

    pg.wait_for_timeout(6000)
    log("현재 URL: " + pg.url)
    b2 = cur()
    if "portal.azure.com" in pg.url and ("리소스" in b2 or "대시보드" in b2 or "Microsoft Azure" in b2 or "모든 서비스" in b2):
        log("✅ 포털 로그인 성공한 듯")
    shot(pg, "4_portal.png")
    log("READY — 브라우저 4분 유지. 비밀번호 안 되면 화면에서 직접 PIN/지문/얼굴로 로그인하세요.")
    for i in range(24):
        time.sleep(10)
        # 도중에 포털 진입하면 사용량 페이지로 이동 시도
        try:
            if "portal.azure.com" in pg.url and i == 6:
                pg.goto("https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/SpeechServices", wait_until="domcontentloaded")
                log("Speech 서비스 허브로 이동 시도")
        except Exception: pass
    shot(pg, "5_final.png")
    log("최종 URL: " + pg.url)
    ctx.close()
print("END")
