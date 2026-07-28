# -*- coding: utf-8 -*-
"""★W23 배경 정지 이미지 1장 생성 — 나노 바나나, 프롬프트만 (2026-07-27).

`flow_make_bgmv.py`(배경 동영상)와 같은 자리에서 만들지만 **모델이 나노 바나나**이고
다운로드가 **메뉴에서 1K 선택**이라는 점이 다르다. 업로드는 없다.

★★사장님 확정 절차 (이 순서대로만):
 1. 리셋 — 크롬 전부 kill → flow_driver 새로 기동 → 새 프로젝트(새 세션)
 2. 하단 설정 칩 → **나노 바나나** + **16:9**
 3. 프롬프트 창 클릭 → 붙여넣기 → 우측 화살표(만들기) **중심 좌표** 클릭
 4. **45초 대기** → 타일 생성 확인
 5. 타일 클릭 → 우상단 **다운로드** → 메뉴에서 **1K** 선택 → 파일 저장

사용:
  python flow_make_bg.py rose_arch
  python flow_make_bg.py --list
"""
import argparse
import glob
import os
import re
import sys
import time

import flow_make_clip as F

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
OUT_DIR = "assets/graphics/bg"
DL_DIR = "debug/downloads"
# 하단 설정 칩 — 동영상 모드는 '동영상 · 8s…', 이미지 모드는 'Nano Banana 2 … 1x' 로 글자가 바뀐다
CHIP_PAT = r"동영상 ·|이미지 ·|Video ·|Image ·|Nano Banana"

TAIL = ("Pastel storybook illustration, bold clean outlines, flat cel shading, warm natural light. "
        "Absolutely no text, no letters, no numbers, no signage lettering, no logos, no watermark. "
        "No human figures, no cartoon characters. Keep the left side of the frame visually calm and "
        "simple. The ground runs continuously from edge to edge across the bottom so a figure could "
        "walk along it. 16:9, 1280x720.")

# W23_scenario.md G-2 — agy 신규 7장. 좌 앵커 x≈380 / 우 앵커 x≈850, 손 높이 y≈300~360
BGS = [
    ("rose_arch",
     "A rose garden with brick arch pillars over a gravel walk. A brick arch pillar stands at the left "
     "about a third in, its side face at chest height; a low stone planter stand sits at the right at "
     "the same height."),
    ("park_cafe",
     "An outdoor park cafe terrace. On the left wall hangs a blank monthly grid board (empty squares "
     "only, no numbers, no writing) at chest height; on the right a parasol pole rises beside a wooden "
     "table at the same height. Wicker chairs, potted flowers, leafy trees behind."),
    ("panda_deck",
     "A panda viewing deck. A wooden deck railing runs along the left at waist-to-chest height; a thick "
     "bamboo post stands at the right at the same height. Bamboo groves and a panda resting in the "
     "middle distance."),
    ("picnic_lawn",
     "A picnic lawn. A big shade tree trunk rises at the left, its bark face at chest height; a wooden "
     "picnic table with a bench back sits at the right at the same height. Checkered blankets on the "
     "grass."),
    ("ferris_lawn",
     "A flower lawn beneath a giant ferris wheel. A low stone lawn kerb runs across the left at hand "
     "height; a ticket-booth railing stands at the right at chest height. The wheel rises behind, "
     "centre and right."),
    ("fountain_square",
     "A fountain plaza. The fountain's stone rim runs across the left at hand height; a park bench with "
     "a backrest sits at the right at the same height. Flower beds around, water jets still."),
    ("notice_plaza",
     "A plaza with a large blank notice board (empty panel, no text, no posters) mounted at the left at "
     "chest height, and a stone column at the right at the same height. Trees and low hedges behind."),
]
BG_MAP = dict(BGS)


def log(m):
    print(m, flush=True)


def sync_index():
    """드라이버 명령 인덱스를 debug/cmd 의 최대 번호에 맞춘다(어긋나면 드라이버가 멈춘다)."""
    files = glob.glob("debug/cmd/*.txt")
    F._n[0] = max((int(re.findall(r"(\d+)\.txt$", p.replace("\\", "/"))[0]) for p in files), default=0)


def find_btn(dump, pattern):
    """텍스트/aria 를 정규식으로 찾는다 — UI 언어가 한/영으로 바뀌므로 둘 다 받는다."""
    for e in dump.get("els", []):
        if re.search(pattern, (e.get("text") or "") + " " + (e.get("aria") or "")):
            return e
    return None


def find_exact(dump, *texts):
    """텍스트가 정확히 일치하는 요소(탭·비율 칩처럼 짧은 라벨용)."""
    for e in dump.get("els", []):
        if (e.get("text") or "").strip() in texts:
            return e
    return None


def center(e):
    return e["x"] + e["w"] // 2, e["y"] + e["h"] // 2


def run(key):
    motion = BG_MAP.get(key)
    if not motion:
        raise SystemExit(f"모르는 배경 키: {key} (가능: {', '.join(k for k, _ in BGS)})")
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.abspath(f"{OUT_DIR}/bg_w23_{key}.png")
    prompt = f"{motion} {TAIL}"

    if not F.reset_and_start():
        return False
    sync_index()

    log("[2] 설정 — 이미지 / 16:9 / 1x / Nano Banana 2")
    # ★리셋 직후엔 하단 프롬프트 바가 아직 안 그려져 있다 → 칩이 보일 때까지 몇 번 다시 찍는다
    chip, d = None, {}
    for _ in range(5):
        d = F.shot(10)
        chip = find_btn(d, CHIP_PAT)
        if chip:
            break
        F.cmd("wait|5", 15)
    if not chip:
        log("★설정 칩 없음"); return False
    log(f"     현재 설정: {((chip.get('text') or '')).strip()[:40]!r}")
    F.cmd("clickxy|%d|%d" % center(chip), 10)
    d = F.shot(8)
    # ★모델 드롭다운(Nano Banana 2)은 **누르지 않는다** — 열린 팝오버가 프롬프트 클릭을 가로채
    #   fillprompt 가 타임아웃되고 빈 프롬프트로 실행돼 버린다(2026-07-27 실측 사고). 기본값 그대로 쓴다.
    # ★항목 텍스트는 아이콘 합자가 붙어 나온다('crop_16_916:9') → 정확일치 말고 포함으로 찾는다
    for want in ((r"이미지|Image",), (r"16:9",), (r"^1x$|1x$",)):
        item = find_btn(d, want[0])
        if item:
            F.cmd("clickxy|%d|%d" % center(item), 8)
            d = F.shot(8)
            log(f"     {want[0]} 선택")
        else:
            log(f"     ({want[0]} 항목 못 찾음 — 현재 설정 유지)")
    model = find_btn(d, r"Nano Banana")
    log(f"     모델: {((model.get('text') or '') if model else '?').strip()[:30]!r}")
    F.cmd("key|Escape", 6)
    d = F.shot(8)
    chip = find_btn(d, CHIP_PAT)
    log(f"     확정 설정: {((chip.get('text') or '') if chip else '?').strip()[:40]!r}")

    log("[3] 프롬프트 입력 + 실행")
    box = next((e for e in d.get("els", []) if e.get("role") == "textbox"), None)
    if not box:
        log("★프롬프트 입력창 없음"); return False
    F.cmd("clickxy|%d|%d" % center(box), 8)
    F.cmd(f"fillprompt|{prompt}", 40)
    d = F.shot(8)
    tb = next((e for e in d.get("els", []) if e.get("role") == "textbox"), None)
    if not tb or not (tb.get("text") or "").startswith(motion[:20]):
        log("★프롬프트가 안 들어갔다(빈 채로 실행 금지)"); return False
    arrow = find_btn(d, r"arrow_forward")
    if not arrow:
        log("★실행(만들기) 버튼 없음"); return False
    n_before = len([e for e in d.get("els", []) if e.get("tag") == "IMG" and e.get("w", 0) > 100])
    F.cmd("clickxy|%d|%d" % center(arrow), 10)

    log("[4] 45초 대기 + 생성 확인")
    F.cmd("wait|45", 70)
    tile = None
    for _ in range(5):
        d = F.shot(10)
        tiles = [e for e in d.get("els", []) if e.get("tag") in ("IMG", "VIDEO") and e.get("w", 0) > 100]
        if len(tiles) > n_before:
            tile = sorted(tiles, key=lambda e: (e["y"], e["x"]))[0]
            log(f"     생성 확인(타일 {n_before}→{len(tiles)})"); break
        F.cmd("wait|10", 25)
    if not tile:
        log("★타일 안 뜸 — 생성 실패"); return False

    log("[5] 타일 클릭 → 우상단 다운로드 → 1K")
    F.cmd("clickxy|%d|%d" % center(tile), 15)
    d = F.shot(10)
    btn = find_btn(d, r"다운로드|downloadDownload")
    if not btn:
        log("★다운로드 버튼 없음"); return False
    before = set(os.listdir(DL_DIR)) if os.path.isdir(DL_DIR) else set()
    F.cmd("clickxy|%d|%d" % center(btn), 12)
    # ★메뉴가 그려지는 데 시간이 걸린다 — 한 번만 찍고 없다고 끝내면 여기서 실패한다(실측)
    item = None
    for _ in range(4):
        d = F.shot(10)
        item = find_btn(d, r"1K")
        if item:
            break
        F.cmd("wait|3", 10)
    if item:
        log(f"     메뉴: {(item.get('text') or '').strip()[:20]!r}")
        mx, my = center(item)
    else:
        # ★스샷 실측 폴백 — 메뉴는 다운로드 버튼 기준 **왼쪽 39 · 아래 53** 에 열린다(1K/2K/4K 순, 60px 간격)
        bx, by = center(btn)
        mx, my = bx - 39, by + 53
        log(f"     메뉴 DOM 미검출 → 스샷 상대좌표로 클릭 ({mx},{my})")
    F.cmd("clickxy|%d|%d" % (mx, my), 12)
    for _ in range(20):
        time.sleep(1.5)
        new = [f for f in os.listdir(DL_DIR) if f not in before]
        if new:
            src = max((os.path.join(DL_DIR, f) for f in new), key=os.path.getmtime)
            if os.path.getsize(src) > 50_000:
                from PIL import Image
                Image.open(src).convert("RGB").save(out)   # 받는 파일은 JPEG → PNG 로 저장
                log(f"✅ 저장: {out} ({os.path.getsize(out)//1024}KB)")
                return True
    log("★다운로드 실패(새 파일 없음)")
    return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("key", nargs="?")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.key:
        for i, (k, m) in enumerate(BGS):
            mark = "有" if os.path.exists(f"{OUT_DIR}/bg_w23_{k}.png") else " "
            print(f"{i+1} [{mark}] {k:16s} {m[:70]}…")
        sys.exit(0)
    sys.exit(0 if run(a.key) else 1)
