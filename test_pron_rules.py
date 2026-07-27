# -*- coding: utf-8 -*-
"""add_pron_to_srt.romanize 회귀 테스트 — 표준 발음법 규칙별 케이스.

자막 발음기호는 철자가 아니라 **실제 발음**이어야 한다(2026-07-27 사장님 지시).
규칙을 손볼 때마다 이걸 돌려서 기존 케이스가 깨지지 않는지 확인한다.

사용: python test_pron_rules.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from add_pron_to_srt import romanize

CASES = [
    # (한글, 기대 로마자, 규칙)
    ("좋은 경험이었어요", "jo-eun gyeong-heo-mi-eo-sseo-yo", "ㅎ탈락+연음"),
    ("할 계획이에요", "hal gye-hoe-gi-e-yo", "연음"),
    ("경험", "gyeong-heom", "기본"),
    ("계획", "gye-hoek", "기본"),
    ("여행", "yeo-haeng", "기본"),
    ("여행을 가다", "yeo-haeng-eul ga-da", "ㅇ받침 유지"),
    ("명소", "myeong-so", "기본"),
    ("예약", "ye-yak", "기본"),
    ("가 본 적이 있어요", "ga bon jeo-gi i-sseo-yo", "연음"),
    ("오른쪽", "o-reun-jjok", "기본"),
    ("학교", "hak-kkyo", "경음화"),
    ("학년", "hang-nyeon", "비음화"),
    ("있는", "in-neun", "비음화"),
    ("감사합니다", "gam-sa-ham-ni-da", "비음화"),
    ("반갑습니다", "ban-gap-sseum-ni-da", "경음화+비음화"),
    ("신라", "sil-la", "유음화"),
    ("설날", "seol-lal", "유음화"),
    ("축하", "chu-ka", "격음화"),
    ("좋고", "jo-ko", "격음화"),
    ("예약했어요", "ye-ya-kae-sseo-yo", "격음화+연음"),
    ("같이", "ga-chi", "구개음화"),
    ("굳이", "gu-ji", "구개음화"),
    ("읽어", "il-geo", "겹받침 연음"),
    ("읽고", "il-kko", "ㄺ+ㄱ"),
    ("많아", "ma-na", "ㄶ 연음"),
    ("싫어", "si-reo", "ㅀ 연음"),
    ("앉아", "an-ja", "ㄵ 연음"),
    ("없어요", "eop-sseo-yo", "14항 ㅅ→ㅆ"),
    ("몫이", "mok-ssi", "14항 ㅅ→ㅆ"),
    ("값이", "gap-ssi", "14항 ㅅ→ㅆ"),
    ("맛", "mat", "중화"),
    ("꽃", "kkot", "중화"),
    ("한국", "han-guk", "기본"),
    ("한국어", "han-gu-geo", "연음"),
    ("서울", "seo-ul", "기본"),
    ("주말에", "ju-ma-re", "연음"),
]


def main():
    bad = []
    for ko, want, rule in CASES:
        got = romanize(ko)
        if got != want:
            bad.append((ko, got, want, rule))
        print(f"{'OK ' if got == want else 'XX '}{ko:<12} {got:<28} [{rule}]")
    print(f"\n{len(CASES) - len(bad)}/{len(CASES)} 통과")
    if bad:
        print("\n실패:")
        for ko, got, want, rule in bad:
            print(f"  {ko} ({rule}): got={got} want={want}")
        sys.exit(1)


if __name__ == "__main__":
    main()
