# -*- coding: utf-8 -*-
"""걷기 **동영상을 움직임 참조로** 붙여 다른 캐릭터의 걷기를 만든다.
   ★사장님 지시(2026-08-04): "걷기 동영상을 프롬프트로 못 주나?" → 준다. 그게 확실하다.
     말로 "걸어라"라고 설명하면 Veo 가 제자리 흔들림만 만들거나 팔다리를 뒤바꾼다
     (실측: 192프레임 동안 인물이 10px 만 움직였다 = 사실상 정지).

   절차: 프로젝트 이동 → 참조 정리 → **걷기 mp4 업로드해 프롬프트에 추가** →
         `@캐릭터` 참조 추가 → 동영상 설정 → 프롬프트 → 만들기 → 내려받기.
   업로드·참조·설정·생성 함수는 검증된 flow_cdp_pipeline / flow_make_group_w24 것을 그대로 쓴다.

   사용: python flow_walk_from_ref.py --char teacherjay
                --motion assets/videos/jieun_w19_walk_right.mp4
                --out W24/clips/tj_walk_r.mp4
"""
import argparse
import os
import subprocess
import time

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

import flow_cdp_pipeline as P
import flow_make_group_w24 as G

GEN_WAIT = 420
UPLOAD_WAIT_MS = 30000

DESC = {
    "teacherjay": "a cartoon man, bald head with a single curl of hair, blue and white checked "
                  "shirt with rolled sleeves, beige trousers, WHITE sneakers on both feet",
}


def log(m):
    print(m, flush=True)


def prompt_for(char):
    who = DESC.get(char, f"the character @{char}")
    return (
        f"Use the WALKING MOTION of the attached reference video exactly as it is - the same gait, "
        f"the same rhythm, the same arm and leg swing, the same number of strides, the same speed - "
        f"but replace the person with @{char}.\n"
        f"@{char} is {who}. Keep his face, hair, clothes, colours, flat cartoon style with clean "
        f"black outlines and his body proportions exactly as registered. His face keeps its "
        f"features: in side profile ONE dark dot EYE, an eyebrow, the nose and chin in profile and "
        f"a small smiling mouth, visible in every frame.\n"
        f"He walks to the RIGHT in full side profile, his LEFT side toward the camera. The near "
        f"(left) arm and near (left) leg stay in front of the body for the whole clip and NEVER swap "
        f"with the far ones. Exactly one head, two arms, two hands, two legs, two white sneakers.\n"
        f"BACKGROUND: pure flat white, unbroken, no floor line, no shadow, no scenery, no text, no "
        f"watermark. The whole body from head to shoes stays inside the frame with empty white space "
        f"above the head and below the shoes."
    )


def attach_media(pg, path):
    """+ 미디어 추가 → 미디어 업로드 → 파일 → 타일 ⋮ → 프롬프트에 추가 (검증된 절차 그대로)."""
    path = os.path.abspath(path)
    if not P.click_btn(pg, "^add\\n미디어 추가", label="미디어 추가(+)"):
        log("    ★'+' 버튼 없음")
        return False
    up = P.find_btn(pg, "미디어 업로드")
    if not up:
        log("    ★'미디어 업로드' 메뉴 없음")
        return False
    with pg.expect_file_chooser(timeout=15000) as fc:
        pg.mouse.click(up["x"], up["y"])
    fc.value.set_files(path)
    log(f"    업로드 {os.path.basename(path)} → {UPLOAD_WAIT_MS // 1000}초 대기")
    pg.wait_for_timeout(UPLOAD_WAIT_MS)
    tiles = P.media_tiles(pg)
    if not tiles:
        log("    ★업로드 타일이 뜨지 않음")
        return False
    t0 = tiles[0]
    pg.mouse.move(t0["x"], t0["y"])
    pg.wait_for_timeout(1500)
    if not P.click_btn(pg, "more_vert\\n더 생성하기", ymin=t0["y"] - 260, label="타일 ⋮"):
        log("    ★타일 ⋮ 없음")
        return False
    return P.click_btn(pg, "프롬프트에 추가", label="프롬프트에 추가")


def run(char, motion, out):
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    P.launch_chrome(os.path.abspath("assets/chrome_profile"))
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(P.CDP_URL)
        ctx = b.contexts[0]
        pg = next((p for p in ctx.pages if "/project/" in p.url), None) or ctx.pages[0]
        pg.bring_to_front()
        log(f"\n=== {char} 걷기 — 움직임 참조 {os.path.basename(motion)} ===")
        pg.goto(G.CHAR_PROJECT, wait_until="domcontentloaded")
        time.sleep(9)

        log("[1] 설정 — 동영상 / Veo 3.1 Lite / 16:9 / 8초")
        if not G.set_chip(pg):
            log("    ★동영상 모드 전환 실패 — 멈춘다")
            return False

        log(f"[2] 이전 참조 지우기 (현재 {G.refcount(pg)}개)")
        G.clear_refs(pg)

        log("[3] 걷기 동영상을 참조로 붙이기")
        if not attach_media(pg, motion):
            return False
        log(f"    참조 {G.refcount(pg)}개")

        log(f"[4] @{char} 캐릭터 참조 붙이기")
        G.add_ref(pg, char)
        n = G.refcount(pg)
        log(f"    참조 {n}개 (동영상 1 + 캐릭터 1 = 2 여야 한다)")
        if n < 2:
            log("    ★참조가 모자라다 — 생성하지 않고 멈춘다")
            return False

        pr = prompt_for(char)
        log(f"[5] 프롬프트 입력 ({len(pr)}자)")
        box = pg.locator("div[role='textbox'][contenteditable='true']").first
        box.click()
        time.sleep(0.4)
        pg.keyboard.press("Control+a")
        pg.keyboard.press("Delete")
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Set-Clipboard -Value ([Console]::In.ReadToEnd())"],
                       input=pr, text=True, encoding="utf-8", check=False)
        box.press("Control+v")
        time.sleep(2)

        before = set(pg.evaluate(G.JS_SRCS))
        log(f"[6] 만들기 (기존 동영상 {len(before)}개 기억)")
        if not P.click_btn(pg, "arrow_forward", label="만들기"):
            log("    ★'만들기' 클릭 실패")
            return False
        log(f"[7] 생성 대기 (최대 {GEN_WAIT}초)")
        src = None
        for i in range(GEN_WAIT // 15):
            time.sleep(15)
            new = set(pg.evaluate(G.JS_SRCS)) - before
            if new:
                src = sorted(new)[0]
                log(f"    {(i + 1) * 15}s — 새 동영상 확인")
                break
            if i and i % 4 == 0:
                log(f"    {(i + 1) * 15}s …")
        if not src:
            log("★생성 실패(시간 초과)")
            return False
        log("[8] 내려받기")
        if not G.fetch_video(pg, out, src):
            return False
        log(f"✅ {out}  {os.path.getsize(out) // 1024}KB")
        return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--char", default="teacherjay")
    ap.add_argument("--motion", default="assets/videos/jieun_w19_walk_right.mp4")
    ap.add_argument("--out", default="W24/clips/tj_walk_r.mp4")
    a = ap.parse_args()
    raise SystemExit(0 if run(a.char, a.motion, a.out) else 1)
