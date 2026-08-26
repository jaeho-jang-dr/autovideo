# -*- coding: utf-8 -*-
"""W1-6 v4 — **29씬**을 DB(KO-W1-6)에 싣는다.

원천 = `W1_6/w1_6_lines.py`(v4). 자리표(`bg/scene_geom.json`)는 **더 이상 쓰지 않는다**.
v3 의 자리표는 4K 원장을 크롭·확대하기 위한 것이었고, v4 는 배경이 전부 8초 동영상이라
잘라 낼 원장 자체가 없다.

싣는 것
  scenes            나레이션 KO/EN · 스펙(배경 **동영상** · 낱말카드 · 파라메트릭 글자)
  scene_objects     인준(동작선) 1 + 파라메트릭 글자 1
  anim_sequences    씬마다 `iw1d6_sNN` — [들어오기] → [동작…] (→ [나가기])

★렌더러는 컷 폴더를 보지 않는다. `anim_char_poses`(char_key=injun_w1d6, 2416행)만 본다.
★기준 에셋 경로에 `/poses/` 가 들어가야 동작선이 돈다.
★인준 오브젝트의 motion_type 은 **`gseq:injun_w1d6:<시퀀스>`** 다.
  char_mode="teacher" 경로는 가로 이동만 되고 **깊이(키·발밑 y)를 못 준다.**
  랜드스케이프에서 인준이 골목을 따라 멀어지려면 gseq 경로여야 한다.

씬 길이를 알아야 비트 초를 못 박을 수 있다
  비트의 `dur` 은 **씬 길이에 대한 비율**이다. 그런데 배경 클립의 사건은 **절대 초**에
  일어난다(예: S1 은 6.6초에 나루터에 닿는다). 그래서 나레이션 실측 길이가 필요하다.
      1) python W1_6/build_w1_6.py            ← 글자수 추정으로 1차
      2) python W1_6/measure_w1_6.py          ← Azure TTS 실측 → _durations.json
      3) python W1_6/build_w1_6.py            ← 실측으로 다시 (비트 초가 정확해진다)
      4) 렌더

    SUB_LANGS=ko WALK_STRIDE_SEC=0.75 TTS_ENGINE=azure WM_LOGO_D=48 WM_VEO_FILL=1 \
      python compile_np.py KO-W1-6 hangeul_w1d6_injun_v4 review ko
"""
import json
import os
import shutil
import sqlite3
import sys

from PIL import ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_6"))
sys.path.insert(0, os.path.join(ROOT, "hangeul_birth_vowels"))
os.environ.setdefault("ELEVEN_API_KEY", "")

import w1_6_lines as L                                    # noqa: E402

DB = "channel/content.db"
EP = "KO-W1-6"
CHAR = "injun_w1d6"
BASEP = "assets/graphics/poses/injun_w1d6_base.png"
BASESRC = "W1_6/act_cuts/m01_talk/injun_w1d6_m01_talk_00.png"
FONT = "assets/fonts/Cafe24Dongdong.ttf"
DURJSON = "W1_6/_durations.json"
CANVAS_W, CANVAS_H = 1280, 720

NACT = 64                       # 동작 컷 = 64프레임
NMOVE = 8                       # 이동 컷 = 한 스트라이드 8프레임
CANVAS_REF = 724.0              # 컷 캔버스 표준 높이(발=캔버스 바닥)
FIG_H = 720.0                   # 컷 캔버스 안의 **서기 인물 높이**(전 컷 통일). 키 → 배율의 기준
ACT_FPS = 8.0                   # 64컷 ÷ 8초 = 원래 속도
RUN_STRIDE = 0.50               # 달리기 한 스트라이드(초) — 질주
LAND_STRETCH = 1.80             # 랜드스케이프 배경을 늘이는 한도(인준이 그 위를 달린다)
PV_STRETCH = 2.00               # 지점 배경을 늘이는 한도
WALK_STRIDE = 0.72              # 걷기 한 스트라이드(초)

# 파라메트릭 글자 — 인준 반대편, 1~3줄
WRITE_CY = 330
WRITE_MARGIN = 52
WRITE_MAX_W, WRITE_MAX_H = 520, 320
WRITE_MIN_PX, WRITE_MAX_PX = 62, 126


def log(m):
    print(m, flush=True)


def glyph_layout(lines):
    """화면 글자 블록 — 글자 크기·블록 크기를 계산한다(카페24 동동)."""
    if not lines:
        return "", 0.3, 0, 0
    f = ImageFont.truetype(FONT, 100)
    wmax = max(f.getbbox(t)[2] for t in lines) or 1
    size = min(100.0 * WRITE_MAX_W / wmax, WRITE_MAX_H / (len(lines) * 1.35), WRITE_MAX_PX)
    size = max(WRITE_MIN_PX, size)
    return ("\n".join(lines), round(size / 200.0, 4),
            int(wmax * size / 100.0), int(len(lines) * size * 1.35))


def note_box_bottom(cap):
    """왼편 위 낱말 카드가 **어디까지 내려오는지**(y) — `compile_np.draw_note_box` 와 같은 셈.

    ★왜 재는가 (2026-08-23 실측)
      카드도 파라메트릭 글자도 인준 반대편에 놓인다. 인준이 오른쪽인 씬(side=R)에서는
      **둘 다 왼쪽**이라, 카드가 두세 줄로 늘어나면 큰 글자와 **겹친다**.
      S14·S15·S23·S29 가 실제로 겹쳤다(S15 는 111px). 그래서 카드 아래로 글자를 내린다.
    """
    from PIL import Image, ImageDraw
    import compile_stickman as _cs
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    f = _cs.get_font(_cs.FONT_BD, 34)
    rows = _cs.wrap(d, cap, f, int(CANVAS_W * 0.42))
    asc, desc = f.getmetrics()
    return 44 + 28 + (asc + desc + 6) * max(1, len(rows))


def est_dur(sc):
    """나레이션 실측이 없을 때의 1차 추정 — 글자수 기준(선희 1.1배속 ≈ 12.2자/초)."""
    ko = len(sc["ko"]) / 12.2 + 0.9
    en = len(sc["en"]) / 15.4 + 0.9
    return round(max(ko, en) + 0.45, 2)


def load_durs():
    if os.path.exists(DURJSON):
        d = json.load(open(DURJSON, encoding="utf-8"))
        return {int(k): float(v) for k, v in d.get("scenes", {}).items()}
    return {}


# ★이름은 동작컷(m##)이지만 **실제로 걷는** 컷 — 이동컷처럼 순환 재생해야 발이 땅에 붙는다.
#   (m39_walk_front_bundle = 한 손에 보따리 들고 정면으로 걸어오는 64컷)
#   (m01_talk_boat = m01_talk 그림을 그대로 재등록한 별칭. S2 배 위 정지 자세 — 캐릭터는
#    움직이지 않지만 **배와 카메라가 함께 멀어지므로** 원칙상 "진짜 이동"과 같다(2026-08-26,
#    사장님 지시). 이름을 따로 둬 다른 29곳의 m01_talk 은 원칙 그대로 고정 크기를 지킨다.)
WALK_LIKE = {"m39_walk_front_bundle", "m01_talk_boat"}
# ★그 컷 64장 안에 **걸음 주기가 몇 번** 들어 있나(자기상관으로 실측). 걸음 속도 환산에 쓴다.
CUT_CYCLES = {"m39_walk_front_bundle": 64.0 / 9.0}


def is_move(cut):
    return cut.startswith("walk") or cut.startswith("run") or cut in WALK_LIKE


def stride_of(cut):
    return RUN_STRIDE if cut.startswith("run") else WALK_STRIDE


def make_beat(cut, a, b, secs, href, fps=None, stretch=1.0, keys=None, stride=None):
    """비트 하나 — 시작/끝의 발밑(x,y)과 키(h)를 그대로 물린다.

    x  : 절대 화소(seq_state 가 그대로 쓴다)
    fy : 절대 발밑 y (seq_foot). 컷 캔버스 높이가 달라도 호출부가 중심을 되계산한다
    s  : 키 ÷ 그 씬의 기준키. scene_objects.scale = 기준키/720 이므로 곱하면 키가 나온다
    """
    x0, y0, h0 = a
    x1, y1, h1 = b
    n = NACT if cut in WALK_LIKE else (NMOVE if is_move(cut) else NACT)
    bt = {"name": "%s_%02d" % (cut, 0),
          "cycle": ["%s_%02d" % (cut, i) for i in range(n)],
          "x_from": round(x0, 1), "x_to": round(x1, 1),
          "fy_from": round(y0, 1), "fy_to": round(y1, 1),
          "s_from": round(h0 / href, 4), "s_to": round(h1 / href, 4),
          "secs": round(secs, 3)}
    # ★등속 구간 — 달리기·걷기는 발이 땅에 붙어야 하므로 smoothstep(양끝 속도 0)을 끈다
    if keys == "linear":
        bt["ease"] = "linear"
    elif keys and isinstance(keys[0], (list, tuple)) and len(keys[0]) == 4             and isinstance(keys[0][0], float) and keys[0][0] <= 1.0 and len(keys) > 2             and all(len(k) == 4 for k in keys):
        bt["ease"] = "linear"
        bt["fy_keys"] = [[k[0], k[2]] for k in keys]
        bt["s_keys"] = [[k[0], round(k[3] / href, 5)] for k in keys]
        bt["x_from"], bt["x_to"] = keys[0][1], keys[-1][1]
    if is_move(cut):
        # ★★★원근법·스트라이드·위치이동을 **함께** 쓴다(사장님 지시 2026-08-25).
        #   걸음 수를 **실제로 나아간 거리**에서 계산한다. 그래야 발이 땅에 붙는다.
        #     깊이(카메라까지 거리, 키 단위) = F / 화면키       (F≈1108px)
        #     사람은 한 걸음주기에 **약 1.2 키**(걷기) · **2.4 키**(달리기)를 나아간다
        #     → 스트라이드(초) = 비트초 × 걸음당거리 ÷ 나아간거리
        #   앞서 배경 늘인 배수를 곱했더니 1.30초가 되어 "다리는 안 움직이고 좌표만" 이었다.
        _F = 1108.0
        _per = 2.4 if cut.startswith("run") else 1.2
        _d0, _d1 = _F / max(6.0, h0), _F / max(6.0, h1)
        _travel = abs(_d1 - _d0)
        if stride:
            # ★★`stride` = **걸음 한 주기**(초)다. 그런데 렌더러의 stride 는
            #   "cycle 전체를 도는 데 걸리는 초"다. m39 는 64컷 안에 **걸음 주기가 약 7번**
            #   들어 있어(자기상관 실측 주기 = **9프레임**), stride=1.0 을 그대로 주면
            #   1초에 7걸음이 되어 **뛰는 것처럼** 빨라진다.
            #   → 컷 안의 주기 수를 곱해 **한 걸음이 정말 그 초가 되게** 한다.
            _cyc = CUT_CYCLES.get(cut, 1)
            bt["stride"] = round(float(stride) * _cyc, 3)
        elif _travel > 0.4 and secs > 0.2:
            _st = secs * _per / _travel
            # 걷기는 0.45~1.10초, 달리기는 0.32~0.80초 밖으로 나가지 않게 묶는다
            _lo, _hi = (0.32, 0.80) if cut.startswith("run") else (0.45, 1.10)
            bt["stride"] = round(min(_hi, max(_lo, _st)), 3)
        else:
            bt["stride"] = round(stride_of(cut), 3)
    else:
        bt["oneshot"] = True
        bt["fps"] = float(fps or ACT_FPS)
        bt["fps_local"] = True                 # ★비트마다 0 에서 다시 센다(안 그러면 얼어붙는다)
    return bt


def bg_rate_for(sc, dur):
    """배경 재생 배속 — 8초 클립이 일찍 끝나 20초씩 얼어붙는 것을 줄인다.

    드론 워킹은 원래 느려서 2배로 늘여도 어색하지 않다. 다만 **랜드스케이프는 덜 늘인다**
    — 인준이 그 위를 달리므로 너무 늘이면 걸음이 땅보다 빨라져 미끄러져 보인다.
    ★S1 은 늘이지 않는다. 사장님이 두 번 짚으신 "아주 빠른 속도로 달려서"가 여기다.
    """
    if sc.get("no_stretch") or float(sc["bg_secs"]) < 4.0:
        return 1.0
    cap = LAND_STRETCH if sc.get("plan") else PV_STRETCH
    bgs = float(sc["bg_secs"])
    span = min(max(dur - 0.5, bgs), bgs * cap)
    return round(bgs / span, 4)


# ---------------------------------------------------------------- 땅에 못박기
_TRACK_CACHE = os.path.join("W1_6", "_ground_track.json")
_TRACKS = json.load(open(_TRACK_CACHE, encoding="utf-8")) if os.path.exists(_TRACK_CACHE) else {}


def ground_track(bg, x, y, bg_secs):
    # ★아직 안 만들어진 배경(무비랑 작업 중)이면 되짚기를 건너뛴다 — 빌드가 멈추면 안 된다
    """배경이 줌인하는 동안 **땅 한 점**이 시각마다 어디로 가고 얼마나 커지는지.

    ★왜 (2026-08-24 사장님 지적 "영상의 왜곡처럼 이상하게 보인다")
      지점 씬을 **고정 좌표·고정 크기**로 세워 두었는데 배경은 8초 내내 밀고 들어온다.
      고택 대문은 통과 높이가 346→447px(+29%) 커지는데 인준은 그대로였다 → 발이 미끄러지고
      안착 구도에서 1.28m 로 쪼그라들어 보였다. 이제 **광학흐름으로 땅을 되짚어** 붙인다.

    돌려주는 것 — [(bg초, x, y, 배율), …]  배율 1.0 = 안착 시각
    """
    key = "%s|%d|%d" % (os.path.basename(bg), round(x), round(y))
    if key in _TRACKS:
        return _TRACKS[key]
    if not os.path.exists(bg):
        return None
    try:
        sys.path.insert(0, os.path.join(ROOT, "W1_6"))
        from track_ground import track as _tk
        fps, n, i_s, rec, lost = _tk(bg, x, y, 1.0, None, 0, 60.0)
    except Exception as e:
        log("   ※땅 되짚기 실패(%s) — 고정 좌표로 간다: %s" % (os.path.basename(bg), str(e)[:60]))
        _TRACKS[key] = None
        return None
    out = []
    for i in sorted(rec):
        px, py, sc = rec[i]
        out.append([round(i / fps, 3), round(px, 1), round(py, 1), round(sc, 4)])

    # ★★되짚기가 **틀릴 수 있다.** 배경에 펄럭이는 것(달력 장·연기·물결)이 있으면
    #   광학흐름이 그것을 따라가 엉뚱한 값을 낸다. 실제로 pv17(달력 벽)에서
    #   배율이 1.93 까지 부풀어 인준이 819px 이 되고 머리가 192px 잘려 나갔다.
    #   **말이 안 되는 답은 버리고 고정 좌표로 되돌아간다.** 조용히 틀린 답보다 낫다.
    ss = [r[3] for r in out]
    xs = [r[1] for r in out]
    ys = [r[2] for r in out]
    # 판별은 **단조성**으로 한다 — 카메라가 한 방향으로 움직이면 배율도 한 방향으로만 변한다.
    # 배경에 펄럭이는 것이 있으면 흐름이 그것을 따라가 **오르락내리락**한다. 그것이 표시다.
    # (배율 폭 자체는 크기로 못 가른다 — 진짜 강한 줌인은 0.09~1.0 까지 간다)
    seq_s = [r[3] for r in out]                     # 시간 순(과거→안착)
    ups = sum(1 for a, b in zip(seq_s, seq_s[1:]) if b > a + 0.004)
    downs = sum(1 for a, b in zip(seq_s, seq_s[1:]) if b < a - 0.004)
    wrong = min(ups, downs) / max(1, ups + downs)
    why = None
    if not out or len(out) < 8:
        why = "표본이 너무 적다"
    elif wrong > 0.20:
        why = "배율이 오르락내리락한다(어긋난 걸음 %.0f%%)" % (wrong * 100)
    elif max(ss) > 1.18:
        why = "안착보다 앞이 더 크다(최대 %.2f) — 되짚기가 엉뚱한 것을 따라갔다" % max(ss)
    elif max(ss) / max(1e-6, min(ss)) > 12.0:
        why = "배율 폭이 %.0f배로 지나치다" % (max(ss) / max(1e-6, min(ss)))
    elif min(ys) < -60 or max(ys) > 790 or min(xs) < -200 or max(xs) > 1480:
        why = "따라간 점이 화면을 벗어난다"
    if why:
        log("   ※땅 되짚기 버림(%s) — %s. 고정 좌표로 간다"
            % (os.path.basename(bg), why))
        _TRACKS[key] = None
        json.dump(_TRACKS, open(_TRACK_CACHE, "w", encoding="utf-8"), ensure_ascii=False)
        return None

    _TRACKS[key] = out
    json.dump(_TRACKS, open(_TRACK_CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    return out


def track_at(tr, t):
    """되짚은 표에서 그 시각의 (x, y, 배율). 표 밖은 끝값."""
    if not tr:
        return None
    if t <= tr[0][0]:
        a = tr[0]; return a[1], a[2], a[3]
    if t >= tr[-1][0]:
        a = tr[-1]; return a[1], a[2], a[3]
    for a, b in zip(tr, tr[1:]):
        if a[0] <= t <= b[0]:
            u = (t - a[0]) / max(1e-9, b[0] - a[0])
            return (a[1] + (b[1] - a[1]) * u,
                    a[2] + (b[2] - a[2]) * u,
                    a[3] + (b[3] - a[3]) * u)
    a = tr[-1]; return a[1], a[2], a[3]


def pin_to_ground(raw, sc, rate, dur):
    """지점 씬의 **제자리 동작 비트**를 땅에 붙인다.

    `pos` 는 **안착 프레임 기준**이다. 그 앞 시각은 되짚은 표대로 발밑과 키를 바꾼다.
    들어오기·나가기 비트는 손대지 않는다(화면 밖에서 들어오는 길이라 땅과 무관).
    """
    tr = ground_track(sc["bg"], sc["pos"][0], sc["pos"][1], sc["bg_secs"])
    if not tr:
        return raw
    stretch = 1.0 / max(1e-6, rate)
    hset = sc["pos"][2]
    acc, out = 0.0, []
    tot = sum(r[3] for r in raw) or 1.0
    for cut, a, b, secs, fps, st, keys in raw:
        t0, t1 = acc, acc + secs
        acc = t1
        if is_move(cut) or keys is not None:
            out.append((cut, a, b, secs, fps, st, keys)); continue
        # 이 비트가 걸친 **배경 시각**(배속을 되돌린다)
        n = 9
        kx, ky, ks = [], [], []
        for i in range(n + 1):
            u = i / float(n)
            bgt = ((t0 + (t1 - t0) * u) / stretch)
            g = track_at(tr, bgt)
            if not g:
                continue
            kx.append(g[0]); ky.append([round(u, 4), round(g[1], 1)])
            ks.append([round(u, 4), round(g[2 - 0] if False else g[2], 4)])
        if len(ky) < 2:
            out.append((cut, a, b, secs, fps, st, keys)); continue
        gkeys = [(round(i / float(n), 4),
                  track_at(tr, ((t0 + (t1 - t0) * (i / float(n))) / stretch)))
                 for i in range(n + 1)]
        pack = [(u, g[0], g[1], hset * g[2]) for u, g in gkeys if g]
        out.append((cut, (pack[0][1], pack[0][2], pack[0][3]),
                    (pack[-1][1], pack[-1][2], pack[-1][3]),
                    secs, fps, st, pack))
    return out


def beats_for(sc, dur, rate):
    """씬 하나의 동작선 — 랜드스케이프는 `plan` 을 그대로, 지점은 들어오기+동작(+나가기)."""
    raw = []                                   # (cut, a, b, secs, fps)
    stretch = 1.0 / max(1e-6, rate)            # 배경이 늘어난 만큼 인준의 길도 늘어난다

    if sc.get("plan"):                         # ★랜드스케이프 — 배경 실측 좌표를 그대로
        # ★계획의 초는 **배경 클립의 시각**이다. 배경을 늘였으면 그만큼 같이 늘여야
        #   인준이 배경보다 먼저 닿거나 늦게 닿지 않는다(발이 땅에 붙어 있어야 한다).
        span = min(float(sc["bg_secs"]) * stretch, dur)
        prev_end = 0.0
        # ★이어 붙인 이동 비트는 **등속**이어야 한다.
        #   비트마다 smoothstep 이면 이음매마다 속도가 0 이 되어 3초에 한 번씩 멈칫한다
        #   (다리는 계속 도는데 몸이 안 나가는 제자리걸음). 다만 **마지막 이동 비트**는
        #   그대로 두어 자리에 자연스럽게 멈춰 서게 한다.
        _mv = [i for i, q in enumerate(sc["plan"]) if is_move(q[0])]
        _last_mv = _mv[-1] if _mv else -1
        for _i, _p in enumerate(sc["plan"]):
            cut, t_end, a, b, fps = _p[:5]
            keys = _p[5] if len(_p) > 5 else None
            if keys is None and is_move(cut) and _i != _last_mv:
                keys = "linear"
            # ★t_end 를 배경 길이 너머까지 쓸 수 있다 — "문 앞에 서서 설명한 뒤 들어간다"처럼
            #   배경이 멈춘 뒤에도 이어져야 하는 연기가 있다(사장님 교정 S22). None 만 배경 끝이다.
            end = span if t_end is None else min(float(t_end) * stretch, dur)
            secs = max(0.30, end - prev_end)
            raw.append((cut, a, b, secs, fps, stretch, keys))
            prev_end = end
        if dur > prev_end + 0.05:
            # ★배경이 멈춘 뒤 — 기본은 그 자리에 서서 **말한다**.
            #   하던 이동컷을 그대로 돌리면 멈춘 땅 위에서 제자리걸음이 된다(가장 눈에 띄는 사고).
            #   ★단 "문 안으로 걸어 들어가는 것이 마지막 장면"처럼 **이동으로 끝나야 하는 씬**은
            #     `hold_cut`/`hold_to` 로 지정한다(사장님 교정 S22).
            _hold = dur - prev_end
            _hc = sc.get("hold_cut")
            # ★계획의 마지막이 **걷는 컷**이면 끝까지 그대로 걷게 둔다.
            #   "저 멀리서부터 가까이까지 **계속 걸어 오는**" 씬은 중간에 서면 안 된다(사장님 지시).
            if _hc is None and raw and raw[-1][0] in WALK_LIKE:
                _hc = raw[-1][0]
                if sc.get("hold_to") is None:
                    sc = dict(sc); sc["hold_to"] = b
            if _hc:
                _ht = sc.get("hold_to") or b
                raw.append((_hc, b, _ht, _hold, None, 1.0, "linear"))
                prev_end = dur
            elif raw and raw[-1][0] == "m01_talk" and raw[-1][2] == b:
                # 계획의 마지막이 이미 말하기면 **이어 붙인다**(따로 두면 64컷을 두 번 돌아 툭 끊긴다)
                c0, a0, b0, s0, f0, t0, k0 = raw[-1]
                raw[-1] = (c0, a0, b0, s0 + _hold, f0, t0, k0)
            else:
                raw.append(("m01_talk", b, b, _hold, None, 1.0, None))
            prev_end = dur
    else:                                      # ★지점 — 들어오기 → 동작들 → 나가기
        pos = sc["pos"]
        afps = sc.get("act_fps") or {}
        en, ex = sc.get("enter"), sc.get("exit")
        fixed = 0.0
        if en:
            esec = L.ENTER_SEC["run" if en.startswith("run") else "walk"]
            raw.append((en, L.enter_start(en, pos), pos, esec, None, 1.0, None))
            fixed += esec
        acts = sc["acts"]
        xsec = L.EXIT_SEC if ex else 0.0
        rest = max(1.2, dur - fixed - xsec)
        # ★`act_secs` = {동작: 초} — 배경 사건에 맞물려야 하는 동작만 초를 못 박는다.
        #   (S8: 문이 4.2~6.0초에 열리므로 **두드리자마자 미는** 동작이 그 시각에 걸려야 한다)
        #   지정 안 한 동작들이 남은 시간을 나눠 갖는다.
        fixed_acts = sc.get("act_secs") or {}
        named = sum(min(v, rest) for k, v in fixed_acts.items() if k in acts)
        free = [a for a in acts if a not in fixed_acts]
        each = max(0.8, (rest - named) / len(free)) if free else 0.0
        for a in acts:
            _sec = fixed_acts.get(a, each)
            raw.append((a, pos, pos, _sec, afps.get(a), 1.0, None))
        if ex:
            raw.append((ex, pos, L.exit_end(ex, pos), xsec, None, 1.0, None))

    # ★2026-08-25 — 사장님 절대 원칙(캐릭터 크기 일관성) 이후 **기본값을 뒤집었다**.
    #   `pin_to_ground` 는 배경이 줌인하는 만큼 **정지 동작(acts) 중에도 키를 키운다** —
    #   광학적으로는 맞지만, "핵심 구간 내내 고정" 원칙과 정면으로 충돌한다.
    #   사장님 지시대로 크기 판단은 화소가 아니라 숫자로 하고, 화소(줌 추적)보다
    #   **크기 일관성**을 우선한다 — 배경이 줌인해도 인준은 고정 크기를 지킨다.
    #   그래서 이제 **명시적으로 `use_ground_pin=True` 를 켠 씬만** 땅을 되짚는다(기본 꺼짐).
    if not sc.get("plan") and sc.get("pos") and sc.get("use_ground_pin"):
        raw = pin_to_ground(raw, sc, rate, dur)              # ★(옵트인) 제자리 동작을 땅에 못박는다
    href = max(max(r[1][2], r[2][2]) for r in raw)          # 그 씬의 기준키 = 가장 큰 키
    out = []
    tot = sum(r[3] for r in raw) or 1.0
    for cut, a, b, secs, fps, st, keys in raw:
        bt = make_beat(cut, a, b, secs, href, fps, st, keys, sc.get("stride"))
        bt["dur"] = round(secs / tot, 5)
        out.append(bt)
    return out, href


def main():
    durs = load_durs()
    os.makedirs(os.path.dirname(BASEP), exist_ok=True)
    # ★캐릭터랑이 m01_talk 를 다시 만들었으므로 기준 이미지도 새로 뜬다
    if os.path.exists(BASESRC):
        shutil.copyfile(BASESRC, BASEP)

    con = sqlite3.connect(DB)
    cur = con.cursor()
    have = {r[0] for r in cur.execute(
        "SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,))}

    r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
    if r:
        AID = r[0]
    else:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) "
                    "VALUES (?,?,?,?,?)",
                    ("인준W1-6기준", "injun_w1d6_base", "pose", BASEP, "W1-6 base"))
        AID = cur.lastrowid

    cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
    cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
    cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'iw1d6_s%'")
    scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

    miss, nglyph, nmoveuse, nactuse = [], 0, {}, {}
    missing_bg = []
    total = 0.0
    for sc in L.SCENES:
        n = sc["n"]
        # ★`fixed_dur` = **화면이 정하는 씬 길이**(초). 나레이션에 억지로 맞추지 않는다.
        #   (사장님 지시 2026-08-25 "길이를 억지로 나레이션에 맞추지 마라")
        #   나레이션이 길면 씬을 넘겨 잘리므로, 그런 씬은 나레이션을 짧게 다시 쓴다.
        dur = float(sc["fixed_dur"]) if sc.get("fixed_dur") else               ((durs.get(n) or est_dur(sc)) + float(sc.get("tail") or 0.0))
        total += dur
        aseq = "iw1d6_s%02d" % n
        rate = bg_rate_for(sc, dur)
        bj, href = beats_for(sc, dur, rate)
        for b in bj:
            miss += [p for p in b["cycle"] if p not in have]
            base = b["cycle"][0].rsplit("_", 1)[0]
            (nmoveuse if is_move(base) else nactuse).setdefault(base, 0)
            (nmoveuse if is_move(base) else nactuse)[base] += 1

        dt, wscale, blk_w, blk_h = glyph_layout(sc["glyph"])
        # ★글자는 인준 반대편. C(가운데) 씬은 왼쪽에 둔다(인준이 가운데라 좌우가 다 비었다)
        side = sc.get("side", "R")
        write_cx = WRITE_MARGIN if side in ("R",) else (CANVAS_W - WRITE_MARGIN - blk_w)
        if side == "C":
            write_cx = WRITE_MARGIN

        bgpath = sc["bg"]
        if not os.path.exists(bgpath):
            # ★첫 번째에서 멈추지 않는다 — 빠진 것을 **다 모아** 마지막에 한 번에 알린다.
            missing_bg.append("S%-2d %s" % (n, bgpath))
            _fb = sc.get("bg_fallback")
            if _fb and os.path.exists(_fb):
                bgpath = _fb

        card = sc["card"]
        cap_ko = "%s  [%s]  %s" % (card[0], card[1], card[2])
        cap_en = "%s  [%s]  %s" % (card[0], card[1], card[3])
        # ★글자가 카드와 같은 쪽이면 카드 아래로 내린다(겹침 방지 — 위 note_box_bottom 설명)
        write_cy = WRITE_CY
        if write_cx < 520:
            _need = max(note_box_bottom(cap_ko), note_box_bottom(cap_en)) + 18 + blk_h / 2.0
            write_cy = max(WRITE_CY, min(_need, CANVAS_H - 30 - blk_h / 2.0))
        spec = {"cap_ko": cap_ko, "cap_en": cap_en,
                "title_ko": sc["title_ko"], "title_en": sc["title_en"],
                "motion": "static", "cam": "still",          # ★코드 줌 금지 — 워킹은 클립 안에
                "char_key": CHAR, "char_mode": "cut",        # ★teacher 아님(깊이 이동 필요)
                "draw_font": "cafe24_dongdong", "draw_dur": 1.6,
                "draw_text": dt, "draw_align": "left",
                "bg": None, "bg_video": bgpath, "bg_secs": sc["bg_secs"], "bg_rate": rate,
                "bg_offset": sc.get("bg_offset"),
                "fixed_dur": bool(sc.get("fixed_dur")),   # ★그림이 씬 길이를 지배하는 씬인지(전체 통본 렌더가 나레이션 길이로
                                                            #   덮어쓰지 않도록 compile_np.py 가 이 플래그를 본다)
                "layer": sc["layer"], "why": sc.get("why", ""),
                "place_en": L.PLACE[sc["place"]], "anim_seq": aseq}
        cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,"
                    "veo_prompt,duration_sec) VALUES (?,?,?,?,?,?,?)",
                    (EP, n, sc["ko"], sc["en"], json.dumps(spec, ensure_ascii=False), "", dur))
        # 인준 — 렌더에서 cx/cy 는 **정확히 상쇄된다**(자리는 비트의 x/fy 가 정한다).
        #   그래서 여기에는 **가장 큰 포즈의 실제 기하**를 적어 둔다.
        #   그래야 `check_char_fit.py` 같은 기존 가드가 옛 방식(중심=cy)으로 재도 맞는 값을 본다.
        #   (안 적어 두면 씬마다 "아래 100~200px 잘림" 이 뜬다 — 실제로는 안 잘리는데도)
        big = max(([b for p in sc["plan"] for b in (p[2], p[3])] if sc.get("plan")
                   else [sc["pos"]]), key=lambda v: v[2])
        anchor = (big[0], big[1] - CANVAS_REF * (href / FIG_H) / 2.0)
        cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,"
                    "z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                    (EP, n, AID, anchor[0], anchor[1], round(href / FIG_H, 6), 5,
                     "gseq:%s:%s" % (CHAR, aseq), 0))
        if dt:
            nglyph += 1
            cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,"
                        "z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                        (EP, n, AID, write_cx, round(write_cy), wscale, 7, "write", 0))
        fields = {"seq_name": aseq, "beats_json": json.dumps(bj, ensure_ascii=False)}
        if "description" in scols:
            fields["description"] = "인준 W1-6 v4 %s" % aseq
        cur.execute("INSERT INTO anim_sequences (%s) VALUES (%s)"
                    % (",".join(fields), ",".join("?" * len(fields))), list(fields.values()))
        _live = min(float(sc["bg_secs"]) / rate, dur)
        log("S%-2d %-5s %-26s %5.1fs 비트%d 키%3d→%3d 배속%.2f 정지%4.1fs 글자x%4d"
            % (n, sc["layer"], os.path.basename(bgpath), dur, len(bj),
               bj[0]["s_from"] * href, bj[-1]["s_to"] * href,
               rate, dur - _live, write_cx))

    if missing_bg:
        log("\n★아직 없는 배경 %d개 — 임시로 옛 배경을 쓰고 있다. 만들어지면 다시 빌드하라"
            % len(missing_bg))
        for m in missing_bg:
            log("   %s" % m)
    if miss:
        log("\n★DB 미등록 컷 %d개 — 롤백" % len(miss))
        for m in sorted(set(miss))[:20]:
            log("   %s" % m)
        con.rollback(); con.close(); return 1

    con.commit()
    ns = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
    no = cur.execute("SELECT COUNT(*) FROM scene_objects WHERE episode=?", (EP,)).fetchone()[0]
    con.close()

    # ★컷 소비 점검 — 만든 컷은 전량 쓴다(남는 것 0)
    allact = {p.rsplit("_", 1)[0] for p in have if p.startswith("m")}
    allmove = {p.rsplit("_", 1)[0] for p in have if not p.startswith("m")}
    unused_a = sorted(allact - set(nactuse))
    unused_m = sorted(allmove - set(nmoveuse))
    log("\n완료: %s %d씬 · 오브젝트 %d · 화면글자 %d씬 · 미등록 컷 없음" % (EP, ns, no, nglyph))
    log("동작컷 %d/%d 사용(슬롯 %d) · 이동컷 %d/%d 사용(슬롯 %d)"
        % (len(nactuse), len(allact), sum(nactuse.values()),
           len(nmoveuse), len(allmove), sum(nmoveuse.values())))
    log("남는 동작컷: %s" % (", ".join(unused_a) or "없음"))
    log("남는 이동컷: %s" % (", ".join(unused_m) or "없음"))
    log("예상 전체 길이 %.1f초 (%d분 %02d초)  ※%s"
        % (total, int(total // 60), int(total % 60),
           "나레이션 실측" if durs else "글자수 추정 — measure_w1_6.py 를 돌려라"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
