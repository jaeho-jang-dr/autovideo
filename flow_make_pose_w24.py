# -*- coding: utf-8 -*-
"""★W24 캐릭터 가이드 — 측면/후면 생성 (나노 바나나 경로, 2026-07-28).

`flow_make_pose.py` 의 **절차를 그대로** 쓰고 대상만 W24로 바꿨다(주차별 복제 관례).
정면 이미지를 가이드로 올려 **같은 캐릭터의 측면·후면**을 뽑는다.
Flow 캐릭터 등록(정면·측면·후면 3장)에 쓸 기준 이미지다.

사용:
  python flow_make_pose_w24.py injun side
  python flow_make_pose_w24.py injun back
  python flow_make_pose_w24.py --list
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
# 캐릭터별 정면 가이드(등록 자산에서 가져온 실제 경로)
GUIDES = {
    # ★사장님 확정 2026-07-28 — 전부 '팔 내린 정면' 기준
    "stickman":    "assets/graphics/stickman_standing.png",        # W1
    "zolla_girl":  "assets/graphics/poses/stickman_zw_base.png",   # W5
    "zolla_man":   "assets/graphics/poses/zollaman_base.png",      # W6
    "jieun":       "assets/graphics/poses/jieun_w13_base.png",     # 노란 원피스
    "injun":       "assets/graphics/poses/injun_w10_base.png",     # 해상도 큰 쪽
    "madam_jay":   "assets/graphics/poses/mj_w14_base.png",
    "teacher_jay": "assets/graphics/poses/tj_w17_bow.png",
}
OUT_DIR = "W24/guides"
DL_DIR = "debug/downloads"

CHAR = ("Keep this exact character unchanged - same face, same hair, same clothes and colours, the "
        "same drawing style with clean black outlines, the same body proportions and the same height "
        "as the reference picture. Only the pose and the viewing angle change. "
        "★STANCE: standing straight at attention with BOTH ARMS HANGING RELAXED DOWN ALONG THE SIDES "
        "of the body, hands open and empty, feet together and flat on the ground. Do not raise, bend "
        "or spread the arms. Neutral calm expression. "
        "Exactly one head, two arms with two hands (five fingers each) and two legs - no extra or "
        "missing limbs. The whole body from head to shoes is fully inside the frame, centred, "
        "plain pure white background, no shadow, no ground line, no extra objects, no other "
        "characters, no text.")

# (키, 각도 설명) — Flow 캐릭터 등록용 3종 중 정면을 제외한 둘
POSES = [
    ("front", "the character faces the camera straight on, front view, looking directly at the viewer. "
              "★Draw it as a BOLD, THICK BLACK INK line drawing on a pure white background - the lines "
              "must be clearly visible and heavy, like a marker pen, not thin or faint. Solid black "
              "strokes, high contrast"),
    ("side",  "the character is turned ninety degrees to the viewer's right, shown in full side "
              "profile: one shoulder toward the camera, the nose and chin in profile, looking straight "
              "ahead to the right"),
    ("back",  "the character is turned completely away from the camera, seen from directly behind: "
              "only the back of the head and the back of the clothes are visible, no face at all"),
]
POSE_MAP = dict(POSES)


def log(m):
    print(m, flush=True)


def sync_index():
    """드라이버 명령 인덱스를 debug/cmd 의 최대 번호에 맞춘다(어긋나면 드라이버가 멈춘다)."""
    files = glob.glob("debug/cmd/*.txt")
    n = max((int(re.findall(r"(\d+)\.txt$", p.replace("\\", "/"))[0]) for p in files), default=0)
    F._n[0] = n
    return n


def find_btn(dump, needle):
    for e in dump.get("els", []):
        t = (e.get("text") or "") + " " + (e.get("aria") or "")
        if needle in t:
            return e
    return None


def center(e):
    return e["x"] + e["w"] // 2, e["y"] + e["h"] // 2


def run(char, key, do_reset=True):
    motion = POSE_MAP.get(key)
    if not motion:
        raise SystemExit(f"모르는 각도: {key} (가능: {', '.join(k for k, _ in POSES)})")
    GUIDE = GUIDES.get(char)
    if not GUIDE:
        raise SystemExit(f"모르는 캐릭터: {char} (가능: {', '.join(GUIDES)})")
    os.makedirs(OUT_DIR, exist_ok=True)
    out = f"{OUT_DIR}/{char}_{key}.png"
    prompt = f"{CHAR} View: {motion}."

    # ★리셋은 매번 한다(사장님 확정). 노리셋으로 이어붙이면 지난 이미지가 남아 타일 좌표가 밀리고
    #   더블클릭이 빗나가 실패한다 — 2026-07-27 실측으로 확인, 그 분기는 제거했다.
    if do_reset and not F.reset_and_start():
        return False
    sync_index()

    # ★사장님 실측(2026-07-27): 업로드하면 **15~20초 안에** 타일이 뜬다.
    #   예전엔 30초 대기 + shot 루프라 더블클릭이 55초에 걸렸다 → **업로드 후 약 25초**로 당긴다.
    t_up = time.time()
    log(f"[2] 업로드 {GUIDE} → 18초 대기(타일은 15~20초에 뜬다)")
    F.cmd(f"upload|{GUIDE}", 40)
    F.cmd("wait|18", 30)
    tile = None
    for _ in range(4):
        F.shot(10)
        tile = F.find(lambda e: e.get("tag") == "IMG" and e.get("w", 0) > 100)
        if tile:
            break
        F.cmd("wait|5", 15)
    if not tile:
        log("★업로드 타일 없음"); return False
    tx, ty = center(tile)
    log(f"     타일 ({tile['x']},{tile['y']}) {tile['w']}x{tile['h']} → 중앙 {tx},{ty} "
        f"(업로드 후 {time.time()-t_up:.0f}초)")

    log("[3] ★타일 더블클릭 → 이미지 편집기(나노 바나나) 진입")
    F.cmd(f"hover|{tx}|{ty}", 10)
    F.cmd(f"dblclick|{tx}|{ty}", 20)
    F.cmd("wait|5", 15)
    d = F.shot(10)
    if "/edit/" not in d.get("url", ""):
        log("★편집기 진입 실패(더블클릭이 안 먹었다)"); return False
    log("     편집기 진입 확인")

    # ★비율은 확인만 한다 — 사장님 확정: 어차피 투명컷 뜨고 키를 맞추므로 3:4 든 9:16 이든 상관없다.
    chip = find_btn(d, "Nano Banana")
    log(f"[4] 설정 확인: {((chip.get('text') or '') if chip else '?')[:40]!r}")

    log("[5] 프롬프트 입력 + 실행")
    box = next((e for e in d.get("els", []) if e.get("role") == "textbox"), None)
    if not box:
        log("★프롬프트 입력창 없음"); return False
    F.cmd("clickxy|%d|%d" % center(box), 8)
    F.cmd(f"fillprompt|{prompt}", 12)
    d = F.shot(8)
    arrow = find_btn(d, "arrow_forward")
    if not arrow:
        log("★실행(만들기) 버튼 없음"); return False
    n_before = len([e for e in d.get("els", []) if e.get("tag") == "IMG" and e.get("w", 0) > 100])
    F.cmd("clickxy|%d|%d" % center(arrow), 10)

    # ★생성 모니터링(사장님 강조) — 40초 뒤부터 이력 타일이 늘었는지 본다. 안 늘면 실패다.
    log("[6] 생성 대기 40초 + 모니터링")
    F.cmd("wait|40", 65)
    made = False
    for i in range(6):
        d = F.shot(10)
        n_now = len([e for e in d.get("els", []) if e.get("tag") == "IMG" and e.get("w", 0) > 100])
        if n_now > n_before:
            log(f"     생성 확인(이력 타일 {n_before}→{n_now})"); made = True; break
        F.cmd("wait|10", 25)
    if not made:
        log("★생성 안 됨(이력 타일 그대로)"); return False

    # ★다운로드 버튼은 **메뉴를 여는 버튼**이다 → '1K 원본 크기'까지 눌러야 파일이 떨어진다(실측).
    log("[7] 우상단 다운로드 → 1K 원본 크기")
    before = set(os.listdir(DL_DIR)) if os.path.isdir(DL_DIR) else set()
    btn = find_btn(d, "다운로드")
    if not btn:
        log("★다운로드 버튼 없음"); return False
    F.cmd("clickxy|%d|%d" % center(btn), 12)
    d = F.shot(8)
    item = find_btn(d, "원본 크기")
    if not item:
        log("★다운로드 메뉴('원본 크기') 없음"); return False
    F.cmd("clickxy|%d|%d" % center(item), 12)
    for _ in range(20):
        time.sleep(1.5)
        new = [f for f in os.listdir(DL_DIR) if f not in before]
        if new:
            src = max((os.path.join(DL_DIR, f) for f in new), key=os.path.getmtime)
            if os.path.getsize(src) > 50_000:
                from PIL import Image
                Image.open(src).convert("RGB").save(out)   # 받는 파일은 JPEG → 실제 PNG 로 저장
                log(f"✅ 저장: {out} ({os.path.getsize(out)//1024}KB)")
                return True
    log("★다운로드 실패(새 파일 없음)")
    return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("char", nargs="?")
    ap.add_argument("view", nargs="?")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.char:
        for c, g in GUIDES.items():
            have = [v for v, _ in POSES if os.path.exists(f"{OUT_DIR}/{c}_{v}.png")]
            print(f"{c:14s} 가이드={'有' if os.path.exists(g) else '★없음'}  생성됨={have or '-'}")
        sys.exit(0)
    sys.exit(0 if run(a.char, a.view) else 1)
