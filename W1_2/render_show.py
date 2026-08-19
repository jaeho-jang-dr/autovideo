# -*- coding: utf-8 -*-
"""W1-2 **모션 쇼케이스** 렌더 — 있는 자산을 전부 화면에 쓴다. 8분.

★사장님 지시(2026-08-12)
  "8분 꽉 채워서 캐릭터 모션, 배경과 협동, 다양한 연출, 놀랄 만한 포즈와 동작."
  "모든 동작 모든 포즈 모든 캐릭터 자산을 다 쓴다. 모든 배경(동영상·정지) 다 쓴다."
  "**자르지 말고 확대하지 마라. 원근법을 쓰라.**"
  "동시에 두 개·세 개 캐릭터가 화면에. 한 캐릭터가 중복해 둘이 나와도 좋다."
  "앞구르기·백플립은 정상 속도대로 하되 여러 번 반복해도 된다."

## 이 스크립트가 지키는 것
· **크롭·확대 없음** — 배경은 1280×720 원본, 캐릭터는 원본 컷을 **축소만** 한다
· **원근** — 뒤 층일수록 작고 발 y 가 위. 발은 항상 그 층의 지면선에 닿는다
· 1회 동작도 **원속(8fps) 그대로 되풀이**해 빈 시간을 없앤다
· 나레이션·자막 없음(이번 판은 모션만 본다)

    python W1_2/render_show.py            # 전부
    python W1_2/render_show.py 2          # 앞 2씬만(빠른 확인)
"""
import glob
import os
import random
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

OUT = "W1_2/_show"
FPS = 24
CUT_FPS = 8.0                      # 컷 원속 (64컷 ÷ 8초)
W, H = 1280, 720

# 원근 층 — (화면 키, 발 y).  뒤로 갈수록 작고 위에 선다
LAYER = {"front": (480, 686), "mid": (420, 648), "back": (250, 566), "far": (190, 536)}
ORDER = {"far": 1, "back": 2, "mid": 3, "front": 4}          # 뒤에서 앞으로 그린다

BG_DIR = "W1_2/bg"
CUT_DIRS = ["W1_2/motion6_cuts", "W1_2/motion6_stride"]
POSE_DIRS = ["W1_2/pose_cuts", "W1_2/_poses"]
CARD_DIR = "W1_2/cards"
M6_DIR = "assets/graphics/poses"


def load_cuts():
    """동작 컷 폴더 → {키: [경로…]}"""
    out = {}
    for base in CUT_DIRS:
        for d in sorted(glob.glob(os.path.join(base, "*"))):
            if not os.path.isdir(d):
                continue
            fs = sorted(glob.glob(os.path.join(d, "*.png")))
            if fs:
                out[os.path.basename(d)] = fs
    # m6 이동컷 라이브러리(낱장) — walk_side_r 등
    keys = set()
    for p in glob.glob(os.path.join(M6_DIR, "m6_*.png")):
        b = os.path.basename(p)[3:-4]
        if b[-3:-2] == "_" and b[-2:].isdigit():
            keys.add(b[:-3])
    for k in sorted(keys):
        fs = sorted(glob.glob(os.path.join(M6_DIR, "m6_%s_*.png" % k)))
        if fs:
            out["m6:" + k] = fs
    return out


def is_single_figure(p):
    """★진짜 **한 명짜리 투명컷**인지 가린다.

    자산 폴더에는 검증용 **시트**(격자 배경 위에 여러 명을 늘어놓고 '카드3'·'오른쪽 3'
    같은 라벨을 찍은 것)가 섞여 있다. 그걸 포즈로 긁어와 화면에 통째로 붙여 버렸다
    (사장님 지적 2026-08-12 — 라벨 글자와 격자무늬가 그대로 나왔다).

    거르는 법 — ①알파가 있어야 하고 ②가로가 세로보다 훨씬 길면 시트다
    ③불투명 화소가 너무 많으면(=배경이 안 뚫린 판) 시트다.
    """
    try:
        im = Image.open(p)
    except Exception:
        return False
    if im.mode not in ("RGBA", "LA"):
        return False                                   # 알파 없음 = 투명컷 아님
    w, h = im.size
    if w > h * 1.6:
        return False                                   # 가로로 긴 판 = 시트
    a = im.convert("RGBA").split()[-1]
    import numpy as _np
    op = (_np.asarray(a) > 8).mean()
    return 0.02 <= op <= 0.55                          # 사람 하나면 이 언저리다


def load_poses():
    out, drop = {}, 0
    for d in POSE_DIRS:
        for p in sorted(glob.glob(os.path.join(d, "*.png"))):
            k = os.path.splitext(os.path.basename(p))[0]
            if k in out:
                continue
            if not is_single_figure(p):
                drop += 1
                continue
            out[k] = p
    if drop:
        print("  (시트·검증 이미지 %d장 걸러냄)" % drop)
    return out


_IM = {}
def img(p):
    if p not in _IM:
        _IM[p] = Image.open(p).convert("RGBA")
    return _IM[p]


def bg_frames(key, n):
    """배경 프레임 n장. 동영상은 끝나면 마지막 프레임 유지(loop 금지). 크롭 없음."""
    mp4 = os.path.join(BG_DIR, key + ".mp4")
    png = os.path.join(BG_DIR, key + ".png")
    if os.path.exists(mp4):
        d = os.path.join(OUT, "_bg", key)
        got = glob.glob(os.path.join(d, "*.png"))
        # ★캐시가 mp4 보다 낡았으면 **다시 뽑는다**.
        #   배경을 새로 만들어 넣어도 캐시가 남아 있으면 옛 배경이 그대로 렌더됐다 —
        #   광화문 노을로 바꾼 dusk_lanterns 자리에 이틀 전 유럽 궁전이 나왔다
        #   (사장님 지적 2026-08-15). 파일 시각을 비교해 근본 차단한다.
        stale = got and os.path.getmtime(mp4) > min(os.path.getmtime(p) for p in got)
        if not got or stale:
            if stale:
                print("     · 배경 캐시가 낡았다 → 다시 뽑는다:", key)
            os.makedirs(d, exist_ok=True)
            for p in got:
                os.remove(p)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp4, "-vsync", "0",
                            os.path.join(d, "f%03d.png")], check=True)
        fs = sorted(glob.glob(os.path.join(d, "*.png")))
        return [fs[min(i, len(fs) - 1)] for i in range(n)]
    return [png] * n


def place_xy(canvas, im, x, foot, h_target):
    """원본 컷을 **축소만** 해서 얹는다. 발이 foot 에 닿는다. 크롭·확대 없음."""
    s = min(1.0, h_target / float(im.height))     # ★확대 금지
    w = max(1, int(round(im.width * s)))
    h = max(1, int(round(im.height * s)))
    canvas.alpha_composite(im.resize((w, h), Image.LANCZOS), (int(x - w / 2), int(foot - h)))


def place(canvas, im, layer, x, t_frac_h=None):
    h_target, foot = LAYER[layer]
    place_xy(canvas, im, x, foot, t_frac_h or h_target)


# ★원근 이동 경로 — **좌표와 크기를 함께** 바꾼다(사장님 지시 2026-08-12).
#   "좌표를 바꾸면서 크기를 바꾸면서 정면 달리기를 하는 거지."
#   "오른편으로 달리면서 사이즈를 줄이고 좌표를 바꾸면 사선으로 멀어지는 게 된다."
#   (이름, 컷키, x시작→끝, 키시작→끝, 발y시작→끝)
#
# ★원근 폭 — **250 ~ 600, 스틱맨 기준** (사장님 확정 2026-08-12)
#   "사선으로 달려 오기·달려 나가기는 더 확실하게, 더 멀리, 더 작게 시작하고 끝낸다.
#    크게는 스틱맨 기준으로 600까지." → "**250에서 600까지.** 스틱맨 기준이다."
#   250 은 글자 하나 크기(그 밑으로는 점처럼 보여 못 쓴다), 600 은 코앞.
#   발 y 도 지평선(520) 부근에서 화면 바닥(700)까지 함께 움직인다.
#   ★최종 확정 — "**아주 작게도 해 보자. 90에서 600까지로 간다.**"
#     먼 쪽 90px(점처럼) → 가까운 쪽 600px(코앞). 6.7배 차이.
NEAR_H, FAR_H = 600, 90
NEAR_Y, FAR_Y = 700, 490
DEEP_H, DEEP_Y = FAR_H, FAR_Y

PATHS = [
    # 앞으로 달려 들어오기 — 아주 작은 점에서 → 600px 로 코앞까지
    ("run_in",      "run_front",      (640, 640),   (FAR_H, NEAR_H), (FAR_Y, NEAR_Y)),
    # 뒤로 달려 나가기 — 코앞에서 → 아주 작은 점으로
    ("run_out",     "run_back",       (640, 640),   (NEAR_H, FAR_H), (NEAR_Y, FAR_Y)),
    # 사선으로 달려 멀어지기 — 왼쪽 아래 코앞 → 오른쪽 위 저 멀리
    ("diag_away_r", "m6:run_side_r",  (180, 1240),  (NEAR_H, FAR_H), (NEAR_Y, FAR_Y)),
    # 사선으로 달려 다가오기 — 오른쪽 위 저 멀리 → 왼쪽 아래 코앞
    ("diag_near_l", "m6:run_side_l",  (1240, 180),  (FAR_H, NEAR_H), (FAR_Y, NEAR_Y)),
    # 사선으로 걸어 멀어지기 — 천천히
    ("diag_walk_r", "m6:walk_side_r", (240, 1180),  (520, 110),      (690, 508)),
    # ★90 판 — 아주 멀리까지 (테스트: 250 판과 견주어 본다)
    ("deep_in",     "run_front",      (640, 640),   (DEEP_H, NEAR_H), (DEEP_Y, NEAR_Y)),
    ("deep_away_r", "m6:run_side_r",  (200, 1260),  (NEAR_H, DEEP_H), (NEAR_Y, DEEP_Y)),
]


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    cuts, poses = load_cuts(), load_poses()
    cards = sorted(glob.glob(os.path.join(CARD_DIR, "*.png")))
    bgs = sorted(os.path.splitext(os.path.basename(p))[0]
                 for p in glob.glob(os.path.join(BG_DIR, "*.mp4")) +
                 glob.glob(os.path.join(BG_DIR, "*.png")))
    bgs = [b for b in bgs if not b.startswith("_")]

    print("자산 — 동작 %d종 · 포즈 %d장 · 카드 %d장 · 배경 %d개"
          % (len(cuts), len(poses), len(cards), len(bgs)))

    # ── 동작·포즈를 배경에 고르게 나눠 담는다(전부 한 번은 쓰인다) ──
    rnd = random.Random(12)
    mkeys = sorted(cuts)
    pkeys = sorted(poses)
    rnd.shuffle(mkeys)
    rnd.shuffle(pkeys)
    nbg = len(bgs)
    per_m = -(-len(mkeys) // nbg)
    per_p = -(-len(pkeys) // nbg)
    LAY_CYCLE = ["back", "mid", "front", "far"]

    scenes = []
    for i, bg in enumerate(bgs):
        ms = mkeys[i * per_m:(i + 1) * per_m]
        ps = pkeys[i * per_p:(i + 1) * per_p]
        acts = []
        # ★배경마다 원근 이동 경로를 하나씩 넣는다 — 다가오기·멀어지기·사선
        pth = PATHS[i % len(PATHS)]
        if pth[1] in cuts:
            acts.append(("path", pth[1], "far", pth, None))
        for j, k in enumerate(ms):
            lay = LAY_CYCLE[j % len(LAY_CYCLE)]
            x0 = [220, 1060, 640, 380][j % 4]
            x1 = [1060, 220, 640, 900][j % 4] if j % 2 == 0 else x0
            acts.append(("cut", k, lay, x0, x1))
        for j, k in enumerate(ps):
            lay = ["front", "back", "mid", "far"][j % 4]
            acts.append(("pose", k, lay, [160, 1120, 300, 980][j % 4], None))
        scenes.append((bg, acts, cards[i % len(cards)] if cards else None))

    if limit:
        scenes = scenes[:limit]

    SEC = 480.0 / len(scenes) if not limit else 30.0
    frames_dir = os.path.join(OUT, "_frames")
    os.makedirs(frames_dir, exist_ok=True)
    for f in glob.glob(os.path.join(frames_dir, "*.png")):
        os.remove(f)

    k = 0
    for bg, acts, card in scenes:
        n = int(SEC * FPS)
        bfs = bg_frames(bg, n)
        ncut = sum(1 for a in acts if a[0] == "cut")
        print("  %-16s %5.1f초 · 동작 %d · 포즈 %d"
              % (bg, SEC, ncut, len(acts) - ncut))
        for i in range(n):
            t = i / float(FPS)
            cv = img(bfs[i]).copy()
            if cv.size != (W, H):
                cv = cv.resize((W, H), Image.LANCZOS)      # 비율 같음 — 크롭 아님
            # ★원근 z-정렬 — **발이 아래에 있을수록(가까울수록) 나중에** 그려 앞을 덮는다.
            #   (사장님 지시 2026-08-12: "스치며 지나가 겹치는 건 괜찮으나 원근을 지켜라.
            #    앞엣것은 보이고 뒤엣것이 덮여야 한다.")
            def _foot(a):
                if a[0] == "path":
                    _, _, _, (af, bf) = a[3][2], a[3][3], a[3][3], a[3][4]
                    LOOP = 6.0
                    u = (t % LOOP) / LOOP
                    return af + (bf - af) * (u * u * (3 - 2 * u))
                return LAYER[a[2]][1]

            for a in sorted(acts, key=_foot):
                kind, key, lay, x0, x1 = a
                if kind == "path":
                    # ★좌표·크기·발 y 를 **한꺼번에** 보간 → 다가오기·멀어지기·사선
                    _, ck, (ax, bx), (ah, bh), (af, bf) = x0
                    fs = cuts[ck]
                    LOOP = 6.0                              # 6초에 한 번 지나간다
                    u = (t % LOOP) / LOOP
                    e = u * u * (3 - 2 * u)                 # smoothstep
                    place_xy(cv, img(fs[int(t * CUT_FPS) % len(fs)]),
                             ax + (bx - ax) * e,
                             af + (bf - af) * e,
                             ah + (bh - ah) * e)
                    continue
                if kind == "cut":
                    fs = cuts[key]
                    idx = int(t * CUT_FPS) % len(fs)        # ★원속으로 되풀이
                    p = fs[idx]
                    x = x0 + (x1 - x0) * ((t * CUT_FPS / len(fs)) % 1.0) if x1 != x0 else x0
                else:
                    p = poses[key]
                    x = x0
                place(cv, img(p), lay, x)
            if card:
                c = img(card)
                s = 150.0 / c.height
                cv.alpha_composite(c.resize((int(c.width * s), 150), Image.LANCZOS),
                                   (W - 190, 30))
            cv.convert("RGB").save(os.path.join(frames_dir, "f%05d.png" % k))
            k += 1

    out = os.path.join(OUT, "w1d2_show.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(frames_dir, "f%05d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", out], check=True)
    print("\n✅ %s  %d프레임 · %.1f초" % (out, k, k / float(FPS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
