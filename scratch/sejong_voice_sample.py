# -*- coding: utf-8 -*-
"""세종 영상용 음성 샘플 — 1장면을 여러 ElevenLabs 음성으로 한/영 생성(비교용)."""
import os, json, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "sejong_film", "voice_samples")
os.makedirs(OUT, exist_ok=True)

# key/model
key = None; model = "eleven_multilingual_v2"
for ln in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    ln = ln.strip()
    if ln.startswith("ELEVEN_API_KEY="): key = ln.split("=", 1)[1].strip()
    if ln.startswith("ELEVEN_MODEL="):
        m = ln.split("=", 1)[1].strip()
        if m: model = m

TEXTS = {
    "ko": "아주 먼 옛날, 책을 세상에서 제일 좋아하는 왕자가 있었어요. 이름은 충녕대군, 나중에 세종대왕이 된답니다! 형들이 마당에서 뛰어놀 때도, 충녕은 방에 쏙 들어가 책을 읽었어요. 책이 제일 재미있는걸요!",
    "en": "Long ago, there was a prince who loved books more than anything. His name was Chungnyeong, and one day he would become the great King Sejong! While his brothers played outside, little Chungnyeong slipped into his room to read. Books are the most fun of all!",
}
CANDS = ["Sarah", "Jessica", "Alice"]

def api_get(path):
    req = urllib.request.Request("https://api.elevenlabs.io/v1/" + path, headers={"xi-api-key": key})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

# name -> full voice_id
voices = {v["name"].split(" - ")[0].strip(): v["voice_id"] for v in api_get("voices")["voices"]}

def tts(voice_id, text, out_path):
    body = json.dumps({
        "text": text, "model_id": model,
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.0,
                            "use_speaker_boost": True, "speed": 1.1},
    }).encode("utf-8")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128"
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    open(out_path, "wb").write(data)
    return len(data)

for cand in CANDS:
    vid = voices.get(cand)
    if not vid:
        print(f"[skip] {cand} 음성 없음"); continue
    for lang, text in TEXTS.items():
        out = os.path.join(OUT, f"{cand}_{lang}.mp3")
        try:
            n = tts(vid, text, out)
            print(f"[OK] {cand} {lang} -> {os.path.basename(out)} ({n//1024} KB)")
        except Exception as e:
            print(f"[ERR] {cand} {lang}: {str(e)[:160]}")
print("\n샘플 폴더:", OUT)
