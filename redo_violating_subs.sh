#!/bin/bash
# ★원칙 위반 자막 재작업 (2026-07-14)
#   위반1: W1 한글판/영어판 ja·zh·es (6개) — 자모 'ㅏ'가 일본어/중국어 문자로 바뀌어 한글이 사라짐
#   위반2: W7 영어판 중국어 (1개) — [로마자 발음] 0개
# 표기 원칙(사장님 확정):
#   자모  'ㅏ' [a]                        한글 + 로마자 발음
#   단어  '오른쪽' [o-reun-jjok] (뜻)      한글 + 로마자 발음 + 그 나라 뜻
#   문장  '어떻게 가요?' (뜻)              한글 + 그 나라 말 뜻
# ★핵심: W1 원본 영어 srt에는 [로마자]가 없다 → add_pron_to_srt.py 로 먼저 주입한 뒤 번역한다.
cd /d/Entertainments/DevEnvironment/autovideo
export PYTHONIOENCODING=utf-8
OUT="scratch/fixed_subs"
LOG="logs/redo_violating_subs.log"
TMP="scratch/_redo_src"
mkdir -p "$OUT" logs "$TMP"
: > "$LOG"

declare -A LNAME=( [ja]="Japanese" [zh]="Simplified Chinese" [es]="Spanish" )
declare -A YTNAME=( [ja]="일본어" [zh]="중국어(중국)" [es]="스페인어" )
declare -A MEAN=( [ja]="Japanese meaning in parentheses, e.g. （右）" \
                  [zh]="Chinese meaning in parentheses, e.g. （右边）" \
                  [es]="Spanish meaning in parentheses, e.g. (derecha)" )

jamo_rule() {   # $1=lang  $2=meaning hint  (W1~W6 자모 강의)
cat <<EOF
⚠️ CRITICAL — this is a Korean ALPHABET (Jamo) lesson. Follow EXACTLY:

1. KEEP every Hangeul letter/word EXACTLY as-is, in Hangeul script.
   ⚠️⚠️ NEVER replace a Hangeul letter with kana/kanji/hanzi/latin. 'ㅏ' must stay 'ㅏ'.
   If the source line contains 'ㅏ' or '아' or any 한글, the SAME 한글 MUST appear in your output.
2. Hangeul LETTER (jamo: ㅏ ㅓ ㅗ ㅜ ㅡ ㅣ ㅐ ㅔ ㄱ ㄴ ㄷ …) → write:  'ㅏ' [a]
   → Hangeul in quotes + ROMAN (English-letter) phonetic value in brackets. NO meaning (letters have none).
   ⚠️ Never transliterate the sound into $1 characters (啊/ア/…) — it cannot distinguish ㅓ from ㅗ.
   Vowels: ㅏ[a] ㅓ[eo] ㅗ[o] ㅜ[u] ㅡ[eu] ㅣ[i] ㅐ[ae] ㅔ[e] ㅑ[ya] ㅕ[yeo] ㅛ[yo] ㅠ[yu] ㅚ[oe] ㅟ[wi] ㅢ[ui] ㅘ[wa] ㅝ[wo] ㅖ[ye] ㅒ[yae]
   Consonants: ㄱ[g] ㄴ[n] ㄷ[d] ㄹ[r/l] ㅁ[m] ㅂ[b] ㅅ[s] ㅇ[ng] ㅈ[j] ㅎ[h] ㅋ[k] ㅌ[t] ㅍ[p] ㅊ[ch] ㄲ[kk] ㄸ[tt] ㅃ[pp] ㅆ[ss] ㅉ[jj]
3. Hangeul WORD/SYLLABLE (아기, 학교 …) → '아기' [a-gi] + $2   (Hangeul + roman + meaning)
4. Hangeul SENTENCE → '문장' + $2   (Hangeul + meaning in $1)
5. Translate ONLY the surrounding explanation into $1. Keep block count/numbering/timestamps identical.

Output SRT only — no code fences, no commentary.
EOF
}

word_rule() {   # $1=lang  $2=meaning hint  (W7+ 단어·문장 강의)
cat <<EOF
⚠️ CRITICAL — Korean teaching video. Follow EXACTLY:

1. KEEP every Korean word/phrase in Hangeul EXACTLY as-is. NEVER replace it with kanji/hanzi/kana.
2. Korean WORD → '오른쪽' [o-reun-jjok] + $2
   → Hangeul + ROMAN (English-letter) pronunciation in brackets + meaning.
   ⚠️⚠️ The [roman] bracket is MANDATORY for every Korean word — do not omit it.
   ⚠️ Pronunciation must always be ROMAN letters (never 汉字/カタカナ音写).
3. Korean SENTENCE → '어떻게 가요?' + $2   (Hangeul + meaning in $1)
4. Single Hangeul LETTER (jamo) → 'ㅏ' [a] only — no meaning.
5. Translate ONLY the surrounding explanation into $1. Keep block count/numbering/timestamps identical.

Output SRT only — no code fences, no commentary.
EOF
}

translate() {   # $1=src  $2=code  $3=out  $4=kind(jamo|word)
  local src="$1" code="$2" out="$3" kind="$4"
  local name="${LNAME[$code]}" mean="${MEAN[$code]}" rule
  if [ "$kind" = "jamo" ]; then rule=$(jamo_rule "$name" "$mean"); else rule=$(word_rule "$name" "$mean"); fi
  local raw="${out}.raw"
  cat "$src" | gemini -m gemini-2.5-flash --yolo \
"Translate this SRT subtitle file into $name.

$rule" 2>>"$LOG" | grep -v '^```' > "$raw"
  [ -s "$raw" ] || { echo "    ✗ 빈 결과 — 재시도" | tee -a "$LOG"
    cat "$src" | gemini -m gemini-2.5-flash --yolo "Translate this SRT into $name.

$rule" 2>>"$LOG" | grep -v '^```' > "$raw"; }
  python scratch/rebuild_srt2.py "$src" "$raw" "$out" >> "$LOG" 2>&1 || cp "$raw" "$out"
  rm -f "$raw"
  local b h r
  b=$(grep -c ' --> ' "$out" 2>/dev/null || echo 0)
  h=$(grep -cE '[가-힣ㄱ-ㅎㅏ-ㅣ]' "$out" 2>/dev/null || echo 0)     # ★자모(ㄱ-ㅎ,ㅏ-ㅣ)도 한글로 카운트
  r=$(grep -o '\[[a-z/-]*\]' "$out" 2>/dev/null | wc -l)
  echo "    → ${YTNAME[$code]}.srt : ${b}블록, 한글 ${h}줄, [로마자] ${r}개" | tee -a "$LOG"
  [ "$h" -lt 5 ] && echo "    ★★경고: 한글 유실 — 재확인 필요" | tee -a "$LOG"
}

# ── 1) W1: 원본 영어/한글판 srt에 [로마자] 주입 후 재번역 ──────────────
HB="hangeul_birth_vowels"
python add_pron_to_srt.py "$HB/hangeul_w1_kosub.en.srt"        "$TMP/w1_ko_src.srt"  | tee -a "$LOG"
python add_pron_to_srt.py "$HB/hangeul_w1_stickman_np.en.srt"  "$TMP/w1_en_src.srt"  | tee -a "$LOG"

echo "=== W01_1_한글판 (자모, src=w1_ko_src) ===" | tee -a "$LOG"
for c in ja zh es; do echo "  [$c] 번역 중..." | tee -a "$LOG"; translate "$TMP/w1_ko_src.srt" "$c" "$OUT/W01_1_한글판/${YTNAME[$c]}.srt" jamo; done

echo "=== W01_2_영어판 (자모, src=w1_en_src) ===" | tee -a "$LOG"
for c in ja zh es; do echo "  [$c] 번역 중..." | tee -a "$LOG"; translate "$TMP/w1_en_src.srt" "$c" "$OUT/W01_2_영어판/${YTNAME[$c]}.srt" jamo; done

# ── 2) W7 영어판 중국어: 발음기호 0개 → 재번역 ─────────────────────────
python add_pron_to_srt.py "$HB/hangeul_w7_stickman_np.en.srt" "$TMP/w7_en_src.srt" | tee -a "$LOG"
echo "=== W07_2_영어판 중국어 재작업 ===" | tee -a "$LOG"
translate "$TMP/w7_en_src.srt" zh "$OUT/W07_2_영어판/중국어(중국).srt" word

echo "" | tee -a "$LOG"
echo "=== 재작업 완료 ===" | tee -a "$LOG"
