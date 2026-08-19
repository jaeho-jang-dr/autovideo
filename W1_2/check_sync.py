# -*- coding: utf-8 -*-
"""배경 사건 ↔ 나레이션 ↔ 자막이 **같은 순간**을 가리키는지 검사한다.

★사장님 지시(2026-08-18)
  "영어판 배경 나레이션 자막 타이밍이 안 맞다. 특히 **밀크**에 관한 것 할 때.
   다시 체크해 보고 배경 자막 나레이션 타이밍 다 새로 맞춰."

## 왜 어긋나나
씬 길이를 늘리면 **그 뒤 씬이 통째로 밀린다.** 좌판 블록에서 입 모양 구간을
18→26초로 늘렸더니 우유가 떨어지는 시각이 +40 에서 **+54.6초**로 밀렸는데,
"우유가 떨어져요" 나레이션은 +42.1초에 그대로 있었다. 12.5초 어긋난 것이다.
씬을 손댈 때마다 **사건 시각을 다시 재서** 나레이션과 맞춰야 한다.

## 무엇을 대조하나
`scene_defs.EVENT` 가 배경 사건 시각을 알고 있고(프레임 실측), 블록 안에서
씬이 이어지는 순서를 더하면 **블록 기준 사건 시각**이 나온다. 그 시각에
나레이션의 어느 줄이 흐르고 있는지 보고, 그 줄이 사건을 말하는 줄인지 본다.

  python W1_2/check_sync.py              # 영어판
  python W1_2/check_sync.py --ko         # 한글판
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

from scene_defs import SCENES, EVENT                     # noqa: E402
from lines_v4 import BLOCKS                              # noqa: E402

# 블록이 어느 씬들로 만들어졌는지 — 씬 렌더 산출물만 적는다
BLOCK_SCENES = {
    3: (3, 4), 4: (5, 6), 6: (8, 9), 61: (10,), 7: (13,),
    10: (15, 16), 12: (23,), 121: (24,), 13: (25, 26),
}
# 그 사건을 말해야 하는 낱말 (없으면 검사에서 건너뛴다)
EVENT_WORD = {
    "stall_cuke": ["오이", "rolling", "굴러"],
    "stall_milk": ["우유", "milk", "falling", "떨어"],
    "fountain_burst": ["오", "fountain", "분수", "솟"],
    "path_fox": ["여우", "fox", "bush", "덤불"],
    "dusk_lanterns": ["등", "lantern", "켜"],
    "plaza_gate": ["비둘기", "pigeon"],
    "plaza_arrive": ["분수", "fountain"],
}
SC = {s[0]: s for s in SCENES}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ko", action="store_true")
    a = ap.parse_args()
    tl = json.load(open("W1_2/_v4_ko_timeline.json" if a.ko else "W1_2/_v3_timeline.json",
                        encoding="utf-8"))
    tl = {b["n"]: b for b in tl}

    print("블록  사건                     사건시각   그때 흐르는 나레이션")
    bad = 0
    for n, scenes in sorted(BLOCK_SCENES.items()):
        b = tl.get(n)
        if not b:
            continue
        t = 0.0
        for sid in scenes:
            s = SC.get(sid)
            if not s:
                continue
            ev = EVENT.get(s[1])
            if ev and ev[1]:
                at = b["start"] + t + ev[1]
                cur = None
                for l in b["lines"]:
                    if l["start"] <= at < l["start"] + l["dur"]:
                        cur = l
                        break
                text = (cur["en"] if cur else "").strip()
                keys = EVENT_WORD.get(s[1], [])
                ok = cur is not None and any(k in text for k in keys)
                if not ok:
                    bad += 1
                print("  B%-2d  S%-2d %-16s +%5.1f초  %s%s"
                      % (n, sid, ev[0][:16], at - b["start"],
                         (text[:46] if cur else "★말이 없다"),
                         "" if ok else "   ★어긋남"))
            t += s[2]
    print("\n★어긋난 사건 %d개" % bad)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
