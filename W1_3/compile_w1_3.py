# -*- coding: utf-8 -*-
"""W1-3 한국어 초안 컴파일러 — edge-tts 나레이션 + 배경 연속 저속재생 + 졸라걸
합성 + 파라메트릭 글자 오버레이 + 로고/장소 표기.

오늘 산출물: 한글판 초안 mp4 + 소프트 자막(.ko.srt, 별도 사이드카 — 번인 안 함).
Azure 최종본·4K·영어판은 다음 단계.

의존: `W1_3/gen_tts_ko.py` → `_audio_ko/*.mp3` , `W1_3/gen_srt_ko.py` → `timeline.json`
      (씬 실제 길이 = 나레이션 실측 + 0.35초 패딩, 두 산출물이 이 표를 공유한다)

좌표·동작 배정은 `W1_3_motion_v2.md` §2(좌표계)·§4(씬별 트랙)를 따르되, 실제 배경
정지 프레임을 직접 열어 눈으로 짚어 고른 값이다([[stage-horizon-measure-by-feet]]).
그림배경이라 진짜 카메라 원근은 아니므로 "실측"은 소실점 역산이 아니라 그 배경의
걸을 수 있는 땅 위 어디에 발을 놓을지 눈으로 정하는 것을 뜻한다.

사용법: python W1_3/compile_w1_3.py [--test S06]   (--test = 그 씬 하나만 렌더해 확인)
"""
import os
import re
import sys
import json
import sqlite3

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moviepy import VideoFileClip, VideoClip, AudioFileClip, concatenate_videoclips
import moviepy.video.fx as vfx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

W, H, FPS = 1280, 720, 24
DB = "channel/content.db"
FONT_PATH = r"C:\Windows\Fonts\malgun.ttf"
LOGO_PATH = "assets/drjay_ed_logo_circle.png"
PLACE_LABEL = "Cheonggyecheon, Seoul"
BG_DIR = "W1_3/bg"
OUT_MP4 = "W1_3/w1_3_ko_draft_v2.mp4"

# ───────────────────────── DB 포즈 인덱스 ─────────────────────────
_conn = sqlite3.connect(DB)
_cur = _conn.cursor()
_cur.execute("SELECT char_key,pose_name,file_path,flip FROM anim_char_poses "
             "WHERE char_key IN ('w12_zgirl','zolla_girl')")
POSE_DB = {}
for ck, pn, fp, flip in _cur.fetchall():
    POSE_DB[(ck, pn)] = (fp, flip)
_conn.close()

_FRAME_RE = re.compile(r"^(.*)_(\d{2,3})$")
_img_cache = {}


def load_pose_img(char_key, pose_name):
    key = (char_key, pose_name)
    if key in _img_cache:
        return _img_cache[key]
    if key not in POSE_DB:
        raise KeyError("포즈 없음: %s / %s" % key)
    fp, flip = POSE_DB[key]
    im = Image.open(os.path.join(ROOT, fp)).convert("RGBA")
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    _img_cache[key] = im
    return im


def frame_pose_name(base, idx):
    return "%s_%02d" % (base, idx)


# ───────────────────────── 씬 타임라인 ─────────────────────────
with open("W1_3/timeline.json", encoding="utf-8") as f:
    TIMELINE = json.load(f)
SCENE_TIME = {s["scene"]: s for s in TIMELINE["scenes"]}
SCENE_ORDER = [s["scene"] for s in TIMELINE["scenes"]]

BG_GROUPS = [
    ("cheonggye_entrance", ["S01", "S02"]),
    ("cheonggye_stairs", ["S03", "S04"]),
    ("cheonggye_stones", ["S05", "S06"]),
    ("cheonggye_stones_midstream", ["S07", "S08", "S09"]),
    ("cheonggye_underpass", ["S10", "S11"]),
    ("cheonggye_willow", ["S12", "S13", "S14"]),
    ("cheonggye_stones_downstream", ["S15", "S16"]),
    ("cheonggye_willow_bench", ["S17", "S18"]),
    ("cheonggye_mural", ["S19", "S20", "S21"]),
    ("cheonggye_bridge_dusk", ["S22", "S23"]),
]
SCENE_BG = {s: bg for bg, ss in BG_GROUPS for s in ss}

# ───────────────────────── 캐릭터 비트 (좌표는 §2 라벨 그대로,
#   foot_y·x 는 각 배경 정지 프레임을 직접 열어 눈으로 고른 값) ─────────────────────────
# beat: t0,t1 = 씬 길이에 대한 비율(0~1) · char_key,base · frames(None=정지 1장) ·
#       fps,loop · x0,x1 · foot0,foot1(발 y) · h0,h1(렌더 키 px, 이미 졸라걸 축척값)
ZG = "w12_zgirl"
ZW = "zolla_girl"


def B(t0, t1, ck, base, x0, foot0, h0, x1=None, foot1=None, h1=None,
      frames=None, fps=16, loop=True, fade=0.0, hold=True):
    # fade(초): 이 비트 시작/끝에서 알파 페이드(구도전환 은닉 구간 앞뒤용, [[stage-horizon-measure-by-feet]]).
    # hold: 이 비트가 씬의 마지막 비트일 때 t1 이후로도 마지막 프레임을 계속 보여줄지
    #       (False=안 보임 -> 씬 끝까지 숨김, 계단씬처럼 실측 불가 구간을 은닉할 때 사용).
    return dict(t0=t0, t1=t1, char_key=ck, base=base,
                x0=x0, x1=x0 if x1 is None else x1,
                foot0=foot0, foot1=foot0 if foot1 is None else foot1,
                h0=h0, h1=h0 if h1 is None else h1,
                frames=frames, fps=fps, loop=loop, fade=fade, hold=hold)


SCENES = {
    # ── cheonggye_entrance(2026-09-01 재실측): 8초 원본이 street-level 광장(0~2s)
    #   -> 재구도 전환(2~3.3s, 모션블러) -> 계단상단 랜딩(4~8s)으로 급변한다(entrance_t0~t4
    #   grid 프레임 실측). 랜딩부는 y<=260까지만 바닥이고 그 아래는 이미 계단 단이라
    #   구 버전의 foot=640(계단 중턱 허공)이 "날아다니는" 원인이었다 — foot=230으로 수정.
    "S01": [B(0.0, 0.62, ZG, "zgirl_run_front", 1000, 470, 180, 560, 560, 300,
              frames=14, fps=14, loop=True),
            B(0.62, 1.0, ZG, "zgirl_attention", 560, 560, 300, fade=0.5)],
    "S02": [B(0.13, 0.55, ZW, "explain", 640, 230, 260, fade=0.4),
            B(0.55, 1.0, ZG, "zgirl_card_hold", 640, 230, 260)],

    # ── cheonggye_stairs(2026-09-01, W1_3/_preview/stairs_foot_coords.json 그대로 반영):
    #   phase A(대각선, 정면으로 내려옴) t=0.5~2.9s / 전환(모션블러, 실측불가 -> 은닉)
    #   2.9~4.4s / phase C(정면대칭, 뒷모습으로 멀어짐) 4.4~8.0s. 8s원본 -> S03+S04
    #   합산길이(24.051s)로 3.00638배 늘어난 시각을 각 씬 비율로 환산했다.
    "S03": [B(0.128, 0.282, ZG, "zgirl_walk_front", 100, 237, 150, 150, 300, 175,
              frames=32, fps=12, loop=True, fade=0.3),
            B(0.282, 0.435, ZG, "zgirl_walk_front", 150, 300, 175, 180, 340, 200,
              frames=32, fps=12, loop=True),
            B(0.435, 0.589, ZG, "zgirl_walk_front", 180, 340, 200, 230, 400, 225,
              frames=32, fps=12, loop=True),
            B(0.589, 0.743, ZG, "zgirl_walk_front", 230, 400, 225, 280, 460, 245,
              frames=32, fps=12, loop=True, fade=0.3, hold=False)],
    # 0.743~1.0 = 전환구간 꼬리, 실측불가라 은닉(캐릭터 없음, 승인된 처리방식)
    "S04": [B(0.121, 0.292, ZG, "zgirl_walk_back", 640, 700, 300, 640, 665, 270,
              frames=17, fps=12, loop=True, fade=0.3),
            B(0.292, 0.463, ZG, "zgirl_walk_back", 640, 665, 270, 640, 600, 245,
              frames=17, fps=12, loop=True),
            B(0.463, 0.634, ZG, "zgirl_walk_back", 640, 600, 245, 640, 530, 220,
              frames=17, fps=12, loop=True),
            B(0.634, 0.805, ZG, "zgirl_walk_back", 640, 530, 220, 640, 470, 195,
              frames=17, fps=12, loop=True),
            B(0.805, 1.0, ZW, "point_right", 640, 470, 195)],
    # 0.0~0.121 = 전환구간 머리(은닉, 승인된 처리방식); 0.805~ = 정착해서 설명

    # ── cheonggye_stones(재실측): 좌안 스텝스톤 지대, y=480~650 밴드가 3장(00/mid/end)
    #   전구간에서 계속 돌/둔치로 남는다. 글자 오버레이(x=520~1050,y~150~350)를
    #   피해 캐릭터를 좌측(x<=650)에 배치.
    "S05": [B(0.0, 0.5, ZG, "zgirl_attention", 280, 560, 300),
            B(0.5, 1.0, ZW, "point_right", 280, 560, 300)],
    "S06": [B(0.0, 0.6, ZG, "zgirl_walk_side", 280, 560, 300, 650, 580, 310,
              frames=11, fps=10, loop=True),
            B(0.6, 1.0, ZG, "zgirl_high_five", 650, 580, 310,
              frames=64, fps=24, loop=False)],

    # ── cheonggye_stones_midstream(재실측): 계속 오른쪽으로 징검다리 건너기,
    #   y=520~600 밴드가 안전(버드나무 가지는 장식, 바닥과 무관).
    "S07": [B(0.0, 0.6, ZG, "zgirl_walk_side", 150, 520, 280, 500, 560, 300,
              frames=11, fps=10, loop=True),
            B(0.6, 1.0, ZG, "zgirl_high_five", 500, 560, 300,
              frames=64, fps=24, loop=False)],
    "S08": [B(0.0, 0.6, ZG, "zgirl_walk_side", 500, 560, 300, 850, 600, 320,
              frames=11, fps=10, loop=True),
            B(0.6, 1.0, ZG, "zgirl_high_five", 850, 600, 320,
              frames=64, fps=24, loop=False)],
    "S09": [B(0.0, 0.4, ZG, "zgirl_attention", 350, 580, 300),
            B(0.4, 1.0, ZG, "zgirl_card_hold", 350, 580, 300)],

    # ── cheonggye_underpass(재실측): 다리 밑 보행로 y=380~520 밴드, D1=205
    #   (원래 설계의도 유지 — 터널 원근이라 작게 보이는 게 자연스러움).
    "S10": [B(0.0, 0.55, ZG, "zgirl_attention", 640, 460, 205),
            B(0.55, 1.0, ZG, "zgirl_stumble_bounce", 640, 460, 205,
              frames=64, fps=24, loop=False)],
    "S11": [B(0.0, 0.35, ZG, "zgirl_walk_front", 750, 460, 190, 640, 470, 205,
              frames=32, fps=12, loop=True),
            B(0.35, 1.0, ZW, "sig_thinker", 640, 470, 205)],

    # ── cheonggye_willow: 물가 웅크림/좌식(자세별 키기준: 앉기60%/웅크림50%),
    #   산책로 바닥 y=420~720 전구간 안전, 유지.
    "S12": [B(0.0, 1.0, ZW, "sit_think", 640, 660, 196)],
    "S13": [B(0.0, 0.5, ZG, "zgirl_mirror", 550, 650, 196),
            B(0.5, 1.0, ZW, "sig_thinker", 150, 650, 196)],
    # 재확인: 이 배경은 씬 후반부로 갈수록 디딤돌이 좌측(x<380)으로 줄어든다
    # (S14와 동일 배경 뒷부분) -> 두번째 비트는 좌측으로 이동해 물에 안 잠기게.
    "S14": [B(0.0, 1.0, ZG, "zgirl_arms_wide", 480, 390, 270)],
    # 재확인: 이 구간(줌 후반)엔 둔치 산책로가 y=310~400 좁은 띠로 줄고 그 아래는
    # 전부 물 — foot=640(구버전)은 물에 잠긴 것처럼 보여 foot=390으로 낮춤.

    # ── cheonggye_stones_downstream(재실측): y=420~650 밴드 안전. "이유" 카드
    #   (cx=640,cy=350)와 안 겹치게 좌측으로 이동.
    "S15": [B(0.0, 1.0, ZG, "zgirl_block_touch", 500, 580, 300,
              frames=64, fps=20, loop=False)],
    "S16": [B(0.0, 0.35, ZG, "zgirl_block_touch", 380, 580, 300,
              frames=64, fps=24, loop=False),
            B(0.35, 0.7, ZG, "zgirl_hands_up", 380, 580, 300),
            B(0.7, 1.0, ZG, "zgirl_card_hold", 380, 580, 300)],

    # ── cheonggye_willow_bench(거의 고정구도, 재확인): 벤치 시트 y~460, 포장 y=520~700.
    #   "여유" 카드(640,350)와 안 겹치게 벤치 왼쪽으로 이동.
    "S17": [B(0.0, 0.6, ZG, "zgirl_block_touch", 350, 650, 391,
              frames=64, fps=24, loop=False),
            B(0.6, 1.0, ZG, "zgirl_high_five", 350, 650, 391,
              frames=64, fps=24, loop=False)],
    "S18": [B(0.0, 1.0, ZW, "sit_think", 680, 580, 235)],

    # ── cheonggye_mural(재실측, entrance급 재구도): 원본 0~2s는 벽에 극단적으로
    #   붙어있어(패닝 줌아웃) 화면 우측 하단 좁은 인도 조각만 바닥이다 —
    #   S19는 그 좁은 인도 위(우측)에서 시작해 조금씩 열리는 인도를 따라가고,
    #   S20/S21은 카메라가 빠지며 넓어진 인도로 옮겨간다.
    "S19": [B(0.3, 0.5, ZG, "zgirl_arms_wide", 1030, 610, 190, fade=0.3),
            B(0.5, 1.0, ZG, "zgirl_clap_together", 970, 630, 250,
              frames=64, fps=24, loop=False)],
    # 0.0~0.3 = 원본 0~0.9s에 해당(벽에 밀착된 줌, 인도가 화면에 없음) -> 은닉
    "S20": [B(0.0, 0.5, ZW, "explain", 780, 560, 300),
            B(0.5, 1.0, ZG, "zgirl_card_hold", 780, 560, 300)],
    "S21": [B(0.0, 0.4, ZG, "zgirl_arms_wide", 550, 560, 340),
            B(0.4, 0.7, ZW, "write_mid", 550, 560, 340),
            B(0.7, 1.0, ZW, "write_up", 550, 560, 340)],

    # ── cheonggye_bridge_dusk: 데크 y=400~720, 소실점 x~600,y~380 (재확인, 낮->노을
    #   색조 전환은 있으나 데크 구도 자체는 8초 내내 고정이라 그대로 유지).
    "S22": [B(0.0, 1.0, ZG, "zgirl_attention", 580, 600, 391)],
    "S23": [B(0.0, 1.0, ZG, "zgirl_run_back", 640, 600, 391, 900, 380, 40,
              frames=13, fps=12, loop=True)],
}

for _s in SCENE_ORDER:
    assert _s in SCENES, "씬 누락: %s" % _s

# ───────────────────────── 파라메트릭 글자 오버레이 (§7 간이 구현) ─────────────────────────
_FONT_CACHE = {}


def font(size):
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = ImageFont.truetype(FONT_PATH, size)
    return _FONT_CACHE[size]


WARM = (255, 140, 66, 255)      # 양성 모음 ㅏㅗㅐ
COOL = (108, 99, 255, 255)      # 음성 모음 ㅓㅜㅔㅡ
NEUTRAL = (255, 255, 255, 235)  # 중성 ㅣ
CONS = (74, 85, 104, 255)       # 자음/자리표시자 ㅇ
GOLD = (255, 215, 0, 255)
RED = (222, 60, 60, 255)
GREEN = (60, 190, 110, 255)
INK = (25, 25, 30, 255)

VOWEL_COLOR = {"ㅏ": WARM, "ㅗ": WARM, "ㅐ": WARM,
               "ㅓ": COOL, "ㅜ": COOL, "ㅔ": COOL, "ㅡ": COOL,
               "ㅣ": NEUTRAL}


def _center_text(draw, cx, cy, text, f, fill):
    b = draw.textbbox((0, 0), text, font=f)
    draw.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), text, font=f, fill=fill)


def box(draw, cx, cy, letter, w=76, h=76, state=None, dim=False):
    color = VOWEL_COLOR.get(letter, CONS)
    if dim:
        color = tuple(list(color[:3]) + [90])
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=color, outline=INK, width=3)
    _center_text(draw, cx, cy, letter, font(38), INK)
    if state == "snap":
        draw.rounded_rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 5], radius=14, outline=GOLD, width=5)
        draw.ellipse([x1 - 16, y0 - 16, x1 + 12, y0 + 12], outline=GREEN, width=5)
    elif state == "wrong":
        draw.rounded_rectangle([x0, y0, x1, y1], radius=12, outline=RED, width=6)
        draw.line([x0 + 8, y0 + 8, x1 - 8, y1 - 8], fill=RED, width=6)
        draw.line([x0 + 8, y1 - 8, x1 - 8, y0 + 8], fill=RED, width=6)


def card(draw, title, meaning, cx, cy):
    w, h = 300, 118
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=(255, 255, 255, 240), outline=INK, width=3)
    _center_text(draw, cx, cy - (16 if meaning else 0), title, font(44), INK)
    if meaning:
        _center_text(draw, cx, cy + 30, "뜻: " + meaning, font(24), (90, 90, 100, 255))


def row(draw, letters, cx, cy, gap=86, highlight_from=0):
    n = len(letters)
    x0 = cx - (n - 1) * gap / 2
    for i, ch in enumerate(letters):
        box(draw, x0 + i * gap, cy, ch, w=70, h=70, dim=(i >= highlight_from))


def swim_block(draw, letter, u0, u1, u, y=360):
    """u0~u1 구간 동안 오른쪽 D2 부근에서 화면 중앙으로 헤엄쳐 온다."""
    if u < u0:
        return
    p = min(1.0, (u - u0) / max(1e-6, u1 - u0))
    x = 1120 + (640 - 1120) * p
    s = 0.5 + 0.5 * p
    box(draw, x, y, letter, w=70 * s, h=70 * s)


def draw_text_overlay(scene_id, u, draw):
    if scene_id == "S04":
        if u > 0.25:
            box(draw, 700, 260, "ㅏ")
        if u > 0.8:
            box(draw, 610, 260, "ㅇ", state="snap")

    elif scene_id == "S05":
        _center_text(draw, 640, 150, "음절 상자", font(30), (255, 255, 255, 255))
        box(draw, 560, 250, "ㅇ")
        for i, ch in enumerate(["ㅏ", "ㅓ", "ㅣ", "ㅐ", "ㅔ"]):
            box(draw, 760 + i * 66, 220, ch, w=54, h=54, dim=(u < 0.5))
        for i, ch in enumerate(["ㅗ", "ㅜ", "ㅡ"]):
            box(draw, 620 + i * 66, 330, ch, w=54, h=54, dim=(u < 0.75))

    elif scene_id == "S06":
        box(draw, 560, 200, "아", state="snap" if u > 0.6 else None)
        box(draw, 636, 200, "이", state="snap" if u > 0.6 else None)

    elif scene_id == "S07":
        box(draw, 560, 200, "오", state="snap" if u > 0.6 else None)
        box(draw, 636, 200, "이", state="snap" if u > 0.6 else None)

    elif scene_id == "S08":
        box(draw, 560, 200, "아", state="snap" if u > 0.6 else None)
        box(draw, 636, 200, "우", state="snap" if u > 0.6 else None)

    elif scene_id == "S09":
        if u > 0.15:
            card(draw, "오", None, 900, 200)
        if u > 0.6:
            card(draw, "이", None, 1120, 200)

    elif scene_id == "S10":
        box(draw, 780, 220, "ㅗ", state="wrong" if u > 0.55 else None)

    elif scene_id == "S11":
        if 0.2 < u < 0.85:
            _center_text(draw, 640, 150, "강, 방…?", font(30), (200, 200, 210, 160))

    elif scene_id == "S12":
        n = min(4, int(u * 5) + 1)
        row(draw, ["아", "오", "우", "이"][:n], 640, 150)

    elif scene_id == "S13":
        row(draw, ["아", "오", "우", "이"], 500, 150)
        if u > 0.15:
            box(draw, 780, 150, "어", state=None)
            if 0.1 < u < 0.4:
                _center_text(draw, 780, 90, "어?", font(28), INK)
        if u > 0.6:
            box(draw, 856, 150, "으", state=None)
            if 0.55 < u < 0.85:
                _center_text(draw, 856, 90, "으차!", font(28), INK)

    elif scene_id == "S14":
        letters = ["아", "어", "오", "우", "으", "이", "애", "에"]
        n = 7 if u < 0.5 else 8
        row(draw, letters[:n], 640, 150, gap=76)

    elif scene_id == "S15":
        swim_block(draw, "유", 0.05, 0.85, u)

    elif scene_id == "S16":
        box(draw, 560, 210, "이", state="snap" if u > 0.35 else None)
        box(draw, 636, 210, "유", state="snap" if u > 0.35 else None)
        if u > 0.7:
            card(draw, "이유", "까닭", 640, 350)

    elif scene_id == "S17":
        box(draw, 560, 210, "여", state="snap" if u > 0.6 else None)
        box(draw, 636, 210, "유", state="snap" if u > 0.6 else None)
        if u > 0.75:
            card(draw, "여유", "느긋함", 640, 350)

    elif scene_id == "S19":
        box(draw, 460, 210, "우", state="snap" if u > 0.5 else None)
        box(draw, 820, 210, "애", state="snap" if u > 0.5 else None)
        if u > 0.6:
            card(draw, "우애", None, 640, 350)

    elif scene_id == "S20":
        if u > 0.3:
            _center_text(draw, 640, 150, "우애  ↔  아우", font(32), (255, 255, 255, 255))

    elif scene_id == "S21":
        row(draw, ["아", "어", "오", "우", "으", "이", "애", "에"], 640, 130, gap=64)
        if u > 0.3:
            card(draw, "이유", None, 380, 300)
        if u > 0.5:
            card(draw, "여유", None, 640, 300)
        if u > 0.7:
            card(draw, "우애", None, 900, 300)

    elif scene_id == "S22":
        _center_text(draw, 640, 620, "자음으로 시작 + ㅇ은 자리 · 세로=오른쪽 가로=아래",
                     font(26), (255, 255, 255, 255))


# ───────────────────────── 로고 · 장소 표기 ─────────────────────────
_logo_im = Image.open(LOGO_PATH).convert("RGBA").resize((48, 48), Image.LANCZOS)


def add_chrome(base):
    base.alpha_composite(_logo_im, (12, 12))
    d = ImageDraw.Draw(base)
    b = d.textbbox((0, 0), PLACE_LABEL, font=font(24))
    tw, th = b[2] - b[0], b[3] - b[1]
    pad = 10
    x1, y1 = W - 16, H - 14
    x0, y0 = x1 - tw - pad * 2, y1 - th - pad * 2
    d.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=(0, 0, 0, 120))
    d.text((x0 + pad - b[0], y0 + pad - b[1]), PLACE_LABEL, font=font(24), fill=(255, 255, 255, 235))
    return base


# ───────────────────────── 캐릭터 비트 렌더 ─────────────────────────
def render_char_beat(beat, t_scene):
    t0 = beat["t0_abs"]
    t1 = beat["t1_abs"]
    u = 0.0 if t1 <= t0 else min(1.0, max(0.0, (t_scene - t0) / (t1 - t0)))
    x = beat["x0"] + (beat["x1"] - beat["x0"]) * u
    foot = beat["foot0"] + (beat["foot1"] - beat["foot0"]) * u
    h = beat["h0"] + (beat["h1"] - beat["h0"]) * u

    if beat["frames"]:
        elapsed = max(0.0, t_scene - t0)
        idx = int(elapsed * beat["fps"])
        idx = idx % beat["frames"] if beat["loop"] else min(idx, beat["frames"] - 1)
        pose_name = frame_pose_name(beat["base"], idx)
    else:
        pose_name = beat["base"]

    im = load_pose_img(beat["char_key"], pose_name)
    scale = h / im.height
    w2, h2 = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    im2 = im.resize((w2, h2), Image.LANCZOS)

    fade = beat.get("fade", 0.0)
    if fade > 0:
        a_in = min(1.0, max(0.0, (t_scene - t0) / fade))
        a_out = 1.0 if t_scene >= t1 else min(1.0, max(0.0, (t1 - t_scene) / fade))
        mul = min(a_in, a_out)
        if mul < 1.0:
            a = im2.getchannel("A").point(lambda v: int(v * mul))
            im2.putalpha(a)

    return im2, int(x - w2 / 2), int(foot - h2)


# ───────────────────────── 씬 클립 조립 ─────────────────────────
def build_scene_clip(scene_id, bg_sub):
    st = SCENE_TIME[scene_id]
    dur = st["len"]
    beats = [dict(b, t0_abs=b["t0"] * dur, t1_abs=b["t1"] * dur) for b in SCENES[scene_id]]

    def make_frame(t):
        t = min(t, dur - 1.0 / FPS)
        bg_frame = bg_sub.get_frame(t)
        base = Image.fromarray(bg_frame.astype(np.uint8)).convert("RGBA")
        if base.size != (W, H):
            base = base.resize((W, H), Image.LANCZOS)

        for b in beats:
            if b["t0_abs"] <= t < b["t1_abs"] or \
                    (b is beats[-1] and b.get("hold", True) and t >= b["t1_abs"]):
                im2, x0, y0 = render_char_beat(b, t)
                base.alpha_composite(im2, (x0, y0))

        text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_text_overlay(scene_id, min(1.0, t / dur), ImageDraw.Draw(text_layer))
        base.alpha_composite(text_layer)
        add_chrome(base)
        return np.array(base.convert("RGB"))

    clip = VideoClip(make_frame, duration=dur).with_fps(FPS)
    audio_path = st["audio"]
    if os.path.exists(audio_path):
        clip = clip.with_audio(AudioFileClip(audio_path))
    return clip


def build_bg_subclips():
    """배경 그룹별로 한 번만 늘려(연속 저속) 씬 경계에서 되감기 없이 잘라 쓴다."""
    subs = {}
    for bg_key, scenes in BG_GROUPS:
        total = sum(SCENE_TIME[s]["len"] for s in scenes)
        path = os.path.join(BG_DIR, bg_key + ".mp4")
        base_clip = VideoFileClip(path).without_audio()
        stretched = base_clip.with_effects([vfx.MultiplySpeed(final_duration=total)])
        t = 0.0
        for s in scenes:
            d = SCENE_TIME[s]["len"]
            subs[s] = stretched.subclipped(t, min(total, t + d))
            t += d
        print("[bg] %-28s 원본8s -> %.2fs (%.2fx)  씬 %s" %
              (bg_key, total, total / 8.0, ",".join(scenes)))
    return subs


def main():
    test_scene = None
    if "--test" in sys.argv:
        test_scene = sys.argv[sys.argv.index("--test") + 1]

    bg_subs = build_bg_subclips()

    if test_scene:
        clip = build_scene_clip(test_scene, bg_subs[test_scene])
        out = "W1_3/_preview/test_%s.mp4" % test_scene
        clip.write_videofile(out, fps=FPS, codec="libx264", audio_codec="aac",
                              preset="medium", logger="bar")
        print("TEST ->", out)
        return

    clips = []
    for s in SCENE_ORDER:
        print("== %s (%.2fs) ==" % (s, SCENE_TIME[s]["len"]))
        clips.append(build_scene_clip(s, bg_subs[s]))

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(OUT_MP4, fps=FPS, codec="libx264", audio_codec="aac",
                           preset="medium", bitrate="6M", logger="bar")
    print("\n완성 ->", OUT_MP4)
    print("총 러닝타임 =", final.duration)


if __name__ == "__main__":
    main()
