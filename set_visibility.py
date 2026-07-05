# -*- coding: utf-8 -*-
"""영상 공개상태를 일부공개(Unlisted)로 게시. 사용: python set_visibility.py <video_id> <tag>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
VID = sys.argv[1]; TAG = sys.argv[2]
SH = "scratch/yt"
def log(m): print(m, flush=True)
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
    # 초안이면 '초안 수정' 클릭해 마법사 열기
    try:
        pg.get_by_text("초안 수정", exact=True).first.click(timeout=6000); pg.wait_for_timeout(4000); log("초안 수정 열기")
    except Exception as e: log("초안수정 없음(이미 게시본?) " + str(e)[:40])
    # 공개 상태 단계로 이동: 다음 버튼 반복(일부공개 라디오 보일 때까지)
    reached = False
    for i in range(5):
        try:
            if pg.get_by_role("radio", name="일부공개").first.is_visible(timeout=2000):
                reached = True; break
        except Exception: pass
        try: pg.locator("#next-button, ytcp-button:has-text('다음')").first.click(timeout=6000); pg.wait_for_timeout(2500); log(f"다음{i+1}")
        except Exception as e: log(f"다음{i+1} 실패 " + str(e)[:40])
    pg.wait_for_timeout(800); pg.screenshot(path=f"{SH}/v_{TAG}_1.png")
    # 일부 공개(UNLISTED) 선택
    try:
        pg.locator("tp-yt-paper-radio-button[name='UNLISTED']").first.click(timeout=6000); log("일부공개(UNLISTED) 선택"); pg.wait_for_timeout(1000)
    except Exception as e:
        try: pg.get_by_text("일부 공개", exact=True).first.click(timeout=4000); log("일부공개(text)")
        except Exception as e2: log("일부공개 실패 " + str(e)[:50])
    pg.screenshot(path=f"{SH}/v_{TAG}_2.png")
    # 저장(게시)
    try:
        pg.locator("#done-button").first.click(timeout=8000); log("저장(게시) 클릭"); pg.wait_for_timeout(6000)
    except Exception as e: log("저장 실패 " + str(e)[:50])
    pg.screenshot(path=f"{SH}/v_{TAG}_3.png")
    log(f"VIS_{TAG}_DONE"); pg.wait_for_timeout(2500); ctx.close()
print("END")
