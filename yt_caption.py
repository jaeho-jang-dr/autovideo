# -*- coding: utf-8 -*-
"""자막 업로드 v3 — 자막칸 클릭→편집기→'파일 업로드' 옵션(정확한 요소)→파일→게시.
사용: python yt_caption.py <VID> <UI언어명> <srt> <add:0|1>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID=sys.argv[1]; UILANG=sys.argv[2]; SRT=os.path.abspath(sys.argv[3]); ADD=(len(sys.argv)>4 and sys.argv[4]=="1")
def log(m): print(m,flush=True)

with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(af.PROFILE,channel="chrome",headless=False,locale="ko-KR",no_viewport=True,accept_downloads=True,ignore_default_args=["--enable-automation"],args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg=ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    os.makedirs("scratch/yt",exist_ok=True); tag=UILANG.replace(" ","").replace("(","").replace(")","")
    def shot(n):
        try: pg.screenshot(path=f"scratch/yt/cap_{tag}_{n}.png")
        except Exception: pass
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations",wait_until="domcontentloaded"); pg.wait_for_timeout(8000)
    if ADD:
        try: pg.get_by_text("언어 추가",exact=True).first.click(timeout=6000); log("언어추가"); pg.wait_for_timeout(1800)
        except Exception as e: log("언어추가 실패 "+str(e)[:40])
        try: pg.get_by_text(UILANG,exact=True).last.click(timeout=5000); log(UILANG+" 선택")
        except Exception as e: log(UILANG+" 선택실패 "+str(e)[:40])
        pg.keyboard.press("Escape"); pg.wait_for_timeout(2500)
    lb=pg.get_by_text(UILANG,exact=True).first.bounding_box()
    if not lb: log("언어행 없음"); shot("norow"); ctx.close(); sys.exit(1)
    hx=None
    for h in pg.get_by_text("자막",exact=True).all():
        b=h.bounding_box()
        if b and b["x"]>400: hx=b["x"]+b["width"]/2; break
    cy=lb["y"]+lb["height"]/2
    pg.mouse.click(hx,cy); pg.wait_for_timeout(5000); shot("01editor")
    # 파일 지정 → 모든 #captions-file-loader 숨김input에 (활성 편집기 것이 다이얼로그 유발)
    got=False
    loaders=pg.locator("#captions-file-loader"); n=loaders.count(); log(f"loader {n}개")
    for i in range(n):
        try: loaders.nth(i).set_input_files(SRT); got=True; log(f"set input[{i}]")
        except Exception as e: log(f"input[{i}] 실패 "+str(e)[:30])
    pg.wait_for_timeout(3500); shot("02loaded")
    # "업로드할 자막 파일 형식 선택 — 타이밍 포함" → 계속
    try:
        b=pg.get_by_role("button",name="계속").first
        if b.is_visible(timeout=5000): b.click(); log("계속(타이밍 포함)")
    except Exception:
        try: pg.get_by_text("계속",exact=True).first.click(timeout=3000); log("계속(text)")
        except Exception as e: log("계속 실패 "+str(e)[:40])
    pg.wait_for_timeout(5000); shot("03loaded2")
    # 게시 (편집기 우상단)
    pub=False
    try:
        b=pg.get_by_role("button",name="게시").first
        if b.is_visible(timeout=5000): b.click(); pub=True; log("게시")
    except Exception:
        try: pg.get_by_text("게시",exact=True).first.click(timeout=3000); pub=True; log("게시(text)")
        except Exception as e: log("게시 실패 "+str(e)[:40])
    pg.wait_for_timeout(6000); shot("04done")
    log(f"=== {UILANG}: 파일={got} 게시={'OK' if pub else 'NO'} ===")
    ctx.close()
log("DONE")
