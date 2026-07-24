#!/bin/bash
# W12 다국어 제목·설명 생성 (ja/zh/es) — Gemini 무료 번역. 영어판 원문 기준.
cd /d/Entertainments/DevEnvironment/autovideo
export PYTHONIOENCODING=utf-8
PKG="hangeul_birth_vowels/w13pkg"
LOG="logs/meta_w13.log"; : > "$LOG"

declare -A LANGS=( [ja]="Japanese" [zh]="Simplified Chinese" [es]="Spanish" )
for code in ja zh es; do
  name="${LANGS[$code]}"
  echo "[제목] $code" | tee -a "$LOG"
  cat "$PKG/en_title.txt" | gemini -m gemini-2.5-flash --yolo \
    "Translate this YouTube video title into $name. Keep it under 90 characters, keep 'W12', keep it SEO-friendly for Korean-learning viewers. Output ONLY the translated title on one line — no quotes, no commentary." \
    2>>"$LOG" | grep -v '^```' | head -1 | sed 's/^["'"'"']//;s/["'"'"']$//' > "$PKG/${code}_title.txt"
  echo "  → $(cat "$PKG/${code}_title.txt")" | tee -a "$LOG"

  echo "[설명] $code" | tee -a "$LOG"
  cat "$PKG/en_desc.txt" | gemini -m gemini-2.5-flash --yolo \
    "Translate this YouTube video description into $name. Keep the same structure, emojis, chapter timestamps (do NOT change the numbers), URLs and the Korean phrases in quotes as-is. Output ONLY the translated description — no code fences, no commentary." \
    2>>"$LOG" | grep -v '^```' > "$PKG/${code}_desc.txt"
  echo "  → $(wc -c < "$PKG/${code}_desc.txt") bytes" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== 생성 결과 ===" | tee -a "$LOG"
for code in ja zh es; do
  t="$PKG/${code}_title.txt"; d="$PKG/${code}_desc.txt"
  echo "  $code: 제목 $(wc -c < $t)B / 설명 $(wc -c < $d)B" | tee -a "$LOG"
done
