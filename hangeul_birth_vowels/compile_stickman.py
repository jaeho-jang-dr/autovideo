#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
compile_stickman.py — KO-W01 "한글의 탄생과 단모음" 스틱맨 영상 렌더러 (DB 중심).

content.db 의 scenes + scene_objects 를 읽어 크림 배경 플랫 레이어드로 합성한다.
 - 포즈/객체/글자 = z_order 순으로 cx,cy,scale 배치 (+ 포즈 발밑 소프트 그림자).
 - 자막: 상단 캡션(cap) + 하단 내레이션(script). 폰트 malgun.ttf 하드코딩.
 - 모션: fade_in / elastic_pop / float / swing / arc / unfurl (프레임별).
 - 내레이션: gTTS/edge-tts 여성, 1.1배속. 캐시. KR/EN 두 버전.

사용:
  python hangeul_birth_vowels/compile_stickman.py --preview      # 정적 프리뷰 시트
  python hangeul_birth_vowels/compile_stickman.py --lang ko      # KR 영상
  python hangeul_birth_vowels/compile_stickman.py --lang en      # EN 영상
"""
import os
import sys
import json
import math
import argparse
import sqlite3
import re as _re

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root on path
from hangeul_strokes import render_vowel, STROKES

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
PDIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")
EP = "KO-W01"                       # overridden by --episode
OUT_PREFIX = "hangeul_w1_stickman"  # overridden by --prefix
PROJECT_NAME = "hangeul_w1_stickman"
W, H = 1280, 720
FPS = 24
CREAM = (245, 245, 240)
INK = (40, 40, 40)
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_BD = "C:/Windows/Fonts/malgunbd.ttf"
if not os.path.exists(FONT_BD):
    FONT_BD = FONT
TTS_DIR = os.path.join(PDIR, "tts_cache")
os.makedirs(TTS_DIR, exist_ok=True)
JAMO_DIR = os.path.join(ROOT, "web", "public", "audio", "jamo")   # SunHi 모음 발음 클립

# 끝에 따로 소리를 붙이지 않는다 — 발음은 나레이션 텍스트 안에서 처리(tts_text).
SCENE_SOUNDS = {}
SOUND_GAP = 0.5

# DB 발음 클립(낱자/단어 SunHi)을 나레이션 TTS보다 **약간 크게** — 학습 포인트(소리) 강조(사용자 표준).
# ensure_scene_audio 의 concat 필터에서 DB 클립 세그먼트에만 volume 적용. 변경 시 오디오 캐시 자동 무효화(해시 포함).
CLIP_GAIN = 1.4   # ≈ +2.9 dB

# 나레이션 TTS 전처리: 문장 속 낱자('ㅏ' 등)를 edge-tts가 건너뛰므로 발음되는 음절/이름으로 치환.
# (자막은 원문 낱자 그대로 표시, 오디오만 치환)
JAMO_SPEAK = {
    "ㅏ": "아", "ㅐ": "애", "ㅑ": "야", "ㅒ": "얘", "ㅓ": "어", "ㅔ": "에",
    "ㅕ": "여", "ㅖ": "예", "ㅗ": "오", "ㅘ": "와", "ㅙ": "왜", "ㅚ": "외",
    "ㅛ": "요", "ㅜ": "우", "ㅝ": "워", "ㅞ": "웨", "ㅟ": "위", "ㅠ": "유",
    "ㅡ": "으", "ㅢ": "의", "ㅣ": "이",
    "ㄱ": "기역", "ㄴ": "니은", "ㄷ": "디귿", "ㄹ": "리을", "ㅁ": "미음",
    "ㅂ": "비읍", "ㅅ": "시옷", "ㅇ": "이응", "ㅈ": "지읒", "ㅊ": "치읓",
    "ㅋ": "키읔", "ㅌ": "티읕", "ㅍ": "피읖", "ㅎ": "히읗",
    "ㄲ": "쌍기역", "ㄸ": "쌍디귿", "ㅃ": "쌍비읍", "ㅆ": "쌍시옷", "ㅉ": "쌍지읒",
}


def tts_text(s):
    """문장 속 단독 낱자를 발음형으로 치환 (TTS 입력용)."""
    return "".join(JAMO_SPEAK.get(ch, ch) for ch in s)


# 따옴표로 감싼 자음 소리·단어 → DB 클립(web/public/audio/jamo/<inner>.mp3) 삽입.
# (단어 내부 음절 오삽입 방지 위해 반드시 따옴표 포함 토큰으로 매칭)
CLIP_QUOTED = {"'그'": "그", "'느'": "느", "'므'": "므", "'스'": "스", "'응'": "응",
               "'누나'": "누나", "'오빠'": "오빠"}
# W3 거센/된소리: 따옴표 친 낱자(소리)·단어 → DB 발음 클립(web/public/audio/jamo/<inner>.mp3).
# 낱자는 글자(jamo) 파일명에 '소리'(그/크/끄…)가 담겨 있어, letter_<jamo> 맥동과도 동기화됨.
for _j in "ㄱㄴㄷㄹㅁㅂㅇㅈㅅㅋㅌㅍㅊㅎㄲㄸㅃㅆㅉ":
    CLIP_QUOTED[f"'{_j}'"] = _j
# W5 이중모음 낱자(소리) — jamo 클립 존재. 따옴표로 감싸 DB 클립 삽입(+부스트)
for _j in "ㅏㅓㅗㅜㅣㅐㅔㅡㅑㅕㅛㅠㅘㅝㅟㅚㅢㅒㅖ":
    CLIP_QUOTED[f"'{_j}'"] = _j
for _w in ["코", "타조", "포도", "치마", "까치", "꼬리", "땅", "빵", "개", "캐", "깨", "자", "차", "짜",
           "강", "책", "산", "옷", "물", "곰", "밥", "부엌", "꽃", "앞",                  # W4 받침 예시
           "야구", "여우", "요리", "우유", "얘기", "예의", "사과", "샤워", "외투", "가위", "의자",  # W5 이중모음 예시
           "음악", "으막", "옷이", "오시", "꽃이", "꼬치", "책을", "채글", "한국어", "한구거",
           "좋아요", "조아요", "웃어요", "우서요", "있어요", "이써요",                          # W6 연음 표기/발음
           "안녕하세요", "감사합니다", "반갑습니다", "안녕히 가세요", "안녕히 계세요",
           "저는", "입니다", "민수", "미국", "사람입니다", "학생",                              # W7 인사말·자기소개
           "하나", "둘", "셋", "넷", "다섯", "여섯", "일곱", "여덟", "아홉", "열",
           "일", "이", "삼", "사", "오", "육", "칠", "팔", "구", "십",
           "월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일", "분", "세", "삼십",  # W8 숫자·날짜·시간
           "앞", "뒤", "옆", "위", "밑", "마트", "학교",                                              # 중급1 위치
           "얼마예요", "이거 주세요", "결제", "할인",                                                 # 중급2 상점
           "주문할게요", "맛있어요", "매워요", "달아요",                                               # 중급3 식당
           "버스", "지하철", "타다", "환승",                                                         # 중급4 교통
           "오른쪽", "왼쪽", "똑바로 가다", "건너다",                                                 # 중급5 길찾기
           "일어나다", "공부하다", "일하다", "자다",                                                  # 중급6 일과
           "맑음", "비", "눈", "춥다", "덥다", "사계절",                                             # 중급7 날씨
           "영화 감상", "운동", "자주", "가끔", "좋아하다",                                            # 중급8 취미·빈도
           "반말", "축약어", "케이팝", "케이드라마", "기쁘다", "슬프다", "긴장되다", "속상하다",       # 고급1·2
           "생각해요", "왜냐하면", "따라서", "분실", "고장", "예약 변경", "긴급",                       # 고급3·4
           "외모", "성격", "내향적", "외향적", "가 본 적이 있어요", "여행", "계획",                     # 고급5·6
           "약속을 잡다", "시간 조율", "모임", "수료", "발표", "최종 평가"]:                            # 고급7·8
    CLIP_QUOTED[f"'{_w}'"] = _w

# ★ 발음 클립 폴더(web/public/audio/jamo)의 모든 mp3를 자동 등록 → 따옴표 친 한글은 무조건 선희 DB 클립.
try:
    for _f in os.listdir(JAMO_DIR):
        if _f.endswith(".mp3"):
            CLIP_QUOTED.setdefault(f"'{_f[:-4]}'", _f[:-4])
except Exception:
    pass


# 배경: 중앙 밝게 → 바깥 아주 옅은 파스텔 (약한 방사형 그라데이션). 1회 생성 후 캐시.
_BG = None
def make_bg():
    global _BG
    if _BG is not None:
        return _BG
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = (xx - W / 2) / (W / 2)
    dy = (yy - H / 2) / (H / 2)
    r = np.clip(np.sqrt(dx * dx + dy * dy) / 1.32, 0.0, 1.0)
    t = (r ** 1.5)[..., None]               # 중앙은 오래 밝게 유지
    center = np.array([252, 251, 247], np.float32)   # 밝은 따뜻한 화이트
    edge = np.array([233, 227, 238], np.float32)     # 아주 옅은 라벤더-핑크 파스텔
    img = center * (1 - t) + edge * t
    _BG = Image.fromarray(img.astype(np.uint8), "RGB").convert("RGBA")
    return _BG


# Flow 풍경 배경(씬별) — cover-fit + 흰 베일(투명도)로 전경 가독성↑. 없으면 절차적 파스텔.
BG_DIR = os.path.join(ROOT, "assets", "graphics", "bg")
BG_VEIL = 0.26
_SCENEBG = {}
def scene_bg(scene):
    key = scene.get("bg")
    if not key:
        return make_bg().copy()
    if key in _SCENEBG:
        return _SCENEBG[key].copy()
    p = os.path.join(BG_DIR, f"{key}.png")
    if os.path.exists(p):
        im = Image.open(p).convert("RGB")
        s = max(W / im.width, H / im.height)
        nw, nh = int(im.width * s + 0.5), int(im.height * s + 0.5)
        im = im.resize((nw, nh), Image.LANCZOS).crop(
            ((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
        base = im.convert("RGBA")
        base.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * BG_VEIL))))
        # 하단 소프트 그라데이션 스크림(자막 가독성 — 박스 대신) : 아래로 갈수록 살짝 어둡게
        scr = np.zeros((H, W, 4), np.uint8)
        yy = np.linspace(0, 1, H)[:, None]
        a = (np.clip((yy - 0.62) / 0.38, 0, 1) ** 1.4 * 90).astype(np.uint8)
        scr[..., 3] = np.broadcast_to(a, (H, W))
        base.alpha_composite(Image.fromarray(scr, "RGBA"))
    else:
        base = make_bg().copy()
    _SCENEBG[key] = base.copy()
    return base


def resolve_path(fp):
    for cand in (os.path.join(ROOT, fp), os.path.join(ROOT, "assets", fp), fp):
        if os.path.exists(cand):
            return cand
    return None


# ---------- data ----------
def load_scenes(lang="ko"):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    scenes = []
    for s in con.execute("SELECT * FROM scenes WHERE episode=? ORDER BY seq", (EP,)):
        spec = json.loads(s["image_prompt"])
        objs = []
        for o in con.execute(
            "SELECT a.file_path fp, o.cx, o.cy, o.scale, o.z_order, o.is_point, o.motion_type "
            "FROM scene_objects o JOIN assets a ON a.id=o.asset_id "
            "WHERE o.episode=? AND o.scene_seq=? ORDER BY o.z_order", (EP, s["seq"])):
            p = resolve_path(o["fp"])
            if p:
                objs.append(dict(path=p, cx=o["cx"], cy=o["cy"], scale=o["scale"],
                                 z=o["z_order"], is_point=o["is_point"], motion=o["motion_type"]))
        # 제스처 시퀀스(포즈 이름 리스트) → 실제 포즈 PNG 경로로 해석
        gpaths = []
        for nm in (spec.get("gesture_seq") or []):
            gp = resolve_path(f"assets/graphics/poses/stickman_{nm}.png")
            if gp:
                gpaths.append(gp)
        _script = s["script_kr"] if lang == "ko" else s["script_en"]
        scenes.append(dict(
            seq=s["seq"], dur=s["duration_sec"],
            script=_script, chunks=split_chunks(_script),
            cap=spec["cap_ko"] if lang == "ko" else spec["cap_en"],
            scene_motion=spec.get("motion", "static"), gestures=gpaths, bg=spec.get("bg"),
            place_en=spec.get("place_en", ""),
            cam=spec.get("cam") or CAM_MODES[(s["seq"] - 1) % len(CAM_MODES)], objs=objs))
    con.close()
    return scenes


# ---------- caching of asset images / fonts ----------
_CACHE = {}
def load_img(path):
    if path not in _CACHE:
        _CACHE[path] = Image.open(path).convert("RGBA")
    return _CACHE[path]


_FONTS = {}
def get_font(path, size):
    k = (path, size)
    if k not in _FONTS:
        _FONTS[k] = ImageFont.truetype(path, size)
    return _FONTS[k]


_TILE = {}
_VDONE = {}
_SHADOW = {}    # 캐릭터 바닥 그림자(블러) 캐시 — (cx,cy,scale)별 1회만 계산
def get_tile(im, w, h, rot, alpha):
    k = (id(im), w, h, round(rot, 1), round(alpha, 2))
    t = _TILE.get(k)
    if t is None:
        t = im.resize((w, h), Image.LANCZOS)
        if rot:
            t = t.rotate(rot, resample=Image.BICUBIC, expand=True)
        if alpha < 1.0:
            t = t.copy()
            t.putalpha(t.split()[3].point(lambda v: int(v * alpha)))
        if len(_TILE) < 1200:
            _TILE[k] = t
    return t


# ---------- motion ----------
def elastic(p):
    if p <= 0:
        return 0.0
    if p >= 1:
        return 1.0
    return 1.0 - math.exp(-7 * p) * math.cos(2 * math.pi * p)


def obj_state(o, t, dur):
    """return (scale_mult, dx, dy, rot, alpha) for motion at time t.
    깔끔 모드: 진동(float/swing) 제거, 팝은 오버슈트 없는 부드러운 등장만."""
    sm, dx, dy, rot, a = 1.0, 0.0, 0.0, 0.0, 1.0
    m = o["motion"]
    if m == "fade_in":
        a = min(1.0, t / 0.4)
    elif m == "elastic_pop":
        d = 0.4
        sm = 0.72 + 0.28 * _smooth(min(1.0, t / d))   # 흔들림(오버슈트) 없는 깔끔 팝
        a = min(1.0, t / 0.25)
    elif m == "float":
        a = min(1.0, t / 0.5)                          # 위아래 진동 제거 — 페이드만
    elif m == "swing":
        a = min(1.0, t / 0.4)                          # 좌우 회전 진동 제거 — 페이드만
    elif m == "arc":
        # rise from right then settle (sun east->west feel)
        p = min(1.0, t / 1.6)
        dx = (1 - p) * 120
        dy = -math.sin(p * math.pi) * 60
        a = min(1.0, t / 0.3)
    elif m == "unfurl":
        p = _smooth(min(1.0, t / 0.8))
        sm = 0.2 + 0.8 * p
        a = min(1.0, t / 0.3)
    elif m == "gesture":
        a = min(1.0, t / 0.35)               # 캐릭터 등장 페이드 (제스처는 아래 gesture_layers에서)
    return sm, dx, dy, rot, a


# ---------- 캐릭터 '살아있는' 모션 (사람이 설명하는 느낌) ----------
def idle_motion(cx, t):
    """캐릭터 흔들림 제거(사용자 요청: 흔들흔들 금지). 호흡/좌우 갸웃 없이 완전 정지."""
    return 0.0, 0.0, 1.0


GESTURE_HOLD = 3.2      # 한 제스처 유지 시간(초) — 느긋하게(차분한 손짓)
GESTURE_XF = 0.14       # 제스처 전환 크로스페이드(초)


def gesture_layers(paths, t):
    """씬 동안 여러 포즈를 번갈아 → 손짓하며 설명하는 느낌.
    반환: ([(path, alpha), ...], pop_scale). 전환 순간 짧은 크로스페이드+팝."""
    n = len(paths)
    if n <= 1:
        return ([(paths[0], 1.0)] if paths else []), 1.0
    idx = int(t / GESTURE_HOLD)
    ls = t - idx * GESTURE_HOLD                                 # 현재 제스처 시작 이후 경과
    cur = paths[idx % n]
    pop = 1.0                                                  # 스쿼시 제거 — 흔들림 없는 차분한 전환
    if ls < GESTURE_XF and idx > 0:                            # 직전 포즈와 빠른 크로스페이드
        prev = paths[(idx - 1) % n]
        p = ls / GESTURE_XF
        return [(prev, 1.0 - p), (cur, p)], pop
    return [(cur, 1.0)], pop


# ---------- 지미집(크레인) 카메라 — 부드러운 푸시인/풀백/팬 (전체 흔들기 아님, 천천히 이징) ----------
CAM_MODES = ["in", "left", "out", "right"]


def _smooth(p):
    p = max(0.0, min(1.0, p))
    return p * p * (3 - 2 * p)                                  # smoothstep 이징


def apply_camera(img, t, dur, mode):
    """카메라 무빙 비활성(사용자 요청: 깔끔/흔들림 금지). 전체 프레임을 정지로 유지."""
    return img
    if not mode or mode == "still":
        return img
    p = _smooth(t / max(0.01, dur))
    Z, PAN = 0.085, 48.0
    z, ox, oy = 1.0 + Z * 0.5, 0.0, 0.0
    if mode == "in":
        z = 1.0 + Z * p
    elif mode == "out":
        z = 1.0 + Z * (1.0 - p)
    elif mode == "left":
        ox = PAN * (0.5 - p) * 2.0                              # 왼→오 팬
    elif mode == "right":
        ox = -PAN * (0.5 - p) * 2.0
    cw, ch = W / z, H / z
    cx, cy = W / 2 + ox, H / 2 + oy
    x0 = max(0.0, min(W - cw, cx - cw / 2))
    y0 = max(0.0, min(H - ch, cy - ch / 2))
    crop = img.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch)))
    return crop.resize((W, H), Image.BILINEAR)


# ---------- compose ----------
def paste(base, im, cx, cy, scale, rot=0.0, alpha=1.0):
    w = max(1, int(im.width * scale))
    h = max(1, int(im.height * scale))
    t = get_tile(im, w, h, rot, alpha)
    base.alpha_composite(t, (int(cx - t.width / 2), int(cy - t.height / 2)))


def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(" "), [], ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if draw.textlength(test, font=font) <= maxw:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_caption(base, cap):
    if not cap:
        return
    d = ImageDraw.Draw(base)
    f = get_font(FONT_BD, 44)
    tw = d.textlength(cap, font=f)
    x, y = (W - tw) / 2, 38
    pad = 22
    d.rounded_rectangle([x - pad, y - 10, x + tw + pad, y + 56], radius=26, fill=(255, 255, 255, 180))
    d.text((x, y), cap, font=f, fill=(30, 30, 30))


# 좌상단 로고(아주 작게) + 우하단 배경 장소 영문명(나중에 찾아가기용)
LOGO_PATH = os.path.join(ROOT, "web", "public", "logo.png")
_LOGO = None
def draw_logo(base):
    global _LOGO
    if _LOGO is None:
        if os.path.exists(LOGO_PATH):
            lg = Image.open(LOGO_PATH).convert("RGBA")
            lw = 30                                   # 절반 크기(사용자 요청)
            lg = lg.resize((lw, max(1, int(lg.height * lw / lg.width))), Image.LANCZOS)
            lg.putalpha(lg.split()[3].point(lambda v: int(v * 0.92)))
            _LOGO = lg
        else:
            _LOGO = False
    if _LOGO:
        base.alpha_composite(_LOGO, (18, 14))


def draw_place(base, place):
    if not place:
        return
    d = ImageDraw.Draw(base)
    f = get_font(FONT, 14)                            # 절반 크기(사용자 요청)
    tw = d.textlength(place, font=f)
    d.text((W - tw - 16, H - 24), place, font=f, fill=(255, 255, 255),
           stroke_width=2, stroke_fill=(28, 24, 18))


def draw_subtitle(base, text):
    """자막 박스 없이 — 흰 글자 + 짙은 외곽선(스트로크)으로 어떤 배경에서도 또렷(하단 스크림과 함께)."""
    if not text:
        return
    d = ImageDraw.Draw(base)
    f = get_font(FONT_BD, 37)
    lines = wrap(d, text, f, W - 150)
    lh = 50
    by = H - lh * len(lines) - 30
    for ln in lines:
        tw = d.textlength(ln, font=f)
        x = (W - tw) / 2
        d.text((x, by), ln, font=f, fill=(255, 255, 255), stroke_width=5, stroke_fill=(24, 20, 16))
        by += lh


# ---------- 자막 청크: 긴 나레이션을 문장 단위 2줄 이하로 쪼개 시간순 표시 ----------
_SENT = _re.compile(r"[^.!?]*[.!?]+|\S[^.!?]*$")


def split_chunks(script, max_chars=50):
    """문장 경계로 나누고, 긴 문장은 쉼표로, 짧은 건 합쳐 각 청크 ≤ max_chars(≈2줄)."""
    script = (script or "").strip()
    if not script:
        return [""]
    sents = [m.group().strip() for m in _SENT.finditer(script) if m.group().strip()]
    units = []
    for s in sents:
        if len(s) <= max_chars:
            units.append(s)
        else:
            buf = ""
            for piece in _re.split(r"(?<=,)\s*", s):
                if buf and len(buf) + len(piece) + 1 > max_chars:
                    units.append(buf.strip()); buf = piece
                else:
                    buf = (buf + " " + piece).strip()
            if buf:
                units.append(buf.strip())
    chunks, cur = [], ""
    for u in units:
        if cur and len(cur) + len(u) + 1 > max_chars:
            chunks.append(cur); cur = u
        else:
            cur = (cur + " " + u).strip()
    if cur:
        chunks.append(cur)
    return chunks or [script]


def subtitle_text(scene, tt, final):
    """현재 시각 tt 에 보여줄 자막 청크. sub_sched=[(chunk_idx, t0, t1)]."""
    chunks = scene.get("chunks")
    if not chunks:
        return scene.get("script", "")
    if final or not scene.get("sub_sched") or len(chunks) == 1:
        return chunks[0]
    sched = scene["sub_sched"]
    for (i, t0, t1) in sched:
        if t0 <= tt < t1:
            return chunks[i]
    return chunks[-1] if tt >= sched[-1][2] else chunks[0]


def compose(scene, t=None, lang="ko", overlay=True):
    """t=None -> static final frame (preview). else animated frame at time t.
    overlay=False -> 자막/캡션 생략(카메라 무빙 뒤에 따로 얹기 위함)."""
    base = scene_bg(scene)
    dur = scene["dur"]
    final = t is None
    tt = dur if final else t
    sched = scene.get("sound_sched") or []
    gestures = scene.get("gestures")
    for o in sorted(scene["objs"], key=lambda x: x["z"]):
        base_name = os.path.splitext(os.path.basename(o["path"]))[0]
        jamo = base_name.replace("letter_", "") if base_name.startswith("letter_") else None
        # 발음되는 순간 해당 글자 살짝 커짐(맥동) — 소리·글자 동기화로 익히기 도움
        pulse = 1.0
        if jamo and not final and sched:
            for (sv, t0, t1) in sched:
                if sv == jamo and t0 <= tt <= t1:
                    pulse = 1.0 + 0.12 * math.sin(math.pi * (tt - t0) / max(0.01, t1 - t0))
                    break
        # 정획순 쓰기: 모음 글자를 한 획씩 (한글교육 — 획순 정확)
        if o["motion"] == "write":
            vch = jamo
            if vch in STROKES:
                prog = 1.0 if final else max(0.0, min(1.0, (tt - 0.3) / 1.3))
                if prog > 0.0:
                    size_px = max(8, int(234 * o["scale"] * pulse))
                    if prog >= 1.0:                       # cache completed glyph
                        ck = (vch, size_px, o["cx"])
                        vim = _VDONE.get(ck)
                        if vim is None:
                            vim = render_vowel(vch, size_px, progress=1.0, seed=o["cx"])
                            _VDONE[ck] = vim
                    else:
                        vim = render_vowel(vch, size_px, progress=prog, seed=o["cx"])
                    base.alpha_composite(vim, (int(o["cx"] - vim.width / 2), int(o["cy"] - vim.height / 2)))
                continue
        is_pose = "/poses/" in o["path"].replace("\\", "/")
        im = load_img(o["path"])
        sm, dx, dy, rot, a = (1, 0, 0, 0, 1) if final else obj_state(o, tt, dur)
        if a <= 0.01:
            continue
        glayers = None
        if is_pose and not final:                     # 캐릭터: 살아있는 idle + (gesture) 제스처 전환
            bob, sway, breathe = idle_motion(o["cx"], tt)
            dy += bob; rot += sway; sm *= breathe
            if o["motion"] == "gesture" and gestures:
                glayers, pop = gesture_layers(gestures, tt)
                sm *= pop
        # soft ground shadow for character poses (그림자는 바닥 고정 — bob에 안 흔들림, 캐시)
        if is_pose:
            shk = (round(o["cx"] + dx), round(o["cy"]), round(o["scale"] * 100))
            sh = _SHADOW.get(shk)
            if sh is None:
                sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                sd = ImageDraw.Draw(sh)
                sw = int(150 * o["scale"])
                shy = o["cy"] + int(300 * o["scale"])
                sd.ellipse([o["cx"] + dx - sw, shy - 16, o["cx"] + dx + sw, shy + 16], fill=(0, 0, 0, 45))
                sh = sh.filter(ImageFilter.GaussianBlur(7))
                if len(_SHADOW) < 200:
                    _SHADOW[shk] = sh
            base.alpha_composite(sh)
        if glayers:                                   # 제스처: 1~2개 포즈 레이어 합성(크로스페이드)
            for gp, ga in glayers:
                paste(base, load_img(gp), o["cx"] + dx, o["cy"] + dy, o["scale"] * sm * pulse, rot, a * ga)
        else:
            paste(base, im, o["cx"] + dx, o["cy"] + dy, o["scale"] * sm * pulse, rot, a)
    if overlay:
        draw_caption(base, scene["cap"])
        draw_subtitle(base, subtitle_text(scene, tt, final))
        draw_logo(base)
        draw_place(base, scene.get("place_en"))
    return base.convert("RGB")


# ---------- preview ----------
def preview(lang="ko"):
    scenes = load_scenes(lang)
    os.makedirs(os.path.join(PDIR, "preview"), exist_ok=True)
    cols, rows = 3, 5
    cw, ch = W // 2, H // 2
    sheet = Image.new("RGB", (cw * cols, ch * rows), (220, 220, 215))
    for i, sc in enumerate(scenes):
        frame = compose(sc, t=None, lang=lang)
        frame.save(os.path.join(PDIR, "preview", f"s{sc['seq']:02d}.png"))
        r, c = divmod(i, cols)
        sheet.paste(frame.resize((cw, ch), Image.LANCZOS), (c * cw, r * ch))
    out = os.path.join(PDIR, "preview", f"_sheet_{lang}.png")
    sheet.save(out)
    print("preview ->", out)


# ---------- TTS (여성 음성, 1.1배속) ----------
import re as _re
import hashlib as _hl


def _ff():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def _silence(dur):
    import subprocess
    p = os.path.join(TTS_DIR, f"sil_{int(round(dur * 1000))}.mp3")
    if not os.path.exists(p):
        subprocess.run([_ff(), "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t",
                        f"{dur:.3f}", p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return p


def _seg_tts(text, lang):
    """나레이션 텍스트 조각 → 여성 TTS, 1.1배속, 캐시(내용 해시)."""
    from tts_manager import save_tts
    import subprocess
    if not _re.search(r"[0-9A-Za-z가-힣ㄱ-ㅎㅏ-ㅣ]", text or ""):   # 부호/공백만 → 짧은 무음(TTS 빈입력 크래시 방지)
        return _silence(max(0.06, min(0.4, len(text or "") * 0.03)))
    h = _hl.md5((lang + "|" + text).encode("utf-8")).hexdigest()[:10]
    raw = os.path.join(TTS_DIR, f"seg_{lang}_{h}.mp3")
    fast = os.path.join(TTS_DIR, f"seg_{lang}_{h}_11.mp3")
    if not os.path.exists(fast):
        if not os.path.exists(raw):
            save_tts(text, raw, lang=lang)          # edge-tts 여성 → gTTS 폴백
        ok = os.path.exists(raw) and os.path.getsize(raw) > 800
        try:
            if not ok:
                raise RuntimeError("empty tts segment")
            subprocess.run([_ff(), "-y", "-i", raw, "-filter:a", "atempo=1.1", "-vn", fast],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except Exception:                            # 빈/깨진 세그먼트 → 폴백(원본 또는 짧은 무음)
            import shutil
            if ok:
                shutil.copy(raw, fast)
            else:
                subprocess.run([_ff(), "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                                "-t", "0.4", fast], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return fast


_PUNCT = _re.compile(r"^[\s,.!?·…'\"~\-—:;()]*$")

# ★ 한글 발음 원칙: 자모·단어·문장 등 한글은 영어판이라도 한국어 음성(선희/gTTS-ko)으로 읽는다.
_KR = _re.compile(r"[가-힣㄰-㆏ᄀ-ᇿ]")


def _split_kr_runs(text):
    """텍스트를 '한글 런 / 비한글 런'으로 분리 → [(run, is_korean), ...].
    한글은 항상 ko 음성, 그 외는 해당 언어 음성으로 읽어 영어 성우가 한글을 읽는 일을 막는다."""
    runs, cur, curk = [], "", None
    for ch in text:
        if not ch.strip():            # 공백/구두점은 현재 런에 붙임
            cur += ch
            continue
        k = bool(_KR.match(ch))
        if curk is None or k == curk:
            cur += ch
            curk = k
        else:
            if cur.strip():
                runs.append((cur, curk))
            cur, curk = ch, k
    if cur.strip():
        runs.append((cur, curk))
    return runs or [(text, bool(_KR.search(text)))]


def ensure_scene_audio(seq, script, lang):
    """나레이션을 낱자 기준으로 쪼개고 그 자리에 DB 발음 클립(SunHi)을 끼워 이어붙인다.
    반환: (mp3경로, 길이, schedule[(낱자, t0, t1)]) — 낱자가 실제로 들리는 시각."""
    from moviepy import AudioFileClip
    import subprocess
    import json as _json
    h = _hl.md5((lang + "||" + f"g{CLIP_GAIN}" + "||krvoice2||" + script).encode("utf-8")).hexdigest()[:10]
    final = os.path.join(TTS_DIR, f"scene_{lang}_{seq:02d}_{h}.mp3")
    schedf = final + ".sched.json"
    if os.path.exists(final) and os.path.exists(schedf):
        return final, AudioFileClip(final).duration, _json.load(open(schedf, encoding="utf-8"))

    quoted = sorted(CLIP_QUOTED, key=len, reverse=True)
    pat = "(" + "|".join([_re.escape(q) for q in quoted] + [_re.escape(k) for k in JAMO_SPEAK]) + ")"
    parts = [p for p in _re.split(pat, script) if p != ""]
    files, sched, t = [], [], 0.0
    loud = set()                                  # DB 발음 클립 세그먼트 인덱스(나레이션보다 약간 크게)
    # 발음 클립을 나레이션에 '거의 말하듯' 이어붙임 — 주변 무음 최소화(클립 자체 길이는 보존).
    PAD = 0.04
    PUNCT_SIL = 0.18
    for part in parts:
        clip, label = None, None
        if part in CLIP_QUOTED:                      # 따옴표 자음소리/단어 → DB 클립
            cand = os.path.join(JAMO_DIR, f"{CLIP_QUOTED[part]}.mp3")
            if os.path.exists(cand):
                clip, label = cand, CLIP_QUOTED[part]
        elif part in JAMO_SPEAK:                      # 낱자 → DB 발음 클립(SunHi)
            cand = os.path.join(JAMO_DIR, f"{part}.mp3")
            if os.path.exists(cand):
                clip, label = cand, part
            else:                                    # 클립 없으면 한국어 음성으로 이름 발음(영어 성우 금지)
                seg = _seg_tts(JAMO_SPEAK[part], "ko")
                files.append(seg); t += AudioFileClip(seg).duration
                continue
        if clip:
            sp = _silence(PAD)
            files.append(sp); t += PAD
            d = AudioFileClip(clip).duration
            loud.add(len(files))                  # 이 세그먼트(DB 발음 클립)는 나레이션보다 약간 크게
            files.append(clip); sched.append([label, round(t, 3), round(t + d, 3)]); t += d
            files.append(sp); t += PAD
        elif _PUNCT.match(part):                      # 구두점/공백 → 짧은 무음
            files.append(_silence(PUNCT_SIL)); t += PUNCT_SIL
        else:                                         # 일반 텍스트 → 한글런은 ko 음성, 그 외는 해당 언어
            for run, is_kr in _split_kr_runs(part):
                seg = _seg_tts(run, "ko" if is_kr else lang)
                files.append(seg); t += AudioFileClip(seg).duration

    # 입력 샘플레이트가 달라도 안전: 각 입력 24kHz mono 리샘플 후 concat 필터로 이어붙임
    inputs, filt = [], ""
    for i, p in enumerate(files):
        inputs += ["-i", p]
        vol = f",volume={CLIP_GAIN}" if i in loud else ""   # DB 발음 클립만 약간 크게
        filt += f"[{i}:a]aresample=24000,aformat=sample_fmts=fltp:channel_layouts=mono{vol}[a{i}];"
    filt += "".join(f"[a{i}]" for i in range(len(files))) + f"concat=n={len(files)}:v=0:a=1[out]"
    subprocess.run([_ff(), "-y", *inputs, "-filter_complex", filt, "-map", "[out]",
                    "-ar", "24000", "-ac", "1", final],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    _json.dump(sched, open(schedf, "w", encoding="utf-8"))
    return final, AudioFileClip(final).duration, sched


def render_video(lang="ko"):
    from moviepy import VideoClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
    from moviepy.audio.fx import MultiplyVolume
    scenes = load_scenes(lang)
    clips = []
    print(f"[render:{lang}] {len(scenes)} scenes — generating narration + frames…")
    for sc in scenes:
        audio_path, narr_dur, jsched = ensure_scene_audio(sc["seq"], sc["script"], lang)
        narr = AudioFileClip(audio_path)
        LEAD, TAIL = 0.25, 0.55          # 씬 길이 = 나레이션 + 짧은 앞뒤 여백
        dur = narr.duration + LEAD + TAIL
        sc["sound_sched"] = [(j, LEAD + t0, LEAD + t1) for (j, t0, t1) in jsched]  # 글자 맥동 동기화
        # 자막 청크 시간창: 글자수 비례로 나레이션 구간에 분배
        _chunks = sc.get("chunks") or [sc["script"]]
        _lens = [max(1, len(c)) for c in _chunks]
        _tot = sum(_lens)
        _acc, _sched = LEAD, []
        for _i, _l in enumerate(_lens):
            _w = narr.duration * _l / _tot
            _sched.append((_i, round(_acc, 3), round(_acc + _w, 3)))
            _acc += _w
        sc["sub_sched"] = _sched

        def mk(t, scene=sc, cam=sc.get("cam"), sdur=dur):
            fr = compose(scene, t=t, lang=lang, overlay=False)        # 씬(자막 제외)
            fr = apply_camera(fr, t, sdur, cam).convert("RGBA")       # 지미집 카메라 무빙
            draw_caption(fr, scene["cap"])                            # 자막/캡션은 고정 오버레이
            draw_subtitle(fr, subtitle_text(scene, t, False))        # 시간순 자막 청크
            draw_logo(fr)                                             # 좌상단 로고
            draw_place(fr, scene.get("place_en"))                    # 우하단 장소 영문명
            return np.asarray(fr.convert("RGB"))

        clip = VideoClip(frame_function=mk, duration=dur)
        scene_audio = CompositeAudioClip([narr.with_start(LEAD)]).with_duration(dur)
        clip = clip.with_audio(scene_audio)
        clips.append(clip)
        print(f"  S{sc['seq']:>2}: dur={dur:4.1f}s  narr={narr.duration:4.1f}s  jamo={len(jsched)}")

    video = concatenate_videoclips(clips, method="compose")

    # optional BGM bed (low volume, looped to length)
    bgm_path = os.path.join(ROOT, "assets", "audio", "lofi_bgm.mp3")
    if os.path.exists(bgm_path):
        try:
            from moviepy import concatenate_audioclips
            bgm = AudioFileClip(bgm_path)
            loops = int(video.duration // bgm.duration) + 1
            bed = concatenate_audioclips([bgm] * loops).subclipped(0, video.duration)
            bed = bed.with_effects([MultiplyVolume(0.07)])
            video = video.with_audio(CompositeAudioClip([video.audio, bed]))
            print("  + BGM bed added")
        except Exception as e:
            print("  (BGM skipped:", e, ")")

    out = os.path.join(PDIR, f"{OUT_PREFIX}_{lang}.mp4")
    video.write_videofile(out, fps=FPS, codec="libx264", audio_codec="aac",
                          threads=4, preset="medium", logger="bar")
    print("video ->", out)

    # update DB
    con = sqlite3.connect(DB)
    con.execute("UPDATE video_projects SET final_path=?, status=?, runtime_sec=?, updated_at=datetime('now') "
                "WHERE name=?", (out, "rendered", round(video.duration), PROJECT_NAME))
    con.execute("UPDATE episodes SET status='rendered' WHERE code=?", (EP,))
    con.commit()
    con.close()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--lang", default="ko")
    ap.add_argument("--episode", default="KO-W01")
    ap.add_argument("--prefix", default="hangeul_w1_stickman")
    args = ap.parse_args()
    EP = args.episode
    OUT_PREFIX = args.prefix
    PROJECT_NAME = args.prefix
    if args.preview:
        preview(args.lang)
    else:
        render_video(args.lang)
