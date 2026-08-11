# -*- coding: utf-8 -*-
"""W1-2 스틱맨 동영상 — **파라메트릭 생성**(Flow 대신).

★사장님 판단(2026-08-11): Omni Flash 는 작고 반복되는 요소를 정확히 못 지킨다.
  · 입 모양 — 아/이/오/우 네 모양을 두 번 시도했으나 '원'과 '다문 선'만 오갔다
  · 카드 장수 — PROP COUNT LOCK 을 넣어도 48프레임 중 4장·5장·3장으로 흔들렸다
  그래서 `stickman_factory` 로 프레임을 직접 그린다. 개수·모양이 구조적으로 고정된다.

    python W1_2/make_param_clips.py            # 3개 전부
    python W1_2/make_param_clips.py mouth_cycle
"""
import argparse
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stickman_factory as F                                  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "W1_2", "clips")
TMP = os.path.join(ROOT, "W1_2", "_framebuf")
FPS = 24
DUR = 8.0
W, H = 1280, 720
FIG_H = 620                 # 화면 안 캐릭터 키
HR, LW = 6.6, 1.46          # 가이드 비율


def log(m):
    print(m, flush=True)


def ease(t):
    """0→1 을 부드럽게(가속·감속)."""
    return t * t * (3 - 2 * t)


def hold(t, segs):
    """구간 목록 [(끝시각, 값), …] 에서 t 가 속한 값을 돌려준다."""
    for end, v in segs:
        if t < end:
            return v
    return segs[-1][1]


def lerp(a, b, t):
    return a + (b - a) * t


def pose_at(key, t):
    """시각 t(초)의 포즈 dict 를 만든다."""
    base = dict(hr=HR, lw=LW, facing="front")

    if key == "mouth_cycle":
        # ★2초마다 한 모양씩 — 몸은 완전히 정지
        expr = hold(t, [(2.0, "mouth_a"), (4.0, "mouth_i"),
                        (6.0, "mouth_o"), (DUR, "mouth_u")])
        return dict(base, pts=F.P(), expr=expr)

    if key == "card_lift":
        # ★가슴(28) → **머리 위(2)** 로 휙 들어 올린다 (사장님 지시 2026-08-11)
        #   머리 중심 y=11, 반지름 6.6 → 정수리 y≈4.4. 카드(높이 13)의 아래끝이
        #   정수리보다 위에 오려면 손 y ≈ 2 여야 한다.
        if t < 0.8:
            y = 28.0                                   # 잠깐 대기
        elif t < 1.8:
            y = lerp(28.0, 2.0, ease((t - 0.8) / 1.0))  # ★1초 만에 휙
        else:
            y = 2.0                                     # 머리 위에서 유지
        # 팔은 위로 뻗는다 — 팔꿈치가 손보다 아래에 있어야 자연스럽다
        el = y + 9 if y < 20 else y - 1
        return dict(base, expr="happy",
                    pts=F.P(elbowLeft=(24.0, el), handLeft=(25.0, y),
                            elbowRight=(36.0, el), handRight=(35.0, y)),
                    card=dict(w=14, h=13, fan=1))

    if key == "card_fan":
        # ★카드는 **항상 정확히 3장**. 손 간격만 벌렸다 모은다
        if t < 1.5:
            s = 0.0
        elif t < 4.5:
            s = ease((t - 1.5) / 3.0)
        elif t < 6.0:
            s = lerp(1.0, 0.0, ease((t - 4.5) / 1.5))
        else:
            s = 0.0
        # ★부채를 **크게** 벌린다(사장님 지시 2026-08-11) — 손 간격 + 카드 간격 + 기울기
        arm = lerp(0.0, 7.0, s)                       # 손이 벌어지는 폭(단위)
        fanw = lerp(1.5, 5.2, s)                      # 카드끼리 벌어지는 정도
        tilt = lerp(0.0, 0.40, s)                     # 바깥장 기울기(라디안 ≈ 23°)
        wob = math.sin(t * 1.6) * 0.2 * s
        return dict(base, expr="happy",
                    pts=F.P(elbowLeft=(24.0 - arm * 0.45, 27),
                            handLeft=(22.0 - arm, 28 + wob),
                            elbowRight=(36.0 + arm * 0.45, 27),
                            handRight=(38.0 + arm, 28 - wob)),
                    card=dict(w=11, h=11, fan=3, spread=fanw, tilt=tilt))

    raise ValueError("모르는 클립: " + key)


def render(key):
    n = int(DUR * FPS)
    d = os.path.join(TMP, key)
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))

    from PIL import Image
    for i in range(n):
        t = i / FPS
        pose = pose_at(key, t)
        im = F.render_pose(pose, seed=7)                     # ★시드 고정 = 손떨림 일정
        a = im.convert("RGBA")

        # ★키는 **머리끝~발끝만** 잰다. 든 카드는 키에 넣지 않는다.
        #   (bbox 로 재면 카드를 올릴수록 사람이 작아진다 — 2026-08-11 실측 확인)
        pts = pose["pts"]
        hr = pose.get("hr", 7.5)
        head_top = F.OY + (pts["head"][1] - hr) * F.S
        foot_bot = F.OY + max(pts["feetLeft"][1], pts["feetRight"][1]) * F.S \
            + pose.get("lw", 1.55) * F.S * 0.5
        body_h = foot_bot - head_top
        s = FIG_H / body_h                                   # ★사람 키 기준 배율

        bbox = a.getbbox()                                   # 카드까지 포함한 실제 그림 범위
        a = a.crop(bbox)
        a = a.resize((max(1, round(a.width * s)), max(1, round(a.height * s))),
                     Image.LANCZOS)
        # ★배경 투명 · 몸은 검정 라인 그대로 (사장님 지시 2026-08-11)
        #   mp4 로 구우면 색이 번져 잉크가 회색이 되므로, **투명 PNG 도 같이** 남긴다.
        # 발끝이 항상 같은 바닥선에 오게 놓는다(키 통일의 짝)
        cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        floor = (H + FIG_H) // 2
        foot_in_crop = (foot_bot - bbox[1]) * s              # 잘라낸 그림 안에서 발끝 위치
        cv.paste(a, ((W - a.width) // 2, int(round(floor - foot_in_crop))), a)
        cv.save(os.path.join(d, "f%04d.png" % i))
        if i % 48 == 0:
            log("    %d/%d 프레임" % (i, n))

    # ★투명 프레임을 그대로 컷으로 남긴다 — mp4 를 거치면 잉크가 회색으로 번진다
    cd = os.path.join(ROOT, "W1_2", "cuts", key)
    os.makedirs(cd, exist_ok=True)
    for f in os.listdir(cd):
        os.remove(os.path.join(cd, f))
    step = max(1, n // 64)
    kept = 0
    for i in range(0, n, step):
        if kept >= 64:
            break
        Image.open(os.path.join(d, "f%04d.png" % i)).save(
            os.path.join(cd, "%s_%02d.png" % (key, kept)))
        kept += 1

    # 미리보기용 mp4 (흰 바탕에 얹어 굽는다 — 확인용일 뿐, 합성엔 위 컷을 쓴다)
    out = os.path.join(OUT, key + ".mp4")
    os.makedirs(OUT, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(d, "f%04d.png"),
                    "-filter_complex", "color=white:s=%dx%d[bg];[bg][0:v]overlay=shortest=1" % (W, H),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", out], check=True)
    log("  ✅ %s  %dKB · %d프레임 · %.1f초 · 투명컷 %d장"
        % (out, os.path.getsize(out) // 1024, n, DUR, kept))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    a = ap.parse_args()
    keys = a.keys or ["mouth_cycle", "card_lift", "card_fan"]
    for k in keys:
        log("\n[%s]" % k)
        render(k)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
