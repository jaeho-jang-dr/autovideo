# -*- coding: utf-8 -*-
"""2.5D 캐릭터 엔진 — 화면 안을 **자유로이** 걸어 다니게 한다.

★사장님 지시(2026-08-13)
  "화면 안에서 뱅글뱅글 돌면서 쪼르르 걸어 다니거나 이리저리 가거나 할 수 있는 엔진."
  "갈 수 있는 곳, 비어 있는 곳으로만 움직인다. 막혀 있으면 앉거나 서 있는다."
  "대각선으로 달리면서 왼 앞에서 오른 저 끝 뒤로 가서 사라지는 것 — 그러나 땅에 발은
   항상 디뎌야 하고 원근법에 맞아야 한다."
  "캐릭터가 어느 곳에 딱 서면 **벌써 계산된 비율의 키로** 서야 하는 것이다."

## 이 엔진이 베낀 것 — 30년 된 어드벤처 게임의 방식
깃허브·업계를 뒤져 보니 **가져다 쓸 완제품은 없었다**(파이썬 것은 `pyvida` 하나뿐인데
2021년에 멈췄고 walk-behind 는 소스에 없다). 대신 **데이터 구조와 알고리즘**을 가져왔다.

| 우리가 부르던 말 | 업계 용어 | 어디서 |
|---|---|---|
| 갈 수 있는 땅 | **walkable area** | AGS 8비트 마스크 |
| 자리마다 정해진 키 | **scaling zone** | AGS 연속 스케일 · SCUMM 스케일 슬롯 |
| 난간 떼었다 붙이기 | **walk-behind** | AGS 마스크 + 기준선 |
| 앞뒤 순서 | **baseline** (발 y 로 정렬) | 모든 엔진 공통 |
| 계단·벤치에 발 얹기 | **foot anchor** | AGS `Character.z` |

핵심 식은 우리가 이미 쓰던 것과 같다 — 땅 위 물체의 화면 키는 `(발y − 지평선)` 에
정비례한다. AGS·SCUMM·Sierra 가 전부 이 한 줄을 쓴다.

## 새로 붙인 것 둘

**① 길찾기** — `scikit-image` 의 `MCP_Geometric`(이미 깔려 있다. 새 의존성 없음).
비용 격자에 `1/크기` 를 넣는다. 멀수록 한 화소를 지나는 데 **오래 걸리므로**, 저절로
"멀리 갈수록 천천히 움직이는" 그림이 된다(AGS 가 이동 속도를 크기에 묶는 것과 같다).
못 가는 곳은 `inf` 로 막는다.

**② 가림(walk-behind)** — 배경마다 마스크 한 장과 `{번호: 기준선 y}`.
캐릭터의 발이 기준선보다 **위(멀리)** 면 그 조각을 캐릭터 위에 다시 얹는다.
난간 너머에서 앞구르기를 하면 난간이 저절로 캐릭터를 가린다.

    python W1_2/stage2d.py steps_seat            # 그 배경의 무대를 재 본다
    python W1_2/stage2d.py steps_seat --path 200,700 1100,560
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

ANCHOR_DIR = "assets/anchors"
BG_DIR = "W1_2/bg"
W, H = 1280, 720

# ★캐릭터 실물 키 비율 — 스틱맨 700 을 1.0 으로 (DB char_heights)
CHAR_RATIO = {"stickman": 1.0, "zman": 711 / 700.0, "zgirl": 651 / 700.0}
CYCLE_M = {"walk": 1.50, "run": 3.20}      # 한 바퀴가 나아가는 실제 거리(m)
SPEED = {"walk": 1.25, "run": 3.60}        # m/s
REAL_M = 1.75                              # 스틱맨 실물 키


class Stage(object):
    """배경 하나의 무대 — 땅·원근·가림을 다 안다."""

    def __init__(self, bg):
        self.bg = bg
        p = os.path.join(ANCHOR_DIR, bg + ".json")
        self.doc = {}
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                self.doc = json.load(f)

        st = self.doc.get("stage") or {}
        g = self.doc.get("ground") or {}
        self.horizon = float(st.get("horizon") or g.get("horizon") or 452.9)
        self.front_h = float(st.get("front_h") or 400.0)
        # 키 = k × (발y − 지평선). 화면 바닥(720)에서 front_h 가 되도록 푼다.
        self.k = float(st.get("k") or self.front_h / max(1.0, H - self.horizon))

        # 세로줄마다 발을 디딜 수 있는 y 범위
        self.step = int(g.get("step") or 16)
        self.top = list(g.get("top") or [])
        self.bot = list(g.get("bot") or [])
        self.anchors = self.doc.get("anchors") or {}
        # ★구역별 키 — 바닥 평면이 아닌 땅(계단·단상)은 공식이 안 듣는다.
        #   [{"y0":.., "y1":.., "h0":.., "h1":..}] — 그 y 범위에서는 키를 이렇게 준다.
        self.zones = list(self.doc.get("zones") or [])
        self._mask = None
        self._cost = None

    # ── 원근 ─────────────────────────────────────────────────────
    def h_at(self, foot_y, who="stickman"):
        """★자리가 정해지면 키가 정해진다.

        ★구역(zone)이 있으면 그쪽이 먼저다 — 계단처럼 **높아진 땅**은 바닥 평면
          공식이 안 듣는다(오를수록 멀어지지만 올라간 만큼 화면에서 도로 내려온다).
          AGS 가 walkable area 마다 zoom 을 따로 두는 것과 같은 이유다.
          구역을 안 두면 계단 꼭대기가 '지평선 위'가 되어 키 0 · 거리 무한이 된다.
        """
        r = CHAR_RATIO.get(who, 1.0)
        for z in self.zones:
            if z["y0"] <= foot_y <= z["y1"]:
                u = (foot_y - z["y0"]) / max(1.0, float(z["y1"] - z["y0"]))
                return (z["h0"] + (z["h1"] - z["h0"]) * u) * r
        return max(0.0, self.k * (foot_y - self.horizon)) * r

    def foot_at(self, h, who="stickman"):
        return self.horizon + h / max(1e-6, self.k * CHAR_RATIO.get(who, 1.0))

    # ── ★자세 비율 — 캐릭터랑이 늘 지켜야 하는 것 ─────────────────
    #   사장님 지시(2026-08-13): "캐릭터랑이 항상 신경 써야 하는 게 그거야 —
    #   **자세에 따른 키 높이와 전체 비율이 어긋나지 않게.**"
    #
    #   자세가 바뀌어도 **축척은 그대로**다. 쭈그리면 몸이 작아지는 게 아니라
    #   그림의 높이가 낮아질 뿐이다.
    #
    #   ★★그런데 잉크 높이만으로 맞추면 **틀린다.** 자산마다 그려진 크기가 조금씩
    #     다르기 때문이다. 실측(2026-08-13) —
    #         엉덩방아 머리 203 · 놀람 머리 204 · 쭈그림 머리 **171**
    #     쭈그림을 잉크 높이(430/740)로만 줄였더니 같은 자리인데 혼자 작아 보였다.
    #     **머리 지름이 축척의 기준**이다 — 자세가 어떻든 머리 크기는 안 변한다.
    #     그래서 ①머리를 기준에 맞추고 ②그 자세의 잉크 높이만큼 그린다.
    STAND_INK = {"stickman": 740.0, "zman": 775.0, "zgirl": 745.0}
    HEAD_REF = {"stickman": 203.0, "zman": 210.0, "zgirl": 196.0}

    def draw_h(self, stand_h, asset_ink_h, asset_head_d=None, who="stickman"):
        """그릴 높이 — **머리를 기준에 맞춘 뒤** 그 자세의 잉크 높이만큼.

        asset_head_d 를 주면 머리로 맞춘다(정확). 안 주면 잉크 높이로만 맞춘다.
        """
        h = stand_h * float(asset_ink_h) / self.STAND_INK.get(who, 740.0)
        if asset_head_d:
            h *= self.HEAD_REF.get(who, 203.0) / float(asset_head_d)
        return h

    @staticmethod
    def head_d(path):
        """그림 한 장의 **머리 지름** — 맨 위 잉크 덩어리의 최대 가로폭."""
        a = np.asarray(Image.open(path).convert("RGBA").split()[-1]) > 8
        if not a.any():
            return 0
        rows = np.nonzero(a.any(1))[0]
        h = rows[-1] - rows[0] + 1
        best = 0
        for y in range(rows[0], min(rows[0] + int(h * 0.35), a.shape[0])):
            xs = np.nonzero(a[y])[0]
            if len(xs):
                best = max(best, int(xs[-1] - xs[0] + 1))
        return best

    def depth_m(self, h):
        """그 크기로 보이는 사람까지의 거리(m)."""
        return 1372.0 * REAL_M / max(1e-6, h)

    # ★사라지는 크기의 바닥 — 하한은 1 이지만(사장님 확정), **시간을 잴 때는** 그보다
    #   위에서 끊어야 한다. 소실점 코앞은 거리가 무한대로 뻗어 44초짜리 길이 나온다.
    #   사람 눈에 캐릭터가 사라지는 건 20px 언저리다. 거기까지만 시간을 잰다.
    VANISH_H = 20.0

    def dist_m(self, a, b):
        """두 화면 자리 사이의 실제 거리(m). a·b = (x, 발y)."""
        ha = max(self.VANISH_H, self.h_at(a[1]))
        hb = max(self.VANISH_H, self.h_at(b[1]))
        za, zb = self.depth_m(ha), self.depth_m(hb)
        xa = (a[0] - W / 2.0) * za / 1372.0
        xb = (b[0] - W / 2.0) * zb / 1372.0
        return math.hypot(xb - xa, zb - za)

    # ── 갈 수 있는 땅 ─────────────────────────────────────────────
    def walk_mask(self):
        """(H, W) bool — 발을 디딜 수 있는 곳."""
        if self._mask is not None:
            return self._mask
        m = np.zeros((H, W), bool)
        if self.top:
            for i, (t, b) in enumerate(zip(self.top, self.bot)):
                x0, x1 = i * self.step, min(W, (i + 1) * self.step)
                m[int(t):int(b), x0:x1] = True
        else:                                       # 실측이 없으면 지평선 아래 전부
            m[int(self.horizon) + 2:, :] = True
        self._mask = m
        return m

    def walkable(self, x, y):
        x, y = int(round(x)), int(round(y))
        if not (0 <= x < W and 0 <= y < H):
            return False
        return bool(self.walk_mask()[y, x])

    def snap(self, x, y):
        """갈 수 없는 자리면 **가장 가까운 갈 수 있는 자리**로 끌어당긴다."""
        if self.walkable(x, y):
            return int(round(x)), int(round(y))
        m = self.walk_mask()
        col = m[:, max(0, min(W - 1, int(round(x))))]
        ys = np.nonzero(col)[0]
        if len(ys):
            return int(round(x)), int(ys[np.argmin(np.abs(ys - y))])
        ys, xs = np.nonzero(m)
        i = np.argmin((xs - x) ** 2 + (ys - y) ** 2)
        return int(xs[i]), int(ys[i])

    # ── 길찾기 ───────────────────────────────────────────────────
    def cost_grid(self, agent_w=0.0):
        """비용 격자 — **멀수록 비싸다**(1/크기). 못 가는 곳은 inf.

        ★AGS 가 이동 속도를 크기에 묶는 것과 같은 효과다. 비용을 이렇게 주면
          "멀리 갈수록 화면에서 천천히 움직인다" 가 저절로 나온다.
        """
        if self._cost is not None:
            return self._cost
        m = self.walk_mask()
        if agent_w > 0:
            from scipy import ndimage
            m = ndimage.binary_erosion(m, np.ones((3, int(agent_w) | 1)))
        yy = np.arange(H, dtype=np.float64)[:, None]
        h = np.maximum(1.0, self.k * (yy - self.horizon))       # 그 줄에서의 키
        c = (self.front_h / h) * np.ones((1, W))                # 멀수록 큰 값
        c[~m] = np.inf
        self._cost = c
        return c

    def path(self, a, b, agent_w=0.0):
        """a → b 로 **갈 수 있는 땅만 밟아** 가는 길. [(x, y), …]"""
        from skimage.graph import MCP_Geometric
        a = self.snap(*a)
        b = self.snap(*b)
        mcp = MCP_Geometric(self.cost_grid(agent_w), fully_connected=True)
        mcp.find_costs([(a[1], a[0])])
        try:
            pts = mcp.traceback((b[1], b[0]))
        except ValueError:
            return [a, b]                            # 이어지지 않으면 직선으로
        return [(int(x), int(y)) for y, x in pts]

    def simplify(self, pts, tol=6.0):
        """꺾인 길을 **곧은 몇 토막**으로 편다 — 계단처럼 지그재그로 걷지 않게."""
        if len(pts) < 3:
            return list(pts)
        out = [pts[0]]
        i = 0
        while i < len(pts) - 1:
            j = len(pts) - 1
            while j > i + 1:
                if self._straight(pts[i], pts[j], tol):
                    break
                j -= 1
            out.append(pts[j])
            i = j
        return out

    def _straight(self, a, b, tol):
        n = max(2, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 4))
        for s in range(n + 1):
            u = s / float(n)
            if not self.walkable(a[0] + (b[0] - a[0]) * u,
                                 a[1] + (b[1] - a[1]) * u):
                return False
        return True

    # ── 가림 (walk-behind) ───────────────────────────────────────
    def occluders(self):
        """[(마스크, 기준선 y)] — 발이 기준선보다 **위**면 캐릭터를 덮는다.

        ★AGS 의 walk-behind 를 그대로 옮긴 것이다. 배경마다 8비트 마스크 한 장
          (0=없음, 1..N=조각 번호)과 조각마다 기준선 y 하나면 된다.
          난간 너머에서 앞구르기를 하면 난간이 저절로 앞을 가린다.
        """
        out = []
        info = self.doc.get("occluders")
        p = os.path.join(ANCHOR_DIR, self.bg + "_occl.png")
        if not info or not os.path.exists(p):
            return out
        idx = np.asarray(Image.open(p).convert("L").resize((W, H), Image.NEAREST))
        for k, base in sorted(info.items()):
            out.append((idx == int(k), float(base)))
        return out

    def compose(self, canvas, layers):
        """배경 위에 캐릭터들을 **발 y 순서로** 얹고, 가림 조각을 다시 덮는다.

        layers = [(발y, RGBA 이미지, x, 화면키)] — 발이 위(먼 것)부터 그린다.
        """
        for foot, im, x, h in sorted(layers, key=lambda d: d[0]):
            s = min(1.0, h / float(im.height))
            w2 = max(1, int(round(im.width * s)))
            h2 = max(1, int(round(im.height * s)))
            canvas.alpha_composite(im.resize((w2, h2), Image.LANCZOS),
                                   (int(x - w2 / 2), int(foot - h2)))
            # ★이 캐릭터보다 앞에 있는 조각을 다시 얹는다
            for mask, base in self.occluders():
                if foot < base:                       # 캐릭터가 그 조각보다 뒤에 있다
                    src = Image.open(os.path.join(BG_DIR, self.bg + ".png")) \
                        .convert("RGBA").resize((W, H), Image.LANCZOS)
                    canvas.paste(src, (0, 0), Image.fromarray(
                        (mask * 255).astype(np.uint8), "L"))
        return canvas


def gait_for(d_m):
    return "run" if d_m > 3.5 else "walk"


def walk_plan(stage, a, b, who="stickman", gait=None):
    """★a 에서 b 로 가는 **완전한 계획** — 좌표·키·시간·배속을 다 계산한다.

    돌려주는 것: [(t0, t1, x0, x1, h0, h1, foot0, foot1, 컷fps)]
    """
    pts = stage.simplify(stage.path(a, b))
    legs = []
    t = 0.0
    for i in range(len(pts) - 1):
        p, q = pts[i], pts[i + 1]
        d = stage.dist_m(p, q)
        g = gait or gait_for(d)
        dur = max(0.15, d / SPEED[g])
        h0, h1 = stage.h_at(p[1], who), stage.h_at(q[1], who)
        # 발이 안 미끄러지는 컷 재생속도 — 초당 바퀴수 × 한 바퀴 프레임수
        fps = (d / dur) / CYCLE_M[g] * (10 if g == "walk" else 20)
        legs.append((round(t, 2), round(t + dur, 2), p[0], q[0],
                     round(h0), round(h1), p[1], q[1], round(fps, 1), g))
        t += dur
    return legs, t


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    bg = sys.argv[1]
    st = Stage(bg)
    m = st.walk_mask()
    print("[%s] 지평선 %d · K %.3f · 앞줄 %d" % (bg, st.horizon, st.k, st.front_h))
    print("  밟을 수 있는 화소 %d (%.1f%%)" % (m.sum(), 100.0 * m.mean()))
    print("  발 y 별 스틱맨 키 — " + " ".join(
        "%d:%d" % (y, round(st.h_at(y))) for y in (720, 680, 640, 600, 560)))
    occ = st.occluders()
    print("  가림 조각 %d개" % len(occ))

    if "--path" in sys.argv:
        i = sys.argv.index("--path")
        a = tuple(int(v) for v in sys.argv[i + 1].split(","))
        b = tuple(int(v) for v in sys.argv[i + 2].split(","))
        legs, tot = walk_plan(st, a, b)
        print("\n  %s → %s · %.1f초 · 다리 %d개" % (a, b, tot, len(legs)))
        for t0, t1, x0, x1, h0, h1, f0, f1, fps, g in legs:
            print("   %5.2f~%5.2f  %-4s x %4d→%4d  키 %3d→%3d  발 %3d→%3d  %.1ffps"
                  % (t0, t1, g, x0, x1, h0, h1, f0, f1, fps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
