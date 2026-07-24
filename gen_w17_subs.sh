#!/bin/bash
# W17 다국어 자막(ja/zh/es) — 소스는 영어판 자막(한글+[로마자]+뜻이 이미 들어있음)
# 한글판·영어판 둘 다 같은 ja/zh/es 자막을 쓴다(화면·타이밍 동일, 오디오만 다름).
# ★ zh=중국 본토 간체(zh-Hans) · es=중남미 스페인어(es-419) 명시 ([[subtitle-spanish-latam-chinese-mainland]])
cd /d/Entertainments/DevEnvironment/autovideo
export PYTHONIOENCODING=utf-8
SRC="hangeul_birth_vowels/hangeul_w17_teacherjay_np.en.srt"
OUT="scratch/fixed_subs"
LOG="logs/gen_w17_subs.log"
mkdir -p logs; : > "$LOG"

declare -A LNAME=( [ja]="Japanese" [zh]="Simplified Chinese (Mainland China, zh-Hans)" [es]="Latin American Spanish (es-419)" )
declare -A YTNAME=( [ja]="일본어" [zh]="중국어(중국)" [es]="스페인어" )
declare -A MEAN=( [ja]="Japanese meaning in parentheses, e.g. （タメ口）" \
                  [zh]="Mainland Simplified Chinese meaning in parentheses, e.g. （半语）" \
                  [es]="Latin American Spanish meaning in parentheses, e.g. (habla informal)" )

rule() {  # $1=lang  $2=meaning hint
cat <<EOF
⚠️⚠️ TRANSLATE **EVERY SINGLE BLOCK**. Do NOT skip any block. Do NOT leave any English sentence
   untranslated. Same number of blocks as input, and EVERY block's text must be in $1
   (except the Hangeul and the [roman] brackets, which stay EXACTLY as-is).

⚠️ CRITICAL — Korean teaching video. Follow EXACTLY:
1. KEEP every Korean word in Hangeul EXACTLY as-is. NEVER replace 한글 with kanji/hanzi/kana.
   '반말' must stay '반말'.
2. KEEP every [roman] pronunciation bracket EXACTLY as-is: '반말' [ban-mal]
   ⚠️ Never convert the roman pronunciation into $1 characters.
3. Korean WORD → '반말' [ban-mal] + $2   (Hangeul + roman + meaning in $1)
4. Korean SENTENCE → '밥 먹었어?' [bap-meog-eoss-eo] + $2
5. Translate ONLY the surrounding English explanation into $1.
   Keep block count / numbering / timestamps identical.

Output SRT only — no code fences, no commentary.
EOF
}

for ed in 1_한글판 2_영어판; do
  d="$OUT/W17_$ed"
  mkdir -p "$d"
  echo "=== W17_$ed ===" | tee -a "$LOG"
  for code in ja zh es; do
    o="$d/${YTNAME[$code]}.srt"
    if [ -s "$o" ]; then echo "  [skip] ${YTNAME[$code]}" | tee -a "$LOG"; continue; fi
    # 한글판/영어판 동일 내용 → 이미 만든 게 있으면 복사(제미나이 호출 절약)
    other="$OUT/W17_2_영어판/${YTNAME[$code]}.srt"
    if [ "$ed" = "1_한글판" ] && [ -s "$other" ]; then cp "$other" "$o"; echo "  [copy] ${YTNAME[$code]}" | tee -a "$LOG"; continue; fi
    echo "  [$code] 번역 중..." | tee -a "$LOG"
    r=$(rule "${LNAME[$code]}" "${MEAN[$code]}")
    raw="${o}.raw"
    cat "$SRC" | gemini -m gemini-2.5-flash --yolo "Translate this SRT subtitle file into ${LNAME[$code]}.

$r" 2>>"$LOG" | grep -v '^```' > "$raw"
    [ -s "$raw" ] || { echo "    ✗ 빈 결과 — 재시도" | tee -a "$LOG"
      cat "$SRC" | gemini -m gemini-2.5-flash --yolo "Translate this SRT into ${LNAME[$code]}. Translate EVERY block.

$r" 2>>"$LOG" | grep -v '^```' > "$raw"; }
    python scratch/rebuild_srt2.py "$SRC" "$raw" "$o" >> "$LOG" 2>&1 || cp "$raw" "$o"
    rm -f "$raw"
    b=$(grep -c ' --> ' "$o"); h=$(grep -cE '[가-힣]' "$o"); rm_=$(grep -o '\[[a-z-]*\]' "$o" | wc -l)
    echo "    → ${YTNAME[$code]}.srt : ${b}블록, 한글 ${h}줄, [로마자] ${rm_}개" | tee -a "$LOG"
  done
done

# 영어판 → 한글판 복사(같은 내용)
for code in ja zh es; do
  s="$OUT/W17_2_영어판/${YTNAME[$code]}.srt"
  t="$OUT/W17_1_한글판/${YTNAME[$code]}.srt"
  [ -s "$s" ] && [ ! -s "$t" ] && cp "$s" "$t" && echo "  [copy→한글판] ${YTNAME[$code]}" | tee -a "$LOG"
done
echo "=== 완료 ===" | tee -a "$LOG"
