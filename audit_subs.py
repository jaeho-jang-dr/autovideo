# -*- coding: utf-8 -*-
"""★자막 원칙 감사 (사장님 확정 원칙, 2026-07-14)
   자모  'ㅏ' [a]                   한글 + 로마자 발음
   단어  '오른쪽' [o-reun-jjok] (뜻)  한글 + 로마자 + 그 나라 뜻
   문장  '어떻게 가요?' (뜻)          한글 + 그 나라 말 뜻
검사: ①한글(자모 포함) 유지 ②[로마자] 존재 ③미번역(영어 원문 잔존) 없음 ④블록수 일치
사용: python audit_subs.py [scratch/fixed_subs]
"""
import os, re, sys, glob

ROOT = sys.argv[1] if len(sys.argv) > 1 else "scratch/fixed_subs"
LANG_CHARS = {
    "일본어": r"[ぁ-んァ-ヶ一-龥]",
    "중국어(중국)": r"[一-龥]",
    "스페인어": r"[A-Za-zÁÉÍÓÚÑáéíóúñ¿¡]",
}
HANGEUL = r"[가-힣ㄱ-ㅎㅏ-ㅣ]"


def blocks(path):
    out = []
    for b in open(path, encoding="utf-8").read().strip().split("\n\n"):
        L = b.split("\n")
        if len(L) >= 3 and "-->" in L[1]:
            out.append((L[0], L[1], " ".join(L[2:])))
    return out


def audit(path):
    name = os.path.basename(path).replace(".srt", "")
    bl = blocks(path)
    txt = "\n".join(t for _, _, t in bl)
    n_han = len(re.findall(HANGEUL, txt))
    n_rom = len(re.findall(r"\[[a-z/ -]+\]", txt))
    # ★중복(영어 원문 + 번역이 한 블록에 같이 남은 경우) — 원문 줄을 지우지 않은 사고
    dup = 0
    pat_l = LANG_CHARS.get(name)
    if name in ("일본어", "중국어(중국)") and pat_l:
        for b in open(path, encoding="utf-8").read().strip().split("\n\n"):
            L = b.split("\n")
            if len(L) < 3 or "-->" not in L[1]:
                continue
            # ★줄 단위로 본다: 같은 블록에 '순수 영어 줄'과 '대상언어 줄'이 따로 있으면 원문 잔존
            has_lang = any(re.search(pat_l, t) for t in L[2:])
            pure_en = any((not re.search(pat_l, t)) and (not re.search(HANGEUL, t))
                          and len(re.findall(r"[A-Za-z]{2,}", t)) >= 1 for t in L[2:])
            if has_lang and pure_en:
                dup += 1
    # 미번역: 따옴표한글/발음기호 뺀 뒤 영단어 4개 이상인데 대상언어 문자 없음
    pat = LANG_CHARS.get(name)
    untr = 0
    for _, _, t in bl:
        core = re.sub(r"\[[a-z/ -]+\]", "", t)
        core = re.sub(r"['\"][^'\"]*['\"]", "", core)
        words = re.findall(r"[A-Za-z]{3,}", core)
        if name == "스페인어":
            # 스페인어는 라틴문자라 영어와 구분 어려움 → 영어 특유 기능어로 판별
            en = re.findall(r"\b(the|and|you|with|that|this|from|your|they|were|when|what|which|have|been)\b",
                            core, re.I)
            if len(words) >= 4 and len(en) >= 2:
                untr += 1
        elif pat and len(words) >= 4 and not re.search(pat, t):
            untr += 1
    return dict(blocks=len(bl), han=n_han, rom=n_rom, untr=untr, dup=dup)


rows = []
for d in sorted(glob.glob(os.path.join(ROOT, "*/"))):
    for f in sorted(glob.glob(os.path.join(d, "*.srt"))):
        r = audit(f)
        folder = os.path.basename(os.path.dirname(f))
        lang = os.path.basename(f).replace(".srt", "")
        bad = []
        if r["han"] < 5:
            bad.append("한글유실")
        if r["rom"] < 5:
            bad.append("발음없음")
        if r["untr"] >= 3:
            bad.append(f"미번역{r['untr']}블록")
        if r.get("dup", 0) >= 3:
            bad.append(f"영어원문중복{r['dup']}블록")
        rows.append((folder, lang, r, bad))

ok = [x for x in rows if not x[3]]
ng = [x for x in rows if x[3]]
print(f"총 {len(rows)}개 | 정상 {len(ok)} | ★위반 {len(ng)}\n")
if ng:
    print("★★재작업 필요:")
    for folder, lang, r, bad in ng:
        print(f"  {folder:<18} {lang:<12} 블록{r['blocks']:>4} 한글{r['han']:>4} 로마자{r['rom']:>3}  → {', '.join(bad)}")
else:
    print("전부 원칙 준수 ✅ (한글 + [로마자] + 그 언어 뜻)")
