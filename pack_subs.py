# -*- coding: utf-8 -*-
"""★자막 업로드 패키지 만들기 (사장님이 유튜브 UI로 직접 올리심 — API 4,000유닛 절약)

한 폴더에 **5개 자막을 유튜브 자막 언어명 그대로** 모아준다:
    subs_upload/W14_1_한글판/  한국어.srt  영어.srt  일본어.srt  중국어(중국).srt  스페인어.srt
    subs_upload/W14_2_영어판/  (동일 5개)

ko/en 은 렌더 산출물(hangeul_birth_vowels/*.ko.srt/.en.srt),
ja/zh/es 는 번역본(scratch/fixed_subs/<주차>/…)에서 가져온다.

사용:
    python pack_subs.py W14 hangeul_w14_madam_np      # 한 주차
    python pack_subs.py --all                          # W1~W13 기존분 전부
"""
import os, re, sys, glob, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
HB = os.path.join(ROOT, "hangeul_birth_vowels")
TRANS = os.path.join(ROOT, "scratch", "fixed_subs")
OUT = os.path.join(ROOT, "subs_upload")

# 유튜브 자막 UI에 뜨는 언어명 그대로
YT = {"ko": "한국어", "en": "영어", "ja": "일본어", "zh": "중국어(중국)", "es": "스페인어"}

# 주차별 렌더 산출물 prefix (ko/en srt 파일명)
PREFIX = {
    "W01": "hangeul_w1_stickman_np", "W02": "hangeul_w2_stickman_np",
    "W03": "hangeul_w3_stickman_np", "W04": "hangeul_w4_stickman_np",
    "W05": "hangeul_w5_stickman_np", "W06": "hangeul_w6_stickman_np",
    "W07": "hangeul_w7_stickman_np", "W08": "hangeul_w8_stickman_np",
    "W09": "hangeul_w9v2_stickman_np", "W10": "hangeul_w10_injun_np",
    "W11": "hangeul_w11_madam_np", "W12": "hangeul_w12_injun_np",
    "W13": "hangeul_w13_jieun_np", "W14": "hangeul_w14_madam_np",
}


def pack(week, prefix=None):
    prefix = prefix or PREFIX.get(week)
    if not prefix:
        print(f"  {week}: prefix 모름 — 건너뜀"); return
    n_ok = 0
    for ed, ord_ in (("한글판", 1), ("영어판", 2)):
        dst = os.path.join(OUT, f"{week}_{ord_}_{ed}")
        os.makedirs(dst, exist_ok=True)
        got = []
        # ① ko / en — 렌더 산출물
        for code in ("ko", "en"):
            src = os.path.join(HB, f"{prefix}.{code}.srt")
            if os.path.exists(src):
                shutil.copy(src, os.path.join(dst, f"{YT[code]}.srt")); got.append(code)
        # ② ja / zh / es — 번역본
        #    ①scratch/fixed_subs/<주차>_<n>_<판>/<언어명>.srt (W1~W14 방식)
        #    ②hangeul_birth_vowels/w<NN>pkg/<prefix>.<code>.srt (W20+ translate_srt_wNN.py 산출)
        tdir = os.path.join(TRANS, f"{week}_{ord_}_{ed}")
        pdir = os.path.join(HB, f"w{int(week[1:]):d}pkg")
        for code in ("ja", "zh", "es"):
            for src in (os.path.join(tdir, f"{YT[code]}.srt"),
                        os.path.join(pdir, f"{prefix}.{code}.srt")):
                if os.path.exists(src):
                    shutil.copy(src, os.path.join(dst, f"{YT[code]}.srt")); got.append(code)
                    break
        miss = [c for c in YT if c not in got]
        mark = "OK" if not miss else "★"
        print(f"  {mark} {week}_{ord_}_{ed:<4} {len(got)}/5  " +
              (f"누락: {','.join(YT[m] for m in miss)}" if miss else ""))
        n_ok += len(got) == 5
    return n_ok


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if "--all" in sys.argv:
        weeks = [w for w in sorted(PREFIX) if w != "W14"]
        print("=== 기존 주차 전부 패키징 ===")
        for w in weeks:
            pack(w)
    else:
        w = (sys.argv[1] if len(sys.argv) > 1 else "W14").upper()
        p = sys.argv[2] if len(sys.argv) > 2 else None
        print(f"=== {w} 자막 패키징 ===")
        pack(w, p)
    print(f"\n→ 업로드 폴더: {OUT}")
