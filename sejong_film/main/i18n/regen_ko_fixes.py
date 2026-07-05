# -*- coding: utf-8 -*-
"""KO 나레이션 5개 씬 재교정 — 자모는 '이름'으로 스펠링(DB 소릿값 클립 대신), 훈민정음/곧 발음 교정.
자막(narration.json)은 그대로, 오디오(audio_11/ko_S##.mp3)만 Kanna로 재생성 + STT 검증.
사용: python sejong_film/main/i18n/regen_ko_fixes.py"""
import os, json, subprocess, urllib.request, shutil

ROOT = "D:/Entertainments/DevEnvironment/autovideo"
MAIN = os.path.join(ROOT, "sejong_film", "main")
AUD = os.path.join(MAIN, "audio_11")
BAK = os.path.join(AUD, "_bak_before_namefix"); os.makedirs(BAK, exist_ok=True)
TMP = os.path.join(MAIN, "_ko_namefix_tmp"); os.makedirs(TMP, exist_ok=True)

# 오디오 전용 교정 텍스트 (자막은 narration.json 원본 유지 — 화면엔 ㄱ, 소리는 '기역')
FIX = {
 13: '곧, 집은 아이들 웃음소리로 가득 찼어요. 충녕은 책만큼이나 가족을 사랑하는 다정한 아빠였지요. 그리고 늘 같은 생각을 했어요. 어떻게 하면 백성들이 더 행복할까?',
 27: '그리고 마침내! 천사백사십삼 년 겨울, 세종은 스물여덟 개의 새 글자를 완성했어요. 이름은 훈민정음. 백성을 가르치는 바른 소리라는 뜻이에요.',
 37: '자, 이제 글자의 비밀! 자음은 우리 입 모양을 본떠 만들었어요. 기역은 혀뿌리가 목구멍을 막는 모양, 니은은 혀가 윗니에 닿는 모양, 미음은 입 모양 그대로! 신기하죠?',
 38: '게다가 소리가 세지면, 줄을 하나씩 더 그었어요. 니은에 줄을 더하면 디귿, 또 더하면 티읕! 모양만 봐도 소리를 알 수 있는, 똑똑한 글자랍니다.',
 49: '우리는 오백팔십 년 전부터 이 멋진 왕 덕분에 가장 가난하고 미천한 집 아이들도 골목에서 나무막대로 흙바닥에 기역, 니은, 디귿, 아, 어, 오, 이응, 리을을 쓰면서 놀 수 있었습니다. 이것이 세종대왕님이 우리 백성과 후손 모두에게 주신 큰 선물이었습니다.',
}

key = None
for ln in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    if ln.strip().startswith("ELEVEN_API_KEY="):
        key = ln.split("=", 1)[1].strip()
def api_get(p):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.elevenlabs.io/v1/"+p, headers={"xi-api-key": key}), timeout=40))
VID = next(v["voice_id"] for v in api_get("voices")["voices"] if "kanna" in v["name"].lower())

def norm(src, dst):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-ar", "44100", "-ac", "2",
                    "-c:a", "libmp3lame", "-b:a", "128k", dst], timeout=60)

def tts(text, dst):
    body = json.dumps({"text": text, "model_id": "eleven_multilingual_v2",
                       "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.0,
                                          "use_speaker_boost": True, "speed": 1.1}}).encode()
    raw = os.path.join(TMP, "_raw.mp3")
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VID}?output_format=mp3_44100_128",
                                 data=body, method="POST", headers={"xi-api-key": key, "Content-Type": "application/json"})
    open(raw, "wb").write(urllib.request.urlopen(req, timeout=120).read())
    norm(raw, dst)

def dur(p):
    try: return float(subprocess.run(["ffprobe", "-v", "quiet", "-of", "csv=p=0", "-show_entries", "format=duration", p], capture_output=True, text=True, timeout=20).stdout.strip())
    except Exception: return 0.0

# STT 검증기
from faster_whisper import WhisperModel
stt = WhisperModel("small", device="cpu", compute_type="int8")
def transcribe(p):
    segs, _ = stt.transcribe(p, language="ko")
    return " ".join(s.text for s in segs).strip()

for n, text in FIX.items():
    out = os.path.join(AUD, f"ko_S{n:02d}.mp3")
    if os.path.exists(out) and not os.path.exists(os.path.join(BAK, f"ko_S{n:02d}.mp3")):
        shutil.copy2(out, os.path.join(BAK, f"ko_S{n:02d}.mp3"))
    tts(text, out)
    got = transcribe(out)
    print(f"[S{n:02d}] {dur(out):.1f}s")
    print(f"   TTS텍스트: {text[:60]}...")
    print(f"   STT확인 : {got[:110]}")
    print()

shutil.rmtree(TMP, ignore_errors=True)
print("재교정 완료:", list(FIX.keys()))
