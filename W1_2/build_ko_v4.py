# -*- coding: utf-8 -*-
"""W1-2 v4 **한글판** — 나레이션(선희) + 한글 자막(srt) + 블록 타임라인.

★사장님 지시(2026-08-17) "한글 버전 만들고 자막 5개 다 만들고, 한글 버전은 한글
  자막과 함께 교정앱에 띄워서 보여줘."

## 영어판과 무엇이 다른가
영어판은 문장을 **영어 조각 + 한글 조각**으로 쪼개, 영어는 Emma 가 한글은 선희 DB
클립이 읽었다. 한글판은 처음부터 끝까지 **한국어 한 사람**이 읽으면 되므로 쪼갤
까닭이 없다 — 문장을 통째로 선희에게 준다.

그래도 **낱말을 짚는 자리**는 DB 클립을 쓴다. 자막에 ' ' 로 감싼 낱말은 발음을
가르치는 자리이고, 그 소리는 다른 주차 강의와 같아야 한다([[feedback-korean-pronunciation-principle]]).

## 자막
★사장님 지시(2026-08-17) "**한글 자막으로 공부하는 외국인도 있으니 한글 자막에도
낱말은 로마자 발음기호가 있어야 한다.**"
문장 전체에 붙이면 읽기를 방해하므로 **그 줄이 가르치는 낱말 하나**에만 붙인다.
어느 낱말인지는 대본의 `box` 가 알고 있다 — "아이 [a-i] child" 처럼.

  python W1_2/build_ko_v4.py --plan    # 계획만
  python W1_2/build_ko_v4.py           # 음성 + srt + 타임라인
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

os.environ.setdefault("TTS_ENGINE", "edge")          # ★초안이므로 edge-tts(선희)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import tts_manager as tm                              # noqa: E402
from lines_v4 import BLOCKS                           # noqa: E402

AUD = os.environ.get("BUILD_AUD") or "W1_2/_audio_ko"    # ★엔진별로 폴더를 나눈다
OUT_SRT = "W1_2/w1d2_v4_ko.srt"
OUT_PLAN = "W1_2/_v4_ko_timeline.json"
# ★교정(한글판 r1, 사장님 2026-08-17) — "영어와는 나레이션 속도 때문에 안 맞을 수
#   있으니 **시간을 잘 조절**하고." 한국어는 같은 뜻을 말해도 영어보다 길어,
#   영상보다 77초가 넘쳤고 그만큼 영상이 되감겨 배경이 거꾸로 흘렀다.
#   문장 사이 숨을 0.35 → 0.25 로 줄인다(76줄이면 7.6초).
GAP = 0.25

# ★한글 자막에도 **낱말에는 로마자 발음기호**를 붙인다 (사장님 2026-08-17
#   "한글 자막으로 공부하는 외국인도 있으니").
#   문장 전체에 붙이면 읽기를 방해하므로, **오늘 배우는 낱말**에만 붙인다.
#   나레이션은 원문(l["ko"])을 그대로 읽으므로 소리에는 영향이 없다.
#   어느 낱말이 그 줄의 **학습 대상**인지는 대본의 `box` 가 이미 알고 있다
#   ("아이 [a-i] child" · "위 [wi] above"). 거기서 낱말과 발음을 그대로 가져온다.
#   낱말 목록을 따로 두면 `이` `오` 같은 한 글자가 "이것" "오늘" 에까지 붙는다.
BOX_WORD = re.compile(r"^([가-힣]+)\s*\[([a-z\-]+)\]")


def mark_words(ko, box):
    """그 줄이 가르치는 낱말에만 ' ' 와 발음기호를 붙인다 — 처음 한 번만."""
    m = BOX_WORD.match((box or "").strip())
    if not m:
        return ko
    w, pron = m.group(1), m.group(2)
    # 조사가 뒤에 붙으므로 뒤쪽은 막지 않는다 ("우유가", "이유라고")
    hit = re.search(r"(?<!['가-힣])%s" % re.escape(w), ko)
    if not hit:
        return ko
    return ko[:hit.start()] + "'%s' [%s]" % (w, pron) + ko[hit.end():]


def stamp(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def line_mp3(n, i, text):
    return os.path.join(AUD, "b%02d_%02d_%s.mp3" % (n, i, stamp(text)))


# ★프로젝트 규칙 — 나레이션은 **항상 10% 빠르게** 튼다(CLAUDE.md 황금원칙 7).
#   한국어는 같은 뜻을 말해도 영어보다 길어, 이 규칙을 빼면 영상이 모자라 앞뒤로
#   오가게(ping-pong) 늘려야 한다. 물줄기가 거꾸로 흐르는 사고가 여기서 났다.
SPEED = 1.15                                          # ★한글은 길어 조금 더 빠르게


def say(text, out):
    """한글판은 **통째로 선희**가 읽는다 — 쪼갤 까닭이 없다. 그다음 10% 빠르게."""
    if os.path.exists(out):
        return out
    raw = out + ".raw.mp3"
    tm.save_tts(text, raw, lang="ko")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw,
                    "-filter:a", "atempo=%.2f" % SPEED,
                    "-c:a", "libmp3lame", "-b:a", "160k", out], check=True)
    os.remove(raw)
    return out


def mp3_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    a = ap.parse_args()
    os.makedirs(AUD, exist_ok=True)

    timeline, t0, idx, srt = [], 0.0, 1, []
    print("블록  제목             영상초  나레이션초  늘림   줄")
    for n, title, clip, sec, lines in BLOCKS:
        durs = []
        for i, l in enumerate(lines):
            p = line_mp3(n, i, l["ko"])
            if not a.plan and not os.path.exists(p):
                say(l["ko"], p)
            durs.append(mp3_dur(p) if os.path.exists(p) else len(l["ko"]) / 7.0)
        need = sum(durs) + GAP * len(lines)
        show = max(sec, need)
        print("  %2d  %-16s %6.1f  %8.1f  %+6.1f  %2d"
              % (n, title, sec, need, show - sec, len(lines)))
        blk = {"n": n, "title": title, "clip": clip, "src_sec": sec,
               "show_sec": round(show, 2), "start": round(t0, 2), "lines": []}
        t = t0
        for i, (l, d) in enumerate(zip(lines, durs)):
            blk["lines"].append({"i": i, "en": l["ko"], "ko": l["ko"],
                                 "box": l["box"], "hangeul": l["hangeul"],
                                 "start": round(t, 2), "dur": round(d, 2)})
            srt.append("%d\n%s --> %s\n%s\n"
                       % (idx, ts(t), ts(t + d), mark_words(l["ko"], l["box"])))
            idx += 1
            t += d + GAP
        timeline.append(blk)
        t0 += show

    if not a.plan:
        with open(OUT_SRT, "w", encoding="utf-8") as f:
            f.write("\n".join(srt))
        with open(OUT_PLAN, "w", encoding="utf-8") as f:
            json.dump(timeline, f, ensure_ascii=False, indent=1)
        print("\n%s  %d줄" % (OUT_SRT, idx - 1))
        print("%s" % OUT_PLAN)
    print("\n전체 %.1f초 = %d분 %d초" % (t0, t0 // 60, t0 % 60))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
