# -*- coding: utf-8 -*-
"""ElevenLabs Voice Library에서 한국어 원어민 음성 3개를 찾아 계정에 추가하고 한국어 샘플 생성."""
import os, re, json, urllib.request, urllib.parse

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "sejong_film", "voice_samples")
os.makedirs(OUT, exist_ok=True)
key = None; model = "eleven_multilingual_v2"
for ln in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    s = ln.strip()
    if s.startswith("ELEVEN_API_KEY="): key = s.split("=", 1)[1].strip()
    if s.startswith("ELEVEN_MODEL=") and s.split("=", 1)[1].strip(): model = s.split("=", 1)[1].strip()

def api_get(path):
    req = urllib.request.Request("https://api.elevenlabs.io/v1/" + path, headers={"xi-api-key": key})
    with urllib.request.urlopen(req, timeout=40) as r: return json.load(r)

def api_post(path, body):
    req = urllib.request.Request("https://api.elevenlabs.io/v1/" + path, data=json.dumps(body).encode("utf-8"),
                                 method="POST", headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r: return json.load(r)

KO = "아주 먼 옛날, 책을 세상에서 제일 좋아하는 왕자가 있었어요. 이름은 충녕대군, 나중에 세종대왕이 된답니다! 형들이 마당에서 뛰어놀 때도, 충녕은 방에 쏙 들어가 책을 읽었어요. 책이 제일 재미있는걸요!"

def tts(vid, text, out_path):
    body = json.dumps({"text": text, "model_id": model,
                       "voice_settings": {"stability": 0.45, "similarity_boost": 0.8,
                                          "style": 0.0, "use_speaker_boost": True, "speed": 1.1}}).encode("utf-8")
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
                                 data=body, method="POST", headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r: open(out_path, "wb").write(r.read())

# 한국어 라이브러리 음성 탐색 (여성 우선, 인기순)
data = api_get("shared-voices?" + urllib.parse.urlencode({"language": "ko", "page_size": "80"}))
voices = data.get("voices", [])
print(f"한국어 라이브러리 음성 {len(voices)}개 발견")

def score(v):
    s = 0.0
    if (v.get("gender") or "").lower() == "female": s += 10
    uc = (str(v.get("use_case", "")) + " " + " ".join(v.get("use_cases", []) if isinstance(v.get("use_cases"), list) else [])).lower()
    if any(k in uc for k in ["narrat", "story", "educat", "conversational", "social", "characters"]): s += 5
    s += min(v.get("cloned_by_count", 0), 8000) / 1000.0
    return s

picked, seen = [], set()
for v in sorted(voices, key=score, reverse=True):
    nm = v.get("name")
    if nm in seen: continue
    seen.add(nm); picked.append(v)
    if len(picked) >= 3: break

for v in picked:
    nm, oid, vid = v.get("name"), v.get("public_owner_id"), v.get("voice_id")
    print(f"\n[선택] {nm} | {v.get('gender')} | {v.get('accent','')} | use={v.get('use_case','')} | 사용수={v.get('cloned_by_count')}")
    newvid = vid
    try:
        r = api_post(f"voices/add/{oid}/{vid}", {"new_name": "KO_" + re.sub(r'\W', '', str(nm))[:18]})
        newvid = r.get("voice_id", vid)
        print("  계정 추가 OK")
    except Exception as e:
        print("  추가 실패(직접 voice_id 시도):", str(e)[:120])
    safe = re.sub(r'\W', '_', str(nm))[:22]
    out = os.path.join(OUT, f"KOR_{safe}_ko.mp3")
    try:
        tts(newvid, KO, out); print(f"  [OK] {os.path.basename(out)} ({os.path.getsize(out)//1024} KB)")
    except Exception as e:
        print("  TTS 실패:", str(e)[:140])
print("\n샘플 폴더:", OUT)
