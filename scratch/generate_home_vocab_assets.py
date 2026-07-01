# -*- coding: utf-8 -*-
"""
home_vocab 라인아트 정지 이미지 에셋 생성기 (Google Flow 이미지 모드)
=====================================================================
배경: autoveo_flow.py 는 Veo '동영상'(scene_N.mp4) 파이프라인이며 프롬프트
파일을 [Scene N] 형식으로만 파싱한다. 이번 작업의 prompts_for_flow.txt 는
'key: prompt' 형식의 '정지 이미지' 에셋 명세이므로 그대로는 호환되지 않는다.

이 스크립트는 autoveo_flow.py 의 검증된 1차 프리미티브
(open_new_project / set_image_mode / fill_prompt / generate) 를 그대로
재사용하되, '단일 세션' 안에서 각 프롬프트를 순차 생성하고 가장 최신(좌측)
타일을 캡처하여 home_vocab/<key>.png (RGBA) 로 저장한다.

사용:
    python scratch/generate_home_vocab_assets.py --prompts home_vocab/prompts_for_flow.txt --outdir home_vocab

특징:
  * 멱등(idempotent): 이미 존재하고 크기가 충분한 png 는 건너뜀 → 중단 후 재실행 시 이어서 진행
  * 실패 시 디버그 스크린샷(debug/asset_<key>_fail.png) 저장 후 다음 에셋으로 진행
  * 진행도 기록: <outdir>/asset_progress.json
"""

import os
import sys
import time
import json
import argparse

# 프로젝트 루트를 path 에 추가해 autoveo_flow 를 import 한다.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "scratch"))

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

import autoveo_flow as af  # noqa: E402
from PIL import Image      # noqa: E402

# 캔버스에서 '미디어 이미지' 포스터들의 src/left 목록 (좌측이 최신)
LIST_SRC_JS = r"""
() => {
  const out=[];
  for (const im of document.querySelectorAll('img')) {
    const s = im.getAttribute('src') || '';
    if (!/media\.getMediaUrlRedirect|googleusercontent/.test(s)) continue;
    const r = im.getBoundingClientRect();
    if (r.width<200 || r.height<120) continue;
    if (r.width>1200 || r.height>900) continue;
    const parent = im.closest('div');
    if (parent && (parent.querySelector('svg') || parent.querySelector('[class*=spinner]') || parent.querySelector('[class*=loading]'))) continue;
    out.push({src:s, left:Math.round(r.x)});
  }
  out.sort((a,b)=>a.left-b.left);
  return out;
}
"""

# known 목록(이전 src들)에 없는 '새' 포스터 중 가장 좌측(최신) 요소 핸들 반환
NEW_EL_JS = r"""
(known) => {
  let best=null, bestLeft=Infinity;
  for (const im of document.querySelectorAll('img')) {
    const s = im.getAttribute('src') || '';
    if (!/media\.getMediaUrlRedirect|googleusercontent/.test(s)) continue;
    const r = im.getBoundingClientRect();
    if (r.width<200 || r.height<120) continue;
    if (r.width>1200 || r.height>900) continue;
    const parent = im.closest('div');
    if (parent && (parent.querySelector('svg') || parent.querySelector('[class*=spinner]') || parent.querySelector('[class*=loading]'))) continue;
    if (known.includes(s)) continue;
    if (r.x < bestLeft){bestLeft=r.x; best=im;}
  }
  return best;
}
"""


def parse_keyed_prompts(path):
    """'key: prompt' 형식을 파싱한다. '#' 주석/빈 줄은 무시."""
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if ":" not in s:
                continue
            key, prompt = s.split(":", 1)
            key, prompt = key.strip(), prompt.strip()
            if key and prompt:
                items.append((key, prompt))
    return items


def list_srcs(page):
    try:
        return [p["src"] for p in (page.evaluate(LIST_SRC_JS) or [])]
    except Exception:
        return []


def capture_new_asset(page, known, out_path, timeout_s=15):
    """새 포스터가 뜨길 기다렸다가 클릭해서 원본 이미지를 다운로드받고 투명화 처리함."""
    deadline = time.time() + timeout_s
    handle = None
    while time.time() < deadline:
        try:
            af.shot(page, "_live")
            h = page.evaluate_handle(NEW_EL_JS, known)
            if h and h.as_element():
                handle = h
                break
        except Exception:
            pass
        page.wait_for_timeout(3000)

    if handle is None:
        af.log("  [CAPTURE] 새 타일 감지 실패")
        return False

    page.wait_for_timeout(2000)
    el = handle.as_element()
    tmp_path = out_path + ".raw.png"
    
    try:
        # 1. 타일 화면으로 스크롤 및 클릭하여 라이트박스 열기
        try:
            el.scroll_into_view_if_needed(timeout=3000)
        except Exception:
            pass
        
        af.log("  [CAPTURE] 생성된 타일을 클릭하여 라이트박스를 엽니다.")
        el.click(timeout=5000)
        page.wait_for_timeout(2000)
        
        # 라이트박스가 열렸는지 다운로드 버튼 유무로 검증
        download_btn_selectors = ["button:has-text('download')", "button[aria-label*='다운로드']", "button[aria-label*='Download']", "button:has-text('다운로드')"]
        lightbox_open = False
        for selector in download_btn_selectors:
            try:
                if page.locator(selector).first.is_visible(timeout=500):
                    lightbox_open = True
                    break
            except Exception:
                pass
                
        if not lightbox_open:
            af.log("  [WARN] 라이트박스가 열리지 않음. 1회 재클릭 시도.")
            page.wait_for_timeout(500)
            el.click(timeout=5000)
            page.wait_for_timeout(2000)
            
        # 2. 다운로드 대기 및 버튼 클릭
        download_clicked = False
        with page.expect_download(timeout=30000) as dl_info:
            for selector in download_btn_selectors:
                try:
                    loc = page.locator(selector).first
                    if loc.is_visible(timeout=1000):
                        loc.click()
                        download_clicked = True
                        break
                except Exception:
                    pass
            
            if not download_clicked:
                raise RuntimeError("라이트박스 다운로드 버튼 검출 실패")
                
            page.wait_for_timeout(1000)
            # 해상도 선택
            try:
                (af.click_text(page, "원본 크기") or af.click_text(page, "원본")
                 or af.click_text(page, "720p"))
            except Exception:
                pass
                
        d = dl_info.value
        d.save_as(tmp_path)
        af.log(f"  [CAPTURE] 이미지 파일 다운로드 성공 -> {tmp_path}")
        
        # 3. 라이트박스 닫기
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)
        
    except Exception as e:
        af.log(f"  [CAPTURE] 이미지 클릭 다운로드 실패: {e}")
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        return False

    # RGBA(4채널)로 변환 저장하고 배경을 투명하게 전처리
    try:
        from process_lineart import make_white_transparent
        # threshold=220 to filter out warm beige (#F5F5F0 or #F0F0F0) background
        success = make_white_transparent(tmp_path, out_path, threshold=220)
        if not success:
            af.log("  [CONVERT] 배경 투명화 처리 실패 (make_white_transparent 반환 False)")
            return False
    except Exception as e:
        af.log(f"  [CONVERT] 배경 투명화 전처리 예외 발생: {e}")
        return False
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

    return os.path.exists(out_path) and os.path.getsize(out_path) > 3000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", default="home_vocab/prompts_for_flow.txt")
    ap.add_argument("--outdir", default="home_vocab")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    
    # Clean up any locking Chrome processes to prevent playwright crash
    # af.force_kill_profile_chrome()
    
    items = parse_keyed_prompts(args.prompts)
    if not items:
        af.log("프롬프트 없음 — 파일/형식 확인 필요")
        return 1

    os.makedirs(args.outdir, exist_ok=True)
    os.makedirs(af.DBG, exist_ok=True)
    progress_file = os.path.join(args.outdir, "asset_progress.json")
    progress = {}
    if os.path.exists(progress_file):
        try:
            progress = json.load(open(progress_file, encoding="utf-8"))
        except Exception:
            progress = {}

    total = len(items)
    af.log(f"총 {total}개 에셋 생성 시작 (outdir={args.outdir})")

    class BrowserWrapper:
        def __init__(self, obj, is_cdp):
            self.obj = obj
            self.is_cdp = is_cdp
        def close(self):
            if self.is_cdp:
                try:
                    self.obj.disconnect()
                    af.log("  [CDP] CDP 연결이 정상적으로 종료(disconnect)되었습니다.")
                except Exception as e:
                    af.log(f"  [CDP] disconnect 오류: {e}")
            else:
                try:
                    self.obj.close()
                except Exception as e:
                    af.log(f"  [BROWSER] close 오류: {e}")

    from playwright.sync_api import sync_playwright
    ok, fail = [], []
    with sync_playwright() as p:
        def reboot_interactive_chrome():
            import subprocess
            af.log("  [REBOOT] 사용자의 실제 모니터 데스크톱 세션에 크롬을 인터랙티브하게 재기동합니다...")
            # 1. 기존 크롬 강제종료
            try:
                subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name 'chrome' -Force -ErrorAction SilentlyContinue"], timeout=10)
            except Exception:
                pass
            # 2. 락 파일 제거
            for lock in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
                p_lock = os.path.join(af.PROFILE, lock)
                if os.path.exists(p_lock) or os.path.islink(p_lock):
                    try:
                        os.remove(p_lock)
                    except Exception:
                        pass
            time.sleep(2)
            # 3. 작업 스케줄러로 대화형 크롬 재실행
            cmd = (
                '$action = New-ScheduledTaskAction -Execute "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" '
                '-Argument "--remote-debugging-port=9222 --user-data-dir=d:\\Entertainments\\DevEnvironment\\autovideo\\assets\\chrome_profile --start-maximized"; '
                '$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\\$env:USERNAME" -LogonType Interactive; '
                'Register-ScheduledTask -TaskName "LaunchChromeDebugReal" -Action $action -Principal $principal -Force; '
                'Start-ScheduledTask -TaskName "LaunchChromeDebugReal"; '
                'Start-Sleep -Seconds 3; '
                'Unregister-ScheduledTask -TaskName "LaunchChromeDebugReal" -Confirm:$false'
            )
            try:
                subprocess.run(["powershell", "-NoProfile", "-Command", cmd], timeout=30)
            except Exception as e:
                af.log(f"  [REBOOT] 스케줄러 실행 중 예외: {e}")
            time.sleep(3)

        def launch():
            # Try directly connecting to 127.0.0.1:9222 via Playwright CDP
            for attempt in range(1, 4):
                try:
                    af.log(f"  [CDP] 127.0.0.1:9222로 직접 플레이라이트 CDP 연결 시도 중... ({attempt}/3)")
                    c = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                    af.log("  [CDP] CDP 연결 성공!")
                    if c.contexts:
                        ctx = c.contexts[0]
                        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
                    else:
                        pg = c.new_page()
                    return BrowserWrapper(c, True), pg
                except Exception as e:
                    af.log(f"  [CDP] 연결 시도 {attempt}/3 실패: {e}")
                    if attempt < 3:
                        time.sleep(2)
            
            af.log("  [CDP] 모든 CDP 연결 실패. 새 브라우저 컨텍스트를 기동합니다.")
            c = p.chromium.launch_persistent_context(
                af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
                no_viewport=True, accept_downloads=True, downloads_path=af.DL_DIR,
                ignore_default_args=["--enable-automation"],
                args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                      "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
            pg = c.pages[0] if c.pages else c.new_page()
            return BrowserWrapper(c, False), pg

        ctx, page = launch()

        if not af.open_new_project(page):
            af.log("[ERR] 새 프로젝트/컴포저 진입 실패 — 중단")
            af.shot(page, "home_vocab_open_fail")
            try:
                ctx.close()
            except Exception:
                pass
            return 2

        # 이미지 모드(이미지 / 16:9 / 1x) 1회 설정 — 세션 내 유지
        af.set_image_mode(page)

        for i, (key, prompt) in enumerate(items, 1):
            out_path = os.path.join(args.outdir, f"{key}.png")
            if not args.force and os.path.exists(out_path) and os.path.getsize(out_path) > 3000:
                af.log(f"[SKIP] ({i}/{total}) {key} — 이미 존재")
                ok.append(key)
                progress[key] = "success"
                continue

            af.log(f"=== ({i}/{total}) 에셋 생성: {key} ===")
            success = False
            for attempt in range(1, 4):
                try:
                    known = list_srcs(page)
                    af.fill_prompt(page, prompt)
                    af.shot(page, "_live")
                    if not af.generate(page):
                        af.log(f"  [WARN] 생성 버튼 클릭 실패 (시도 {attempt}/3)")
                        page.wait_for_timeout(1500)
                        # 모드가 풀렸을 수 있어 재설정
                        af.set_image_mode(page)
                        continue
                    
                    af.shot(page, "_live")
                    af.log("  [WAIT] 이미지 생성을 위해 45초 동안 대기합니다...")
                    page.wait_for_timeout(45000)
                    af.shot(page, "_live")
                    
                    # 45초 후 타일이 없거나 실패하면 캡처 실패로 간주하고 즉시 복구 돌입
                    if capture_new_asset(page, known, out_path, timeout_s=15):
                        success = True
                        break
                    
                    af.log(f"  [WARN] 45초 대기 후 에셋 타일 검출 실패 (시도 {attempt}/3)")
                    af.shot(page, f"asset_{key}_fail_try{attempt}")
                    
                    # 실패한 카드 타일 삭제 시도 (delete_forever 또는 af.delete_tile_by_index)
                    try:
                        deleted = False
                        del_btn = page.locator("button:has-text('삭제'), button:has-text('delete_forever')").first
                        if del_btn.is_visible(timeout=2000):
                            del_btn.click()
                            af.log("  [CLI-AUTO] 실패한 미완성 카드 타일을 삭제(delete_forever)했습니다.")
                            deleted = True
                        if not deleted:
                            af.log("  [CLI-AUTO] af.delete_tile_by_index를 사용하여 가장 최근 타일을 삭제합니다.")
                            af.delete_tile_by_index(page, 0)
                    except Exception as del_e:
                        af.log(f"  [CLI-AUTO] 카드 삭제 예외: {del_e}")
                    
                    # 즉시 브라우저를 닫고 재기동하여 새로고침/재진입 처리
                    af.log("  [REBOOT] 생성 실패로 브라우저를 재부팅하고 프로젝트로 재진입합니다...")
                    try:
                        ctx.close()
                    except Exception:
                        pass
                    reboot_interactive_chrome()
                    ctx, page = launch()
                    if not af.open_new_project(page):
                        af.log("  [REBOOT-ERR] 프로젝트 재진입 실패")
                        break
                    af.set_image_mode(page)
                    
                except Exception as e:
                    af.log(f"  [ERR] {key} 시도 {attempt} 예외: {str(e)[:120]}")
                    try:
                        af.shot(page, f"asset_{key}_exc_try{attempt}")
                    except Exception:
                        pass
                    page.wait_for_timeout(2000)

            if success:
                af.log(f"[ASSET-OK] {key} ({i}/{total}) -> {out_path} ({os.path.getsize(out_path)} bytes)")
                ok.append(key)
                progress[key] = "success"
            else:
                af.log(f"[ASSET-FAIL] {key} ({i}/{total})")
                fail.append(key)
                progress[key] = "fail"

            try:
                json.dump(progress, open(progress_file, "w", encoding="utf-8"),
                          ensure_ascii=False, indent=2)
            except Exception:
                pass

        af.log(f"완료 — 성공 {len(ok)}/{total}, 실패 {len(fail)}: {fail}")
        try:
            ctx.close()
        except Exception:
            pass

    return 0 if not fail else 3


if __name__ == "__main__":
    sys.exit(main())
