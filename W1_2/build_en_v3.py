# -*- coding: utf-8 -*-
"""W1-2 v3 **영어판** — 나레이션(edge-tts Emma) + 영어 자막(srt) + 블록 타임라인.

★사장님 지시(2026-08-14)
  "영어 자막 하나 만들고 영어판 렌더해서 보여줘. edge-tts 엠마를 쓰고,
   DB 성우는 선희로 미리 만들어서 다 넣고 시작하라."

## 왜 나레이션이 먼저인가
자막 타이밍은 **나레이션 길이가 정한다.** 문장마다 음성을 만들어 실제 길이를 재고,
그 길이대로 블록을 채운 뒤 srt 를 쓴다. 반대로 하면 자막과 소리가 어긋난다.

## 블록이 모자라면 영상을 늘린다
나레이션이 영상보다 길면 **속도를 바꾸지 않고** 영상을 앞뒤로 오가게(ping-pong) 이어
늘린다. 속도를 건드리면 걸음걸이가 무너진다.

  python W1_2/build_en_v3.py --plan    # 계획만 (음성 안 만듦)
  python W1_2/build_en_v3.py           # 음성 + srt + 타임라인
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

os.environ.setdefault("TTS_ENGINE", "edge")          # ★초안이므로 edge-tts
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import tts_manager as tm                              # noqa: E402
# ★2026-08-17 — 대본 원천을 v4 로 옮겼다. v4 는 **낱말 하나를 한 곳에서만**
#   꺼낸다(사장님 지시: 전반부 아이 중복·우유 두 번). v3 는 그대로 남겨 둔다.
from lines_v4 import BLOCKS                           # noqa: E402

# ★2026-08-18 — 나레이션 폴더를 **엔진별로 나눈다.** 캐시 이름은 대본 도장만
#   쓰므로 edge 로 만든 음성이 azure 렌더에 그대로 재사용된다
#   ([[tts-cache-engine-trap]]). 최종본은 BUILD_AUD=W1_2/_audio_en_azure 로 준다.
AUD = os.environ.get("BUILD_AUD") or "W1_2/_audio_en"
OUT_SRT = "W1_2/w1d2_v3_en.srt"
OUT_PLAN = "W1_2/_v3_timeline.json"
GAP = 0.35                                            # 문장 사이 숨 (기존 규칙)

# ★한글은 **선희 DB 클립**으로 따로 발음한다 (사장님 확정 원칙 2026-08-17)
#   "자막 안에 있는 한글은 ' ' 로 구분하고, 선희 음성으로 데이터베이스에 다 입력해서
#    따로 구분해서 발음하도록 모두 고친다. 이것이 원래 원칙이다."
#   옛 코드는 영어 문장을 **통째로 Emma** 에게 읽혔다 — 문장 속 '아이' '오이' 까지
#   영어 성우가 읽어 발음 교육이 무너졌다([[feedback-korean-pronunciation-principle]]).
JAMO_DIR = os.environ.get("JAMO_DIR") or os.path.join("web", "public", "audio", "jamo")
# ★2026-08-17 교정(r16 #2) — "아래아 으 이 는 선희가 발음해야지 뭐가 섞였네."
#   원인은 **옛 글자가 범위 밖**이었다는 것이다. `ㆍ`(U+318D) 는 ㄱ~ㅣ 구간에
#   들어가지 않아 따옴표가 안 붙었고, 그래서 영어 성우가 통째로 읽었다.
#   훈민정음 옛 글자 넷(ㆍ ㅿ ㆁ ㆆ)을 한글 범위에 함께 넣는다.
KO_CLS = "가-힣ㄱ-ㅎㅏ-ㅣㆍㅿㆁㆆ"
KO_RUN = re.compile(r"[%s]+" % KO_CLS)
QUOTED = re.compile(r"'([%s]+)'" % KO_CLS)
CLIP_GAIN = 1.4                                       # DB 클립은 나레이션보다 또렷하게
# ★DB 발음 클립은 **10% 느리게** 튼다 (사장님 지시 2026-08-17
#   "성우 데이터베이스 목소리가 너무 빠르다. 10% 정도 속도를 줄인다").
#   DB 파일 자체는 건드리지 않는다 — 다른 주차 강의가 이미 그 속도로 완성돼 있다.
CLIP_TEMPO = 0.90


def quote_ko(s):
    """문장 속 한글 토막을 ' ' 로 감싼다. 이미 감싼 것은 건드리지 않는다."""
    return re.sub(r"(?<!')(?<!\w)([%s]+)(?!')" % KO_CLS, r"'\1'", s)


# ★2026-08-17 (사장님 지적: "중간에 나레이션과 자막이 다른 곳이 많이 있다")
#   원인은 **캐시 키가 번호뿐**이었다는 것이다. `b04_07.mp3` 는 줄 번호로만 정해져
#   대본을 고쳐도 파일명이 그대로라, 옛 소리가 새 자막 위에 그대로 붙었다.
#   줄 하나가 삭제·삽입되면 그 뒤 번호가 통째로 밀려 **전부 어긋난다.**
#   이제 **대본 글자에서 뽑은 도장**을 파일명에 박는다 — 대본이 바뀌면 이름이
#   바뀌므로 옛 소리를 다시 쓸 길이 없다. `check_narration.py` 로 검증한다.
def stamp(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def line_mp3(n, i, text):
    return os.path.join(AUD, "b%02d_%02d_%s.mp3" % (n, i, stamp(text)))


def _seg(text, path, lang):
    """조각 하나를 음성으로. 한글이면 ko(선희), 아니면 en(Emma)."""
    if not os.path.exists(path):
        tm.save_tts(text, path, lang=lang)
    return path


def say(text, out):
    """★한글 조각은 **DB 클립**, 영어 조각은 **Emma** — 쪼개서 이어 붙인다."""
    if os.path.exists(out):
        return out
    tmp = os.path.join(AUD, "_seg")
    os.makedirs(tmp, exist_ok=True)
    parts = [p for p in QUOTED.split(quote_ko(text)) if p and p.strip()]
    segs, k = [], 0
    for p in parts:
        k += 1
        if KO_RUN.fullmatch(p):                       # 한글 조각
            clip = os.path.join(JAMO_DIR, p + ".mp3")
            if os.path.exists(clip):
                segs.append((clip, True))             # ★DB 클립(선희)
                continue
            segs.append((_seg(p, os.path.join(tmp, "ko_%s.mp3" % stamp(p)), "ko"),
                         True))                       # 클립이 없으면 한국어 음성으로
        else:                                          # 영어 조각
            t = p.strip(" ,")
            if not t:
                continue
            # ★조각 이름도 **조각 글자 자체의 도장**으로 짓는다(2026-08-17).
            #   옛 이름은 `b12_01_01_en.mp3` — 블록·줄 번호였다. 블록 mp3 를 지워도
            #   조각은 남아, 줄이 하나 밀리면 **옛 문장이 그대로 이어붙었다.**
            #   사장님이 들은 "노을 등이 켜진다" 자리에서 "거울 앞에서 연습" 소리가
            #   난 것이 이것이다. 이제 글자가 같아야만 재사용된다.
            segs.append((_seg(t, os.path.join(tmp, "en_%s.mp3" % stamp(t)), "en"),
                         False))
    if not segs:
        tm.save_tts(text, out, lang="en")
        return out
    if len(segs) == 1 and not segs[0][1]:
        shutil.copyfile(segs[0][0], out)
        return out
    # ★조각 앞뒤 **무음을 잘라내고** 이어 붙인다.
    #   TTS 산출물과 DB 클립 모두 앞뒤에 0.2~0.4초씩 여백이 있어, 조각이 여럿이면
    #   그 여백이 그대로 쌓인다. 자르지 않았더니 좌판 블록이 60초→110초로 불었다
    #   (2026-08-17). 자르면 한 문장처럼 이어진다. DB 클립만 조금 크게.
    trim = ("silenceremove=start_periods=1:start_silence=0.03:"
            "start_threshold=-45dB:detection=peak,areverse,"
            "silenceremove=start_periods=1:start_silence=0.03:"
            "start_threshold=-45dB:detection=peak,areverse")
    ins, filt = [], []
    for i, (p, is_clip) in enumerate(segs):
        ins += ["-i", p]
        slow = ",atempo=%.2f" % CLIP_TEMPO if is_clip else ""
        filt.append("[%d:a]aresample=24000,%s%s,volume=%.2f[a%d]"
                    % (i, trim, slow, CLIP_GAIN if is_clip else 1.0, i))
    fc = ";".join(filt) + ";" + "".join("[a%d]" % i for i in range(len(segs))) \
         + "concat=n=%d:v=0:a=1[out]" % len(segs)
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + ins +
                   ["-filter_complex", fc, "-map", "[out]",
                    "-c:a", "libmp3lame", "-b:a", "160k", out], check=True)
    return out


def mp3_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def ts(t):
    """srt 시각 — 00:01:23,456"""
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true", help="음성 만들지 않고 계획만")
    a = ap.parse_args()
    os.makedirs(AUD, exist_ok=True)

    timeline, t0, idx, srt = [], 0.0, 1, []
    print("블록  제목             영상초  나레이션초  늘림   줄")
    for n, title, clip, sec, lines in BLOCKS:
        durs = []
        for i, l in enumerate(lines):
            p = line_mp3(n, i, l["en"])                # ★대본 도장이 박힌 이름
            if not a.plan and not os.path.exists(p):
                say(l["en"], p)                        # ★한글=선희 DB 클립 / 영어=Emma
            durs.append(mp3_dur(p) if os.path.exists(p) else len(l["en"]) / 14.0)
        need = sum(durs) + GAP * len(lines)
        show = max(sec, need)                          # 모자라면 영상을 늘린다
        print("  %2d  %-16s %6.1f  %8.1f  %+6.1f  %2d"
              % (n, title, sec, need, show - sec, len(lines)))
        blk = {"n": n, "title": title, "clip": clip, "src_sec": sec,
               "show_sec": round(show, 2), "start": round(t0, 2), "lines": []}
        t = t0
        for i, (l, d) in enumerate(zip(lines, durs)):
            blk["lines"].append({"i": i, "en": l["en"], "ko": l["ko"],
                                 "box": l["box"], "hangeul": l["hangeul"],
                                 "start": round(t, 2), "dur": round(d, 2)})
            # ★자막에도 한글은 ' ' 로 구분해 적는다 — 소리와 글자가 같은 규칙을 따른다
            srt.append("%d\n%s --> %s\n%s\n" %
                       (idx, ts(t), ts(t + d), quote_ko(l["en"])))
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
        # ★2026-08-17 (사장님 지시) — "한글 ' ' 표시 부분 안에 있는 단어에 대한
        #   로마자 발음기호를 다 삽입해야 한다." 자막에만 넣는다 — DB(나레이션)에
        #   넣으면 TTS 가 로마자를 읽어 버린다([[subtitle-romanization-rule]]).
        #   철자가 아니라 **실제 발음**으로 적는다: 'ㅏ'[a] · '오이'[o-i].
        subprocess.run([sys.executable, os.path.join(ROOT, "add_pron_to_srt.py"),
                        OUT_SRT, OUT_SRT], check=True)
    print("\n전체 %.1f초 = %d분 %d초" % (t0, t0 // 60, t0 % 60))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
