#!/bin/bash
# ★★W1~W13 다국어 자막 재번역 v2 — 사장님 확정 표기 원칙(2026-07-14)
#   자모(W1~W6): 한글 + [로마자 발음기호]              예) 'ㅏ' [a]
#   단어(W7~W13): 한글 + [로마자 발음] + 그 나라 뜻     예) '오른쪽' [o-reun-jjok] (右边)
#   문장:         한글 + 그 나라 말 뜻 설명            예) '어떻게 가요?' (怎么去?)
#   ※발음기호는 항상 영어(로마자) — 각국 문자 음차 금지(ㅓ/ㅗ 구분 안 됨)
cd /d/Entertainments/DevEnvironment/autovideo
export PYTHONIOENCODING=utf-8
OUT="scratch/fixed_subs"
LOG="logs/fix_all_subs2.log"
mkdir -p "$OUT" logs
: > "$LOG"

declare -A LNAME=( [ja]="Japanese" [zh]="Simplified Chinese" [es]="Spanish" )
declare -A YTNAME=( [ja]="일본어" [zh]="중국어(중국)" [es]="스페인어" )
declare -A MEAN=( [ja]="Japanese meaning in parentheses, e.g. （右）" \
                  [zh]="Chinese meaning in parentheses, e.g. （右边）" \
                  [es]="Spanish meaning in parentheses, e.g. (derecha)" )

# 자모 강의(W1~W6) 프롬프트
jamo_rule() {  # $1=lang name  $2=meaning hint
cat <<EOF
⚠️ CRITICAL — this is a Korean ALPHABET (Jamo) lesson. Follow EXACTLY:

1. KEEP every Hangeul letter/word EXACTLY as-is. NEVER replace it with kanji/hanzi/kana.
2. For each Hangeul LETTER (jamo like ㅏ ㅓ ㅗ ㅜ ㅡ ㅣ ㅐ ㅔ ㄱ ㄴ ㄷ …), write it as:
       'ㅏ' [a]
   → Hangeul in quotes, then the ROMAN (English-letter) phonetic value in square brackets.
   ⚠️ Do NOT add a "meaning" for a letter — letters have no meaning.
   ⚠️ Do NOT transliterate the sound into $1 characters (啊/ア/…) — it cannot distinguish ㅓ from ㅗ.
   Vowel romanization: ㅏ[a] ㅓ[eo] ㅗ[o] ㅜ[u] ㅡ[eu] ㅣ[i] ㅐ[ae] ㅔ[e] ㅑ[ya] ㅕ[yeo] ㅛ[yo] ㅠ[yu] ㅚ[oe] ㅟ[wi] ㅢ[ui] ㅘ[wa] ㅝ[wo] ㅖ[ye] ㅒ[yae]
   Consonant romanization: ㄱ[g] ㄴ[n] ㄷ[d] ㄹ[r/l] ㅁ[m] ㅂ[b] ㅅ[s] ㅇ[ng] ㅈ[j] ㅎ[h] ㅋ[k] ㅌ[t] ㅍ[p] ㅊ[ch] ㄲ[kk] ㄸ[tt] ㅃ[pp] ㅆ[ss] ㅉ[jj]
3. For a Hangeul WORD or SYLLABLE (e.g. 아기, 학교), write: '아기' [a-gi] + $2
4. For a Hangeul SENTENCE, write: '문장' + $2 (meaning only; romanization optional)
5. Translate only the surrounding explanation into $1. Keep block count/numbering/timestamps identical.

Output SRT only — no code fences, no commentary.
EOF
}

# 단어·문장 강의(W7~) 프롬프트
word_rule() {  # $1=lang name  $2=meaning hint
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

translate() {   # $1=src_en_srt  $2=code  $3=out  $4=week
  local src="$1" code="$2" out="$3" w="$4"
  local name="${LNAME[$code]}" mean="${MEAN[$code]}"
  local rule
  if [ "$w" -le 6 ]; then rule=$(jamo_rule "$name" "$mean"); else rule=$(word_rule "$name" "$mean"); fi
  local raw="${out}.raw"
  cat "$src" | gemini -m gemini-2.5-flash --yolo \
"Translate this SRT subtitle file into $name.

$rule" 2>>"$LOG" | grep -v '^```' > "$raw"
  python scratch/rebuild_srt2.py "$src" "$raw" "$out" >> "$LOG" 2>&1 || cp "$raw" "$out"
  rm -f "$raw"
}

process() {   # $1=week $2=edition $3=src_en
  local w="$1" ed="$2" src="$3"
  [ -f "$src" ] || { echo "  W$w $ed: 원본 없음 스킵" | tee -a "$LOG"; return; }
  # ★사장님 지시: 한글판 → 영어판 순으로 정렬되게 번호 부여(동영상 순서와 일치)
  local ord
  if [ "$ed" = "한글판" ]; then ord=1; else ord=2; fi
  local d="$OUT/W$(printf %02d $w)_${ord}_$ed"
  mkdir -p "$d"
  local kind
  if [ "$w" -le 6 ]; then kind="자모"; else kind="단어/문장"; fi
  echo "=== W$w $ed ($kind) ===" | tee -a "$LOG"
  for code in ja zh es; do
    local o="$d/${YTNAME[$code]}.srt"
    echo "  [$code] 번역 중..." | tee -a "$LOG"
    translate "$src" "$code" "$o" "$w"
    local h=$(grep -c '[가-힣]' "$o" 2>/dev/null || echo 0)
    local b=$(grep -c ' --> ' "$o" 2>/dev/null || echo 0)
    echo "    → ${YTNAME[$code]}.srt : ${b}블록, 한글 ${h}줄" | tee -a "$LOG"
  done
}

HB="hangeul_birth_vowels"
for w in 1 2 3 4 5 6 7 8; do
  process $w "한글판" "$HB/hangeul_w${w}_kosub.en.srt"       # ★한글판 먼저
  process $w "영어판" "$HB/hangeul_w${w}_stickman_np.en.srt"
done
for w in 9 10 11 12 13; do
  case $w in
    13) process $w "한글판" "$HB/hangeul_w13_jieun_np.en.srt"
        process $w "영어판" "$HB/hangeul_w13_jieun_np.en.srt" ;;
    *)  process $w "한글판" "$HB/w${w}pkg/ko_en.srt"
        process $w "영어판" "$HB/w${w}pkg/en_en.srt" ;;
  esac
done

echo "" | tee -a "$LOG"
echo "=== 완료 ===" | tee -a "$LOG"
find "$OUT" -name "*.srt" | wc -l | tee -a "$LOG"
