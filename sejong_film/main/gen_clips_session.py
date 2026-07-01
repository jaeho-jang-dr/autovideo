# -*- coding: utf-8 -*-
"""단일 브라우저 · 단일 프로젝트 클립 생성 (검증된 수동 방식).
- 브라우저 1개 + 프로젝트 1개만 사용. 클립마다 '+ 새 프로젝트'(open_new_project) 호출 안 함.
- 클립마다 캔버스 타일을 삭제해 비운 뒤 업로드→애니메이션→영상(80초)→왼편 타일 다운로드.
- 새로 뜨는 블랭크 탭/윈도우는 자동으로 닫음.
- 페이지가 죽으면 브라우저만 재기동(프로젝트 재진입), 같은 클립 재시도.
env: SCENES="3,4,5" 로 특정 씬만(테스트). 없으면 누락 전체.
사용: python sejong_film/main/gen_clips_session.py"""
import os, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT); os.chdir(ROOT)
import autoveo_flow as af
from playwright.sync_api import sync_playwright

KF = os.path.join(ROOT, "sejong_film", "main", "keyframes")
OUTD = os.path.join(ROOT, "sejong_main_kf")
af.OUT_DIR = OUTD
os.makedirs(OUTD, exist_ok=True); os.makedirs(af.DL_DIR, exist_ok=True); os.makedirs(af.DBG, exist_ok=True)

mot = {}
for line in open(os.path.join(ROOT, "sejong_film", "main", "kf_motions.tsv"), encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if len(p) >= 2: mot[p[0]] = p[1]

def exists_ok(n):
    f = os.path.join(OUTD, f"scene_{n}.mp4")
    return os.path.exists(f) and os.path.getsize(f) > 10000

sel = os.environ.get("SCENES", "").strip()
TARGETS = [int(x) for x in sel.split(",") if x.strip()] if sel else list(range(1, 49))
LAUNCH_ARGS = ["--start-maximized", "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR", "--disable-gpu"]

def clear_canvas(page):
    for _ in range(10):
        try:
            posters = page.evaluate(af.POSTERS_JS) or []
        except Exception:
            return
        if not posters: return
        af.delete_tile_by_index(page, 0)
        page.wait_for_timeout(600)

def ensure_project(page):
    try:
        if "/project/" in page.url and page.locator(af.PROMPT_SELECTOR).first.is_visible(timeout=2000):
            return True
    except Exception:
        pass
    return af.open_new_project(page)

import subprocess
def profile_chrome_count():
    try:
        o = subprocess.run(["powershell","-NoProfile","-Command",
            "(Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | Where-Object { $_.CommandLine -like '*assets\\chrome_profile*' } | Measure-Object).Count"],
            capture_output=True, text=True, timeout=20)
        return int((o.stdout or "0").strip() or "0")
    except Exception:
        return -1

RELAUNCH_CAP = 3
with sync_playwright() as pw:
    state = {"main": None, "launches": 0}
    def launch():
        # ★ 창 스팸 방지: 띄우기 전 프로필이 깨끗한지 확인. 좀비가 남아있으면 안 띄우고 중단.
        if state["launches"] >= RELAUNCH_CAP:
            raise RuntimeError(f"재기동 {RELAUNCH_CAP}회 초과 — 창 스팸 방지 위해 중단")
        af.force_kill_profile_chrome(); time.sleep(3)
        for _ in range(5):
            if profile_chrome_count() == 0: break
            af.force_kill_profile_chrome(); time.sleep(2)
        if profile_chrome_count() not in (0, -1):
            raise RuntimeError("프로필 크롬이 살아있어 새 창을 띄우지 않고 중단(좀비/사용자 크롬 확인 필요)")
        state["launches"] += 1
        c = pw.chromium.launch_persistent_context(
            af.PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
            accept_downloads=True, downloads_path=af.DL_DIR,
            ignore_default_args=["--enable-automation"], args=LAUNCH_ARGS)
        pg = c.pages[0] if c.pages else c.new_page()
        state["main"] = pg
        def on_page(newpg):   # 블랭크 탭 자동 닫기
            if newpg is not state["main"]:
                try: newpg.wait_for_timeout(400); newpg.close()
                except Exception: pass
        c.on("page", on_page)
        return c, pg

    ctx, page = launch()
    if not ensure_project(page):
        af.log("[ERR] 최초 프로젝트 진입 실패 — 1회 재기동")
        try: ctx.close()
        except Exception: pass
        ctx, page = launch(); ensure_project(page)

    def make_one(n):
        key = f"S{n:02d}"; img = os.path.join(KF, f"{key}.png")
        if not os.path.exists(img): af.log(f"  NO_KF {key}"); return False
        out_path = os.path.join(OUTD, f"scene_{n}.mp4")
        ensure_project(page)
        clear_canvas(page)
        if not af.upload_image(page, img):
            af.log("  [ERR] 업로드 실패"); return False
        page.wait_for_timeout(8000)
        animated = False
        for a in range(4):
            if af.animate_image(page): animated = True; break
            page.wait_for_timeout(3500)
        if not animated:
            af.log("  [ERR] 애니메이션 적용 실패"); return False
        page.wait_for_timeout(1500)
        return af.make_video(page, out_path, mot.get(key, "subtle cinematic motion, no text"), n)

    MAXPASS = 4
    for pa in range(1, MAXPASS + 1):
        remaining = [n for n in TARGETS if not exists_ok(n) and os.path.exists(os.path.join(KF, f"S{n:02d}.png"))]
        af.log(f"===== PASS {pa} (남은 {len(remaining)}: {remaining}) =====")
        if not remaining: break
        consec_fail = 0
        for n in remaining:
            af.log(f"---- CLIP {n} (S{n:02d}) pass {pa} ----")
            try:
                ok = make_one(n)
            except af.BrowserRebootException:
                ok = False; af.log("[REBOOT] 세션 재기동")
                try: ctx.close()
                except Exception: pass
                ctx, page = launch(); ensure_project(page)
            except Exception as e:
                ok = False; af.log(f"[ERR] CLIP {n}: {str(e)[:100]}")
                # 페이지 죽었으면 재기동
                dead = False
                try: _ = page.url
                except Exception: dead = True
                if dead or "closed" in str(e).lower():
                    try: ctx.close()
                    except Exception: pass
                    ctx, page = launch(); ensure_project(page)
            done = sum(1 for x in range(1, 49) if exists_ok(x))
            if ok and exists_ok(n):
                af.log(f"OK_{n} ({done}/48)"); consec_fail = 0
            else:
                af.log(f"MISS_{n} ({done}/48)"); consec_fail += 1
            if consec_fail >= 6:
                af.log("[ABORT] 연속 6회 실패 — 패스 중단(쿨다운 후 다음 패스)"); break
            time.sleep(6)
        done = sum(1 for x in range(1, 49) if exists_ok(x))
        af.log(f"===== PASS {pa} 완료 ({done}/48) =====")
        if all(exists_ok(n) for n in TARGETS): break
        time.sleep(60)
    try: ctx.close()
    except Exception: pass

done = sum(1 for x in range(1, 49) if exists_ok(x))
miss = [n for n in TARGETS if not exists_ok(n)]
print(f"DONE {done}/48, 타깃 누락: {miss}")
print("ALL_CLIPS_SESSION_DONE")
