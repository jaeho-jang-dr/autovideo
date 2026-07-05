# -*- coding: utf-8 -*-
"""한 세션에서 [언어 추가 → 자막칸 클릭 → 파일 업로드 → 게시] 원자적 수행.
사용: python yt_sub_full.py <VIDEO_ID> <UI언어명> <srt경로>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]; UILANG = sys.argv[2]; SRT = os.path.abspath(sys.argv[3])
def log(m): print(m, flush=True)

# querySelectorAll 로 언어행 y + 자막열 x (YT Studio 라벨은 라이트DOM 슬롯에 있음)
CELL_JS = """(lang) => {
  let langEl=null, hdr=null;
  document.querySelectorAll('*').forEach(e=>{
    if(e.childElementCount===0){
      const t=(e.textContent||'').trim();
      if(t===lang && !langEl){ if(e.getBoundingClientRect().x<400) langEl=e; }
      if(t==='자막' && !hdr){ if(e.getBoundingClientRect().x>400) hdr=e; }
    }
  });
  if(!langEl||!hdr) return null;
  const lr=langEl.getBoundingClientRect(), hr=hdr.getBoundingClientRect();
  return {x: Math.round(hr.x+hr.width/2), y: Math.round(lr.y+lr.height/2), lx: Math.round(lr.x)};
}"""

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, accept_downloads=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    os.makedirs("scratch/yt", exist_ok=True)
    def shot(n):
        try: pg.screenshot(path=f"scratch/yt/f_{UILANG}_{n}.png")
        except Exception: pass

    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded")
    pg.wait_for_timeout(8000); shot("01")

    # 1) 언어 추가 → 언어 선택
    try:
        pg.get_by_text("언어 추가", exact=True).first.click(timeout=6000); log("언어 추가")
    except Exception as e: log("언어추가 실패:"+str(e)[:50])
    pg.wait_for_timeout(1800)
    try:
        box = pg.locator("input").first
        if box.count() and box.is_visible(timeout=1500):
            box.fill(UILANG); pg.wait_for_timeout(1000)
    except Exception: pass
    try:
        pg.get_by_text(UILANG, exact=True).first.click(timeout=6000); log(UILANG+" 선택")
    except Exception as e: log(UILANG+" 선택 실패:"+str(e)[:50])
    pg.wait_for_timeout(3000); shot("02")

    # 2) 자막칸 좌표 → hover → 클릭 (편집기 진입)
    cell = pg.evaluate(CELL_JS, UILANG)
    log("자막칸: "+str(cell))
    if not cell:
        log("자막칸 못찾음"); shot("02b"); ctx.close(); sys.exit(1)
    pg.mouse.move(cell["x"], cell["y"]); pg.wait_for_timeout(1000); shot("03hover")
    pg.mouse.click(cell["x"], cell["y"]); pg.wait_for_timeout(5000); shot("04editor")
    log("URL: "+pg.url)

    # 3) 파일 업로드
    ok=False
    try:
        with pg.expect_file_chooser(timeout=9000) as fc:
            for t in ["파일 업로드","업로드"]:
                try: pg.get_by_text(t, exact=False).first.click(timeout=3000); log("'"+t+"'"); break
                except Exception: pass
        fc.value.set_files(SRT); ok=True; log("파일지정 "+os.path.basename(SRT))
    except Exception as e:
        log("1차 업로드실패:"+str(e)[:60])
        try:
            pg.get_by_text("시간 코드 포함", exact=False).first.click(timeout=2500)
            with pg.expect_file_chooser(timeout=6000) as fc2:
                for t in ["계속","파일 업로드","업로드"]:
                    try: pg.get_by_text(t, exact=False).first.click(timeout=2500); break
                    except Exception: pass
            fc2.value.set_files(SRT); ok=True; log("2차 파일지정")
        except Exception as e2: log("2차 실패:"+str(e2)[:60])
    pg.wait_for_timeout(4000); shot("05uploaded")

    # 시간코드 포함(파일 뒤 다이얼로그)
    try:
        el=pg.get_by_text("시간 코드 포함", exact=False).first
        if el.is_visible(timeout=1500): el.click(); pg.wait_for_timeout(800)
    except Exception: pass

    # 4) 게시
    pub=False
    for t in ["게시","저장","완료"]:
        try:
            b=pg.get_by_text(t, exact=True).first
            if b.is_visible(timeout=2500): b.click(); pub=True; log("'"+t+"' 클릭"); break
        except Exception: pass
    pg.wait_for_timeout(5000); shot("06done")
    log("게시완료" if pub else "게시버튼 못찾음")
    pg.wait_for_timeout(1000); ctx.close()
log("DONE")
