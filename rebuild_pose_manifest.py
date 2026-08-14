# -*- coding: utf-8 -*-
"""assets/graphics/poses/_manifest.json 을 **디스크에 있는 파일 기준**으로 다시 만든다.

★사고 기록(2026-08-11): `register_poses.py` 는 매니페스트에 없는 stickman 행을 **전부 지운다**.
  W1-2 포즈 8개만 든 매니페스트로 돌렸다가 DB 114행이 20행으로 줄었다.
  그래서 **등록 전에는 반드시 이 스크립트로 매니페스트를 디스크와 맞춘 뒤** 등록한다.

설명(ko/en)은 `stickman_factory.POSES` 에 있으면 그것을 쓰고,
없으면 파일명에서 만들어 넣는다(다른 경로로 생성된 캐릭터 포즈들).
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stickman_factory as F                                   # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(ROOT, "assets", "graphics", "poses")
MAN = os.path.join(DIR, "_manifest.json")

# 파일명 앞머리 → 캐릭터 이름
CHAR = {
    "dr_jay": "닥터제이", "madam_jay": "마담제이", "injun": "인준", "jieun": "지은",
    "zm": "졸라맨", "zw": "졸라우먼", "zg": "졸라걸", "z": "졸라맨",
    "w24": "W24", "w1d2": "W1-2",
}


def describe(name):
    """POSES 에 없는 파일 — 이름에서 사람이 읽을 설명을 만든다."""
    parts = name.split("_")
    who = ""
    for k in ("dr_jay", "madam_jay", "injun", "jieun", "zm", "zw", "zg"):
        if name.startswith(k + "_"):
            who = CHAR[k]
            parts = name[len(k) + 1:].split("_")
            break
    act = " ".join(parts)
    ko = f"{who} {act}".strip() if who else act
    return ko, act


def main():
    old = {}
    if os.path.exists(MAN):
        for e in json.load(open(MAN, encoding="utf-8")):
            old[e["name"]] = e

    out = []
    for path in sorted(glob.glob(os.path.join(DIR, "stickman_*.png"))):
        name = os.path.basename(path)[len("stickman_"):-4]
        if name in F.POSES:
            p = F.POSES[name]
            e = {"name": name, "file": f"assets/graphics/poses/stickman_{name}.png",
                 "expr": p.get("expr", "neutral"), "facing": p.get("facing", "front"),
                 "ko": p["ko"], "en": p["en"]}
        elif name in old:
            e = old[name]                                        # 기존 설명 보존
        else:
            ko, en = describe(name)
            e = {"name": name, "file": f"assets/graphics/poses/stickman_{name}.png",
                 "expr": "neutral", "facing": "front", "ko": ko, "en": en}
        out.append(e)

    json.dump(out, open(MAN, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    n_reg = sum(1 for e in out if e["name"] in F.POSES)
    print("매니페스트 %d개 (레지스트리 %d · 그 외 %d) → %s"
          % (len(out), n_reg, len(out) - n_reg, MAN))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
