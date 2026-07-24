#!/bin/bash
# ★누락 자막 10개 완성 (2026-07-14)
#   W9 영어판(ja/zh/es) · W10 한글판(ja/zh/es) · W10 영어판(ja/zh/es) · W13 영어판(es)
#   ⚠️완료분(68개)은 절대 건드리지 않는다 — 이미 있는 srt는 skip.
# 표기 원칙(사장님 확정):
#   자모  'ㅏ' [a]                        — 한글 + 로마자 발음
#   단어  '오른쪽' [o-reun-jjok] (뜻)      — 한글 + 로마자 발음 + 그 나라 뜻
#   문장  '어떻게 가요?' (뜻)              — 한글 + 그 나라 말 뜻
#   ※발음기호는 항상 로마자(각국 문자 음차 금지 — ㅓ/ㅗ 구분 불가)
cd /d/Entertainments/DevEnvironment/autovideo
export PYTHONIOENCODING=utf-8
OUT="scratch/fixed_subs"
LOG="logs/fix_missing_subs.log"
mkdir -p "$OUT" logs
: > "$LOG"

declare -A LNAME=( [ja]="Japanese" [zh]="Simplified Chinese" [es]="Spanish" )
declare -A YTNAME=( [ja]="일본어" [zh]="중국어(중국)" [es]="스페인어" )
declare -A MEAN=( [ja]="Japanese meaning in parentheses, e.g. （右）" \
                  [zh]="Chinese meaning in parentheses, e.g. （右边）" \
                  [es]="Spanish meaning in parentheses, e.g. (derecha)" )

word_rule() {   # $1=lang name  $2=meaning hint   (W7+ = 단어·문장 강의)
cat <<EOF
⚠️ CRITICAL — Korean teaching video. Follow EXACTLY:

1. KEEP every Korean word/phrase in Hangeul EXACTLY as-is. NEVER remove it or replace it with kanji/hanzi/kana.
2. For each Korean WORD: '오른쪽' [o-reun-jjok] + $2
   → Hangeul, then ROMAN (English-letter) pronunciation in square brackets, then the meaning.
   ⚠️ Pronunciation must always be in ROMAN letters (never 汉字/カタカナ音写).
3. For each Korean SENTENCE: '어떻게 가요?' + $2   (meaning in $1; romanization optional for long sentences)
4. For a single Hangeul LETTER (jamo), write only 'ㅏ' [a] — no meaning.
5. Translate only the surrounding explanation into $1. Keep block count/numbering/timestamps identical.

Output SRT only — no code fences, no commentary.
EOF
}

translate() {   # $1=src_en_srt  $2=code  $3=out
  local src="$1" code="$2" out="$3"
  local name="${LNAME[$code]}" mean="${MEAN[$code]}"
  local rule; rule=$(word_rule "$name" "$mean")
  local raw="${out}.raw"
  cat "$src" | gemini -m gemini-2.5-flash --yolo \
"Translate this SRT subtitle file into $name.

$rule" 2>>"$LOG" | grep -v '^```' > "$raw"
  if [ ! -s "$raw" ]; then echo "    ✗ 번역 실패(빈 결과) — 재시도" | tee -a "$LOG"
    cat "$src" | gemini -m gemini-2.5-flash --yolo "Translate this SRT into $name.

$rule" 2>>"$LOG" | grep -v '^```' > "$raw"
  fi
  python scratch/rebuild_srt2.py "$src" "$raw" "$out" >> "$LOG" 2>&1 || cp "$raw" "$out"
  rm -f "$raw"
}

process() {   # $1=폴더명  $2=src_en
  local d="$OUT/$1" src="$2"
  [ -f "$src" ] || { echo "★원본 없음 스킵: $src" | tee -a "$LOG"; return; }
  mkdir -p "$d"
  echo "=== $1  (src: $(basename "$src")) ===" | tee -a "$LOG"
  for code in ja zh es; do
    local o="$d/${YTNAME[$code]}.srt"
    if [ -s "$o" ]; then echo "  [skip] ${YTNAME[$code]} 이미 있음" | tee -a "$LOG"; continue; fi
    echo "  [$code] 번역 중..." | tee -a "$LOG"
    translate "$src" "$code" "$o"
    local h b
    h=$(grep -c '[가-힣]' "$o" 2>/dev/null || echo 0)
    b=$(grep -c ' --> ' "$o" 2>/dev/null || echo 0)
    echo "    → ${YTNAME[$code]}.srt : ${b}블록, 한글 ${h}줄" | tee -a "$LOG"
  done
}

HB="hangeul_birth_vowels"
# W9 영어판 — 원본 = w9v2 EN(68블록/5:00, 영상 301초와 일치)
process "W09_2_영어판"  "$HB/hangeul_w9v2_stickman_np.en.srt"
# W10 한글판·영어판 — 원본 = w10 injun EN(49블록/4:17, 영상 260초와 일치)
process "W10_1_한글판"  "$HB/hangeul_w10_injun_np.en.srt"
process "W10_2_영어판"  "$HB/hangeul_w10_injun_np.en.srt"
# W13 영어판 — 스페인어만 누락(정전으로 실패). ja/zh는 skip됨
process "W13_2_영어판"  "$HB/hangeul_w13_jieun_np.en.srt"

echo "" | tee -a "$LOG"
echo "=== 완료 — 총 srt: $(find "$OUT" -name '*.srt' | wc -l) / 78 ===" | tee -a "$LOG"
