# -*- coding: utf-8 -*-
"""동영상 업로드(CDP 9222 재사용, 로그인된 디버그 크롬). 일부공개 기본 + 썸네일 + AI=예 + 교육 + video_id 캡처.
사용: python upload_cdp.py <video> <desc.txt> "<title>" <thumb|none> [unlisted|private|public]"""
import sys, os, time, re
from playwright.sync_api import sync_playwright
VIDEO = os.path.abspath(sys.argv[1]); DESC = open(sys.argv[2], encoding="utf-8").read()
TITLE = sys.argv[3]
THUMB = None if sys.argv[4].lower() == "none" else os.path.abspath(sys.argv[4])
VIS = sys.argv[5] if len(sys.argv) > 5 else "unlisted"
VISNAME = {"unlisted": "일부 공개", "private": "비공개", "public": "공개"}[VIS]
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)
def shot(pg, n):
    try: pg.screenshot(path=SH + f"/uc_{n}.png")
    except Exception: pass
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pg = ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto("https://studio.youtube.com/", wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
    try:
        op = False
        for sel in ["#upload-icon", "ytcp-icon-button#upload-icon", "ytcp-button:has-text('동영상 업로드')", "text=동영상 업로드"]:
            try: pg.locator(sel).first.click(timeout=4000); op = True; break
            except Exception: pass
        if not op:
            pg.locator("ytcp-button:has-text('만들기')").first.click(timeout=4000); pg.wait_for_timeout(1200)
            pg.get_by_text("동영상 업로드", exact=False).first.click(timeout=4000); op = True
        pg.wait_for_timeout(3500)
        # ★ 4K(>50MB) 업로드: Playwright 파일전송(원격 CDP 50MB 제한) 대신 CDP DOM.setFileInputFiles로 직접 지정
        cdp = ctx.new_cdp_session(pg)
        findjs = ("(()=>{function f(r){let i=r.querySelector('input[type=file]');if(i)return i;"
                  "for(const e of r.querySelectorAll('*'))if(e.shadowRoot){const x=f(e.shadowRoot);if(x)return x;}return null;}return f(document);})()")
        oid = None
        for _ in range(20):
            ev = cdp.send("Runtime.evaluate", {"expression": findjs})
            oid = ev.get("result", {}).get("objectId")
            if oid: break
            pg.wait_for_timeout(1000)
        if not oid:
            raise RuntimeError("file input 못 찾음")
        bnid = cdp.send("DOM.describeNode", {"objectId": oid})["node"]["backendNodeId"]
        cdp.send("DOM.setFileInputFiles", {"files": [VIDEO], "backendNodeId": bnid})
        log("파일선택 OK (CDP setFileInputFiles, backendNodeId)")
    except Exception as e:
        log("파일선택 실패 " + str(e)[:120]); shot(pg, "err"); sys.exit(1)
    pg.wait_for_timeout(9000)
    try:
        tb = pg.locator("[contenteditable='true'][aria-label*='제목']").first
        tb.click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(400)
        pg.keyboard.insert_text(TITLE); log("제목")
    except Exception as e: log("제목 실패 " + str(e)[:70])
    try:
        db = pg.locator("[contenteditable='true'][aria-label*='설명해']").first
        db.click(); pg.wait_for_timeout(300); pg.keyboard.insert_text(DESC); log("설명")
    except Exception as e: log("설명 실패 " + str(e)[:70])
    if THUMB:
        try:
            pg.locator("ytcp-thumbnail-uploader input[type=file]").first.set_input_files(THUMB); pg.wait_for_timeout(3000); log("썸네일 업로드")
        except Exception as e: log("썸네일 실패 " + str(e)[:70])
    VID = ""
    try:
        for sel in ["ytcp-uploads-dialog a[href*='youtu.be/']", "ytcp-uploads-dialog a[href*='/watch?v=']", "ytcp-uploads-dialog a[href*='/video/']"]:
            try:
                href = pg.locator(sel).first.get_attribute("href", timeout=2000)
                m = re.search(r"(?:youtu\.be/|v=|/video/)([A-Za-z0-9_-]{9,})", href or "")
                if m: VID = m.group(1); break
            except Exception: pass
    except Exception: pass
    log("VIDEO_ID=" + (VID or "미확인")); shot(pg, "1details")
    try:
        r = pg.get_by_role("radio", name="아동용이 아닙니다", exact=False).first
        r.scroll_into_view_if_needed(); pg.wait_for_timeout(300); r.click(); log("아동용아님")
    except Exception as e: log("아동용 실패 " + str(e)[:60])
    try: pg.locator("ytcp-button:has-text('자세히 보기'),#toggle-button").first.click(timeout=6000); pg.wait_for_timeout(1800); log("자세히보기")
    except Exception as e: log("자세히 실패 " + str(e)[:50])
    try:
        r = pg.get_by_role("radio", name="AI가 사용되었습니다", exact=False).first
        r.scroll_into_view_if_needed(); pg.wait_for_timeout(300); r.click(); log("AI예")
    except Exception as e: log("AI 실패 " + str(e)[:60])
    try:
        for t in ["인물/블로그", "엔터테인먼트", "카테고리 선택"]:
            try:
                el = pg.get_by_text(t, exact=True).first
                if el.is_visible(timeout=1500): el.scroll_into_view_if_needed(); el.click(); pg.wait_for_timeout(1000); break
            except Exception: pass
        pg.get_by_text("교육", exact=True).first.click(timeout=4000); log("카테고리 교육"); pg.keyboard.press("Escape"); pg.wait_for_timeout(1000)
    except Exception as e: log("카테고리 스킵 " + str(e)[:50]); pg.keyboard.press("Escape")
    shot(pg, "2set")
    for i in range(3):
        try: pg.locator("#next-button, ytcp-button:has-text('다음')").first.click(timeout=8000); pg.wait_for_timeout(2500)
        except Exception as e: log(f"다음{i+1} 실패 " + str(e)[:40])
    shot(pg, "3vis")
    try:
        pg.get_by_role("radio", name=VISNAME, exact=True).first.click(timeout=6000); log(VISNAME)
    except Exception:
        try: pg.get_by_text(VISNAME, exact=True).first.click(timeout=4000); log(VISNAME + "(text)")
        except Exception as e2: log("공개상태 실패 " + str(e2)[:50])
    pg.wait_for_timeout(1500)
    saved = False
    try:
        btn = pg.locator("#done-button").first
        btn.wait_for(state="visible", timeout=12000)
        for attempt in range(3):
            try: btn.click(timeout=5000, force=True); saved = True; break
            except Exception:
                try: pg.eval_on_selector("#done-button", "el=>{const b=el.querySelector('button')||el;b.click();}"); saved = True; break
                except Exception: pg.wait_for_timeout(1500)
        log("저장/게시" if saved else "저장 클릭 실패")
    except Exception as e: log("저장 실패 " + str(e)[:70])
    pg.wait_for_timeout(6000); shot(pg, "4done")
    dl = time.time() + 300
    while time.time() < dl:
        pg.wait_for_timeout(10000)
        try: body = pg.inner_text("body")
        except Exception: body = ""
        if any(k in body for k in ["처리 중", "업로드 완료", "처리 완료", "SD 처리", "동영상 처리"]): break
    shot(pg, "5uploaded")
    log("VIDEO_ID_FINAL=" + (VID or "미확인")); log("UPLOAD_DONE")
print("END")
