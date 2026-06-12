"""
flow_probe.py — Interactive-journey diagnostic for Google Flow.

Walks the REAL navigation path (dashboard -> new project -> editor),
dismissing cookie/announcement overlays, and deep-scans the editor DOM
(light + shadow + iframes) for file inputs, prompt fields and buttons.

Read-only: never uploads / generates / downloads.
"""

import os
import json
from playwright.sync_api import sync_playwright

BASE = "https://labs.google/fx/tools/flow"
DEBUG_DIR = "debug"

DEEP_SCAN_JS = r"""
() => {
  const out = [];
  const interesting = (el) => {
    const tag = el.tagName;
    if (['INPUT','TEXTAREA','BUTTON','SELECT','A','LABEL'].includes(tag)) return true;
    const ce = el.getAttribute && el.getAttribute('contenteditable');
    if (ce === 'true' || ce === 'plaintext-only') return true;
    const role = el.getAttribute && el.getAttribute('role');
    if (['button','textbox','tab','menuitem'].includes(role)) return true;
    return false;
  };
  const vis = (el) => { const r = el.getBoundingClientRect();
    return r.width>0 && r.height>0; };
  const desc = (el, inShadow) => ({
    tag: el.tagName, type: el.getAttribute('type')||'',
    id: el.id||'', cls: (el.className&&el.className.toString?el.className.toString():'').slice(0,70),
    text: (el.textContent||'').trim().slice(0,50),
    ph: el.getAttribute('placeholder')||'', aria: el.getAttribute('aria-label')||'',
    testid: el.getAttribute('data-testid')||'', role: el.getAttribute('role')||'',
    ce: el.getAttribute('contenteditable')||'', accept: el.getAttribute('accept')||'',
    visible: vis(el), inShadow: inShadow,
  });
  const walk = (root, inShadow) => {
    let nodes; try { nodes = root.querySelectorAll('*'); } catch(e){ return; }
    for (const el of nodes) {
      if (interesting(el)) out.push(desc(el, inShadow));
      if (el.shadowRoot) walk(el.shadowRoot, true);
    }
  };
  walk(document, false);
  return { elements: out, url: location.href, title: document.title };
}
"""


def shot(page, name):
    os.makedirs(DEBUG_DIR, exist_ok=True)
    p = os.path.abspath(f"{DEBUG_DIR}/{name}.png")
    try:
        page.screenshot(path=p, full_page=False); print(f"[shot] {p}")
    except Exception as e:
        print(f"[shot fail] {e}")


def dismiss_overlays(page, rounds=4):
    labels = [
        "button:has-text('Agree')", "button:has-text('동의')",
        "button:has-text('No thanks')", "button:has-text('Accept all')",
        "button:has-text('시작하기')", "button:has-text('Get started')",
        "button:has-text('Got it')", "button:has-text('확인')",
        "button:has-text('Continue')", "button:has-text('Skip')",
        "button:has-text('Close')", "[aria-label='Close']", "[aria-label='닫기']",
    ]
    for _ in range(rounds):
        hit = False
        for sel in labels:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=500):
                    loc.click(timeout=2000, force=True)
                    print(f"[dismiss] {sel}")
                    hit = True
                    page.wait_for_timeout(900)
            except Exception:
                pass
        if not hit:
            break


def scan(page, tag):
    print(f"\n########## SCAN: {tag}  url={page.url}")
    for i, f in enumerate(page.frames):
        try:
            data = f.evaluate(DEEP_SCAN_JS)
        except Exception as e:
            print(f"  Frame[{i}] eval-fail {str(e)[:60]}")
            continue
        els = data.get("elements", [])
        if not els:
            continue
        print(f"  Frame[{i}] {f.url[:70]}")
        for e in els:
            label = e['aria'] or e['ph'] or e['testid'] or e['text']
            if not label:
                continue
            if e['tag'] in ('INPUT', 'TEXTAREA') or e['ce'] or \
               e['role'] in ('textbox', 'button', 'tab', 'menuitem') or \
               e['tag'] in ('BUTTON', 'A'):
                fl = "S" if e['inShadow'] else " "
                v = "v" if e['visible'] else "."
                print(f"    [{fl}{v}] {e['tag']:<8} t={e['type']:<7} "
                      f"r={e['role']:<7} testid='{e['testid'][:20]}' "
                      f"ph='{e['ph'][:18]}' aria='{e['aria'][:24]}' "
                      f"txt='{e['text'][:26]}'")


def click_first_visible(page, selectors, label):
    for sel in selectors:
        for f in page.frames:
            try:
                locs = f.locator(sel)
                for j in range(min(locs.count(), 5)):
                    loc = locs.nth(j)
                    if loc.is_visible(timeout=400):
                        loc.click(timeout=3000)
                        print(f"[click {label}] {sel}")
                        return True
            except Exception:
                pass
    print(f"[click {label} FAIL] none of {len(selectors)} selectors visible")
    return False


def main():
    profile_dir = os.path.abspath("assets/chrome_profile")
    os.makedirs(DEBUG_DIR, exist_ok=True)
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir, channel="chrome", headless=False,
            locale="en-US", ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                  "--no-first-run", "--disable-session-crashed-bubble", "--lang=en-US"])
        page = context.pages[0] if context.pages else context.new_page()

        print(f"[nav] {BASE}")
        page.goto(BASE, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(4000)
        if "accounts.google.com" in page.url:
            try:
                page.wait_for_url("**/labs.google/**", timeout=60000)
            except Exception:
                pass
        dismiss_overlays(page)
        page.wait_for_timeout(1500)
        shot(page, "j01_dashboard")
        scan(page, "DASHBOARD")

        # Try to open the editor: New project tile / button
        opened = click_first_visible(page, [
            "button:has-text('새 프로젝트')", "button:has-text('New project')",
            "a:has-text('새 프로젝트')", "a:has-text('New project')",
            "button:has-text('프로젝트')", "button:has-text('Project')",
            "[aria-label*='프로젝트']", "[aria-label*='project' i]",
            "button:has-text('Try Omni now')", "button:has-text('새 만들기')",
            "button:has-text('만들기')", "button:has-text('Create')",
        ], "new-project")
        page.wait_for_timeout(5000)
        dismiss_overlays(page)
        page.wait_for_timeout(1500)
        shot(page, "j02_after_newproject")
        scan(page, "AFTER-NEW-PROJECT")

        # If a project list exists, try opening the first project tile too
        # (in case New project wasn't found, an existing project opens the editor)
        if not opened:
            click_first_visible(page, [
                "[class*='project' i] a", "[class*='project' i] button",
                "[class*='tile' i]", "[class*='card' i] a",
                "main a[href*='project']",
            ], "existing-project")
            page.wait_for_timeout(5000)
            dismiss_overlays(page)
            shot(page, "j03_after_existing")
            scan(page, "AFTER-EXISTING-PROJECT")

        # Save final HTML for offline grep
        try:
            with open(os.path.join(DEBUG_DIR, "probe_editor.html"), "w",
                      encoding="utf-8") as fh:
                fh.write(page.content())
            print("[html] debug/probe_editor.html saved")
        except Exception as e:
            print(f"[html fail] {e}")

        shot(page, "j99_final")
        print("\n[done] holding 3s")
        page.wait_for_timeout(3000)
        context.close()


if __name__ == "__main__":
    main()
