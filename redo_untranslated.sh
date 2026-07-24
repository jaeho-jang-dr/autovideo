#!/bin/bash
# ★미번역 블록이 남은 자막 5개 재번역 (audit_subs.py 결과, 2026-07-14)
#   W01_2_영어판/일본어, W03_1_한글판/중국어, W04_1_한글판/중국어,
#   W05_1_한글판/일본어, W13_2_영어판/중국어
# 원인: 제미나이가 중간 블록 구간을 통째로 건너뜀 → 원문(영어)이 그대로 남음
# 대책: "EVERY block must be translated, none skipped" 를 프롬프트에 명시 + 원본에 [로마자] 주입 후 번역
cd /d/Entertainments/DevEnvironment/autovideo
export PYTHONIOENCODING=utf-8
OUT="scratch/fixed_subs"; TMP="scratch/_redo_src"; LOG="logs/redo_untranslated.log"
mkdir -p "$TMP" logs; : > "$LOG"
HB="hangeul_birth_vowels"

declare -A LNAME=( [ja]="Japanese" [zh]="Simplified Chinese" [es]="Spanish" )
declare -A YTNAME=( [ja]="일본어" [zh]="중국어(중국)" [es]="스페인어" )
declare -A MEAN=( [ja]="Japanese meaning in parentheses, e.g. （右）" \
                  [zh]="Chinese meaning in parentheses, e.g. （右边）" \
                  [es]="Spanish meaning in parentheses, e.g. (derecha)" )

rule() {   # $1=lang  $2=meaning  $3=kind(jamo|word)
cat <<EOF
⚠️⚠️ TRANSLATE **EVERY SINGLE BLOCK**. Do NOT skip any block. Do NOT leave any English sentence
   untranslated. The output must have the SAME number of blocks as the input, and EVERY block's
   text must be in $1 (except the Hangeul and the [roman] brackets, which stay as-is).

⚠️ CRITICAL — Korean teaching video. Follow EXACTLY:
1. KEEP every Hangeul EXACTLY as-is, in Hangeul script. NEVER replace 한글 with kana/kanji/hanzi.
   'ㅏ' must stay 'ㅏ'. '안녕하세요' must stay '안녕하세요'.
2. Hangeul LETTER (jamo) → 'ㅏ' [a]   (Hangeul + ROMAN phonetic in brackets, no meaning)
   Vowels: ㅏ[a] ㅓ[eo] ㅗ[o] ㅜ[u] ㅡ[eu] ㅣ[i] ㅐ[ae] ㅔ[e] ㅑ[ya] ㅕ[yeo] ㅛ[yo] ㅠ[yu] ㅚ[oe] ㅟ[wi] ㅢ[ui] ㅘ[wa] ㅝ[wo]
   Consonants: ㄱ[g] ㄴ[n] ㄷ[d] ㄹ[r/l] ㅁ[m] ㅂ[b] ㅅ[s] ㅇ[ng] ㅈ[j] ㅎ[h] ㅋ[k] ㅌ[t] ㅍ[p] ㅊ[ch] ㄲ[kk] ㄸ[tt] ㅃ[pp] ㅆ[ss] ㅉ[jj]
3. Korean WORD → '오른쪽' [o-reun-jjok] + $2      (Hangeul + ROMAN + meaning)
   ⚠️ The [roman] bracket is MANDATORY for every Korean word.
   ⚠️ Pronunciation must always be ROMAN letters (never 汉字/カタカナ音写 — cannot distinguish ㅓ from ㅗ).
4. Korean SENTENCE → '어떻게 가요?' + $2          (Hangeul + meaning in $1)
5. Translate ONLY the surrounding explanation into $1. Keep block count/numbering/timestamps identical.

Output SRT only — no code fences, no commentary.
EOF
}

redo() {   # $1=src_srt  $2=code  $3=out  $4=kind
  local src="$1" code="$2" out="$3" kind="$4"
  local name="${LNAME[$code]}" mean="${MEAN[$code]}"
  local r; r=$(rule "$name" "$mean" "$kind")
  local raw="${out}.raw"
  echo "  [$code] $out 재번역..." | tee -a "$LOG"
  cat "$src" | gemini -m gemini-2.5-flash --yolo "Translate this SRT subtitle file into $name.

$r" 2>>"$LOG" | grep -v '^```' > "$raw"
  [ -s "$raw" ] || { echo "    ✗ 빈 결과 — 재시도" | tee -a "$LOG"
    cat "$src" | gemini -m gemini-2.5-flash --yolo "Translate this SRT into $name. Translate EVERY block, skip none.

$r" 2>>"$LOG" | grep -v '^```' > "$raw"; }
  python scratch/rebuild_srt2.py "$src" "$raw" "$out" >> "$LOG" 2>&1 || cp "$raw" "$out"
  rm -f "$raw"
}

# 원본에 [로마자] 주입(이미 있으면 그대로)
python add_pron_to_srt.py "$HB/hangeul_w1_stickman_np.en.srt" "$TMP/w1_en_src.srt"  >> "$LOG"
python add_pron_to_srt.py "$HB/hangeul_w3_kosub.en.srt"       "$TMP/w3_ko_src.srt"  >> "$LOG"
python add_pron_to_srt.py "$HB/hangeul_w4_kosub.en.srt"       "$TMP/w4_ko_src.srt"  >> "$LOG"
python add_pron_to_srt.py "$HB/hangeul_w5_kosub.en.srt"       "$TMP/w5_ko_src.srt"  >> "$LOG"
python add_pron_to_srt.py "$HB/hangeul_w13_jieun_np.en.srt"   "$TMP/w13_en_src.srt" >> "$LOG"

redo "$TMP/w1_en_src.srt"  ja "$OUT/W01_2_영어판/일본어.srt"        jamo
redo "$TMP/w3_ko_src.srt"  zh "$OUT/W03_1_한글판/중국어(중국).srt"  jamo
redo "$TMP/w4_ko_src.srt"  zh "$OUT/W04_1_한글판/중국어(중국).srt"  jamo
redo "$TMP/w5_ko_src.srt"  ja "$OUT/W05_1_한글판/일본어.srt"        jamo
redo "$TMP/w13_en_src.srt" zh "$OUT/W13_2_영어판/중국어(중국).srt"  word

echo "=== 재번역 완료 ===" | tee -a "$LOG"
