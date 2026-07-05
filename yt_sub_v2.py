# -*- coding: utf-8 -*-
"""자막 업로드 v2 — 언어추가→(자막칸 hover→추가)→파일업로드→게시. 한 세션 원자적.
사용: python yt_sub_v2.py <VIDEO_ID> <UI언어명> <srt>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID=sys.argv[1]; LANG=sys.argv[2]; SRT=os.path.abspath(sys.argv[3])
def log(m): print(m, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, accept_downloads=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    os.makedirs("scratch/yt", exist_ok=True)
    def shot(n):
        try: pg.screenshot(path=f"scratch/yt/v2_{LANG}_{n}.png")
        except Exception: pass
    def bbox(loc):
        try: return loc.bounding_box(timeout=4000)
        except Exception: return None

    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded")
    pg.wait_for_timeout(8000); shot("01")

    # 1) 언어 추가 → 언어 선택 (검색창 입력 안 함)
    try: pg.get_by_text("언어 추가", exact=True).first.click(timeout=6000); log("언어 추가")
    except Exception as e: log("언어추가 실패:"+str(e)[:50])
    pg.wait_for_timeout(2000); shot("02menu")
    try:
        pg.get_by_role("option", name=LANG).first.click(timeout=4000); log(LANG+" 선택(option)")
    except Exception:
        try: pg.get_by_text(LANG, exact=True).last.click(timeout=5000); log(LANG+" 선택(text.last)")
        except Exception as e: log(LANG+" 선택 실패:"+str(e)[:50])
    pg.keyboard.press("Escape"); pg.wait_for_timeout(2500); shot("03added")
    log("URL after add: "+pg.url)

    # 혹시 언어 선택하자마자 편집기로 진입했는지 확인
    editor_now = False
    for t in ["파일 업로드","자동 동기화","직접 입력"]:
        try:
            if pg.get_by_text(t, exact=False).first.is_visible(timeout=1200): editor_now=True; break
        except Exception: pass

    if not editor_now:
        # 2) 자막칸 hover → 추가 클릭
        en = pg.get_by_text(LANG, exact=True).first
        enb = bbox(en)
        log("행 bbox: "+str(enb))
        if not enb:
            log("언어행 못찾음"); shot("03b"); ctx.close(); sys.exit(1)
        # 자막 열 헤더 x (언어행보다 오른쪽)
        hx=None
        for h in pg.get_by_text("자막", exact=True).all():
            b=bbox(h)
            if b and b["x"]>enb["x"]+80: hx=b["x"]+b["width"]/2; break
        if hx is None: hx=enb["x"]+enb["width"]+300
        cy=enb["y"]+enb["height"]/2
        log(f"자막칸 hover=({round(hx)},{round(cy)})")
        pg.mouse.move(hx, cy); pg.wait_for_timeout(1500); shot("04hover")
        # 추가 버튼(hover시 노출) 클릭, 없으면 좌표 클릭
        clicked=False
        try:
            add=pg.get_by_text("추가", exact=True)
            for i in range(add.count()):
                b=bbox(add.nth(i))
                if b and abs((b["y"]+b["height"]/2)-cy)<25:
                    add.nth(i).click(timeout=3000); clicked=True; log("'추가' 클릭"); break
        except Exception: pass
        if not clicked:
            pg.mouse.click(hx, cy); log("좌표 클릭")
        pg.wait_for_timeout(5000); shot("05editor")
        log("URL: "+pg.url)

    # 3) 파일 업로드
    ok=False
    try:
        with pg.expect_file_chooser(timeout=9000) as fc:
            for t in ["파일 업로드","업로드"]:
                try: pg.get_by_text(t, exact=False).first.click(timeout=3000); log("'"+t+"' 클릭"); break
                except Exception: pass
        fc.value.set_files(SRT); ok=True; log("파일지정 "+os.path.basename(SRT))
    except Exception as e:
        log("업로드 실패:"+str(e)[:70]); shot("05b")
    pg.wait_for_timeout(3500); shot("06uploaded")
    # 시간코드 포함
    try:
        el=pg.get_by_text("시간 코드 포함", exact=False).first
        if el.is_visible(timeout=1500): el.click(); pg.wait_for_timeout(800); log("시간코드포함")
    except Exception: pass
    # 4) 게시
    pub=False
    for t in ["게시","저장","완료"]:
        try:
            b=pg.get_by_text(t, exact=True).first
            if b.is_visible(timeout=2500): b.click(); pub=True; log("'"+t+"' 게시"); break
        except Exception: pass
    pg.wait_for_timeout(5000); shot("07done")
    log("=== 결과: "+("게시완료 ✅" if pub else "게시 못함 ❌")+" ===")
    pg.wait_for_timeout(1000); ctx.close()
log("DONE")
