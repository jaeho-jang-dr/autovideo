# -*- coding: utf-8 -*-
"""자막 파일 업로드 → 게시. KO는 동영상언어 행에 바로, 그 외는 언어추가 후.
사용: python yt_sub_up.py <VID> <UI언어명> <srt> <add:0|1>"""
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
        try: pg.screenshot(path=f"scratch/yt/su_{tag}_{n}.png")
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

    # 언어행 자막칸 클릭 → 편집기
    lb=pg.get_by_text(UILANG, exact=True).first.bounding_box()
    if not lb: log("언어행 못찾음:"+UILANG); shot("norow"); ctx.close(); sys.exit(1)
    hx=None
    for h in pg.get_by_text("자막", exact=True).all():
        b=h.bounding_box()
        if b and b["x"]>400: hx=b["x"]+b["width"]/2; break
    cy=lb["y"]+lb["height"]/2
    log(f"자막칸=({round(hx)},{round(cy)})")
    pg.mouse.move(hx,cy); pg.wait_for_timeout(900); pg.mouse.click(hx,cy); pg.wait_for_timeout(4500); shot("01editor")

    # 파일 업로드
    ok=False
    try:
        with pg.expect_file_chooser(timeout=9000) as fc:
            pg.get_by_text("파일 업로드", exact=True).first.click(timeout=4000); log("파일 업로드 클릭")
        fc.value.set_files(SRT); ok=True; log("파일지정 "+os.path.basename(SRT))
    except Exception as e:
        log("파일업로드 실패:"+str(e)[:70])
        # file input 직접
        try:
            pg.locator("input[type=file]").first.set_input_files(SRT); ok=True; log("input 직접 지정")
        except Exception as e2: log("input실패:"+str(e2)[:50])
    pg.wait_for_timeout(3500); shot("02loaded")
    # 시간코드 다이얼로그 대응
    for t in ["시간 코드 포함","계속","확인"]:
        try:
            el=pg.get_by_text(t, exact=False).first
            if el.is_visible(timeout=1200): el.click(); log("'"+t+"'"); pg.wait_for_timeout(1500); break
        except Exception: pass
    pg.wait_for_timeout(2000); shot("03ready")

    # 게시
    pub=False
    for t in ["게시","저장"]:
        try:
            b=pg.get_by_text(t, exact=True).first
            if b.is_visible(timeout=2500): b.click(); pub=True; log("'"+t+"' 게시"); break
        except Exception: pass
    pg.wait_for_timeout(5000); shot("04done")
    log(f"=== {UILANG}: 파일={ok} 게시={'✅' if pub else '❌'} ===")
    pg.wait_for_timeout(1000); ctx.close()
log("DONE")
