# -*- coding: utf-8 -*-
"""
정지 이미지 에셋 생성기 (재작성판) — Google Flow 이미지 모드.

기존 generate_home_vocab_assets.py 의 문제(실패 시 전체 chrome 강제종료/스케줄러
재부팅 루프, 라이트박스 다운로드 의존 캡처)를 제거하고, 검증된 autoveo_flow 1차
프리미티브(open_new_project / set_image_mode / fill_prompt[클립보드 붙여넣기] /
generate / wait_image)를 그대로 재사용한다.

캡처: 라이트박스 다운로드 대신 **생성된 이미지 타일을 직접 스크린샷** → process_lineart
의 make_white_transparent 로 베이지 배경 투명화 → <outdir>/<key>.png.

특징: 단일 세션, 멱등(존재하는 png 스킵), 실패해도 세션 내 재시도(최대 3회)하고
사용자의 일반 크롬은 절대 건드리지 않는다.

사용:
  python gen_assets_flow.py --prompts home_vocab/prompts_for_flow.txt --outdir home_vocab
  python gen_assets_flow.py --only character_sleeping,character_studying,character_reading
"""
import os
import sys
import json
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "scratch"))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

import autoveo_flow as af  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

def check_asset_exists_in_db(key):
    """SQLite와 Supabase DB에 해당 key가 등록되어 있는지 교차 확인합니다."""
    # 1. SQLite 확인
    db_path = os.path.join(ROOT, "channel", "content.db")
    in_sqlite = False
    if os.path.exists(db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT id FROM assets WHERE file_path = ? OR name_en = ? OR name_kr = ?", (f"{key}.png", key, key))
            if cur.fetchone():
                in_sqlite = True
            cur.close()
            conn.close()
        except Exception as e:
            af.log(f"  [DB_CHECK] SQLite 조회 실패: {e}")

    # 2. Supabase 확인
    in_supabase = False
    env_path = os.path.join(ROOT, ".env")
    if os.path.exists(env_path):
        try:
            import psycopg2
            env = {}
            for ln in open(env_path, encoding="utf-8"):
                ln = ln.strip()
                if ln and not ln.startswith("#") and "=" in ln:
                    k, v = ln.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
            
            conn = psycopg2.connect(
                host=env["SUPABASE_DB_HOST"], port=env.get("SUPABASE_DB_PORT", "5432"),
                user=env["SUPABASE_DB_USER"], password=env["SUPABASE_DB_PASSWORD"],
                dbname=env.get("SUPABASE_DB_NAME", "postgres"), sslmode="require", connect_timeout=10
            )
            cur = conn.cursor()
            cur.execute("SELECT id FROM assets WHERE file_path = %s OR name_en = %s OR name_kr = %s", (f"{key}.png", key, key))
            if cur.fetchone():
                in_supabase = True
            else:
                cur.execute("SELECT id FROM character_assets WHERE key = %s OR file_path = %s", (key, f"{key}.png"))
                if cur.fetchone():
                    in_supabase = True
            cur.close()
            conn.close()
        except Exception as e:
            af.log(f"  [DB_CHECK] Supabase 조회 실패: {e}")
            
    return in_sqlite or in_supabase

TRANSPARENT = True   # --no-transparent 로 끄면 원본(배경 보존) 저장 — 레퍼런스/캐릭터 사진용
ASPECT = "16:9"      # --aspect 로 변경(쇼츠/세로용은 9:16)

# 현재 캔버스의 '생성 미디어 이미지' src 목록(생성 직전 스냅샷용).
SRCS_JS = r"""
() => {
  const out=[];
  for (const im of document.querySelectorAll('img')) {
    const s = im.getAttribute('src')||'';
    if (!/media\.getMediaUrlRedirect|googleusercontent/.test(s)) continue;
    const r = im.getBoundingClientRect();
    if (r.width<200||r.height<120||r.width>1200||r.height>900) continue;
    out.push(s);
  }
  return out;
}
"""

# known(생성 전 src들)에 없는 '새' 포스터 중 가장 좌측(최신) 요소 핸들 반환.
# → 이전 에셋 타일을 잘못 잡는 오프셋 버그 방지(가장 큰 타일이 아니라 '새로 생긴' 타일).
NEW_EL_JS = r"""
(known) => {
  let best=null, bestLeft=Infinity;
  for (const im of document.querySelectorAll('img')) {
    const s = im.getAttribute('src')||'';
    if (!/media\.getMediaUrlRedirect|googleusercontent/.test(s)) continue;
    const r = im.getBoundingClientRect();
    if (r.width<200||r.height<120||r.width>1200||r.height>900) continue;
    const parent = im.closest('div');
    if (parent && (parent.querySelector('svg')||parent.querySelector('[class*=spinner]')||parent.querySelector('[class*=loading]'))) continue;
    if (known.includes(s)) continue;
    if (r.x < bestLeft){bestLeft=r.x; best=im;}
  }
  return best;
}
"""


def bot_guard(page, pace_ms=9000):
    """봇 감지('비정상적인 활동' 등) 시 크롬을 죽이지 않고 '다시 시도'로 풀고 길게 대기한다.
    매 에셋마다 호출해 사람처럼 페이싱(pace_ms)도 준다. 반환 True=봇 감지였음."""
    page.wait_for_timeout(pace_ms)   # 정상 페이싱(연속 생성 방지 → 봇감지 예방)
    try:
        body = page.inner_text("body", timeout=2000) or ""
    except Exception:
        body = ""
    if ("비정상" in body) or ("정책" in body) or ("unusual" in body.lower()) or ("verify" in body.lower()):
        af.log("  [BOT] 비정상 활동/정책 메시지 감지 — '다시 시도' 후 4분 대기(크롬 유지)")
        for t in ("다시 시도", "Try again", "refresh"):
            try:
                if af.click_text(page, t):
                    break
            except Exception:
                pass
        page.wait_for_timeout(240000)   # 트립되면 플래그가 끈적 — 90초론 부족, 넉넉히 식힘
        return True
    return False


def parse_keyed_prompts(path):
    items = []
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if not s or s.startswith("#") or ":" not in s:
            continue
        k, p = s.split(":", 1)
        k, p = k.strip(), p.strip()
        if k and p:
            items.append((k, p))
    return items


def make_bg_transparent(raw_path, out_path, tol=28):
    """가장자리(4모서리)에서 연결된 '근사-흰색/베이지' 배경만 투명화(flood-fill).
    캐릭터 내부의 흰색(얼굴·셔츠 등)은 외곽 배경과 단절돼 있어 보존된다.
    (코너 색 기준 + 허용오차 방식으로 실제 배경색만 안전하게 제거)."""
    try:
        from PIL import Image
        from collections import deque
        img = Image.open(raw_path).convert("RGBA")
        w, h = img.size
        px = img.load()
        
        # 4 모서리 색상들
        corners = [px[0, 0][:3], px[w - 1, 0][:3], px[0, h - 1][:3], px[w - 1, h - 1][:3]]
        # median (간단히 정렬하여 중간값 추출)
        bg_r = sorted([c[0] for c in corners])[2]
        bg_g = sorted([c[1] for c in corners])[2]
        bg_b = sorted([c[2] for c in corners])[2]
        
        seen = bytearray(w * h)
        dq = deque([(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)])
        while dq:
            x, y = dq.popleft()
            if x < 0 or y < 0 or x >= w or y >= h:
                continue
            idx = y * w + x
            if seen[idx]:
                continue
            seen[idx] = 1
            r, g, b, a = px[x, y]
            
            # 허용오차 확인
            if abs(r - bg_r) > tol or abs(g - bg_g) > tol or abs(b - bg_b) > tol:
                continue   # 배경(코너색)과 충분히 다르면 멈춤(=외곽선)
            
            px[x, y] = (r, g, b, 0)
            dq.append((x + 1, y)); dq.append((x - 1, y))
            dq.append((x, y + 1)); dq.append((x, y - 1))
        img.save(out_path)
        return True
    except Exception as e:
        af.log(f"  [CONVERT] flood-fill 투명화 예외: {str(e)[:100]}")
        return False


def capture_asset(page, out_path):
    """생성된 이미지 타일을 ⋮메뉴 → 다운로드(원본)로 받아 베이지 배경 투명화 저장.
    (autoveo 영상 다운로드와 동일한 검증된 방식 — DOM 스크린샷의 '잘못된 타일/렌더 전
    프레임/배경 노이즈' 문제를 회피한다.)"""
    # 누적 캔버스에서 '가장 좌측(=가장 최신) 타일'을 타깃한다(가장 큰 타일 X — 이전 에셋을 잡음).
    posters = page.evaluate(af.POSTERS_JS) or []
    if not posters:
        af.log("  [CAPTURE] 이미지 타일 없음")
        return False
    center = posters[0]  # POSTERS_JS 는 left 오름차순 → [0] 이 최신
    raw = out_path + ".raw.png"
    try:
        with page.expect_download(timeout=30000) as dl:
            if not af.open_tile_menu(page, center):
                raise RuntimeError("타일 ⋮ 메뉴 열기 실패")
            af.click_text(page, "다운로드")
            page.wait_for_timeout(900)
            (af.click_text(page, "원본 크기") or af.click_text(page, "720p 원본 크기")
             or af.click_text(page, "원본") or af.click_text(page, "720p"))
        d = dl.value
        d.save_as(raw)
        af.log("  [CAPTURE] 타일 원본 다운로드 성공")
    except Exception as e:
        af.log(f"  [CAPTURE] 다운로드 실패: {str(e)[:100]}")
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        return False
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass
    if TRANSPARENT:
        ok = make_bg_transparent(raw, out_path)   # 가장자리 연결 배경만 투명화
    else:
        try:
            from PIL import Image
            Image.open(raw).convert("RGBA").save(out_path)   # 원본 그대로(배경 보존)
            ok = True
        except Exception as e:
            af.log(f"  [SAVE] 원본 저장 예외: {str(e)[:80]}")
            ok = False
    try:
        os.remove(raw)
    except Exception:
        pass
    return bool(ok) and os.path.exists(out_path) and os.path.getsize(out_path) > 3000


def parse_ref_jobs(path):
    """'outkey | ref_image_path[,ref2,...] | pose_prompt' 형식 파싱.
    ref 필드는 콤마로 여러 레퍼런스 경로를 줄 수 있다(예: 졸라맨+졸라녀 둘이 함께)."""
    jobs = []
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if not s or s.startswith("#") or "|" not in s:
            continue
        parts = [x.strip() for x in s.split("|", 2)]
        if len(parts) == 3 and all(parts):
            jobs.append((parts[0], parts[1], parts[2]))
    return jobs


def run_ref_jobs(jobs_path, outdir, force, yes=False):
    """레퍼런스 이미지를 업로드(프롬프트에 추가)하고 포즈 프롬프트로 '같은 캐릭터'의 변형
    이미지를 생성→캡처한다. (캐릭터 일관성 유지용)."""
    jobs = parse_ref_jobs(jobs_path)
    if not jobs:
        af.log("ref-jobs: 작업 없음 — 파일/형식 확인")
        return 1
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(af.DBG, exist_ok=True)

    def made(k):
        f = os.path.join(outdir, f"{k}.png")
        return os.path.exists(f) and os.path.getsize(f) > 3000

    pend = [(k, r, p) for k, r, p in jobs if force or not made(k)]
    af.log(f"ref-jobs 전체 {len(jobs)} / 대상 {len(pend)}: {[k for k, _, _ in pend]}")
    if not pend:
        af.log("대상 없음(모두 존재).")
        return 0
    lock = os.path.join(af.PROFILE, "SingletonLock")
    if os.path.exists(lock):
        try:
            os.remove(lock)
        except Exception:
            pass

    ok, fail = [], []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
            no_viewport=True, accept_downloads=True, downloads_path=af.DL_DIR,
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                  "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for i, (key, ref, prompt) in enumerate(pend, 1):
            out = os.path.join(outdir, f"{key}.png")
            ref_paths = [r.strip() for r in ref.split(",") if r.strip()]
            af.log(f"=== ({i}/{len(pend)}) {key}  ref={', '.join(os.path.basename(r) for r in ref_paths)} ===")
            
            # DB 사전 체크 추가
            if check_asset_exists_in_db(key):
                af.log(f"  [DB_EXISTS] '{key}' 에셋이 DB(SQLite 또는 Supabase)에 이미 존재합니다.")
                if yes:
                    ans = 'y'
                else:
                    sys.stdout.write(f"\n[INTERACTIVE_PROMPT] '{key}' 에셋이 이미 DB에 존재합니다. 재생성하시겠습니까? (y/n): ")
                    sys.stdout.flush()
                    try:
                        ans = sys.stdin.readline().strip().lower()
                    except Exception:
                        ans = 'n'
                if ans != 'y':
                    af.log(f"  [SKIP] 사용자가 재생성을 취소하여 '{key}' 생성을 건너뜁니다.")
                    continue
                    
            done = False
            for attempt in range(1, 4):
                try:
                    if not af.open_new_project(page):
                        af.log("  [WARN] 프로젝트 진입 실패")
                        page.wait_for_timeout(2500)
                        continue
                    af.set_image_mode(page, aspect=ASPECT)
                    # 여러 레퍼런스를 순차 업로드(각각 '프롬프트에 추가') → 한 컴포저에 함께 첨부.
                    upload_ok = True
                    for rp in ref_paths:
                        if not af.upload_image(page, os.path.abspath(rp)):
                            af.log(f"  [WARN] 레퍼런스 업로드 실패({os.path.basename(rp)}) {attempt}/3")
                            upload_ok = False
                            break
                        page.wait_for_timeout(3500)   # 각 업로드 타일 준비
                    if not upload_ok:
                        page.wait_for_timeout(1500)
                        continue
                    # 업로드된 레퍼런스 이미지가 POSTERS_JS 목록에 완전히 나타날 때까지 대기 (레이스 컨디션 방지)
                    uploaded_appeared = False
                    n_before = 0
                    for _ in range(10):  # 최대 15초 대기
                        try:
                            n_before = len(page.evaluate(af.POSTERS_JS) or [])
                        except Exception:
                            n_before = 0
                        if n_before >= len(ref_paths):
                            uploaded_appeared = True
                            break
                        page.wait_for_timeout(1500)
                    if not uploaded_appeared:
                        af.log(f"  [WARN] 업로드한 레퍼런스 타일 미출현 (현재 {n_before}/{len(ref_paths)})")
                    af.fill_prompt(page, prompt)
                    if not af.generate(page):
                        af.log(f"  [WARN] 생성버튼 실패 {attempt}/3")
                        page.wait_for_timeout(1500)
                        continue
                    appeared = False
                    for _ in range(20):
                        page.wait_for_timeout(3000)
                        try:
                            if len(page.evaluate(af.POSTERS_JS) or []) > n_before:
                                appeared = True
                                break
                        except Exception:
                            pass
                    if not appeared:
                        af.log(f"  [WARN] 새 타일 미출현 {attempt}/3")
                        af.shot(page, f"ref_{key}_fail_try{attempt}")
                        continue
                    page.wait_for_timeout(2500)
                    if capture_asset(page, out):
                        done = True
                        break
                    af.log(f"  [WARN] 캡처 실패 {attempt}/3")
                except Exception as e:
                    af.log(f"  [ERR] {key} {attempt}: {str(e)[:120]}")
                    page.wait_for_timeout(2000)
            if done:
                af.log(f"[OK] {key} -> {out} ({os.path.getsize(out)} bytes)")
                ok.append(key)
            else:
                af.log(f"[FAIL] {key}")
                fail.append(key)
        af.log(f"ref-jobs 완료 — 성공 {len(ok)} / 실패 {len(fail)}: {fail}")
        try:
            ctx.close()
        except Exception:
            pass
    return 0 if not fail else 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", default="home_vocab/prompts_for_flow.txt")
    ap.add_argument("--outdir", default="home_vocab")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", default="", help="콤마구분 특정 key만 생성")
    ap.add_argument("--ref-jobs", default="", help="레퍼런스 기반 포즈 생성 작업파일 (outkey | ref | prompt)")
    ap.add_argument("--no-transparent", action="store_true", help="투명화하지 않고 원본(배경 보존) 저장")
    ap.add_argument("--yes", "-y", action="store_true", help="DB 중복이 있어도 프롬프트 대기 없이 승인 처리")
    ap.add_argument("--gap", type=int, default=0, help="이미지 사이 휴먼 페이스 대기(초). 봇감지는 누적형이라 짧아도 됨(권장 20). 0=대기없음")
    ap.add_argument("--session-batch", type=int, default=0, help="N장마다 브라우저 세션을 새로 시작(봇감지 누적 카운트 리셋). 권장 4. 0=비활성")
    ap.add_argument("--session-batch-first", type=int, default=0, help="첫 세션만 다른 장수(예: 5). 0=session-batch와 동일. 권장 5(첫 5장)→이후 4장씩")
    ap.add_argument("--aspect", default="16:9", help="Flow 이미지 비율 (예: 16:9, 9:16, 1:1). 쇼츠/세로용은 9:16")
    args = ap.parse_args()
    global GAP, ASPECT
    GAP = args.gap
    ASPECT = args.aspect
    SBATCH = args.session_batch
    SBATCH_FIRST = args.session_batch_first or args.session_batch

    global TRANSPARENT
    TRANSPARENT = not args.no_transparent

    if args.ref_jobs:
        return run_ref_jobs(args.ref_jobs, args.outdir, args.force, args.yes)

    items = parse_keyed_prompts(args.prompts)
    if args.only:
        only = set(x.strip() for x in args.only.split(",") if x.strip())
        items = [(k, p) for k, p in items if k in only]

    os.makedirs(args.outdir, exist_ok=True)
    os.makedirs(af.DBG, exist_ok=True)
    pf = os.path.join(args.outdir, "asset_progress.json")
    progress = {}
    if os.path.exists(pf):
        try:
            progress = json.load(open(pf, encoding="utf-8"))
        except Exception:
            progress = {}

    def made(k):
        f = os.path.join(args.outdir, f"{k}.png")
        return os.path.exists(f) and os.path.getsize(f) > 3000

    pending = [(k, p) for k, p in items if args.force or not made(k)]
    af.log(f"전체 {len(items)} / 생성 대상 {len(pending)}: {[k for k, _ in pending]}")
    if not pending:
        af.log("생성할 에셋 없음(모두 존재).")
        return 0

    if os.path.exists(os.path.join(af.PROFILE, "SingletonLock")):
        try:
            os.remove(os.path.join(af.PROFILE, "SingletonLock"))
        except Exception:
            pass

    ok, fail = [], []
    with sync_playwright() as p:
        ctx = None
        page = None

        def start_browser():
            nonlocal ctx, page
            if ctx:
                af.log("  [REBOOT] 기존 크롬 세션을 종료합니다.")
                try:
                    ctx.close()
                except Exception:
                    pass
                time.sleep(3)
            if os.path.exists(os.path.join(af.PROFILE, "SingletonLock")):
                try:
                    os.remove(os.path.join(af.PROFILE, "SingletonLock"))
                except Exception:
                    pass
            af.log("  [REBOOT] 크롬 세션을 새로 시작합니다.")
            ctx = p.chromium.launch_persistent_context(
                af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
                no_viewport=True, accept_downloads=True, downloads_path=af.DL_DIR,
                ignore_default_args=["--enable-automation"],
                args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                      "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
            page = ctx.pages[0] if ctx.pages else ctx.new_page()

        import time
        start_browser()

        _since_reset = 0
        _cur_batch = SBATCH_FIRST if SBATCH_FIRST > 0 else SBATCH   # 첫 세션 장수(예: 5)
        for i, (key, prompt) in enumerate(pending, 1):
            out = os.path.join(args.outdir, f"{key}.png")
            # ★ 봇감지 누적 회피: 세션당 장수 한도에 도달하면 브라우저 세션을 새로 시작해 카운트를 리셋한다
            #   (봇감지는 페이싱이 아니라 세션당 횟수에 걸림. 첫 세션 5장 → 이후 4장씩. 2026-06-30)
            if SBATCH > 0 and i > 1 and _since_reset >= _cur_batch:
                af.log(f"  [SESSION] {_cur_batch}장 생성 — 세션 리셋(봇감지 누적 카운트 초기화)")
                start_browser()
                _since_reset = 0
                _cur_batch = SBATCH      # 두 번째 세션부터는 작은 배치(4)
            _since_reset += 1
            # 휴먼 페이스: 첫 장 빼고 매 장 사이 GAP±지터 만큼 쉰다(연사 봇감지 예방, 100장 지속가능)
            # time.sleep 사용 — 리부트로 page가 닫혀도 안전(page.wait_for_timeout는 stale page에서 크래시)
            if i > 1 and GAP > 0:
                import random as _rnd
                import time as _time
                w = GAP + _rnd.randint(0, max(1, GAP // 2))
                af.log(f"  [PACE] 다음 장까지 {w}s 휴먼 대기…")
                _time.sleep(w)
            af.log(f"=== ({i}/{len(pending)}) {key} ===")

            # DB 사전 체크 추가
            if check_asset_exists_in_db(key):
                af.log(f"  [DB_EXISTS] '{key}' 에셋이 DB(SQLite 또는 Supabase)에 이미 존재합니다.")
                if args.yes:
                    ans = 'y'
                else:
                    sys.stdout.write(f"\n[INTERACTIVE_PROMPT] '{key}' 에셋이 이미 DB에 존재합니다. 재생성하시겠습니까? (y/n): ")
                    sys.stdout.flush()
                    try:
                        ans = sys.stdin.readline().strip().lower()
                    except Exception:
                        ans = 'n'
                if ans != 'y':
                    af.log(f"  [SKIP] 사용자가 재생성을 취소하여 '{key}' 생성을 건너뜁니다.")
                    progress[key] = "success"  # 기존 DB에 있으므로 성공으로 표기
                    try:
                        json.dump(progress, open(pf, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                    continue
                    
            done = False
            bot_detected = False
            for attempt in range(1, 4):
                try:
                    if not af.open_new_project(page):
                        af.log("  [WARN] 프로젝트 진입 실패")
                        page.wait_for_timeout(2500)
                        continue
                    af.set_image_mode(page, aspect=ASPECT)
                    if bot_guard(page):   # 페이싱 + 봇감지('비정상 활동') 가드
                        bot_detected = True
                    try:
                        n_before = len(page.evaluate(af.POSTERS_JS) or [])
                    except Exception:
                        n_before = 0
                    af.fill_prompt(page, prompt)
                    if not af.generate(page):
                        af.log(f"  [WARN] 생성버튼 실패 {attempt}/3")
                        page.wait_for_timeout(1500)
                        continue
                    # ★ 새 타일이 '추가'(포스터 개수 증가)될 때까지 대기 → off-by-one(직전 타일 캡처) 방지.
                    appeared = False
                    for _ in range(20):   # 20 * 3s = 60s
                        page.wait_for_timeout(3000)
                        try:
                            if len(page.evaluate(af.POSTERS_JS) or []) > n_before:
                                appeared = True
                                break
                        except Exception:
                            pass
                    if not appeared:
                        af.log(f"  [WARN] 새 타일 미출현 {attempt}/3")
                        af.shot(page, f"asset_{key}_fail_try{attempt}")
                        continue
                    page.wait_for_timeout(2500)   # 완전 렌더 대기 후 최신(좌측) 타일 다운로드
                    if capture_asset(page, out):
                        done = True
                        break
                    af.log(f"  [WARN] 캡처 실패 {attempt}/3")
                    af.shot(page, f"asset_{key}_capfail_try{attempt}")
                except Exception as e:
                    af.log(f"  [ERR] {key} {attempt}: {str(e)[:120]}")
                    page.wait_for_timeout(2000)

            if done:
                af.log(f"[OK] {key} -> {out} ({os.path.getsize(out)} bytes)")
                ok.append(key)
                progress[key] = "success"
            else:
                af.log(f"[FAIL] {key}")
                fail.append(key)
                progress[key] = "fail"
            try:
                json.dump(progress, open(pf, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            except Exception:
                pass

            # 봇이 감지되었거나 에셋 생성에 실패한 경우 크롬 재부팅
            if bot_detected or not done:
                af.log("  [BOT/FAIL DETECTED] 다음 작업을 위해 크롬 브라우저를 재부팅합니다.")
                start_browser()

        af.log(f"완료 — 성공 {len(ok)} / 실패 {len(fail)}: {fail}")
        try:
            if ctx:
                ctx.close()
        except Exception:
            pass
    return 0 if not fail else 3


if __name__ == "__main__":
    sys.exit(main())
