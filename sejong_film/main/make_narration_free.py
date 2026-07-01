# -*- coding: utf-8 -*-
"""본편 무료 나레이션 (gTTS) — 48샷 마스터 스크립트 파싱 → ko_S##.mp3 / en_S##.mp3.
무료 확인용. OK 후 ElevenLabs(Kanna/Alice)로 교체. 캐시(존재 시 스킵)."""
import os, re, sys, subprocess
from gtts import gTTS

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SCRIPT = os.path.join(ROOT, "sejong_film", "sejong_master_shotscript_48.md")
OUT = os.path.join(ROOT, "sejong_film", "main", "audio_free")
os.makedirs(OUT, exist_ok=True)
FORCE = "--force" in sys.argv

ko, en = {}, {}; cur = None
for line in open(SCRIPT, encoding="utf-8"):
    m = re.match(r"^\*\*S(\d+)", line)
    if m: cur = int(m.group(1)); continue
    mk = re.match(r"^-\s*KO:\s*(.*)$", line)
    me = re.match(r"^-\s*EN:\s*(.*)$", line)
    if mk and cur: ko[cur] = mk.group(1).strip()
    if me and cur: en[cur] = me.group(1).strip()

def is_music(t):
    return ("음악" in t and "나레이션 없음" in t) or t.lower().startswith("(music")

def dur(p):
    try:
        o = subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],
                           capture_output=True, text=True, timeout=20); return float(o.stdout.strip())
    except Exception: return 0.0

tot = {"ko":0.0,"en":0.0}
for lang, table in (("ko", ko), ("en", en)):
    for n in sorted(table):
        txt = table[n]
        out = os.path.join(OUT, f"{lang}_S{n:02d}.mp3")
        if is_music(txt):
            print(f"[music] {lang}_S{n:02d} (스킵)"); continue
        if (not FORCE) and os.path.exists(out) and os.path.getsize(out) > 800:
            tot[lang] += dur(out); print(f"[skip] {lang}_S{n:02d}"); continue
        # 따옴표 등 음성에 방해되는 기호 정리
        clean = txt.replace("“","").replace("”","").replace("‘","'").replace("’","'")
        try:
            gTTS(clean, lang=lang).save(out); d = dur(out); tot[lang] += d
            print(f"[OK] {lang}_S{n:02d} {d:4.1f}s")
        except Exception as e:
            print(f"[ERR] {lang}_S{n:02d}: {str(e)[:80]}")
    print(f"  == {lang} 합계 {tot[lang]:.1f}s ({tot[lang]/60:.1f}분) ==")
print(f"TOTAL KO {tot['ko']/60:.1f}분 / EN {tot['en']/60:.1f}분")
