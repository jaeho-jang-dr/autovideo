# -*- coding: utf-8 -*-
"""자막 업로드 v2 — #captions-file-loader 숨김 input에 직접 set_input_files → 게시.
사용: python yt_sub_up2.py <VID> <UI언어명> <srt> <add:0|1>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID=sys.argv[1]; UILANG=sys.argv[2]; SRT=os.path.abspath(sys.argv[3]); ADD=(len(sys.argv)>4 and sys.argv[4]=="1")
def log(m): print(m, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, accept_downloads=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    os.makedirs("scratch/yt",exist_ok=True)
    tag=UILANG.replace(" ","").replace("(","").replace(")","")
    def shot(n):
        try: pg.screenshot(path=f"scratch/yt/s2_{tag}_{n}.png")
        except Exception: pass

    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded")
    pg.wait_for_timeout(8000)

    if ADD:
        try: pg.get_by_text("언어 추가", exact=True).first.click(timeout=6000); log("언어 추가")
        except Exception as e: log("언어추가 실패:"+str(e)[:50])
        pg.wait_for_timeout(1800)
        try: pg.get_by_text(UILANG, exact=True).last.click(timeout=5000); log(UILANG+" 선택")
        except Exception as e: log(UILANG+" 선택 실패:"+str(e)[:50])
        pg.keyboard.press("Escape"); pg.wait_for_timeout(2500)

    lb=pg.get_by_text(UILANG, exact=True).first.bounding_box()
    if not lb: log("언어행 못찾음:"+UILANG); shot("norow"); ctx.close(); sys.exit(1)
    hx=None
    for h in pg.get_by_text("자막", exact=True).all():
        b=h.bounding_box()
        if b and b["x"]>400: hx=b["x"]+b["width"]/2; break
    cy=lb["y"]+lb["height"]/2
    pg.mouse.click(hx,cy); pg.wait_for_timeout(5000); shot("01editor")

    # 숨김 자막 input에 직접 파일 지정
    ok=False
    try:
        loader=pg.locator("#captions-file-loader")
        loader.last.set_input_files(SRT); ok=True; log("captions-file-loader 지정: "+os.path.basename(SRT))
    except Exception as e:
        log("input 지정 실패:"+str(e)[:60])
        try: pg.locator("#captions-file-loader").first.set_input_files(SRT); ok=True; log("first 지정")
        except Exception as e2: log("first 실패:"+str(e2)[:50])
    pg.wait_for_timeout(4000); shot("02loaded")

    # 게시 (편집기 우상단)
    pub=False
    try:
        b=pg.get_by_text("게시", exact=True).first
        if b.is_visible(timeout=3000): b.click(); pub=True; log("게시 클릭")
    except Exception as e: log("게시 실패:"+str(e)[:50])
    pg.wait_for_timeout(5000); shot("03done")
    log(f"=== {UILANG}: 파일={ok} 게시={'✅' if pub else '❌'} ===")
    pg.wait_for_timeout(1000); ctx.close()
log("DONE")
