#!/bin/bash
# ★★ 다국어 자막 생성 (범용) — 사장님 원칙(2026-07-14):
#    모든 외국어 자막(ja/zh/es)에 **한글 원문을 그대로 두고** 그 나라 뜻/발음을 병기한다.
#    (일본어에서 한글이 통째로 사라져 학습이 안 되던 문제 수정)
# 사용: bash make_subs.sh <PREFIX> <PKG>
#   예: bash make_subs.sh hangeul_w14_madam hangeul_birth_vowels/w14pkg
cd /d/Entertainments/DevEnvironment/autovideo
export PYTHONIOENCODING=utf-8
PREFIX="${1:?PREFIX 필요}"
PKG="${2:?PKG 필요}"
SRC_KO="hangeul_birth_vowels/${PREFIX}_np.ko.srt"
SRC_EN="hangeul_birth_vowels/${PREFIX}_np.en.srt"
mkdir -p "$PKG" logs
LOG="logs/subs_$(basename $PKG).log"; : > "$LOG"

# 동영상 언어 자막 그대로
cp "$SRC_KO" "$PKG/ko_ko.srt"
cp "$SRC_EN" "$PKG/en_en.srt"
cp "$SRC_EN" "$PKG/ko_en.srt"
cp "$SRC_KO" "$PKG/en_ko.srt"

declare -A LANGS=( [ja]="Japanese" [zh]="Simplified Chinese" [es]="Spanish" )
# ★사장님 원칙: 한글 + 발음 + 뜻을 **전부** 넣는다(친절하게).
declare -A HINT=(
  [ja]="Format: '오른쪽' (オルンチョク = 右)  — Hangeul, then KATAKANA pronunciation, then the Japanese meaning."
  [zh]="Format: '오른쪽' (欧伦秋 = 右边)  — Hangeul, then the pronunciation written in Chinese characters (approximate sound), then the Chinese meaning."
  [es]="Format: '오른쪽' (o-reun-chok = derecha)  — Hangeul, then romanized pronunciation with hyphens, then the Spanish meaning."
)

for code in ja zh es; do
  name="${LANGS[$code]}"
  echo "[번역] $code ($name)" | tee -a "$LOG"
  raw="$PKG/_raw_$code.srt"
  cat "$SRC_EN" | gemini -m gemini-2.5-flash --yolo \
"Translate this SRT subtitle file into $name.

⚠️ CRITICAL RULE — this is a Korean-language teaching video. Be maximally helpful to the learner:
1. KEEP every Korean word or phrase written in Hangeul EXACTLY AS-IS. Do NOT translate them away, do NOT replace them with kanji/hanzi, do NOT remove them.
2. After EACH Korean expression, ADD BOTH (a) its PRONUNCIATION and (b) its MEANING, in parentheses.
   ${HINT[$code]}
   Always give BOTH pronunciation AND meaning — never just one.
3. Translate ONLY the surrounding explanation sentences into $name.
4. Keep the exact same block count, numbering and timestamps.

Example (English source -> $name target):
  Source:  Today's key word: '오른쪽' — right.
  CORRECT: keeps '오른쪽' in Hangeul + pronunciation + meaning, per the format above.
  WRONG:   removes the Hangeul, or gives only the meaning without the pronunciation.

Output the SRT only — no code fences, no commentary." \
    2>>"$LOG" | grep -v '^```' > "$raw"

  python scratch/rebuild_srt2.py "$SRC_EN" "$raw" "$PKG/en_$code.srt" >> "$LOG" 2>&1 || cp "$raw" "$PKG/en_$code.srt"
  cp "$PKG/en_$code.srt" "$PKG/ko_$code.srt"

  # ★검증: 한글이 실제로 남아 있나 (영어 SRT의 60% 이상이어야 정상)
  hen=$(grep -c '[가-힣]' "$SRC_EN")
  hxx=$(grep -c '[가-힣]' "$PKG/en_$code.srt")
  n=$(grep -c ' --> ' "$PKG/en_$code.srt")
  echo "  → $code: $n 블록 / 한글 포함 $hxx 줄 (영어판 $hen 줄)" | tee -a "$LOG"
  if [ "$hxx" -lt $((hen * 6 / 10)) ]; then
    echo "  ⚠️ 경고: $code 자막에 한글이 너무 적다 → 재번역 필요!" | tee -a "$LOG"
  fi
done

echo "" | tee -a "$LOG"
echo "=== 생성된 자막 (한글 포함 줄 수) ===" | tee -a "$LOG"
for f in "$PKG"/ko_*.srt "$PKG"/en_*.srt; do
  [ -f "$f" ] && echo "  $(basename $f): $(grep -c ' --> ' $f) 블록 / 한글 $(grep -c '[가-힣]' $f) 줄" | tee -a "$LOG"
done
rm -f "$PKG"/_raw_*.srt
