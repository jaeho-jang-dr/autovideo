# -*- coding: utf-8 -*-
"""**전체를 다시 그리지 않고 그 블록만 갈아 끼운다.**

★사장님 지시(2026-08-18)
  "부분 랜더 한다고 전체가 타이밍이 엉클어지거나 하면 안 된다. 전체 렌더 하면서
   부분만 고치면서 나레이션·자막·배경 타이밍을 다 보고 교정앱에 보여주는
   **전번 판 부분 랜더 도구가 더 유용하다.** 그것을 찾아서 앞으로 계속 쓰자."

앞서 만든 `render_blocks.py` 는 고친 블록만 **따로 떼어** 짧은 영상을 만들었다.
그건 그 대목만 확인할 뿐, 앞뒤와의 이음새·전체 타이밍을 볼 수 없다.
이 도구는 `patch_scene.py`(W12 등에서 쓰던 것)와 같은 방식이다 —
**[앞부분 | 새로 그린 블록 | 뒷부분]** 으로 이어 붙여 **온전한 전체 영상**을 낸다.

## 안전장치 — 길이가 바뀌면 붙이지 않는다
블록 길이가 달라지면 뒤 타임라인이 통째로 밀린다. 그런 경우에는 이어 붙이지 않고
"전체 렌더가 필요하다" 고 알린다. 붙일 수 있는 것은 **길이가 같은 교정**뿐이다
(포즈 교체·크기 조정·배경 갈아 끼우기 따위).

  python W1_2/patch_blocks.py <원본.mp4> 9,13
  python W1_2/patch_blocks.py <원본.mp4> 9 --ko
"""
import argparse
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

FPS = 24


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(r.stdout.strip())


def cut(src, t0, t1, out):
    """구간을 잘라 낸다 — 프레임 정확도를 위해 다시 인코딩한다."""
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", src, "-ss", "%.3f" % t0]
    if t1 is not None:
        cmd += ["-to", "%.3f" % t1]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-avoid_negative_ts", "make_zero", out]
    subprocess.run(cmd, check=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="갈아 끼울 원본 영상")
    ap.add_argument("blocks")
    ap.add_argument("--ko", action="store_true")
    a = ap.parse_args()
    want = [int(x) for x in a.blocks.split(",") if x.strip()]

    tlp = "W1_2/_v4_ko_timeline.json" if a.ko else "W1_2/_v3_timeline.json"
    tl = json.load(open(tlp, encoding="utf-8"))
    total_new = sum(b["show_sec"] for b in tl)
    total_old = dur(a.src)
    if abs(total_new - total_old) > 0.2:
        # ★길이가 달라졌으면 **그 블록 뒤가 통째로 밀린다.** 다만 고친 블록부터
        #   끝까지 다 갈아 끼우면 밀림이 흡수된다 — 앞부분만 그대로 쓰면 되므로
        #   그래도 전체 렌더보다 훨씬 빠르다. 뒤 블록을 다 지정했는지 확인한다.
        tail = [b["n"] for b in tl if b["start"] >= min(x["start"] for x in tl if x["n"] in want) - 0.01]
        if set(tail) - set(want):
            print("★전체 길이가 달라졌다 — 옛 %.1f초 / 새 %.1f초" % (total_old, total_new))
            print("  블록 길이가 바뀌면 **그 뒤가 통째로 밀린다.**")
            print("  고친 블록부터 끝까지 지정하면 붙일 수 있다:  %s"
                  % ",".join(str(x) for x in tail))
            return 1
        print("길이가 %.1f → %.1f초로 바뀐다 (고친 블록부터 끝까지 다시 그린다)"
              % (total_old, total_new))

    keep = sorted((b for b in tl if b["n"] in want), key=lambda b: b["start"])
    if not keep:
        raise SystemExit("그런 블록이 없다: %s" % want)

    tmp = "W1_2/_patch"
    os.makedirs(tmp, exist_ok=True)
    for f in glob.glob(tmp + "/*.mp4"):
        os.remove(f)

    # ① 갈아 끼울 블록만 렌더 (전체 타임라인 중 그 블록만 그린다)
    parts, cur = [], 0.0
    for i, b in enumerate(keep):
        if b["start"] > cur + 0.01:
            parts.append(cut(a.src, cur, b["start"], "%s/keep%d.mp4" % (tmp, i)))
        one = "%s/blk%d.json" % (tmp, b["n"])
        bb = dict(b)
        shift = bb["start"]
        bb["start"] = 0.0
        bb["lines"] = [dict(l, start=round(l["start"] - shift, 2)) for l in b["lines"]]
        json.dump([bb], open(one, "w", encoding="utf-8"), ensure_ascii=False)
        env = dict(os.environ)
        env["ASM_TL"] = one
        env["ASM_OUT"] = "%s/new%d_r%%d.mp4" % (tmp, b["n"])
        env["ASM_TMP"] = "W1_2/_asm_patch"
        if a.ko:
            env["ASM_AUD"] = "W1_2/_audio_ko"
        subprocess.run([sys.executable, "W1_2/assemble_en_v3.py"], env=env, check=True)
        made = sorted(glob.glob("%s/new%d_r*.mp4" % (tmp, b["n"])))[-1]
        parts.append(made)
        cur = b["start"] + b["show_sec"]
        print("  B%d 갈아 끼움 (%.1f~%.1f초)" % (b["n"], b["start"], cur))
    if cur < total_old - 0.05:
        parts.append(cut(a.src, cur, None, "%s/tail.mp4" % tmp))

    lst = "%s/list.txt" % tmp
    with open(lst, "w", encoding="utf-8") as f:
        for p in parts:
            f.write("file '%s'\n" % os.path.abspath(p).replace("\\", "/"))
    v = 1 + len(glob.glob("W1_2/w1d2_patched_r*.mp4"))
    out = "W1_2/w1d2_patched_r%d.mp4" % v
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", out], check=True)
    print("\n%s  %.1f초 (원본 %.1f초)" % (out, dur(out), total_old))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
