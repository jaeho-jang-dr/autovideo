# -*- coding: utf-8 -*-
"""인터랙트랑(InteractRang) — 배경과 캐릭터를 **실제로 맞물리게** 하는 엔진.

★사장님 지시(2026-08-11)
  "캐릭터가 따로 움직이면서 투명컷 했는데 배경의 어느 부분에 가서 걸터앉는다,
   앉는다, 기댄다, 손으로 잡는다, 만진다, 땅에 주저앉아 현미경으로 살핀다,
   손으로 땅을 휘저으며 찾는다 — 이런 동작들을 만들어서 상호작용을 하는 것."
  "배경에 사람이 가기도 하고, 배경을 움직여서 사람의 손이 올라가면서 잡기도 하고,
   둘 다 되는 엔진을 만들어 보자."

일반 영상은 배경·캐릭터가 한 프롬프트로 같이 생성되니 저절로 맞물린다.
한글강의는 **플랫 레이어드**(배경 따로, 투명컷 캐릭터 따로)라 그게 안 된다.
이 엔진이 그 간극을 메운다.

## 두 방향
A. **캐릭터 → 배경** (정적 접점)
   배경의 벤치 앉는 면·난간·계단·기둥에 **앵커**를 찍어 두고,
   캐릭터의 엉덩이/손/발이 그 앵커에 오도록 배치한다.
B. **배경 → 캐릭터** (동적 접점)
   배경 클립에서 움직이는 물체를 **프레임마다 추적**해 그 좌표를 얻고,
   캐릭터의 손이 그 좌표를 따라가게 한다.

## 자료 구조
앵커는 배경 1장당 JSON 한 개. 좌표는 **1280x720 기준**.

```json
{
  "bg": "gwanghwamun_bench",
  "size": [1280, 720],
  "anchors": {
    "bench_seat":  {"type": "sit",   "x": 880, "y": 470, "facing": "left"},
    "bench_back":  {"type": "lean",  "x": 905, "y": 400},
    "rail_grip":   {"type": "grab",  "x": 760, "y": 430},
    "ground_dig":  {"type": "ground","x": 700, "y": 640}
  }
}
```

`type` 이 캐릭터의 **어느 부위**를 그 점에 맞출지 정한다.

| type | 맞추는 부위 | 쓰는 포즈 |
|---|---|---|
| `sit`    | 엉덩이(pelvis) | 걸터앉기·앉기 |
| `lean`   | 등/어깨 | 기대기 |
| `grab`   | 손(hand) | 잡기 |
| `touch`  | 손끝 | 만지기 |
| `ground` | 손 + 무릎 | 주저앉아 살피기·휘젓기 |
| `stand`  | 발(feet) | 서기 — 바닥선 |
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
ANCHOR_DIR = os.path.join(ROOT, "assets", "anchors")

# 캐릭터에서 어느 부위를 앵커에 맞출지 — 투명컷 PNG 기준의 상대 위치(0~1)
# ★포즈마다 다르므로 포즈 등록 때 같이 저장한다. 아래는 기본값.
PART = {
    "sit":    ("pelvis", 0.50, 0.62),     # 엉덩이 ≈ 키의 62% 지점
    "lean":   ("back",   0.50, 0.45),
    "grab":   ("hand",   0.90, 0.40),     # 오른손을 앞으로 뻗은 포즈 기준
    "touch":  ("hand",   0.92, 0.42),
    "ground": ("hand",   0.80, 0.92),
    "stand":  ("feet",   0.50, 1.00),
}


# ── 앵커 ──────────────────────────────────────────────────────────────────
def anchor_path(bg_key):
    return os.path.join(ANCHOR_DIR, bg_key + ".json")


def load_anchors(bg_key):
    p = anchor_path(bg_key)
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))


def save_anchors(bg_key, size, anchors):
    os.makedirs(ANCHOR_DIR, exist_ok=True)
    d = {"bg": bg_key, "size": list(size), "anchors": anchors}
    json.dump(d, open(anchor_path(bg_key), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    return d


# ── A. 캐릭터 → 배경 (정적 접점) ──────────────────────────────────────────
def place_on_anchor(char_png, anchor, char_h, part=None):
    """캐릭터를 앵커에 맞춰 놓을 좌상단 좌표를 돌려준다.

    char_h — 화면에 놓을 캐릭터 키(px). 키 통일 규격을 그대로 쓴다.
    """
    im = Image.open(char_png).convert("RGBA")
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    im = im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    s = char_h / im.height
    w, h = max(1, round(im.width * s)), char_h
    im = im.resize((w, h), Image.LANCZOS)

    t = part or anchor.get("type", "stand")
    _, fx, fy = PART.get(t, PART["stand"])
    # 캐릭터 안에서 그 부위가 있는 픽셀 위치
    px, py = fx * w, fy * h
    left = int(round(anchor["x"] - px))
    top = int(round(anchor["y"] - py))
    return im, (left, top)


# ── B. 배경 → 캐릭터 (동적 접점) ──────────────────────────────────────────
def track_moving_object(frames, roi=None, thresh=18):
    """카메라 고정 배경 클립에서 **움직이는 물체**의 좌표를 프레임마다 찾는다.

    frames — PIL Image 목록(같은 크기). 카메라가 고정이라 프레임 차분이면 충분하다.
    roi    — (x0, y0, x1, y1) 로 찾을 범위를 좁힌다(왼편은 글자 자리라 보통 오른쪽만).
    반환   — [(i, x, y, area), …]  물체를 못 찾은 프레임은 건너뛴다.
    """
    from scipy import ndimage

    g = [np.asarray(f.convert("L"), np.float32) for f in frames]
    base = np.median(np.stack(g[:5]), axis=0)          # 처음 몇 장의 중앙값 = 배경
    out = []
    for i, cur in enumerate(g):
        d = np.abs(cur - base)
        if roi:
            m = np.zeros_like(d, bool)
            m[roi[1]:roi[3], roi[0]:roi[2]] = True
            d = d * m
        mask = d > thresh
        if mask.sum() < 40:
            continue
        lab, n = ndimage.label(mask)
        sizes = ndimage.sum(mask, lab, range(1, n + 1))
        k = int(np.argmax(sizes)) + 1
        ys, xs = np.nonzero(lab == k)
        out.append((i, float(xs.mean()), float(ys.mean()), float(sizes[k - 1])))
    return out


def hand_target_from_track(track, n_frames):
    """추적 결과를 프레임마다의 손 목표 좌표로 채운다(빈 프레임은 앞뒤로 메움)."""
    if not track:
        return None
    xs = {i: (x, y) for i, x, y, _ in track}
    out, last = [], track[0][1:3]
    for i in range(n_frames):
        if i in xs:
            last = xs[i]
        out.append(last)
    return out


# ── 원근 — 발 위치에 따라 키가 정해진다 ──────────────────────────────────
#
# ★지평선 법칙 (사장님 질문 2026-08-11 — "그것에 관한 법칙이 있나?")
#
#   **같은 키의 사람은 발이 어디에 있든 머리끝이 항상 지평선에 온다.**
#   카메라 눈높이가 곧 지평선이기 때문이다. 그래서 화면상의 키는
#
#       키(px) = k × (발의 y − 지평선 y)          k = 기준키 / (기준발y − 지평선y)
#
#   가 된다. **발이 지평선에 가까울수록(멀수록) 작아지고, 화면 아래로 내려올수록 커진다.**
#   선형이라 기준점 **하나**만 있으면 상수 k 가 정해진다.
#
#   ※눈높이보다 큰 사람은 머리가 지평선 위로, 작은 사람(아이)은 아래로 온다.
#     그 경우 k 를 사람마다 따로 잡으면 된다(졸라걸은 졸라맨의 0.917 배).
def perspective_height(foot_y, horizon_y, ref_foot_y, ref_h, ratio=1.0):
    """발 y 에 놓을 때의 화면상 키(px).

    horizon_y  — 지평선(카메라 눈높이) y
    ref_foot_y — 기준이 되는 발 y
    ref_h      — 그 자리에 섰을 때의 키(px)
    ratio      — 그 캐릭터의 키 비율(졸라맨 1.0 · 졸라걸 0.917 …)
    """
    denom = float(ref_foot_y - horizon_y)
    if denom <= 0:
        raise ValueError("기준 발이 지평선보다 위에 있다")
    k = ref_h / denom
    h = k * (foot_y - horizon_y) * ratio
    return max(1.0, h)


def foot_y_for_height(h, horizon_y, ref_foot_y, ref_h, ratio=1.0):
    """반대로 — 이 키로 보이게 하려면 발을 어디에 놓아야 하나."""
    k = ref_h / float(ref_foot_y - horizon_y)
    return horizon_y + h / (k * ratio)


# ── 가림(오클루전) — 캐릭터가 배경 물체 **뒤로** 가게 한다 ────────────────
def occlude(bg, comp, region):
    """캐릭터를 얹은 그림(comp) 위에 **배경의 그 부분을 다시 덮는다.**

    ★사장님 지시(2026-08-11): "벤치 뒤에 가서 서면 벤치에 가려지는 부분이 생겨야 한다.
      배경이 먼저고 캐릭터가 먼저지만 **일부를 지우면** 그것도 가능해진다."

    region — (x0, y0, x1, y1) 또는 알파 마스크 PNG 경로.
             그 영역만 배경 원본으로 되돌려 캐릭터를 가린다.
    """
    out = comp.copy()
    if isinstance(region, (tuple, list)):
        x0, y0, x1, y1 = [int(v) for v in region]
        out.paste(bg.crop((x0, y0, x1, y1)), (x0, y0))
        return out
    m = Image.open(region).convert("L")
    if m.size != bg.size:
        m = m.resize(bg.size, Image.LANCZOS)
    out.paste(bg, (0, 0), m)                     # 마스크가 흰 곳만 배경으로 덮는다
    return out


def make_occ_mask(bg_png, box, out_png, color_test=None):
    """배경에서 **가릴 물체의 마스크**를 만든다.

    box        — 물체가 있는 대략의 범위 (x0,y0,x1,y1)
    color_test — 그 범위 안에서 물체로 볼 색 판정 함수(RGB 배열 → bool 배열).
                 없으면 범위 전체를 마스크로 쓴다(사각형 가림).
    """
    im = Image.open(bg_png).convert("RGB")
    a = np.asarray(im).astype(int)
    m = np.zeros(a.shape[:2], np.uint8)
    x0, y0, x1, y1 = [int(v) for v in box]
    if color_test is None:
        m[y0:y1, x0:x1] = 255
    else:
        sub = a[y0:y1, x0:x1]
        m[y0:y1, x0:x1] = np.where(color_test(sub), 255, 0).astype(np.uint8)
    Image.fromarray(m).save(out_png)
    return out_png


def wood_mask(sub):
    """나무색(벤치) 판정 — R>G>B 이고 R 130~215."""
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    return (r > 130) & (r < 215) & (g > 90) & (g < 180) & (b < 150) & \
           (r > g + 15) & (g > b + 10)


# ── 확인용 — 앵커를 배경 위에 찍어 본다 ──────────────────────────────────
def draw_anchors(bg_png, bg_key, out_png):
    from PIL import ImageDraw, ImageFont
    d = load_anchors(bg_key)
    if not d:
        raise SystemExit("앵커 없음: " + anchor_path(bg_key))
    im = Image.open(bg_png).convert("RGB")
    dr = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 22)
    except Exception:
        f = None
    COL = {"sit": (220, 60, 60), "lean": (60, 140, 220), "grab": (40, 170, 90),
           "touch": (200, 140, 40), "ground": (150, 80, 200), "stand": (90, 90, 90)}
    for name, a in d["anchors"].items():
        c = COL.get(a.get("type", "stand"), (0, 0, 0))
        x, y = a["x"], a["y"]
        dr.ellipse([x - 11, y - 11, x + 11, y + 11], outline=c, width=4)
        dr.line([(x - 20, y), (x + 20, y)], fill=c, width=2)
        dr.line([(x, y - 20), (x, y + 20)], fill=c, width=2)
        dr.text((x + 16, y - 30), "%s (%s)" % (name, a.get("type")), font=f, fill=c)
    im.save(out_png)
    return out_png


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("show", help="앵커를 배경 위에 찍어 본다")
    p.add_argument("bg_png")
    p.add_argument("bg_key")
    p.add_argument("out_png")

    p = sub.add_parser("track", help="배경 클립에서 움직이는 물체를 추적한다")
    p.add_argument("frames_dir")
    p.add_argument("--roi", help="x0,y0,x1,y1")

    a = ap.parse_args()
    if a.cmd == "show":
        print(draw_anchors(a.bg_png, a.bg_key, a.out_png))
    elif a.cmd == "track":
        import glob
        fs = sorted(glob.glob(os.path.join(a.frames_dir, "*.png")))
        ims = [Image.open(f) for f in fs]
        roi = tuple(int(v) for v in a.roi.split(",")) if a.roi else None
        tr = track_moving_object(ims, roi)
        print("프레임 %d · 추적된 프레임 %d" % (len(ims), len(tr)))
        for i, x, y, ar in tr[::max(1, len(tr) // 12)]:
            print("  f%03d  (%4.0f, %4.0f)  면적 %.0f" % (i, x, y, ar))
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
