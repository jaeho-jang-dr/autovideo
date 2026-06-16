"""
autoveo_flow.py — AutoVeo engine: scenario -> (Google Flow) image -> animate ->
video clip -> download, 100% browser GUI (Playwright over the logged-in Chrome
profile). NO API keys, NO browser extension. Account login only.

Verified recipe for the Flow "Omni" editor (labs.google/fx/tools/flow, ko-KR, 2026):
  composer prompt : div[role='textbox'][contenteditable='true']
  agent pill      : "에이전트" — a TOGGLE. If the standard model chip is hidden,
                    the composer is in Agent mode; click it once to return to the
                    standard box that shows the model chip.
  model chip menu : tabs 이미지/동영상 · aspect(16:9..) · count(1x..) · model dropdown.
                    Image model = "Nano Banana 2" (0 credits). Video = Veo/Omni.
  generate button : button:has-text('arrow_forward')  (bottom composer)
  image -> video  : hover the generated image tile -> its ⋮ "더 생성하기" menu ->
                    "애니메이션 적용"  (image becomes the FIRST FRAME, mode -> 동영상 8s)
  download        : hover the result tile -> ⋮ -> "다운로드" -> "720p 원본 크기"
  done signal     : a finished Veo clip downloads as a real MP4; while still
                    rendering the same button yields the first-frame JPEG. So we
                    DOWNLOAD-AND-VERIFY the file header (ftyp=mp4) in a retry loop —
                    the only fully reliable completion signal.

Per scene we use a FRESH project so the newest (left-most) tile is the video.

Prompt file format, one scene per line:
  [Scene 1] <image prompt> :: <motion prompt>
If ':: ' is omitted the same text drives both the image and the motion.

Usage:
  python autoveo_flow.py --prompts test_scene.txt
  python autoveo_flow.py --prompts test_scene.txt --scene 1
  python autoveo_flow.py --prompts test_scene.txt --force
"""
import os
import re
import sys
import time
import shutil
import argparse
import traceback
from playwright.sync_api import sync_playwright

class BrowserRebootException(Exception):
    pass


for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE = "https://labs.google/fx/tools/flow"
PROFILE = os.path.abspath("assets/chrome_profile")
DBG = "debug"
DL_DIR = os.path.abspath(os.path.join(DBG, "downloads"))
OUT_DIR = ""
PROMPT_SELECTOR = "div[role='textbox'][contenteditable='true']"

# Largest generated image tile (the source frame).
BIG_MEDIA_IMG_JS = r"""
() => {
  let best=null, area=0;
  for (const im of document.querySelectorAll('img')) {
    const s = im.getAttribute('src') || '';
    // 프로필 이미지나 로딩/플레이스홀더 이미지는 제외
    if (!/media\.getMediaUrlRedirect|googleusercontent/.test(s)) continue;
    
    const r = im.getBoundingClientRect();
    if (r.width<200 || r.height<120) continue;
    if (r.width>1200 || r.height>900) continue;
    
    // 부모 div에 스피너가 들어있는 렌더링 중 상태 제외
    const parent = im.closest('div');
    if (parent && (parent.querySelector('svg') || parent.querySelector('[class*="spinner"]') || parent.querySelector('[class*="loading"]'))) {
      continue;
    }
    
    const a=r.width*r.height;
    if (a>area){area=a; best={x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2)};}
  }
  return best;
}
"""

# All result posters in the canvas (newest results sit left-most -> smallest x).
POSTERS_JS = r"""
() => {
  const out=[];
  for (const im of document.querySelectorAll('img')) {
    const s = im.getAttribute('src') || '';
    if (!/media\.getMediaUrlRedirect|googleusercontent/.test(s)) continue;
    
    const r = im.getBoundingClientRect();
    if (r.width<200 || r.height<120) continue;
    if (r.width>1200 || r.height>900) continue;
    
    const parent = im.closest('div');
    if (parent && (parent.querySelector('svg') || parent.querySelector('[class*="spinner"]') || parent.querySelector('[class*="loading"]'))) {
      continue;
    }
    
    out.push({x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2), left:Math.round(r.x)});
  }
  out.sort((a,b)=>a.left-b.left);
  return out;
}
"""



# Finished VIDEO tile: a play_circle overlay AND a real poster img (the only
# reliable way to target the *video* — not the still image — for download).
VIDEO_DONE_JS = r"""
() => {
  let best=null, area=Infinity;
  for (const el of document.querySelectorAll('div,button,a,li')) {
    const t = el.textContent||'';
    if (!t.includes('play_circle')) continue;
    let poster=false;
    for (const im of el.querySelectorAll('img')) {
      const s=im.getAttribute('src')||'';
      const r=im.getBoundingClientRect();
      if (/media\.getMediaUrlRedirect|googleusercontent/.test(s) && r.width>200){poster=true;break;}
    }
    if (!poster) continue;
    const r = el.getBoundingClientRect();
    if (r.width<250 || r.height<150) continue;
    const a=r.width*r.height;
    if (a<area){area=a; best={x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2)};}
  }
  return best;
}
"""

# Is the composer showing the standard model chip (i.e. NOT in Agent mode)?
HAS_CHIP_JS = r"""
() => {
  for (const b of document.querySelectorAll('button')) {
    const t=b.textContent||''; const r=b.getBoundingClientRect();
    if (r.y>540 && (t.includes('Nano Banana')||t.includes('crop_16_9')||
        t.includes('동영상 ·')||t.includes('이미지 ·'))) return true;
  }
  return false;
}
"""

# Tile ⋮ ("더 생성하기"/more_vert) nearest a target point (below the top bar).
MORE_NEAR_JS = r"""
(t) => {
  let best=null, bd=1e9;
  for (const b of document.querySelectorAll('button')) {
    const tx=(b.textContent||'').trim();
    const aria=(b.getAttribute('aria-label')||'').trim();
    const isMore = tx.includes('더 생성하기') || tx.includes('more_vert') || 
                   tx.includes('더보기') || aria.includes('더보기') || 
                   aria.includes('More') || aria.includes('옵션') || aria.includes('more');
    if (!isMore) continue;
    const r=b.getBoundingClientRect();
    if (r.y<60 || r.width<=0) continue;
    const cx=r.x+r.width/2, cy=r.y+r.height/2, d=Math.hypot(cx-t.x, cy-t.y);
    if (d<bd){bd=d; best={x:Math.round(cx), y:Math.round(cy)};}
  }
  return best;
}
"""



def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def shot(page, name):
    try:
        page.screenshot(path=os.path.abspath(os.path.join(DBG, f"{name}.png")))
    except Exception:
        pass


def is_mp4(path):
    try:
        with open(path, "rb") as f:
            head = f.read(16)
        return b"ftyp" in head            # MP4 box; a JPEG poster starts with FFD8
    except Exception:
        return False


def parse_prompts(path):
    scenes, pat = {}, re.compile(r"\[Scene\s+(\d+)\]\s+(.*)", re.IGNORECASE)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.strip())
            if not m:
                continue
            n, body = int(m.group(1)), m.group(2).strip()
            if "::" in body:
                img, mot = body.split("::", 1)
                scenes[n] = (img.strip(), mot.strip())
            else:
                scenes[n] = (body, body)
    return scenes


def dismiss(page):
    # Changelog iframe 등 화면을 가리는 오버레이 강제 제거 (Javascript)
    try:
        page.evaluate("""() => {
            const iframes = document.querySelectorAll('iframe');
            for (const f of iframes) {
                if (f.src.includes('changelog') || f.src.includes('changelogs')) {
                    // 가장 인접한 모달 컨테이너 또는 iframe 본체를 삭제
                    const parentModal = f.closest('div[role="dialog"]') || f.closest('div');
                    if (parentModal) {
                        parentModal.remove();
                    } else {
                        f.remove();
                    }
                }
            }
            // 뒷배경 블러 처리나 백드롭 레이어도 제거 시도
            const backdrops = document.querySelectorAll('div[class*="backdrop"], div[class*="Backdrop"]');
            for (const b of backdrops) {
                b.remove();
            }
        }""")
    except Exception:
        pass

    # Escape 키를 눌러 모달창을 닫는 보편적 예외 처리
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
    except Exception:
        pass

    for sel in ["button:has-text('Agree')", "button:has-text('동의')",
                "button:has-text('No thanks')", "button:has-text('확인')"]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=400):
                loc.click(timeout=2000, force=True)
                page.wait_for_timeout(500)
        except Exception:
            pass


def click_text(page, t, ymin=None, timeout=4000):
    for sel in (f"button:has-text('{t}')", f"[role='button']:has-text('{t}')",
                f"[aria-label*='{t}']", f"text={t}"):
        try:
            locs = page.locator(sel)
            for i in range(locs.count()):
                loc = locs.nth(i)
                if loc.is_visible():
                    box = loc.bounding_box()
                    if ymin is not None and (not box or box["y"] < ymin):
                        continue
                    loc.click(timeout=timeout)
                    return True
        except Exception:
            pass
    return False


def open_new_project(page):
    # 브라우저 기동 직후 첫 내비게이션이 net::ERR_CONNECTION_RESET 등으로 일시 실패하는
    # 경우가 있어, 일시적 네트워크 오류에 한해 짧은 백오프로 재시도한다(씬 영구 누락 방지).
    last_err = None
    for attempt in range(4):
        try:
            page.goto(BASE, wait_until="domcontentloaded", timeout=60000)
            last_err = None
            break
        except Exception as e:
            last_err = e
            log(f"  [NAV] goto 실패(시도 {attempt+1}/4): {str(e)[:80]} — 4초 후 재시도")
            page.wait_for_timeout(4000)
    if last_err is not None:
        raise last_err
    page.wait_for_timeout(3500)
    if "accounts.google.com" in page.url:
        log("로그인 필요 — labs.google 복귀 대기(90s)")
        # 구글 로그인 계정 선택 자동화 시도 (CLI 자동 명령)
        try:
            for sel in [
                "div[data-email='drjang00@gmail.com']",
                "text=drjang00@gmail.com",
                "div:has-text('drjang00@gmail.com')",
                "li:has-text('drjang00@gmail.com')",
                "[aria-label*='drjang00@gmail.com']"
            ]:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=1000):
                    log(f"  [CLI-AUTO] 구글 계정 선택 검출: {sel} 클릭 시도")
                    loc.click(timeout=3000)
                    page.wait_for_timeout(2000)
                    break
        except Exception as e:
            log(f"  [CLI-AUTO] 구글 계정 선택 에러: {e}")
            
        # 비밀번호 입력 후 '다음' 버튼 자동 클릭 시도
        try:
            for next_sel in [
                "button:has-text('다음')",
                "button:has-text('Next')",
                "#passwordNext",
                "#identifierNext"
            ]:
                loc = page.locator(next_sel).first
                if loc.is_visible(timeout=1000):
                    log(f"  [CLI-AUTO] 구글 로그인 '다음' 버튼 검출: {next_sel} 클릭 시도")
                    loc.click(timeout=3000)
                    page.wait_for_timeout(2000)
                    break
        except Exception as e:
            log(f"  [CLI-AUTO] '다음' 버튼 클릭 에러: {e}")
            
        try:
            page.wait_for_url("**/labs.google/**", timeout=90000)
        except Exception:
            pass
    dismiss(page)
    # 라이트박스나 모달이 열려 있어 컴포저 진입을 막는 것을 방지하기 위해 Escape 키를 보냅니다.
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)
    except Exception:
        pass
    dismiss(page)
    if "/project/" not in page.url:
        click_text(page, "새 프로젝트") or click_text(page, "New project")
        page.wait_for_timeout(4000)
        dismiss(page)
    for _ in range(40):
        try:
            if page.locator(PROMPT_SELECTOR).first.is_visible(timeout=500):
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def set_image_mode(page, aspect="16:9", count="1x"):
    """Exit Agent mode if needed, then select 이미지 / aspect / count."""
    if not page.evaluate(HAS_CHIP_JS):
        click_text(page, "에이전트", ymin=540)      # toggle Agent OFF
        page.wait_for_timeout(900)
    # open the model chip menu (chip label may be 동영상.. or Nano Banana..)
    for t in ("Nano Banana", "crop_16_9", "동영상", "이미지"):
        if click_text(page, t, ymin=540):
            break
    page.wait_for_timeout(1200)
    click_text(page, "이미지")
    page.wait_for_timeout(250)
    click_text(page, aspect)
    page.wait_for_timeout(250)
    click_text(page, count)
    page.wait_for_timeout(250)
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)


def fill_prompt(page, text):
    b = page.locator(PROMPT_SELECTOR).first
    b.click()
    page.wait_for_timeout(150)
    try:
        b.press("Control+A")
        b.press("Delete")
    except Exception:
        pass
    page.keyboard.type(text, delay=4)
    page.wait_for_timeout(300)


def generate(page):
    return click_text(page, "arrow_forward", ymin=540)


def wait_image(page, n, timeout_s=40):
    """최대 40초 동안 이미지가 생성되기를 기다립니다. 5초 주기로 스캔합니다.
    만약 40초 동안 생성되지 않으면, 실패로 처리하고 사용자의 프로토콜을 수행합니다:
    1. 스크린샷 캡처
    2. 재시작(Retry) 버튼 감지하여 클릭
    3. 스크린샷 캡처
    4. 오른쪽/최신 타일 삭제 버튼 위치 확인하여 삭제
    5. False 반환 (상위 호출처에서 재시도)"""
    
    log(f"이미지 생성 대기 중... (최대 {timeout_s}초)")
    deadline = time.time() + timeout_s
    success = False
    
    # 5초 간격으로 확인하며 40초 한도 대기
    while time.time() < deadline:
        if page.evaluate(BIG_MEDIA_IMG_JS):
            page.wait_for_timeout(1500)
            success = True
            break
        page.wait_for_timeout(5000)
        
    if success:
        return True
        
    # 이미지 생성 실패 상황
    log(f"  [FAIL] {timeout_s}초 내 이미지 생성 실패. 에러 복구 프로토콜 기동.")
    
    # 1) 스샷 저장
    shot(page, f"s{n}_img_fail_before_retry")
    
    # 2) 재시작 버튼 찾기 및 클릭
    retry_btn = None
    for selector in ["button:has-text('다시 실행')", "button:has-text('재실행')", "button:has-text('Retry')", "button:has-text('다시 시도')", "button[aria-label*='재실행']", "button[aria-label*='Retry']"]:
        try:
            loc = page.locator(selector).first
            if loc.is_visible(timeout=500):
                retry_btn = loc
                break
        except Exception:
            pass
            
    if retry_btn:
        log("  [WARN] 이미지 생성 재시작 버튼을 발견하여 클릭합니다.")
        try:
            retry_btn.click()
            page.wait_for_timeout(1500)
        except Exception as e:
            log(f"  재시작 버튼 클릭 실패: {e}")
            
    # 3) 다시 스샷 저장
    shot(page, f"s{n}_img_fail_after_retry")
    
    # 4) 오른쪽 타일(혹은 최신 타일) 삭제 버튼 위치 확인 후 삭제
    # posters 목록의 갯수에 따라 판단: 2개 이상일 땐 1번째(오른쪽), 1개일 땐 0번째(가장최근)를 삭제
    posters = page.evaluate(POSTERS_JS)
    idx_to_delete = 1 if (posters and len(posters) >= 2) else 0
    delete_tile_by_index(page, idx_to_delete)
    
    return False


def open_tile_menu(page, center):
    page.mouse.move(center["x"], center["y"])
    page.wait_for_timeout(1000)
    more = page.evaluate(MORE_NEAR_JS, center)
    if not more:
        page.mouse.move(center["x"], center["y"] - 20)
        page.wait_for_timeout(800)
        more = page.evaluate(MORE_NEAR_JS, center)
    if not more:
        return False
    page.mouse.click(more["x"], more["y"])
    page.wait_for_timeout(900)
    return True


def animate_image(page):
    """Hover the generated image -> ⋮ -> '애니메이션 적용' (image becomes 1st frame)."""
    center = page.evaluate(BIG_MEDIA_IMG_JS)
    if not center or not open_tile_menu(page, center):
        return False
    return click_text(page, "애니메이션 적용") or click_text(page, "애니메이션") or click_text(page, "Animate")



def try_download_video(page, tmp_path, n):
    """Download the FINISHED video tile (play_circle overlay + real poster) as the
    원본 MP4. We click the video to open the lightbox, click the top-right download button,
    and then select the original resolution. Then we close the lightbox by pressing Escape."""
    target = page.evaluate(VIDEO_DONE_JS)
    if not target:
        return False                          # no finished-video tile yet
    try:
        # 1. Click the video tile to open the lightbox.
        # Check if click succeeds by verifying if the lightbox's download button appears.
        # If not, we screenshot, log, and retry clicking.
        log(f"  비디오 타일 클릭 시도 ({target['x']}, {target['y']})")
        page.mouse.click(target["x"], target["y"])
        page.wait_for_timeout(1500)
        
        # Check if download button (lightbox) is visible. If not, retry click.
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
            log(f"  [WARN] 라이트박스가 열리지 않음. 스크린샷 저장 및 재클릭 시도.")
            shot(page, f"s{n}_click_failed_retry")
            page.mouse.move(target["x"], target["y"])
            page.wait_for_timeout(300)
            page.mouse.click(target["x"], target["y"])
            page.wait_for_timeout(1500)
        
        # 2. Wait for download and click top-right download icon/button
        download_clicked = False
        with page.expect_download(timeout=60000) as dl:
            for selector in download_btn_selectors:
                try:
                    loc = page.locator(selector).first
                    if loc.is_visible(timeout=800):
                        loc.click()
                        download_clicked = True
                        break
                except Exception:
                    pass
            
            if not download_clicked:
                raise RuntimeError("Lightbox download button not found")
                
            page.wait_for_timeout(1000)
            # 3. Select resolution
            (click_text(page, "원본 크기") or click_text(page, "720p")
             or click_text(page, "원본"))
             
        d = dl.value
        d.save_as(tmp_path)
        
        # 4. Close lightbox
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)
    except Exception as e:
        log(f"  download try 실패: {str(e)[:90]}")
        # Make sure to close the lightbox on failure
        try:
            page.keyboard.press("Escape")
            page.wait_for_timeout(800)
        except Exception:
            pass
        return False
        
    if is_mp4(tmp_path):
        return True
    try:
        os.remove(tmp_path)                   # JPEG poster -> still rendering
    except Exception:
        pass
    return False


def delete_tile_by_index(page, idx):
    """지정된 인덱스(0: 왼쪽/최신, 1: 오른쪽 등)의 타일을 삭제합니다."""
    log(f"  [CLEAN] {idx}번째 타일 삭제 시도...")
    try:
        posters = page.evaluate(POSTERS_JS)
        if not posters or len(posters) <= idx:
            log(f"  [CLEAN] 삭제할 {idx}번째 타일이 없습니다. (현재 타일 수: {len(posters) if posters else 0})")
            return False
            
        target = posters[idx]
        # 1. ⋮ 더보기 메뉴 열기
        if not open_tile_menu(page, target):
            log("  [CLEAN] 타일 메뉴(⋮) 열기 실패")
            return False
            
        page.wait_for_timeout(500)
        # 2. '삭제' 또는 '제거' 클릭 (오클릭 방지를 위해 팝업 메뉴 영역으로 제한)
        menu_loc = page.locator("[role='menu'], .v-menu__content, .v-overlay-container, [role='menuitem']")
        deleted = False
        for text in ("삭제", "Delete", "제거", "Remove"):
            try:
                # 팝업 내에서 먼저 텍스트 요소를 찾음
                item = menu_loc.locator(f"text={text}").first
                if item.is_visible(timeout=500):
                    item.click(timeout=1000)
                    deleted = True
                    break
            except Exception:
                pass
                
        if not deleted:
            deleted = (click_text(page, "삭제") or click_text(page, "Delete") or 
                       click_text(page, "제거") or click_text(page, "Remove"))
                       
        if not deleted:
            log("  [CLEAN] 삭제 메뉴 클릭 실패")
            page.keyboard.press("Escape")
            return False
            
        page.wait_for_timeout(800)
        # 3. 팝업 확인창의 삭제/확인 클릭 (대화상자 다이얼로그 영역으로 제한)
        dialog_loc = page.locator("[role='dialog'], .v-dialog, .v-overlay-container")
        confirmed = False
        for text in ("확인", "삭제", "Delete", "Confirm"):
            try:
                item = dialog_loc.locator(f"text={text}").first
                if item.is_visible(timeout=500):
                    item.click(timeout=1000)
                    confirmed = True
                    break
            except Exception:
                pass
                
        if not confirmed:
            confirmed = (click_text(page, "확인") or click_text(page, "삭제") or 
                         click_text(page, "Delete") or click_text(page, "Confirm"))
                         
        page.wait_for_timeout(1500)
        log(f"  [CLEAN] {idx}번째 타일 삭제 완료 ✔")
        return True
    except Exception as e:
        log(f"  [CLEAN] 타일 삭제 중 오류 발생: {e}")
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        return False


def make_video(page, out_path, motion_prompt, n, budget_s=80):
    """동영상 프롬프트를 제출하고 80초 동안 아무 다운로드도 시도하지 않고 대기합니다.
    80초 후, 가장 왼쪽 타일을 클릭해 라이트박스를 띄운 다음 우상단 다운로드 버튼을 클릭해 원본 크기로 저장합니다.
    실패하면 스샷을 남기고 실패 타일을 지운 뒤 다시 시도합니다."""
    
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        fill_prompt(page, motion_prompt)
        log(f"비디오 생성 명령 실행 (시도 {retry_count + 1}/{max_retries})")
        if not generate(page):
            log("[ERR] 동영상 생성 버튼 클릭 실패")
            return False
            
        # 1. 80초 동안 무조건 완성 대기 (디스크 낭비 방지)
        log("동영상 생성 중... (80초 완성 대기)")
        page.wait_for_timeout(80000)
        
        # 2. 가장 왼쪽 타일(비디오) 클릭하여 라이트박스 띄우기
        posters = page.evaluate(POSTERS_JS)
        if not posters or len(posters) < 1:
            log("  [WARN] 캔버스에 타일이 존재하지 않습니다. 실패 처리.")
            delete_tile_by_index(page, 0)
            retry_count += 1
            continue
            
        target = posters[0]
        log(f"  가장 왼쪽 비디오 타일 클릭 시도 ({target['x']}, {target['y']})")
        page.mouse.click(target["x"], target["y"])
        page.wait_for_timeout(2000)
        
        # 3. 라이트박스가 정상적으로 열렸는지 (우상단 다운로드 버튼 유무로) 검증
        download_btn_selectors = ["button:has-text('download')", "button[aria-label*='다운로드']", "button[aria-label*='Download']", "button:has-text('다운로드')"]
        lightbox_open = False
        for selector in download_btn_selectors:
            try:
                if page.locator(selector).first.is_visible(timeout=500):
                    lightbox_open = True
                    break
            except Exception:
                pass
                
        # 클릭이 빗나갔거나 라이트박스가 안 열렸다면 1회 재클릭 시도
        if not lightbox_open:
            log("  [WARN] 라이트박스가 열리지 않음. 스크린샷 후 마우스 이동 재클릭 시도.")
            shot(page, f"s{n}_lightbox_retry")
            page.mouse.move(target["x"], target["y"])
            page.wait_for_timeout(300)
            page.mouse.click(target["x"], target["y"])
            page.wait_for_timeout(2000)
            
            # 재확인
            for selector in download_btn_selectors:
                try:
                    if page.locator(selector).first.is_visible(timeout=500):
                        lightbox_open = True
                        break
                except Exception:
                    pass
                    
        # 4. 다운로드 수행
        success = False
        if lightbox_open:
            tmp = os.path.join(DL_DIR, f"_scene_{n}.bin")
            try:
                download_clicked = False
                with page.expect_download(timeout=60000) as dl:
                    for selector in download_btn_selectors:
                        try:
                            loc = page.locator(selector).first
                            if loc.is_visible(timeout=800):
                                loc.click()
                                download_clicked = True
                                break
                        except Exception:
                            pass
                    
                    if not download_clicked:
                        raise RuntimeError("다운로드 버튼 클릭 실패")
                        
                    page.wait_for_timeout(1000)
                    (click_text(page, "원본 크기") or click_text(page, "720p") or click_text(page, "원본"))
                    
                d = dl.value
                d.save_as(tmp)
                
                # 라이트박스 닫기
                page.keyboard.press("Escape")
                page.wait_for_timeout(1000)
                
                if is_mp4(tmp):
                    shutil.move(tmp, out_path)
                    success = True
                    log(f"  [OK] 다운로드 성공: {out_path}")
                else:
                    log("  [WARN] 다운로드한 파일이 MP4가 아닙니다 (렌더링 미완료 정적 이미지).")
                    try:
                        os.remove(tmp)
                    except Exception:
                        pass
            except Exception as e:
                log(f"  [ERR] 라이트박스 내 다운로드 실패: {e}")
                try:
                    page.keyboard.press("Escape")
                except Exception:
                    pass
        else:
            log("  [FAIL] 라이트박스를 띄우지 못했습니다. (80초 경과 또는 클릭 오류)")
            
        if success:
            return True
            
        # 실패 복구 흐름 (타일 지우고 재작동)
        log("  [RETRY] 영상 생성 실패 또는 80초 타임아웃. 캔버스의 실패 타일을 삭제합니다.")
        shot(page, f"s{n}_vid_fail_retry")
        
        # 에러 재시작 버튼이 있으면 클릭해봄
        retry_btn = None
        for selector in ["button:has-text('다시 실행')", "button:has-text('재실행')", "button:has-text('Retry')", "button:has-text('다시 시도')", "button[aria-label*='재실행']", "button[aria-label*='Retry']"]:
            try:
                loc = page.locator(selector).first
                if loc.is_visible(timeout=500):
                    retry_btn = loc
                    break
            except Exception:
                pass
        if retry_btn:
            try:
                retry_btn.click()
                page.wait_for_timeout(1000)
            except Exception:
                pass
                
        # 왼쪽 타일 삭제
        delete_tile_by_index(page, 0)
        
        retry_count += 1
        if retry_count >= max_retries:
            log("  [ERR] 3회 연속 비디오 생성 실패. 브라우저 재기동(Reboot)을 위해 예외를 발생시킵니다.")
            raise BrowserRebootException("3 consecutive video generation failures")
            
        page.wait_for_timeout(2000)
        
    return False


def make_scene(page, n, image_prompt, motion_prompt, force=False):
    global OUT_DIR
    out_path = os.path.join(OUT_DIR, f"scene_{n}.mp4")
    if (not force) and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        log(f"[SKIP] 존재함: {out_path}")
        return True
        
    img_retry = 0
    max_img_retry = 3
    img_success = False
    
    while img_retry < max_img_retry:
        log(f"=== Scene {n} (이미지 생성 시도 {img_retry+1}/{max_img_retry}) ===")
        if not open_new_project(page):
            log("[ERR] 프로젝트/컴포저 진입 실패")
            shot(page, f"s{n}_entry_fail")
            img_retry += 1
            if img_retry >= max_img_retry:
                log("  [ERR] 프로젝트 진입 3회 연속 실패. 브라우저 재기동(Reboot)을 요청합니다.")
                raise BrowserRebootException("3 consecutive project entry failures")
            page.wait_for_timeout(3000)
            continue
        shot(page, f"s{n}_00_editor")

        set_image_mode(page)
        fill_prompt(page, image_prompt)
        if not generate(page):
            log("[ERR] 이미지 생성 버튼 클릭 실패")
            return False
            
        if wait_image(page, n):
            img_success = True
            break
            
        img_retry += 1
        if img_retry >= max_img_retry:
            log("  [ERR] 이미지 생성 3회 연속 실패. 브라우저 재기동(Reboot)을 요청합니다.")
            raise BrowserRebootException("3 consecutive image generation failures")
            
    if not img_success:
        return False
        
    shot(page, f"s{n}_01_image")

    # [CLI-AUTO] 정적 이미지 fallback을 위해 이미지 요소를 캡처하여 격리 폴더에 저장
    try:
        img_element = page.evaluate_handle(r"""
            () => {
                let best=null, area=0;
                for (const im of document.querySelectorAll('img')) {
                    const r = im.getBoundingClientRect();
                    if (r.width<200 || r.height<120) continue;
                    if (r.width>1200 || r.height>900) continue;
                    const a=r.width*r.height;
                    if (a>area){area=a; best=im;}
                }
                return best;
            }
        """)
        if img_element.as_element():
            img_path = os.path.join(OUT_DIR, f"scene_{n}.png")
            img_element.as_element().screenshot(path=img_path)
            log(f"  [CLI-AUTO] 정적 이미지 fallback 캡처 저장 성공: {img_path}")
    except Exception as img_err:
        log(f"  [CLI-AUTO] 정적 이미지 캡처 실패: {img_err}")

    if not animate_image(page):
        log("[ERR] '애니메이션 적용' 실패")
        shot(page, f"s{n}_animate_fail")
        return False
    page.wait_for_timeout(1200)
    shot(page, f"s{n}_02_animate")

    if make_video(page, out_path, motion_prompt, n):
        log(f"[OK] Scene {n} → {out_path}")
        shot(page, f"s{n}_03_done")
        return True
    log(f"[FAIL] Scene {n} 영상 생성/다운로드 실패")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", default="prompts_for_veo.txt")
    ap.add_argument("--scene", type=int)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    scenes = parse_prompts(args.prompts)
    if not scenes:
        log("프롬프트 없음")
        return
        
    # Set output directory to project root, named after the prompts file (e.g. chiropractic_science)
    prompts_base = os.path.splitext(os.path.basename(args.prompts))[0]
    # Remove '_prompts' suffix if present
    if prompts_base.endswith("_prompts"):
        prompts_base = prompts_base[:-8]
    global OUT_DIR
    OUT_DIR = os.path.abspath(prompts_base)
    
    os.makedirs(DBG, exist_ok=True)
    os.makedirs(DL_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    progress_file = os.path.join(OUT_DIR, "progress_scenes.json")
    progress = {}
    if os.path.exists(progress_file):
        import json
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                progress = json.load(f)
            log(f"로드된 진행도 기록: {len(progress)}개 씬 상태 정보 획득")
        except Exception as e:
            log(f"진행도 파일 로드 오류: {e}")

    todo = [args.scene] if args.scene else sorted(scenes)

    ok, fail = [], []
    with sync_playwright() as p:
        def launch_browser():
            c = p.chromium.launch_persistent_context(
                PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
                accept_downloads=True, downloads_path=DL_DIR,
                ignore_default_args=["--enable-automation"],
                args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                      "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
            pg = c.pages[0] if c.pages else c.new_page()
            return c, pg

        ctx, page = launch_browser()
        idx = 0
        while idx < len(todo):
            n = todo[idx]
            if n not in scenes:
                idx += 1
                continue
            
            # 증분 생성 조건 체크: 이미 성공했고 파일도 있으면 생성 건너뜀
            out_path = os.path.join(OUT_DIR, f"scene_{n}.mp4")
            if not args.force and progress.get(str(n)) == "success" and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                log(f"[SKIP-PROGRESS] 이미 성공한 씬: {out_path}")
                ok.append(n)
                idx += 1
                continue

            try:
                success = make_scene(page, n, *scenes[n], force=args.force)
                
                # 성공 및 실패 여부를 진행도 파일에 기록
                import json
                progress[str(n)] = "success" if success else "fail"
                try:
                    with open(progress_file, "w", encoding="utf-8") as f:
                        json.dump(progress, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    log(f"진행도 기록 저장 실패: {e}")

                if success:
                    ok.append(n)
                else:
                    fail.append(n)
                idx += 1
            except BrowserRebootException as re_err:
                log(f"[REBOOT] 브라우저 재기동 요구 발생: {re_err}. 5초 대기 후 세션을 재시작합니다.")
                try:
                    ctx.close()
                except Exception:
                    pass
                time.sleep(5)
                ctx, page = launch_browser()
            except Exception as e:
                log(f"[ERR] Scene {n} 일반 에러: {e}")
                traceback.print_exc()
                shot(page, f"s{n}_error")
                fail.append(n)
                idx += 1
        log(f"완료 — 성공 {ok} / 실패 {fail}")
        try:
            ctx.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
