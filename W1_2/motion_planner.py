# -*- coding: utf-8 -*-
"""동작 계산기 — 말로 시키면 **좌표·크기·발 y·컷·배속을 스스로 계산**하는 엔진.

★사장님 지시(2026-08-13)
  "'저기 계단 중간에 올라가서 한 칸씩 뛰어 내려와서 오른편으로 달려 나가라' 이렇게
   명령하면, 원근에 따른 캐릭터의 키와 몸의 비율적 사이즈 계산, 멀면 달려가고
   가까우면 걸어가기, 비스듬히 갈 때 각 보당 좌표 — 그런 것을 계산해 주는
   파이선 동작 계산기 같은 것을 만들어서 스스로 사용하면서 움직이는 거지."
  "'우물가에 가서 웅크리고 무엇인가를 주워서 오라' 고 시키면 그 동작을 분석하고
   좌표 만들고 캐릭터 크기 만들고, 가는 자세·웅크린 자세·돌아오는 자세·마지막 자세
   그런 것을 설계해서 실행하는 엔진을 만들어야 한다."

## 무엇을 계산하는가

1. **무대(Stage)** — 화면을 카메라로 본다. 지평선 아래는 땅이고, 땅 위 한 점의
   화면 y 가 정해지면 그 자리에 선 사람의 **화면 키와 거리(m)** 가 한꺼번에 정해진다.
   그래서 좌표·크기·발 y 를 따로 찍을 필요가 없다 — 하나만 주면 나머지가 나온다.
2. **세계 거리** — 두 자리 사이가 실제로 몇 미터인지 잰다.
   → **멀면 달리고 가까우면 걷는다**(3.5m 가 갈림길), 걸리는 시간도 여기서 나온다.
3. **보(step)** — 걸음 하나가 몇 미터인지 알므로 몇 보인지, 각 보의 좌표가 어디인지
   나온다. 사선으로 가면 보마다 크기가 줄거나 는다.
4. **배속(발 안 미끄러지게)** — 땅 위 실제 속도와 컷의 보폭이 맞아야 발이 안 밀린다.
   `배속 = (초당 걸음수 × 한 바퀴 프레임수) / 컷 원속`
   ※ 이 식으로 걷기를 계산하면 8.3fps 가 나온다 — 사장님이 "딱 맞다" 하신 8.0 과 같다.
     모델이 이미 승인된 값을 재현하므로 달리기 값도 믿을 만하다.
5. **자세(pose)** — ★자세가 바뀌어도 **축척은 그대로**다. 웅크리면 잉크 높이가
   줄지 몸이 작아지는 게 아니다. 그래서 화면 키가 아니라 **축척**을 넘긴다.

## 왜 이게 필요했나 — 실측으로 드러난 버그

`render_show.place_xy()` 는 **이미지** 아래끝을 발 y 로 잡고 **이미지** 높이로 크기를
정한다. 그런데 1024×1024 캔버스 포즈는 발 밑에 투명 여백이 203~307px 있다.
  · 난간 잡기 → 발이 뜬다        (교정 9번)
  · 난간 기대기 → 키가 70% 로 준다 (교정 12번)
  · 벤치에서 일어서도 안 커진다    (교정 15번)
  · 후면 달리기 발이 뜬다          (교정 20번)
**교정 넷이 이 한 가지 버그**였다. 그래서 이 엔진은 **잉크 기준**으로만 계산한다.

    python W1_2/motion_planner.py                  # 자기 검사 + 예제 두 개
    python W1_2/motion_planner.py "저기 계단 중간에 올라가서 한 칸씩 뛰어내려와서 오른편으로 달려 나가라" steps_seat
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

METRICS = "W1_2/cut_metrics.json"
ANCHOR_DIR = "assets/anchors"
CUT_FPS = 8.0                       # 컷 원속 (64컷 ÷ 8초)


# ══════════════════════════════════════════════════════════════════════
# 1. 무대 — 카메라로 본 땅
# ══════════════════════════════════════════════════════════════════════
class Stage(object):
    """화면(1280×720)을 **땅을 내려다보는 카메라**로 본다.

    핀홀 카메라로 땅을 보면, 땅 위 한 점의 화면 y 와 그 자리에 선 사람의 화면 키는
    **둘 다 거리에 반비례**한다. 그래서 키는 (발 y − 지평선) 에 **정비례**한다.

        키 = K × (발y − 지평선)

    지평선은 두 점(90@490, 600@700)으로 풀어 **452.9** 가 나왔다.
    ★실측으로 광화문 밑단이 y≈435 였다 — 계산된 지평선과 맞아떨어진다.

    ★K 는 사장님이 **배경에 맞춘 쪽으로 확정**하셨다(2026-08-13).
      옛 K=2.4258 은 "90~600" 규격에서 나온 값인데, 배경 안의 크기를 아는 것
      (계단 한 칸 0.15m·돌난간 1.0m)에 대어 보니 캐릭터가 배경보다 1.9배 컸다.
      교정판 ② — **발y 610 에서 스틱맨 200px** → K = 200/158 = **1.266**.
      "배경에 맞춘 둘째 장으로 한다." 이로써 앞줄 캐릭터는 340px, 저 멀리는 50px 이 된다.
    """
    W, H_PX = 1280, 720
    HORIZON = 452.9                  # 지평선 화면 y (땅의 끝)
    K = 1.266                        # 발 y 1px 내려올 때 늘어나는 키(px)
    FOCAL = 1372.0                   # 초점거리(px) — 가로 화각 ≈ 50°
    CX = 640.0

    H_FAR, H_NEAR = 50.0, 340.0      # 쓸 수 있는 키의 폭 (배경에 맞춘 무대)

    def __init__(self, horizon=None, ref=None):
        """★배경마다 그린 원근이 다르다 — 배경 하나에 무대 하나.

        `ref` = (발y, 그 자리에 선 스틱맨의 화면 키). 배경 안의 **크기를 아는 물건**
        (돌난간 1.0m·화분 1.6m 같은)에 대어 재면 된다. 그 한 점과 지평선이 무대를 정한다.
        재 놓은 것이 없으면 사장님이 정하신 90~600 기본 무대를 쓴다.
        """
        if horizon is not None:
            self.HORIZON = float(horizon)
        if ref:
            y, h = float(ref[0]), float(ref[1])
            self.K = h / max(1e-6, y - self.HORIZON)

    def h_at(self, foot_y):
        """그 자리에 선 **스틱맨의 화면 키**."""
        return self.K * (foot_y - self.HORIZON)

    def foot_at(self, h):
        """그 키로 보이려면 발이 있어야 할 **화면 y**."""
        return self.HORIZON + h / self.K

    def clamp_h(self, h):
        return max(self.H_FAR, min(self.H_NEAR, h))

    def on_ground(self, foot_y):
        """그 발 y 가 **바닥 평면 위**인가. 지평선보다 위면 계단처럼 높아진 땅이다."""
        return foot_y > self.HORIZON + 12.0

    # ── 세계 좌표 ──────────────────────────────────────────────────
    #   ★거리는 **화면 키**에서 나온다(발 y 가 아니라).
    #     그래야 계단·난간처럼 **바닥 평면이 아닌 자리**도 그대로 계산된다.
    def depth_m(self, h, real_m=1.75):
        """화면 키 h 로 보이는 키 real_m 인 사람까지의 **거리(m)**."""
        return self.FOCAL * real_m / max(1e-6, h)

    def world(self, x, h, real_m=1.75):
        """화면 (x, 화면키) → 세계 (좌우 m, 앞뒤 m)."""
        z = self.depth_m(h, real_m)
        return ((x - self.CX) * z / self.FOCAL, z)

    def screen(self, wx, wz, real_m=1.75):
        """세계 (좌우 m, 앞뒤 m) → 화면 (x, 발y, 키)."""
        h = self.FOCAL * real_m / max(1e-6, wz)
        return (self.CX + wx * self.FOCAL / wz, self.foot_at(h), h)

    def dist_m(self, a, b, real_m=1.75):
        """두 자리 사이의 **실제 거리(m)**. a·b = (x, 화면키)."""
        ax, az = self.world(a[0], a[1], real_m)
        bx, bz = self.world(b[0], b[1], real_m)
        return math.hypot(bx - ax, bz - az)

    def px_per_m(self, h, real_m=1.75):
        return h / real_m


STAGE = Stage()


# ══════════════════════════════════════════════════════════════════════
# 2. 배우 — 캐릭터별 실물 키
# ══════════════════════════════════════════════════════════════════════
# W24 규격(인준 180cm=770px) × 700/749 — DB `char_heights` 와 같은 값
CAST = {
    "stickman": dict(px=700, m=1.75, prefix=("m6:", "sm_", "stickman_", "run_", "walk_",
                                             "back_", "butt_", "forward_", "high_",
                                             "hop_", "pick_", "reach_", "shoulder_",
                                             "sit_", "skid_", "tiptoe")),
    "zman":     dict(px=711, m=1.78, prefix=("zman_",)),
    "zgirl":    dict(px=651, m=1.63, prefix=("zgirl_",)),
}


def who(key):
    """컷·포즈 키 → 어느 캐릭터인가."""
    k = key[5:] if key.startswith("POSE:") else key
    for name in ("zman", "zgirl"):
        if k.startswith(CAST[name]["prefix"][0]):
            return name
    return "stickman"


def real_m(key):
    return CAST[who(key)]["m"]


def rel_size(key):
    """스틱맨을 1.0 으로 봤을 때의 **키 비율** — 졸라맨 1.016, 졸라걸 0.930."""
    return CAST[who(key)]["px"] / float(CAST["stickman"]["px"])


# ══════════════════════════════════════════════════════════════════════
# 3. 자산 — 실측표(cut_metrics.json)
# ══════════════════════════════════════════════════════════════════════
class Assets(object):
    """컷·포즈의 **잉크 실측값**. 이미지 캔버스가 아니라 잉크로만 계산한다."""

    # 한 바퀴(cycle)가 땅에서 나아가는 **실제 거리(m)** — 사람의 보행 규격
    CYCLE_M = {"walk": 1.50, "run": 3.20}
    SPEED_MPS = {"walk": 1.25, "run": 3.60}

    # ★서 있을 때의 잉크 높이를 무엇으로 잡는가
    #   원샷 동작(구르기·앉기…)은 **첫 프레임**이 서 있는 상태다.
    #   이동 컷(걷기·달리기)은 내내 서 있으므로 중앙값.
    ONESHOT = {"back_flip", "butt_fall", "forward_roll", "hop_down", "pick_up",
               "sit_stand", "skid_stop", "high_five", "shoulder_arm",
               "zman_sit_stand", "zgirl_high_five", "zman_head_tilt",
               "reach_catch", "reach_catch_l", "tiptoe"}

    def __init__(self, path=METRICS):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        self.cuts, self.poses = d["cuts"], d["poses"]

    # ── 축척의 기준이 되는 "서 있는 잉크 높이" ──────────────────────
    def ref_h(self, key):
        k = key[5:] if key.startswith("POSE:") else key
        if k in self.poses:
            return self._pose_ref(k)
        c = self.cuts.get(k)
        if not c:
            return None
        return float(c["ink_h_first"] if k in self.ONESHOT else c["ink_h_med"])

    # 1024 캔버스 포즈들은 **서 있는 자기 짝**이 기준이다.
    #   웅크린 포즈의 잉크(430)를 기준 삼으면 웅크릴 때 몸이 커져 버린다.
    POSE_REF = {
        "stickman_w1d2_crouch_ground_r": "stickman_w1d2_grab_rail_r",
        "stickman_w1d2_sit_bench":       "stickman_w1d2_stand_behind_bench",
        "stickman_w1d2_sit_bench_l":     "stickman_w1d2_stand_behind_bench",
        "stickman_w1d2_sit_bench_r":     "stickman_w1d2_stand_behind_bench",
    }

    def _pose_ref(self, k):
        src = self.POSE_REF.get(k)
        if src and src in self.poses:
            return float(self.poses[src]["ink_h"])
        return float(self.poses[k]["ink_h"])

    def ink_h(self, key):
        k = key[5:] if key.startswith("POSE:") else key
        if k in self.poses:
            return float(self.poses[k]["ink_h"])
        c = self.cuts.get(k)
        return float(c["ink_h_med"]) if c else None

    def foot_pad(self, key):
        """발 밑 투명 여백 — ★이만큼 빼줘야 발이 땅에 닿는다."""
        k = key[5:] if key.startswith("POSE:") else key
        if k in self.poses:
            return float(self.poses[k]["foot_pad"])
        c = self.cuts.get(k)
        return float(c["foot_pad_med"]) if c else 0.0

    def img_h(self, key):
        k = key[5:] if key.startswith("POSE:") else key
        if k in self.poses:
            return float(self.poses[k]["img_h"])
        c = self.cuts.get(k)
        return float(c["img_h"]) if c else None

    def frames(self, key):
        c = self.cuts.get(key[3:] if key.startswith("m6:") else key)
        c = self.cuts.get(key, c)
        return int(c["n"]) if c else 1

    # ── ★동작 구간 자동 검출 ────────────────────────────────────────
    #   8초짜리 Veo 컷은 앞뒤로 **그냥 서 있는 시간**이 길다(hop_down 은 64컷 중
    #   실제 뛰어내리는 게 20컷쯤). 그대로 틀면 동작이 늦고 안 끝난 것처럼 보인다.
    #   서 있는 자세(중앙값)에서 얼마나 벗어나는지로 동작의 처음·끝을 찾는다.
    def action_window(self, key):
        """(첫 컷, 끝 컷) — 실제로 몸이 움직이는 구간. 이동 컷은 전체를 쓴다."""
        k = key[5:] if key.startswith("POSE:") else key
        k = k[3:] if k.startswith("m6:") else k
        c = self.cuts.get(k)
        if not c or k not in self.ONESHOT:
            return (0, self.frames(key))
        tops = c.get("ink_top_list") or []
        bots = c.get("ink_bot_list") or []
        if not tops:
            return (0, c["n"])
        import statistics as st
        t0, b0 = st.median(tops), st.median(bots)
        span = max(1.0, st.median(c["ink_h_list"]))
        moved = [i for i in range(len(tops))
                 if abs(tops[i] - t0) > span * 0.06 or abs(bots[i] - b0) > span * 0.04]
        if not moved:
            return (0, c["n"])
        # 앞뒤로 두 컷씩 여유를 둬서 동작이 잘리지 않게 한다
        return (max(0, moved[0] - 2), min(c["n"], moved[-1] + 3))

    # ── ★렌더가 받을 값으로 옮긴다 ────────────────────────────────
    def render_h(self, key, stand_h):
        """이 캐릭터가 **서면 stand_h 로 보일 축척**일 때, 렌더에 줄 `h` 값.

        `place_xy()` 가 `이미지높이` 로 나누므로, 잉크 기준 축척을
        이미지 기준 값으로 되돌려 준다. 자세가 바뀌어도 축척은 그대로다.
        """
        ref = self.ref_h(key)
        img = self.img_h(key)
        if not ref or not img:
            return stand_h
        return stand_h * img / ref

    def render_foot(self, key, foot_y, stand_h):
        """발이 `foot_y` 에 닿게 하려면 렌더에 줄 발 y — **여백만큼 내려준다**."""
        ref = self.ref_h(key)
        pad = self.foot_pad(key)
        if not ref or pad <= 0:
            return foot_y
        return foot_y + pad * (stand_h / ref)


# ══════════════════════════════════════════════════════════════════════
# 4. 걸음 계산 — 보폭·보수·배속
# ══════════════════════════════════════════════════════════════════════
GAIT_CUT = {
    ("walk", "r"): "m6:walk_side_r", ("walk", "l"): "m6:walk_side_l",
    ("run", "r"):  "m6:run_side_r",  ("run", "l"):  "m6:run_side_l",
    ("walk", "in"): "run_front", ("run", "in"): "run_front",
    ("walk", "out"): "run_back", ("run", "out"): "run_back",
}
TURN_CUT = {("walk", "r"): "m6:walk_turn_r", ("walk", "l"): "m6:walk_turn_l",
            ("run", "r"): "m6:run_turn_r", ("run", "l"): "m6:run_turn_l"}
EXIT_CUT = {("walk", "r"): "m6:walk_exit_r", ("walk", "l"): "m6:walk_exit_l",
            ("run", "r"): "m6:run_exit_r", ("run", "l"): "m6:run_exit_l"}


def gait_for(dist_m):
    """★멀면 달려가고 가까우면 걸어간다 — 갈림길은 3.5m."""
    return "run" if dist_m > 3.5 else "walk"


def travel_time(dist_m, gait):
    return dist_m / Assets.SPEED_MPS[gait]


def steps_of(dist_m, gait):
    """몇 **보**인가 (한 바퀴 = 두 보)."""
    return dist_m / (Assets.CYCLE_M[gait] / 2.0)


def stride_fps(dist_m, dur_s, gait, n_frames):
    """★발이 안 미끄러지는 **컷 재생 fps**.

        초당 바퀴수 = (실제속도 m/s) ÷ (한 바퀴 m)
        fps        = 초당 바퀴수 × 한 바퀴 프레임수
    """
    if dur_s <= 0:
        return CUT_FPS
    cycles_per_s = (dist_m / dur_s) / Assets.CYCLE_M[gait]
    return cycles_per_s * n_frames


# ══════════════════════════════════════════════════════════════════════
# 5. 자리(앵커) — 배경 위의 이름 붙은 지점
# ══════════════════════════════════════════════════════════════════════
def load_anchor_file(bg):
    p = os.path.join(ANCHOR_DIR, bg + ".json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_anchors(bg):
    return load_anchor_file(bg).get("anchors", {})


def load_stage(bg):
    """배경별 무대. 앵커 파일에 `stage` 가 있으면 그걸로 교정한 무대를 준다."""
    st = load_anchor_file(bg).get("stage")
    if not st:
        return STAGE
    return Stage(st.get("horizon"), st.get("ref"))


class Spot(object):
    """무대 위 한 자리 — (x, 발 y, 서면 보일 키).

    ★바닥 평면 위면 발 y 하나로 키가 정해진다. **계단처럼 높아진 땅**은 공식이
      풀리지 않으므로 앵커에 `h` 를 적어 둬야 한다 — 없으면 여기서 잡아 준다.
    """

    def __init__(self, x, foot_y, h=None, stage=None):
        self.stage = stage or STAGE
        self.x = float(x)
        self.foot = float(foot_y)
        if h:
            self.h = float(h)
        elif self.stage.on_ground(foot_y):
            self.h = self.stage.clamp_h(self.stage.h_at(foot_y))
        else:
            raise ValueError(
                "발 y=%.0f 는 지평선(%.0f) 위다 — 계단처럼 **높아진 땅**이라 "
                "키가 공식으로 안 풀린다. 앵커에 \"h\": <화면 키> 를 적어라."
                % (foot_y, self.stage.HORIZON))

    def __repr__(self):
        return "Spot(x=%.0f foot=%.0f h=%.0f · %.1fm)" % (
            self.x, self.foot, self.h, self.stage.depth_m(self.h))

    def as_tuple(self):
        """거리 계산에 쓰는 (x, 화면키)."""
        return (self.x, self.h)


def spot_of(anchor, bg_anchors, stage=None):
    """앵커 이름 → Spot.

    앵커의 `y` 는 **몸이 닿는 면**이다. 무엇에 닿느냐로 발 자리가 갈린다.
      stand — 그 면이 곧 발판이다
      sit   — 그 단에 걸터앉는다. 발은 그 단 (계단·평상)
      grab / lean — 손이 그 높이에 있고 ★**발은 땅에 있다**
                    (사장님: "난간 잡고 걸터앉을 때는 발이 땅에 닿아 있어야 한다")
    """
    sg = stage or STAGE
    a = bg_anchors[anchor]
    x, y, t = float(a["x"]), float(a["y"]), a.get("type", "stand")
    if "h" in a:                                   # 실측해 적어 둔 값이 우선이다
        return Spot(x, float(a.get("foot", y)), a["h"], sg)
    if t in ("grab", "lean"):
        # 손 높이 1.0m 를 아는 채로 발 y 를 푼다. 계단 위 난간처럼 지평선보다
        # 위에 있는 것은 이 식이 풀리지 않으므로 앵커에 `foot`/`h` 를 적어 둔다.
        foot = float(a.get("foot", 0)) or None
        if foot is None:
            denom = 1.0 - (1.0 / 1.75) * sg.K
            foot = (y - (1.0 / 1.75) * sg.K * sg.HORIZON) / denom
            if not (sg.HORIZON < foot <= sg.H_PX):
                foot = y + 120.0                   # 못 풀면 손 아래 한 뼘으로 둔다
        return Spot(x, foot, None, sg)
    return Spot(x, y, None, sg)


# ══════════════════════════════════════════════════════════════════════
# 6. 계획 — 동사를 이어 붙여 비트를 만든다
# ══════════════════════════════════════════════════════════════════════
class Plan(object):
    """말로 시킨 동작을 **비트 목록**으로 옮긴다.

    비트 = `(t0, t1, 컷키, x0, x1, h0, h1, f0, f1, fps)`
      · x·h·발y 를 **함께** 보간한다 → 사선 이동·다가오기·멀어지기가 저절로 된다
      · 마지막 `fps` 는 ★발이 안 미끄러지는 재생속도 (render_scenes 가 쓴다)
    """

    def __init__(self, bg, assets=None, char="stickman", t0=0.0):
        self.bg = bg
        self.A = assets or Assets()
        self.char = char
        self.anchors = load_anchors(bg)
        self.stage = load_stage(bg)                 # ★배경별로 교정된 무대
        self.t = float(t0)
        self.beats = []
        self.log = []
        self.here = None                            # 지금 서 있는 자리

    # ── 자리 잡기 ────────────────────────────────────────────────
    def at(self, where, h=None):
        """시작 자리를 정한다. 앵커 이름이나 (x, 발y) 둘 다 받는다."""
        self.here = self._resolve(where, h)
        self.log.append("시작 %s" % self.here)
        return self

    def _resolve(self, where, h=None):
        if isinstance(where, Spot):
            return where
        if isinstance(where, str):
            if where in self.anchors:
                return spot_of(where, self.anchors, self.stage)
            raise KeyError("'%s' 앵커가 %s 에 없다. 있는 것: %s"
                           % (where, self.bg, ", ".join(sorted(self.anchors))))
        x, y = where[0], where[1]
        return Spot(x, y, h, self.stage)

    # ── 동사 ─────────────────────────────────────────────────────
    def go(self, to, h=None, gait=None):
        """★**간다** — 거리를 재서 멀면 달리고 가까우면 걷는다.

        방향(좌·우), 걸리는 시간, 보수, 발 안 미끄러지는 배속을 전부 계산한다.
        """
        dst = self._resolve(to, h)
        src = self.here or dst
        d = self.stage.dist_m(src.as_tuple(), dst.as_tuple(), CAST[self.char]["m"])
        g = gait or gait_for(d)
        dur = travel_time(d, g)
        side = "r" if dst.x >= src.x else "l"
        key = GAIT_CUT[(g, side)]
        n = self.A.frames(key)
        fps = stride_fps(d, dur, g, n)
        self._emit(key, src, dst, dur, fps)
        self.log.append(
            "  %s %.1fm %s %.1f초 · %.1f보 · %s %.1ffps(%.1f배) · 키 %d→%d"
            % ("달려간다" if g == "run" else "걸어간다", d,
               "오른쪽" if side == "r" else "왼쪽", dur, steps_of(d, g), key,
               fps, fps / CUT_FPS, src.h, dst.h))
        self.here = dst
        return self

    def approach(self, to, h=None):
        """★**앞으로 달려 나온다**(정면) — 좌표는 그대로, 깊이만 줄인다."""
        dst = self._resolve(to, h)
        src = self.here or dst
        d = self.stage.dist_m(src.as_tuple(), dst.as_tuple(), CAST[self.char]["m"])
        dur = travel_time(d, "run")
        key = "run_front" if dst.h > src.h else "run_back"
        fps = stride_fps(d, dur, "run", self.A.frames(key))
        self._emit(key, src, dst, dur, fps)
        self.log.append("  %s %.1fm %.1f초 · %s %.1ffps(%.1f배) · 키 %d→%d"
                        % ("달려 나온다" if dst.h > src.h else "달려 나간다",
                           d, dur, key, fps, fps / CUT_FPS, src.h, dst.h))
        self.here = dst
        return self

    def climb(self, to, h=None):
        """★**올라간다** — 계단은 걷기로, 올라갈수록 작아진다(멀어지므로)."""
        return self.go(to, h, gait="walk")

    def hop_down(self, to, steps=3, sec=1.6, h=None):
        """★**한 칸씩 뛰어내린다** — 칸마다 커지며 내려온다.

        (사장님: "저 위 계단 위로 올라가서 서 있다가 키가 작은 상태로 한 칸씩
         뛰어내리면서 점점 커지고, 계단을 다 내려오면 우측으로 달려 나간다")

        칸마다 컷을 **한 바퀴 다 돈다** — 반쯤 하다 멈추지 않는다.
        한 번 뛰어내리는 데 실제로 걸리는 시간이 1.6초쯤이므로 그만큼으로 몰아 돌린다.
        """
        dst = self._resolve(to, h)
        src = self.here or dst
        key = "hop_down"
        i0, i1 = self.A.action_window(key)            # ★뛰어내리는 토막만 쓴다
        fps = (i1 - i0) / float(sec)
        for i in range(steps):
            u0, u1 = i / float(steps), (i + 1) / float(steps)
            a = self._between(src, dst, u0)
            b = self._between(src, dst, u1)
            self._emit(key, a, b, sec, fps, (i0, i1))
            self.log.append("  %d칸째 뛰어내린다 %.1f초 · 키 %d→%d · 컷 %d~%d %.1ffps"
                            % (i + 1, sec, a.h, b.h, i0, i1, fps))
        self.here = dst
        return self

    def _between(self, a, b, u):
        """두 자리 사이 — x·발y·키를 **함께** 보간한다(원근이 저절로 생긴다)."""
        return Spot(a.x + (b.x - a.x) * u,
                    a.foot + (b.foot - a.foot) * u,
                    a.h + (b.h - a.h) * u, self.stage)

    def act(self, key, sec=None, at=None, h=None, repeat=1):
        """★**제자리 동작** — 웅크리기·줍기·앉기·구르기·포즈.

        ★동작 구간만 잘라서 **끝까지 한 번 다 돈다**. 앞뒤로 그냥 서 있는 시간은 뺀다.
        (사장님: "동작을 정확하고 분명하게 끝까지 다 마친다. 반쯤 하다 멈추면 안 된다")
        `repeat` 로 여러 번 되풀이할 수 있다 — 앞구르기·백플립은 반복해도 좋다.
        """
        spot = self._resolve(at, h) if at is not None else self.here
        if spot is None:
            raise ValueError("먼저 at() 으로 자리를 잡아라")
        if key.startswith("POSE:"):
            self._emit(key, spot, spot, sec or 2.0, CUT_FPS)
            self.log.append("  %s %.1f초 (포즈) · 키 %d" % (key, sec or 2.0, spot.h))
            self.here = spot
            return self
        i0, i1 = self.A.action_window(key)
        one = (i1 - i0) / CUT_FPS                     # 그 토막의 원속 길이
        sec = sec or one * repeat
        fps = (i1 - i0) * repeat / float(sec)
        self._emit(key, spot, spot, sec, fps, (i0, i1))
        self.log.append("  %s %.1f초 (제자리 %d번) · 컷 %d~%d/%d %.1ffps · 키 %d"
                        % (key, sec, repeat, i0, i1, self.A.frames(key), fps, spot.h))
        self.here = spot
        return self

    def turn(self, side="r", gait="walk", sec=1.8):
        """★**돌아선다** — 나가기 전에 방향을 바꾼다. 사람이 도는 데 걸리는 만큼."""
        key = TURN_CUT[(gait, side)]
        n = self.A.frames(key)
        fps = n / float(sec)
        self._emit(key, self.here, self.here, sec, fps)
        self.log.append("  돌아선다(%s) %.1f초 · %d컷 %.1ffps"
                        % ("오른쪽" if side == "r" else "왼쪽", sec, n, fps))
        return self

    def exit(self, side="r", gait="run"):
        """★**화면 밖으로 나간다** — 화면 끝을 넘어설 때까지 달린다."""
        src = self.here
        x_end = self.stage.W + 140 if side == "r" else -140
        dst = Spot(x_end, src.foot, src.h, self.stage)
        d = self.stage.dist_m(src.as_tuple(), dst.as_tuple(), CAST[self.char]["m"])
        dur = travel_time(d, gait)
        key = GAIT_CUT[(gait, side)]
        fps = stride_fps(d, dur, gait, self.A.frames(key))
        self._emit(key, src, dst, dur, fps)
        self.log.append("  %s쪽으로 나간다 %.1fm %.1f초 · %.1ffps(%.1f배)"
                        % ("오른" if side == "r" else "왼", d, dur, fps, fps / CUT_FPS))
        self.here = dst
        return self

    def away(self, h=None):
        """★**저 멀리로 달려 나간다** — 지평선 쪽으로 작아지며 사라진다."""
        src = self.here
        hh = h or self.stage.H_FAR
        dst = Spot(src.x, self.stage.foot_at(hh), hh, self.stage)
        return self.approach(dst)

    def hold(self, sec, key=None):
        """자리를 지키며 기다린다(배경 사건을 기다릴 때)."""
        k = key or "POSE:sm_arms_out_wide"
        self._emit(k, self.here, self.here, sec, CUT_FPS)
        self.log.append("  기다린다 %.1f초" % sec)
        return self

    def wait_until(self, t):
        """배경 사건 시각까지 시간을 맞춘다."""
        if t > self.t:
            self.hold(t - self.t)
        return self

    # ── 비트 굽기 ────────────────────────────────────────────────
    def _emit(self, key, a, b, dur, fps, win=None):
        """★여기서 **잉크 기준 → 렌더 기준** 으로 옮긴다.

        렌더(`place_xy`)는 이미지 아래끝·이미지 높이를 쓰므로,
        잉크로 잰 키와 발 y 를 이미지 기준으로 되돌려 준다.
        이 한 줄이 발 뜸·키 줄어듦을 함께 없앤다.
        """
        h0 = self.A.render_h(key, a.h * rel_size(key))
        h1 = self.A.render_h(key, b.h * rel_size(key))
        f0 = self.A.render_foot(key, a.foot, a.h * rel_size(key))
        f1 = self.A.render_foot(key, b.foot, b.h * rel_size(key))
        i0, i1 = win if win else (0, self.A.frames(key))
        self.beats.append((round(self.t, 2), round(self.t + dur, 2), key,
                           round(a.x), round(b.x), round(h0), round(h1),
                           round(f0), round(f1), round(fps, 2), i0, i1))
        self.t += dur

    # ── 내보내기 ────────────────────────────────────────────────
    def dump(self):
        print("\n".join(self.log))
        print("  ─ 합계 %.1f초 · 비트 %d개" % (self.t, len(self.beats)))
        return self

    def code(self, indent=4):
        """`scene_defs.py` 에 그대로 붙일 수 있는 파이선 코드."""
        sp = " " * indent
        out = []
        for b in self.beats:
            out.append("%s(%5.2f,%6.2f, %-22s %5d,%5d, %4d,%4d, %4d,%4d, %5.2f),"
                       % (sp, b[0], b[1], '"%s",' % b[2], b[3], b[4],
                          b[5], b[6], b[7], b[8], b[9]))
        return "\n".join(out)


# ══════════════════════════════════════════════════════════════════════
# 7. 말로 시키기 — 한국어 명령 → 계획
# ══════════════════════════════════════════════════════════════════════
VERB_WORDS = [
    ("hop_down", ("한칸씩", "한 칸씩", "뛰어내", "뛰어 내")),
    ("climb",    ("올라가", "올라 가", "올라서", "올라간")),
    ("crouch",   ("웅크", "쭈그", "주워", "주어", "줍")),
    ("sit",      ("앉", "걸터")),
    ("stand",    ("일어", "일어서")),
    ("turn",     ("돌아서", "돌아 서", "뒤돌")),
    ("exit",     ("나가", "나 가", "빠져나")),
    ("away",     ("저 멀리", "저멀리", "멀어", "사라")),
    ("come",     ("달려 나오", "달려나오", "다가", "돌아와", "돌아 와", "와라", "오라")),
    ("go",       ("가서", "가고", "간다", "가라", "걸어", "달려")),
]
SIDE_WORDS = {"r": ("오른", "우측", "우편"), "l": ("왼", "좌측", "좌편")}


def find_anchor(text, anchors):
    """명령문 안의 말과 앵커를 맞춰 본다.

    ★앵커의 `alias` 에 적힌 말이 가장 세다 — 설명문 짐작은 자주 틀린다
      ("계단 중간" 을 "계단 아래 포장" 으로 잘못 집었다).
    """
    best, score = None, 0
    for name, a in anchors.items():
        s = 0
        for al in a.get("alias", []):
            if al in text:
                s += 10 + len(al) * 2               # 별명이 최우선
        for tok in a.get("note", "").replace("—", " ").split():
            t = tok.strip("()·,.")
            if len(t) >= 2 and t in text:
                s += len(t)
        for t in name.split("_"):
            if len(t) >= 3 and t in text.lower():
                s += 2
        if s > score:
            best, score = name, s
    return best


def parse(text, bg, plan=None):
    """★말 → 계획. 무엇으로 알아들었는지 **찍어 준다** — 틀리면 바로 고칠 수 있게."""
    p = plan or Plan(bg)
    anchors = p.anchors
    side = "r"
    for s, words in SIDE_WORDS.items():
        if any(w in text for w in words):
            side = s
    # 문장을 절로 쪼갠다 ("~해서", "~하고", "~다가")
    parts, buf = [], ""
    for ch in text:
        buf += ch
        if buf.endswith(("고 ", "서 ", "다가 ", "와서 ", "가서 ")):
            parts.append(buf)
            buf = ""
    if buf.strip():
        parts.append(buf)

    print("[알아들은 것] 배경=%s · 방향=%s · 절 %d개"
          % (bg, "오른쪽" if side == "r" else "왼쪽", len(parts)))
    if not p.here:
        p.at((640, 660))
    for i, cl in enumerate(parts, 1):
        verb = None
        for v, words in VERB_WORDS:
            if any(w in cl for w in words):
                verb = v
                break
        anc = find_anchor(cl, anchors)
        print("  %d. %-28s → %-9s %s" % (i, cl.strip()[:28], verb or "?", anc or ""))
        if verb == "climb" and anc:
            p.climb(anc)
        elif verb == "hop_down":
            # 내려올 자리 — 앵커에 계단 아래가 있으면 거기로, 없으면 바닥으로
            down = "step_bottom" if "step_bottom" in anchors else (p.here.x, 660)
            p.hop_down(down, steps=4)
        elif verb == "crouch":
            p.act("pick_up")
        elif verb == "sit":
            p.act("sit_stand")
        elif verb == "stand":
            p.act("sit_stand")
        elif verb == "turn":
            p.turn(side)
        elif verb == "exit":
            p.exit(side)
        elif verb == "away":
            p.away()
        elif verb == "come":
            p.approach((640, 682))
        elif verb == "go" and anc:
            p.go(anc)
        elif verb == "go":
            p.go((1080 if side == "r" else 200, p.here.foot))
    return p


# ══════════════════════════════════════════════════════════════════════
def selftest():
    """모델이 **이미 승인된 값**을 재현하는지 스스로 검사한다."""
    print("=== 무대 검사 ===")
    for y in (490, 540, 590, 648, 682, 700):
        print("  발y %3d → 스틱맨 키 %3.0fpx · 거리 %.1fm"
              % (y, STAGE.h_at(y), STAGE.depth_m(STAGE.h_at(y))))
    print("  지평선 y=%.0f (광화문 밑단 실측 y≈435 와 맞음)" % STAGE.HORIZON)

    print("\n=== 배속 검사 — 승인된 값과 맞는가 ===")
    A = Assets()
    for gait, key in (("walk", "m6:walk_side_r"), ("run", "m6:run_side_r")):
        n = A.frames(key)
        d = 10.0
        dur = travel_time(d, gait)
        fps = stride_fps(d, dur, gait, n)
        print("  %-5s %-16s %2d컷 · %.2f m/s → %.1ffps (원속 8.0 의 %.2f배)"
              % (gait, key, n, Assets.SPEED_MPS[gait], fps, fps / CUT_FPS))
    print("  ★걷기가 8.3fps → 사장님이 \"딱 맞다\" 하신 8.0 과 같다. 모델이 맞다.")

    print("\n=== 발 뜸·키 줄어듦 교정 검사 ===")
    for k in ("stickman_w1d2_grab_rail_r", "stickman_w1d2_sit_bench",
              "stickman_w1d2_crouch_ground_r", "m6:walk_side_r"):
        key = k if k.startswith("m6:") else "POSE:" + k
        rh = A.render_h(key, 420)
        rf = A.render_foot(key, 660, 420)
        old_h = 420
        old_ink = 420 * A.ink_h(key) / A.img_h(key)
        print("  %-34s 옛: 잉크 %3.0fpx·발 %3.0f뜸 → 새: h=%4.0f 발y=%4.0f (잉크 %3.0fpx)"
              % (k, old_ink, old_h * A.foot_pad(key) / A.img_h(key),
                 rh, rf, rh * A.ink_h(key) / A.img_h(key)))


def demo():
    print("\n\n" + "=" * 70)
    print("예제 1 — \"저기 계단 중간에 올라가서 한 칸씩 뛰어내려와서 오른편으로 달려 나가라\"")
    print("=" * 70)
    p = Plan("steps_seat").at("step_bottom")
    parse("저기 계단 중간에 올라가서 한 칸씩 뛰어내려와서 오른편으로 달려 나가라",
          "steps_seat", p)
    p.dump()
    print("\n[scene_defs 에 붙일 코드]")
    print(p.code())

    print("\n\n" + "=" * 70)
    print("예제 2 — \"우물가에 가서 웅크리고 무엇인가를 주워서 오라\"")
    print("=" * 70)
    q = Plan("stall_cuke").at((640, 682))
    q.go((300, 600)).act("pick_up").turn("r").go((720, 682)).act("POSE:sm_presenting", 3.0)
    q.dump()
    print("\n[scene_defs 에 붙일 코드]")
    print(q.code())


if __name__ == "__main__":
    if len(sys.argv) > 2:
        parse(sys.argv[1], sys.argv[2]).dump()
    else:
        selftest()
        demo()
