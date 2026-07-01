# -*- coding: utf-8 -*-
"""
[단계 검증용] DB에서 지은 사진을 가져와 Google Flow 입력란에 올리는 것까지만 수행.
생성(만들기)은 하지 않는다. 업로드 후 브라우저를 띄운 채 대기(유지)한다.

순서:
  1) Supabase DB(character_assets)에서 jieun_base_front 의 storage_url 조회 → 로컬 다운로드
  2) 헤드드 크롬(assets/chrome_profile)으로 Flow 진입 → 이미지 모드 → 레퍼런스 업로드
  3) 입력란에 사진이 올라간 화면 스크린샷 저장 + 상태파일 기록
  4) 브라우저를 닫지 않고 대기(사용자가 직접 확인)

실행(백그라운드 권장):
  python scratch/flow_load_photo.py
"""
import os
import sys
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
SHOT_PATH = os.path.join(ROOT, "scratch", "flow_photo_loaded.png")
STATUS = os.path.join(ROOT, "scratch", "flow_load_status.txt")


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
    """1) DB에서 지은 정면 사진 storage_url 조회 → 다운로드."""
    import psycopg2
    e = load_env()
    conn = psycopg2.connect(
        host=e["SUPABASE_DB_HOST"], port=e["SUPABASE_DB_PORT"],
        user=e["SUPABASE_DB_USER"], password=e["SUPABASE_DB_PASSWORD"],
        dbname=e["SUPABASE_DB_NAME"], sslmode="require", connect_timeout=20)
    cur = conn.cursor()
    cur.execute("SELECT storage_url FROM character_assets WHERE key='jieun_base_front'")
    row = cur.fetchone()
    conn.close()
    if not row:
        raise RuntimeError("DB에 jieun_base_front 레코드 없음")
    url = row[0]
    af.log(f"[DB] storage_url = {url}")
    urllib.request.urlretrieve(url, REF_LOCAL)
    sz = os.path.getsize(REF_LOCAL)
    if open(REF_LOCAL, "rb").read(8) != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("다운로드 파일이 PNG가 아님")
    af.log(f"[DB] 다운로드 완료 → {REF_LOCAL} ({sz} bytes)")
    return REF_LOCAL


def main():
    try:
        os.remove(STATUS)
    except Exception:
        pass
    ref = fetch_from_db()

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
            write_status("[FAIL] 프로젝트/컴포저 진입 실패")
            page.wait_for_timeout(600000)
            return 1
        af.set_image_mode(page)

        if not af.upload_image(page, os.path.abspath(ref)):
            write_status("[FAIL] 이미지 업로드 실패")
            af.shot(page, "flow_load_upload_fail")
            page.wait_for_timeout(600000)
            return 1

        page.wait_for_timeout(3500)   # 업로드 타일 렌더 대기
        try:
            page.screenshot(path=SHOT_PATH)
        except Exception as ex:
            af.log(f"[SHOT] 스크린샷 예외: {ex}")
        write_status(f"[OK] DB 사진을 Flow 입력란에 업로드 완료 | ref={os.path.basename(ref)} "
                     f"| screenshot={SHOT_PATH}")
        af.log("브라우저를 닫지 않고 대기합니다(최대 30분). 확인 후 알려주세요.")
        page.wait_for_timeout(1800000)   # 30분 유지 — 사용자가 직접 확인
    return 0


if __name__ == "__main__":
    sys.exit(main())
