#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
인트로 / 아웃트로 합성기 — Flow(Veo) 모션 클립 기반.

워크플로 (씬 영상 만들 때와 동일한 파이프라인):
  1) autoveo_flow.py 로 Flow 에서 이미지 생성(Nano Banana) -> 애니메이션 -> Veo 8s 클립 다운로드
     -> intro_outro/scene_1.mp4 (인트로),  scene_2.mp4 / scene_3.mp4 (아웃트로 A/B)
  2) 이 스크립트로 합성: Veo 워터마크 위치(우하단 안쪽)에 채널 로고를 정확히 덮어 가리고
     (크롭하지 않아 구도 100% 유지) + 나레이션(gTTS KR, 1.1배속) + 자막 + 페이드.

결과:
  - assets/intro.mp4  = scene_1 풀 8초 (이미지 1장 -> 8초 동영상)
  - assets/outro.mp4  = scene_2(4초) + scene_3(4초) = 8초 (이미지 2장 합성)

본편 영상에 앞뒤로 붙이기 + 음성 재컴파일 규칙 (★ 새 영상 만들 때마다):
  make_video.py --scenario <대본> --output <out.mp4> \
                --intro assets/intro.mp4 --outro assets/outro.mp4
  - 인트로/아웃트로는 *자체 나레이션이 입혀진 완성품* -> 그대로 앞/뒤에 concat (재컴파일 불필요).
  - 본편 각 씬의 음성은 make_video.py 가 그 영상에 맞게 **자동 재컴파일**한다:
      기존 assets/audio/scene_*.mp3 캐시 강제 삭제 -> 대본으로 TTS 새로 생성 -> 1.1배속 ->
      Veo 클립을 나레이션 길이에 배속 싱크(speed_factor). 즉 대본/클립이 바뀌면 음성도 자동 갱신.
  - 인트로/아웃트로 자체 음성/문구를 바꾸려면 이 스크립트(make_intro_outro.py)를 다시 실행.

나레이션 규칙: 영어 채널명을 한글 발음으로 읽지 않는다("닥터제이 에드" 금지) — 자연스러운 한국어로.
스타일 근거: .harness/context/ted_ed_reverse_engineering.md (컷페이퍼/미색/웜팔레트, 작은 로고).
재현: `python make_intro_outro.py`   (intro_outro/scene_1..3.mp4 클립이 준비돼 있어야 함)
"""
import os
import argparse

from tts_manager import save_tts
from moviepy import (VideoFileClip, AudioFileClip, CompositeAudioClip,
                     CompositeVideoClip, TextClip, concatenate_videoclips)
import moviepy.video.fx as vfx
import moviepy.audio.fx as afx
import numpy as np
import cv2

ROOT = os.path.dirname(os.path.abspath(__file__))

# --- 나레이션 대본 (사람이 수정하는 단일 원천) ---------------------------------
# 영어 채널명을 한글 발음으로 읽지 않는다("닥터제이 에드" 금지). 자연스러운 한국어로.
INTRO_TEXT = "의사의 메스로 세상을 해부하고, 만화가의 상상력으로 꿰맵니다."
OUTRO_TEXT = "새로운 지식의 여정을 응원합니다. 구독과 좋아요로 함께해 주세요."

# --- 규격 ---------------------------------------------------------------------
W, H, FPS = 1280, 720, 24
SPEED = 1.1                 # 나레이션 10% 빠르게 (채널 디폴트)
LEAD = 0.3                  # 페이드인 동안 무음
SEG_INTRO = 8.0            # 인트로 = Flow 클립 1개 풀 8초
SEG_OUTRO = 6.0           # 아웃트로 = 오디오 및 감쇄 벨소리 여운을 포함하여 6초 설정
VIDEO_FADE = 0.4
FONT = r"C:\Windows\Fonts\malgun.ttf"
LOGO = "assets/drjay_ed_logo_circle.png"

# Veo 워터마크(반투명 별)는 세 클립 모두 우하단 안쪽 고정 위치(1280x720 기준 측정값).
# 크롭으로 밀어내면 구도가 잘리므로, 여기에 채널 로고를 정확히 덮어 가린다.
WM_CX, WM_CY, LOGO_SIZE = 1145, 598, 76

# Flow 결과 클립
CLIP_INTRO = "intro_outro/scene_1.mp4"
CLIP_OUTRO_A = "intro_outro/scene_2.mp4"
CLIP_OUTRO_B = "intro_outro/scene_3.mp4"


def _abs(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def wrap_ko(text, max_chars=18):
    """공백 단위로 한국어 자막 줄바꿈(대략 max_chars 기준)."""
    words, lines, cur = text.split(" "), [], []
    for w in words:
        if len(" ".join(cur + [w])) <= max_chars:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return "\n".join(lines)


def load_logo():
    img = cv2.imread(_abs(LOGO), cv2.IMREAD_UNCHANGED)
    if img is None or img.ndim != 3 or img.shape[2] != 4:
        return None
    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)   # MoviePy RGBA 프레임 정합


def make_narration(text, mp3_path, force=True):
    mp3_path = _abs(mp3_path)
    os.makedirs(os.path.dirname(mp3_path), exist_ok=True)
    if force:
        for f in (mp3_path, mp3_path + ".txt"):
            if os.path.exists(f):
                os.remove(f)
    save_tts(text, mp3_path, lang="ko")
    return mp3_path


def narration_audio(mp3_path):
    raw = AudioFileClip(_abs(mp3_path))
    nar = raw.with_effects([vfx.MultiplySpeed(SPEED)])
    fade = min(0.3, nar.duration / 3)
    nar = nar.with_effects([afx.AudioFadeOut(fade)]).with_start(LEAD)
    return nar


def process_clip(path, seconds, logo_rgba):
    """Flow 8s 클립 -> seconds 초로 트림 + 워터마크 위치에 채널 로고를 정확히 덮어
    Veo 워터마크를 가림(크롭하지 않아 전체 구도 100% 유지) -> 720p 정규화."""
    clip = VideoFileClip(_abs(path)).without_audio()
    seconds = min(seconds, clip.duration)
    clip = clip.subclipped(0, seconds)
    w, h = clip.size

    overlay = None
    if logo_rgba is not None:
        ls = LOGO_SIZE
        rl = cv2.resize(logo_rgba, (ls, ls), interpolation=cv2.INTER_AREA)
        # 워터마크 좌표는 1280x720 기준 측정값 -> 실제 클립 해상도에 맞게 스케일
        cx, cy = int(WM_CX * w / W), int(WM_CY * h / H)
        x0, y0 = cx - ls // 2, cy - ls // 2
        x0 = max(0, min(x0, w - ls))
        y0 = max(0, min(y0, h - ls))
        overlay = (x0, y0, x0 + ls, y0 + ls, rl[:, :, :3], rl[:, :, 3:4] / 255.0)

    def f(frame):
        out = frame.copy()
        if overlay is not None:
            xs, ys, xe, ye, lr, la = overlay
            patch = out[ys:ye, xs:xe]
            out[ys:ye, xs:xe] = ((1.0 - la) * patch + la * lr).astype(np.uint8)
        return out

    clip = clip.image_transform(f)
    if (w, h) != (W, H):
        clip = clip.resized((W, H))
    return clip


def subtitle(text, duration):
    # 박스 높이 120, 하단에서 충분히 띄워(화면 밖 잘림 방지) 중앙 배치
    box_h = 120
    txt = TextClip(text=wrap_ko(text), font=FONT, font_size=30, color="white",
                   stroke_color="black", stroke_width=2, method="caption",
                   size=(W - 200, box_h), text_align="center")
    return txt.with_position(("center", H - box_h - 48)).with_duration(duration)


def finalize(base, text, out_path):
    dur = base.duration
    comp = CompositeVideoClip([base, subtitle(text, dur)])
    comp = comp.with_effects([vfx.FadeIn(VIDEO_FADE), vfx.FadeOut(VIDEO_FADE)])
    comp.write_videofile(_abs(out_path), fps=FPS, codec="libx264", audio_codec="aac")
    comp.close()


def build_intro(logo, force=True):
    print("\n=== 인트로 합성 (scene_1 풀 8초) ===")
    mp3 = make_narration(INTRO_TEXT, "assets/audio/intro_narration.mp3", force)
    base = process_clip(CLIP_INTRO, SEG_INTRO, logo).with_audio(
        CompositeAudioClip([narration_audio(mp3)]))
    finalize(base, INTRO_TEXT, "assets/intro.mp4")
    print(f"intro.mp4 완료: {base.duration:.2f}s")


def generate_bell_chime(output_path, duration=1.5, sample_rate=44100):
    import wave
    import struct
    import math
    num_samples = int(sample_rate * duration)
    frequencies = [880.0, 1320.0, 1760.0, 2200.0]
    amplitudes = [0.4, 0.2, 0.1, 0.05]
    decays = [3.0, 5.0, 7.0, 9.0]
    
    frames = []
    for i in range(num_samples):
        t = i / sample_rate
        val = 0.0
        for f, a, d in zip(frequencies, amplitudes, decays):
            val += a * math.sin(2 * math.pi * f * t) * math.exp(-d * t)
        val = max(-1.0, min(1.0, val))
        fade_len = int(sample_rate * 0.1)
        if i > num_samples - fade_len:
            fade_factor = (num_samples - i) / fade_len
            val *= fade_factor
        ival = int(val * 32767)
        frames.append(struct.pack('<h', ival))
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with wave.open(output_path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(b''.join(frames))
    print(f"Generated bell chime sound -> {output_path}")

def build_outro(logo, force=True):
    print("\n=== 아웃트로 합성 (scene_3 종 4초 단독) ===")
    chime_wav = _abs("assets/audio/bell_chime.wav")
    if force or not os.path.exists(chime_wav):
        generate_bell_chime(chime_wav)

    mp3 = make_narration(OUTRO_TEXT, "assets/audio/outro_narration.mp3", force)
    
    # 4초짜리 종/알림벨 클립 단독 사용
    base = process_clip(CLIP_OUTRO_B, SEG_OUTRO, logo)
    
    # 오디오 합성 (나레이션 + 2.5초 시점에 종소리 시작)
    nar = narration_audio(mp3)
    chime = AudioFileClip(chime_wav)
    
    mixed_audio = CompositeAudioClip([
        nar, 
        chime.with_start(2.5)
    ]).with_duration(SEG_OUTRO)
    
    base = base.with_audio(mixed_audio)
    finalize(base, OUTRO_TEXT, "assets/outro.mp4")
    print(f"outro.mp4 완료: {base.duration:.2f}s")


def main():
    ap = argparse.ArgumentParser(description="인트로/아웃트로 합성 (Flow 모션 클립 기반)")
    ap.add_argument("--only", choices=["intro", "outro"])
    ap.add_argument("--no-force", action="store_true", help="나레이션 캐시 재사용")
    args = ap.parse_args()
    force = not args.no_force

    missing = [c for c in (CLIP_INTRO, CLIP_OUTRO_A, CLIP_OUTRO_B)
               if not os.path.exists(_abs(c))]
    need = {"intro": [CLIP_INTRO], "outro": [CLIP_OUTRO_A, CLIP_OUTRO_B]}
    targets = [args.only] if args.only else ["intro", "outro"]
    need_clips = [c for t in targets for c in need[t]]
    blocked = [c for c in need_clips if c in missing]
    if blocked:
        print("[ERR] 필요한 Flow 클립이 없습니다 — 먼저 autoveo_flow.py 로 생성하세요:")
        for c in blocked:
            print(f"   - {c}")
        return

    logo = load_logo()
    if logo is None:
        print(f"[WARN] 로고 로드 실패({LOGO}) — 로고 없이 진행")

    if "intro" in targets:
        build_intro(logo, force)
    if "outro" in targets:
        build_outro(logo, force)
    print("\n[DONE] assets/intro.mp4 / assets/outro.mp4 준비 완료")


if __name__ == "__main__":
    main()
