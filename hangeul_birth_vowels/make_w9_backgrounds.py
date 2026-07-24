#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_w9_backgrounds.py — KO-W09 '위치·장소' 씬별 해운대(Haeundae) 파스텔 배경 프롬프트.
 - 장소 = 해운대 해변. 씬마다 다른 뷰(해변·마린시티·동백섬·보드워크·카페 + 항공샷 + 구글맵 뷰).
 - 배경은 '은은하게(subtle)': 낮은 채도·단순·여백 많게 → 스틱맨/글자가 튀도록.
 - 좌측 1/3 + 하단은 캐릭터 자리로 비움. no text, no people. 16:9.
출력: hangeul_birth_vowels/w9_bg_prompts.txt  (Gemini 무료 이미지로 씬별 생성 → assets/graphics/bg/bg_w9_sNN.png)
재실행: python hangeul_birth_vowels/make_w9_backgrounds.py
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 은은한 파스텔 + 캐릭터/글자 자리 확보
STYLE = ("soft muted pastel storybook illustration, low saturation, gentle warm palette, "
         "simple minimal detail, light and unobtrusive so foreground pops, thick friendly outlines, "
         "no text, no people, full-frame background covering the whole image, "
         "avoid large buildings or busy props as much as possible, keep it open and simple "
         "(small touches like a few seashells, a conch or a tiny crab are fine), 16:9")
AERIAL = ("high-altitude aerial drone shot, bird's-eye view, ")

# 씬별 (뷰타입, 해운대 모티프)
SCENES = [
 ("wide",  "Haeundae Beach wide crescent bay, calm turquoise sea, soft sand, a few seagulls"),
 ("wide",  "Haeundae seaside boardwalk promenade with benches, the sea on one side"),
 ("wide",  "Haeundae beach with a small lifeguard tower and striped umbrellas near the front"),
 ("wide",  "the tall Marine City skyscrapers of Haeundae seen from the sea, a small sailboat on calm water"),
 ("wide",  "Dongbaek Island green cliff hill with a red-and-white lighthouse beside Haeundae Beach"),
 ("wide",  "Gwangan Bridge arching over the sea in front of Haeundae Beach, open sky"),
 ("wide",  "a striped beach umbrella with a few seashells and a tiny crab on the Haeundae sand"),
 ("wide",  "cozy interior of a bright seaside cafe overlooking Haeundae Beach"),
 ("wide",  "open sandy Haeundae shore under a wide clear sky, gentle waves, outdoors"),
 ("wide",  "the Cheongsapo twin lighthouses, one red one white, on the Haeundae coast"),
 ("wide",  "a Haeundae coastal cliff path looking toward the left, the sea below"),
 ("wide",  "a Haeundae seaside street looking toward the right, cafes and lamp posts"),
 ("wide",  "a friendly neighborhood mart storefront near Haeundae"),
 ("wide",  "a tidy neighborhood school gate near Haeundae"),
 ("wide",  "a Haeundae cafe street with a small bank and a pocket park"),
 ("aerial","the whole crescent of Haeundae Beach with Gwangan Bridge and Marine City"),
 ("wide",  "Haeundae Beach and its buildings along the shore seen from out on the sea"),
 ("wide",  "a Haeundae seaside street crossroad with cafes and shops on both sides"),
 ("aerial","Haeundae streets meeting the beach, the bridge in the distance"),
 ("wide",  "Haeundae Beach at warm sunset, the bridge lights and calm sea, golden-pink pastel sky"),
]

def prompt(view, motif):
    pre = AERIAL if view == "aerial" else ""
    return f"{pre}{motif}, {STYLE}"

def main():
    lines = ["# KO-W09 해운대 씬별 배경 프롬프트 (은은한 파스텔)",
             "# 생성: Gemini 무료 이미지(250/일)로 씬별 1장 → 저장: assets/graphics/bg/bg_w9_sNN.png",
             "# 좌측/하단 비움(캐릭터 자리). no text/people. 16:9.\n"]
    for i, (view, motif) in enumerate(SCENES, 1):
        lines.append(f"## 씬 {i:02d}  [{view}]  → bg_w9_s{i:02d}.png")
        lines.append(prompt(view, motif))
        lines.append("")
    out = os.path.join(ROOT, "hangeul_birth_vowels", "w9_bg_prompts.txt")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    print(f"배경 프롬프트 {len(SCENES)}씬 생성 → {out}")
    print("항공샷:", [i+1 for i,(v,_) in enumerate(SCENES) if v=='aerial'],
          "| 구글맵뷰:", [i+1 for i,(v,_) in enumerate(SCENES) if v=='map'])

if __name__ == "__main__":
    main()
