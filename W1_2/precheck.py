# -*- coding: utf-8 -*-
"""업로드 전 **10가지 점검** — 올리기 전에 눈으로 확인할 것을 기계가 먼저 센다.

★사장님 지시(2026-08-18) "업로드 하기 전 10가지 체크 하고."

  ① 4K 해상도  ② 길이 일치  ③ 오디오 트랙  ④ 나레이션이 Azure 인가
  ⑤ 자막 5종 존재  ⑥ 자막 줄 수 일치  ⑦ 외국어 자막에 한글·발음기호 보존
  ⑧ 썸네일 규격(1280x720·2MB 미만)  ⑨ 제목·설명·태그·AI 고지
  ⑩ 워터마크 덮개 로고와 장소 표시가 실제로 찍혔는가

  python W1_2/precheck.py
"""
import io
import os
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

V4K = {"ko": "W1_2/w1d2_4k_ko.mp4", "en": "W1_2/w1d2_4k_en.mp4"}
VSRC = {"ko": "W1_2/w1d2_final_ko_r1.mp4", "en": "W1_2/w1d2_final_en_r1.mp4"}
THUMB = {"ko": "W1_2/w1d2_thumb_ko.jpg", "en": "W1_2/w1d2_thumb_en.jpg"}
SUBS = "W1_2/subs"
PKG = "W1_2/w1d2pkg"
AUD = {"ko": "W1_2/_audio_ko_azure", "en": "W1_2/_audio_en_azure"}
LANGS = ["ko", "en", "ja", "zh-Hans", "es-419"]

ok = [0]
bad = [0]


def chk(no, name, good, detail=""):
    (ok if good else bad)[0] += 1
    print("  %s %2d %-26s %s" % ("✅" if good else "★", no, name, detail))


def probe(p, *ent):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", ",".join(ent),
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    return r.stdout.strip()


def main():
    print("=== 업로드 전 10가지 점검 ===\n")
    for lang in ("ko", "en"):
        print("[%s판]" % lang.upper())
        v, src = V4K[lang], VSRC[lang]
        # ① 4K
        wh = probe(v, "stream=width,height").split("\n")[0]
        chk(1, "4K 해상도", wh == "3840,2160", wh)
        # ② 길이 일치 (원본과 4K)
        d4, ds = float(probe(v, "format=duration") or 0), float(probe(src, "format=duration") or 0)
        chk(2, "길이 일치", abs(d4 - ds) < 0.5, "%.1f초 (원본 %.1f)" % (d4, ds))
        # ③ 오디오
        acodec = probe(v, "stream=codec_name").split("\n")
        chk(3, "오디오 트랙", len(acodec) >= 2, "/".join(acodec[:2]))
        # ④ Azure 나레이션
        n = len([f for f in os.listdir(AUD[lang]) if f.endswith(".mp3")]) if os.path.isdir(AUD[lang]) else 0
        chk(4, "Azure 나레이션", n >= 70, "%d줄 (%s)" % (n, AUD[lang]))
        # ⑧ 썸네일
        t = THUMB[lang]
        if os.path.exists(t):
            im = Image.open(t)
            mb = os.path.getsize(t) / 1048576.0
            chk(8, "썸네일 규격", im.size == (1280, 720) and mb < 2,
                "%dx%d · %.2fMB" % (im.size[0], im.size[1], mb))
        else:
            chk(8, "썸네일 규격", False, "없음")
        # ⑨ 메타
        ti = os.path.join(PKG, "%s_title.txt" % lang)
        de = os.path.join(PKG, "%s_desc.txt" % lang)
        tg = os.path.join(PKG, "w1d2_tags_%s.txt" % lang)
        good = all(os.path.exists(x) for x in (ti, de, tg))
        ai = good and ("AI" in io.open(de, encoding="utf-8").read() or
                       "Veo" in io.open(de, encoding="utf-8").read())
        chk(9, "제목·설명·태그·AI고지", good and ai,
            "제목 %d자 · 태그 %d개 · AI고지 %s"
            % (len(io.open(ti, encoding="utf-8").read()) if good else 0,
               len(io.open(tg, encoding="utf-8").read().split(",")) if good else 0,
               "있음" if ai else "★없음"))
        # ⑩ 로고·장소 표시
        f = os.path.join("scratch", "_pre_%s.png" % lang)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "100", "-i", src,
                        "-frames:v", "1", f], check=True)
        a = np.array(Image.open(f).convert("RGB")).astype(int)
        logo = a[573:625, 1134:1186]                 # 로고 자리
        dark = (logo.max(2) < 90).mean()             # 로고는 검은 테두리 원
        place = a[694:716, 1000:1240]
        bright = (place.max(2) > 200).mean()         # 흰 글자
        chk(10, "로고·장소 표시", dark > 0.25 and bright > 0.02,
            "로고 %.0f%% · 장소글자 %.1f%%" % (dark * 100, bright * 100))
        print()

    # ⑤⑥⑦ 자막
    print("[자막]")
    files = {c: os.path.join(SUBS, "w1d2.%s.srt" % c) for c in LANGS}
    have = [c for c in LANGS if os.path.exists(files[c])]
    chk(5, "자막 5종", len(have) == 5, " ".join(have))
    cnt = {}
    for c in have:
        s = io.open(files[c], encoding="utf-8").read().strip().split("\n\n")
        cnt[c] = len(s)
    chk(6, "자막 줄 수 일치", len(set(cnt.values())) == 1,
        " ".join("%s:%d" % (c, cnt[c]) for c in have))
    import re
    keep = {}
    for c in ("ja", "zh-Hans", "es-419"):
        if c not in have:
            continue
        s = io.open(files[c], encoding="utf-8").read()
        keep[c] = (len(re.findall(r"[가-힣ㆍ]", s)), len(re.findall(r"\[[a-z\-]+\]", s)))
    chk(7, "외국어 자막 한글·발음", all(k[0] > 60 and k[1] > 30 for k in keep.values()),
        " ".join("%s:한글%d/발음%d" % (c, k[0], k[1]) for c, k in keep.items()))

    print("\n=== 통과 %d · 실패 %d ===" % (ok[0], bad[0]))
    return 1 if bad[0] else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
