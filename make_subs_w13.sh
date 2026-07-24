#!/bin/bash
# W13 5개국어 자막 생성 — Gemini 무료 번역 + 타임스탬프 재조립(필수).
# 원본: hangeul_w13_jieun_np.{ko,en}.srt  → w13pkg/{ko,en}_{ko,en,ja,zh,es}.srt
# ★KO판(한국어 오디오)에도 다국어 자막 필수(학습자=한국어 듣기+모국어 자막)
cd /d/Entertainments/DevEnvironment/autovideo
export PYTHONIOENCODING=utf-8
PKG="hangeul_birth_vowels/w13pkg"
SRC_KO="hangeul_birth_vowels/hangeul_w13_jieun_np.ko.srt"
SRC_EN="hangeul_birth_vowels/hangeul_w13_jieun_np.en.srt"
mkdir -p "$PKG" logs
LOG="logs/subs_w13.log"
: > "$LOG"

# 동영상 언어 자막(그대로 복사)
cp "$SRC_KO" "$PKG/ko_ko.srt"      # KO판의 한국어 자막
cp "$SRC_EN" "$PKG/en_en.srt"      # EN판의 영어 자막
cp "$SRC_EN" "$PKG/ko_en.srt"      # KO판의 영어 자막(영어 SRT 그대로 — 타임라인 동일)
cp "$SRC_KO" "$PKG/en_ko.srt"      # EN판의 한국어 자막

# 번역 (EN 원문 → ja/zh/es). 타임라인이 같으므로 KO판·EN판 공용으로 쓴다.
declare -A LANGS=( [ja]="Japanese" [zh]="Simplified Chinese" [es]="Spanish" )
for code in ja zh es; do
  name="${LANGS[$code]}"
  echo "[번역] $code ($name)" | tee -a "$LOG"
  raw="$PKG/_raw_$code.srt"
  cat "$SRC_EN" | gemini -m gemini-2.5-flash --yolo \
    "Translate this SRT subtitle file into $name. Keep the exact same block count, numbering and timestamps. Translate ONLY the subtitle text. Output the SRT only — no code fences, no commentary." \
    2>>"$LOG" | grep -v '^```' > "$raw"
  # ★타임스탬프 재조립(Gemini가 자주 망가뜨림) — 원본 EN 타임스탬프 + 번역 텍스트
  python scratch/rebuild_srt2.py "$SRC_EN" "$raw" "$PKG/en_$code.srt" >> "$LOG" 2>&1 \
    || cp "$raw" "$PKG/en_$code.srt"
  cp "$PKG/en_$code.srt" "$PKG/ko_$code.srt"     # KO판에도 동일 타임라인 자막
  n=$(grep -c ' --> ' "$PKG/en_$code.srt" 2>/dev/null || echo 0)
  echo "  → $code: $n 블록" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== 생성된 자막 ===" | tee -a "$LOG"
for f in "$PKG"/ko_*.srt "$PKG"/en_*.srt; do
  [ -f "$f" ] && echo "  $(basename $f): $(grep -c ' --> ' $f) 블록" | tee -a "$LOG"
done
rm -f "$PKG"/_raw_*.srt
