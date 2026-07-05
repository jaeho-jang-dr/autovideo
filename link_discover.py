# -*- coding: utf-8 -*-
"""쇼츠 '관련 동영상' 피커 DOM 탐색: 편집 페이지 열고 피커 트리거 클릭 후 구조 덤프.
사용: python link_discover.py [short_id]"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

SID = sys.argv[1] if len(sys.argv) > 1 else "OAnDgIm3M_g"
os.makedirs("scratch/yt", exist_ok=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto(f"https://studio.youtube.com/video/{SID}/edit", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)

    def dump(tag):
        try:
            pg.screenshot(path=f"scratch/yt/disc_{tag}.png", full_page=True)
        except Exception as e:
            print("shot err", str(e)[:60])
        print(f"--- BODY KEYWORDS [{tag}] ---")
        try:
            b = pg.inner_text("body")
            for kw in ["관련 동영상", "관련 콘텐츠", "코드 스캔", "고급 기능", "인증", "동영상 추가",
                       "관련성", "링크", "video-verification", "관련 링크"]:
                if kw in b: print("  HIT:", kw)
        except Exception as e:
            print("body err", str(e)[:60])

    print("=== INITIAL PAGE ===", pg.url)
    dump("00_initial")

    # picker 트리거 존재/개수
    for sel in ["ytcp-shorts-content-links-picker",
                "ytcp-shorts-content-links-picker ytcp-dropdown-trigger",
                "ytcp-video-metadata-related-video",
                "[test-id*='related']"]:
        try:
            n = pg.locator(sel).count()
            print(f"COUNT {sel}: {n}")
        except Exception as e:
            print(f"COUNT {sel}: ERR {str(e)[:40]}")

    # 트리거 클릭
    clicked = False
    for sel in ["ytcp-shorts-content-links-picker ytcp-dropdown-trigger",
                "ytcp-shorts-content-links-picker"]:
        try:
            loc = pg.locator(sel).first
            if loc.count() > 0:
                loc.scroll_into_view_if_needed(timeout=4000)
                loc.click(timeout=5000)
                clicked = True
                print("CLICKED:", sel)
                break
        except Exception as e:
            print("click err", sel, str(e)[:60])
    pg.wait_for_timeout(3500)
    dump("01_after_trigger")

    # 열린 다이얼로그/메뉴/입력창 덤프
    for sel in ["tp-yt-paper-dialog", "ytcp-dialog", "ytcp-text-menu",
                "input#search-input", "input[aria-label*='검색']", "input"]:
        try:
            n = pg.locator(sel).count()
            print(f"OPEN COUNT {sel}: {n}")
        except Exception:
            pass

    # 첫 다이얼로그 outerHTML 앞부분
    for sel in ["ytcp-dialog", "tp-yt-paper-dialog"]:
        try:
            loc = pg.locator(sel).first
            if loc.count() > 0 and loc.is_visible():
                html = loc.evaluate("el => el.outerHTML")
                print(f"=== {sel} HTML (first 2500) ===")
                print(html[:2500])
                break
        except Exception as e:
            print("html err", sel, str(e)[:60])

    print("READY — 20초 대기 후 종료")
    pg.wait_for_timeout(20000)
    ctx.close()
print("END")
