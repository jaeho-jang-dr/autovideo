# -*- coding: utf-8 -*-
"""W23 씬 배정 감사 — 렌더 전 사전 점검 (2026-07-27).

W23_scenario.md 의 씬 36행을 파싱해서
  ① 배경 파일이 실제로 있는가(정지/동영상)
  ② 시나리오가 부르는 동작 이름 ↔ 실제 만들어진 클립/컷 이름이 맞는가
  ③ 만들어 둔 동작 컷이 **전부 쓰이는가** (사장님 지시: 캐릭터 동영상 모두 사용)
  ④ 정지 포즈가 전부 있는가
를 표로 뽑는다. 출력은 콘솔 + scratch/w23_scene_audit.md
"""
import glob
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
SCEN = "W23/W23_scenario.md"
BG_STILL = "assets/graphics/bg"
BG_MOV = "W23/bg_clips"
POSE_STILL = "W23/poses_still_norm"
CUTS = "W23/poses"


def parse():
    scenes = []
    for ln in open(SCEN, encoding="utf-8"):
        m = re.match(r"- \*\*(S\d+)\*\* (.+)", ln.strip())
        if not m:
            continue
        parts = [p.strip() for p in m.group(2).split("|")]
        if len(parts) < 5:
            continue
        title, glyph, narr, bg, motion = parts[0], parts[1], parts[2], parts[3], parts[4]
        tag = parts[5] if len(parts) > 5 else ""
        bm = re.match(r"`([^`]+)`\[(\w+)\]", bg)
        scenes.append({
            "id": m.group(1), "title": title, "glyph": glyph.strip("`"),
            "bg": bm.group(1) if bm else bg, "bgtype": bm.group(2) if bm else "?",
            "motion": motion, "tag": tag, "narr": narr,
        })
    return scenes


def have_cuts():
    ks = set()
    for p in glob.glob(f"{CUTS}/injun_w23_*_*.png"):
        m = re.match(r"injun_w23_(.+)_\d+$", os.path.basename(p)[:-4])
        if m:
            ks.add(m.group(1))
    return ks


def have_stills():
    return {os.path.basename(p).replace("injun_w23_", "")[:-4]
            for p in glob.glob(f"{POSE_STILL}/injun_w23_*.png")}


def main():
    scenes = parse()
    cuts, stills = have_cuts(), have_stills()
    out = ["# W23 씬 배정 감사 (렌더 전 사전 점검)", "",
           f"- 씬 {len(scenes)}개 · 제작된 동작컷 {len(cuts)}종 · 정지 포즈 {len(stills)}종", ""]

    # ① 배경
    bgs = Counter((s["bg"], s["bgtype"]) for s in scenes)
    out += ["## ① 배경 파일 존재 여부", "", "| 배경키 | 종류 | 쓰는 씬 수 | 파일 |", "|---|---|---|---|"]
    miss_bg = []
    for (k, t), n in sorted(bgs.items()):
        if t == "VIDEO":
            ok = os.path.exists(f"{BG_MOV}/bg_w23_{k}.mp4")
            f = f"{BG_MOV}/bg_w23_{k}.mp4"
        else:
            ok = os.path.exists(f"{BG_STILL}/bg_w23_{k}.png")
            f = f"{BG_STILL}/bg_w23_{k}.png"
        if not ok:
            miss_bg.append(k)
        out.append(f"| `{k}` | {t} | {n} | {'✅' if ok else '❌ 없음'} {f} |")

    # ② 동작 이름 매칭
    named = Counter()
    for s in scenes:
        for w in re.findall(r"[a-z_]{3,}", s["motion"]):
            named[w] += 1
    out += ["", "## ② 시나리오가 부르는 동작/포즈 이름", "",
            "| 이름 | 씬 수 | 실제 자산 |", "|---|---|---|"]
    unknown = []
    for w, n in sorted(named.items(), key=lambda x: -x[1]):
        if w in cuts:
            kind = "동작컷 ✅"
        elif w in stills:
            kind = "정지 ✅"
        elif w in ("walk_r", "walk_l"):
            kind = "걷기컷 ✅"
        else:
            kind = "❌ 자산 없음"
            unknown.append(w)
        out.append(f"| `{w}` | {n} | {kind} |")

    # ③ 만든 동작컷이 전부 쓰이는가
    used = {w for w in named if w in cuts}
    unused = sorted(cuts - used - {"walk_l", "walk_r"})
    out += ["", "## ③ 제작 동작컷 사용 현황 (★사장님 지시: 전부 사용)", "",
            f"- 사용 {len(used)}종: {', '.join(sorted(used)) or '없음'}",
            f"- **미사용 {len(unused)}종: {', '.join(unused) or '없음'}**"]

    # ④ 정지 포즈
    used_st = {w for w in named if w in stills}
    out += ["", "## ④ 정지 포즈 사용 현황", "",
            f"- 사용 {len(used_st)}종 / 보유 {len(stills)}종",
            f"- 미사용: {', '.join(sorted(stills - used_st)) or '없음'}"]

    out += ["", "## ⑤ 즉시 조치 필요", "",
            f"- 배경 파일 없음 **{len(set(miss_bg))}키**: {', '.join(sorted(set(miss_bg)))}",
            f"- 이름만 있고 자산 없음 **{len(unknown)}개**: {', '.join(unknown)}",
            f"- 미사용 동작컷 **{len(unused)}종** → 씬 재배정 필요"]

    txt = "\n".join(out)
    os.makedirs("scratch", exist_ok=True)
    open("scratch/w23_scene_audit.md", "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
