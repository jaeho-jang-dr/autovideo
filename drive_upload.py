# -*- coding: utf-8 -*-
"""로그인된 크롬 프로필로 Google Drive(drjang00)에 파일 업로드.
사용: python drive_upload.py <파일경로> [폴더명] [--cdp]
  --cdp : 이미 떠 있는 크롬(9222)의 새 탭에서 업로드한다.
          ★Flow 작업 중에는 프로필이 잠겨 새 크롬을 못 띄우므로 이 모드를 쓴다.
업로드 후 공유링크는 사용자가 Drive에서 확인(또는 파일이 내 드라이브에 생김)."""
import sys, os, time
sys.path.insert(0,os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

ARGS=[a for a in sys.argv[1:] if not a.startswith("--")]
CDP="--cdp" in sys.argv
FILE=os.path.abspath(ARGS[0])
assert os.path.exists(FILE), FILE
FOLDER=ARGS[1] if len(ARGS)>1 else None
SZ=os.path.getsize(FILE)/1024/1024
print(f"업로드 대상: {FILE} ({SZ:.0f}MB)  폴더={FOLDER}  CDP={CDP}")

with sync_playwright() as pw:
    if CDP:
        br=pw.chromium.connect_over_cdp("http://localhost:9222")
        ctx=br.contexts[0]
        pg=ctx.new_page()
        pg.bring_to_front()
    else:
        ctx=pw.chromium.launch_persistent_context(af.PROFILE,channel="chrome",headless=False,locale="ko-KR",
            no_viewport=True,ignore_default_args=["--enable-automation"],
            args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
        pg=ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.set_default_timeout(45000)
    pg.goto("https://drive.google.com/drive/my-drive",wait_until="domcontentloaded")
    pg.wait_for_timeout(8000)
    # 폴더 지정 시 해당 폴더로 진입(더블클릭) 후 그 안에 업로드
    if FOLDER:
        entered=False
        for _ in range(2):
            try:
                tile=pg.get_by_text(FOLDER,exact=True).first
                tile.wait_for(state="visible",timeout=8000)
                tile.dblclick(); pg.wait_for_timeout(5000); entered=True; break
            except Exception as e:
                print("폴더 진입 재시도:",str(e)[:50]); pg.wait_for_timeout(2000)
        print(f"폴더 '{FOLDER}' 진입:",entered, "URL=",pg.url)
        if not entered: print("!! 폴더 진입 실패 — 루트에 업로드될 수 있음")
    # 신규 → 파일 업로드 → 파일선택
    clicked=False
    for nm in ["신규","새로 만들기","New"]:
        try:
            b=pg.get_by_role("button",name=nm).first
            if b.is_visible(timeout=2500): b.click(); clicked=True; break
        except Exception: pass
    if not clicked:
        try: pg.locator("div[role=button]:has-text('신규')").first.click(); clicked=True
        except Exception: pass
    print("신규 클릭:",clicked)
    pg.wait_for_timeout(1500)
    # 파일 업로드 메뉴 → 파일 선택창
    with pg.expect_file_chooser(timeout=20000) as fcinfo:
        done=False
        for nm in ["파일 업로드","파일 올리기","File upload"]:
            try:
                mi=pg.get_by_role("menuitem",name=nm).first
                if mi.is_visible(timeout=2500): mi.click(); done=True; break
            except Exception: pass
        if not done:
            for nm in ["파일 업로드","File upload"]:
                try: pg.get_by_text(nm,exact=False).first.click(); done=True; break
                except Exception: pass
    fc=fcinfo.value
    fc.set_files(FILE)
    print("파일 선택 완료 — 업로드 시작")
    # 업로드 완료 대기 (진행 토스트가 사라지거나 '업로드 완료' 표시)
    deadline=time.time()+ max(180, SZ*3)  # MB당 최대 3초
    ok=False
    while time.time()<deadline:
        pg.wait_for_timeout(5000)
        try:
            body=pg.inner_text("body")
        except Exception:
            body=""
        if "업로드 완료" in body or "uploads complete" in body.lower() or "1개 업로드 완료" in body:
            ok=True; break
        # 진행중 표시 없어지면 완료로 간주
        if ("업로드 중" not in body and "uploading" not in body.lower() and "남음" not in body) and time.time()>deadline-max(180,SZ*3)+40:
            pass
    print("업로드 완료 감지:",ok)
    pg.wait_for_timeout(3000)
    pg.screenshot(path="scratch/drive_upload_done.png")
    # ★CDP 모드에서는 사용자의 브라우저이므로 컨텍스트를 닫지 않는다(탭만 닫는다)
    if CDP:
        pg.close()
    else:
        ctx.close()
print("DONE")
