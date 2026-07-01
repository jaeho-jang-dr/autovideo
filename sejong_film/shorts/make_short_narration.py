# -*- coding: utf-8 -*-
"""쇼츠 나레이션 생성 — 한국어=Kanna, 영어=Jessica (4비트씩)."""
import os, json, subprocess, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "sejong_film", "shorts", "audio")
os.makedirs(OUT, exist_ok=True)
key = None; model = "eleven_multilingual_v2"
for ln in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    s = ln.strip()
    if s.startswith("ELEVEN_API_KEY="): key = s.split("=", 1)[1].strip()
    if s.startswith("ELEVEN_MODEL=") and s.split("=", 1)[1].strip(): model = s.split("=", 1)[1].strip()

def api_get(path):
    req = urllib.request.Request("https://api.elevenlabs.io/v1/" + path, headers={"xi-api-key": key})
    with urllib.request.urlopen(req, timeout=40) as r: return json.load(r)

acct = api_get("voices")["voices"]
def find(sub):
    for v in acct:
        if sub.lower() in v["name"].lower(): return v["voice_id"]
    return None
VID = {"ko": find("Kanna"), "en": find("Alice")}
print("voice ids:", "Kanna", bool(VID["ko"]), "/ Alice", bool(VID["en"]))

KO = [
    "한글은 세상에서 가장 과학적인 글자예요. 그런데, 어떻게 만들었을까요?",
    "자음은 우리 입 모양을 본떴어요! 기역, 니은, 미음!",
    "모음은 하늘과 땅과 사람! 점 하나, 가로선, 세로선!",
    "스물여덟 글자에 담긴 세종대왕의 비밀! 풀영상에서 만나요!",
]
EN = [
    "Hangeul is the world's most scientific alphabet. But how was it made?",
    "The consonants copy the shape of your mouth! Giyeok, Nieun, Mieum!",
    "And the vowels? Sky, earth, and person! A dot, a flat line, a tall line!",
    "The secret of twenty-eight letters — watch the full story!",
]

def tts(vid, text, out_path):
    body = json.dumps({"text": text, "model_id": model,
                       "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.0,
                                          "use_speaker_boost": True, "speed": 1.1}}).encode("utf-8")
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
                                 data=body, method="POST", headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r: open(out_path, "wb").write(r.read())

def dur(p):
    try:
        o = subprocess.run(["ffprobe", "-v", "quiet", "-of", "csv=p=0", "-show_entries", "format=duration", p],
                           capture_output=True, text=True, timeout=20); return float(o.stdout.strip())
    except Exception: return 0.0

for lang, lines in (("ko", KO), ("en", EN)):
    t = 0.0
    for i, txt in enumerate(lines, 1):
        out = os.path.join(OUT, f"{lang}_{i}.mp3")
        tts(VID[lang], txt, out); d = dur(out); t += d
        print(f"[OK] {lang}_{i} {d:4.1f}s")
    print(f"  {lang} 합계 {t:.1f}s\n")
