"""
flow_driver.py — keep ONE logged-in Flow browser open and drive it by commands.

Claude drops command files into debug/cmd/<n>.txt; this process executes them in
order against the live page, saving debug/_live.png (+ _live.json) and logging to
debug/_drv.log. Lets Claude "click around" + watch generation slowly, confirm via
screenshots, and download — without relaunching.

Command file format (one line): VERB|arg1|arg2
  newproject               open a fresh project from the dashboard
  goto|<url>               navigate
  clicktext|<txt>|<ymin>   click first visible button/role=button containing txt (y>=ymin)
  clickxy|<x>|<y>          physical mouse click
  hover|<x>|<y>            physical mouse hover
  type|<text>              type into focused element
  fillprompt|<text>        focus the composer textbox and type
  key|<KeyName>            press a key (Escape, Enter, ...)
  wait|<seconds>           sleep, then refresh screenshot/dump (watch generation)
  imgstatus                log whether a finished image poster is present
  vidstatus                log whether a finished video tile (play_circle+poster) is present
  dlvideo|<abs_path>       download the finished video tile to abs_path (pre-creates its dir)
  dump / shot              refresh dump / screenshot only
  quit                     close browser and exit
After every command: debug/_live.png + debug/_live.json are refreshed.
"""
import os
import sys
import json
import time
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
CMD_DIR = os.path.join(DBG, "cmd")
PROMPT_SELECTOR = "div[role='textbox'][contenteditable='true']"

SCAN_JS = r"""
() => {
  const out = [];
  const want = (el) => {
    const t = el.tagName;
    if (['INPUT','TEXTAREA','BUTTON','A','SELECT','LABEL','LI','VIDEO','IMG'].includes(t)) return true;
    const ce = el.getAttribute && el.getAttribute('contenteditable');
    if (ce === 'true' || ce === 'plaintext-only') return true;
    const r = el.getAttribute && el.getAttribute('role');
    return ['button','textbox','tab','menuitem','menuitemradio','option','radio','switch','progressbar'].includes(r);
  };
  const walk = (root) => {
    let ns; try { ns = root.querySelectorAll('*'); } catch(e){ return; }
    for (const el of ns) {
      if (want(el)) {
        const rc = el.getBoundingClientRect();
        if (rc.width>0 && rc.height>0) {
          out.push({tag: el.tagName, role: el.getAttribute('role')||'',
            aria: el.getAttribute('aria-label')||'', testid: el.getAttribute('data-testid')||'',
            src: (el.getAttribute('src')||'').slice(0,60),
            text: (el.textContent||'').trim().slice(0,70),
            x: Math.round(rc.x), y: Math.round(rc.y),
            w: Math.round(rc.width), h: Math.round(rc.height)});
        }
      }
      if (el.shadowRoot) walk(el.shadowRoot);
    }
  };
  walk(document);
  return out;
}
"""

BIG_MEDIA_IMG_JS = r"""
() => {
  let best=null, area=0;
  for (const im of document.querySelectorAll('img')) {
    const s = im.getAttribute('src')||'';
    if (!/media\.getMediaUrlRedirect|googleusercontent\.com\/(?:fife|gen)/.test(s)) continue;
    const r = im.getBoundingClientRect();
    if (r.width<250 || r.height<150) continue;
    const a=r.width*r.height;
    if (a>area){area=a; best={x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2), w:Math.round(r.width), h:Math.round(r.height)};}
  }
  return best;
}
"""

# finished video tile: play_circle overlay AND a real poster img
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
    if (a<area){area=a; best={x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2), w:Math.round(r.width), h:Math.round(r.height)};}
  }
  return best;
}
"""

MORE_NEAR_JS = r"""
(t) => {
  let best=null, bd=1e9;
  for (const b of document.querySelectorAll('button')) {
    const tx=(b.textContent||'');
    if (!(tx.includes('더 생성하기') || tx.includes('more_vert'))) continue;
    const r=b.getBoundingClientRect();
    if (r.y<60 || r.width<=0 || r.height<=0) continue;
    const cx=r.x+r.width/2, cy=r.y+r.height/2;
    const d=Math.hypot(cx-t.x, cy-t.y);
    if (d<bd){bd=d; best={x:Math.round(cx), y:Math.round(cy)};}
  }
  return best;
}
"""


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        with open(os.path.join(DBG, "_drv.log"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def shot(page):
    try:
        page.screenshot(path=os.path.abspath(os.path.join(DBG, "_live.png")))
    except Exception as e:
        log(f"shot fail: {e}")


def dump(page):
    data = []
    for fr in page.frames:
        try:
            els = fr.evaluate(SCAN_JS)
        except Exception:
            continue
        if els:
            data.append({"url": fr.url, "els": els})
    with open(os.path.join(DBG, "_live.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


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
                    if ymin is not None and (not box or box["y"] < float(ymin)):
                        continue
                    loc.click(timeout=timeout)
                    log(f"clicktext OK '{t}' via {sel}")
                    return True
        except Exception:
            pass
    log(f"clicktext MISS '{t}'")
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


def upload(page, image_path):
    """Inject an existing image into the hidden file input across all frames.
    Logs which frame/index accepted it, then tries to confirm via the
    '프롬프트에 추가'/'Add to prompt'/'Add media' button if one appears."""
    image_path = os.path.abspath(image_path)
    if not os.path.exists(image_path):
        log(f"upload: file missing {image_path}")
        return False
    done = False
    for i, fr in enumerate(page.frames):
        try:
            inputs = fr.locator("input[type='file']")
            for j in range(inputs.count()):
                try:
                    inputs.nth(j).set_input_files(image_path, timeout=5000)
                    log(f"upload OK set_input_files frame[{i}][{j}] {image_path}")
                    done = True
                    break
                except Exception as e:
                    log(f"upload try frame[{i}][{j}]: {str(e)[:70]}")
        except Exception:
            pass
        if done:
            break
    if not done:
        log("upload: no file input accepted the image")
        return False
    page.wait_for_timeout(2500)
    # Best-effort confirm (the new uploaded ingredient may need a confirm click)
    for t in ("프롬프트에 추가", "Add to prompt", "추가", "Add"):
        if click_text(page, t):
            log(f"upload: confirmed via '{t}'")
            break
    page.wait_for_timeout(1500)
    return True


def animate(page):
    """Hover the largest generated/uploaded image tile -> its ⋮ menu ->
    '애니메이션 적용' so the image becomes the first frame of a video."""
    center = page.evaluate(BIG_MEDIA_IMG_JS)
    if not center:
        log("animate: no big image tile found")
        return False
    log(f"animate: tile center {center}")
    if not open_tile_menu(page, center):
        log("animate: tile ⋮ menu open fail")
        return False
    ok = (click_text(page, "애니메이션 적용") or click_text(page, "애니메이션")
          or click_text(page, "Animate"))
    log(f"animate: 애니메이션 적용 -> {ok}")
    return ok


def dlvideo(page, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tile = page.evaluate(VIDEO_DONE_JS)
    if not tile:
        log("dlvideo: 완성 영상 타일 미발견")
        return False
    try:
        with page.expect_download(timeout=90000) as dl:
            if not open_tile_menu(page, tile):
                raise RuntimeError("tile menu open fail")
            click_text(page, "다운로드")
            page.wait_for_timeout(800)
            (click_text(page, "원본 크기") or click_text(page, "720p")
             or click_text(page, "원본"))
        d = dl.value
        d.save_as(out_path)
        log(f"dlvideo OK -> {out_path}")
        return True
    except Exception as e:
        log(f"dlvideo FAIL: {str(e)[:140]}")
        return False


def do(page, parts):
    verb = parts[0]
    if verb == "newproject":
        if "/project/" not in page.url:
            click_text(page, "새 프로젝트") or click_text(page, "New project")
            page.wait_for_timeout(4000)
            dismiss(page)
    elif verb == "goto":
        page.goto(parts[1], wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        dismiss(page)
    elif verb == "clicktext":
        ymin = parts[2] if len(parts) > 2 and parts[2] != "" else None
        click_text(page, parts[1], ymin)
    elif verb == "clickxy":
        page.mouse.click(float(parts[1]), float(parts[2]))
        log(f"clickxy {parts[1]},{parts[2]}")
    elif verb == "hover":
        page.mouse.move(float(parts[1]), float(parts[2]))
        log(f"hover {parts[1]},{parts[2]}")
    elif verb == "type":
        page.keyboard.type(parts[1], delay=5)
        log("type done")
    elif verb == "fillprompt":
        b = page.locator(PROMPT_SELECTOR).first
        b.click()
        page.wait_for_timeout(150)
        try:
            b.press("Control+A"); b.press("Delete")
        except Exception:
            pass
        page.keyboard.type(parts[1], delay=4)
        log("fillprompt done")
    elif verb == "key":
        page.keyboard.press(parts[1])
        log(f"key {parts[1]}")
    elif verb == "wait":
        secs = min(float(parts[1]), 200)
        log(f"wait {secs}s ...")
        page.wait_for_timeout(int(secs * 1000))
    elif verb == "imgstatus":
        r = page.evaluate(BIG_MEDIA_IMG_JS)
        log(f"imgstatus: {'DONE '+str(r) if r else 'none'}")
    elif verb == "vidstatus":
        r = page.evaluate(VIDEO_DONE_JS)
        log(f"vidstatus: {'DONE '+str(r) if r else 'none(생성중/없음)'}")
    elif verb == "upload":
        upload(page, parts[1])
    elif verb == "animate":
        animate(page)
    elif verb == "dlvideo":
        dlvideo(page, parts[1])
    elif verb in ("dump", "shot"):
        pass
    else:
        log(f"unknown verb {verb}")


def main():
    os.makedirs(CMD_DIR, exist_ok=True)
    os.makedirs(DL_DIR, exist_ok=True)
    open(os.path.join(DBG, "_drv.log"), "w", encoding="utf-8").close()
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
            accept_downloads=True, downloads_path=DL_DIR,
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                  "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(BASE, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3500)
        dismiss(page)
        if "/project/" not in page.url:
            click_text(page, "새 프로젝트") or click_text(page, "New project")
            page.wait_for_timeout(4000)
            dismiss(page)
        for _ in range(40):
            try:
                if page.locator(PROMPT_SELECTOR).first.is_visible(timeout=500):
                    break
            except Exception:
                pass
            time.sleep(0.5)
        shot(page)
        dump(page)
        log(f"READY url={page.url}")

        nxt = 1
        while True:
            f = os.path.join(CMD_DIR, f"{nxt}.txt")
            if not os.path.exists(f):
                time.sleep(0.4)
                continue
            try:
                cmd = open(f, "r", encoding="utf-8").read().strip()
            except Exception:
                time.sleep(0.2)
                continue
            log(f"CMD {nxt}: {cmd}")
            parts = cmd.split("|")
            if parts[0] == "quit":
                shot(page)
                open(os.path.join(CMD_DIR, f"{nxt}.done"), "w").write("ok")
                break
            try:
                do(page, parts)
            except Exception as e:
                log(f"ERR {nxt}: {e}")
            page.wait_for_timeout(700)
            shot(page)
            try:
                dump(page)
            except Exception:
                pass
            open(os.path.join(CMD_DIR, f"{nxt}.done"), "w").write("ok")
            nxt += 1

        ctx.close()
        log("CLOSED")


if __name__ == "__main__":
    main()
