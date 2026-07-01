# -*- coding: utf-8 -*-
"""졸라 한글 쇼츠 v2 최종화 — 무음 영상 + 배경음악 mux → dynamite_short_v2.mp4.
영상정보는 content.db에 링크 저장(바이너리는 로컬/유튜브에만)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "channel"))
try: import content_db as cdb
except Exception: cdb = None
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
from moviepy import VideoFileClip, AudioFileClip
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut

PROJECT = "zolla_hangul_dynamite"
ODIR = os.path.join(ROOT, "zolla_hangul")
SILENT = os.path.join(ODIR, "dynamite_short_v2_silent.mp4")
BGM = os.path.join(ODIR, "bgm.wav")
OUT = os.path.join(ODIR, "dynamite_short_v2.mp4")

def main():
    v = VideoFileClip(SILENT)
    if os.path.exists(BGM):
        a = AudioFileClip(BGM)
        if a.duration >= v.duration: a = a.with_duration(v.duration)
        a = a.with_effects([AudioFadeIn(0.3), AudioFadeOut(0.6)])
        v = v.with_audio(a)
        print(f"BGM: {os.path.basename(BGM)} -> {v.duration:.1f}s")
    v.write_videofile(OUT, fps=30, codec="libx264", audio_codec="aac",
                      threads=os.cpu_count() or 4, preset="medium", bitrate="6000k")
    print(f"[OK] {OUT}")
    if cdb:
        try:
            cdb.upsert_project(PROJECT, title_kr="졸라 한글 레고 쇼츠 v2 — 다이나마이트(춤+군무)",
                description="춤추는 졸라+모든 자모 군무→삐뚤조합→낙하→졸라맨이 주워 던짐→동시완성+영어라벨. 세로 1080x1920",
                local_dir=ODIR, final_path=OUT, bgm_path=BGM,
                runtime_sec=round(float(v.duration), 2), n_scenes=1, status="review",
                notes="v2 모션그래픽. 음악=자작 임시(Dynamite 음원/가사 미포함). 유튜브 업로드 시 공식 음원 추가 예정.")
            print("[DB] 갱신 완료")
        except Exception as e:
            print(f"[WARN] DB: {e}")

if __name__ == "__main__":
    main()
