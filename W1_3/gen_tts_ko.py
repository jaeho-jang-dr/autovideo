# -*- coding: utf-8 -*-
"""W1-3 한국어 나레이션 edge-tts 초안 생성 + 1.1배속 + 실측.
- 오늘은 edge-tts만 쓴다(Azure/최종본 아님). ★save_tts()는 .env에 ELEVEN_API_KEY가 있으면
  ElevenLabs로 새 텐데, 그 키는 비활성화돼 있어 안전하지만, 명시적으로
  tts_manager.save_tts_edge_tts()를 직접 호출해 edge 엔진을 강제한다.
- 여성 기본 음성(선희, ko-KR-SunHiNeural) — EDGE_ACTIVE_VOICE 미설정 시 기본값.
- 캐시: 기존 캐시 없음(첫 렌더) — 무조건 새로 생성.

사용법: python W1_3/gen_tts_ko.py
출력: W1_3/_audio_ko/{scene}.raw.mp3 (edge-tts 원본)
      W1_3/_audio_ko/{scene}.mp3     (atempo=1.1 적용, 최종 나레이션)
      W1_3/_audio_ko/durations.json  (씬별 실측 길이 초)
"""
import os
import sys
import json
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.pop("TTS_ENGINE", None)  # edge 강제 — Azure 분기 타지 않게 비움

import tts_manager as tm  # noqa: E402
from narration_ko import NARR_KO, SCENE_ORDER  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_audio_ko")
SPEED = 1.1


def mp3_dur(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    durations = {}
    for scene in SCENE_ORDER:
        text = NARR_KO[scene]
        raw = os.path.join(OUT_DIR, "%s.raw.mp3" % scene)
        final = os.path.join(OUT_DIR, "%s.mp3" % scene)

        # 첫 렌더 — 기존 캐시 무시하고 강제 재생성(프로젝트 골든룰)
        for p in (raw, raw + ".txt", final):
            if os.path.exists(p):
                os.remove(p)

        ok = tm.save_tts_edge_tts(text, raw, lang="ko")
        if not ok:
            raise RuntimeError("edge-tts 생성 실패: %s" % scene)

        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", raw,
             "-filter:a", "atempo=%.2f" % SPEED,
             "-c:a", "libmp3lame", "-b:a", "160k", final],
            check=True,
        )
        d = mp3_dur(final)
        durations[scene] = d
        print("%s  raw=%.2fs -> 1.1x=%.2fs" % (scene, mp3_dur(raw), d))

    with open(os.path.join(OUT_DIR, "durations.json"), "w", encoding="utf-8") as f:
        json.dump(durations, f, ensure_ascii=False, indent=2)

    total = sum(durations.values())
    print("\n합계(나레이션만, 패딩 전) = %.2f초 (%.1f분)" % (total, total / 60))


if __name__ == "__main__":
    main()
