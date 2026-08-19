# -*- coding: utf-8 -*-
"""W1-2 v3 **영어판 합성** — 12블록 이어 붙이기 + 파라메트릭 한글 + 나레이션.

★사장님 지시(2026-08-14) "영어판 렌더해서 교정앱에 올려서 보여줘.
  파라메트릭 렌더 가능한 한 충분히 해야 한다."

## 하는 일
  ① 블록마다 씬 영상을 `_v3_timeline.json` 이 정한 길이로 채운다
     — 모자라면 **앞뒤로 오가게(ping-pong)** 이어 늘린다. 속도는 건드리지 않는다.
  ② 그 위에 **파라메트릭 한글**을 획순으로 그려 얹는다 (`hangeul_write` + `old_jamo`)
  ③ 좌상단 **텍스트박스**를 얹는다
  ④ 영어 나레이션(edge-tts Emma)을 이어 붙여 깐다
  ⑤ 자막은 **번인하지 않는다** — `w1d2_v3_en.srt` 로 따로 낸다

## 화면 한글 고르기
대본의 '화면 한글' 칸에는 `**삽화** 여우 그림 카드` 처럼 **지시어**가 섞여 있다.
그리라는 글자가 아니므로 걸러 낸다 — 자모·단어만 남긴다.

  python W1_2/assemble_en_v3.py --plan     # 계획만
  python W1_2/assemble_en_v3.py            # 렌더
"""
import argparse
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import hangeul_write as HW                            # noqa: E402
import old_jamo                                       # noqa: E402,F401

W, H, FPS = 1280, 720, 24
# ★2026-08-17 — 한글판도 **같은 합성기**를 쓴다. 화면 글자·로고·장소 표시·자막
#   시각 맞추기가 두 판에서 다르면 안 되기 때문이다. 바뀌는 것은 타임라인과
#   나레이션 폴더, 산출물 이름뿐이라 환경변수로만 갈아 끼운다.
#     ASM_TL   타임라인 json   ASM_AUD  나레이션 폴더   ASM_OUT  산출물 이름틀
TL = os.environ.get("ASM_TL") or "W1_2/_v3_timeline.json"
OUT_PAT = os.environ.get("ASM_OUT") or "W1_2/w1d2_v3_en_r%d.mp4"
AUD = os.environ.get("ASM_AUD") or "W1_2/_audio_en"
# ★2026-08-18 — 임시 폴더도 **판별로 나눈다.** 한글판과 영어판을 동시에 돌렸더니
#   같은 `_asm/out` 을 서로 지우고 쓰다 충돌했다("Device or resource busy").
TMP = os.environ.get("ASM_TMP") or "W1_2/_asm"
FONT = r"C:\Windows\Fonts\malgun.ttf"

# 씬 영상이 없는 블록 — 배경으로 채운다
BG_FOR = {3: "W1_2/bg/plaza_gate.mp4", 6: "W1_2/bg/stall_cuke.mp4",
          10: "W1_2/bg/path_leaves.mp4", 12: "W1_2/bg/dusk_lanterns.mp4"}

# 그리라는 글자가 아닌 말 — 대본 지시어
STOP = {"삽화", "그림", "카드", "블록", "스냅", "놀란", "얼굴", "손가락", "다섯",
        "형제", "치아", "우유팩", "여우팩", "난색", "한색", "회색", "모음", "단어", "은"}


def words_of(s):
    """'화면 한글' 칸에서 **그릴 글자만** 골라낸다."""
    s = re.sub(r"\*\*|\(.*?\)|←.*|→.*|=.*", " ", s or "")
    out = []
    for tok in re.split(r"[·／/\s|]+", s):
        tok = tok.strip()
        if not tok or tok in STOP:
            continue
        if not re.fullmatch(r"[가-힣ㄱ-ㅎㅏ-ㅣㆍㅿㆁㆆ]+", tok):
            continue
        if len(tok) > 4:
            continue
        out.append(tok)
    return out[:3]


def frames_of(clip, d):
    """클립을 프레임으로 풀어 필요한 장수만큼 만든다 — **정방향으로만**.

    ★교정(한글판 r1, 사장님 2026-08-17) — "실루엣 사람들은 **뒤로 걷고** 있다."
      옛 코드는 모자란 길이를 **앞뒤로 오가게(ping-pong)** 채웠다. 배경 8초가
      끝나면 되감기가 시작돼 사람들이 뒷걸음질하고 물줄기가 빨려 들어갔다.
      한국어 나레이션이 영어보다 길어 그 되감기가 블록마다 길게 나왔다.

      이제 **끝 프레임에서 멈춰 선다**. 배경 움직임이 멎을 뿐, 거꾸로 가지는
      않는다. 캐릭터 동선이 든 씬 영상은 루프하면 순간이동하므로 멈추는 편이
      낫다 — 남는 시간은 애초에 생기지 않게 씬 길이로 맞추는 것이 정답이고,
      여기는 마지막 안전망이다.
    """
    key = re.sub(r"[^A-Za-z0-9_]", "_", clip)
    dd = os.path.join(TMP, key)
    os.makedirs(dd, exist_ok=True)
    if not glob.glob(dd + "/*.png"):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", clip,
                        "-vf", "scale=%d:%d" % (W, H), os.path.join(dd, "f%04d.png")], check=True)
    fs = sorted(glob.glob(dd + "/*.png"))
    need = int(round(d * FPS))
    if need <= len(fs):
        return fs[:need]
    return fs + [fs[-1]] * (need - len(fs))


# ★2026-08-17 (사장님 지시) — "오른 하단에 워터마크 딱 맞는 크기의 로고로 다 덮어
#   주어야 하고, 오른 하단에 광화문이라는 영어 장소 표시를 다 해 주어야 한다.
#   앞엣것 W23 W24 등을 참고해서."
#
#   배경이 Flow(Veo) 산출물이라 우하단에 **반짝임 워터마크**와 코너 'Veo' 글자가
#   남는다. 지우려 하면 배경이 뭉개지므로 **같은 크기 로고로 덮는** 것이 정석이다.
#   좌표는 `hangeul_birth_vowels/compile_stickman.py` 가 1280x720 에서 쓰던 실측값
#   그대로다 — r15 우하단을 잘라 보니 반짝임 중심이 (1170, 605) 로 그 값과 맞았다.
#   ★순서: 배경 → 로고 → 캐릭터 → 자막 ([[project-w24-graduation]]). 여기서는
#   캐릭터가 이미 배경에 합성돼 들어오므로, 글자를 얹기 **전에** 로고를 찍는다.
WM_LOGO = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
# ★2026-08-17 교정(r16) — "로고가 너무 크다. 워터마크 딱 지울 만큼만의 크기로 막아줘."
#   자동 검출은 배경 무늬를 반짝임으로 잡아 번번이 틀렸다. 프레임을 6배로 늘려
#   **격자를 얹고 눈으로 짚어** 쟀다([[stage-horizon-measure-by-feet]]):
#     반짝임 ✦ — x 1137~1182 · y 576~622  →  45 x 46, 중심 (1160, 599)
#   옛 값 88px·(1177,615) 는 크기가 두 배였고 중심도 17px 오른쪽 아래로 밀려 있어
#   **왼쪽 위 뿔이 삐져나왔다.** 52px 이면 46 을 3px 여유로 덮는다.
WM_D = 52
WM_CX, WM_CY = 1160, 599
WM_VEO_BOX = (1232, 686, 44, 28)                      # 코너 'Veo' 글자 x, y, w, h
PLACE = "Gwanghwamun, Seoul"                          # 우하단 장소 표시
_WM = {}


def _fill_from_around(img, box):
    """코너 글자를 **주변 색으로** 메운다 — 지운 자리가 눈에 띄지 않게."""
    x, y, w, h = box
    a = np.array(img)
    top = a[max(0, y - 4):y, x:x + w]
    left = a[y:y + h, max(0, x - 4):x]
    ref = np.concatenate([top.reshape(-1, 4), left.reshape(-1, 4)]) \
        if top.size and left.size else None
    if ref is None or not len(ref):
        return
    a[y:y + h, x:x + w] = np.median(ref, axis=0).astype(np.uint8)
    img.paste(Image.fromarray(a, "RGBA"), (0, 0))


def draw_wm_cover(img):
    """①코너 'Veo' 를 주변 색으로 ②반짝임 워터마크를 로고 하나로 덮는다."""
    if "main" not in _WM:
        _WM["main"] = (Image.open(WM_LOGO).convert("RGBA").resize((WM_D, WM_D), Image.LANCZOS)
                       if os.path.exists(WM_LOGO) else None)
    _fill_from_around(img, WM_VEO_BOX)
    if _WM["main"]:
        img.alpha_composite(_WM["main"], (WM_CX - WM_D // 2, WM_CY - WM_D // 2))


def draw_place(img):
    """우하단 장소 표시 — 로고와 겹치지 않게 왼쪽으로 비켜 놓는다."""
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 16)
    tw = d.textlength(PLACE, font=f)
    d.text((1280 - tw - 54, 720 - 26), PLACE, font=f, fill=(255, 255, 255),
           stroke_width=2, stroke_fill=(28, 24, 18))


def draw_block(img, box, words, prog):
    """텍스트박스 + 파라메트릭 한글을 얹는다."""
    d = ImageDraw.Draw(img, "RGBA")
    if box:
        f = ImageFont.truetype(FONT, 34)
        t = re.sub(r"\*\*", "", box)[:22]
        w = d.textlength(t, font=f)
        d.rounded_rectangle([28, 26, 28 + w + 34, 26 + 56], 12, fill=(20, 24, 34, 205))
        d.text((45, 40), t, font=f, fill=(255, 255, 255))
    # ★글자 자리는 **상반부 가로 중앙**으로 못 박혀 있다
    #   (§0-D · 사장님 확정 2026-08-12) — x 200~1080 · y 60~340 · **최대 세 줄**.
    #   "글자는 일관성 있게 늘 있는 위치에 있어야 보는 사람 눈에 보이니,
    #    상 1/2 에 준하고 좌우에 너무 치우치지 않게 하고 세 줄까지 되게 정하자."
    #   ★2026-08-14 교정 — 옛 코드는 화면 **오른쪽 끝에 세로로 쌓았다**. 오른쪽에 선
    #     캐릭터(S8·S9 는 x980)와 겹쳤고, 셋째 글자부터는 화면 밖으로 나갔다.
    # ★진행도 — 단어가 하나씩 차례로 **끝까지** 써져야 한다.
    #   옛 식 `prog*1.6 - k*0.35` 는 단어가 다섯을 넘으면 뒤쪽이 영영 다 안 써졌다
    #   ('우유'가 '으으'로, '여우'가 조각으로 남았다 · 2026-08-14 발견).
    #   앞섬(lead)을 단어 수에 맞춰 늘려 **마지막 단어도 prog=1 에서 100%** 가 되게 한다.
    span = 0.35
    lead = 1.0 + span * max(0, len(words) - 1)

    def pr(k):
        return max(0.0, min(1.0, prog * lead - k * span))

    vis = [(k, wd) for k, wd in enumerate(words) if pr(k) > 0]
    if not vis:
        return
    # ★`render_syllable` 은 **한 음절**만 그린다. '아이' 를 통째로 넘기면 두 글자가
    #   한 칸에 겹쳐 그려진다(2026-08-14 발견 — 옛 코드부터 있던 결함).
    #   음절로 쪼개 칸을 나누되, **단어 사이는 넓게** 띄워 단어가 붙어 보이지 않게 한다.
    cells = [(ch, k, i == 0) for k, wd in vis for i, ch in enumerate(wd)]
    # ★2026-08-15 사장님 지시 — "글자가 너무 크다. 파라메트릭 글자 사이즈를 줄이고
    #   **캐릭터 얼굴에 겹치지 않게** 캐릭터 없는 오른편에 쓰든지 **상 1/4** 에 쓰도록."
    #   → 늘 같은 자리라야 눈에 익으므로 **상 1/4(y 16~196)** 로 못 박고 크기를 낮춘다.
    #     전경 캐릭터도 600/717 로 줄여(render_scenes.CHAR_SCALE) 머리가 y 260 아래로
    #     내려가므로 글자와 겹치지 않는다.
    X0, X1, Y0, Y1 = 200, 1080, 16, 196               # 상 1/4
    AW, AH, GAP, WGAP = X1 - X0, Y1 - Y0, 8, 46       # 음절 사이 / 단어 사이
    n = len(cells)
    rows = 1 if n <= 6 else 2                         # 상 1/4 에는 두 줄까지
    per = -(-n // rows)
    S = max(40, min(120, (AW - (per - 1) * WGAP) // per,
                    (AH - (rows - 1) * GAP) // rows))
    # ★단어가 줄을 넘어 쪼개지지 않게 **단어 단위**로 줄을 나눈다
    #   ('오이' 가 앞줄 끝 '오' 와 뒷줄 머리 '이' 로 갈라졌다 · 2026-08-14)
    lines_, cur = [], []
    for k, wd in vis:
        piece = [(ch, k, i == 0) for i, ch in enumerate(wd)]
        if cur and len(cur) + len(piece) > per and len(lines_) < rows - 1:
            lines_.append(cur)
            cur = []
        cur += piece
    if cur:
        lines_.append(cur)
    rows = len(lines_)
    # 줄이 실제로 하나로 줄었으면 남은 높이를 글자에 돌려준다
    S = max(40, min(120, S if rows > 1 else min(120, AH),
                    (AW - (max(len(r) for r in lines_) - 1) * WGAP)
                    // max(len(r) for r in lines_)))
    top = Y0 + (AH - (rows * S + (rows - 1) * GAP)) // 2
    for r, row in enumerate(lines_):
        if not row:
            break
        rw = sum(S + (0 if i == 0 else (WGAP if f else GAP))
                 for i, (_, _, f) in enumerate(row))
        x, y = X0 + (AW - rw) // 2, top + r * (S + GAP)
        for i, (ch, k, f) in enumerate(row):
            if i:
                x += WGAP if f else GAP
            img.alpha_composite(HW.render_syllable(ch, S, pr(k)), (x, y))
            x += S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    a = ap.parse_args()
    tl = json.load(io.open(TL, encoding="utf-8"))
    os.makedirs(TMP, exist_ok=True)

    print("블록  제목             길이   영상                         화면한글")
    plan = []
    for b in tl:
        clip = b["clip"] or BG_FOR.get(b["n"])
        ws = []
        for l in b["lines"]:
            ws += words_of(l["hangeul"])
        seen, uw = set(), []
        for x in ws:
            if x not in seen:
                seen.add(x); uw.append(x)
        print("  %2d  %-16s %5.1f  %-27s %s"
              % (b["n"], b["title"], b["show_sec"], os.path.basename(clip or "-"),
                 " ".join(uw[:6]) or "-"))
        plan.append((b, clip, uw))
    if a.plan:
        return 0

    od = os.path.join(TMP, "out")
    os.makedirs(od, exist_ok=True)
    for f in glob.glob(od + "/*.png"):
        os.remove(f)
    idx = 0
    for b, clip, uw in plan:
        fs = frames_of(clip, b["show_sec"])
        n = len(fs)
        for i, fp in enumerate(fs):
            t = b["start"] + i / float(FPS)
            cur = None
            for l in b["lines"]:
                if l["start"] <= t < l["start"] + l["dur"] + 0.35:
                    cur = l
                    break
            img = Image.open(fp).convert("RGBA")
            draw_wm_cover(img)                        # ★워터마크 → 로고로 덮기
            draw_place(img)                           # ★우하단 장소 표시
            if cur:
                p = (t - cur["start"]) / max(0.4, cur["dur"])
                draw_block(img, cur["box"], words_of(cur["hangeul"]), p)
            img.convert("RGB").save(os.path.join(od, "f%05d.png" % idx))
            idx += 1
        print("  블록 %2d  %d프레임" % (b["n"], n), flush=True)

    # ── 나레이션 — ★**자막이 정한 절대 시각**에 놓는다 ─────────────────
    #   옛 코드는 문장 오디오를 무음 없이 연달아 붙였다. 블록 영상이 나레이션보다
    #   길면 그 남는 시간만큼 다음 블록 소리가 앞당겨져, 뒤로 갈수록 자막과 어긋났다.
    #   실측(2026-08-17): 블록2 에서 이미 7.3초, 마지막엔 **37.6초** 벌어졌다.
    #   → 문장 앞에 모자란 만큼 **무음을 끼워** 자막 시각에 정확히 맞춘다.
    sil_dir = os.path.join(TMP, "sil")
    os.makedirs(sil_dir, exist_ok=True)

    def silence(sec):
        """그 길이의 무음 mp3 — 같은 길이는 한 번만 만든다."""
        key = "%.2f" % sec
        p = os.path.join(sil_dir, "s%s.mp3" % key.replace(".", "_"))
        if not os.path.exists(p):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                            "-i", "anullsrc=r=24000:cl=mono", "-t", key,
                            "-c:a", "libmp3lame", "-b:a", "64k", p], check=True)
        return p

    lst = os.path.join(TMP, "aud.txt")
    drift = 0.0
    missing = []
    with io.open(lst, "w", encoding="utf-8") as f:
        cur = 0.0
        for b in tl:
            for l in b["lines"]:
                # ★2026-08-17 — 나레이션 파일 이름은 **대본 도장**으로 정해진다
                #   (build_en_v3.line_mp3 와 같은 규칙). 번호로만 짓던 옛 이름은
                #   줄이 하나 밀리면 옛 소리를 그대로 물고 왔다.
                p = os.path.join(AUD, "b%02d_%02d_%s.mp3"
                                 % (b["n"], l["i"],
                                    hashlib.sha1(l["en"].encode("utf-8")).hexdigest()[:8]))
                if not os.path.exists(p):
                    # ★조용히 건너뛰지 않는다. 옛 코드는 `continue` 였고, 이름 규칙이
                    #   바뀐 순간 74줄이 통째로 빠져 **빈 목록**이 만들어졌다
                    #   (ffmpeg 가 "Invalid data" 로 죽어서야 알았다).
                    missing.append("B%d #%d  %s" % (b["n"], l["i"], l["en"][:60]))
                    continue
                gap = l["start"] - cur
                if gap > 0.02:
                    f.write("file '%s'\n"
                            % os.path.abspath(silence(gap)).replace("\\", "/"))
                    cur += gap
                drift = max(drift, abs(l["start"] - cur))
                f.write("file '%s'\n" % os.path.abspath(p).replace("\\", "/"))
                f.write("outpoint %.3f\n" % l["dur"])
                cur += l["dur"]
    if missing:
        print("\n★ 나레이션 %d줄이 없다 — build_en_v3.py 를 먼저 돌려라." % len(missing))
        for m in missing[:20]:
            print("   " + m)
        raise SystemExit("나레이션이 빠진 채로는 합치지 않는다")
    print("  나레이션 — 자막 시각에 맞춤 (최대 어긋남 %.2f초)" % drift)
    wav = os.path.join(TMP, "narr.m4a")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c:a", "aac", "-b:a", "160k", wav], check=True)

    v = 1 + len(glob.glob(OUT_PAT.replace("%d", "*")))
    out = OUT_PAT % v
    # ★교정(2026-08-18) — `-shortest` 는 **나레이션이 끝나는 순간 영상도 끊는다.**
    #   마지막 블록은 말이 끝난 뒤 달려 나가 사라지는 10초가 더 있는데, 그 대목이
    #   통째로 잘려 스틱맨이 화면 한복판에 선 채로 영상이 끝났다(사장님 지적).
    #   소리가 모자라는 뒤쪽은 **무음으로 채워** 영상을 끝까지 살린다.
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(od, "f%05d.png"), "-i", wav,
                    "-af", "apad", "-t", "%.3f" % (idx / float(FPS)),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", out], check=True)
    print("\n%s  %d프레임 · %.1f초" % (out, idx, idx / float(FPS)))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
