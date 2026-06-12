"""
place_clips.py — 생성 또는 다운로드한 비디오 클립들을
assets/videos/scene_1.mp4 ~ scene_16.mp4 로 순서대로 배치한다.

사용법:
  python place_clips.py "C:\\Users\\antigravity\\Downloads"      # 다운로드 폴더 지정
  python place_clips.py "<폴더>" --by-number                     # 파일명 속 숫자 기준 정렬
  python place_clips.py "<폴더>" --copy                          # 이동(move) 대신 복사(copy)

기본 동작:
  - 폴더의 .mp4 를 '다운로드(생성) 순서'(수정시간)대로 정렬해 scene_1..16 에 매핑한다.
  - --by-number 를 주면 파일명에 들어있는 숫자 기준으로 정렬한다.
  - 매핑 결과 표를 먼저 출력하므로, 정렬이 어긋나면 Ctrl+C 후 옵션을 바꿔 다시 실행한다.
"""
import os
import re
import sys
import shutil
import argparse

sys.stdout.reconfigure(encoding="utf-8")

DEST_DIR = os.path.join("assets", "videos")
EXPECTED = 16


def first_number(name):
    m = re.search(r"\d+", name)
    return int(m.group()) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="다운로드된 .mp4 들이 있는 폴더")
    ap.add_argument("--by-number", action="store_true", help="파일명 속 숫자 기준 정렬")
    ap.add_argument("--copy", action="store_true", help="이동 대신 복사")
    args = ap.parse_args()

    if not os.path.isdir(args.source):
        print(f"[오류] 폴더를 찾을 수 없음: {args.source}")
        sys.exit(1)

    mp4s = [
        os.path.join(args.source, f)
        for f in os.listdir(args.source)
        if f.lower().endswith(".mp4")
    ]
    if not mp4s:
        print(f"[오류] .mp4 파일이 없음: {args.source}")
        sys.exit(1)

    if args.by_number:
        mp4s.sort(key=lambda p: (first_number(os.path.basename(p)) is None,
                                 first_number(os.path.basename(p)) or 0,
                                 os.path.basename(p)))
    else:
        mp4s.sort(key=lambda p: os.path.getmtime(p))

    os.makedirs(DEST_DIR, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"  매핑 미리보기 — {len(mp4s)}개 클립 (정렬: "
          f"{'파일명 숫자' if args.by_number else '다운로드 순서/수정시간'})")
    print(f"{'='*70}")
    plan = []
    for i, src in enumerate(mp4s[:EXPECTED], start=1):
        dest = os.path.join(DEST_DIR, f"scene_{i}.mp4")
        plan.append((src, dest))
        print(f"  {os.path.basename(src):<45} ->  scene_{i}.mp4")
    print(f"{'='*70}")

    if len(mp4s) != EXPECTED:
        print(f"  [경고] .mp4 개수가 {len(mp4s)}개입니다 (기대값 {EXPECTED}). "
              f"앞 {min(len(mp4s), EXPECTED)}개만 배치합니다.")

    op = shutil.copy2 if args.copy else shutil.move
    verb = "복사" if args.copy else "이동"
    for src, dest in plan:
        op(src, dest)
    print(f"\n  완료: {len(plan)}개 클립을 {DEST_DIR}\\ 로 {verb}했습니다.")
    print(f"  다음: python make_video_hypnosis.py  (최종 렌더링)\n")


if __name__ == "__main__":
    main()
