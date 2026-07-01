#!/usr/bin/env bash
# Download + place the 30 W1 backfill NotebookLM artifacts (audio/slides/report x 10 notebooks).
cd "D:/Entertainments/DevEnvironment/autovideo"
ROOT="D:/Entertainments/DevEnvironment/autovideo"
STG="$ROOT/scratch/nlm"
LOG="$STG/backfill_download.log"
: > "$LOG"
echo "wait 8min for NotebookLM generation..." >> "$LOG"
sleep 480

# parse TRIG lines: TRIG <base> <lang> notebook=<id> audio=<id> slides=<id> report=<id>
grep '^TRIG ' "$STG/backfill_trigger.log" | while read -r _ base lang nb au sl rp; do
  nb=${nb#notebook=}; au=${au#audio=}; sl=${sl#slides=}; rp=${rp#report=}
  sfx=""; [ "$lang" = "en" ] && sfx="_en"
  apath="$STG/dl_${base}_podcast${sfx}.m4a"
  spath="$STG/dl_${base}_slides${sfx}.pdf"
  rpath="$STG/dl_${base}_notes${sfx}.md"
  for try in 1 2 3; do
    PROMPT="Use notebooklm-mcp on notebook \"$nb\". download_artifact each (poll/wait if in_progress): audio \"$au\" -> $apath ; slide_deck \"$sl\" (slide_deck_format='pdf') -> $spath ; report \"$rp\" (markdown) -> $rpath . Print DL ${base} ${lang} done."
    echo "$PROMPT" | gemini -m gemini-2.5-flash --yolo > "$STG/dlrun_${base}_${lang}.log" 2>&1
    if [ -f "$apath" ] && [ -f "$spath" ] && [ -f "$rpath" ]; then break; fi
    sleep 90
  done
  echo "downloaded ${base} ${lang}: a=$([ -f "$apath" ]&&echo y||echo n) s=$([ -f "$spath" ]&&echo y||echo n) r=$([ -f "$rpath" ]&&echo y||echo n)" >> "$LOG"
done

# placement (python): slides->web docs, notes md->pdf->web docs, podcast->R2(guard)
PYTHONUTF8=1 python "$STG/place_backfill.py" >> "$LOG" 2>&1
echo "BACKFILL_DOWNLOAD_DONE" >> "$LOG"
