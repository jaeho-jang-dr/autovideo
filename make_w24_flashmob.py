# -*- coding: utf-8 -*-
"""W24 플래시몹 합본 — 클립 체인 연결 + 워터마크 로고 덮기 + BGM (2026-08-03).

지금까지 ad-hoc ffmpeg 으로 만들던 합본 절차를 그대로 스크립트로 고정했다.
로고 좌표는 `W24_flashmob_logo.mp4` 를 역산해 확정한 값이다(템플릿 매칭 err 5.82).

체인: 각 클립의 **마지막 프레임**이 다음 클립의 첫 프레임이라 이어 붙이면 끊김이 없다.
  1 점화 → 2 짝 댄스 → 3 부감 원 정렬 → 4 눈높이 복귀·최종 포즈 → **5 폭죽 피날레**

사용:
  python make_w24_flashmob.py              # 있는 클립까지만 붙인다
  python make_w24_flashmob.py --out W24/W24_flashmob_v3.mp4
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

FPS = 24
W, H = 1280, 720
MP3 = "W24/Never Coming Down - The Soundlings.mp3"
LOGO = "assets/drjay_ed_logo_circle.png"
LOGO_SIZE, LOGO_X, LOGO_Y = 60, 1128, 568   # ★Veo 반짝임 워터마크(48px @1159,599 중심) 덮기
FADE = 1.5                                   # 끝맺음 — 마지막 1.5초 음악 페이드아웃

# ★순서 고정. 파일명은 Flow 다운로드 이름 그대로 둔다(재생성하면 여기만 바꾼다).
CLIPS = [
    ("1 점화",            "W24/dance/Flash_mob_in_plaza_building_202607281715.mp4"),
    ("2 짝 댄스",         "W24/dance/Seven_dancers_in_plaza_202607281622.mp4"),
    ("3 부감 원 정렬",    "W24/dance/Dancers_form_circle_in_plaza_202607281628.mp4"),
    ("4 눈높이·최종포즈", "W24/dance/Seven_dancers_in_neon_plaza_202607281635.mp4"),
    ("5 폭죽 피날레",     "W24/dance/clip5_finale.mp4"),
]


def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())


def main(out):
    have, missing = [], []
    for label, p in CLIPS:
        (have if os.path.exists(p) else missing).append((label, p))
    for label, p in missing:
        print(f"  ★없음: {label} — {p}")
    if not have:
        raise SystemExit("붙일 클립이 하나도 없다")

    total = 0.0
    for label, p in have:
        d = dur(p)
        print(f"  {label:16s} {d:6.2f}s  {os.path.basename(p)}")
        total += d
    print(f"  = 합계 {total:.2f}s ({len(have)}클립)")

    # 소스 클립의 Veo 오디오는 버리고 BGM 만 쓴다 → 영상만 concat 한 뒤 음악을 얹는다.
    n = len(have)
    parts = "".join(f"[{i}:v]" for i in range(n))
    fc = (f"{parts}concat=n={n}:v=1:a=0[v];"
          f"[{n}:v]scale={LOGO_SIZE}:{LOGO_SIZE}[lg];"
          f"[v][lg]overlay={LOGO_X}:{LOGO_Y}[vout];"
          f"[{n+1}:a]afade=t=out:st={total-FADE:.2f}:d={FADE}[aout]")

    cmd = ["ffmpeg", "-y"]
    for _, p in have:
        cmd += ["-i", p]
    cmd += ["-i", LOGO, "-i", MP3,
            "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
            "-t", f"{total:.3f}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
            "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", out]
    print(f"  렌더 → {out}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2500:])
        raise SystemExit("★ffmpeg 실패")
    print(f"✅ {out}  {os.path.getsize(out)//1024}KB  {dur(out):.2f}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="W24/W24_flashmob_v3.mp4")
    a = ap.parse_args()
    print("=== W24 플래시몹 합본 ===")
    main(a.out)
