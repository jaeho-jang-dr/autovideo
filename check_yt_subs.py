# -*- coding: utf-8 -*-
"""★유튜브에 실제로 올라간 자막 언어 확인 (업로드 후 검증용)
   한글강의 W1~W13 한글판/영어판 각각 ko/en/ja/zh/es 5개 자막이 다 있는지 점검.
사용: python check_yt_subs.py
"""
import sys
from yt_api import yt, existing_caption_langs

# (주차, 판, video_id) — DB youtube_uploads 기준
VIDEOS = [
    ("W01", "한글판", "PfNFf6umSsc"), ("W01", "영어판", "X_biKW_jDYg"),
    ("W02", "한글판", "C8NQM0GaWrc"), ("W02", "영어판", "KrHzUwFQ0XI"),
    ("W03", "한글판", "gHYAXDo0MYs"), ("W03", "영어판", "3UOVzWlilB4"),
    ("W04", "한글판", "2Fl5pixR-yE"), ("W04", "영어판", "UqG0AdEh5Iw"),
    ("W05", "한글판", "Wo-O0-_914c"), ("W05", "영어판", "RL7QZ37HVXI"),
    ("W06", "한글판", "nF04YoEV8jk"), ("W06", "영어판", "pxufMbQq8sM"),
    ("W07", "한글판", "zVVrm8De8QY"), ("W07", "영어판", "YNiTusNTJCM"),
    ("W08", "한글판", "xp9ktV7zOYY"), ("W08", "영어판", "xgEedO2aFnk"),
    ("W10", "한글판", "HhSRarWJS0E"), ("W10", "영어판", "YTex0QGe17o"),
    ("W11", "한글판", "TJLaZH-ghC0"), ("W11", "영어판", "Ecv5l7aQHGE"),
    ("W12", "한글판", "pM7eN6Qt6s4"), ("W12", "영어판", "VPgmXo5jXtY"),
    ("W13", "한글판", "zsfOc4R4IbA"), ("W13", "영어판", "XT0jYFhrsxY"),
]
WANT = ["ko", "en", "ja", "zh", "es"]   # zh는 zh-CN/zh-Hans 로도 올 수 있음


def norm(langs):
    out = set()
    for l in langs:
        l = l.lower()
        if l.startswith("zh"):
            out.add("zh")
        elif l.startswith("pt"):
            out.add("pt")
        else:
            out.add(l.split("-")[0])
    return out


def main():
    y = yt()
    print(f"{'영상':<16} {'있는 자막':<28} {'누락'}")
    print("-" * 64)
    miss_total = []
    for wk, ed, vid in VIDEOS:
        try:
            langs = existing_caption_langs(y, vid)
        except Exception as e:
            print(f"{wk} {ed:<8} ★조회실패 {vid}: {str(e)[:40]}")
            continue
        have = norm(langs.keys())
        missing = [w for w in WANT if w not in have]
        tag = f"{wk} {ed}"
        mark = "✅" if not missing else "★"
        print(f"{mark} {tag:<13} {','.join(sorted(have)):<28} {','.join(missing) if missing else '-'}")
        if missing:
            miss_total.append((wk, ed, vid, missing))
    print("-" * 64)
    if miss_total:
        print(f"\n★누락 있는 영상 {len(miss_total)}개:")
        for wk, ed, vid, m in miss_total:
            print(f"  {wk} {ed} ({vid}) → {', '.join(m)}")
    else:
        print("\n전부 5개 언어(ko/en/ja/zh/es) 자막 완비 ✅")


if __name__ == "__main__":
    main()
