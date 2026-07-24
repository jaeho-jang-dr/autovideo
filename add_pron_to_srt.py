# -*- coding: utf-8 -*-
"""★자막 SRT에 로마자 발음기호 추가 (사장님 확정 원칙, 2026-07-14)
   자모:  'ㅏ' [a]                       — 한글 + 로마자 발음
   단어:  '오른쪽' [o-reun-jjok] (뜻)     — 한글 + 발음 + 뜻
   문장:  '어떻게 가요?' (뜻)             — 한글 + 뜻

⚠️ 나레이션과 자막이 같은 텍스트를 쓰므로, DB가 아니라 **SRT에만** 발음을 넣는다
   (DB에 넣으면 TTS가 로마자를 읽어버림).

사용: python add_pron_to_srt.py <입력.srt> <출력.srt>
"""
import sys, re, os

# 국립국어원 로마자 표기(간이) — 자모
JAMO_ROM = {
    "ㅏ": "a", "ㅑ": "ya", "ㅓ": "eo", "ㅕ": "yeo", "ㅗ": "o", "ㅛ": "yo",
    "ㅜ": "u", "ㅠ": "yu", "ㅡ": "eu", "ㅣ": "i", "ㅐ": "ae", "ㅒ": "yae",
    "ㅔ": "e", "ㅖ": "ye", "ㅘ": "wa", "ㅙ": "wae", "ㅚ": "oe", "ㅝ": "wo",
    "ㅞ": "we", "ㅟ": "wi", "ㅢ": "ui",
    "ㄱ": "g", "ㄴ": "n", "ㄷ": "d", "ㄹ": "r", "ㅁ": "m", "ㅂ": "b",
    "ㅅ": "s", "ㅇ": "ng", "ㅈ": "j", "ㅊ": "ch", "ㅋ": "k", "ㅌ": "t",
    "ㅍ": "p", "ㅎ": "h", "ㄲ": "kk", "ㄸ": "tt", "ㅃ": "pp", "ㅆ": "ss", "ㅉ": "jj",
}

CHO = ["g","kk","n","d","tt","r","m","b","pp","s","ss","","j","jj","ch","k","t","p","h"]
JUNG = ["a","ae","ya","yae","eo","e","yeo","ye","o","wa","wae","oe","yo","u","wo","we","wi","yu","eu","ui","i"]
JONG = ["","k","k","k","n","n","n","t","l","l","l","l","l","l","l","l","m","p","p","t","t","ng","t","t","k","t","p","t"]


def romanize(word):
    """한글 단어 → 로마자(음절 단위 하이픈). 간이 규칙."""
    out = []
    for ch in word:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            idx = code - 0xAC00
            cho = idx // 588
            jung = (idx % 588) // 28
            jong = idx % 28
            out.append(CHO[cho] + JUNG[jung] + JONG[jong])
        elif ch in JAMO_ROM:
            out.append(JAMO_ROM[ch])
        elif ch.strip():
            out.append(ch)
    return "-".join(o for o in out if o)


def process_line(line):
    """따옴표 안 한글에 [발음] 추가. 이미 [..]가 붙어 있으면 건너뜀."""
    if "[" in line and re.search(r"\[[a-z\-]+\]", line):   # 이미 처리됨
        return line

    # ★조사/짧은 연결어는 발음기호를 붙이지 않는다(예: '112'와 '119' 사이 '와'가
    #   따옴표 짝에 잘못 잡혀 [wa]가 붙던 버그 방지). 사장님 지시 2026-07-23.
    PARTICLES = {"와", "과", "은", "는", "이", "가", "을", "를", "도", "에", "의",
                 "로", "으로", "나", "이나", "며", "고", "서", "만", "부터", "까지",
                 "에서", "에게", "한테", "보다", "처럼", "요"}

    def repl(m):
        q, inner, q2 = m.group(1), m.group(2), m.group(3)
        s = inner.strip()
        if s in PARTICLES:                 # 조사만 따옴표에 잡힌 경우 → 원문 그대로(발음기호 X)
            return m.group(0)
        # 자모 하나 → 발음만(뜻 없음)
        if len(s) == 1 and s in JAMO_ROM:
            return f"{q}{inner}{q2} [{JAMO_ROM[s]}]"
        # 긴 문장(4어절 이상)은 발음 생략(가독성)
        if len(s.split()) >= 4:
            return m.group(0)
        rom = romanize(s)
        if not rom:
            return m.group(0)
        return f"{q}{inner}{q2} [{rom}]"

    # ★따옴표 안에 '한글이 실제로 들어있는' 것만 매칭 (영어 아포스트로피 Today's 등 회피)
    pat = re.compile(r"(['\"])([^'\"]*[가-힣ㄱ-ㅎㅏ-ㅣ][^'\"]*)(['\"])")
    out = pat.sub(repl, line)
    # ]뒤에 문자가 바로 붙으면 공백 삽입 (구두점 앞에는 넣지 않음)
    out = re.sub(r"(\[[a-z\-]+\])(?=[^\s.,!?)\]])", r"\1 ", out)
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    out = []
    for line in open(src, encoding="utf-8"):
        s = line.rstrip("\n")
        if re.match(r"^\d+$", s) or " --> " in s or not s.strip():
            out.append(s)
        else:
            out.append(process_line(s))
    open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n")
    # 통계
    t = open(dst, encoding="utf-8").read()
    n = len(re.findall(r"\[[a-z\-]+\]", t))
    print(f"{dst}: 발음기호 {n}개 추가")


if __name__ == "__main__":
    main()
