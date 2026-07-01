#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""setup_w1mon_bg.py — 1주 월요일(KO-W01) 핵심 영상에 경복궁/광화문/세종대왕 배경을 붙인다.

내용·스틱맨·글자·자막은 그대로, 배경만 Flow 파스텔로 교체(첫인상 강화).
- 각 씬 image_prompt spec 에 "bg": "bg_w1mon_s{seq:02d}" 추가.
- 배경 프롬프트 → hangeul_w1mon_bg_prompts.txt (경복궁/광화문/세종 + 씬 사물 포함).
재실행: python setup_w1mon_bg.py
"""
import os
import sys
import json
import sqlite3

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")
EP = "KO-W01"

COMMON = ("soft pastel storybook illustration, gentle warm pastel palette, thick friendly outlines, "
          "flat colors, no text, no modern people, leave the left third and the lower area open for a "
          "character and subtitles, 16:9")

# 씬별 경복궁/광화문/세종 배경 (씬 내용·사물 반영)
BG = {
 1: f"a grand panorama of Gwanghwamun Square with the great bronze seated statue of King Sejong, the Gwanghwamun gate and Gyeongbokgung palace and Bukaksan mountain softly behind, morning light, {COMMON}",
 2: f"interior of an old Gyeongbokgung study hall with tall stacks of thick old Chinese-character books and rolled bamboo scrolls, a puzzled question-mark mood, dim warm light, {COMMON}",
 3: f"interior of Gyeongbokgung Geunjeongjeon throne hall with an empty royal throne and a golden royal crown on a stand, warm compassionate light, {COMMON}",
 4: f"a Gyeongbokgung courtyard with an unfurled glowing Hunminjeongeum manuscript scroll on a low wooden table, soft golden sparkles, {COMMON}",
 5: f"a Gyeongbokgung stone courtyard at night, big calm sky with a round moon above (heaven), flat stone ground below (earth), a single tall wooden pillar (human), starry, {COMMON}",
 6: f"a Gyeongbokgung courtyard at sunrise, the warm sun rising over the eastern tiled rooflines, long soft shadows, {COMMON}",
 7: f"a wide Gyeongbokgung courtyard with clear bright sky above and pale stone ground below emphasized, palace roofs on the horizon, {COMMON}",
 8: f"the serene Hyangwonjeong pavilion and lotus pond garden of Gyeongbokgung, perfectly balanced and harmonious, soft reflections, {COMMON}",
 9: f"a festive bright panorama of Gwanghwamun Square with the bronze King Sejong statue, palace gate behind, cheerful sky, {COMMON}",
 10: f"a clean Gyeongbokgung courtyard with the palace gate and tiled roofs, calm daytime, {COMMON}",
 11: f"the Gyeonghoeru pavilion of Gyeongbokgung standing over a calm reflecting pond, mountains behind, {COMMON}",
 12: f"a long open colonnade walkway of Gyeongbokgung with wooden pillars and tiled roof, soft daylight, {COMMON}",
 13: f"a peaceful Gyeongbokgung flower garden beside a stone palace wall, blossoms, {COMMON}",
 14: f"a warm Gyeongbokgung interior room with a round bronze hand-mirror on a small wooden stand, soft light, {COMMON}",
 15: f"a celebratory Gwanghwamun Square with the King Sejong statue, soft lanterns and a few balloons, warm festive evening glow, {COMMON}",
}


# 씬별 배경 장소 영문 정식 표기(우하단 표시, 없으면 빈칸) — 나중에 찾아갈 수 있게
PLACE_EN = {
    1: "Gwanghwamun Square, Seoul", 2: "Gyeongbokgung Palace, Seoul",
    3: "Gyeongbokgung Palace, Seoul", 4: "Gyeongbokgung Palace, Seoul",
    5: "Gyeongbokgung Palace, Seoul", 6: "Gyeongbokgung Palace, Seoul",
    7: "Gyeongbokgung Palace, Seoul", 8: "Hyangwonjeong, Gyeongbokgung",
    9: "Gwanghwamun Square, Seoul", 10: "Gyeongbokgung Palace, Seoul",
    11: "Gyeonghoeru, Gyeongbokgung", 12: "Gyeongbokgung Palace, Seoul",
    13: "Gyeongbokgung Palace, Seoul", 14: "Gyeongbokgung Palace, Seoul",
    15: "Gwanghwamun Square, Seoul",
}


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    rows = cur.execute("SELECT seq, image_prompt FROM scenes WHERE episode=? ORDER BY seq", (EP,)).fetchall()
    n = 0
    for seq, ip in rows:
        spec = json.loads(ip)
        spec["bg"] = f"bg_w1mon_s{seq:02d}"
        spec["place_en"] = PLACE_EN.get(seq, "")
        cur.execute("UPDATE scenes SET image_prompt=? WHERE episode=? AND seq=?",
                    (json.dumps(spec, ensure_ascii=False), EP, seq))
        n += 1
    con.commit()
    con.close()

    out = os.path.join(ROOT, "hangeul_w1mon_bg_prompts.txt")
    lines = [f"bg_w1mon_s{seq:02d}: {BG[seq]}" for seq in sorted(BG)]
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"added bg to {n} KO-W01 scenes; {len(BG)} prompts -> {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
