# -*- coding: utf-8 -*-
"""제목·설명 입력 견고판 — 위치로 번역칸 잡기 + 클립보드 붙여넣기 + 지우기 + 검증 + 재시도.
사용: python meta_robust.py <VIDEO_ID> <UI언어명> <DB언어코드>"""
import sys, os, sqlite3, time
from playwright.sync_api import sync_playwright
try:
    import pyperclip; HASCLIP = True
except Exception: HASCLIP = False
VID, UILANG, DBLANG = sys.argv[1], sys.argv[2], sys.argv[3]
def log(m): print(m, flush=True)
c = sqlite3.connect("channel/content.db"); cur = c.cursor()
row = cur.execute("SELECT title,description FROM video_localizations WHERE video_id=? AND lang=?", (VID, DBLANG)).fetchone()
c.close()
if not row: log("DB 번역 없음 " + DBLANG); sys.exit(1)
TITLE, DESC = row
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pg = None
    for p in ctx.pages:
        if "studio.youtube.com" in p.url: pg = p
    if pg is None: pg = ctx.pages[-1] if ctx.pages else ctx.new_page()
    pg.set_default_timeout(15000)
    if "/translations" not in pg.url or VID not in pg.url:
        pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded"); time.sleep(7)
    # 언어행 × '제목 및 설명' 셀 클릭
    lb = pg.get_by_text(UILANG, exact=True).first.bounding_box()
    hx = None
    for h in pg.get_by_text("제목 및 설명", exact=True).all():
        bb = h.bounding_box()
        if bb: hx = bb["x"] + bb["width"] / 2; break
    pg.mouse.click(hx, lb["y"] + lb["height"] / 2); time.sleep(5)
    # 오른쪽(번역) textarea들: y 순으로 정렬 → [0]=제목, [1]=설명
    def right_fields():
        tas = pg.locator("textarea"); out = []
        for i in range(tas.count()):
            bb = tas.nth(i).bounding_box()
            if bb and bb["x"] > 900: out.append((bb["y"], tas.nth(i)))
        out.sort(key=lambda x: x[0])
        return [t for _, t in out]
    # 편집기 뜰 때까지 대기
    for _ in range(10):
        if len(right_fields()) >= 2: break
        time.sleep(1)
    fields = right_fields()
    def put(field, text, name):
        for attempt in range(3):
            try:
                field.dblclick(); time.sleep(0.3)              # 더블클릭 포커스
                field.press("Control+a"); field.press("Delete"); time.sleep(0.2)  # 기존내용 지움
                if HASCLIP:
                    pyperclip.copy(text); field.press("Control+v")  # 클립보드 붙여넣기
                else:
                    field.fill(text)
                time.sleep(0.4)
                val = (field.input_value() or "").strip()
                if val[:15] == text.strip()[:15]: log(f"{name} 입력 OK"); return True
                log(f"{name} 재시도({attempt}) 현재='{val[:15]}'")
            except Exception as e: log(f"{name} 오류 {str(e)[:40]}")
            time.sleep(0.5)
        return False
    ok_t = put(fields[0], TITLE, "제목") if len(fields) >= 1 else False
    ok_d = put(fields[1], DESC, "설명") if len(fields) >= 2 else False
    # 게시
    pub = False
    for _ in range(6):
        for t in ("게시", "저장"):
            try:
                btn = pg.get_by_role("button", name=t).first
                if btn.is_visible(timeout=1500) and btn.is_enabled(): btn.click(timeout=3000); pub = True; break
            except Exception: pass
        if pub: break
        time.sleep(1.5)
    time.sleep(5)
    log(f"=== {UILANG}: 제목={ok_t} 설명={ok_d} 게시={'OK' if pub else 'NO'} (clip={HASCLIP}) ===")
print("DONE")
