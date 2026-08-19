# -*- coding: utf-8 -*-
"""W1-2 **동작 정합 검사** — 사람처럼 움직이는가를 수치로 본다.

사장님 지시(2026-08-15): "움직임이 비정상적인 곳이 많어. 잘 살펴 보고 **리얼하게
사람처럼** 움직이게 렌더해."

눈으로만 훑으면 놓친다. 비트 표(`scene_defs.SCENES`)를 읽어 아래를 짚는다.

  ① **이음매 끊김** — 앞 비트가 끝난 자리와 다음 비트가 시작하는 자리가 다르면
     캐릭터가 순간이동한다. x·키·발 y 셋 다 본다.
  ② **미끄러짐** — 서 있는 포즈(POSE:)인데 x 가 움직이면 발을 붙인 채 미끄러진다.
  ③ **걸음 속도** — 걷기는 ~152 px/s, 달리기는 ~456 px/s 가 실측 기준이다(§0-C).
     너무 느리면 슬로비디오, 너무 빠르면 발이 헛돈다.
  ④ **발 뜸** — 발 y 가 그 키의 원근 지면(FOOT 표)에서 크게 벗어나면 공중에 뜬다.
     ※배경 사정으로 일부러 어긋내는 자리(계단·난간·분수)는 예외로 적어 둔다.
  ⑤ **크기 튐** — 한 비트 안에서 키가 2배 넘게 변하면 확대·축소가 눈에 띈다.

    python W1_2/check_motion.py           # 전부
    python W1_2/check_motion.py 5 6       # 그 씬만
"""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

import scene_defs as S                                    # noqa: E402

WALK = 152.0                       # px/s — 실측 기준 걸음
RUN = 456.0
SEAM_X, SEAM_H, SEAM_F = 40, 40, 40    # 이음매 허용치
SLIDE_X = 24                       # 정지 포즈가 이만큼 넘게 움직이면 미끄러짐
FOOT_TOL = 70                      # 원근 지면에서 이만큼 벗어나면 뜬 것으로 본다

# 발이 지면에 없어도 되는 자리 — 계단·난간·분수·벤치는 배경이 지면을 대신한다
FOOT_FREE = {"steps_seat", "steps_rail", "stall_rail", "bench_pair", "bench_open",
             "fountain_burst"}


# ★깊이로 오가는 컷 — 화면 가로세로 이동이 거의 없이 **키만** 바뀐다.
#   정면 달리기는 다가오고 후면 달리기는 멀어진다. 화면 이동으로 속도를 재면
#   전부 '느리다'로 잡히므로 속도 검사에서 뺀다(키 변화로 따로 본다).
DEPTH = ("run_front", "run_back", "run_exit", "walk_exit", "run_turn", "walk_turn")


def kind_of(key):
    k = key.split(":")[-1]
    if key.startswith("POSE:"):
        return "pose"
    if any(k.startswith(d) for d in DEPTH):
        return "depth"
    if "walk" in k:
        return "walk"
    if "run" in k:
        return "run"
    return "cut"


def check(sc):
    n, bg, sec, ein, eout, beats, extra = sc
    out = []
    prev = None
    for b in beats:
        t0, t1, key, x0, x1, h0, h1 = b[:7]
        f0 = b[7] if len(b) >= 9 else S.foot_of(h0)
        f1 = b[8] if len(b) >= 9 else S.foot_of(h1)
        dur = max(1e-6, t1 - t0)
        kind = kind_of(key)

        # ① 이음매
        if prev:
            px1, ph1, pf1, pt1, pkey = prev
            if abs(x0 - px1) > SEAM_X:
                out.append("이음매 x 끊김 %.2fs  %s→%s  x %d→%d (%+d)"
                           % (t0, pkey, key, px1, x0, x0 - px1))
            if abs(h0 - ph1) > SEAM_H:
                out.append("이음매 키 끊김 %.2fs  %s→%s  키 %d→%d (%+d)"
                           % (t0, pkey, key, ph1, h0, h0 - ph1))
            if abs(f0 - pf1) > SEAM_F:
                out.append("이음매 발 끊김 %.2fs  %s→%s  발 %d→%d (%+d)"
                           % (t0, pkey, key, pf1, f0, f0 - pf1))

        # ② 미끄러짐
        if kind == "pose" and abs(x1 - x0) > SLIDE_X:
            out.append("정지 포즈가 미끄러진다 %.2f~%.2fs  %s  x %d→%d"
                       % (t0, t1, key, x0, x1))

        # ③ 걸음 속도 — ★원근을 반영한다.
        #   가로 이동만 보면 다가오거나 멀어지는 구간을 다 '느리다'고 잡는다.
        #   화면에서 실제로 몸이 지나간 거리는 **가로 + 발 y** 두 축이고,
        #   멀리 있을수록(키가 작을수록) 같은 걸음이 화면에서 짧게 보이므로
        #   평균 키로 되돌려 준다.
        if kind in ("walk", "run"):
            span = ((x1 - x0) ** 2 + (f1 - f0) ** 2) ** 0.5
            h_avg = max(1.0, (h0 + h1) / 2.0)
            v = span / dur * (420.0 / h_avg)          # 키 420 기준으로 환산
            want = WALK if kind == "walk" else RUN
            if v < want * 0.40:
                out.append("%s가 제자리걸음처럼 느리다 %.2f~%.2fs  %s  %.0f px/s (기준 %.0f)"
                           % ("걷기" if kind == "walk" else "달리기",
                              t0, t1, key, v, want))
            elif v > want * 2.4:
                out.append("%s가 너무 빨라 발이 헛돈다 %.2f~%.2fs  %s  %.0f px/s (기준 %.0f)"
                           % ("걷기" if kind == "walk" else "달리기",
                              t0, t1, key, v, want))

        # ④ 발 뜸
        if bg not in FOOT_FREE:
            for tt, hh, ff in ((t0, h0, f0), (t1, h1, f1)):
                want_f = S.foot_of(hh)
                if abs(ff - want_f) > FOOT_TOL:
                    out.append("발이 지면에서 뜬다 %.2fs  %s  키%d 의 지면 %d 인데 발 %d (%+d)"
                               % (tt, key, hh, want_f, ff, ff - want_f))

        # ③-B 깊이 이동은 **키가 얼마나 빨리 변하는가**로 본다.
        #   1초에 키가 8% 도 안 바뀌면 다가오는 것도 멀어지는 것도 아니라 제자리다.
        if kind == "depth" and h0 > 0 and h1 > 0:
            ratio = max(h0, h1) / float(min(h0, h1))
            per_s = ratio ** (1.0 / dur)
            if per_s < 1.08 and abs(x1 - x0) / dur < 120:
                out.append("깊이 이동이 거의 없다(제자리로 보인다) %.2f~%.2fs  %s  "
                           "키 %d→%d, 초당 %.1f%%" % (t0, t1, key, h0, h1,
                                                    (per_s - 1) * 100))

        # ⑤ 크기 튐 — ★원근 이동(멀리서 다가오며 커진다)은 정상이다.
        #   문제는 **제자리에서** 키만 바뀌는 것 — 그건 확대·축소로 보인다.
        moved = abs(x1 - x0) > 60 or abs(f1 - f0) > 40
        if h0 > 0 and not moved:
            r = max(h1 / float(h0), h0 / float(max(1, h1)))
            if r > 1.35:
                out.append("제자리에서 키만 %.2f배 바뀐다(확대·축소로 보인다) "
                           "%.2f~%.2fs  %s  %d→%d" % (r, t0, t1, key, h0, h1))

        prev = (x1, h1, f1, t1, key)
    return out


def main():
    want = {int(a) for a in sys.argv[1:]} if len(sys.argv) > 1 else None
    total = 0
    print("W1-2 동작 정합 검사 — 이음매 · 미끄러짐 · 걸음속도 · 발뜸 · 크기튐\n")
    for sc in S.SCENES:
        if want and sc[0] not in want:
            continue
        rows = check(sc)
        if rows:
            total += len(rows)
            print("  S%-2d %-15s %d건" % (sc[0], sc[1], len(rows)))
            for r in rows:
                print("        · " + r)
    print("\n" + "=" * 70)
    print("★어긋난 자리 %d건" % total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
