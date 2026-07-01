# -*- coding: utf-8 -*-
"""
[일관성 파이프라인] DB의 지은 정면 사진을 레퍼런스로 → 점프(별 모양: 두 팔·두 다리 다 벌림)
동작 사진을 Google Flow 이미지 모드로 생성 → '왼편(최신)의 새 타일'만 다운로드 → 저장.

직전 버그(기존 타일을 잘못 캡처) 방지책:
  - 생성 '전' 화면의 모든 타일 src 를 known 으로 기록
  - 생성 '후' known 에 없는 '새 타일' 중 가장 왼쪽 것만 골라 다운로드
  - 받은 이미지 md5 가 기존 home_vocab/*.png 중 어떤 것과도 같으면 STALE 로 간주(실패 처리)

단계마다 스크린샷(scratch/_jump_*.png) 남김. 이미지 ~40초 소요.
"""
import os
import sys
import glob
import time
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

REF_LOCAL = os.path.join(ROOT, "home_vocab", "_dbref_jieun_base_front.png")
OUT = os.path.join(ROOT, "home_vocab", "jieun_jumping.png")
STATUS = os.path.join(ROOT, "scratch", "jump_status.txt")
SHOTDIR = os.path.join(ROOT, "scratch")

PROMPT = ("Using the uploaded reference image, keep the EXACT same Korean schoolgirl "
          "character Jieun — same long brown hair, same face, same navy and white sailor "
          "school uniform with a red neckerchief and a navy pleated skirt — but now draw her "
          "doing an energetic STAR JUMP high in mid-air: BOTH arms stretched out wide and up, "
          "BOTH legs spread wide apart, both feet clearly off the ground, big happy smile, full "
          "of energy, dynamic symmetric star-shaped jumping-jack pose, front view facing the "
          "camera, ONE single full-body figure (no extra figures, no character sheet), "
          "minimalist 2D line art, thick clean black outlines, clean whiteboard marker drawing "
          "style, on a solid flat light beige background (#F5F5F0), no text, no signatures")

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

# known(생성 전 src)에 없는 '새' 타일 중 가장 왼쪽 것의 center 좌표 반환(스피너 타일 제외).
NEW_LEFT_JS = r"""
(known) => {
  let best=null, bestLeft=Infinity;
  for (const im of document.querySelectorAll('img')) {
    const s = im.getAttribute('src')||'';
    if (!/media\.getMediaUrlRedirect|googleusercontent/.test(s)) continue;
    const r = im.getBoundingClientRect();
    if (r.width<200||r.height<120||r.width>1200||r.height>900) continue;
    const parent = im.closest('div');
    if (parent && (parent.querySelector('svg')||parent.querySelector('[class*="spinner"]')||parent.querySelector('[class*="loading"]'))) continue;
    if (known.includes(s)) continue;
    if (r.x < bestLeft){bestLeft=r.x; best={x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2), left:Math.round(r.x), src:s};}
  }
  return best;
}
"""


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def load_env(p=os.path.join(ROOT, ".env")):
    d = {}
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d


def write_status(msg):
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write(msg + "\n")
    af.log(msg)


def fetch_from_db():
    import psycopg2
    e = load_env()
    conn = psycopg2.connect(
        host=e["SUPABASE_DB_HOST"], port=e["SUPABASE_DB_PORT"],
        user=e["SUPABASE_DB_USER"], password=e["SUPABASE_DB_PASSWORD"],
        dbname=e["SUPABASE_DB_NAME"], sslmode="require", connect_timeout=20)
    cur = conn.cursor()
    cur.execute("SELECT storage_url FROM character_assets WHERE key='jieun_base_front'")
    url = cur.fetchone()[0]
    conn.close()
    af.log(f"[1/6 DB] storage_url = {url}")
    urllib.request.urlretrieve(url, REF_LOCAL)
    af.log(f"[1/6 DB] 다운로드 완료 → {REF_LOCAL} ({os.path.getsize(REF_LOCAL)} bytes, md5={md5(REF_LOCAL)})")
    return REF_LOCAL


def download_new_tile(page, center, raw):
    with page.expect_download(timeout=30000) as dl:
        if not af.open_tile_menu(page, center):
            raise RuntimeError("새 타일 ⋮ 메뉴 열기 실패")
        af.click_text(page, "다운로드")
        page.wait_for_timeout(900)
        (af.click_text(page, "원본 크기") or af.click_text(page, "720p 원본 크기")
         or af.click_text(page, "원본") or af.click_text(page, "720p"))
    dl.value.save_as(raw)
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass


def main():
    try:
        os.remove(STATUS)
    except Exception:
        pass
    ref = fetch_from_db()

    # 기존 png md5 집합(스테일 캡처 검증용)
    existing = {}
    for f in glob.glob(os.path.join(ROOT, "home_vocab", "*.png")):
        if os.path.basename(f) == "jieun_jumping.png":
            continue
        try:
            existing[md5(f)] = os.path.basename(f)
        except Exception:
            pass

    lock = os.path.join(af.PROFILE, "SingletonLock")
    if os.path.exists(lock):
        try:
            os.remove(lock)
        except Exception:
            pass

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
            no_viewport=True, accept_downloads=True, downloads_path=af.DL_DIR,
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                  "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        if not af.open_new_project(page):
            write_status("[FAIL] 프로젝트 진입 실패")
            return 1
        af.set_image_mode(page)

        # 2) 더보기 → 입력창에 사진(레퍼런스) 넣기
        af.log("[2/6] 레퍼런스 사진 업로드(입력창에 넣기)")
        if not af.upload_image(page, os.path.abspath(ref)):
            write_status("[FAIL] 레퍼런스 업로드 실패")
            af.shot(page, "_jump_upload_fail")
            return 1
        page.wait_for_timeout(4000)
        try:
            page.screenshot(path=os.path.join(SHOTDIR, "_jump_1_uploaded.png"))
        except Exception:
            pass

        # 생성 '전' 타일 src 기록(= known). 업로드된 레퍼런스 타일도 여기 포함됨.
        known = page.evaluate(SRCS_JS) or []
        af.log(f"[3/6] 생성 전 타일 {len(known)}개 기록(known)")

        # 3) 스크립트(프롬프트) 추가 입력
        af.log("[4/6] 점프 스크립트 입력(클립보드 붙여넣기)")
        af.fill_prompt(page, PROMPT)
        page.wait_for_timeout(800)
        try:
            page.screenshot(path=os.path.join(SHOTDIR, "_jump_2_prompt.png"))
        except Exception:
            pass

        # 4) 생성
        if not af.generate(page):
            write_status("[FAIL] 생성 버튼 클릭 실패")
            af.shot(page, "_jump_generate_fail")
            return 1
        af.log("[5/6] 생성 클릭 — ~40초 대기 후 '왼편 새 타일' 출현 폴링")

        new_tile = None
        page.wait_for_timeout(38000)        # 이미지 ~40초
        for k in range(24):                 # 추가 최대 72초
            try:
                new_tile = page.evaluate(NEW_LEFT_JS, known)
            except Exception:
                new_tile = None
            if new_tile:
                af.log(f"  새 타일 출현(왼쪽 left={new_tile.get('left')}) — 3초 후 다운로드")
                break
            page.wait_for_timeout(3000)
        if not new_tile:
            write_status("[FAIL] 새 타일(왼편 최신) 미출현 — 생성 실패 추정")
            af.shot(page, "_jump_no_new_tile")
            return 1

        page.wait_for_timeout(3000)         # 완전 렌더 대기
        try:
            page.screenshot(path=os.path.join(SHOTDIR, "_jump_3_generated.png"))
        except Exception:
            pass

        # 5) 새 타일 다운로드(원본)
        raw = OUT + ".raw.png"
        try:
            download_new_tile(page, new_tile, raw)
        except Exception as ex:
            write_status(f"[FAIL] 새 타일 다운로드 실패: {str(ex)[:120]}")
            af.shot(page, "_jump_dl_fail")
            return 1

        # 6) 스테일 검증 + 저장(불투명 원본)
        from PIL import Image
        Image.open(raw).convert("RGBA").save(OUT)
        try:
            os.remove(raw)
        except Exception:
            pass
        new_md5 = md5(OUT)
        if new_md5 in existing:
            write_status(f"[STALE] 받은 이미지가 기존 '{existing[new_md5]}' 와 동일(md5={new_md5}) — "
                         f"잘못된 타일 캡처. 저장 취소.")
            af.shot(page, "_jump_stale")
            try:
                os.remove(OUT)
            except Exception:
                pass
            return 2
        write_status(f"[OK] 점프 사진 생성·저장 완료 → home_vocab/jieun_jumping.png "
                     f"({os.path.getsize(OUT)} bytes, md5={new_md5}, 기존과 중복 아님 ✔)")
        af.log("브라우저를 잠시 유지합니다(직접 확인용). 12분 후 자동 종료.")
        try:
            page.wait_for_timeout(720000)   # 12분 유지(닫아도 무방)
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
