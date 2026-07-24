# -*- coding: utf-8 -*-
"""W16 면책 자막(자막 전용·무나레이션) 후처리.
 - 영상 끝에 TAIL초 정지 프레임(dock_sunset 마지막 프레임 freeze)을 붙이고
 - 해당 언어 SRT 말미에 면책 자막 1개를 추가한다(각 나라 언어로).
사용: python finalize_w16_disclaimer.py <video.mp4> <lang:ko|en|ja|zh|es> <srt_path> [out.mp4]
"""
import sys, os, re, subprocess, shutil

TAIL = 6.0
DISC = {
    "ko": "이 모든 활동을 남이섬에서 다 할 수 있는 것은 아니에요.\n남이섬은 이 한글 교육 영상의 배경으로만 사용되었어요.",
    "en": "Not all of these activities can actually be done on Nami Island.\nIt was used only as the backdrop for this Korean-learning video.",
    "ja": "これらの活動すべてを南怡島（ナミソム）でできるわけではありません。\n南怡島はこの韓国語学習動画の背景として使われただけです。",
    "zh": "并非所有这些活动都能在南怡岛进行。\n南怡岛只是作为这部韩语教学视频的背景使用。",
    "es": "No todas estas actividades se pueden hacer en la isla de Nami.\nLa isla de Nami se usó solo como escenario para este video de aprendizaje de coreano.",
}


def ff():
    for c in ("ffmpeg", r"C:\ffmpeg\bin\ffmpeg.exe"):
        if shutil.which(c) or os.path.exists(c):
            return c
    return "ffmpeg"


def probe_dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    return float(out.stdout.strip())


def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def append_srt(srt, lang, t0, t1):
    txt = DISC[lang]
    idx = 0
    if os.path.exists(srt):
        for ln in open(srt, encoding="utf-8"):
            if re.match(r"^\d+\s*$", ln.strip()):
                idx = max(idx, int(ln.strip()))
    with open(srt, "a", encoding="utf-8") as f:
        f.write(f"\n{idx+1}\n{ts(t0)} --> {ts(t1)}\n{txt}\n")
    print(f"  SRT 면책 추가: {os.path.basename(srt)} [{lang}] {ts(t0)}~{ts(t1)}")


def extend_video(vin, vout):
    FF = ff()
    # 마지막 프레임을 TAIL초 정지(freeze)로 이어붙임 — tpad clone
    subprocess.run([FF, "-y", "-i", vin,
                    "-vf", f"tpad=stop_mode=clone:stop_duration={TAIL}",
                    "-af", f"apad=pad_dur={TAIL}",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "192k", vout], check=True)
    print(f"  영상 tail {TAIL}s freeze 추가 -> {os.path.basename(vout)}")


if __name__ == "__main__":
    vin = sys.argv[1]; lang = sys.argv[2]; srt = sys.argv[3]
    vout = sys.argv[4] if len(sys.argv) > 4 else vin.replace(".mp4", "_disc.mp4")
    dur = probe_dur(vin)
    append_srt(srt, lang, dur, dur + TAIL)
    extend_video(vin, vout)
    print(f"완료: {vout} (총 {dur+TAIL:.1f}s)")
