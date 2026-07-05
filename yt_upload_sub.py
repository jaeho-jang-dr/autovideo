# -*- coding: utf-8 -*-
"""이미 추가된 언어 행에 자막 파일 업로드 → 게시. (자막 칸 hover→추가→파일업로드→게시)
사용: python yt_upload_sub.py <VIDEO_ID> <UI언어명> <srt경로>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]; UILANG = sys.argv[2]; SRT = os.path.abspath(sys.argv[3])
def log(m): print(m, flush=True)

def cell_coords(pg, lang):
    """Playwright 로케이터(Shadow DOM 관통)로 언어행 y + 자막열 x 산출."""
    en = pg.get_by_text(lang, exact=True).first
    enb = en.bounding_box()
    if not enb: return None
    y = enb["y"] + enb["height"]/2
    # '자막' 열 헤더 x (사이드바 자막 x<400 제외)
    hx = None
    for h in pg.get_by_text("자막", exact=True).all():
        b = h.bounding_box()
        if b and b["x"] > 400:
            hx = b["x"] + b["width"]/2; break
    if hx is None: hx = enb["x"] + 560   # 폴백: 언어 x + 오프셋
    return {"x": round(hx), "y": round(y)}

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, accept_downloads=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    os.makedirs("scratch/yt", exist_ok=True)
    def shot(n):
        try: pg.screenshot(path=f"scratch/yt/up_{UILANG}_{n}.png")
        except Exception: pass

    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded")
    pg.wait_for_timeout(8000)
    cell = cell_coords(pg, UILANG)
    log("자막칸 좌표: "+str(cell))
    if not cell:
        log("행/자막칸 못찾음"); shot("00_norow"); ctx.close(); sys.exit(1)
    pg.mouse.move(cell["x"], cell["y"]); pg.wait_for_timeout(1200); shot("01_hover")
    pg.mouse.click(cell["x"], cell["y"]); pg.wait_for_timeout(5000); shot("02_editor")
    log("현재 URL: "+pg.url)

    # 편집기에서 '파일 업로드'
    ok=False
    try:
        with pg.expect_file_chooser(timeout=9000) as fc:
            for t in ["파일 업로드","업로드"]:
                try: pg.get_by_text(t, exact=False).first.click(timeout=3000); log(f"'{t}' 클릭"); break
                except Exception: pass
        fc.value.set_files(SRT); ok=True; log("파일 지정: "+os.path.basename(SRT))
    except Exception as e:
        log("파일업로드 1차 실패: "+str(e)[:70])
        # '시간 코드 포함' 라디오 먼저
        try:
            pg.get_by_text("시간 코드 포함", exact=False).first.click(timeout=3000); log("시간코드포함 선택")
            with pg.expect_file_chooser(timeout=7000) as fc2:
                for t in ["계속","파일 업로드","업로드"]:
                    try: pg.get_by_text(t, exact=False).first.click(timeout=2500); break
                    except Exception: pass
            fc2.value.set_files(SRT); ok=True; log("2차 파일 지정 성공")
        except Exception as e2: log("2차 실패: "+str(e2)[:70])
    pg.wait_for_timeout(4000); shot("03_uploaded")

    # 시간코드 포함 다이얼로그가 파일 뒤에 뜨는 경우
    for t in ["시간 코드 포함"]:
        try:
            el=pg.get_by_text(t, exact=False).first
            if el.is_visible(timeout=1500): el.click(); log("시간코드포함(후)")
        except Exception: pass
    # 게시/저장
    published=False
    for t in ["게시","저장","완료","PUBLISH"]:
        try:
            b=pg.get_by_text(t, exact=True).first
            if b.is_visible(timeout=2500): b.click(); published=True; log(f"'{t}' 클릭"); break
        except Exception: pass
    pg.wait_for_timeout(5000); shot("04_done")
    log("게시완료" if published else "게시버튼 못찾음")
    pg.wait_for_timeout(1000); ctx.close()
log("DONE")
