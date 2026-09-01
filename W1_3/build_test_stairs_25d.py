# -*- coding: utf-8 -*-
"""W1-3 S03-S04 계단씬(cheonggye_stairs) 2.5D 지면고정(ground-anchored) 테스트클립.

배경(cheonggye_stairs.mp4, 8초, 24fps, 1280x720)을 프레임 단위로 직접 열어
계단 단(트레드-라이저 접합부)의 실제 화면 좌표를 눈으로 짚어 측정했다
([[stage-horizon-measure-by-feet]] 원칙 — 자동 엣지검출은 돌 표면의 얼룩/균열을
오검출하므로 쓰지 않음).

핵심 발견: 이 배경은 카메라가 8초 내내 매끄럽게 전진 돌리하는 게 아니라,
  · t=0.5~3.0s (프레임 1~6): 정지된 대각선 구도 — 계단이 화면 왼쪽에서
    우하단으로 대각선으로 흐르고, 우측에 나무 늘어선 산책로가 보인다.
  · t=3.0~4.3s (프레임 7~9 부근): 급격한 전진돌리+틸트다운 재구도 —
    이 구간 추출 프레임은 모션블러/디졸브로 계단 경계가 실측 불가능하다.
  · t=4.4~8.0s (프레임 9~16): 정지된 정면(head-on) 구도로 정착 — 계단이
    화면 중앙 하단에 좌우대칭으로 위치, 그 위로 산책로가 다리 쪽으로
    멀어진다(f_013.png=6.5s 기준 실측, f_009/f_016로 앞뒤 정지 구간 확인).

따라서 좌표표는 "8초 전체에 걸친 linear interpolation" 이 아니라, 위 두 정지
구간마다 실측한 여러 개의 계단 단 좌표를 구간별 piecewise-linear로 잇고,
카메라가 재구도되며 실측이 불가능한 전환 구간(2.9~4.4s)은 캐릭터를
숨김(페이드) 처리해 "안 보이는 곳에서 미끄러지는" 상황 자체를 없앴다.

[2026-09-01 사장님 수정지시 반영]
  1. 구간 A(0.5~2.9s, 대각선 구도): 뒷모습(zgirl_walk_back) -> 정면
     (zgirl_walk_front, W1_2/motion6_stride_recolored/zgirl_walk_front/,
     compile_w1_3.py S03 "계단 정면 전환"과 동일 컷)으로 스프라이트만 교체.
     발 좌표(x, foot, t)는 기존 실측값을 그대로 재사용 — 대각선 계단을
     카메라 쪽으로(front) 내려오는 동선이라 방향 전환만으로 의미가 맞는다
     (전환 전에는 "뒤로 내려가며 커짐"이 어색했으나, 정면 사용시 "카메라
     쪽으로 다가오며 커짐"으로 자연스러워진다).
  2. 전환구간(2.9~4.4s) 페이드 은닉: 변경 없음(승인된 부분).
  3. 구간 C(4.4~7.9s, 정면 대칭 구도): zgirl_walk_back 유지, 방향 불변.
  4. 스케일(h) 곡선: 구간 C 말미(70px)까지 지나치게 작아지던 것을
     완화했다. 새 범위는 전체 A+C 통틀어 h∈[150,300](비율 2.0배)로,
     기존 h∈[70,340](비율 4.86배)보다 훨씬 완만하다. compile_w1_3.py의
     기존 S03/S04 스케일 관례(h 205~300대)에도 더 가깝게 맞췄다.
     완전 고정(scale=1.0 통일)은 아니고 원근감은 약하게 남겼다.

좌표표 산출 방법(보고용):
  1. `_frames_stairs_measure/f_001.png`~`f_016.png` (0.5s 간격 24fps 추출본,
     기존 세션에서 이미 추출됨 — 재추출 안 함) 를 그대로 읽어 각 시점 구도를
     직접 눈으로 비교(정지 구간 vs 전환 구간 판별).
  2. `grid20.py` 로 계단 영역만 20px 격자 + 100px 라벨을 얹어 크롭
     (스크래치패드에 저장) → 트레드(밝은 수평면)와 라이저(어두운 수직면)의
     경계선(계단코, nosing)을 육안으로 짚어 (x,y) 픽셀 좌표를 읽었다.
  3. 캐릭터 스케일(h, px)은 같은 지점의 라이저 높이(px) 및 배경 속
     보행자 실루엣 키(원경 f_013.png 기준 약 60~70px)를 대조해 정했다.
  4. 결과 좌표표는 `_preview/stairs_foot_coords.json` 에 저장.

사용법: python W1_3/build_test_stairs_25d.py
출력: W1_3/_preview/test_stairs_25d.mp4
"""
import os
import json

import numpy as np
from PIL import Image

from moviepy import VideoFileClip, VideoClip

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

W, H, FPS = 1280, 720, 24
BG_PATH = "W1_3/bg/cheonggye_stairs.mp4"
# 구간 A = 정면(카메라를 보며 내려옴), 구간 C = 후면(멀어짐) — 사장님 지시(2026-09-01)
CHAR_DIR_A = "W1_2/motion6_stride_recolored/zgirl_walk_front"
CHAR_FRAMES_A = 32        # zgirl_walk_front_00..31
CHAR_DIR_C = "W1_2/motion6_stride_recolored/zgirl_walk_back"
CHAR_FRAMES_C = 17        # zgirl_walk_back_00..16
CHAR_FPS = 12             # 기존 compile_w1_3.py S03 첫 비트와 동일 캐덴스
OUT_JSON = "W1_3/_preview/stairs_foot_coords.json"
OUT_MP4 = "W1_3/_preview/test_stairs_25d.mp4"

# ───────────────────────── 실측 좌표표 ─────────────────────────
# 각 항목: t(초), foot_x(발 중심 x), foot_y(발 바닥 y), h(캐릭터 렌더 키 px)
# f_001.png(대각선 구도, 0.5~3.0s 정지 확인) / f_013.png(정면 구도, 4.4~8.0s
# 정지 확인, f_009·f_016으로 앞뒤 프레임 동일 구도 교차검증) 실측값.
# x/foot/t는 원본 실측값 그대로 재사용(사장님 지시 1번 — 재측정 없이 그대로
# 써도 된다고 명시). h(스케일)만 완만한 원근 곡선으로 재조정(지시 4번).
PHASE_A = [  # 대각선 구도 — 화면 왼쪽 계단을 정면으로 우하단(카메라 쪽)으로
             # 걸어 내려옴. zgirl_walk_front 사용 — 카메라를 보며 다가옴.
    dict(t=0.5, x=100, foot=237, h=150),
    dict(t=1.1, x=150, foot=300, h=175),
    dict(t=1.7, x=180, foot=340, h=200),
    dict(t=2.3, x=230, foot=400, h=225),
    dict(t=2.9, x=280, foot=460, h=245),
]
PHASE_C = [  # 정면 구도 — 카메라가 따라붙어 가까이 나타난 뒤, 남은 계단을
             # 밟고 올라가는 화면(=실제로는 계속 내려가 산책로로 멀어짐)
             # zgirl_walk_back 유지 — 뒷모습으로 멀어짐(방향 불변).
    dict(t=4.4, x=640, foot=700, h=300),
    dict(t=5.1, x=640, foot=665, h=270),
    dict(t=5.8, x=640, foot=600, h=245),
    dict(t=6.5, x=640, foot=530, h=220),
    dict(t=7.2, x=640, foot=470, h=195),
    dict(t=8.0, x=640, foot=430, h=180),
]
FADE = 0.15  # 각 구간 시작/끝 페이드(초) — 전환구간 은닉을 자연스럽게

COORD_TABLE = {
    "background": BG_PATH,
    "character": "zolla_girl (w12_zgirl) — phase A: front walk "
                  "(zgirl_walk_front_00..31, W1_2/motion6_stride_recolored/zgirl_walk_front/), "
                  "phase C: back walk (zgirl_walk_back_00..16, "
                  "W1_2/motion6_stride_recolored/zgirl_walk_back/)",
    "frame_size": [W, H],
    "method": (
        "실제 배경 프레임(_frames_stairs_measure/f_001~f_016.png, 0.5s 간격)을 "
        "직접 열어 눈으로 비교 -> 카메라가 0.5~3.0s 대각선 정지, 3.0~4.3s 재구도"
        "(모션블러, 실측불가), 4.4~8.0s 정면 정지 3단계임을 확인. 정지 구간마다 "
        "grid20.py 로 20px 격자를 얹은 크롭에서 계단 트레드/라이저 경계선(계단코)"
        "을 육안으로 짚어 (x,y) px 좌표를 읽었다. [2026-09-01] h(캐릭터 렌더 키)는 "
        "사장님 지시로 완만한 원근 곡선으로 재조정(A+C 통틀어 h∈[150,300], 이전 "
        "h∈[70,340]보다 훨씬 완만함); x/foot 좌표는 원 실측값 그대로 재사용. "
        "재구도 구간은 실측이 불가능하므로 캐릭터를 페이드 은닉해 미끄러짐을 "
        "원천적으로 없앴다(이 처리 방식은 승인되어 변경하지 않음)."
    ),
    "phases": [
        {"name": "A_diagonal_view", "visible_t_range": [PHASE_A[0]["t"] - FADE, PHASE_A[-1]["t"] + FADE],
         "note": "배경 카메라 정지 구도(프레임 1~6, 0.5~3.0s 동일 구도 확인). "
                 "계단이 화면 좌측에서 우하단으로 대각선. [2026-09-01] 정면"
                 "(zgirl_walk_front)으로 카메라를 보며 계단을 내려옴 — 뒷모습에서 "
                 "정면으로 전환.",
         "character": "zgirl_walk_front",
         "keyframes": PHASE_A},
        {"name": "transition_hidden", "t_range": [PHASE_A[-1]["t"] + FADE, PHASE_C[0]["t"] - FADE],
         "note": "배경 카메라가 급격히 전진돌리+틸트다운 재구도. 이 구간 추출 "
                 "프레임(f_007~f_009 부근)에 모션블러/디졸브가 발생해 계단 경계를 "
                 "실측할 수 없어 캐릭터를 페이드아웃/숨김 처리. (변경 없음)"},
        {"name": "C_settled_view", "visible_t_range": [PHASE_C[0]["t"] - FADE, PHASE_C[-1]["t"] + FADE],
         "note": "배경 카메라 정지 구도(프레임 9~16, 4.4~8.0s 동일 구도 확인, "
                 "f_013.png=6.5s 기준 실측). 계단이 화면 중앙 하단, 위로 산책로가 "
                 "다리 쪽으로 멀어짐 — 캐릭터는 계단을 마저 내려가 산책로로 "
                 "멀어지는 방향(화면 아래->위, 커짐->작아짐)으로 이동. 뒷모습"
                 "(zgirl_walk_back) 방향은 변경하지 않음.",
         "character": "zgirl_walk_back",
         "keyframes": PHASE_C},
    ],
}


def save_coord_table():
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(COORD_TABLE, f, ensure_ascii=False, indent=2)
    print("[coords] 저장: %s" % OUT_JSON)


# ───────────────────────── 캐릭터 프레임 캐시 ─────────────────────────
_char_cache = {}


def load_char_frame(char_dir, frames, idx):
    idx = idx % frames
    key = (char_dir, idx)
    if key not in _char_cache:
        basename = os.path.basename(char_dir)  # e.g. zgirl_walk_front
        p = os.path.join(char_dir, "%s_%02d.png" % (basename, idx))
        _char_cache[key] = Image.open(p).convert("RGBA")
    return _char_cache[key]


def interp_keyframes(kfs, t):
    """kfs: [{t,x,foot,h}, ...] t오름차순. 구간별 piecewise-linear."""
    if t <= kfs[0]["t"]:
        k = kfs[0]
        return k["x"], k["foot"], k["h"]
    if t >= kfs[-1]["t"]:
        k = kfs[-1]
        return k["x"], k["foot"], k["h"]
    for i in range(len(kfs) - 1):
        a, b = kfs[i], kfs[i + 1]
        if a["t"] <= t <= b["t"]:
            u = 0.0 if b["t"] <= a["t"] else (t - a["t"]) / (b["t"] - a["t"])
            x = a["x"] + (b["x"] - a["x"]) * u
            foot = a["foot"] + (b["foot"] - a["foot"]) * u
            h = a["h"] + (b["h"] - a["h"]) * u
            return x, foot, h
    k = kfs[-1]
    return k["x"], k["foot"], k["h"]


def fade_alpha(t, t0, t1, fade):
    """t0~t1 구간 안에서 fade초 페이드인/아웃되는 0~1 배율."""
    if t < t0 or t > t1:
        return 0.0
    a = min(1.0, (t - t0) / max(1e-6, fade))
    b = min(1.0, (t1 - t) / max(1e-6, fade))
    return max(0.0, min(a, b))


def render_char_at(t, kfs, phase_t0, phase_t1, char_dir, frames):
    """phase_t0/t1 = 페이드 포함 가시구간. kfs[0]['t']/kfs[-1]['t'] = 실측구간."""
    alpha_mul = fade_alpha(t, phase_t0, phase_t1, FADE)
    if alpha_mul <= 0.0:
        return None
    x, foot, h = interp_keyframes(kfs, t)
    elapsed = max(0.0, t - phase_t0)
    idx = int(elapsed * CHAR_FPS) % frames
    im = load_char_frame(char_dir, frames, idx)
    scale = h / im.height
    w2, h2 = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    im2 = im.resize((w2, h2), Image.LANCZOS)
    if alpha_mul < 1.0:
        a = im2.getchannel("A").point(lambda v: int(v * alpha_mul))
        im2.putalpha(a)
    x0, y0 = int(x - w2 / 2), int(foot - h2)
    return im2, x0, y0


def build_clip():
    bg = VideoFileClip(BG_PATH)
    dur = bg.duration

    a_t0, a_t1 = PHASE_A[0]["t"] - FADE, PHASE_A[-1]["t"] + FADE
    c_t0, c_t1 = PHASE_C[0]["t"] - FADE, PHASE_C[-1]["t"] + FADE

    def make_frame(t):
        t = min(t, dur - 1.0 / FPS)
        bg_frame = bg.get_frame(t)
        base = Image.fromarray(bg_frame.astype(np.uint8)).convert("RGBA")
        if base.size != (W, H):
            base = base.resize((W, H), Image.LANCZOS)

        r = render_char_at(t, PHASE_A, a_t0, a_t1, CHAR_DIR_A, CHAR_FRAMES_A)
        if r is None:
            r = render_char_at(t, PHASE_C, c_t0, c_t1, CHAR_DIR_C, CHAR_FRAMES_C)
        if r is not None:
            im2, x0, y0 = r
            base.alpha_composite(im2, (x0, y0))

        return np.array(base.convert("RGB"))

    clip = VideoClip(make_frame, duration=dur).with_fps(FPS)
    if bg.audio is not None:
        clip = clip.with_audio(bg.audio)
    return clip


def main():
    save_coord_table()
    os.makedirs(os.path.dirname(OUT_MP4), exist_ok=True)
    clip = build_clip()
    clip.write_videofile(
        OUT_MP4, fps=FPS, codec="libx264", audio_codec="aac",
        ffmpeg_params=["-movflags", "+faststart"],
    )
    print("[done] %s" % OUT_MP4)


if __name__ == "__main__":
    main()
