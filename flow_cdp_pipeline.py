# -*- coding: utf-8 -*-
"""flow_cdp_pipeline.py — Google Flow 영상 생성 파이프라인 (CDP 9222 + Playwright).

2026-07-26 검증 완료. `autoveo_flow.py --upload` 방식이 '애니메이션 적용' 단계에서
반복 실패하던 문제를 UI 절차 자체를 사장님 수동 절차 그대로 옮겨서 해결한 버전.

절차 (사장님 확정):
  1. 크롬을 --remote-debugging-port=9222 로 직접 띄우고 CDP 로 붙는다
     (launch_persistent_context 는 프로필 락이 남아 있으면 로그도 없이 무한 대기)
  2. 새 프로젝트 → 우상단 '+' (미디어 추가) → '미디어 업로드' → 파일 선택
  3. 업로드 30초 대기 (타일이 뜨기 전엔 아무 메뉴도 안 나옴)
  4. 타일 hover → '⋮' → '프롬프트에 추가'
  5. 모델 칩(토글) → '동영상' → 모델 드롭다운 → 'Veo 3.1 - Lite' → 9:16 / 1x / 8s
  6. 프롬프트 클립보드 붙여넣기 → '만들기'
  7. 90초 대기 (그 이상 걸리면 실패로 본다)
  8. 제일 위 왼쪽 타일 클릭 → 라이트박스 우상단 '다운로드' → 저장 후 ftyp 검증

사용:
  python flow_cdp_pipeline.py --image W22/_orig/jieun_teacher_side_right.png \
      --prompt-file prompt.txt --out W22/clips/vid_jieun_search.mp4 [--aspect 9:16]
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

import autoveo_flow as avf

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_URL = "http://localhost:9222"
UPLOAD_WAIT_MS = 30000      # 업로드 반영 대기 — 사장님 확정
GEN_WAIT_MS = 90000         # 생성 대기 — 90초면 충분, 넘으면 실패


def log(m):
    print(m, flush=True)


def launch_chrome(profile, url="https://labs.google/fx/tools/flow"):
    """CDP 포트가 이미 열려 있으면 재사용, 아니면 프로필 락 정리 후 새로 띄운다."""
    try:
        urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=2)
        log("  [CDP] 기존 9222 세션 재사용")
        return
    except Exception:
        pass
    avf.force_kill_profile_chrome(profile)
    time.sleep(2)
    subprocess.Popen([
        CHROME, "--remote-debugging-port=9222", f"--user-data-dir={profile}",
        "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR",
        "--window-size=1680,1000", url,
    ])
    for _ in range(20):
        time.sleep(1)
        try:
            urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=2)
            log("  [CDP] 크롬 기동 완료")
            return
        except Exception:
            pass
    raise RuntimeError("CDP 9222 기동 실패")


def find_btn(page, rx, ymin=None):
    """정규식으로 보이는 버튼/메뉴항목 하나를 찾아 {t,x,y} 반환."""
    return page.evaluate("""([rx, ymin]) => {
      const re = new RegExp(rx);
      for (const b of document.querySelectorAll("button,[role='button'],[role='menuitem'],[role='option']")) {
        const r = b.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        if (ymin !== null && r.top < ymin) continue;
        const t = (b.innerText || '').trim();
        if (re.test(t))
          return {t: t.slice(0, 40), x: Math.round(r.left + r.width / 2),
                  y: Math.round(r.top + r.height / 2)};
      }
      return null;
    }""", [rx, ymin])


def click_btn(page, rx, ymin=None, wait=1200, label=""):
    b = find_btn(page, rx, ymin)
    if not b:
        log(f"  [MISS] 버튼 못 찾음: {label or rx}")
        return False
    page.mouse.click(b["x"], b["y"])
    page.wait_for_timeout(wait)
    log(f"  [CLICK] {label or rx} → {b['t']!r} ({b['x']},{b['y']})")
    return True


def media_tiles(page):
    """미디어 그리드의 타일 목록(위→아래, 왼→오른쪽 정렬)."""
    return page.evaluate("""() => {
      const out = [];
      for (const im of document.querySelectorAll('img')) {
        const s = im.getAttribute('src') || '';
        if (!/media\\.getMediaUrlRedirect|googleusercontent/.test(s)) continue;
        const r = im.getBoundingClientRect();
        if (r.width < 100 || r.height < 100) continue;
        out.push({x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2),
                  w: Math.round(r.width), h: Math.round(r.height)});
      }
      out.sort((a, b) => a.y - b.y || a.x - b.x);
      return out;
    }""")


def open_chip(page):
    """모델 칩은 토글 — 하위 옵션이 보일 때까지 눌러서 연다."""
    for _ in range(3):
        if find_btn(page, "arrow_drop_down"):
            return True
        chip = find_btn(page, "crop_|동영상 ·|Nano", ymin=1000)
        if not chip:
            return False
        page.mouse.click(chip["x"], chip["y"])
        page.wait_for_timeout(1500)
    return bool(find_btn(page, "arrow_drop_down"))


def run(image, prompt, out, aspect="9:16", model="Veo 3.1 - Lite", profile=None):
    profile = profile or os.path.abspath("assets/chrome_profile_0")
    image = os.path.abspath(image)
    out = os.path.abspath(out)
    assert os.path.exists(image), image
    os.makedirs(os.path.dirname(out), exist_ok=True)

    launch_chrome(profile)
    with sync_playwright() as p:
        br = p.chromium.connect_over_cdp(CDP_URL)
        ctx = br.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.bring_to_front()

        # 1) 새 프로젝트
        avf.open_new_project(page)
        page.wait_for_timeout(3000)

        # 2) '+' 미디어 추가 → '미디어 업로드' → 파일
        if not click_btn(page, "^add\\n미디어 추가", label="미디어 추가(+)"):
            raise RuntimeError("'+' 버튼 없음")
        up = find_btn(page, "미디어 업로드")
        if not up:
            raise RuntimeError("'미디어 업로드' 메뉴 없음")
        with page.expect_file_chooser(timeout=15000) as fc:
            page.mouse.click(up["x"], up["y"])
        fc.value.set_files(image)
        log(f"  [UPLOAD] {image}")

        # 3) 업로드 반영 대기
        page.wait_for_timeout(UPLOAD_WAIT_MS)
        tiles = media_tiles(page)
        if not tiles:
            raise RuntimeError("업로드 타일이 뜨지 않음")

        # 4) 타일 ⋮ → '프롬프트에 추가'
        t0 = tiles[0]
        page.mouse.move(t0["x"], t0["y"])
        page.wait_for_timeout(1500)
        if not click_btn(page, "more_vert\\n더 생성하기", ymin=t0["y"] - 260, label="타일 ⋮"):
            raise RuntimeError("타일 ⋮ 없음")
        if not click_btn(page, "프롬프트에 추가", label="프롬프트에 추가"):
            raise RuntimeError("'프롬프트에 추가' 없음")

        # 5) 동영상 / 모델 / 비율 / 1개
        if not open_chip(page):
            raise RuntimeError("모델 칩 열기 실패")
        click_btn(page, "play_circle\\n동영상", label="동영상")
        open_chip(page)
        click_btn(page, "arrow_drop_down", label="모델 드롭다운")
        click_btn(page, model, label=model)
        open_chip(page)
        click_btn(page, f"crop_\\S*\\n{aspect}", label=aspect)
        open_chip(page)
        click_btn(page, "^1x$", label="1x")
        page.keyboard.press("Escape")
        page.wait_for_timeout(800)
        chip = find_btn(page, "crop_|동영상 ·", ymin=1000)
        log(f"  [CHIP] {chip['t']!r}" if chip else "  [CHIP] 확인 불가")

        # 6) 프롬프트 붙여넣기 → 만들기
        avf.fill_prompt(page, prompt)          # 클립보드 Ctrl+V (Slate 에디터 대응)
        page.wait_for_timeout(1000)
        if not avf.generate(page):
            raise RuntimeError("'만들기' 클릭 실패")

        # 7) 90초 대기
        log(f"  [WAIT] {GEN_WAIT_MS // 1000}초 생성 대기")
        page.wait_for_timeout(GEN_WAIT_MS)

        # 8) 제일 위 왼쪽 타일 → 라이트박스 우상단 다운로드
        tiles = media_tiles(page)
        if not tiles:
            raise RuntimeError("생성 타일 없음 — 90초 내 미완성 = 실패")
        page.mouse.click(tiles[0]["x"], tiles[0]["y"])
        page.wait_for_timeout(2500)
        dl = find_btn(page, "download\\n다운로드")
        if not dl:
            raise RuntimeError("라이트박스 다운로드 버튼 없음")
        with page.expect_download(timeout=120000) as info:
            page.mouse.click(dl["x"], dl["y"])
            page.wait_for_timeout(2500)
            for t in ("원본 크기", "원본", "720p", "1080p", "다운로드"):
                try:
                    loc = page.locator(f"text={t}").first
                    if loc.is_visible(timeout=800):
                        loc.click(timeout=3000)
                        break
                except Exception:
                    pass
        info.value.save_as(out)
        br.close()

    size = os.path.getsize(out)
    with open(out, "rb") as f:
        ok = b"ftyp" in f.read(12)
    log(f"[{'OK' if ok and size else 'FAIL'}] {out} ({size} bytes, mp4={ok})")
    return ok and size > 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="첫 프레임으로 쓸 기초 이미지")
    ap.add_argument("--prompt-file", required=True, help="모션 프롬프트 텍스트 파일(UTF-8)")
    ap.add_argument("--out", required=True, help="저장할 mp4 경로")
    ap.add_argument("--aspect", default="9:16", help="9:16 또는 16:9")
    ap.add_argument("--model", default="Veo 3.1 - Lite")
    ap.add_argument("--profile", default=None, help="크롬 프로필 (기본 assets/chrome_profile_0)")
    a = ap.parse_args()
    prompt = open(a.prompt_file, encoding="utf-8").read().strip()
    sys.exit(0 if run(a.image, prompt, a.out, a.aspect, a.model, a.profile) else 1)


if __name__ == "__main__":
    main()
