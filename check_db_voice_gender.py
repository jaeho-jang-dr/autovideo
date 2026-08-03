# -*- coding: utf-8 -*-
"""DB 발음 클립의 성별 판별 — 남자 음성을 찾아 선희로 다시 만들 목록을 뽑는다 (2026-08-03).

사장님 지시: "데이터베이스에 남자 음성 있으면 선희로 다 바꾼다."

판별은 **기본주파수(F0)** 로 한다. 한국어 성인 기준 여성 ≈ 180~260Hz, 남성 ≈ 90~140Hz.
자기상관으로 프레임마다 F0 을 재고 중앙값을 쓴다. 150Hz 아래면 남자로 본다.

사용:
  python check_db_voice_gender.py            # 판별만
  python check_db_voice_gender.py --list     # 남자로 판정된 것 목록 저장
"""
import argparse
import glob
import os
import subprocess
import wave

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

DIRS = ["web/public/audio/jamo", "assets/audio/w24", "assets/audio"]
MALE_MAX_HZ = 150.0
OUT_LIST = "scratch/w24_male_voice_clips.txt"


def f0_of(mp3):
    """mp3 → 16k 모노 wav 로 뽑아 자기상관으로 F0 중앙값."""
    tmp = os.path.join(os.environ.get("TEMP", "."), "_f0.wav")
    r = subprocess.run(["ffmpeg", "-y", "-i", mp3, "-ac", "1", "-ar", "16000", tmp],
                       capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return None
    with wave.open(tmp, "rb") as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float)
    if len(x) < sr // 4:
        return None
    x = x / (np.abs(x).max() + 1e-9)
    lo, hi = int(sr / 400), int(sr / 70)          # 70~400Hz 탐색
    f0s = []
    win = 1024
    for s in range(0, len(x) - win * 2, win):
        seg = x[s:s + win * 2]
        if np.abs(seg).mean() < 0.04:             # 무음 구간 제외
            continue
        seg = seg - seg.mean()
        ac = np.correlate(seg, seg, "full")[len(seg) - 1:]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        peak = lo + int(np.argmax(ac[lo:hi]))
        if ac[peak] > 0.30:
            f0s.append(sr / peak)
    return float(np.median(f0s)) if len(f0s) >= 3 else None


def main(save):
    files = []
    for d in DIRS:
        files += sorted(glob.glob(f"{d}/*.mp3"))
    files = [f for f in files if os.path.getsize(f) > 2000]
    print(f"검사 대상 {len(files)}개")
    male, female, unknown = [], [], []
    for i, f in enumerate(files):
        v = f0_of(f)
        if v is None:
            unknown.append(f)
        elif v < MALE_MAX_HZ:
            male.append((f, v))
        else:
            female.append((f, v))
        if (i + 1) % 60 == 0:
            print(f"  … {i+1}/{len(files)}")
    print(f"\n여성(선희로 보임) {len(female)} · ★남성 {len(male)} · 판정불가 {len(unknown)}")
    if female:
        print(f"  여성 F0 중앙값 {np.median([v for _f, v in female]):.0f}Hz")
    if male:
        print(f"  ★남성 F0 중앙값 {np.median([v for _f, v in male]):.0f}Hz")
        for f, v in male[:25]:
            print(f"     {v:5.0f}Hz  {f}")
        if len(male) > 25:
            print(f"     … 외 {len(male)-25}개")
        if save:
            os.makedirs("scratch", exist_ok=True)
            with open(OUT_LIST, "w", encoding="utf-8") as w:
                for f, v in male:
                    w.write(f"{f}\t{v:.0f}\n")
            print(f"\n✅ 재생성 대상 목록 → {OUT_LIST}")
    else:
        print("  남성 음성 없음 — 전부 선희로 보인다")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    raise SystemExit(main(ap.parse_args().list))
