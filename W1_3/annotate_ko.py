# -*- coding: utf-8 -*-
"""W1-3 자막 발음/뜻 주석 — [[subtitle-romanization-rule]] 관례:
   자모 'ㅏ' [a] / 단어 '오른쪽' [o-reun-jjok] (뜻) 처럼 인용부호 뒤에 '[발음]'을,
   뜻이 있으면 이어서 '(뜻)'을 붙인다. `W1_2/build_ko_v4.py`의 mark_words() 단일-단어
   버전을 여러 개 토큰을 순서대로 처리하도록 확장했다(원본 로직은 그대로 계승).
"""
import re


def _mark_one(text, surface, pron, meaning=None):
    """text 안에서 surface의 첫 등장(인용부호 포함 또는 평문)을 찾아 뒤에
    ' [pron]'(및 있으면 ' (meaning)')을 붙인다. 이미 주석이 붙어 있으면 건너뛴다."""
    tag = " [%s]" % pron
    if meaning:
        tag += " (%s)" % meaning

    # 이미 이 표면형에 주석이 붙어 있으면 중복 방지
    if (surface + tag) in text:
        return text

    # 1) 인용부호 형태 — 'surface(꼬리 문장부호 허용)'
    m = re.search(r"'%s[^']*'" % re.escape(surface), text)
    if m:
        return text[:m.end()] + tag + text[m.end():]

    # 2) 평문 형태 — 첫 등장 뒤에 삽입
    idx = text.find(surface)
    if idx == -1:
        return text
    end = idx + len(surface)
    return text[:end] + tag + text[end:]


def annotate(text, tokens):
    """tokens: [(surface, pron, meaning_or_None), ...] 순서대로 적용."""
    for surface, pron, meaning in tokens:
        text = _mark_one(text, surface, pron, meaning)
    return text


# 씬별 주석 토큰 — §3(8모음 대조표) · §6(자막 5개국어 발음기호) · §5(낱말 뜻) 반영.
# 과잉주석 방지 — 씬마다 그 씬에서 실제로 처음 등장하는 것만 단다.
ANNOTATE_TOKENS = {
    "S01": [("아이", "a-i", None), ("오이", "o-i", None), ("아우", "a-u", None)],
    "S04": [("ㅏ", "a", None)],
    "S05": [("ㅏ", "a", None), ("ㅓ", "eo", None), ("ㅣ", "i", None),
            ("ㅐ", "ae", None), ("ㅔ", "e", None),
            ("ㅗ", "o", None), ("ㅜ", "u", None), ("ㅡ", "eu", None)],
    "S06": [("아이", "a-i", None)],
    "S07": [("오이", "o-i", None)],
    "S08": [("아우", "a-u", None)],
    "S09": [("오", "o", None), ("이", "i", None)],
    "S10": [("ㅗ", "o", None)],
    "S11": [("강", "gang", None), ("방", "bang", None)],
    "S12": [("아", "a", None), ("오", "o", None), ("우", "u", None)],
    "S13": [("어", "eo", None), ("ㅓ", "eo", None), ("으차", "eu-cha", None), ("ㅡ", "eu", None)],
    "S14": [("ㅔ", "e", None)],
    "S15": [("우유", "u-yu", None)],
    "S16": [("이유", "i-yu", None)],  # 뜻(까닭)은 바로 뒤 나레이션이 직접 설명 — 중복 방지
    "S17": [("여우", "yeo-u", None), ("여유", "yeo-yu", None)],  # 뜻(느긋함)도 동일
    "S19": [("우", "u", None), ("애", "ae", None), ("우애", "u-ae", None)],
    "S20": [("아우", "a-u", None)],
    "S21": [("이유", "i-yu", None), ("여유", "yeo-yu", None), ("우애", "u-ae", None)],
}


def annotate_scene(scene_id, text):
    return annotate(text, ANNOTATE_TOKENS.get(scene_id, []))


if __name__ == "__main__":
    from narration_ko import NARR_KO, SCENE_ORDER
    for s in SCENE_ORDER:
        print(s, "=>", annotate_scene(s, NARR_KO[s]))
