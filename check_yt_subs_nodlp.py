# -*- coding: utf-8 -*-
"""★유튜브 자막 확인 — API 쿼터 안 씀 (yt-dlp 공개 메타데이터 사용)
   한글강의 각 영상에 수동 자막 ko/en/ja/zh/es 가 실제로 붙었는지 점검.
   ⚠️자동자막(ASR)은 automatic_captions 로 분리되므로 제외 — 우리가 올린 것만 본다.
사용: python check_yt_subs_nodlp.py
"""
import sys
import yt_dlp

VIDEOS = [
    ("W01", "한글판", "PfNFf6umSsc"), ("W01", "영어판", "X_biKW_jDYg"),
    ("W02", "한글판", "C8NQM0GaWrc"), ("W02", "영어판", "KrHzUwFQ0XI"),
    ("W03", "한글판", "gHYAXDo0MYs"), ("W03", "영어판", "3UOVzWlilB4"),
    ("W04", "한글판", "2Fl5pixR-yE"), ("W04", "영어판", "UqG0AdEh5Iw"),
    ("W05", "한글판", "Wo-O0-_914c"), ("W05", "영어판", "RL7QZ37HVXI"),
    ("W06", "한글판", "nF04YoEV8jk"), ("W06", "영어판", "pxufMbQq8sM"),
    ("W07", "한글판", "zVVrm8De8QY"), ("W07", "영어판", "YNiTusNTJCM"),
    ("W08", "한글판", "xp9ktV7zOYY"), ("W08", "영어판", "xgEedO2aFnk"),
    ("W09", "한글판", None),          ("W09", "영어판", None),
    ("W10", "한글판", "HhSRarWJS0E"), ("W10", "영어판", "YTex0QGe17o"),
    ("W11", "한글판", "TJLaZH-ghC0"), ("W11", "영어판", "Ecv5l7aQHGE"),
    ("W12", "한글판", "pM7eN6Qt6s4"), ("W12", "영어판", "VPgmXo5jXtY"),
    ("W13", "한글판", "zsfOc4R4IbA"), ("W13", "영어판", "XT0jYFhrsxY"),
]
WANT = ["ko", "en", "ja", "zh", "es"]


def norm(langs):
    out = set()
    for l in langs:
        l = l.lower()
        if l.startswith("zh"):
            out.add("zh")
        else:
            out.add(l.split("-")[0])
    return out


def main():
    opts = {"quiet": True, "skip_download": True, "no_warnings": True,
            "listsubtitles": False, "extract_flat": False}
    missing_all = []
    print(f"{'영상':<15} {'올라간 수동자막':<26} 누락")
    print("-" * 62)
    with yt_dlp.YoutubeDL(opts) as ydl:
        for wk, ed, vid in VIDEOS:
            tag = f"{wk} {ed}"
            if not vid:
                print(f"·  {tag:<13} (업로드 기록 없음)")
                continue
            try:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
            except Exception as e:
                print(f"★ {tag:<13} 조회실패: {str(e)[:36]}")
                continue
            subs = info.get("subtitles") or {}          # 수동 업로드 자막만
            have = norm(subs.keys())
            miss = [w for w in WANT if w not in have]
            mark = "OK" if not miss else "★ "
            print(f"{mark} {tag:<13} {','.join(sorted(have)) or '(없음)':<26} {','.join(miss) if miss else '-'}")
            if miss:
                missing_all.append((wk, ed, vid, miss))
    print("-" * 62)
    if missing_all:
        print(f"\n★누락 {len(missing_all)}개 영상:")
        for wk, ed, vid, m in missing_all:
            print(f"   {wk} {ed} ({vid}) → 없는 자막: {', '.join(m)}")
    else:
        print("\n전 영상 ko/en/ja/zh/es 5개 자막 완비 ✅")


if __name__ == "__main__":
    main()
