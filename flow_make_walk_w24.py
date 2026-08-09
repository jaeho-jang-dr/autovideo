# -*- coding: utf-8 -*-
"""붙여 둔 측면컷 참조로 **8초 걷기 영상** 만들기.
   ★사장님 지시(2026-08-04): "만들어지면 그 영상을 프롬프트에 추가하고 다시 동영상으로 고친 다음
     프롬프트 넣고 실행." — 참조는 **사장님이 이미 붙이셨다.** 지우지 않는다.

   절차: 설정 칩을 동영상/Veo 3.1 Lite/16:9/8초로 되돌림 → 걷기 프롬프트 → 만들기 → 내려받기.
   사용: python flow_make_walk_w24.py [--out W24/clips/tj_walk_r.mp4]
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

PROMPT = (
    "The exact character in the reference picture, unchanged: same face, same bald head with the "
    "single curl of hair, same blue and white checked shirt with rolled sleeves, same beige "
    "trousers, same WHITE sneakers on BOTH feet, same flat cartoon style with clean black outlines "
    "and the same body proportions and height.\n"
    "★FACE: his face is always drawn with features - in this right-facing side profile ONE EYE is "
    "clearly visible as a dark dot, together with the eyebrow, the nose and chin in profile, and a "
    "small smiling MOUTH. The eye is open and looking ahead in every frame; it never disappears and "
    "the face is never left blank.\n"
    "ACTION: he really WALKS FORWARD to the RIGHT, travelling across the ground in a perfect side "
    "profile with a relaxed, natural human gait - about three unhurried strides in eight seconds. "
    "Each step: the heel touches down first, the body rolls over the foot, then the toe pushes off "
    "and that leg swings through with the knee bending. The arms swing gently in opposition to the "
    "legs - right leg forward, left arm forward. The whole body rises and falls very slightly with "
    "each step. Head level, facing right, gentle friendly smile. BOTH HANDS ARE EMPTY.\n"
    "★The feet must GRIP the ground - never sliding, never skating, never moon-walking, never "
    "marching stiffly on the spot. He is genuinely walking, not shuffling in place.\n"
    "ANATOMY LOCK: exactly ONE head, ONE neck, TWO arms with two elbows, TWO hands, TWO legs with "
    "two knees, TWO feet each wearing a WHITE sneaker. No extra limbs, no extra legs, no duplicated "
    "feet, no floating parts. Knees bend backward only, elbows forward only.\n"
    "★SIDE LOCK (most important): he faces RIGHT, so his LEFT side is toward the camera for the "
    "whole eight seconds. His LEFT arm and LEFT leg are the NEAR limbs, drawn in front of his body; "
    "his RIGHT arm and RIGHT leg are the FAR limbs, drawn behind his body and slightly overlapped by "
    "it. These NEVER swap: the near arm stays the near arm and the near leg stays the near leg from "
    "the first frame to the last. Limbs never jump to the other side of the body, never cross "
    "through the torso, never change which one is in front. The near-side limbs are always fully "
    "visible; the far-side limbs are always partly hidden behind the body.\n"
    "CAMERA: a smooth TRACKING SHOT - the camera glides along beside him at exactly his walking "
    "speed, holding him centred in the frame at chest height in full side view. Because the "
    "background is plain white, only he moves. No pan, no zoom, no shake, no rotation.\n"
    "FRAMING: shot wide. His head is in the upper fifth of the frame and his SHOES sit well ABOVE "
    "the bottom edge with a wide empty band of white beneath them. The whole body, both hands and "
    "both shoes stay inside the frame at all times.\n"
    "BACKGROUND: pure flat white (#FFFFFF), unbroken edge to edge. No floor line, no horizon, no "
    "wall, no stripe, no gradient, no scenery, no props, no shadow, no text, no watermark."
)


def log(m):
    print(m, flush=True)


def run(out, skip_chip=False):
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    P.launch_chrome(os.path.abspath("assets/chrome_profile"))
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(P.CDP_URL)
        ctx = b.contexts[0]
        pg = next((p for p in ctx.pages if "/project/" in p.url), None) or ctx.pages[0]
        pg.bring_to_front()
        time.sleep(1.5)

        log("\n=== 티쳐제이 걷기 8초 ===")
        log(f"[0] 붙어 있는 참조 {G.refcount(pg)}개 — ★지우지 않는다(사장님이 붙이심)")
        if skip_chip:      # ★사장님이 이미 동영상으로 바꿔 두셨다 — 건드리면 되레 틀어진다
            log(f"[1] 설정 — 건너뜀 (현재 칩: {G.chip_text(pg)[:40]!r})")
        elif not G.set_chip(pg):
            log("    ★동영상 모드 전환 실패 — 멈춘다")
            return False

        log(f"[2] 프롬프트 입력 ({len(PROMPT)}자)")
        box = pg.locator("div[role='textbox'][contenteditable='true']").first
        box.click()
        time.sleep(0.4)
        pg.keyboard.press("Control+a")
        pg.keyboard.press("Delete")
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Set-Clipboard -Value ([Console]::In.ReadToEnd())"],
                       input=PROMPT, text=True, encoding="utf-8", check=False)
        box.press("Control+v")
        time.sleep(2)

        before = set(pg.evaluate(G.JS_SRCS))
        log(f"[3] 만들기 (기존 동영상 {len(before)}개 기억)")
        if not P.click_btn(pg, "arrow_forward", label="만들기"):
            log("    ★'만들기' 클릭 실패")
            return False
        log(f"[4] 생성 대기 (최대 {GEN_WAIT}초)")
        src = None
        for i in range(GEN_WAIT // 15):
            time.sleep(15)
            now = set(pg.evaluate(G.JS_SRCS))
            new = now - before
            if new:
                src = sorted(new)[0]
                log(f"    {(i + 1) * 15}s — 새 동영상 확인")
                break
            if i and i % 4 == 0:
                log(f"    {(i + 1) * 15}s …")
        if not src:
            log("★생성 실패(시간 초과)")
            return False
        log("[5] 내려받기")
        if not G.fetch_video(pg, out, src):
            return False
        mb = os.path.getsize(out) // 1024
        log(f"✅ {out}  {mb}KB")
        return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="W24/clips/tj_walk_r.mp4")
    ap.add_argument("--skip-chip", action="store_true")
    a = ap.parse_args()
    raise SystemExit(0 if run(a.out, a.skip_chip) else 1)
