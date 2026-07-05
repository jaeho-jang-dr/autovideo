# -*- coding: utf-8 -*-
"""이미 업로드된 동영상(초안)의 공개 상태를 편집페이지에서 변경+저장.
사용: python yt_setvis.py <VIDEO_ID> <unlisted|public|private>"""
import sys, os, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
VIS = sys.argv[2] if len(sys.argv) > 2 else "unlisted"
VISNAME = {"unlisted": "일부 공개", "private": "비공개", "public": "공개"}[VIS]
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)
def shot(pg, n):
    try: pg.screenshot(path=f"{SH}/sv_{n}.png")
    except Exception: pass

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000); shot(pg, "1edit")
    # 공개 상태 드롭다운 열기 (우측 패널의 현재 상태 트리거)
    opened = False
    for sel in ["#visibility-container ytcp-dropdown-trigger", "#visibility-container",
                "ytcp-video-visibility-select ytcp-dropdown-trigger",
                "ytcp-dropdown-trigger:has-text('비공개')",
                "tp-yt-paper-dropdown-menu:has-text('비공개')",
                "#child-input:has-text('비공개')"]:
        try:
            pg.locator(sel).first.click(timeout=4000); opened = True; log("드롭다운 열림 "+sel); break
        except Exception: pass
    pg.wait_for_timeout(2500); shot(pg, "2dropdown")
    # 라디오 선택
    picked = False
    try:
        pg.get_by_role("radio", name=VISNAME, exact=True).first.click(timeout=6000); picked = True; log(VISNAME+" 라디오")
    except Exception:
        for sel in [f"tp-yt-paper-radio-button:has-text('{VISNAME}')",
                    f"#radioContainer :text('{VISNAME}')", f":text('{VISNAME}')"]:
            try: pg.locator(sel).first.click(timeout=4000); picked = True; log(VISNAME+" "+sel); break
            except Exception: pass
    pg.wait_for_timeout(1500); shot(pg, "3picked")
    # 저장 (상단 우측)
    saved = False
    for sel in ["#save", "ytcp-button#save", "ytcp-button:has-text('저장')", "#done-button"]:
        try:
            b = pg.locator(sel).first; b.wait_for(state="visible", timeout=6000)
            try: b.click(timeout=4000, force=True)
            except Exception: pg.eval_on_selector(sel, "el=>{(el.querySelector('button')||el).click();}")
            saved = True; log("저장 "+sel); break
        except Exception: pass
    pg.wait_for_timeout(5000); shot(pg, "4saved")
    # 확인
    body = ""
    try: body = pg.inner_text("body")
    except Exception: pass
    log("STATE_HAS_"+VISNAME.replace(' ','')+"="+str(VISNAME in body))
    log("SETVIS_DONE VID="+VID+" -> "+VISNAME+(" OK" if saved and picked else " CHECK"))
    pg.wait_for_timeout(2000); ctx.close()
print("END")
