# -*- coding: utf-8 -*-
"""titan_science 자막 — 나레이션에서 KO/EN srt 를 만들고, 나머지 3개국어로 옮긴다.

★자막은 **번인 금지** — 소프트 srt 로만 붙인다.
★언어코드: 스페인어는 **es-419**(라틴아메리카), 중국어는 **zh-Hans**(본토 간체).

    python titan_srt.py --base        # ko / en srt
    python titan_srt.py --translate   # ja / zh-Hans / es-419
"""
import argparse
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
SUB_DIR = os.path.join(ROOT, "titan_science", "subs")
AUD_DIR = os.path.join(ROOT, "titan_science", "audio")

import titan_narr as N          # noqa: E402  씬 원고·길이 계산을 그대로 쓴다

MAX_CHARS = {"ko": 38, "en": 78}        # 한 자막에 넣을 최대 글자


def split_sentences(text, lang):
    """문장 단위로 자르고, 너무 길면 쉼표에서 한 번 더 자른다."""
    parts = re.split(r"(?<=[.!?。])\s+|(?<=다\.)\s*|(?<=요\.)\s*", text)
    parts = [p.strip() for p in parts if p and p.strip()]
    out = []
    for p in parts:
        if len(p) <= MAX_CHARS[lang]:
            out.append(p)
            continue
        buf = ""
        for chunk in re.split(r"(?<=,)\s+", p):
            if buf and len(buf) + len(chunk) > MAX_CHARS[lang]:
                out.append(buf.strip())
                buf = chunk
            else:
                buf = (buf + " " + chunk).strip()
        if buf:
            out.append(buf)
    return out


def ts(t):
    h, r = divmod(max(0.0, t), 3600)
    m, s = divmod(r, 60)
    return "%02d:%02d:%06.3f" % (h, m, s).replace(".", ",") if False else \
        "%02d:%02d:%02d,%03d" % (h, m, int(s), round((s - int(s)) * 1000))


def build(lang):
    sc = N.scenes()
    starts, lens = scene_starts()
    cues = []
    for n in sorted(sc):
        mp3 = os.path.join(AUD_DIR, "s%02d_%s.mp3" % (n, lang))
        if not os.path.exists(mp3):
            continue
        d = min(N.dur(mp3), lens[n] - 0.15)      # 렌더에서 씬 안에 맞춰 넣었다
        t0 = starts[n]
        sents = split_sentences(sc[n][lang], lang)
        total = sum(len(s) for s in sents) or 1
        cur = t0
        for s in sents:
            span = d * len(s) / total
            cues.append((cur, cur + span - 0.06, s))
            cur += span
    return cues


def scene_starts():
    import collections
    per = collections.defaultdict(float)
    for f in os.listdir(N.CLIP_DIR):
        m = re.match(r"^s(\d\d)_.+\.mp4$", f)
        if m:
            per[int(m.group(1))] += N.dur(os.path.join(N.CLIP_DIR, f))
    starts, t = {}, 0.0
    for n in sorted(per):
        starts[n] = t
        t += per[n]
    return starts, dict(sorted(per.items()))


def write_srt(cues, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, s) in enumerate(cues, 1):
            f.write("%d\n%s --> %s\n%s\n\n" % (i, ts(a), ts(b), s))
    return path


def read_srt(path):
    """(시작, 끝, 본문) 목록으로 읽는다."""
    blocks = re.split(r"\n\s*\n", open(path, encoding="utf-8").read().strip())
    out = []
    for b in blocks:
        ln = b.strip().splitlines()
        if len(ln) >= 3:
            out.append((ln[1], "\n".join(ln[2:])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", action="store_true")
    ap.add_argument("--translate", action="store_true")
    a = ap.parse_args()
    os.makedirs(SUB_DIR, exist_ok=True)

    if a.base or not (a.base or a.translate):
        for lg in ("ko", "en"):
            cues = build(lg)
            p = write_srt(cues, os.path.join(SUB_DIR, "TITAN_%s.srt" % lg))
            print("%s  %d줄" % (p, len(cues)))
    if a.translate:
        print("번역은 titan_tx.py 로 한다")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
