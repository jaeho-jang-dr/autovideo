# -*- coding: utf-8 -*-
"""세종 라이트 시나리오 37장면 -> ElevenLabs Jessica 나레이션(한/영, 1.1배속) 생성 + 총길이 측정."""
import os, re, json, subprocess, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCEN = os.path.join(ROOT, "sejong_film", "sejong_scenario_light.md")
OUT = os.path.join(ROOT, "sejong_film", "audio")
os.makedirs(OUT, exist_ok=True)

key = None; model = "eleven_multilingual_v2"
for ln in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    s = ln.strip()
    if s.startswith("ELEVEN_API_KEY="): key = s.split("=", 1)[1].strip()
    if s.startswith("ELEVEN_MODEL=") and s.split("=", 1)[1].strip(): model = s.split("=", 1)[1].strip()

def api_get(path):
    req = urllib.request.Request("https://api.elevenlabs.io/v1/" + path, headers={"xi-api-key": key})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

VID = {v["name"].split(" - ")[0].strip(): v["voice_id"] for v in api_get("voices")["voices"]}["Jessica"]

# 라이트 시나리오 파싱: 'N. KO ...' 다음 줄 'EN ...'
scenes = {}
cur = None
for ln in open(SCEN, encoding="utf-8"):
    m = re.match(r"^\s*(\d+)\.\s+KO\s+(.+)$", ln)
    if m:
        cur = int(m.group(1)); scenes[cur] = {"ko": m.group(2).strip(), "en": ""}
        continue
    e = re.match(r"^\s*EN\s+(.+)$", ln)
    if e and cur is not None:
        scenes[cur]["en"] = e.group(1).strip(); cur = None

def tts(text, out_path):
    body = json.dumps({"text": text, "model_id": model,
                       "voice_settings": {"stability": 0.45, "similarity_boost": 0.8,
                                          "style": 0.0, "use_speaker_boost": True, "speed": 1.1}}).encode("utf-8")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VID}?output_format=mp3_44100_128"
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        open(out_path, "wb").write(r.read())

def dur(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "quiet", "-of", "csv=p=0",
                              "-show_entries", "format=duration", path],
                             capture_output=True, text=True, timeout=20)
        return float(out.stdout.strip())
    except Exception:
        return 0.0

tot = {"ko": 0.0, "en": 0.0}
for n in sorted(scenes):
    for lang in ("ko", "en"):
        txt = scenes[n][lang]
        if not txt:
            print(f"[skip] scene {n} {lang} 비어있음"); continue
        out = os.path.join(OUT, f"scene_{n:02d}_{lang}.mp3")
        try:
            tts(txt, out); d = dur(out); tot[lang] += d
            print(f"[OK] s{n:02d} {lang} {d:4.1f}s")
        except Exception as ex:
            print(f"[ERR] s{n:02d} {lang}: {str(ex)[:140]}")

print(f"\n=== 총 나레이션 길이 ===")
print(f"  KO: {tot['ko']:.0f}s = {tot['ko']/60:.1f}분")
print(f"  EN: {tot['en']:.0f}s = {tot['en']/60:.1f}분")
print("  (장면 전환·여백 제외한 순수 나레이션. 영상은 여기에 비주얼 호흡 더해짐)")
