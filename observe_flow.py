# -*- coding: utf-8 -*-
"""Flow 9:16 영상 생성이 실제로 완료되는지 '눈으로' 관찰하는 진단 스크립트.
검증된 업로드/애니메이션/생성 함수는 그대로 쓰고, 결과 캡처만 주기적 스크린샷+상태감지로 대체.
사용: python observe_flow.py <이미지경로> "<모션프롬프트>"
결과: scratch/obs/ 에 20초 간격 스크린샷 + 콘솔에 상태 로그.
"""
import sys, os, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

IMG = sys.argv[1] if len(sys.argv) > 1 else "shorts_src/scene_0.png"
MOTION = sys.argv[2] if len(sys.argv) > 2 else "slow motion yellow highlights trace the title letters, subtle camera push-in, hand-drawn look"
IMG = os.path.abspath(IMG)
OBS = os.path.abspath("scratch/obs")
os.makedirs(OBS, exist_ok=True)

def log(m): print(m, flush=True);

# 화면에서 에러/토스트/상태 텍스트를 긁어오는 JS
# (캔버스 중앙영역 x>480 에 나타나는 '비디오'만 카운트 — 사이드바 갤러리 오탐 방지)
STATUS_JS = r"""
() => {
  const bits = [];
  for (const el of document.querySelectorAll('[role="alert"],[class*="toast"],[class*="Toast"],[class*="snackbar"]')) {
    const t=(el.textContent||'').trim();
    if (t && t.length<200) bits.push('ALERT: '+t);
  }
  // 실제 <video> 요소 (완성/재생가능 영상)
  let videos=0, canvasVideos=0;
  for (const v of document.querySelectorAll('video')) {
    videos++;
    const r=v.getBoundingClientRect();
    if (r.width>150 && r.x>480) canvasVideos++;
  }
  // 캔버스(x>480)에 있는 큰 미디어 타일(이미지 포함)
  let canvasTiles=0;
  for (const im of document.querySelectorAll('img')) {
    const s=im.getAttribute('src')||'';
    if (!/media\.getMediaUrlRedirect|googleusercontent/.test(s)) continue;
    const r=im.getBoundingClientRect();
    if (r.width>150 && r.x>480) canvasTiles++;
  }
  // 진행중 스피너/로딩/진행바
  let spin=0;
  for (const el of document.querySelectorAll('[class*="spinner"],[class*="Spinner"],[class*="loading"],[class*="Loading"],[role="progressbar"]')) {
    const r=el.getBoundingClientRect();
    if (r.width>0) spin++;
  }
  const bodyTxt = document.body.innerText || '';
  const marks = [];
  for (const kw of ['생성 중','생성하는 중','Generating','대기열','처리 중','크레딧이 부족','오류','실패','할 수 없','문제가','다시 시도','제한']) {
    if (bodyTxt.includes(kw)) marks.push(kw);
  }
  return {videos, canvasVideos, canvasTiles, spinners:spin, marks, alerts:bits.slice(0,5)};
}
"""

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(
        af.PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
        accept_downloads=True, downloads_path=af.DL_DIR, slow_mo=150,
        ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR", "--disable-gpu"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.set_default_timeout(30000)

    try:
        log("[1] 새 프로젝트 진입...")
        if not af.open_new_project(page):
            log("[ERR] 프로젝트 진입 실패"); page.screenshot(path=os.path.join(OBS,"fail_entry.png")); ctx.close(); sys.exit(1)
        page.screenshot(path=os.path.join(OBS,"01_editor.png"))

        log(f"[2] 이미지 업로드: {IMG}")
        if not af.upload_image(page, IMG):
            log("[ERR] 업로드 실패"); page.screenshot(path=os.path.join(OBS,"fail_upload.png")); ctx.close(); sys.exit(1)
        page.wait_for_timeout(9000)
        page.screenshot(path=os.path.join(OBS,"02_uploaded.png"))

        log("[3] 애니메이션 적용...")
        animated = False
        for a in range(4):
            if af.animate_image(page): animated=True; break
            log(f"    재시도 {a+1}/4"); page.wait_for_timeout(4000)
        if not animated:
            log("[ERR] 애니메이션 적용 실패"); page.screenshot(path=os.path.join(OBS,"fail_animate.png")); ctx.close(); sys.exit(1)
        page.wait_for_timeout(1500)
        page.screenshot(path=os.path.join(OBS,"03_animate_ready.png"))

        log("[4] 모션 프롬프트 입력 + 생성 실행")
        af.fill_prompt(page, MOTION)
        if not af.generate(page):
            log("[ERR] 생성 버튼 클릭 실패"); page.screenshot(path=os.path.join(OBS,"fail_generate.png")); ctx.close(); sys.exit(1)
        log("    생성 명령 실행됨. 이제 4분간 30초 간격 전량 관찰(조기종료 없음).")

        # 관찰 루프: 최대 4분(240초), 30초 간격, 조기종료 없이 매 구간 스크린샷+상태
        t0 = time.time()
        i = 0
        while time.time() - t0 < 240:
            page.wait_for_timeout(30000)
            i += 1
            elapsed = int(time.time()-t0)
            shotpath = os.path.join(OBS, f"obs_{i:02d}_{elapsed}s.png")
            try:
                page.screenshot(path=shotpath)
            except Exception as e:
                log(f"    [{elapsed}s] 스크린샷 실패(드라이버死?): {str(e)[:60]}"); break
            try:
                st = page.evaluate(STATUS_JS)
                log(f"    [{elapsed}s] videos={st['videos']} canvasVideos={st['canvasVideos']} canvasTiles={st['canvasTiles']} spinners={st['spinners']} marks={st['marks']} alerts={st['alerts']}")
            except Exception as e:
                log(f"    [{elapsed}s] 상태 감지 실패: {str(e)[:80]}")

        log("[관찰 종료] scratch/obs/ 스크린샷 확인")
        page.wait_for_timeout(1500)
    except Exception as e:
        log(f"[FATAL] {type(e).__name__}: {str(e)[:200]}")
        try: page.screenshot(path=os.path.join(OBS,"fatal.png"))
        except Exception: pass
    finally:
        try: ctx.close()
        except Exception: pass
log("OBSERVE_DONE")
