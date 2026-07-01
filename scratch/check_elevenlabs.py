# -*- coding: utf-8 -*-
"""ElevenLabs 계정 점검 — 요금제/사용량/음성 목록. 키 값은 절대 출력하지 않음."""
import os, json, urllib.request

# .env에서 ElevenLabs 키 찾기 (값 노출 금지)
key = None
keyname = None
envp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
for ln in open(envp, encoding="utf-8"):
    ln = ln.strip()
    if ln and not ln.startswith("#") and "=" in ln:
        k, v = ln.split("=", 1)
        if k.strip() == "ELEVEN_API_KEY":
            key = v.strip().strip('"').strip("'"); keyname = k.strip()
if not key:
    raise SystemExit("ElevenLabs 키를 .env에서 못 찾음")
print(f"[키] .env의 '{keyname}' 사용 (값 비표시)")

def api(path):
    req = urllib.request.Request("https://api.elevenlabs.io/v1/" + path,
                                 headers={"xi-api-key": key})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

# 1) 구독/사용량
try:
    s = api("user/subscription")
    print("\n=== 요금제/사용량 ===")
    print("  tier:", s.get("tier"))
    print("  status:", s.get("status"))
    used, lim = s.get("character_count"), s.get("character_limit")
    print(f"  문자 사용: {used} / {lim} (남음 {lim-used if lim and used is not None else '?'})")
    print("  voice_limit:", s.get("voice_limit"), " 전문음성 가능:", s.get("can_use_professional_voice_cloning"))
except Exception as e:
    print("구독 조회 실패:", str(e)[:200])

# 2) 음성 목록 (이름/언어/성별 라벨)
try:
    v = api("voices")
    print("\n=== 사용 가능한 음성 (상위) ===")
    for vo in v.get("voices", [])[:30]:
        lbl = vo.get("labels", {}) or {}
        print(f"  {vo.get('name'):16} | {lbl.get('gender','?'):6} | {lbl.get('age','?'):10} | {lbl.get('descriptive', lbl.get('description',''))[:24]:24} | id={vo.get('voice_id')[:8]}")
except Exception as e:
    print("음성 조회 실패:", str(e)[:200])
