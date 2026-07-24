# -*- coding: utf-8 -*-
"""YouTube Studio 번역 제목/설명 추가 v2. 사용: python yt_add_localization.py <vid> <lang> <title> <desc>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID, LANG, TITLE, DESC = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
tag = f"{VID}_{LANG}"
def log(m): print(m, flush=True)
def shot(n):
    try: pg.screenshot(path=f"{SH}/L_{tag}_{n}.png")
    except Exception: pass

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(20000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded"); pg.wait_for_timeout(7000)

    # 언어 이미 있나?
    exists = False
    try: exists = pg.get_by_text(LANG, exact=True).first.is_visible(timeout=2000)
    except Exception: pass
    if not exists:
        try:
            pg.get_by_text("언어 추가", exact=True).first.click(timeout=6000); pg.wait_for_timeout(1500); log("언어 추가 클릭")
            # 검색창에 입력
            try: pg.get_by_placeholder("언어 검색").fill(LANG, timeout=2500); pg.wait_for_timeout(1000)
            except Exception: pass
            pg.get_by_text(LANG, exact=True).first.click(timeout=6000); pg.wait_for_timeout(2500); log(f"{LANG} 선택")
        except Exception as e: log(f"언어추가 실패: {str(e)[:50]}")
    else: log(f"{LANG} 이미 존재")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(800); shot("1")

    # 그 언어 행의 '제목 및 설명' 셀 클릭(좌표: 언어 y, 제목및설명 x≈72%) → 편집기
    try:
        sp = pg.get_by_text(LANG, exact=True).first
        box = sp.bounding_box(); w = pg.evaluate("() => window.innerWidth")
        pg.mouse.click(w * 0.72, box["y"] + box["height"] / 2); pg.wait_for_timeout(3800); log("제목및설명 셀 클릭")
    except Exception as e: log(f"셀 클릭 실패: {str(e)[:50]}")
    shot("2")

    # 번역 제목/설명 필드 채우기
    def fill(sels, text, label):
        for s in sels:
            try:
                b = pg.locator(s).first
                if b.is_visible(timeout=1500):
                    b.click(); pg.wait_for_timeout(300); b.fill(text); log(f"{label} OK ({s})"); pg.wait_for_timeout(400); return True
            except Exception: continue
        log(f"{label} 실패(필드못찾음)"); return False
    fill(["textarea[aria-label*='제목']", "#translated-title textarea", "ytcp-social-suggestions-textbox[label*='제목'] #textbox", "input[aria-label*='제목']"], TITLE, "번역제목")
    fill(["textarea[aria-label*='설명']", "#translated-description textarea", "ytcp-social-suggestions-textbox[label*='설명'] #textbox"], DESC, "번역설명")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(500); shot("3")

    # 게시
    try:
        pg.get_by_role("button", name="게시").first.click(timeout=6000); log("게시 클릭"); pg.wait_for_timeout(4000)
    except Exception as e: log(f"게시 실패: {str(e)[:50]}")
    shot("4")
    log(f"LOC_{tag}_DONE"); pg.wait_for_timeout(1500); ctx.close()
print("END")
