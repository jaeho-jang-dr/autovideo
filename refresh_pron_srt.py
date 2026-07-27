# -*- coding: utf-8 -*-
"""★기존 SRT의 로마자 발음기호를 최신 규칙(표준 발음법)으로 갱신 (2026-07-27)

철자 그대로 끊어 적던 옛 표기 → 실제 발음 표기로 교체한다.
  '좋은 경험이었어요' [jot-eun-gyeong-heom-i-eot-eo-yo]
    → '좋은 경험이었어요' [jo-eun gyeong-heo-mi-eo-sseo-yo]

이미 렌더가 끝난 W17~W22 자막을 다시 만들 때 쓴다(영상 재렌더 불필요 — 소프트자막이므로
자막 트랙만 다시 먹이면 된다). 원본은 <파일>.bak 으로 남긴다.

사용: python refresh_pron_srt.py <파일1.srt> [파일2.srt ...]
      python refresh_pron_srt.py --dry <파일.srt>      # 바뀌는 줄만 보여주고 저장 안 함
"""
import sys, re, os, shutil
import add_pron_to_srt as pron

# 소문자 로마자 대괄호만 제거 — 옛 표기엔 '?'·'~'가 섞여 들어간 것도 있다([ye-yak-haet-eo-yo-?]).
# 대문자·한글이 든 대괄호(고유명사 [Hallasan] 등)는 건드리지 않는다.
OLD_ROM = re.compile(r"\s*\[[a-z~][a-z\-~?!., ]*\]")


def refresh(path, dry=False):
    src = open(path, encoding="utf-8").read().splitlines()
    out, changed = [], []
    for ln in src:
        if re.match(r"^\d+$", ln) or " --> " in ln or not ln.strip():
            out.append(ln)
            continue
        stripped = OLD_ROM.sub("", ln)                     # 옛 발음기호 제거
        stripped = re.sub(r"\s{2,}", " ", stripped).strip()
        new = pron.process_line(stripped)
        new = re.sub(r"(\[[a-z][a-z\- ]*\])\s*\[([A-Z][A-Za-z]*)\]", r"\1 (\2)", new)
        new = re.sub(r"\s+\)", ")", re.sub(r"\(\s+", "(", new))
        out.append(new)
        if new != ln:
            changed.append((ln, new))

    n = len(re.findall(pron.ROM_RE, "\n".join(out)))
    print(f"\n=== {os.path.basename(path)} — 발음기호 {n}개 · 바뀐 줄 {len(changed)}개 ===")
    for old, new in changed[:200]:
        print(f"  - {old}\n  + {new}")
    if dry:
        print("  (dry-run — 저장 안 함)")
        return
    if not os.path.exists(path + ".bak"):
        shutil.copy(path, path + ".bak")
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"  → 저장 완료 (원본 {os.path.basename(path)}.bak)")


def main():
    args = sys.argv[1:]
    dry = "--dry" in args
    files = [a for a in args if a != "--dry"]
    if not files:
        print(__doc__)
        sys.exit(1)
    for f in files:
        refresh(f, dry)


if __name__ == "__main__":
    main()
