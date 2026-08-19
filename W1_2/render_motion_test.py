# -*- coding: utf-8 -*-
"""★캐릭터 모션만 보는 테스트 렌더 — 나레이션·자막 없음.

사장님 지시(2026-08-12): "나레이션과 자막에 신경 쓰지 말고 **캐릭터 모션만 완벽하게**
다 만들면서 렌더해서 보여 줘. 배경이나 캐릭터를 **크롭하거나 확대하지 마라**.
캐릭터의 동작을 **정확하고 분명하게 끝까지 다 마친다.**"

- 씬 길이를 **동작 길이(컷수÷fps)** 에 맞춘다 → 동작이 끝나고 우두커니 서 있지 않는다
- 자막·노트박스 없이 배경 + 캐릭터만 합성한다
- 크롭·확대 없음(compose 가 쓰는 apply_camera 는 이미 꺼져 있다)

    python W1_2/render_motion_test.py            # 동작이 있는 씬 전부
    python W1_2/render_motion_test.py 1 2 4 13   # 고른 씬만
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "hangeul_birth_vowels"))
os.environ.setdefault("EDGE_ACTIVE_VOICE", "sunhi")

import sqlite3                                           # noqa: E402
from PIL import Image                                    # noqa: E402
import compile_stickman as cs                            # noqa: E402

OUT = "W1_2/_motion_test"
FPS = 24
DB = "channel/content.db"


def cut_len(con, sname):
    r = con.execute("SELECT beats_json FROM anim_sequences WHERE seq_name=?", (sname,)).fetchone()
    if not r:
        return None
    b = json.loads(r[0])[0]
    if not b.get("oneshot"):
        return None
    return len(b["cycle"]) / float(b.get("fps") or 8.0)


def main():
    want = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else None
    cs.EP = "KO-W1-2"
    scenes = cs.load_scenes("ko")
    con = sqlite3.connect(DB)
    os.makedirs(OUT, exist_ok=True)

    picked = []
    for s in scenes:
        if want and s["seq"] not in want:
            continue
        secs = None
        for o in s["objs"]:
            m = str(o["motion"])
            if m.startswith("gseq:") and ":" in m[5:]:
                L = cut_len(con, m[5:].split(":", 1)[1])
                if L:
                    secs = max(secs or 0, L)
        if secs is None:
            continue                                     # 정지 포즈뿐인 씬은 건너뛴다
        picked.append((s, round(secs + 0.6, 2)))         # 끝나고 0.6초만 여운

    print("모션 씬 %d개" % len(picked))
    frames_dir = os.path.join(OUT, "_frames")
    os.makedirs(frames_dir, exist_ok=True)
    for f in os.listdir(frames_dir):
        os.remove(os.path.join(frames_dir, f))

    k = 0
    for s, secs in picked:
        s = dict(s)
        s["dur"] = secs                                  # ★동작 길이에 씬을 맞춘다
        n = int(secs * FPS)
        print("  S%-2d %5.1f초 · %d프레임 · bg=%s" % (s["seq"], secs, n, s["bg"]))
        for i in range(n):
            fr = cs.compose(s, i / float(FPS), "ko", False)   # overlay=False → 자막 없음
            fr.convert("RGB").save(os.path.join(frames_dir, "f%05d.png" % k))
            k += 1

    out = os.path.join(OUT, "w1d2_motion_test.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(frames_dir, "f%05d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", out], check=True)
    print("\n✅ %s  %d프레임 · %.1f초" % (out, k, k / float(FPS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
