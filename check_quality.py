# -*- coding: utf-8 -*-
"""세종 본편(6lGedBJ5xx4) 재생 화질 옵션(1080p/2160p 4K) 활성화 확인."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
VID = "6lGedBJ5xx4"
def log(m): print(m, flush=True)
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu", "--autoplay-policy=no-user-gesture-required"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto(f"https://www.youtube.com/watch?v={VID}", wait_until="domcontentloaded")
    pg.wait_for_timeout(12000)
    # 재생 시작
    try: pg.keyboard.press("k")
    except Exception: pass
    pg.wait_for_timeout(3000)
    # 설정(톱니바퀴) 클릭
    try:
        pg.locator("button.ytp-settings-button").first.click(timeout=6000); pg.wait_for_timeout(1500); log("설정 열기")
    except Exception as e: log("설정버튼 실패 " + str(e)[:50])
    # 화질 메뉴 클릭
    try:
        pg.get_by_text("화질", exact=False).first.click(timeout=5000); pg.wait_for_timeout(1500); log("화질 메뉴")
    except Exception:
        try: pg.get_by_text("Quality", exact=False).first.click(timeout=4000); pg.wait_for_timeout(1500); log("Quality 메뉴")
        except Exception as e: log("화질메뉴 실패 " + str(e)[:50])
    pg.wait_for_timeout(1000); pg.screenshot(path="scratch/yt/quality.png")
    # 해상도 옵션 텍스트 추출
    opts = pg.evaluate("""() => {
      const out=[];
      document.querySelectorAll('.ytp-menuitem-label, .ytp-quality-menu .ytp-menuitem').forEach(e=>{
        const t=(e.textContent||'').trim(); if(t) out.push(t);
      });
      return [...new Set(out)];
    }""")
    log("해상도 옵션: " + " | ".join(opts))
    ctx.close()
print("END")
