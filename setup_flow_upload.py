# -*- coding: utf-8 -*-
"""반자동: 키프레임을 Flow에 업로드+첫프레임 지정+스크립트 붙여넣기까지만 하고 브라우저를 열어둔다.
사용자가 [생성]을 누르고 완성 후 [다운로드 → 원본 크기]를 클릭하면, 그 다운로드를 낚아채
자동으로 지정 경로(scene_N.mp4)로 저장한다.
사용: python setup_flow_upload.py <KEY> [hold_seconds]     예) python setup_flow_upload.py S02
  KEY(S02 등)로 키프레임(keyframes/S##.png), 출력명(sejong_main_kf/scene_N.mp4), 모션(kf_motions.tsv)을 자동 조회.
"""
import os, sys, time
ROOT = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); os.chdir(ROOT)
import autoveo_flow as af
from playwright.sync_api import sync_playwright

KEY   = sys.argv[1].upper().strip()                     # 예: S02
HOLD  = int(sys.argv[2]) if len(sys.argv) > 2 else 1800
n     = int(KEY[1:])
img   = os.path.abspath(os.path.join("sejong_film", "main", "keyframes", f"{KEY}.png"))
out   = os.path.abspath(os.path.join("sejong_main_kf", f"scene_{n}.mp4"))
motion = ""
for line in open(os.path.join("sejong_film", "main", "kf_motions.tsv"), encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if len(p) >= 2 and p[0] == KEY:
        motion = p[1]; break
if not motion:
    print(f"[ERR] 모션 없음: {KEY}"); sys.exit(1)
os.makedirs(os.path.dirname(out), exist_ok=True)
os.makedirs(af.DL_DIR, exist_ok=True)

print(f"[SETUP] keyframe={img}")
print(f"[SETUP] out={out}")

af.force_kill_profile_chrome(); time.sleep(3)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(
        af.PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
        accept_downloads=True, downloads_path=af.DL_DIR,
        ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR", "--disable-gpu"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()

    saved = {"done": False}
    def on_dl(d):
        try:
            tmp = os.path.join(af.DL_DIR, "_manual_dl.bin")
            d.save_as(tmp)
            if af.is_mp4(tmp):
                import shutil; shutil.move(tmp, out)
                print(f"SAVED {out}")
                saved["done"] = True
            else:
                print("DL_NOT_MP4 (썸네일 등 무시)")
        except Exception as e:
            print("DL_ERR", str(e)[:120])
    page.on("download", on_dl)

    ok = False
    if af.open_new_project(page):
        if af.upload_image(page, img):
            page.wait_for_timeout(9000)
            animated = False
            for _ in range(4):
                if af.animate_image(page): animated = True; break
                page.wait_for_timeout(4000)
            if animated:
                page.wait_for_timeout(1500)
                af.fill_prompt(page, motion)
                ok = True
                print("READY  ← 브라우저에서 [생성] 누르고, 완성되면 [다운로드→원본 크기] 클릭하세요")
            else:
                print("ANIMATE_FAIL")
        else:
            print("UPLOAD_FAIL")
    else:
        print("PROJECT_FAIL")

    # 브라우저 열어둔 채 대기(이벤트 펌핑). 다운로드 낚아채면 조기 종료.
    waited = 0
    while waited < HOLD * 1000 and not saved["done"]:
        page.wait_for_timeout(3000); waited += 3000
    if saved["done"]:
        print("DONE_SAVED")
    else:
        print("HOLD_TIMEOUT (다운로드 감지 못함)")
