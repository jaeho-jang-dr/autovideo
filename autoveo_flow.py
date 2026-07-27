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
import subprocess
import traceback
from playwright.sync_api import sync_playwright

class BrowserRebootException(Exception):
    pass


def force_kill_profile_chrome(profile_path=None):
    """지정된 크롬 프로필 폴더를 쓰는 크롬만 강제 종료하고 락 파일을 제거한다.
    사용자의 일반 크롬 세션은 CommandLine 필터로 보존한다."""
    if not profile_path:
        profile_path = PROFILE
    profile_name = os.path.basename(profile_path)
    try:
        ps = (
            f"Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | "
            f"Where-Object {{ $_.CommandLine -like '*assets\\\\{profile_name}*' }} | "
            f"ForEach-Object {{ try {{ Stop-Process -Id $_.ProcessId -Force "
            f"-ErrorAction SilentlyContinue }} catch {{}} }}"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], timeout=30)
    except Exception as e:
        try:
            log(f"  [REBOOT] chrome 강제종료 중 경고: {e}")
        except Exception:
            pass
    for lock in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        try:
            p = os.path.join(profile_path, lock)
            if os.path.exists(p) or os.path.islink(p):
                os.remove(p)
        except Exception:
            pass


for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE = "https://labs.google/fx/tools/flow"
PROFILE = os.path.abspath("assets/chrome_profile") # Default fallback
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
    if (r.width<120 || r.height<120) continue;
    if (r.width>1200 || r.height>1600) continue;
    
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
      if (/media\.getMediaUrlRedirect|googleusercontent/.test(s) && r.width>120){poster=true;break;}
    }
    if (!poster) continue;
    const r = el.getBoundingClientRect();
    if (r.width<150 || r.height<150) continue;
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
        # Toggle DevTools F12 to capture console logs for diagnostics
        try:
            page.keyboard.press("F12")
            page.wait_for_timeout(2500)
        except Exception:
            pass
        page.screenshot(path=os.path.abspath(os.path.join(DBG, f"{name}.png")))
        # Toggle DevTools off to avoid interference
        try:
            page.keyboard.press("F12")
            page.wait_for_timeout(500)
        except Exception:
            pass
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
    scenes = {}
    curr_scene = None
    curr_img = None
    curr_mot = None
    
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue
            
        # Check for [Scene X] pattern
        scene_match = re.match(r"\[Scene\s+(\d+)\](.*)", line_str, re.IGNORECASE)
        if scene_match:
            # Save previous scene if exists
            if curr_scene is not None:
                img_val = curr_img if curr_img else ""
                mot_val = curr_mot if curr_mot else img_val
                scenes[curr_scene] = (img_val, mot_val)
            
            curr_scene = int(scene_match.group(1))
            rest = scene_match.group(2).strip()
            curr_img = None
            curr_mot = None
            
            # Check if it is a single-line format: [Scene X] image :: motion
            if rest:
                if "::" in rest:
                    img_val, mot_val = rest.split("::", 1)
                    curr_img = img_val.strip()
                    curr_mot = mot_val.strip()
                else:
                    curr_img = rest
                    curr_mot = rest
        else:
            # We are inside a scene block
            if curr_scene is not None:
                if line_str.lower().startswith("image:"):
                    curr_img = line_str[6:].strip()
                elif line_str.lower().startswith("motion:"):
                    mot_part = line_str[7:].strip()
                    # If motion starts with ::, strip it
                    if mot_part.startswith("::"):
                        mot_part = mot_part[2:].strip()
                    curr_mot = mot_part
                    
    # Save the last scene
    if curr_scene is not None:
        img_val = curr_img if curr_img else ""
        mot_val = curr_mot if curr_mot else img_val
        scenes[curr_scene] = (img_val, mot_val)
        
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
            
            // "이동 중에도" 또는 "새 항목에서 열기" 모바일 홍보 팝업 및 다이얼로그 강제 제거 (바디 하위 포털 정리) - React 크래시 방지를 위해 삭제 대신 숨김 처리
            try {
                const bodyChildren = Array.from(document.body.children);
                for (const child of bodyChildren) {
                    if (child.id === '__next' || child.id === 'root' || child.tagName === 'SCRIPT' || child.tagName === 'STYLE') {
                        continue;
                    }
                    const text = child.innerText || '';
                    if (text.includes('이동 중에도') || text.includes('새 항목에서') || text.includes('사용해 보세요')) {
                        child.style.display = 'none';
                        child.style.pointerEvents = 'none';
                    } else {
                        const style = window.getComputedStyle(child);
                        if (style.position === 'fixed' || style.position === 'absolute') {
                            child.style.display = 'none';
                            child.style.pointerEvents = 'none';
                        }
                    }
                }
            } catch (portalErr) {}

            // 전체 화면을 덮는 고정 백드롭/블러 레이어 강제 숨김
            try {
                const allElements = document.querySelectorAll('*');
                for (const el of allElements) {
                    if (el === document.body || el === document.documentElement || el.id === '__next' || el.id === 'root' || el.tagName === 'SCRIPT' || el.tagName === 'STYLE') {
                        continue;
                    }
                    const style = window.getComputedStyle(el);
                    if (style.position === 'fixed' || style.position === 'absolute') {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > window.innerWidth * 0.8 && rect.height > window.innerHeight * 0.8) {
                            el.style.display = 'none';
                            el.style.pointerEvents = 'none';
                        }
                    }
                }
            } catch (overlayErr) {}

            // pointer-events: none 및 blur 필터 차단 해제 복구
            try {
                document.body.style.pointerEvents = 'auto';
                document.body.style.filter = 'none';
                document.body.style.overflow = 'auto';
                document.documentElement.style.pointerEvents = 'auto';
                document.documentElement.style.filter = 'none';
                
                const mainApp = document.getElementById('__next') || document.getElementById('root');
                if (mainApp) {
                    mainApp.style.filter = 'none';
                    mainApp.style.pointerEvents = 'auto';
                }
            } catch (styleErr) {}
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
                    try:
                        loc.click(timeout=timeout, force=True)
                        return True
                    except Exception:
                        loc.click(timeout=timeout)
                        return True
        except Exception:
            pass
    return False


def open_new_project(page, force_new=True):
    # 이미 프로젝트 페이지에 정상 진입해 있고 프롬프트 입력창이 활성화되어 있더라도 force_new가 참이면 새 프로젝트를 생성
    if not force_new and "/project/" in page.url:
        try:
            if page.locator(PROMPT_SELECTOR).first.is_visible(timeout=3000):
                log("  [NAV] 이미 프로젝트 화면에 정상 진입해 있습니다. 바로 진행합니다.")
                return True
        except Exception:
            pass


    # 브라우저 기동 직후 첫 내비게이션이 net::ERR_CONNECTION_RESET 등으로 일시 실패하는
    # 경우가 있어, 일시적 네트워크 오류에 한해 짧은 백오프로 재시도한다(씬 영구 누락 방지).
    last_err = None
    for attempt in range(4):
        try:
            log(f"  [NAV] {BASE}로 이동 중... (시도 {attempt+1}/4)")
            page.goto(BASE, wait_until="commit", timeout=30000)
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
    # Landing page enter check
    try:
        for enter_sel in [
            "button:has-text('Google Flow로 만들기')", 
            "a:has-text('Google Flow로 만들기')", 
            "div:has-text('Google Flow로 만들기')", 
            "button:has-text('Make with Google Flow')", 
            "a:has-text('Make with Google Flow')"
        ]:
            loc = page.locator(enter_sel).first
            if loc.is_visible(timeout=1000):
                log(f"  [CLI-AUTO] Landing page detected. Clicking enter button: {enter_sel}")
                loc.click(timeout=3000)
                page.wait_for_timeout(3000)
                break
    except Exception as enter_err:
        log(f"  [CLI-AUTO] Landing page enter button click error: {enter_err}")
        
    # 에디터 프롬프트 박스가 아직 안 보이는 상태라면 새 프로젝트 버튼을 클릭해야 함
    prompt_visible = False
    try:
        if page.locator(PROMPT_SELECTOR).first.is_visible(timeout=500):
            prompt_visible = True
    except Exception:
        pass

    if ("/project/" not in page.url) or (not prompt_visible):
        success_click = False
        # 1. JS direct click on the project button (very robust fallback)
        try:
            button_html = page.evaluate(r"""() => {
                const btn = Array.from(document.querySelectorAll('*')).find(el => {
                    const txt = (el.innerText || '').trim();
                    return (txt === '+ 새 프로젝트' || txt === '+ 새로운 프로젝트' || txt === '새 프로젝트' || txt === '새로운 프로젝트' || txt === '+ New project' || txt === 'New project');
                });
                if (btn) {
                    let clickable = btn;
                    while (clickable && clickable.parentElement && clickable.tagName !== 'BUTTON' && clickable.getAttribute('role') !== 'button' && !clickable.className.includes('button') && !clickable.className.includes('btn')) {
                        clickable = clickable.parentElement;
                    }
                    return clickable ? clickable.outerHTML : btn.outerHTML;
                }
                return 'Not Found';
            }""")
            log(f"  [CLI-AUTO] 매칭된 새 프로젝트 버튼 HTML: {button_html}")

            clicked_via_js = page.evaluate(r"""() => {
                const btn = Array.from(document.querySelectorAll('*')).find(el => {
                    const txt = (el.innerText || '').trim();
                    return (txt === '+ 새 프로젝트' || txt === '+ 새로운 프로젝트' || txt === '새 프로젝트' || txt === '새로운 프로젝트' || txt === '+ New project' || txt === 'New project');
                });
                if (btn) {
                    let clickable = btn;
                    while (clickable && clickable.parentElement && clickable.tagName !== 'BUTTON' && clickable.getAttribute('role') !== 'button' && !clickable.className.includes('button') && !clickable.className.includes('btn')) {
                        clickable = clickable.parentElement;
                    }
                    const target = clickable || btn;
                    target.click();
                    const events = ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'];
                    for (const name of events) {
                        try {
                            target.dispatchEvent(new MouseEvent(name, { bubbles: true, cancelable: true, view: window }));
                        } catch (e) {}
                    }
                    return true;
                }
                return false;
            }""")
            if clicked_via_js:
                log("  [CLI-AUTO] JS로 새 프로젝트 버튼 클릭 (전체 마우스 이벤트) 성공 ✔")
                success_click = True
        except Exception as js_click_err:
            log(f"  [WARN] JS 새 프로젝트 버튼 클릭 오류: {js_click_err}")

        # 1.5 Playwright native button locator click fallback
        if not success_click:
            try:
                for selector in [
                    "button:has-text('새로운 프로젝트')",
                    "button:has-text('새 프로젝트')",
                    "button:has-text('New project')",
                    "button:has-text('add_2')"
                ]:
                    loc = page.locator(selector).first
                    if loc.is_visible(timeout=500):
                        loc.click(timeout=2000, force=True)
                        log(f"  [CLI-AUTO] Playwright 네이티브 로케이터 클릭 성공 ({selector}) ✔")
                        success_click = True
                        break
            except Exception as pl_click_err:
                log(f"  [WARN] Playwright 네이티브 로케이터 클릭 실패: {pl_click_err}")

        # 2. Playwright text click fallback
        if not success_click:
            success_click = (
                click_text(page, "+ 새로운 프로젝트") or
                click_text(page, "새로운 프로젝트") or
                click_text(page, "+ 새 프로젝트") or 
                click_text(page, "새 프로젝트") or 
                click_text(page, "+ New project") or 
                click_text(page, "New project")
            )
        if not success_click:
            try:
                for sel in ["div:has-text('새로운 프로젝트')", "div:has-text('새 프로젝트')", "div:has-text('New project')", "div:has-text('+')"]:
                    loc = page.locator(sel).first
                    if loc.is_visible(timeout=1000):
                        loc.click(timeout=3000, force=True)
                        success_click = True
                        break
            except Exception:
                pass
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
        # 1. Try to close the agent sidebar first if visible
        closed_sidebar = False
        for close_sel in [
            "button[aria-label*='닫기']",
            "button[aria-label*='Close']",
            "button[aria-label*='close']",
            "button:has(.material-icons:has-text('close'))",
            "button:has-text('close')",
            ".material-icons:has-text('close')"
        ]:
            try:
                loc = page.locator(close_sel).first
                if loc.is_visible(timeout=500):
                    loc.click(timeout=1000)
                    log(f"  [CLI-AUTO] 에이전트 사이드바 닫기 클릭 성공: {close_sel}")
                    closed_sidebar = True
                    page.wait_for_timeout(1000)
                    break
            except Exception:
                pass
        
        if not closed_sidebar:
            click_text(page, "에이전트")      # toggle Agent OFF
            page.wait_for_timeout(900)
    # open the model chip menu (chip label may be 동영상.. or Nano Banana..)
    for t in ("Nano Banana", "crop_16_9", "동영상", "이미지"):
        if click_text(page, t):
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


def set_os_clipboard(text):
    """OS 클립보드에 UTF-8 텍스트를 안정적으로 올린다 (한글 자모 포함 대응)."""
    import subprocess, tempfile
    fd, p = tempfile.mkstemp(suffix=".txt")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Get-Content -Raw -Encoding UTF8 -LiteralPath '{p}' | Set-Clipboard"],
            check=False,
        )
    finally:
        try:
            os.remove(p)
        except Exception:
            pass


def fill_prompt(page, text):
    b = page.locator(PROMPT_SELECTOR).first
    
    # 1. 텍스트 박스 클릭 및 포커스 확보 (다양한 방법 동원)
    focus_success = False
    for attempt in range(3):
        try:
            if attempt == 0:
                b.click(timeout=2000)
            elif attempt == 1:
                b.click(force=True, timeout=2000)
            else:
                b.evaluate("el => el.focus()")
            focus_success = True
            break
        except Exception:
            page.wait_for_timeout(150)
            
    if not focus_success:
        log("  [WARN] 포커스 획득 실패.")
        
    page.wait_for_timeout(200)
    
    # 2. 기존 텍스트 비우기 — 실제 키 입력으로 Slate 모델까지 동기화
    try:
        b.click(timeout=1500)
    except Exception:
        pass
    try:
        b.press("Control+a")
        page.wait_for_timeout(80)
        b.press("Delete")
        page.wait_for_timeout(120)
    except Exception:
        pass

    # 3. 프롬프트 입력 — OS 클립보드 붙여넣기(Ctrl+V)를 사용한다.
    def _editor_text():
        try:
            return (b.evaluate("el => el.innerText") or "").strip()
        except Exception:
            return ""

    target = (text or "").strip()
    probe = target[:18]
    pasted_ok = False

    try:
        set_os_clipboard(text)
        page.wait_for_timeout(150)
        b.press("Control+v")
        page.wait_for_timeout(450)
        cur = _editor_text()
        if cur and probe and probe in cur:
            pasted_ok = True
            log("  [CLI-AUTO] OS 클립보드 붙여넣기 성공 ✔")
        else:
            log(f"  [WARN] 붙여넣기 후 에디터 불일치 (len={len(cur)}).")
    except Exception as e:
        log(f"  [WARN] OS 클립보드 붙여넣기 실패: {e}")

    # 4. 폴백 — 실제 키보드 타이핑 (keydown/beforeinput/input 완전 발생 → Slate 모델 갱신)
    if not pasted_ok:
        try:
            b.press("Control+a")
            page.wait_for_timeout(60)
            b.press("Delete")
            page.wait_for_timeout(100)
            page.keyboard.type(text, delay=12)
            page.wait_for_timeout(300)
            cur = _editor_text()
            if cur and probe and probe in cur:
                log("  [CLI-AUTO] 키보드 타이핑 폴백 성공 ✔")
            else:
                log(f"  [WARN] 타이핑 후에도 에디터 내용 불일치 (len={len(cur)}).")
        except Exception as e:
            log(f"  [WARN] 키보드 타이핑 폴백 실패: {e}")
        
    # 5. 생성 버튼 활성화 대기 (aria-disabled="true"가 해제될 때까지 최대 3초 대기)
    try:
        deadline = time.time() + 3.0
        btn_activated = False
        while time.time() < deadline:
            is_disabled = page.evaluate("""() => {
                const btn = Array.from(document.querySelectorAll('button')).find(btn => 
                    btn.textContent.includes('arrow_forward') || 
                    (btn.getAttribute('aria-label') && (btn.getAttribute('aria-label').includes('만들기') || btn.getAttribute('aria-label').includes('Generate') || btn.getAttribute('aria-label').includes('생성')))
                );
                if (!btn) return true;
                return btn.getAttribute('aria-disabled') === 'true' || btn.disabled;
            }""")
            if not is_disabled:
                log("  [CLI-AUTO] 생성 버튼 활성화 상태 감지 ✔")
                btn_activated = True
                break
            page.wait_for_timeout(200)
        if not btn_activated:
            log("  [WARN] 생성 버튼이 여전히 비활성화(aria-disabled=true) 상태입니다. 강제 클릭을 시도합니다.")
    except Exception:
        pass
        
    page.wait_for_timeout(300)


def generate(page):
    # Debug info to trace button selectors and disabled states
    try:
        buttons_info = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('button')).map(b => ({
                text: b.textContent || '',
                aria: b.getAttribute('aria-label') || '',
                disabled: b.disabled,
                visible: b.getBoundingClientRect().width > 0,
                className: b.className || '',
                html: b.outerHTML.substring(0, 150)
            }));
        }""")
        log("=== [DEBUG] 화면의 모든 버튼 목록 ===")
        for idx, btn in enumerate(buttons_info):
            if btn['visible']:
                log(f"Button {idx}: text='{btn['text']}', aria='{btn['aria']}', disabled={btn['disabled']}, html='{btn['html']}'")
    except Exception as dbg_err:
        log(f"=== [DEBUG] 버튼 스캔 에러: {dbg_err}")

    # 1. Try with the original text click first (no Y limit to prevent resolution scale bugs)
    if click_text(page, "arrow_forward", timeout=3000):
        return True
        
    # 2. Selector fallback list for the submit/generate button
    for sel in [
        "button:has-text('arrow_forward')",
        "button[aria-label*='생성']",
        "button[aria-label*='Generate']",
        "button:has(.material-icons:has-text('arrow_forward'))",
        "button:has(svg)",
        "button:has-text('제출')"
    ]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible():
                loc.click(force=True, timeout=2000)
                return True
        except Exception:
            pass
    return False


def wait_image(page, n, timeout_s=100):
    """최대 100초 동안 이미지가 생성되기를 기다립니다. 3초 주기로 스캔합니다.
    ★타임아웃이 짧으면(구 40초) Nano Banana2가 늦게 끝날 때 '다시 실행'이 눌려
      이미지가 하나 더 생성됨(2크레딧 낭비). 넉넉히 기다려 중복 생성을 막는다.
    만약 40초 동안 생성되지 않으면, 실패로 처리하고 사용자의 프로토콜을 수행합니다:
    1. 스크린샷 캡처
    2. 재시작(Retry) 버튼 감지하여 클릭
    3. 스크린샷 캡처
    4. 오른쪽/최신 타일 삭제 버튼 위치 확인하여 삭제
    5. False 반환 (상위 호출처에서 재시도)"""
    
    log(f"이미지 생성 대기 중... (최대 {timeout_s}초)")
    deadline = time.time() + timeout_s
    success = False
    
    # 3초 간격으로 확인하며 한도까지 대기 (완성 즉시 감지 → 불필요한 재시도 방지)
    while time.time() < deadline:
        if page.evaluate(BIG_MEDIA_IMG_JS):
            page.wait_for_timeout(1500)
            success = True
            break
        page.wait_for_timeout(3000)
        
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
            retry_count += 1
            if retry_count >= max_retries:
                log("  [ERR] 3회 연속 비디오 생성 실패. 브라우저 재기동(Reboot)을 위해 예외를 발생시킵니다.")
                raise BrowserRebootException("3 consecutive video generation failures")
            page.wait_for_timeout(3000)
            continue
            
        # 1. 80초 기본 대기 후, 완성(VIDEO_DONE_JS)될 때까지 폴링(최대 220초).
        #    영상이 90초+ 걸리는 경우 대응. 완성 감지 전엔 클릭하지 않음(조기 클릭 방지).
        log("동영상 생성 중... (80초 기본 대기 → 완성까지 폴링, 최대 220초)")
        page.wait_for_timeout(80000)
        waited = 80000
        while waited < 220000:
            try:
                if page.evaluate(VIDEO_DONE_JS):
                    log(f"  완성 비디오 감지 ({waited//1000}s)")
                    break
            except Exception:
                pass
            page.wait_for_timeout(10000)
            waited += 10000

        # 2. 가장 왼쪽 타일(비디오) 클릭하여 라이트박스 띄우기
        posters = page.evaluate(POSTERS_JS)
        if not posters or len(posters) < 1:
            log("  [WARN] 캔버스에 타일이 존재하지 않습니다. 실패 처리.")
            delete_tile_by_index(page, 0)
            retry_count += 1
            continue
            
        target = posters[0]
        log(f"  가장 왼쪽 비디오 타일 클릭 시도 ({target['x']}, {target['y']})")
        
        # Session 0 백그라운드 환경 크래시 방지를 위해 try-except 감싸고 JS dispatch 클릭 병행
        clicked = False
        try:
            page.mouse.click(target["x"], target["y"])
            clicked = True
        except Exception as e:
            log(f"  [WARN] mouse.click 에러 (무시하고 JS dispatch 시도): {e}")
            
        # JS click event dispatch (세그폴트 방지 및 백그라운드 100% 신뢰성 보장)
        try:
            js_clicked = page.evaluate(r"""() => {
                const imgs = Array.from(document.querySelectorAll('img')).filter(im => {
                    const s = im.getAttribute('src') || '';
                    if (!/media\.getMediaUrlRedirect|googleusercontent/.test(s)) return false;
                    const r = im.getBoundingClientRect();
                    return r.width >= 120 && r.height >= 120 && r.width <= 1200 && r.height <= 1600;
                });
                if (imgs.length > 0) {
                    imgs.sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left);
                    const targetImg = imgs[0];
                    targetImg.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                    return true;
                }
                return false;
            }""")
            if js_clicked:
                clicked = True
        except Exception as js_err:
            log(f"  [WARN] JS dispatch 클릭 오류: {js_err}")
            
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
            
            try:
                page.mouse.move(target["x"], target["y"])
                page.wait_for_timeout(300)
                page.mouse.click(target["x"], target["y"])
            except Exception:
                pass
                
            # JS 재클릭 시도
            try:
                page.evaluate(r"""() => {
                    const imgs = Array.from(document.querySelectorAll('img')).filter(im => {
                        const s = im.getAttribute('src') || '';
                        if (!/media\.getMediaUrlRedirect|googleusercontent/.test(s)) return false;
                        const r = im.getBoundingClientRect();
                        return r.width >= 120 && r.height >= 120 && r.width <= 1200 && r.height <= 1600;
                    });
                    if (imgs.length > 0) {
                        imgs.sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left);
                        imgs[0].dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                    }
                }""")
            except Exception:
                pass
                
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


def upload_image(page, image_path):
    """기존 이미지 파일을 Flow 의 숨은 file input 에 주입(set_input_files) + '추가' 확인.
    (flow_driver.upload 와 동일 로직 — 세종 초상화 등 레퍼런스 업로드용)."""
    image_path = os.path.abspath(image_path)
    if not os.path.exists(image_path):
        log(f"  [UPLOAD] 파일 없음: {image_path}")
        return False
    done = False
    for i, fr in enumerate(page.frames):
        try:
            inputs = fr.locator("input[type='file']")
            for j in range(inputs.count()):
                try:
                    inputs.nth(j).set_input_files(image_path, timeout=5000)
                    log(f"  [UPLOAD] OK set_input_files frame[{i}][{j}] {image_path}")
                    done = True
                    break
                except Exception:
                    pass
        except Exception:
            pass
        if done:
            break
    if not done:
        log("  [UPLOAD] 어떤 file input 도 이미지를 받지 못함")
        return False
    page.wait_for_timeout(2500)
    for t in ("프롬프트에 추가", "Add to prompt", "추가", "Add"):
        if click_text(page, t):
            log(f"  [UPLOAD] 확인 클릭 '{t}'")
            break
    page.wait_for_timeout(2500)
    return True


def make_scene_upload(page, n, image_path, motion_prompt, aspect="16:9"):
    """업로드 기반 씬: 텍스트→이미지 대신 레퍼런스 이미지를 업로드해 첫 프레임으로 쓰고,
    이후 모션→영상→다운로드는 검증된 make_video 파이프라인을 그대로 사용."""
    global OUT_DIR
    out_path = os.path.join(OUT_DIR, f"scene_{n}.mp4")
    log(f"=== Scene {n} (업로드 기반: {os.path.basename(image_path)}) ===")
    if not open_new_project(page):
        log("[ERR] 프로젝트/컴포저 진입 실패")
        return False
    shot(page, f"s{n}_00_editor")
    set_image_mode(page, aspect=aspect)
    if not upload_image(page, image_path):
        log("[ERR] 이미지 업로드 실패")
        shot(page, f"s{n}_upload_fail")
        return False
    page.wait_for_timeout(30000)  # 업로드는 실제 ~30초 걸림(사장님 확정). 타일 완전 준비 전엔 '애니메이션 적용'이 없어 실패함
    animated = False
    for attempt in range(5):
        if animate_image(page):
            animated = True
            break
        log(f"  [UPLOAD] 애니메이션 적용 재시도 {attempt+1}/5 (타일 준비 대기)...")
        page.wait_for_timeout(6000)
    if not animated:
        log("[ERR] '애니메이션 적용' 실패")
        shot(page, f"s{n}_animate_fail")
        return False
    page.wait_for_timeout(1500)
    shot(page, f"s{n}_02_animate")
    if make_video(page, out_path, motion_prompt, n):
        log(f"[OK] Scene {n} (업로드) → {out_path}")
        shot(page, f"s{n}_03_done")
        return True
    log(f"[FAIL] Scene {n} 영상 생성/다운로드 실패")
    return False


def make_scene(page, n, image_prompt, motion_prompt, force=False, aspect="16:9"):
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

        set_image_mode(page, aspect=aspect)
        fill_prompt(page, image_prompt)
        if not generate(page):
            shot(page, f"s{n}_generate_fail")
            log("[ERR] 이미지 생성 버튼 클릭 실패")
            img_retry += 1
            if img_retry >= max_img_retry:
                log("  [ERR] 이미지 생성 3회 연속 실패. 브라우저 재기동(Reboot)을 요청합니다.")
                raise BrowserRebootException("3 consecutive image generation failures")
            page.wait_for_timeout(3000)
            continue
            
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
    ap.add_argument("--upload", default="", help="이 이미지를 업로드해 첫 프레임으로 사용(텍스트→이미지 생성 대신). --scene N 과 함께 사용.")
    ap.add_argument("--motion", default="", help="업로드 씬의 모션 프롬프트 직접 지정(미지정 시 프롬프트 파일의 모션 사용).")
    ap.add_argument("--aspect", default="16:9", help="영상 가로세로 비율 (16:9, 9:16 등)")
    ap.add_argument("--profile-idx", type=int, help="특정 번호의 크롬 프로필을 고정으로 사용 (0-9)")
    ap.add_argument("--profiles-count", type=int, help="라운드 로빈으로 교대하여 사용할 총 크롬 프로필 수 (지정 시 매 씬마다 교대 가동)")
    ap.add_argument("--profile-cycle", default="", help="명시적 프로필 순환 순서(쉼표). 예: '0,1,0,2,0,3,0,4,0,5' — 대용량 계정(0)을 매번 끼워 소진 극대화. --profiles-count보다 우선.")
    ap.add_argument("--interactive", action="store_true", help="프로필 로그인을 위한 수동 인터랙티브 모드 기동 (브라우저를 열어두고 대기)")
    args = ap.parse_args()

    scenes = parse_prompts(args.prompts)
    if not scenes and not args.interactive:
        log("프롬프트 없음")
        return
        
    global PROFILE
    if args.profile_idx is not None:
        PROFILE = os.path.abspath(f"assets/chrome_profile_{args.profile_idx}")
        log(f"[PROFILE] 지정된 단일 프로필 사용: {PROFILE}")

    # Set output directory to project root, named after the prompts file (e.g. chiropractic_science)
    prompts_base = os.path.splitext(os.path.basename(args.prompts))[0]
    if prompts_base.endswith("_prompts"):
        prompts_base = prompts_base[:-8]
    global OUT_DIR
    OUT_DIR = os.path.abspath(prompts_base)
    
    os.makedirs(DBG, exist_ok=True)
    os.makedirs(DL_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1. 수동 인터랙티브 로그인 헬퍼 모드
    if args.interactive:
        log(f"\n==================================================================")
        log(f"[INTERACTIVE MODE] 크롬 프로필 로그인 세션을 활성화합니다.")
        log(f"타겟 프로필 경로: {PROFILE}")
        log(f"구글 계정 로그인을 완료한 뒤, 정상 브라우징이 가능한 상태가 되면")
        log(f"이 명령 프롬프트 창에서 [Enter] 키를 눌러 브라우저를 닫고 세션을 저장해 주세요.")
        log(f"==================================================================\n")
        
        force_kill_profile_chrome(PROFILE)
        with sync_playwright() as p:
            c = p.chromium.launch_persistent_context(
                PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
                ignore_default_args=["--enable-automation"],
                args=["--start-maximized", "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
            pg = c.pages[0] if c.pages else c.new_page()
            try:
                pg.goto(BASE)
            except Exception as ge:
                log(f"페이지 접속 실패 (무시 가능): {ge}")
            
            # 사용자 엔터 입력 대기
            print("\n>>> 구글 계정 로그인을 완전히 마치셨다면 이 창에서 [Enter] 키를 입력하세요...", flush=True)
            input()
            try:
                c.close()
            except Exception:
                pass
        log("[INTERACTIVE] 세션 설정 및 저장이 성공적으로 완료되었습니다!")
        return

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

    todo = [args.scene] if args.scene is not None else sorted(scenes)

    class BrowserWrapper:
        def __init__(self, obj, is_cdp):
            self.obj = obj
            self.is_cdp = is_cdp
        def close(self):
            if self.is_cdp:
                try:
                    self.obj.disconnect()
                    log("  [CDP] CDP 연결이 정상적으로 종료(disconnect)되었습니다.")
                except Exception as e:
                    log(f"  [CDP] disconnect 오류: {e}")
            else:
                try:
                    self.obj.close()
                    log("  [BROWSER] 브라우저 컨텍스트 정상 종료 완료.")
                except Exception as e:
                    log(f"  [BROWSER] close 오류: {e}")

    ok, fail = [], []

    # 명시적 순환 순서(예: 0,1,0,2,0,3,0,4,0,5) — 대용량 계정 0을 매번 끼워 소진 극대화
    _cyc = [int(x) for x in args.profile_cycle.split(",") if x.strip() != ""] if args.profile_cycle else None
    _cyc_pos = {"i": 0}

    def get_run_profile(scene_num):
        if _cyc:
            idx = _cyc[_cyc_pos["i"] % len(_cyc)]; _cyc_pos["i"] += 1
            return os.path.abspath(f"assets/chrome_profile_{idx}")
        if args.profiles_count and args.profiles_count >= 1:
            idx = scene_num % args.profiles_count
            return os.path.abspath(f"assets/chrome_profile_{idx}")
        return PROFILE

    # A. 라운드 로빈 순환 모드 (매 씬마다 브라우저를 새로 열고 닫음)
    if (args.profiles_count and args.profiles_count >= 1) or _cyc:
        log(f"[SCHEDULER] 총 {args.profiles_count}개 크롬 프로필 라운드 로빈 순환 생성 모드 시작")
        for n in todo:
            if n not in scenes:
                continue
                
            out_path = os.path.join(OUT_DIR, f"scene_{n}.mp4")
            if not args.force and progress.get(str(n)) == "success" and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                log(f"[SKIP-PROGRESS] 이미 성공한 씬: {out_path}")
                ok.append(n)
                continue

            current_profile = get_run_profile(n)
            log(f"\n>>> [ROUND-ROBIN] Scene {n} 생성 시작 | 프로필: {os.path.basename(current_profile)}")
            
            # 기동 전 안전 락 클리어
            force_kill_profile_chrome(current_profile)
            time.sleep(1)
            
            try:
                with sync_playwright() as p:
                    log(f"  [LAUNCH] {os.path.basename(current_profile)} persistent context 기동")
                    c = p.chromium.launch_persistent_context(
                        current_profile, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
                        accept_downloads=True, downloads_path=DL_DIR, slow_mo=150,
                        ignore_default_args=["--enable-automation"],
                        args=["--start-maximized", "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR", "--disable-gpu"])
                    pg = c.pages[0] if c.pages else c.new_page()
                    
                    if args.upload:
                        success = make_scene_upload(pg, n, args.upload, args.motion or scenes[n][1], aspect=args.aspect)
                    else:
                        success = make_scene(pg, n, *scenes[n], force=args.force, aspect=args.aspect)
                        
                    # 진행 상황 저장
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
                    
                    try:
                        c.close()
                    except Exception:
                        pass
            except Exception as e:
                log(f"[ERR] Scene {n} 순환 처리 에러: {e}")
                traceback.print_exc()
                fail.append(n)
            
            # 프로세스 정리 및 쿨다운
            force_kill_profile_chrome(current_profile)
            time.sleep(3) # 씬 전환 간의 간격 쿨다운
            
    # B. 기존 단일 세션 연속 처리 모드 (전동 스택 호환성 보존)
    else:
        with sync_playwright() as p:
            def launch_browser():
                import urllib.request
                try:
                    urllib.request.urlopen("http://localhost:9222/json", timeout=2)
                    log("  [CDP] localhost:9222에서 실행 중인 크롬 감지! CDP 연결을 시도합니다.")
                    c = p.chromium.connect_over_cdp("http://localhost:9222")
                    if c.contexts:
                        ctx = c.contexts[0]
                        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
                    else:
                        pg = c.new_page()
                    return BrowserWrapper(c, True), pg
                except Exception:
                    log("  [CDP] localhost:9222 감지 실패. 새 브라우저 컨텍스트를 기동합니다.")
                    c = p.chromium.launch_persistent_context(
                        PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
                        accept_downloads=True, downloads_path=DL_DIR, slow_mo=150,
                        ignore_default_args=["--enable-automation"],
                        args=["--start-maximized", "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR", "--disable-gpu"])
                    pg = c.pages[0] if c.pages else c.new_page()
                    return BrowserWrapper(c, False), pg

            ctx, page = launch_browser()
            idx = 0
            while idx < len(todo):
                n = todo[idx]
                if n not in scenes:
                    idx += 1
                    continue
                
                out_path = os.path.join(OUT_DIR, f"scene_{n}.mp4")
                if not args.force and progress.get(str(n)) == "success" and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                    log(f"[SKIP-PROGRESS] 이미 성공한 씬: {out_path}")
                    ok.append(n)
                    idx += 1
                    continue

                try:
                    if args.upload:
                        success = make_scene_upload(page, n, args.upload, args.motion or scenes[n][1], aspect=args.aspect)
                    else:
                        success = make_scene(page, n, *scenes[n], force=args.force, aspect=args.aspect)
                    
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
                    log(f"[REBOOT] 브라우저 재기동 요구 발생: {re_err}. 크롬 강제 종료 후 5초 쿨다운 뒤 세션을 재시작합니다.")
                    try:
                        ctx.close()
                    except Exception:
                        pass
                    force_kill_profile_chrome(PROFILE)
                    time.sleep(5)
                    ctx, page = launch_browser()
                except Exception as e:
                    log(f"[ERR] Scene {n} 일반 에러: {e}")
                    traceback.print_exc()
                    shot(page, f"s{n}_error")
                    fail.append(n)
                    idx += 1
            try:
                ctx.close()
            except Exception:
                pass

    log(f"최종 완료 — 성공 {ok} / 실패 {fail}")


if __name__ == "__main__":
    main()
