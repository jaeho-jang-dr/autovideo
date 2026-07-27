# -*- coding: utf-8 -*-
"""★자막 SRT에 로마자 발음기호 추가 (사장님 확정 원칙, 2026-07-14 / 발음규칙 2026-07-27)
   자모:  'ㅏ' [a]                       — 한글 + 로마자 발음
   단어:  '오른쪽' [o-reun-jjok] (뜻)     — 한글 + 발음 + 뜻
   문장:  '어떻게 가요?' (뜻)             — 한글 + 뜻

★2026-07-27 사장님 지시 — **실제 발음(표준 발음법) 표기**로 전환.
   철자 그대로 음절을 끊어 적던 방식은 학습자가 잘못 읽는다:
     좋은 경험이었어요  (X) jot-eun-gyeong-heom-i-eot-eo-yo
                        (O) jo-eun gyeong-heo-mi-eo-sseo-yo
   연음·ㅎ탈락·격음화·경음화·비음화·유음화·구개음화·겹받침을 적용한 뒤 로마자로 옮긴다.
   어절(띄어쓰기)은 공백으로 나누고 음절은 하이픈으로 잇는다.

⚠️ 나레이션과 자막이 같은 텍스트를 쓰므로, DB가 아니라 **SRT에만** 발음을 넣는다
   (DB에 넣으면 TTS가 로마자를 읽어버림).

사용: python add_pron_to_srt.py <입력.srt> <출력.srt>
"""
import sys, re, os

# 국립국어원 로마자 표기(간이) — 낱자(자모) 단독 표기용
JAMO_ROM = {
    "ㅏ": "a", "ㅑ": "ya", "ㅓ": "eo", "ㅕ": "yeo", "ㅗ": "o", "ㅛ": "yo",
    "ㅜ": "u", "ㅠ": "yu", "ㅡ": "eu", "ㅣ": "i", "ㅐ": "ae", "ㅒ": "yae",
    "ㅔ": "e", "ㅖ": "ye", "ㅘ": "wa", "ㅙ": "wae", "ㅚ": "oe", "ㅝ": "wo",
    "ㅞ": "we", "ㅟ": "wi", "ㅢ": "ui",
    "ㄱ": "g", "ㄴ": "n", "ㄷ": "d", "ㄹ": "r", "ㅁ": "m", "ㅂ": "b",
    "ㅅ": "s", "ㅇ": "ng", "ㅈ": "j", "ㅊ": "ch", "ㅋ": "k", "ㅌ": "t",
    "ㅍ": "p", "ㅎ": "h", "ㄲ": "kk", "ㄸ": "tt", "ㅃ": "pp", "ㅆ": "ss", "ㅉ": "jj",
}

CHO_L = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
JUNG_L = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ")
JONG_L = [""] + list("ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ")

# 초성 자리 로마자(모음 앞) / 종성 자리 로마자(7종성)
CHO_ROM = {"ㄱ": "g", "ㄲ": "kk", "ㄴ": "n", "ㄷ": "d", "ㄸ": "tt", "ㄹ": "r",
           "ㅁ": "m", "ㅂ": "b", "ㅃ": "pp", "ㅅ": "s", "ㅆ": "ss", "ㅇ": "",
           "ㅈ": "j", "ㅉ": "jj", "ㅊ": "ch", "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "h"}
JUNG_ROM = {"ㅏ": "a", "ㅐ": "ae", "ㅑ": "ya", "ㅒ": "yae", "ㅓ": "eo", "ㅔ": "e",
            "ㅕ": "yeo", "ㅖ": "ye", "ㅗ": "o", "ㅘ": "wa", "ㅙ": "wae", "ㅚ": "oe",
            "ㅛ": "yo", "ㅜ": "u", "ㅝ": "wo", "ㅞ": "we", "ㅟ": "wi", "ㅠ": "yu",
            "ㅡ": "eu", "ㅢ": "ui", "ㅣ": "i"}
JONG_ROM = {"": "", "ㄱ": "k", "ㄴ": "n", "ㄷ": "t", "ㄹ": "l", "ㅁ": "m", "ㅂ": "p", "ㅇ": "ng"}

# 겹받침 → (남는 받침, 뒤로 넘어가는 자음)
DOUBLE = {"ㄳ": ("ㄱ", "ㅅ"), "ㄵ": ("ㄴ", "ㅈ"), "ㄶ": ("ㄴ", "ㅎ"),
          "ㄺ": ("ㄹ", "ㄱ"), "ㄻ": ("ㄹ", "ㅁ"), "ㄼ": ("ㄹ", "ㅂ"),
          "ㄽ": ("ㄹ", "ㅅ"), "ㄾ": ("ㄹ", "ㅌ"), "ㄿ": ("ㄹ", "ㅍ"),
          "ㅀ": ("ㄹ", "ㅎ"), "ㅄ": ("ㅂ", "ㅅ")}
# 받침 중화(음절의 끝소리 규칙, 7종성)
NEUTRAL = {"ㄲ": "ㄱ", "ㅋ": "ㄱ", "ㄳ": "ㄱ", "ㄺ": "ㄱ",
           "ㅅ": "ㄷ", "ㅆ": "ㄷ", "ㅈ": "ㄷ", "ㅊ": "ㄷ", "ㅌ": "ㄷ", "ㅎ": "ㄷ",
           "ㅍ": "ㅂ", "ㅄ": "ㅂ", "ㄿ": "ㅂ",
           "ㄵ": "ㄴ", "ㄶ": "ㄴ", "ㄻ": "ㅁ",
           "ㄼ": "ㄹ", "ㄽ": "ㄹ", "ㄾ": "ㄹ", "ㅀ": "ㄹ"}
TENSE = {"ㄱ": "ㄲ", "ㄷ": "ㄸ", "ㅂ": "ㅃ", "ㅅ": "ㅆ", "ㅈ": "ㅉ"}   # 경음화
ASPIR = {"ㄱ": "ㅋ", "ㄷ": "ㅌ", "ㅂ": "ㅍ", "ㅈ": "ㅊ"}              # 격음화
NASAL = {"ㄱ": "ㅇ", "ㄷ": "ㄴ", "ㅂ": "ㅁ"}                          # 비음화


def decompose(ch):
    """가~힣 → [초성, 중성, 종성]. 아니면 None."""
    code = ord(ch)
    if not (0xAC00 <= code <= 0xD7A3):
        return None
    idx = code - 0xAC00
    return [CHO_L[idx // 588], JUNG_L[(idx % 588) // 28], JONG_L[idx % 28]]


def pronounce(syls):
    """음절 [초,중,종] 목록에 표준 발음법을 적용해 실제 소리로 바꾼다(어절 단위)."""
    for i in range(len(syls) - 1):
        cur, nxt = syls[i], syls[i + 1]
        jong, cho = cur[2], nxt[0]
        if not jong:
            continue

        # ── 1) 뒤 음절이 'ㅇ'(무음) → 연음 / ㅎ탈락 / 구개음화 ──
        if cho == "ㅇ":
            if jong == "ㅇ":                       # 여행을 → 여행을 (ㅇ은 안 넘어감)
                continue
            if jong == "ㅎ":                       # 좋은 → 조은
                cur[2] = ""
            elif jong in DOUBLE:
                a, b = DOUBLE[jong]
                if b == "ㅎ":                      # 많아 → 마나 / 싫어 → 시러
                    cur[2] = ""
                    nxt[0] = a
                else:                              # 읽어 → 일거 / 앉아 → 안자
                    cur[2] = a
                    # 표준발음법 14항 — 넘어가는 ㅅ은 된소리로: 없어→업써, 몫이→목씨
                    nxt[0] = "ㅆ" if b == "ㅅ" else b
            elif jong in ("ㄷ", "ㅌ") and nxt[1] == "ㅣ":   # 구개음화: 굳이→구지, 같이→가치
                nxt[0] = "ㅈ" if jong == "ㄷ" else "ㅊ"
                cur[2] = ""
            else:                                  # 경험이 → 경허미 / 있어 → 이써
                nxt[0] = jong
                cur[2] = ""
            continue

        # ── 2) 격음화 (ㅎ + 예사소리 / 예사소리 + ㅎ) ──
        if jong in ("ㅎ", "ㄶ", "ㅀ"):
            if cho in ASPIR:                       # 좋고 → 조코 / 않다 → 안타
                nxt[0] = ASPIR[cho]
                if nxt[0] == "ㅌ" and nxt[1] == "ㅣ":       # 굳히다류 → 구치다
                    nxt[0] = "ㅊ"
                cur[2] = "" if jong == "ㅎ" else DOUBLE[jong][0]
                continue
            if cho == "ㅅ":                        # 좋습니다 → 조씀니다
                nxt[0] = "ㅆ"
                cur[2] = "" if jong == "ㅎ" else DOUBLE[jong][0]
                continue
            if cho == "ㄴ":                        # 좋네 → 존네 / 않네 → 안네
                cur[2] = "ㄴ" if jong != "ㅀ" else "ㄹ"
                continue
        if cho == "ㅎ":
            a, b = DOUBLE.get(jong, ("", jong))    # ㄺ→(ㄹ,ㄱ) 처럼 뒤 자음이 ㅎ와 만난다
            base = NEUTRAL.get(b, b)
            if base in ASPIR:                      # 축하 → 추카 / 입학 → 이팍 / 앉히 → 안치
                nxt[0] = ASPIR[base]
                cur[2] = a
                continue

        # ── 3) 받침 중화 → 자음동화 → 경음화 ──
        base = NEUTRAL.get(jong, jong)
        if jong == "ㄺ" and cho == "ㄱ":            # 읽고 → 일꼬 (ㄺ은 ㄱ 앞에서 ㄹ, 뒤는 된소리)
            cur[2] = "ㄹ"
            nxt[0] = "ㄲ"
            continue
        if base in NASAL and cho in ("ㄴ", "ㅁ"):   # 비음화: 있는→인는, 학년→항년
            base = NASAL[base]
        elif base in NASAL and cho == "ㄹ":         # 백로 → 뱅노
            base = NASAL[base]
            nxt[0] = "ㄴ"
        elif base in ("ㅁ", "ㅇ") and cho == "ㄹ":  # 담력 → 담녁
            nxt[0] = "ㄴ"
        elif base == "ㄴ" and cho == "ㄹ":          # 유음화: 신라 → 실라
            base = "ㄹ"
        elif base == "ㄹ" and cho == "ㄴ":          # 설날 → 설랄
            nxt[0] = "ㄹ"
        elif base in ("ㄱ", "ㄷ", "ㅂ") and cho in TENSE:   # 경음화: 학교 → 학꾜
            nxt[0] = TENSE[cho]
        cur[2] = base

    if syls:                                        # 마지막 받침도 중화(맛 → 맏 → mat)
        syls[-1][2] = NEUTRAL.get(syls[-1][2], syls[-1][2])
        if syls[-1][2] in DOUBLE:                   # 겹받침 홀로 끝나면 대표음
            syls[-1][2] = DOUBLE[syls[-1][2]][0]
    return syls


def rom_eojeol(word):
    """어절 하나(공백 없는 한글 덩어리) → 실제 발음 로마자, 음절은 하이픈."""
    syls, out = [], []
    for ch in word:
        d = decompose(ch)
        if d:
            syls.append(d)
        elif ch in JAMO_ROM:
            syls.append(None)                       # 낱자 섞임 — 아래에서 따로 처리
    if not syls or any(s is None for s in syls):    # 낱자만/섞임 → 낱자 표기로
        return "-".join(JAMO_ROM.get(c, c) for c in word if c.strip())
    pronounce(syls)
    for i, (cho, jung, jong) in enumerate(syls):
        c = CHO_ROM.get(cho, cho)
        if i > 0 and syls[i - 1][2] == "ㄹ" and cho == "ㄹ":   # ㄹㄹ → ll (실라 sil-la)
            c = "l"
        out.append(c + JUNG_ROM.get(jung, jung) + JONG_ROM.get(jong, ""))
    return "-".join(o for o in out if o)


def romanize(text):
    """한글 단어/구 → 실제 발음 로마자. 어절은 공백, 음절은 하이픈."""
    words = [w for w in re.split(r"\s+", text.strip()) if w]
    return " ".join(r for r in (rom_eojeol(w) for w in words) if r)


ROM_RE = r"\[[a-z\- ]+\]"      # 발음기호 패턴(어절 사이 공백 포함)

# 따옴표 — 곧은('"), 굽은(‘’“”), 일본/중국 꺾쇠(「」『』) 모두 지원
QOPEN = "'\"‘“「『"
QCLOSE = "'\"’”」』"
QUOTE_PAT = re.compile(
    f"([{QOPEN}])([^{QOPEN}{QCLOSE}]*[가-힣ㄱ-ㅎㅏ-ㅣ][^{QOPEN}{QCLOSE}]*)([{QCLOSE}])"
)


def process_line(line):
    """따옴표 안 한글에 [발음] 추가. 이미 [..]가 붙어 있으면 건너뜀."""
    if "[" in line and re.search(ROM_RE, line):   # 이미 처리됨
        return line

    # ★조사/짧은 연결어는 발음기호를 붙이지 않는다(예: '112'와 '119' 사이 '와'가
    #   따옴표 짝에 잘못 잡혀 [wa]가 붙던 버그 방지). 사장님 지시 2026-07-23.
    PARTICLES = {"와", "과", "은", "는", "이", "가", "을", "를", "도", "에", "의",
                 "로", "으로", "나", "이나", "며", "고", "서", "만", "부터", "까지",
                 "에서", "에게", "한테", "보다", "처럼", "요"}

    def repl(m):
        q, inner, q2 = m.group(1), m.group(2), m.group(3)
        s = inner.strip()
        # ★조사 가드는 '오작동'일 때만 건다. 오작동은 따옴표가 짝이 어긋나 생기므로
        #   («'112'와 '119'» → 안쪽이 "와 ") 안쪽에 공백이 붙어 있다.
        #   반면 «drop the '요'» 처럼 조사를 **일부러** 인용한 것은 공백이 없다 —
        #   W17(반말·축약어)에선 '요'가 학습 대상이라 발음기호를 반드시 남긴다.
        if s in PARTICLES and inner != s:
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
    #   일본어판은 「」, 중국어판은 “”/「」를 쓴다 — 곧은따옴표만 보면 ja 자막의 발음기호가
    #   통째로 빠진다(2026-07-27 W21 ja 75→5 사고). 홑/겹·굽은·꺾쇠 따옴표를 모두 받는다.
    out = QUOTE_PAT.sub(repl, line)
    # ]뒤에 문자가 바로 붙으면 공백 삽입 (구두점 앞에는 넣지 않음 — 전각 구두점 포함)
    out = re.sub(r"(" + ROM_RE + r")(?=[^\s.,!?)\]、。，、！？）」』])", r"\1 ", out)
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
    n = len(re.findall(ROM_RE, t))
    print(f"{dst}: 발음기호 {n}개 추가")


if __name__ == "__main__":
    main()
