# -*- coding: utf-8 -*-
"""W24 포즈를 자세별 규격 키에 맞춘 사본을 만든다 (★축소만 한다).

   기준 (사장님 확정 2026-08-04): 서기 100% · 구부림 80% · 의자앉기 60% · 바닥웅크림 50%.
   키는 **머리끝~발끝**만 재고 의자·소품·들어 올린 물건은 안 센다.

   - 원본은 절대 건드리지 않는다. 사본만 assets/graphics/poses/w24n/ 에 만든다.
     (경로에 '/poses/' 가 있어야 렌더러가 캐릭터로 인식한다 — compile_stickman.is_pose)
   - **확대는 하지 않는다.** 키워야 맞는 것(배율 > 1.02)은 손대지 않고 목록으로 보고한다.
     화질이 상하고, 원본이 잘못 그려진 것은 줄여서 될 일이 아니기 때문이다.
   사용: python normalize_w24_poses.py [--dry]
"""
import argparse
import glob
import os

from PIL import Image

import make_w24_consistency_sheet as M

OUT = "assets/graphics/poses/w24n"
MAX_UP = 1.02                      # 이보다 키워야 하면 = 다시 만들 대상. 손대지 않는다.
TOL = 6.0                          # 목표 대비 이 %p 안이면 원본 그대로 쓴다


def main(dry):
    os.makedirs(OUT, exist_ok=True)
    made, kept, todo = [], [], []
    for p in sorted(glob.glob("assets/graphics/poses/w24_*.png")):
        ch, pose = M.char_of(os.path.basename(p)[4:-4])
        if not ch:
            continue
        im = Image.open(p).convert("RGBA")
        hf = M.head_feet(im)
        if not hf:
            continue
        h = hf[1] - hf[0] + 1
        tgt = M.pose_target(pose)
        want = M.SPEC[ch] * tgt / 100.0            # 이 자세에서 나와야 할 머리~발끝 px
        k = want / h
        if abs(h / M.SPEC[ch] * 100 - tgt) < TOL:
            kept.append(os.path.basename(p))
            continue
        if k > MAX_UP:                              # ★키워야 함 → 재생성 대상
            todo.append((ch, pose, round(h / M.SPEC[ch] * 100), tgt, round(k, 3)))
            continue
        if not dry:
            im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))),
                      Image.LANCZOS).save(f"{OUT}/{os.path.basename(p)}")
        made.append((os.path.basename(p), round(k, 3), h, round(want)))

    print(f"{'(모의) ' if dry else ''}=== W24 포즈 규격 맞춤 (축소만) ===")
    print(f"  그대로 사용   {len(kept)}장 (목표 ±{TOL:.0f}%p 이내)")
    print(f"  축소 사본 생성 {len(made)}장 → {OUT}/")
    for n, k, h, w in made[:30]:
        print(f"      {n:<38} {h}px → {w}px  (×{k})")
    if todo:
        print(f"  ★키워야 해서 손대지 않음 {len(todo)}장 — 다시 만들 대상:")
        for ch, pose, r, t, k in todo:
            print(f"      {ch}_{pose:<22} {r}% (목표 {t:.0f}%) — ×{k} 필요")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    raise SystemExit(main(ap.parse_args().dry))
