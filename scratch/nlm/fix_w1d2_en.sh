#!/usr/bin/env bash
# Trigger + download + place ONLY w1d2 en (the one that failed in the W1 backfill).
cd "D:/Entertainments/DevEnvironment/autovideo"
ROOT="D:/Entertainments/DevEnvironment/autovideo"
STG="$ROOT/scratch/nlm"
LOG="$STG/fix_w1d2_en.log"
: > "$LOG"

base="w1d2"; lang="en"; sfx="_en"
SRC="$STG/src_${base}_${lang}.txt"
apath="$STG/dl_${base}_podcast${sfx}.m4a"
spath="$STG/dl_${base}_slides${sfx}.pdf"
rpath="$STG/dl_${base}_notes${sfx}.md"

echo "== trigger w1d2 en ==" >> "$LOG"
TPROMPT="Use notebooklm-mcp. 1) notebook_create name 'drjayed ${base} ${lang}'. 2) Read the local file ${SRC} and source_add its full text (type text, title '${base} ${lang}'). 3) studio_create audio (English), slide_deck (English), report (English). Print ONE final line exactly: TRIG ${base} ${lang} notebook=<id> audio=<id> slides=<id> report=<id>"
echo "$TPROMPT" | gemini -m gemini-2.5-flash --yolo > "$STG/trig_w1d2_en.log" 2>&1
TRIG=$(grep -E "^TRIG " "$STG/trig_w1d2_en.log" | tail -1)
echo "$TRIG" >> "$LOG"
# parse
set -- $TRIG
nb=${4#notebook=}; au=${5#audio=}; sl=${6#slides=}; rp=${7#report=}
echo "nb=$nb au=$au sl=$sl rp=$rp" >> "$LOG"

echo "== wait 9min for generation ==" >> "$LOG"
sleep 540

for try in 1 2 3 4; do
  DPROMPT="Use notebooklm-mcp on notebook \"$nb\". download_artifact each (poll/wait if in_progress): audio \"$au\" -> $apath ; slide_deck \"$sl\" (slide_deck_format='pdf') -> $spath ; report \"$rp\" (markdown) -> $rpath . Print DL ${base} ${lang} done."
  echo "$DPROMPT" | gemini -m gemini-2.5-flash --yolo > "$STG/dlrun_${base}_${lang}.log" 2>&1
  if [ -f "$apath" ] && [ -f "$spath" ] && [ -f "$rpath" ]; then break; fi
  echo "  retry $try: a=$([ -f "$apath" ]&&echo y||echo n) s=$([ -f "$spath" ]&&echo y||echo n) r=$([ -f "$rpath" ]&&echo y||echo n)" >> "$LOG"
  sleep 90
done
echo "downloaded ${base} ${lang}: a=$([ -f "$apath" ]&&echo y||echo n) s=$([ -f "$spath" ]&&echo y||echo n) r=$([ -f "$rpath" ]&&echo y||echo n)" >> "$LOG"
echo "FIX_W1D2_EN_DONE" >> "$LOG"
