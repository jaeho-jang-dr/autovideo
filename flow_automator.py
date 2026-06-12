"""
flow_automator.py — Google Flow (labs.google/fx/tools/flow) browser automator.

100% GUI automation via Playwright over the user's local Chrome profile.
NO Veo/Gemini/Vertex API keys are ever used. NO browser extension is used.

Editor anatomy (new Google Flow "Omni" editor, 2026):
  dashboard -> "새 프로젝트"(New project) -> project editor with a bottom
  composer bar.
  * Hidden upload input : input[type="file"][accept="image/*"] (global)
  * "미디어 추가" button  : <button> add icon, accessible-name "미디어 추가"
  * Prompt field        : div[role="textbox"][contenteditable="true"]
                          (Slate editor, placeholder "무엇을 만들고 싶으신가요?")
  * Generate button     : <button> arrow_forward icon, accessible-name "만들기"
                          (aria-disabled until image + prompt are present)

Usage:
  python flow_automator.py                      # all scenes, fully automatic
  python flow_automator.py --scene 1            # single scene
  python flow_automator.py --scene 1 --verify   # upload+prompt only, NO generate
  python flow_automator.py --force              # re-generate even if mp4 exists
  python flow_automator.py --debug              # open editor, dump DOM, exit
"""

import os
import re
import sys
import time
import glob
import shutil
import argparse
import traceback
from playwright.sync_api import sync_playwright

# Korean Windows consoles default to cp949, which cannot encode characters such
# as the em-dash or arrows used in log lines. Force UTF-8 stdout/stderr so logs
# never crash the run (display may mojibake, but files stay correct UTF-8).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

FLOW_BASE = "https://labs.google/fx/tools/flow"
DEBUG_DIR = "debug"
DOWNLOAD_DIR = os.path.abspath(os.path.join(DEBUG_DIR, "downloads"))

# Bottom-composer signal: the Slate prompt textbox is the reliable "editor ready"
PROMPT_SELECTOR = "div[role='textbox'][contenteditable='true']"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_prompts(prompt_file):
    prompts = {}
    if not os.path.exists(prompt_file):
        print(f"[ERROR] Prompt file not found: {prompt_file}")
        return prompts
    pattern = re.compile(r"\[Scene\s+(\d+)\]\s+(.*)", re.IGNORECASE)
    with open(prompt_file, "r", encoding="utf-8") as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                prompts[int(m.group(1))] = m.group(2).strip()
    return prompts


def save_screenshot(page, name):
    os.makedirs(DEBUG_DIR, exist_ok=True)
    path = os.path.abspath(f"{DEBUG_DIR}/{name}.png")
    try:
        page.screenshot(path=path, full_page=False)
        print(f"[DEBUG] Screenshot: {path}")
    except Exception as e:
        print(f"[DEBUG] Screenshot failed: {e}")
    return path


def dump_frame_tree(page):
    """Diagnostic: dump frames + interactive elements (light + shadow DOM)."""
    scan_js = r"""
    () => {
      const out = [];
      const want = (el) => {
        const t = el.tagName;
        if (['INPUT','TEXTAREA','BUTTON','A','SELECT','LABEL'].includes(t)) return true;
        const ce = el.getAttribute && el.getAttribute('contenteditable');
        if (ce === 'true' || ce === 'plaintext-only') return true;
        const r = el.getAttribute && el.getAttribute('role');
        return ['button','textbox','tab','menuitem'].includes(r);
      };
      const walk = (root, sh) => {
        let ns; try { ns = root.querySelectorAll('*'); } catch(e){ return; }
        for (const el of ns) {
          if (want(el)) {
            const rc = el.getBoundingClientRect();
            out.push({tag: el.tagName, type: el.getAttribute('type')||'',
              role: el.getAttribute('role')||'', ce: el.getAttribute('contenteditable')||'',
              ph: el.getAttribute('placeholder')||'', aria: el.getAttribute('aria-label')||'',
              testid: el.getAttribute('data-testid')||'', accept: el.getAttribute('accept')||'',
              text: (el.textContent||'').trim().slice(0,50),
              vis: rc.width>0 && rc.height>0, sh: sh});
          }
          if (el.shadowRoot) walk(el.shadowRoot, true);
        }
      };
      walk(document, false);
      return out;
    }"""
    print(f"\n{'='*60}\n[FRAMES] Total: {len(page.frames)}")
    for i, f in enumerate(page.frames):
        print(f"  [{i:02d}] {f.url[:110]}")
        try:
            for el in f.evaluate(scan_js):
                lbl = el['aria'] or el['ph'] or el['testid'] or el['text']
                if not (lbl or el['type'] == 'file'):
                    continue
                mark = "S" if el['sh'] else " "
                v = "v" if el['vis'] else "."
                print(f"    [{mark}{v}] {el['tag']:<8} t={el['type']:<6} "
                      f"r={el['role']:<7} accept='{el['accept'][:10]}' "
                      f"testid='{el['testid'][:18]}' ph='{el['ph'][:16]}' "
                      f"aria='{el['aria'][:22]}' txt='{el['text'][:24]}'")
        except Exception:
            pass
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Overlay dismissal (cookie consent + announcement modals)
# ---------------------------------------------------------------------------

def dismiss_overlays(page, rounds=4):
    """Click away cookie banners / changelog modals that block the editor."""
    labels = [
        # cookie consent
        "button:has-text('Agree')", "button:has-text('동의')",
        "button:has-text('Accept all')", "button:has-text('No thanks')",
        # Gemini Omni Pricing Update modal and other onboarding modals
        "button:has-text('시작하기')", "button:has-text('Start')",
        "button:has-text('Get started')", "button:has-text('시작')",
        "button:has-text('Got it')", "button:has-text('확인')",
        "button:has-text('Continue')", "button:has-text('Skip')",
        "button:has-text('Close')", "button:has-text('닫기')",
        "[aria-label='Close']", "[aria-label='닫기']",
        "[aria-label*='close' i]",
    ]
    for _ in range(rounds):
        hit = False
        for sel in labels:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=400):
                    loc.click(timeout=2000, force=True)
                    print(f"[overlay] dismissed: {sel}")
                    hit = True
                    page.wait_for_timeout(700)
            except Exception:
                pass
        if not hit:
            break


# ---------------------------------------------------------------------------
# Navigate to Frames to Video tab in the sidebar
# ---------------------------------------------------------------------------

def navigate_to_frames_to_video(page, timeout_ms=20000):
    """Click the Frames to Video sidebar tab after new project is opened."""
    if "frames-to-video" in page.url:
        print(f"[FTV] 이미 frames-to-video URL: {page.url}")
        return True
    # If the prompt composer is already visible, we're already in the right editor.
    try:
        if page.locator(PROMPT_SELECTOR).first.is_visible(timeout=800):
            print("[FTV] 프롬프트 입력창 이미 노출 — 에디터 준비됨, 탭 클릭 생략.")
            return True
    except Exception:
        pass

    ftv_selectors = [
        # English
        "button:has-text('Frames to Video')",
        "[role='tab']:has-text('Frames to Video')",
        "a:has-text('Frames to Video')",
        "[aria-label*='Frames to Video' i]",
        "[data-testid*='frames' i]",
        # Korean
        "button:has-text('프레임으로 동영상')",
        "[role='tab']:has-text('프레임으로 동영상')",
        "a:has-text('프레임으로 동영상')",
        "[aria-label*='프레임으로 동영상']",
        # Short forms
        "[role='tab']:has-text('Frames')",
        "li:has-text('Frames to Video')",
        "li:has-text('프레임으로 동영상')",
    ]
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        for sel in ftv_selectors:
            for f in page.frames:
                try:
                    loc = f.locator(sel).first
                    if loc.is_visible(timeout=400):
                        loc.click(timeout=3000)
                        print(f"[FTV] Frames to Video 탭 클릭: {sel}")
                        page.wait_for_timeout(2500)
                        dismiss_overlays(page)
                        page.wait_for_timeout(1000)
                        return True
                except Exception:
                    pass
        if "frames-to-video" in page.url:
            print(f"[FTV OK] frames-to-video URL 도달: {page.url}")
            return True
        time.sleep(0.8)
    print("[FTV WARN] Frames to Video 탭 미발견 — 현재 에디터 화면에서 계속 진행.")
    return False


# ---------------------------------------------------------------------------
# Open the editor (dashboard -> new project -> composer ready)
# ---------------------------------------------------------------------------

def open_editor(page, is_interactive, timeout_ms=60000):
    """Navigate to the editor and return True when the composer is ready."""
    print(f"[NAV] {FLOW_BASE}")
    page.goto(FLOW_BASE, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3500)

    if "accounts.google.com" in page.url:
        print("[AUTH] 구글 로그인 페이지로 리디렉트 됨.")
        if is_interactive:
            input("로그인 완료 후 [Enter] 를 누르세요...")
        else:
            print("자동 모드: 로그인 완료를 최대 90초 대기...")
            try:
                page.wait_for_url("**/labs.google/**", timeout=90000)
                print("[AUTH OK] labs.google 복귀 확인.")
            except Exception:
                print("[AUTH WARN] labs.google 복귀 미감지. 계속 진행합니다.")

    dismiss_overlays(page)
    save_screenshot(page, "01_dashboard")

    # If we're not already inside a project / frames-to-video editor, open a fresh one.
    if "/project/" not in page.url and "frames-to-video" not in page.url:
        new_project_selectors = [
            "button:has-text('새 프로젝트')", "button:has-text('New project')",
            "a:has-text('새 프로젝트')", "a:has-text('New project')",
            "button:has-text('Try Omni now')",
            "[aria-label*='새 프로젝트']", "[aria-label*='New project' i]",
        ]
        clicked = False
        for sel in new_project_selectors:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=800):
                    loc.click(timeout=3000)
                    print(f"[NAV] Opened new project via: {sel}")
                    clicked = True
                    page.wait_for_timeout(3000)
                    dismiss_overlays(page)
                    break
            except Exception:
                pass
        if not clicked:
            print("[NAV WARN] '새 프로젝트' 버튼 미발견 — 기존 화면에서 에디터 진입 시도.")

    # Make sure we're on the Frames-to-Video composer if such a tab exists.
    navigate_to_frames_to_video(page, timeout_ms=8000)

    # Wait for the composer (prompt textbox) to be ready.
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        try:
            if page.locator(PROMPT_SELECTOR).first.is_visible(timeout=500):
                print("[Editor OK] 프롬프트 입력창 감지됨.")
                return True
        except Exception:
            pass
        time.sleep(0.5)
    print("[Editor WARN] 프롬프트 입력창 미감지 (타임아웃).")
    return False


# ---------------------------------------------------------------------------
# Confirm the uploaded ingredient ("프롬프트에 추가" / "Add to prompt")
# ---------------------------------------------------------------------------

def click_add_to_prompt_by_ratio(page):
    """Fallback: click the 'Add to prompt' button using screen-ratio coords."""
    try:
        viewport = page.viewport_size
        w, h = (viewport["width"], viewport["height"]) if viewport else (1280, 720)
        x = int(w * 0.6406)
        y = int(h * 0.6944)
        print(f"[Upload] 비율 좌표 물리 클릭 시도: {x}, {y} (Viewport: {w}x{h})")
        page.mouse.click(x, y)
        page.wait_for_timeout(2500)
        return True
    except Exception as e:
        print(f"[Upload WARN] 비율 좌표 클릭 실패: {e}")
        return False


def click_add_to_prompt(page, timeout_ms=30000):
    """Wait up to timeout_ms for the '프롬프트에 추가' button via a recursive JS
    shadow-DOM scanner, then click it. Falls back to a ratio mouse click."""
    print("[Upload] '프롬프트에 추가' 버튼 대기 중 (JS Deep Shadow DOM 스캔)...")
    deadline = time.time() + timeout_ms / 1000
    js_script = """
    (targetText) => {
        function search(node) {
            if (!node) return null;
            if (node.nodeType === Node.ELEMENT_NODE) {
                if (node.shadowRoot) {
                    const res = search(node.shadowRoot);
                    if (res) return res;
                }
                const txt = (node.textContent || node.innerText || "").trim();
                if (txt.includes(targetText) && node.offsetWidth > 0 && node.offsetHeight > 0) {
                    const childCount = node.children ? node.children.length : 0;
                    if (childCount <= 2) {
                        node.click();
                        return txt;
                    }
                }
            }
            for (let i = 0; i < node.childNodes.length; i++) {
                const res = search(node.childNodes[i]);
                if (res) return res;
            }
            return null;
        }
        return search(document.body);
    }
    """
    while time.time() < deadline:
        for f in page.frames:
            try:
                for text in ["프롬프트에 추가", "Add to prompt", "Add to project"]:
                    clicked_text = f.evaluate(js_script, text)
                    if clicked_text:
                        print(f"[Upload OK] JS Deep 스캔 성공 클릭: '{clicked_text}'")
                        page.wait_for_timeout(2000)
                        return True
            except Exception:
                pass
        time.sleep(0.5)
    print("[Upload WARN] '프롬프트에 추가' 버튼 미감지 — 비율 좌표 클릭으로 폴백.")
    click_add_to_prompt_by_ratio(page)
    return False


# ---------------------------------------------------------------------------
# Upload image
# ---------------------------------------------------------------------------

def upload_image(page, image_path):
    """Upload the scene image as the first-frame ingredient. Return True/False."""
    print(f"[Upload] {image_path}")

    # Strategy A: set_input_files directly on the global hidden image input.
    for i, f in enumerate(page.frames):
        try:
            inputs = f.locator("input[type='file']")
            for j in range(inputs.count()):
                try:
                    inputs.nth(j).set_input_files(image_path, timeout=5000)
                    print(f"[Upload OK] set_input_files Frame[{i}][{j}]")
                    page.wait_for_timeout(2500)
                    click_add_to_prompt(page)
                    return True
                except Exception as e:
                    print(f"[Upload WARN] direct input Frame[{i}][{j}]: "
                          f"{str(e)[:80]}")
        except Exception:
            pass

    # Strategy B: click the upload/frame-add button and feed the file chooser.
    # Bilingual: covers both the old Frames-to-Video editor (시작 프레임 추가 / Add
    # start frame) and the new Omni editor (미디어 추가 / Add media).
    add_media_selectors = [
        # Old Frames-to-Video editor — start frame / add frame
        "button:has-text('시작 프레임 추가')", "button:has-text('Add start frame')",
        "[aria-label*='시작 프레임 추가']", "[aria-label*='Add start frame' i]",
        "button:has-text('프레임 추가')", "button:has-text('Add frame')",
        "[aria-label*='프레임 추가']", "[aria-label*='Add frame' i]",
        # New Omni editor — add media
        "button:has-text('미디어 추가')", "button:has-text('Add media')",
        "[aria-label='미디어 추가']", "[aria-label='Add media']",
        # Generic fallbacks
        "button:has-text('미디어')", "button:has-text('Upload')",
        "button:has-text('업로드')",
    ]
    for sel in add_media_selectors:
        try:
            loc = page.locator(sel).first
            if not loc.is_visible(timeout=600):
                continue
            # The add button opens a dialog; the file chooser may fire on click,
            # otherwise an in-dialog "업로드"/"Upload" entry triggers it.
            try:
                with page.expect_file_chooser(timeout=4000) as fc:
                    loc.click()
                fc.value.set_files(image_path)
                print(f"[Upload OK] file_chooser via '{sel}'")
                page.wait_for_timeout(2500)
                click_add_to_prompt(page)
                return True
            except Exception:
                # Dialog opened without immediate chooser — try the input again
                page.wait_for_timeout(800)
                for f in page.frames:
                    try:
                        inp = f.locator("input[type='file']").first
                        inp.set_input_files(image_path, timeout=4000)
                        print(f"[Upload OK] dialog input via '{sel}'")
                        page.wait_for_timeout(2500)
                        click_add_to_prompt(page)
                        return True
                    except Exception:
                        pass
                # Try a nested "업로드/Upload" menu item inside the dialog
                for item in ["text=업로드", "text=Upload", "text=내 기기",
                             "text=컴퓨터에서 업로드", "text=Upload from computer"]:
                    try:
                        mi = page.locator(item).first
                        if mi.is_visible(timeout=500):
                            with page.expect_file_chooser(timeout=4000) as fc2:
                                mi.click()
                            fc2.value.set_files(image_path)
                            print(f"[Upload OK] dialog item '{item}'")
                            page.wait_for_timeout(2500)
                            click_add_to_prompt(page)
                            return True
                    except Exception:
                        pass
        except Exception:
            pass

    print("[Upload FAIL] 모든 업로드 전략 실패.")
    return False


# ---------------------------------------------------------------------------
# Enter prompt (Slate contenteditable)
# ---------------------------------------------------------------------------

def enter_prompt(page, text):
    """Type the prompt into the Slate composer. Return True/False."""
    for i, f in enumerate(page.frames):
        try:
            locs = f.locator(PROMPT_SELECTOR)
            for j in range(locs.count()):
                loc = locs.nth(j)
                if not loc.is_visible():
                    continue
                try:
                    loc.click()
                    page.wait_for_timeout(200)
                    # Clear any residual text, then type (Slate ignores fill()).
                    try:
                        loc.press("Control+A")
                        loc.press("Delete")
                    except Exception:
                        pass
                    page.keyboard.type(text, delay=8)
                    page.wait_for_timeout(300)
                    got = (loc.inner_text() or "").strip()
                    if text[:15] in got:
                        print(f"[Prompt OK] typed via Frame[{i}][{j}]")
                        return True
                    # Fallback: insert_text in one shot
                    page.keyboard.insert_text(text)
                    page.wait_for_timeout(200)
                    if text[:15] in (loc.inner_text() or ""):
                        print(f"[Prompt OK] insert_text Frame[{i}][{j}]")
                        return True
                except Exception as e:
                    print(f"[Prompt WARN] Frame[{i}][{j}]: {str(e)[:80]}")
        except Exception:
            pass
    print("[Prompt FAIL] 프롬프트 입력창을 찾지 못함.")
    return False


# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------

def generate_button(page):
    """Return a locator for the '만들기'(generate) button, or None."""
    selectors = [
        # Korean
        "button:has-text('만들기')", "[aria-label='만들기']",
        # English
        "button:has-text('Create')", "[aria-label='Create']",
        "button:has-text('Generate')", "[aria-label='Generate']",
        # Frames-to-Video specific
        "button:has-text('생성')", "[aria-label='생성']",
    ]
    for sel in selectors:
        for f in page.frames:
            try:
                locs = f.locator(sel)
                for j in range(locs.count()):
                    btn = locs.nth(j)
                    if btn.count() and btn.is_visible():
                        return btn
            except Exception:
                pass
    return None


def is_generate_ready(page, wait_ms=8000):
    """Wait up to wait_ms for the generate button to become enabled."""
    deadline = time.time() + wait_ms / 1000
    while time.time() < deadline:
        btn = generate_button(page)
        if btn is not None:
            try:
                disabled = btn.get_attribute("aria-disabled")
                if disabled not in ("true",) and btn.is_enabled():
                    return True
            except Exception:
                pass
        time.sleep(0.5)
    return False


def click_generate(page):
    """Click the generate button once enabled. Return True/False."""
    if not is_generate_ready(page, wait_ms=10000):
        print("[Generate WARN] 생성 버튼이 활성화되지 않음 (이미지/프롬프트 확인).")
    btn = generate_button(page)
    if btn is None:
        print("[Generate FAIL] 생성 버튼 미발견.")
        return False
    try:
        btn.click(timeout=4000)
        print("[Generate OK] '만들기' 클릭.")
        return True
    except Exception as e:
        # Last resort: Enter key in the composer submits in many builds.
        print(f"[Generate WARN] click 실패({str(e)[:60]}), Enter 시도.")
        try:
            page.keyboard.press("Enter")
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Wait for video and download
# ---------------------------------------------------------------------------

def _harvest_downloaded_file(output_path):
    """Fallback: move the newest .mp4 from DOWNLOAD_DIR to output_path."""
    try:
        candidates = glob.glob(os.path.join(DOWNLOAD_DIR, "*.mp4"))
        if not candidates:
            return False
        newest = max(candidates, key=os.path.getmtime)
        shutil.move(newest, output_path)
        print(f"[Download SUCCESS] (folder fallback) {newest} → {output_path}")
        return True
    except Exception as e:
        print(f"[Download WARN] folder fallback 실패: {str(e)[:120]}")
        return False


def wait_and_download(page, output_path, timeout_seconds=420):
    """Wait for the generated clip, open its menu, and download it."""
    print(f"[Download] 최대 {timeout_seconds}s 동안 생성/다운로드 대기...")

    direct_dl = [
        "button:has-text('다운로드')", "button:has-text('Download')",
        "[aria-label='다운로드']", "[aria-label='Download']",
        "[aria-label*='다운로드']", "[aria-label*='download' i]",
        "a[download]", "[data-testid*='download' i]",
        "button:has-text('내보내기')", "button:has-text('Export')",
    ]
    # menu trigger (per-result "옵션 더보기" / more_vert) then a download item
    more_triggers = [
        "[aria-label*='옵션 더보기']", "[aria-label*='더보기']",
        "[aria-label*='More' i]", "button:has-text('more_vert')",
    ]

    try:
        with page.expect_download(timeout=timeout_seconds * 1000) as dl_info:
            start = time.time()
            clicked = False
            last_log = 0
            while not clicked and (time.time() - start) < (timeout_seconds - 5):
                # (1) direct download buttons
                for sel in direct_dl:
                    for f in page.frames:
                        try:
                            locs = f.locator(sel)
                            for j in range(locs.count()):
                                b = locs.nth(j)
                                if b.is_visible():
                                    b.click()
                                    print(f"[Download] 직접 버튼 클릭: {sel}")
                                    clicked = True
                                    break
                        except Exception:
                            pass
                        if clicked:
                            break
                    if clicked:
                        break

                # (2) hover newest result tile -> more menu -> 다운로드
                if not clicked:
                    for f in page.frames:
                        try:
                            vids = f.locator("video")
                            n = vids.count()
                            if n == 0:
                                continue
                            tile = vids.nth(n - 1)
                            if not tile.is_visible():
                                continue
                            tile.hover()
                            page.wait_for_timeout(400)
                            for mt in more_triggers:
                                try:
                                    mb = f.locator(mt).last
                                    if mb.is_visible(timeout=400):
                                        mb.click()
                                        page.wait_for_timeout(500)
                                        for item in ["text=다운로드", "text=Download"]:
                                            mi = page.locator(item).first
                                            if mi.is_visible(timeout=600):
                                                mi.click()
                                                print("[Download] 메뉴 → 다운로드 클릭")
                                                clicked = True
                                                break
                                except Exception:
                                    pass
                                if clicked:
                                    break
                            # (3) right-click context menu fallback
                            if not clicked:
                                try:
                                    tile.click(button="right")
                                    page.wait_for_timeout(400)
                                    for item in ["text=다운로드", "text=Download"]:
                                        mi = page.locator(item).first
                                        if mi.is_visible(timeout=600):
                                            mi.click()
                                            print("[Download] 컨텍스트 메뉴 다운로드")
                                            clicked = True
                                            break
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        if clicked:
                            break

                if not clicked:
                    elapsed = int(time.time() - start)
                    if elapsed - last_log >= 15:
                        print(f"  ... 생성 대기 중 ({elapsed}s)")
                        # Take a screenshot roughly every 30 seconds for diagnostics
                        if (elapsed // 30) * 30 >= last_log:
                            save_screenshot(page, f"wait_dl_{elapsed}s")
                        last_log = elapsed
                    time.sleep(4)

            if not clicked:
                print("[Download WARN] 다운로드 트리거 미발견 — 다운로드 이벤트만 대기.")

        dl = dl_info.value
        dl.save_as(output_path)
        print(f"[Download SUCCESS] 저장 → {output_path}")
        return True
    except Exception as e:
        print(f"[Download WARN] expect_download 실패({str(e)[:120]}) — 폴더 폴백 시도.")
        return _harvest_downloaded_file(output_path)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def automate_flow(scene_id=None, prompt_file="prompts_for_veo.txt",
                  auto=False, debug_only=False, verify=False, force=False):
    prompts = parse_prompts(prompt_file)
    if not prompts:
        print("[ERROR] No prompts loaded.")
        return

    if scene_id is not None:
        if scene_id not in prompts:
            print(f"[ERROR] Scene {scene_id} not found in {prompt_file}.")
            return
        scenes_to_process = [scene_id]
    else:
        scenes_to_process = sorted(prompts.keys())

    profile_dir = os.path.abspath("assets/chrome_profile")
    os.makedirs(profile_dir, exist_ok=True)
    os.makedirs("assets/videos", exist_ok=True)
    os.makedirs(DEBUG_DIR, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    is_interactive = sys.stdin.isatty() and not (auto or verify)

    print("=" * 60)
    print("  Google Flow Playwright Automator — Omni editor")
    print(f"  URL: {FLOW_BASE}")
    mode = ("DEBUG (dump only)" if debug_only else
            "VERIFY (no generate)" if verify else
            "FULLY AUTOMATIC" if auto else "INTERACTIVE")
    print(f"  MODE: {mode}")
    print("=" * 60)

    succeeded, skipped, failed = [], [], []

    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                channel="chrome",
                headless=False,
                locale="en-US",
                accept_downloads=True,
                downloads_path=DOWNLOAD_DIR,
                ignore_default_args=["--enable-automation"],
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--disable-session-crashed-bubble",
                    "--disable-infobars",
                    "--lang=en-US",
                ],
            )
        except Exception as e:
            print("[ERROR] Browser launch failed.")
            print("다른 Chrome 창이 같은 프로필을 사용 중일 수 있습니다. 모두 닫고 재시도하세요.")
            print(repr(str(e)[:200]))
            return

        page = context.pages[0] if context.pages else context.new_page()

        editor_ok = open_editor(page, is_interactive,
                                timeout_ms=20000 if debug_only else 60000)

        if debug_only:
            dump_frame_tree(page)
            print("\n[DEBUG MODE] 분석 완료.")
            if is_interactive:
                try:
                    input("브라우저를 닫으려면 [Enter]...")
                except Exception:
                    pass
            context.close()
            return

        # -----------------------------------------------------------------
        # Scene processing loop
        # -----------------------------------------------------------------
        for idx, num in enumerate(scenes_to_process):
            image_path = os.path.abspath(f"assets/images/scene_{num}.png")
            output_path = os.path.abspath(f"assets/videos/scene_{num}.mp4")
            prompt_text = prompts[num]

            if not os.path.exists(image_path):
                print(f"\n[SKIP] Image not found: {image_path}")
                skipped.append(num)
                continue

            # Idempotent: don't re-burn credits on clips we already have.
            if (not force) and (not verify) and os.path.exists(output_path) \
                    and os.path.getsize(output_path) > 0:
                print(f"\n[SKIP] 이미 존재함 (--force 로 재생성): {output_path}")
                skipped.append(num)
                continue

            print(f"\n{'='*60}\nScene {num}\n  Image : {image_path}\n"
                  f"  Prompt: {prompt_text[:90]}\n{'='*60}")

            try:
                # Fresh editor for each scene (also re-opens after the first).
                if idx > 0:
                    open_editor(page, is_interactive, timeout_ms=40000)
                    save_screenshot(page, f"scene{num}_00_fresh")

                # Step 1: upload
                print("\n[Step 1] 이미지 업로드...")
                uploaded = upload_image(page, image_path)
                page.wait_for_timeout(1500)
                save_screenshot(page, f"scene{num}_01_upload")

                # Step 2: prompt
                print("\n[Step 2] 프롬프트 입력...")
                prompted = enter_prompt(page, prompt_text)
                page.wait_for_timeout(800)
                save_screenshot(page, f"scene{num}_02_prompt")

                ready = is_generate_ready(page, wait_ms=8000)
                print(f"[State] upload={uploaded} prompt={prompted} "
                      f"generate_ready={ready}")

                if verify:
                    if uploaded and prompted and ready:
                        print(f"[VERIFY OK] Scene {num}: 업로드+프롬프트+생성버튼 활성 "
                              f"— 100% 자동 동작 확인 (생성은 건너뜀).")
                        succeeded.append(num)
                    else:
                        print(f"[VERIFY FAIL] Scene {num}: "
                              f"upload={uploaded} prompt={prompted} ready={ready}")
                        failed.append(num)
                    continue

                # Step 3: generate
                print("\n[Step 3] 생성(만들기) 클릭...")
                click_generate(page)
                save_screenshot(page, f"scene{num}_03_generate")

                # Step 4: download
                print("\n[Step 4] 영상 생성 대기 및 다운로드...")
                if wait_and_download(page, output_path, timeout_seconds=420):
                    save_screenshot(page, f"scene{num}_04_done")
                    print(f"[OK] Scene {num} 완료 → {output_path}")
                    succeeded.append(num)
                else:
                    print(f"[FAIL] Scene {num} 다운로드 실패.")
                    failed.append(num)

            except Exception as e:
                print(f"\n[ERROR] Scene {num}: {e}")
                traceback.print_exc()
                save_screenshot(page, f"error_scene{num}")
                failed.append(num)

        # -----------------------------------------------------------------
        # Summary
        # -----------------------------------------------------------------
        print(f"\n{'='*60}")
        print("  실행 요약")
        print(f"  성공 : {succeeded}")
        print(f"  스킵 : {skipped}")
        print(f"  실패 : {failed}")
        print(f"{'='*60}")

        if is_interactive:
            try:
                input("종료하려면 [Enter]...")
            except Exception:
                pass
        context.close()

    return {"succeeded": succeeded, "skipped": skipped, "failed": failed}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Google Flow Playwright Automator — Omni editor (100% browser)"
    )
    parser.add_argument("--scene", type=int, help="처리할 씬 번호 (생략 시 전체)")
    parser.add_argument("--auto", action="store_true",
                        help="완전 자동 모드 (수동 입력 대기 없음)")
    parser.add_argument("--verify", action="store_true",
                        help="업로드+프롬프트까지만 검증하고 생성은 건너뜀 (크레딧 미소모)")
    parser.add_argument("--force", action="store_true",
                        help="이미 mp4가 있어도 재생성 (기본은 존재 시 스킵)")
    parser.add_argument("--debug", action="store_true",
                        help="에디터 진입 후 DOM/프레임 구조만 덤프하고 종료")
    parser.add_argument("--prompts", default="prompts_for_veo.txt",
                        help="프롬프트 파일 경로 (기본 prompts_for_veo.txt)")
    args = parser.parse_args()

    automate_flow(
        scene_id=args.scene,
        prompt_file=args.prompts,
        auto=args.auto,
        verify=args.verify,
        force=args.force,
        debug_only=args.debug,
    )
