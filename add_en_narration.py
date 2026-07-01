#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
완성된 영상에 '영어 나레이션' 오디오 트랙을 추가한다 (한국어 나레이션과 토글 가능).

설계: make_video.py 를 건드리지 않고, 이미 만들어진 <video>.en.srt 의
      씬별 타이밍(start/end)과 영어 텍스트를 그대로 활용한다.
  1) en.srt 파싱 → 각 큐 (start, end, english_text)
  2) 큐마다 영어 TTS 생성(tts_manager, lang=en) → 1.1배속 → 그 슬롯 길이에 맞춤
     (길면 살짝 배속해 압축, 짧으면 슬롯 시작에 두고 뒤는 무음) → 같은 타임라인 정렬
  3) 전체 영어 오디오 트랙을 <video>.en.m4a 로 출력 (유튜브 스튜디오 다국어 오디오 업로드용)
  4) ffmpeg 으로 영상에 2번째 오디오 트랙(eng)으로 내장 — 1번=한국어(기본), 2번=English

사용:
  python add_en_narration.py <video.mp4>            # <video>.en.srt 자동 사용
  python add_en_narration.py <video.mp4> --srt path.en.srt
결과:
  - <video>.mp4 (오디오 ko/en 2트랙 내장, 자막 트랙은 보존)
  - <video>.en.m4a (영어 나레이션 단독 파일)
"""
import os
import sys
import argparse
import subprocess

from tts_manager import save_tts
from moviepy import AudioFileClip, CompositeAudioClip
import moviepy.video.fx as vfx  # MultiplySpeed is generic; make_video.py applies it to audio the same way


def srt_time_to_sec(ts):
    ts = ts.strip().replace(".", ",")
    hh, mm, rest = ts.split(":")
    ss, ms = rest.split(",")
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000.0


def parse_srt(path):
    cues = []
    with open(path, "r", encoding="utf-8") as f:
        blocks = f.read().split("\n\n")
    for blk in blocks:
        lines = [ln for ln in blk.splitlines() if ln.strip() != ""]
        if len(lines) < 2:
            continue
        # lines[0]=index, lines[1]=timecode, lines[2:]=text
        tc = lines[1] if "-->" in lines[1] else (lines[0] if "-->" in lines[0] else None)
        if not tc:
            continue
        start_s, end_s = [p.strip() for p in tc.split("-->")]
        text = " ".join(lines[2:]) if "-->" in lines[1] else " ".join(lines[1:])
        cues.append((srt_time_to_sec(start_s), srt_time_to_sec(end_s), text.strip()))
    return cues


def video_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    ).stdout.strip()
    return float(out)


def main():
    ap = argparse.ArgumentParser(description="영상에 영어 나레이션 오디오 트랙 추가")
    ap.add_argument("video")
    ap.add_argument("--srt", default="", help="영어 SRT (기본: <video>.en.srt)")
    ap.add_argument("--speed", type=float, default=1.1, help="나레이션 배속(채널 기본 1.1)")
    args = ap.parse_args()

    video = os.path.abspath(args.video)
    base, _ = os.path.splitext(video)
    srt_path = args.srt or (base + ".en.srt")
    if not os.path.exists(video):
        print(f"[ERR] 영상 없음: {video}"); sys.exit(1)
    if not os.path.exists(srt_path):
        print(f"[ERR] 영어 SRT 없음: {srt_path}"); sys.exit(1)

    cues = parse_srt(srt_path)
    print(f"[INFO] {len(cues)}개 큐 파싱: {srt_path}")
    vdur = video_duration(video)
    print(f"[INFO] 영상 길이: {vdur:.2f}s")

    tmp_dir = os.path.join(os.path.dirname(video), "_en_tts")
    os.makedirs(tmp_dir, exist_ok=True)

    segments = []
    for i, (start, end, text) in enumerate(cues):
        slot = max(0.1, end - start)
        if not text.strip():
            continue
        mp3 = os.path.join(tmp_dir, f"en_{i:03d}.mp3")
        save_tts(text, mp3, lang="en")
        raw = AudioFileClip(mp3).with_effects([vfx.MultiplySpeed(args.speed)])
        d = raw.duration
        if d > slot:
            # 슬롯보다 길면 살짝 더 배속해 정확히 슬롯 길이에 맞춘다 (다음 씬 침범 방지)
            raw = raw.with_effects([vfx.MultiplySpeed(d / slot)])
        seg = raw.with_start(start)
        segments.append(seg)
        print(f"  cue {i}: slot={slot:.2f}s tts={d:.2f}s -> {'compressed' if d>slot else 'padded'}")

    if not segments:
        print("[ERR] 생성된 영어 세그먼트 없음"); sys.exit(1)

    en_track = CompositeAudioClip(segments).with_duration(vdur)
    en_audio_path = base + ".en.m4a"
    print(f"[INFO] 영어 나레이션 트랙 쓰기: {en_audio_path}")
    en_track.write_audiofile(en_audio_path, codec="aac", fps=44100, logger=None)

    # ffmpeg: 기존 영상(ko 오디오 + 자막 트랙) + en 오디오 → ko(기본)/en 2트랙
    tmp_out = base + ".dub.mp4"
    cmd = [
        "ffmpeg", "-y", "-i", video, "-i", en_audio_path,
        "-map", "0", "-map", "1:a",
        "-c", "copy",
        "-metadata:s:a:0", "language=kor", "-metadata:s:a:0", "title=한국어",
        "-metadata:s:a:1", "language=eng", "-metadata:s:a:1", "title=English",
        "-disposition:a:0", "default", "-disposition:a:1", "0",
        tmp_out,
    ]
    print("[INFO] 오디오 2트랙 내장(mux)...")
    r = subprocess.run(cmd)
    if r.returncode == 0 and os.path.exists(tmp_out):
        os.replace(tmp_out, video)
        print(f"[OK] ko/en 나레이션 2트랙 내장 완료 → {video}")
        print(f"[OK] 유튜브 다국어 오디오 업로드용 파일 → {en_audio_path}")
    else:
        print("[ERR] mux 실패")
        if os.path.exists(tmp_out):
            os.remove(tmp_out)
        sys.exit(1)


if __name__ == "__main__":
    main()
