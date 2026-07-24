#!/bin/bash
# ★W1~W12 다국어 자막(ja/zh/es) 일괄 재번역 — 한글 + 발음 + 뜻 전부 넣기(사장님 원칙)
# 결과는 scratch/fixed_subs/W##_한글판|영어판/ 에 언어별로 정리 → 사장님이 수동 업로드
cd /d/Entertainments/DevEnvironment/autovideo
export PYTHONIOENCODING=utf-8
OUT="scratch/fixed_subs"
LOG="logs/fix_all_subs.log"
mkdir -p "$OUT" logs
: > "$LOG"

declare -A HINT=(
  [ja]="Format: '오른쪽' (オルンチョク = 右) — Hangeul, then KATAKANA pronunciation, then the Japanese meaning."
  [zh]="Format: '오른쪽' (欧伦作 = 右边) — Hangeul, then pronunciation in Chinese characters (approximate sound), then the Chinese meaning."
  [es]="Format: '오른쪽' (o-reun-chok = derecha) — Hangeul, then romanized pronunciation with hyphens, then the Spanish meaning."
)
declare -A LNAME=( [ja]="Japanese" [zh]="Simplified Chinese" [es]="Spanish" )
declare -A YTNAME=( [ja]="일본어" [zh]="중국어(중국)" [es]="스페인어" )

translate() {   # $1=source_en_srt  $2=code  $3=out_srt
  local src="$1" code="$2" out="$3"
  local name="${LNAME[$code]}"
  local raw="${out}.raw"
  cat "$src" | gemini -m gemini-2.5-flash --yolo \
"Translate this SRT subtitle file into $name.

⚠️ CRITICAL — Korean-language teaching video. Be maximally helpful to the learner:
1. KEEP every Korean word/phrase in Hangeul EXACTLY AS-IS. Never remove it, never replace it with kanji/hanzi.
2. After EACH Korean expression add BOTH (a) PRONUNCIATION and (b) MEANING in parentheses.
   ${HINT[$code]}
   Always BOTH — never just one.
3. Translate only the surrounding explanation into $name.
4. Keep the exact same block count, numbering and timestamps.

Output SRT only — no code fences, no commentary." 2>>"$LOG" | grep -v '^```' > "$raw"
  python scratch/rebuild_srt2.py "$src" "$raw" "$out" >> "$LOG" 2>&1 || cp "$raw" "$out"
  rm -f "$raw"
}

# 주차별 (영어 원본 SRT, 한글판/영어판, 출력 폴더)
process() {   # $1=week $2=edition $3=base_en_srt
  local w="$1" ed="$2" src="$3"
  [ -f "$src" ] || { echo "  W$w $ed: 영어 자막 없음 ($src) — 스킵" | tee -a "$LOG"; return; }
  local d="$OUT/W$(printf %02d $w)_$ed"
  mkdir -p "$d"
  echo "=== W$w $ed (원본: $src) ===" | tee -a "$LOG"
  for code in ja zh es; do
    local o="$d/${YTNAME[$code]}.srt"
    [ -f "$o" ] && { echo "  $code: 이미 있음 스킵" | tee -a "$LOG"; continue; }
    echo "  [$code] 번역 중..." | tee -a "$LOG"
    translate "$src" "$code" "$o"
    local h=$(grep -c '[가-힣]' "$o" 2>/dev/null || echo 0)
    local b=$(grep -c ' --> ' "$o" 2>/dev/null || echo 0)
    echo "    → ${YTNAME[$code]}.srt : ${b}블록, 한글 ${h}줄" | tee -a "$LOG"
  done
}

HB="hangeul_birth_vowels"
# W1~W8 (stickman_np=영어판, kosub=한글판)
for w in 1 2 3 4 5 6 7 8; do
  process $w "영어판" "$HB/hangeul_w${w}_stickman_np.en.srt"
  process $w "한글판" "$HB/hangeul_w${w}_kosub.en.srt"
done
# W9~W12 (pkg)
for w in 9 10 11 12; do
  process $w "한글판" "$HB/w${w}pkg/ko_en.srt"
  process $w "영어판" "$HB/w${w}pkg/en_en.srt"
done

echo "" | tee -a "$LOG"
echo "=== 완료 — 결과 폴더 ===" | tee -a "$LOG"
find "$OUT" -name "*.srt" | sort | tee -a "$LOG"
