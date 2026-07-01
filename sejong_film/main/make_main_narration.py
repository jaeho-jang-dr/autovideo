# -*- coding: utf-8 -*-
"""본편 나레이션 — 시나리오 라이트(37장면) 파싱 → KO=Kanna / EN=Alice. 캐시(존재 시 스킵)."""
import os, re, json, subprocess, urllib.request, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SCEN = os.path.join(ROOT, "sejong_film", "sejong_scenario_light.md")
OUT = os.path.join(ROOT, "sejong_film", "main", "audio")
os.makedirs(OUT, exist_ok=True)
FORCE = "--force" in sys.argv

key = None; model = "eleven_multilingual_v2"
for ln in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    s = ln.strip()
    if s.startswith("ELEVEN_API_KEY="): key = s.split("=", 1)[1].strip()
    if s.startswith("ELEVEN_MODEL=") and s.split("=", 1)[1].strip(): model = s.split("=", 1)[1].strip()

def api_get(path):
    req = urllib.request.Request("https://api.elevenlabs.io/v1/" + path, headers={"xi-api-key": key})
    with urllib.request.urlopen(req, timeout=40) as r: return json.load(r)
vs = api_get("voices")["voices"]
def find(sub): return next((v["voice_id"] for v in vs if sub.lower() in v["name"].lower()), None)
VID = {"ko": find("Kanna"), "en": find("Alice")}
print("voices: Kanna", bool(VID["ko"]), "/ Alice", bool(VID["en"]))

# 시나리오 파싱: "N. KO ..." 다음 줄 "   EN ..."
ko, en = {}, {}
cur = None
for line in open(SCEN, encoding="utf-8"):
    m = re.match(r"^\s*(\d+)\.\s+KO\s+(.*)$", line)
    if m:
        cur = int(m.group(1)); ko[cur] = m.group(2).strip(); continue
    m2 = re.match(r"^\s*EN\s+(.*)$", line)
    if m2 and cur is not None:
        en[cur] = m2.group(1).strip()
scenes = sorted(ko)
print(f"파싱된 장면: {len(scenes)} (KO {len(ko)} / EN {len(en)})")

SPEED = {"ko": 1.1, "en": 1.05}
def tts(lang, text, out_path):
    body = json.dumps({"text": text, "model_id": model,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.0,
                           "use_speaker_boost": True, "speed": SPEED[lang]}}).encode("utf-8")
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VID[lang]}?output_format=mp3_44100_128",
        data=body, method="POST", headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r: open(out_path, "wb").write(r.read())

def dur(p):
    try:
        o = subprocess.run(["ffprobe", "-v", "quiet", "-of", "csv=p=0", "-show_entries", "format=duration", p],
                           capture_output=True, text=True, timeout=20); return float(o.stdout.strip())
    except Exception: return 0.0

tot = {"ko": 0.0, "en": 0.0}
for lang, table in (("ko", ko), ("en", en)):
    for n in scenes:
        out = os.path.join(OUT, f"{lang}_{n:02d}.mp3")
        if (not FORCE) and os.path.exists(out) and os.path.getsize(out) > 1000:
            tot[lang] += dur(out); print(f"[skip] {lang}_{n:02d}"); continue
        tts(lang, table[n], out); d = dur(out); tot[lang] += d
        print(f"[OK] {lang}_{n:02d} {d:4.1f}s")
    print(f"  == {lang} 합계 {tot[lang]:.1f}s ({tot[lang]/60:.1f}분) ==\n")
print(f"TOTAL KO {tot['ko']/60:.1f}분 / EN {tot['en']/60:.1f}분")
