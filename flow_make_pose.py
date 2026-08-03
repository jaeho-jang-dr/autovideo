# -*- coding: utf-8 -*-
"""★W23 정지 포즈 1장 생성 — 나노 바나나(이미지 편집기) 경로 (2026-07-27).

동영상용 `flow_make_clip.py` 와 **타일 다루는 법이 정반대**다:
  - 동영상: 타일 본체 클릭 금지 → ⋮ → '프롬프트에 추가'
  - 정지 포즈: **타일 본체를 더블클릭** → 이미지 편집기(🍌 Nano Banana Pro) 진입

★★사장님 확정 절차 (2026-07-27, 이대로만 — 바꾸지 말 것):
 1. 리셋 — 크롬 전부 kill → flow_driver 새로 기동 → 새 프로젝트
 2. 가이드 이미지 업로드 → **30초 대기** → 타일 확인
 3. ★타일 중앙을 **hover 후 더블클릭** → URL 이 /edit/... 로 바뀌면 편집기 진입 성공
 4. 설정 칩(🍌 Nano Banana Pro) **확인만** — 비율은 3:4 든 9:16 이든 상관없다
    (어차피 투명컷 뜨고 키를 맞춘다)
 5. 프롬프트 입력 → 우측 화살표(만들기) **중심 좌표** 클릭
 6. **40초 대기 + 생성 모니터링** — 이력 타일 수가 늘었는지로 확인. 안 늘면 실패
 7. 우상단 **아래화살표(다운로드)** 클릭 → 열리는 메뉴에서 **맨 위 '1K 원본 크기'** 클릭
    → debug/downloads 에 떨어진 새 파일(JPEG)을 PNG 로 변환 저장

실측 함정:
  - 드라이버 명령 좌표는 `dblclick|x|y` 처럼 **파이프 구분**(쉼표는 파싱 에러)
  - 버튼은 좌상단이 아니라 **중심**을 눌러야 한다
  - 명령 인덱스는 debug/cmd 의 최대 번호에서 이어가야 한다(어긋나면 드라이버가 멈춰 대기)

사용:
  python flow_make_pose.py explain
  python flow_make_pose.py explain --no-reset
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
GUIDE = "W23/guides/upload/injun_w23_guide_front.png"
OUT_DIR = "W23/poses_still"
DL_DIR = "debug/downloads"

CHAR = ("Keep this exact character unchanged - same face, same hair, navy blue short-sleeve t-shirt, "
        "beige trousers, white sneakers, the same flat cartoon style with clean black outlines, the same "
        "body proportions and the same height as the reference picture. Only the pose changes. "
        "Exactly one head, two arms with two hands (five fingers each) and two legs in white sneakers - "
        "no extra or missing limbs. The whole body from head to shoes is fully inside the frame, standing "
        "upright and centred, plain pure white background, no shadow, no ground line, no extra objects, "
        "no other characters, no text.")

# (키, 포즈 설명) — W23_scenario.md H-2 의 16종
POSES = [
    ("explain", "he stands facing the viewer and explains something, his right hand raised open at chest "
                "height as if presenting a point, left arm relaxed at his side, friendly smile"),
    ("present_right", "he presents something on his right side: his right arm extended out to the side at "
                      "chest height, palm open and upward, body turned very slightly that way, warm smile"),
    ("present_left", "he presents something on his left side: his left arm extended out to the side at "
                     "chest height, palm open and upward, body turned very slightly that way, warm smile"),
    ("nod_agree", "he nods in agreement: chin slightly lowered, eyes softly closed in a pleased smile, "
                  "both hands relaxed at his sides"),
    ("count_three", "he holds up his right hand at shoulder height showing exactly three fingers "
                    "(index, middle and ring finger up, thumb and little finger folded), bright smile"),
    ("phone_calendar", "he holds a small smartphone in his left hand at chest height and points at its "
                       "screen with his right index finger, looking down at it with a focused smile"),
    ("raising_hand", "he raises his right arm straight up high above his head, hand open, looking forward "
                     "with an eager bright smile"),
    ("hard_smile", "he smiles awkwardly with a slightly embarrassed look, right hand scratching the back "
                   "of his head, left arm relaxed at his side"),
    ("thumbs_up", "he gives a clear thumbs-up with his right hand at chest height, big confident smile"),
    ("invite_hand", "he invites the viewer in: both arms open forward at waist height, palms up, "
                    "welcoming warm smile"),
    ("bow", "he bows politely from the waist about thirty degrees, both arms straight down along his "
            "sides, eyes lowered, polite smile"),
    # ★상호작용 5종 — 대상(난간·기둥·판·벤치)은 **그리지 않는다**. 손 높이만 가슴~허리로 통일.
    ("lean_rail", "he stands facing the viewer and rests his right forearm on an invisible waist-high "
                  "railing to his right - the forearm is horizontal at waist height, hand relaxed - "
                  "weight on one leg, relaxed smile. Do not draw the railing itself"),
    ("hand_on_post", "he stands facing the viewer with his right hand placed flat on an invisible vertical "
                     "post at chest height to his right, arm slightly bent, relaxed smile. "
                     "Do not draw the post itself"),
    ("tap_board", "he stands facing the viewer and taps an invisible upright board to his right with the "
                  "fingertips of his right hand at chest height, looking that way with a bright smile. "
                  "Do not draw the board itself"),
    ("point_board", "he stands facing the viewer and points at one spot on an invisible upright board to "
                    "his right with his right index finger at chest height, looking that way, explaining "
                    "smile. Do not draw the board itself"),
    ("lean_bench", "he stands facing the viewer and rests his right hand on the back of an invisible bench "
                   "at waist height to his right, body relaxed, easy smile. Do not draw the bench itself"),
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


def run(key, do_reset=True):
    motion = POSE_MAP.get(key)
    if not motion:
        raise SystemExit(f"모르는 포즈 키: {key} (가능: {', '.join(k for k, _ in POSES)})")
    os.makedirs(OUT_DIR, exist_ok=True)
    out = f"{OUT_DIR}/injun_w23_{key}.png"
    prompt = f"{CHAR} Pose: {motion}."

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
    ap.add_argument("key")
    a = ap.parse_args()
    sys.exit(0 if run(a.key) else 1)
