# -*- coding: utf-8 -*-
"""★W23 배경 동영상 1개 생성 — 이미지 업로드 없이 프롬프트만으로 (2026-07-27).

`flow_make_clip.py`(캐릭터 동작)와 다른 점: **업로드·타일·⋮ '프롬프트에 추가' 단계가 전부 없다.**
배경은 참조 이미지가 필요 없으므로 새 세션에서 곧바로 프롬프트를 넣고 만든다.

★★사장님 확정 절차 (2026-07-27 실측 성공 — 이대로만, 바꾸지 말 것):
 1. 리셋 — 크롬 전부 kill → flow_driver 새로 기동 → 새 프로젝트(새 세션)
    (리셋 코드는 flow_make_clip.py 의 reset_and_start() 를 그대로 쓴다)
 2. 하단 프롬프트 창의 **동영상 설정 칩**(`동영상 · 8s…`)을 눌러 옵션 메뉴를 열고
    **16:9** 와 **Veo 3.1 - Lite** 를 선택한다. 칩이 `crop_16_9` 로 바뀌면 성공
    ※ 리셋 직후엔 하단 바가 아직 안 그려져 있다 → 칩이 보일 때까지 몇 번 다시 찍는다
 3. 프롬프트 창 클릭 → 프롬프트 붙여넣기 → 우측 화살표(만들기) **중심 좌표** 클릭
 4. **90초 대기** + vidstatus 로 생성 확인
 5. **왼편 상단 타일 클릭 → 편집 화면(/edit/) 진입 → 우상단 아래화살표(다운로드)**
    → 메뉴 없이 바로 mp4 가 debug/downloads 에 떨어진다 (정지 이미지와 달리 1K/2K/4K 메뉴 없음)

실측 결과: 1280x720 · 8초 · 192프레임 · 약 7MB, 다운로드 5초 내

사용:
  python flow_make_bgmv.py gate_in
  python flow_make_bgmv.py --list
"""
import argparse
import glob
import os
import re
import shutil
import sys
import time

import flow_make_clip as F

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
OUT_DIR = "W23/bg_clips"
DL_DIR = "debug/downloads"

TAIL = ("Pastel storybook illustration, bold clean outlines, flat cel shading, warm natural light. "
        "Absolutely no text, no letters, no numbers, no signage lettering, no logos, no watermark. "
        "No human figures, no cartoon characters. Keep the left side of the frame visually calm and "
        "simple. The ground runs continuously from edge to edge across the bottom so a figure could "
        "walk along it. 16:9, 1280x720.")

# W23_scenario.md G-1 — 배경 동영상 6개(0-2초 시작 → 2-6초 이동/줌 → 6-8초 끝 구도)
BGS = [
    ("gate_in",
     "0-2s: straight-on wide shot of a grand theme-park entrance arch with a clock tower, seen from "
     "outside across the paved forecourt. 2-6s: the camera accelerates forward and flies through the "
     "arch, the arch structure sweeping past overhead and out of frame. 6-8s: the camera decelerates "
     "and settles into a locked wide view of the inner plaza - a broad tulip-bed plaza with a low stone "
     "flowerbed rail on the left and a large blank park map board on the right. Location changes from "
     "outside the gate to inside the plaza. Bold forward dolly, no Ken Burns."),
    ("to_garden",
     "0-2s: a wide tulip-bed plaza. 2-6s: the camera whips right and rushes low across the flowerbeds "
     "toward an arched flower tunnel, blossoms streaking past on both sides. 6-8s: it snaps to a stop "
     "inside the tunnel, locked on a wide view of the arched flower walkway - an ornamental lamppost on "
     "the left, a wooden bench on the right. The location changes from open plaza to inside the tunnel."),
    # ★탈선 금지 — 열차는 매 프레임 레일 위에만, 다이내믹은 카메라가 담당(2026-07-27 사장님 지시)
    ("coaster_rush",
     "0-2s: a distant wide shot of a tall wooden roller coaster standing above a garden, the track "
     "curving down from the lift hill. 2-5s: a coaster train descends the track, its wheels locked on "
     "the rails the whole time and following the curve of the track exactly, while the camera races "
     "alongside and swings with it. 5-8s: the camera crash-zooms in hard and stops right beside the "
     "track - the wooden rail and support beams now fill the frame, a viewing railing on the left, a "
     "thick timber support post on the right. STRICT: the train stays on the rails at every single "
     "frame - it never derails, never leaves the track, never flies or floats through the air, and "
     "never passes through the structure. The wooden track stays intact and unbroken, no collapsing "
     "beams, no flying debris. The dramatic change comes only from the camera move (far wide to "
     "extreme close), not from the train breaking away."),
    ("to_carousel",
     "0-2s: an arched flower tunnel. 2-6s: the camera lifts, banks left and flies over hedges and lawns "
     "toward a carousel plaza, the scenery below streaking past. 6-8s: it lands and locks into a wide "
     "front view of the carousel plaza - the carousel filling the centre and right, a low painted fence "
     "on the left, a blank plaza notice board on the right. The location changes from garden to plaza."),
    ("parade_fills",
     "0-2s: a completely empty parade street lined with flower planters, quiet and still. 2-6s: a "
     "flower-covered parade float and a line of decorated carts surge in from the right and roll toward "
     "the camera, ribbons streaming, confetti bursting into the air, the street rapidly filling. 6-8s: "
     "the parade occupies the whole middle ground and the street is packed with colour, settling into a "
     "locked wide shot - a street fence on the left, a flower planter stand on the right. The scene "
     "transforms from empty to full."),
    ("night_finale",
     "0-2s: the plaza at sunset, orange sky. 2-5s: the sky darkens through pink to deep blue while "
     "festoon lamps and building lights switch on in sequence across the plaza. 5-8s: fireworks burst "
     "open across the whole night sky above the silhouette of the distant wooden coaster, the plaza "
     "glowing. Day turns to night inside one clip."),
]
BG_MAP = dict(BGS)


def log(m):
    print(m, flush=True)


def sync_index():
    files = glob.glob("debug/cmd/*.txt")
    F._n[0] = max((int(re.findall(r"(\d+)\.txt$", p.replace("\\", "/"))[0]) for p in files), default=0)


def find_btn(dump, needle):
    for e in dump.get("els", []):
        if needle in ((e.get("text") or "") + " " + (e.get("aria") or "")):
            return e
    return None


def center(e):
    return e["x"] + e["w"] // 2, e["y"] + e["h"] // 2


def run(key):
    motion = BG_MAP.get(key)
    if not motion:
        raise SystemExit(f"모르는 배경 키: {key} (가능: {', '.join(k for k, _ in BGS)})")
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.abspath(f"{OUT_DIR}/bg_w23_{key}.mp4")
    prompt = f"{motion} {TAIL}"

    if not F.reset_and_start():
        return False
    sync_index()

    log("[2] 동영상 설정 — 애셋 / 16:9 / 1개 / Veo 3.1 Lite")
    # ★리셋 직후에는 하단 프롬프트 바가 아직 안 그려져 있다 → 뜰 때까지 몇 번 다시 찍는다
    chip, d = None, {}
    for _ in range(5):
        d = F.shot(10)
        chip = find_btn(d, "동영상 ·")
        if chip:
            break
        F.cmd("wait|5", 15)
    if not chip:
        log("★설정 칩 없음"); return False
    log(f"     현재 설정: {((chip.get('text') or '')).strip()[:40]!r}")
    F.cmd("clickxy|%d|%d" % center(chip), 10)
    d = F.shot(8)
    for want in ("16:9", "Veo 3.1 - Lite"):
        item = find_btn(d, want)
        if item:
            F.cmd("clickxy|%d|%d" % center(item), 8)
            d = F.shot(8)
            log(f"     {want} 선택")
        else:
            log(f"     ({want} 항목 못 찾음 — 현재 설정 유지)")
    F.cmd("key|Escape", 6)
    d = F.shot(8)
    chip = find_btn(d, "동영상 ·")
    log(f"     확정 설정: {((chip.get('text') or '') if chip else '?').strip()[:40]!r}")

    log("[3] 프롬프트 입력 + 실행")
    box = next((e for e in d.get("els", []) if e.get("role") == "textbox"), None)
    if not box:
        log("★프롬프트 입력창 없음"); return False
    F.cmd("clickxy|%d|%d" % center(box), 8)
    F.cmd(f"fillprompt|{prompt}", 12)
    d = F.shot(8)
    arrow = find_btn(d, "arrow_forward")
    if not arrow:
        log("★실행(만들기) 버튼 없음"); return False
    F.cmd("clickxy|%d|%d" % center(arrow), 10)

    log("[4] 90초 대기 + 생성 모니터링")
    F.cmd("wait|90", 140)
    for i in range(4):
        F.cmd("vidstatus", 15)
        if F.find(lambda e: e.get("tag") == "VIDEO" and e.get("w", 0) > 100) or F.vidstatus_done():
            log("     완성 동영상 타일 확인"); break
        F.cmd("wait|15", 35)
    else:
        log("★동영상 타일 안 뜸 — 생성 실패"); return False

    # ★실측 확정 경로(2026-07-27): grabvideo 는 이 화면에서 안 먹는다.
    #   **왼편 상단 타일을 클릭해 편집 화면(/edit/)으로 들어간 뒤**, 우상단 다운로드 버튼을 누르면
    #   메뉴 없이 곧바로 파일이 떨어진다(동영상은 1K/2K/4K 메뉴가 없다).
    log("[5] 왼편 상단 타일 클릭 → 편집 화면 → 우상단 다운로드")
    t0 = time.time()
    d = F.shot(10)
    tiles = [e for e in d.get("els", []) if e.get("tag") in ("IMG", "VIDEO") and e.get("w", 0) > 100]
    if not tiles:
        log("★타일 없음"); return False
    t = sorted(tiles, key=lambda e: (e["y"], e["x"]))[0]
    F.cmd("clickxy|%d|%d" % center(t), 12)
    d = F.shot(8)
    if "/edit/" not in d.get("url", ""):
        log("★편집 화면 진입 실패"); return False
    dl = find_btn(d, "다운로드")
    if not dl:
        log("★다운로드 버튼 없음"); return False
    before = set(os.listdir(DL_DIR)) if os.path.isdir(DL_DIR) else set()
    F.cmd("clickxy|%d|%d" % center(dl), 12)
    for _ in range(20):
        time.sleep(1.5)
        new = [f for f in os.listdir(DL_DIR) if f not in before]
        if new:
            src = max((os.path.join(DL_DIR, f) for f in new), key=os.path.getmtime)
            if os.path.getsize(src) > 500_000:
                shutil.copyfile(src, out)
                log(f"     다운로드 구간 {time.time()-t0:.1f}s")
                log(f"✅ 저장: {out} ({os.path.getsize(out)//1024}KB)")
                return True
    log("★다운로드 실패")
    return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("key", nargs="?")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.key:
        for i, (k, m) in enumerate(BGS):
            mark = "有" if os.path.exists(f"{OUT_DIR}/bg_w23_{k}.mp4") else " "
            print(f"{i+1} [{mark}] {k:14s} {m[:70]}…")
        sys.exit(0)
    sys.exit(0 if run(a.key) else 1)
