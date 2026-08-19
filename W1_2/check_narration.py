# -*- coding: utf-8 -*-
"""나레이션 mp3 를 **받아써서** 자막(대본)과 대조한다.

★사장님 지시(2026-08-17)
  "중간에 나레이션과 자막이 다른 곳이 많이 있다. 이것 다 고쳐야 한다.
   새로 모두 체크 해보고 고친다."

## 왜 눈으로는 못 잡나
나레이션 mp3 는 `b<블록>_<줄>.mp3` 라는 **이름으로만** 캐시된다. 대본을 고쳐도
파일명이 그대로면 옛 음성이 그대로 붙는다. 파일 시각으로 걸러 보면 대본을 안 고친
줄까지 다 걸려 쓸모가 없다. **실제로 무엇을 말하는지 받아써서** 대본과 맞춰야
어긋난 줄만 정확히 나온다.

## 어떻게 대조하나
받아쓰기는 문장부호·대소문자·숫자 표기가 제멋대로다. 그래서
  - 소문자화, 문장부호 제거, `77` ↔ `seventy-seven` 같은 숫자 표기 통일
  - 한글은 받아쓰기가 로마자로 뱉으므로 **영어 부분만** 비교한다
    (한글 조각은 선희 DB 클립이라 소리는 애초에 대본대로다)
한 뒤 difflib 유사도로 잰다. 0.75 미만이면 어긋난 것으로 본다.

  python W1_2/check_narration.py            # 검사만
  python W1_2/check_narration.py --fix      # 어긋난 mp3 를 지운다(다음 빌드가 다시 만든다)
"""
import argparse
import difflib
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

from lines_v4 import BLOCKS                              # noqa: E402

AUD = "W1_2/_audio_en"
HIT = 0.75                                               # 이 밑이면 어긋난 것


# ★mp3 이름은 **대본 도장**으로 정해진다 (build_en_v3.py 와 같은 규칙).
#   번호로만 짓던 옛 이름은 줄이 하나 밀리면 옛 소리를 그대로 물고 왔다.
def line_mp3(n, i, text):
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return os.path.join(AUD, "b%02d_%02d_%s.mp3" % (n, i, h))

NUM = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
       "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten",
       "14": "fourteen", "77": "seventy seven", "224": "two hundred twenty four"}


def norm(s):
    """비교용으로 다듬는다 — 한글은 빼고, 영어만 남긴다."""
    s = re.sub(r"[가-힣ㄱ-ㅎㅏ-ㅣ]+", " ", s)             # 한글 조각 제거
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    out = []
    for w in s.split():
        out.append(NUM.get(w, w))
    return " ".join(" ".join(out).split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="어긋난 mp3 를 지운다")
    ap.add_argument("--model", default="base")
    a = ap.parse_args()

    from faster_whisper import WhisperModel
    m = WhisperModel(a.model, device="cpu", compute_type="int8")

    print("블록 줄  일치도  대본 / 받아쓰기")
    bad = []
    for n, title, clip, sec, lines in BLOCKS:
        for i, l in enumerate(lines):
            p = line_mp3(n, i, l["en"])
            if not os.path.exists(p):
                print("B%-2d %2d  ------  ★mp3 없음" % (n, i))
                bad.append((n, i, p, "없음"))
                continue
            segs, _ = m.transcribe(p, language="en", beam_size=1)
            heard = " ".join(s.text for s in segs)
            want, got = norm(l["en"]), norm(heard)
            if not want:                                  # 한글만 있는 줄
                continue
            r = difflib.SequenceMatcher(None, want, got).ratio()
            mark = "" if r >= HIT else "  ★어긋남"
            print("B%-2d %2d  %.2f%s" % (n, i, r, mark))
            if r < HIT:
                print("      대본: %s" % l["en"])
                print("      소리: %s" % heard.strip())
                bad.append((n, i, p, "%.2f" % r))

    print("\n★ 어긋난 줄 %d 개" % len(bad))
    for n, i, p, why in bad:
        print("  B%d #%d  %s" % (n, i, why))
    if a.fix and bad:
        for n, i, p, why in bad:
            if os.path.exists(p):
                os.remove(p)
        print("\n%d 개 지웠다 — build_en_v3.py 를 다시 돌리면 대본대로 새로 만든다." % len(bad))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
