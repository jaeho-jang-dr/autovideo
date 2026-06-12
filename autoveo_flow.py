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
    const r = im.getBoundingClientRect();
    if (r.width<200 || r.height<120) continue;
    if (r.width>1200 || r.height>900) continue;
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
    const r = im.getBoundingClientRect();
    if (r.width<200 || r.height<120) continue;
    if (r.width>1200 || r.height>900) continue;
    out.push({x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2), left:Math.round(r.x)});
  }
  out.sort((a,b)=>a.left-b.left);
  return out;
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
    page.goto(BASE, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3500)
    if "accounts.google.com" in page.url:
        log("로그인 필요 — labs.google 복귀 대기(90s)")
        try:
            page.wait_for_url("**/labs.google/**", timeout=90000)
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


def wait_image(page, timeout=120):
    """Image gen takes ~35-40s; wait for the result poster."""
    page.wait_for_timeout(25000)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if page.evaluate(BIG_MEDIA_IMG_JS):
            page.wait_for_timeout(1500)
            return True
        time.sleep(3)
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



def try_download_leftmost(page, tmp_path):
    """Download the left-most (newest = video) poster's 원본 MP4 to tmp_path.
    Returns True only if the saved file is a real MP4 (i.e. the clip is done)."""
    posters = page.evaluate(POSTERS_JS)
    if not posters:
        return False
    target = posters[0]                       # left-most = newest = the video
    try:
        with page.expect_download(timeout=60000) as dl:
            if not open_tile_menu(page, target):
                raise RuntimeError("tile ⋮ open fail")
            click_text(page, "다운로드")
            page.wait_for_timeout(800)
            (click_text(page, "원본 크기") or click_text(page, "720p")
             or click_text(page, "원본"))
        d = dl.value
        d.save_as(tmp_path)
    except Exception as e:
        log(f"  download try 실패: {str(e)[:90]}")
        return False
    if is_mp4(tmp_path):
        return True
    try:
        os.remove(tmp_path)                   # JPEG poster -> still rendering
    except Exception:
        pass
    return False


def make_video(page, out_path, motion_prompt, n, budget_s=360):
    """Generate the clip, then download-and-verify until a real MP4 arrives."""
    fill_prompt(page, motion_prompt)
    if not generate(page):
        log("[ERR] 동영상 생성 버튼 클릭 실패")
        return False
    log("동영상 생성 중... (이미지보다 오래 걸림)")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)   # pre-create target dir
    tmp = os.path.join(DL_DIR, f"_scene_{n}.bin")
    page.wait_for_timeout(110000)             # min wait — Veo rarely finishes faster
    deadline = time.time() + budget_s
    while time.time() < deadline:
        shot(page, f"s{n}_vid_poll")
        if try_download_leftmost(page, tmp):
            shutil.move(tmp, out_path)
            return True
        log(f"  ... 아직 렌더링 중, 20s 후 재시도 ({int(deadline-time.time())}s 남음)")
        time.sleep(20)
    return False


def make_scene(page, n, image_prompt, motion_prompt, force=False):
    global OUT_DIR
    out_path = os.path.join(OUT_DIR, f"scene_{n}.mp4")
    if (not force) and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        log(f"[SKIP] 존재함: {out_path}")
        return True
    log(f"=== Scene {n} ===")
    if not open_new_project(page):
        log("[ERR] 프로젝트/컴포저 진입 실패")
        return False
    shot(page, f"s{n}_00_editor")

    set_image_mode(page)
    fill_prompt(page, image_prompt)
    if not generate(page):
        log("[ERR] 이미지 생성 버튼 클릭 실패")
        return False
    log("이미지 생성 중... (~35-40s)")
    if not wait_image(page):
        log("[ERR] 이미지 미생성(timeout)")
        shot(page, f"s{n}_img_timeout")
        return False
    shot(page, f"s{n}_01_image")

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

    todo = [args.scene] if args.scene else sorted(scenes)

    ok, fail = [], []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
            accept_downloads=True, downloads_path=DL_DIR,
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                  "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for n in todo:
            if n not in scenes:
                continue
            try:
                (ok if make_scene(page, n, *scenes[n], force=args.force) else fail).append(n)
            except Exception as e:
                log(f"[ERR] Scene {n}: {e}")
                traceback.print_exc()
                shot(page, f"s{n}_error")
                fail.append(n)
        log(f"완료 — 성공 {ok} / 실패 {fail}")
        ctx.close()


if __name__ == "__main__":
    main()
