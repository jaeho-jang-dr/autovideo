# -*- coding: utf-8 -*-
"""고친 **블록만** 렌더해서 확인용 짧은 영상을 만든다 (부분 렌더).

★사장님 지시(2026-08-18) "부분으로 랜더해서 교정앱에 띄워서 다시 보여줘."
전체 6분을 다시 그리면 오래 걸린다. 고친 블록만 뽑아 이어 붙이면 몇십 초면 된다.
자막도 그 구간만 잘라 시각을 0부터 다시 매긴다.

  python W1_2/render_blocks.py 9,13            # 영어판 B9·B13
  python W1_2/render_blocks.py 9,13 --ko       # 한글판
"""
import argparse
import glob
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))


def ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("blocks")
    ap.add_argument("--ko", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    want = [int(x) for x in a.blocks.split(",") if x.strip()]

    tlp = "W1_2/_v4_ko_timeline.json" if a.ko else "W1_2/_v3_timeline.json"
    tl = json.load(open(tlp, encoding="utf-8"))
    keep = [b for b in tl if b["n"] in want]
    if not keep:
        raise SystemExit("그런 블록이 없다: %s" % want)

    # 고른 블록만 남긴 타임라인을 만들되, 시각을 0부터 다시 매긴다
    t0 = 0.0
    for b in keep:
        shift = b["start"] - t0
        b["start"] = round(b["start"] - shift, 2)
        for l in b["lines"]:
            l["start"] = round(l["start"] - shift, 2)
        t0 = b["start"] + b["show_sec"]
    sub = "W1_2/_part_timeline.json"
    json.dump(keep, io.open(sub, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 자막도 그 구간만
    srt, idx = [], 1
    for b in keep:
        for l in b["lines"]:
            srt.append("%d\n%s --> %s\n%s\n"
                       % (idx, ts(l["start"]), ts(l["start"] + l["dur"]), l["en"]))
            idx += 1
    out_srt = "W1_2/w1d2_part.srt"
    io.open(out_srt, "w", encoding="utf-8").write("\n".join(srt))

    tag = "ko" if a.ko else "en"
    out = a.out or ("W1_2/w1d2_part_%s_b%s_r%%d.mp4" % (tag, "_".join(map(str, want))))
    env = dict(os.environ)
    env["ASM_TL"] = sub
    env["ASM_OUT"] = out
    env["ASM_TMP"] = "W1_2/_asm_part"
    if a.ko:
        env["ASM_AUD"] = "W1_2/_audio_ko"
    print("블록 %s · %.1f초" % (want, t0))
    subprocess.run([sys.executable, "W1_2/assemble_en_v3.py"], env=env, check=True)
    print("자막 →", out_srt)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
