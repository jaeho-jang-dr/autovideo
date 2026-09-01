# -*- coding: utf-8 -*-
"""졸라걸 뒷모습(180도) 기준 이미지 1장 — 정면 기준 이미지를 나노 바나나 편집기로 회전.

★사장님 지시(2026-08-12, flow_cdp_pipeline.py에 이미 확정): "playwright locator.click()
사용하라." — 좌표 클릭(page.mouse.click/dblclick)은 팝오버·오버레이에 가로채여도 성공한
것처럼 보여 원인을 가린다. 이 스크립트는 **좌표를 전혀 쓰지 않는다** — 요소를 찾아 표식을
달고(`flow_cdp_pipeline.find_btn` 방식) 그 표식으로 locator 를 만들어 click()/dblclick() 한다.
(1차 시도가 `flow_make_pose.py`의 옛 좌표 방식을 그대로 베껴 실패했다 — 이 판이 수정판이다.)

사용:
  python W1_2/flow_make_zgirl_back.py
"""
import argparse
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from playwright.sync_api import sync_playwright          # noqa: E402
import flow_cdp_pipeline as P                             # noqa: E402
import autoveo_flow as avf                                # noqa: E402

GUIDE = os.path.abspath("W1_2/motion_src/guide_zgirl_front.png")
OUT = os.path.abspath("W1_2/motion_src/guide_zgirl_back.png")
DL_DIR = "debug/downloads"

PROMPT = (
    "Keep this exact character unchanged except for the rotation described below: a "
    "hand-drawn stick figure with a black outline, a round WHITE face, ORANGE HAIR tied "
    "up in a small bun on top (the only colour anywhere on her), plain white background, "
    "no shading, no floor line, no shadow, no text. "
    "★LIMB THICKNESS - STRICT: arms and legs stay THIN, SINGLE-WEIGHT LINES exactly as "
    "thin as the reference - never thicker, never filled in as solid shapes, no fat "
    "tube-like limbs. Exactly two arms and exactly two legs, same length and proportions "
    "as the reference, standing upright and centred, whole body inside the frame.\n\n"
    "BODY ROTATION - EXACTLY 180 DEGREES from the reference (the reference faces the "
    "camera at 0 degrees). Turn her all the way around so we see her BACK. Her back, "
    "the back of her shoulders, and the back of her legs and shoes face the camera.\n\n"
    "WHAT IS VISIBLE ON THE HEAD, AND NOTHING ELSE: from directly behind there are NO "
    "eyes and NO mouth anywhere - the face is not visible at all. The orange hair bun "
    "sits on top of the head exactly as in the reference, and the orange hair covers "
    "the back of the head the same way it covers the front in the reference (mirrored "
    "coverage, not a bald patch). Draw nothing else on the head - no ear, no facial "
    "feature peeking through."
)


def log(m):
    print(m, flush=True)


def media_srcs(page):
    """flow_cdp_pipeline.media_tiles 와 같은 필터(미디어 img)로 src 목록을 뽑는다.
    다운로드 버튼 UI 대신 이 src 를 직접 fetch 하기 위해 좌표가 아니라 URL 이 필요하다."""
    return page.evaluate("""() => {
      const out = [];
      for (const im of document.querySelectorAll('img')) {
        // ★currentSrc 를 우선한다 — 브라우저가 실제로 로드한 **완전한 절대 URL**이다.
        //   getAttribute('src')는 프로토콜 없는 상대/protocol-relative 값(//host/...)일
        //   수 있어 APIRequestContext.get() 이 'Invalid URL'로 죽었다(2026-08-31 실측).
        let s = im.currentSrc || im.getAttribute('src') || '';
        if (s.startsWith('//')) s = 'https:' + s;   // protocol-relative 보정
        if (!/^https?:\\/\\//.test(s)) continue;      // 완전한 절대 URL만 통과
        if (!/media\\.getMediaUrlRedirect|googleusercontent/.test(s)) continue;
        const r = im.getBoundingClientRect();
        if (r.width < 60 || r.height < 60) continue;
        out.push(s);
      }
      return out;
    }""")


def mark_tile(page):
    """업로드된 이미지 타일(가장 큰 img) 하나에 CLICK_MARK 표식을 달고 그 정보를 반환.
    flow_cdp_pipeline.find_btn 과 같은 표식 방식이지만 대상이 button 이 아니라 img 다."""
    return page.evaluate("""(mark) => {
      for (const e of document.querySelectorAll('[' + mark + ']')) e.removeAttribute(mark);
      let best = null, bestArea = 0;
      for (const im of document.querySelectorAll('img')) {
        const r = im.getBoundingClientRect();
        const area = r.width * r.height;
        if (r.width < 60 || r.height < 60) continue;
        if (area > bestArea) { bestArea = area; best = {el: im, r}; }
      }
      if (!best) return null;
      best.el.setAttribute(mark, '1');
      return {w: Math.round(best.r.width), h: Math.round(best.r.height)};
    }""", P.CLICK_MARK)


def run():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    profile = os.path.abspath("assets/chrome_profile_0")

    # ★사장님 지시(2026-08-31): "크롬 완전히 새로 띄우고 다시 시도해."
    #   flow_cdp_pipeline.launch_chrome()는 9222 포트가 이미 떠 있으면 그 세션을
    #   그대로 재사용한다 — 직전 실패 시도가 남긴 깨진 화면 상태(엉뚱한 페이지, 이미
    #   /edit/ 진입해 있는 등)를 그대로 물려받아 "새 프로젝트" 버튼을 못 찾는 원인이었다.
    #   그 프로필 크롬만 강제 종료(다른 크롬 창은 안 건드림)해서 반드시 새로 띄운다.
    log("[0] 크롬 완전히 새로 — 이 프로필만 강제 종료 후 재기동")
    avf.force_kill_profile_chrome(profile)
    time.sleep(2)
    P.launch_chrome(profile)
    time.sleep(3)

    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(P.CDP_URL)
        pg = next((p for p in b.contexts[0].pages if "labs.google" in p.url), None) \
            or b.contexts[0].pages[0]
        pg.bring_to_front()
        pg.set_default_timeout(30000)

        log("[1] 새 프로젝트")
        avf.open_new_project(pg)
        pg.wait_for_timeout(3500)

        log(f"[2] 업로드 {GUIDE}")
        if not avf.upload_image(pg, GUIDE):
            log("★업로드 실패"); return False

        log("[3] 타일 렌더 대기 (locator 기반, 좌표 없음)")
        tiles = P.wait_tiles(pg, timeout_ms=60000)
        if not tiles:
            log("★타일 안 뜸"); return False
        log(f"     타일 {len(tiles)}개 확인")

        log("[4] 타일 표식 → locator.dblclick() → 편집기(나노 바나나) 진입")
        info = mark_tile(pg)
        if not info:
            log("★타일 표식 실패"); return False
        loc = pg.locator(f"[{P.CLICK_MARK}='1']")
        try:
            loc.dblclick(timeout=10000)
        except Exception as e:
            log(f"  [DBLCLICK-FALLBACK] locator 실패: {str(e).splitlines()[0][:70]}")
            try:
                loc.evaluate("""e => {
                  const opts = {bubbles:true, cancelable:true, view:window};
                  e.dispatchEvent(new MouseEvent('mousedown', opts));
                  e.dispatchEvent(new MouseEvent('mouseup', opts));
                  e.dispatchEvent(new MouseEvent('click', opts));
                  e.dispatchEvent(new MouseEvent('dblclick', opts));
                }""")
            except Exception as e2:
                log(f"★JS dblclick도 실패(좌표 안 씀): {str(e2).splitlines()[0][:70]}")
                return False
        pg.wait_for_timeout(3000)
        if "/edit/" not in pg.url:
            log(f"★편집기 진입 실패 — 현재 url: {pg.url}"); return False
        log("     편집기 진입 확인 (/edit/)")

        log("[5] 프롬프트 입력 + 실행")
        avf.fill_prompt(pg, PROMPT)
        pg.wait_for_timeout(1500)
        make_btn = P.find_btn(pg, "arrow_forward")
        if not make_btn:
            log("★실행(만들기) 버튼 못 찾음"); return False
        srcs_before = set(media_srcs(pg))
        P.click_marked(pg, make_btn, "만들기")

        log("[6] 생성 대기 + 모니터링 (최대 90초)")
        new_src = None
        for _ in range(9):
            pg.wait_for_timeout(10000)
            now = media_srcs(pg)
            fresh = [s for s in now if s not in srcs_before]
            if fresh:
                new_src = fresh[0]
                log(f"     생성 확인 (새 이미지 src 확보)"); break
        if not new_src:
            log("★생성 안 됨(새 미디어 src 없음)"); return False

        # ★사장님 지시로 재시도한 결과, 다운로드 버튼 UI 경로는 CDP 연결 세션에서
        #   debug/downloads 로 안 잡혔다(flow_make_group_w24.fetch_video 와 같은 이유로
        #   추정). **같은 해법을 그대로 적용** — 다운로드 버튼을 누르지 않고, 생성된
        #   <img> 의 src 를 인증된 요청으로 직접 받는다(브라우저 컨텍스트의 쿠키/세션
        #   그대로 사용하므로 로그인·서명 문제 없음).
        log("[7] <img> src 직접 받기 (다운로드 버튼 UI 우회)")
        r = pg.context.request.get(new_src, timeout=60000)
        if r.status != 200:
            log(f"★src 요청 실패 status={r.status}"); return False
        body = r.body()
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        tmp = OUT + ".tmp"
        open(tmp, "wb").write(body)
        if os.path.getsize(tmp) < 20_000:
            log(f"★받은 파일이 너무 작음 ({os.path.getsize(tmp)}B) — 실패로 간주"); return False
        from PIL import Image
        Image.open(tmp).convert("RGB").save(OUT)
        os.remove(tmp)
        log(f"✅ 저장: {OUT} ({os.path.getsize(OUT)//1024}KB)")
        return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.parse_args()
    sys.exit(0 if run() else 1)
