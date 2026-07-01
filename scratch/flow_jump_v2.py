# -*- coding: utf-8 -*-
"""
[사용자 지정 정확한 순서] 지은 점프 사진 생성.
  1) DB에서 사진 가져온다
  2) 새 Google Flow 프로젝트 연다
  3) 사진을 넣는다(업로드)
  4) 사진이 '타일'로 뜬다(~25초)
  5) ★그 타일을 클릭해서 '입력창'에 넣는다★   ← 직전에 빠졌던 단계
  6) 스크립트(프롬프트)를 넣고 ENTER
  7) 45초 기다린다
  8) '왼편(최신) 타일'을 다운로드 → 저장
단계마다 스크린샷(scratch/_v2_*.png). 받은 이미지 md5가 기존과 같으면 STALE 처리(저장취소).
"""
import os
import sys
import glob
import hashlib
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

import autoveo_flow as af  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

REF = os.path.join(ROOT, "home_vocab", "_dbref_jieun_base_front.png")
OUT = os.path.join(ROOT, "home_vocab", "jieun_jumping.png")
STATUS = os.path.join(ROOT, "scratch", "jump_status.txt")
SD = os.path.join(ROOT, "scratch")

PROMPT = ("Using the uploaded reference image, keep the EXACT same Korean schoolgirl "
          "character Jieun — same long brown hair, same face, same navy and white sailor "
          "school uniform with a red neckerchief and a navy pleated skirt — but now draw her "
          "doing an energetic STAR JUMP high in mid-air: BOTH arms stretched out wide, BOTH "
          "legs spread wide apart, both feet off the ground, big happy smile, dynamic "
          "symmetric star-shaped jumping pose, front view facing the camera, ONE single "
          "full-body figure, minimalist 2D line art, thick clean black outlines, clean "
          "whiteboard marker drawing style, on a solid flat light beige background (#F5F5F0), "
          "no text, no signatures")

SRCS_JS = r"""
() => { const o=[]; for (const im of document.querySelectorAll('img')){const s=im.getAttribute('src')||'';
if(!/media\.getMediaUrlRedirect|googleusercontent/.test(s))continue; const r=im.getBoundingClientRect();
if(r.width<200||r.height<120||r.width>1200||r.height>900)continue; o.push(s);} return o; }
"""
TILES_JS = r"""
() => { const o=[]; for (const im of document.querySelectorAll('img')){const s=im.getAttribute('src')||'';
if(!/media\.getMediaUrlRedirect|googleusercontent/.test(s))continue; const r=im.getBoundingClientRect();
if(r.width<200||r.height<120||r.width>1200||r.height>900)continue;
const p=im.closest('div'); if(p&&(p.querySelector('svg')||p.querySelector('[class*="spinner"]')||p.querySelector('[class*="loading"]')))continue;
o.push({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),left:Math.round(r.x),src:s});}
o.sort((a,b)=>a.left-b.left); return o; }
"""
NEW_LEFT_JS = r"""
(known) => { let best=null,bl=Infinity; for (const im of document.querySelectorAll('img')){const s=im.getAttribute('src')||'';
if(!/media\.getMediaUrlRedirect|googleusercontent/.test(s))continue; const r=im.getBoundingClientRect();
if(r.width<200||r.height<120||r.width>1200||r.height>900)continue;
const p=im.closest('div'); if(p&&(p.querySelector('svg')||p.querySelector('[class*="spinner"]')||p.querySelector('[class*="loading"]')))continue;
if(known.includes(s))continue; if(r.x<bl){bl=r.x; best={x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),left:Math.round(r.x),src:s};}}
return best; }
"""


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def env(p=os.path.join(ROOT, ".env")):
    d = {}
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d


def status(m):
    open(STATUS, "w", encoding="utf-8").write(m + "\n")
    af.log(m)


def shot(page, name):
    try:
        page.screenshot(path=os.path.join(SD, name))
    except Exception:
        pass


def main():
    try:
        os.remove(STATUS)
    except Exception:
        pass

    # 1) DB에서 사진 가져온다
    e = env()
    import psycopg2
    cn = psycopg2.connect(host=e["SUPABASE_DB_HOST"], port=e["SUPABASE_DB_PORT"],
                          user=e["SUPABASE_DB_USER"], password=e["SUPABASE_DB_PASSWORD"],
                          dbname=e["SUPABASE_DB_NAME"], sslmode="require", connect_timeout=20)
    url = cn.cursor().execute if False else None
    cur = cn.cursor()
    cur.execute("SELECT storage_url FROM character_assets WHERE key='jieun_base_front'")
    src_url = cur.fetchone()[0]
    cn.close()
    urllib.request.urlretrieve(src_url, REF)
    af.log(f"[1] DB 사진 다운로드 → {REF} ({os.path.getsize(REF)} bytes)")

    existing = {}
    for f in glob.glob(os.path.join(ROOT, "home_vocab", "*.png")):
        if os.path.basename(f) != "jieun_jumping.png":
            try:
                existing[md5(f)] = os.path.basename(f)
            except Exception:
                pass

    lk = os.path.join(af.PROFILE, "SingletonLock")
    if os.path.exists(lk):
        try:
            os.remove(lk)
        except Exception:
            pass

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
            no_viewport=True, accept_downloads=True, downloads_path=af.DL_DIR,
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                  "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        # 2) 새 Flow 프로젝트
        if not af.open_new_project(page):
            status("[FAIL] 새 프로젝트 진입 실패")
            return 1
        af.set_image_mode(page)
        shot(page, "_v2_0_project.png")

        # 3) 사진 넣는다(업로드)
        af.log("[3] 사진 업로드")
        if not af.upload_image(page, os.path.abspath(REF)):
            status("[FAIL] 업로드 실패")
            shot(page, "_v2_upload_fail.png")
            return 1

        # 4) 타일로 뜰 때까지 ~25초
        af.log("[4] 사진 타일 출현 대기(~25초)")
        page.wait_for_timeout(25000)
        tiles = page.evaluate(TILES_JS) or []
        shot(page, "_v2_1_uploaded_tile.png")
        if not tiles:
            status("[FAIL] 업로드 타일 미출현")
            return 1
        af.log(f"[4] 타일 {len(tiles)}개 — 가장 왼쪽 타일을 입력창에 넣기 위해 클릭")

        # 5) ★타일의 '더보기(⋮)' → '추가하기' 로 입력창에 넣는다★ (단순 클릭으론 추가 안 됨)
        t = tiles[0]
        added = False
        if af.open_tile_menu(page, t):
            page.wait_for_timeout(700)
            for label in ("추가하기", "프롬프트에 추가", "장면에 추가", "추가", "Add to prompt", "Add"):
                if af.click_text(page, label):
                    af.log(f"[5] 더보기(⋮) → '{label}' 클릭 — 입력창에 추가")
                    added = True
                    break
        if not added:
            status("[FAIL] 타일 더보기→추가하기 실패(입력창에 안 들어감)")
            shot(page, "_v2_add_fail.png")
            return 1
        page.wait_for_timeout(2500)
        shot(page, "_v2_2_added.png")

        # 6) 스크립트 입력 + ENTER
        af.log("[6] 점프 스크립트 입력 후 ENTER")
        af.fill_prompt(page, PROMPT)
        page.wait_for_timeout(800)
        shot(page, "_v2_3_prompt.png")
        known = page.evaluate(SRCS_JS) or []     # 생성 직전 타일 src(=ref 포함)
        af.log(f"    생성 전 타일 {len(known)}개 기록(known)")
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)
        # ENTER로 생성이 시작 안 됐으면 '만들기' 버튼 폴백
        started = (len(page.evaluate(SRCS_JS) or []) != len(known)) or False
        if not started:
            af.log("    ENTER 후 변화 없음 → '만들기' 버튼 폴백")
            af.generate(page)

        # 7) 45초 대기 후 왼편 새 타일 폴링
        af.log("[7] 45초 대기")
        page.wait_for_timeout(45000)
        new = None
        for _ in range(20):           # +최대 60초 여유
            new = page.evaluate(NEW_LEFT_JS, known)
            if new:
                break
            page.wait_for_timeout(3000)
        if not new:
            status("[FAIL] 왼편 새 타일 미출현(생성 실패 추정)")
            shot(page, "_v2_no_new.png")
            return 1
        page.wait_for_timeout(3000)
        shot(page, "_v2_4_generated.png")
        af.log(f"[8] 왼편 새 타일(left={new['left']}) 다운로드")

        # 8) 왼편 타일 다운로드
        raw = OUT + ".raw.png"
        try:
            with page.expect_download(timeout=30000) as dl:
                if not af.open_tile_menu(page, new):
                    raise RuntimeError("타일 ⋮ 메뉴 실패")
                af.click_text(page, "다운로드")
                page.wait_for_timeout(900)
                (af.click_text(page, "원본 크기") or af.click_text(page, "720p 원본 크기")
                 or af.click_text(page, "원본") or af.click_text(page, "720p"))
            dl.value.save_as(raw)
            try:
                page.keyboard.press("Escape")
            except Exception:
                pass
        except Exception as ex:
            status(f"[FAIL] 다운로드 실패: {str(ex)[:120]}")
            shot(page, "_v2_dl_fail.png")
            return 1

        from PIL import Image
        Image.open(raw).convert("RGBA").save(OUT)
        try:
            os.remove(raw)
        except Exception:
            pass
        m = md5(OUT)
        if m in existing:
            status(f"[STALE] 받은 이미지가 기존 '{existing[m]}' 와 동일(md5={m}) — 잘못된 타일. 저장취소.")
            try:
                os.remove(OUT)
            except Exception:
                pass
            return 2
        status(f"[OK] 점프 사진 생성·저장 완료 → home_vocab/jieun_jumping.png "
               f"({os.path.getsize(OUT)} bytes, md5={m}, 기존 중복 아님 ✔)")
        af.log("브라우저 12분 유지(확인용). 닫아도 됩니다.")
        try:
            page.wait_for_timeout(720000)
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
