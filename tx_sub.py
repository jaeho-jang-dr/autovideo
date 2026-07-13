# -*- coding: utf-8 -*-
"""자막 파일 업로드(견고): /translations → 언어행 자막칸 클릭 → 편집기 → 파일업로드(시간코드포함) → 게시.
사용: python tx_sub.py <VID> "<행텍스트>" <srt> [add]   ('add' 주면 먼저 '언어 추가'로 그 언어 추가)
예:  python tx_sub.py Bohkrg5mmTw "한국어 (동영상 언어)" child_growth_science/child_growth.ko.srt
     python tx_sub.py Bohkrg5mmTw "영어" child_growth_science/child_growth.en.srt add"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]; ROW = sys.argv[2]; SRT = os.path.abspath(sys.argv[3])
ADD = len(sys.argv) > 4 and sys.argv[4] == "add"
TAG = "".join(ch for ch in ROW if ch.isalnum())[:6]
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)
def shot(pg, n):
    try: pg.screenshot(path=os.path.join(SH, f"sub_{TAG}_{n}.png")); log("shot " + n)
    except Exception as e: log("shot fail " + str(e)[:40])

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222")   # 로그인된 디버그 크롬 재사용(프로필 충돌 회피)
    ctx = b.contexts[0]
    pg = ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded"); pg.wait_for_timeout(8000)
    shot(pg, "0_page")

    # (옵션) 언어 추가
    if ADD:
        try:
            pg.get_by_text("언어 추가", exact=False).first.click(timeout=6000); pg.wait_for_timeout(1500)
            # 드롭다운/검색에서 언어 선택
            langname = ROW.split("(")[0].strip()
            try:
                sb = pg.get_by_placeholder("언어 검색"); sb.click(); sb.type(langname, delay=60); pg.wait_for_timeout(1200)
            except Exception: pass
            for sel in [f"tp-yt-paper-item:has-text('{langname}')", f"text={langname}"]:
                try: pg.locator(sel).first.click(timeout=3000); log("언어 추가: " + langname); break
                except Exception: pass
            pg.wait_for_timeout(2500)
        except Exception as e: log("언어 추가 스킵/실패 " + str(e)[:60])
        shot(pg, "1_added")

    # 행/자막칸 좌표를 JS로 직접 계산 — 우선 <tr>/<td> 테이블에서 정확한 자막셀,
    # 실패 시 기존 yt-formatted-string 폴백 (다른 페이지 호환)
    part = ROW.split("(")[0].strip()
    info = pg.evaluate("""(args) => {
        const [full, part] = args;
        const all = [...document.querySelectorAll('yt-formatted-string, span, div, td, th')];
        // 자막 열 X (헤더 leaf)
        let capx = null;
        for(const e of document.querySelectorAll('th, td, span, div, yt-formatted-string')){
            if(e.children.length===0 && e.textContent.trim()==='자막'){
                const r=e.getBoundingClientRect();
                if(r.width>0 && r.x>300 && r.y<320){ capx=r.x+r.width/2; break; } } }
        // 대상 행 <tr>: 첫 td 텍스트가 언어명과 일치(자동 자막 제외)
        let cellx=null, celly=null;
        for(const tr of document.querySelectorAll('tr')){
            const tds=[...tr.querySelectorAll('td')];
            if(!tds.length) continue;
            const lt=tds[0].textContent.trim();
            const match = (lt===full) || (lt===part) ||
                          (part && lt.startsWith(part) && lt.indexOf('자동')<0 && lt.indexOf('(동영상')<0 && full===part);
            if(!match) continue;
            // 자막 td = capx에 가장 가까운 td (없으면 두번째 td)
            let capTd=null, bestdx=1e9;
            if(capx!==null){ for(const td of tds){ const r=td.getBoundingClientRect();
                const dx=Math.abs(r.x+r.width/2-capx); if(dx<bestdx){bestdx=dx; capTd=td;} } }
            if(!capTd && tds.length>=2) capTd=tds[1];
            if(capTd){ const rr=capTd.getBoundingClientRect();
                cellx=rr.x+rr.width/2; celly=rr.y+rr.height/2; }
            break;
        }
        // 폴백용 y/sx
        function rowY(txt){ const cs=[];
            for(const e of all){ if(e.offsetParent!==null && e.textContent.trim()===txt){
                const r=e.getBoundingClientRect();
                if(r.width>0 && r.height>0 && r.x<460 && r.y>150) cs.push(r.y+r.height/2); } }
            return cs.length ? Math.max(...cs) : null; }
        let y = rowY(full); if(y===null) y = rowY(part);
        return {cellx:cellx, celly:celly, y:y, sx:capx, vw:window.innerWidth};
    }""", [ROW, part])
    if not info or (info.get("cellx") is None and info.get("y") is None):
        shot(pg, "2b_norow"); log("행 못찾음: " + ROW); pg.close(); raise SystemExit
    if info.get("cellx") is not None:
        hx = info["cellx"]; rowy = info["celly"]; log("자막셀(td) 사용")
    else:
        rowy = info["y"]; hx = info["sx"] if info.get("sx") else info["vw"] * 0.42
    log(f"자막칸 클릭 ({round(hx)},{round(rowy)})")
    pg.mouse.click(round(hx), round(rowy)); pg.wait_for_timeout(5000)
    log("URL: " + pg.url); shot(pg, "2_editor")

    # 업로드 플로우: '파일 업로드' 클릭 → (시간코드 다이얼로그) → file chooser
    def try_upload():
        # 1) 파일 업로드 버튼(파일 chooser 바로 열릴 수도)
        try:
            with pg.expect_file_chooser(timeout=6000) as fc:
                for t in ["파일 업로드", "업로드", "Upload file"]:
                    try: pg.get_by_text(t, exact=False).first.click(timeout=2500); log("클릭: " + t); break
                    except Exception: pass
            fc.value.set_files(SRT); log("파일 지정(직접)"); return True
        except Exception:
            pass
        shot(pg, "3_afterupload")
        # 2) 시간코드 다이얼로그: '시간 코드 포함' 선택 → 계속/업로드에서 chooser
        try:
            for t in ["시간 코드 포함", "시간 코드가 포함", "타임코드 포함"]:
                try: pg.get_by_text(t, exact=False).first.click(timeout=2500); log("시간코드포함 선택"); break
                except Exception: pass
            pg.wait_for_timeout(800)
            with pg.expect_file_chooser(timeout=6000) as fc2:
                for t in ["계속", "파일 선택", "업로드", "Continue"]:
                    try: pg.get_by_text(t, exact=False).first.click(timeout=2500); log("클릭: " + t); break
                    except Exception: pass
            fc2.value.set_files(SRT); log("파일 지정(2단계)"); return True
        except Exception as e:
            log("업로드 실패: " + str(e)[:70]); return False
    ok = try_upload()
    pg.wait_for_timeout(4000); shot(pg, "4_uploaded")

    # 게시/저장
    pub = False
    for t in ["게시", "저장", "PUBLISH", "완료"]:
        try:
            btns = pg.get_by_text(t, exact=True)
            for i in range(btns.count()):
                bt = btns.nth(i)
                if bt.is_visible() and bt.is_enabled():
                    bt.click(); pub = True; log(f"'{t}' 클릭"); break
            if pub: break
        except Exception: pass
    pg.wait_for_timeout(5000); shot(pg, "5_done")

    # 검증
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded"); pg.wait_for_timeout(6000)
    try:
        rows = pg.locator("tr, [class*='language-row']").all()
        for r in rows[:8]:
            t = r.inner_text()[:70].replace("\n", " | ")
            if ROW.split("(")[0].strip() in t: log("ROW: " + t)
    except Exception: pass
    log(f"RESULT upload={ok} publish={pub}")
    pg.wait_for_timeout(2000); pg.close()
print("END")
