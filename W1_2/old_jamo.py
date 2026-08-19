# -*- coding: utf-8 -*-
"""훈민정음 **옛 글자 넷**을 획순 엔진에 얹는다 — ㆍ ㅿ ㆁ ㆆ.

★사장님 지시(2026-08-14) "실제로 광화문 광장 분수에 나오는 글자를 그대로 표현해."

광화문광장 한글분수가 표현하는 것은 **훈민정음 28자**(초성 17 + 중성 11)다.
그중 넷은 지금 안 쓰는 옛 글자라 `hangeul_write` 의 획 표에 없었다.

  ㆍ 아래아    천지인의 하늘 — 점 하나
  ㅿ 반치음    ㅅ 의 아래를 닫은 세모
  ㆁ 옛이응    ㅇ 위에 짧은 세로 꼭지
  ㆆ 여린히읗  ㅇ 위에 짧은 가로획

★`hangeul_write.py` 는 검증된 엔진이라 **고치지 않는다.** 대신 이 모듈을 불러
  획 표(`C_STROKES`)에 네 자를 **얹기만** 한다. 엔진의 획순 규칙·좌표계(220 상자)를
  그대로 따르므로 `render_char` / `render_syllable` 이 곧바로 그린다.

★가획 순서는 엔진의 ㅎ 을 그대로 따른다 — 덧획을 먼저 긋고 ㅇ 을 마지막에 닫는다.
  (ㅎ 의 획 표가 ①위 짧은획 ②가로 ③ㅇ 순서다. 새 글자만 다르게 하면 안 어울린다)

    import old_jamo            # 부르기만 하면 등록된다
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import hangeul_write as HW                                  # noqa: E402

BOX = 220


def _circle_ccw(cx, cy, r, n=28):
    """ㅇ 과 같은 반시계 원. 엔진의 것과 같은 모양이 나오게 12시에서 시작한다."""
    pts = []
    for i in range(n + 1):
        a = math.pi / 2 + 2 * math.pi * i / n          # 위 12시 → 반시계
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _spiral(cx, cy, r, turns=3, n=64):
    """가운데에서 밖으로 말아 나가는 한 획 — 굵게 찍으면 **속이 찬 점**이 된다."""
    pts = []
    for i in range(n + 1):
        u = i / float(n)
        a = 2 * math.pi * turns * u
        rr = r * u
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


# ㅎ 의 ㅇ 획을 그대로 빌려 쓴다 — 위에 덧획이 붙는 글자는 원이 조금 아래로 내려간다
_O_UNDER = HW.strokes_of("ㅎ")[2][0]

OLD = {
    # 아래아 — 점 하나. ★원 둘레만 그으면 가운데가 빈 도넛이 된다.
    #   가운데에서 밖으로 **말아 나가는 한 획**으로 그어 속을 채운다(획은 하나 그대로).
    "ㆍ": [(_spiral(110, 112, 15), "①점(하늘)")],

    # 반치음 — ㅅ 의 아래를 닫은 세모. 왼 삐침 → 오른 삐침 → 밑변
    "ㅿ": [([(110, 44), (52, 190)], "①왼 삐침"),
           ([(110, 44), (168, 190)], "②오른 삐침"),
           ([(52, 190), (168, 190)], "③밑변")],

    # 옛이응 — 위 꼭지를 먼저, ㅇ 을 나중에 (엔진의 ㅎ 과 같은 차례)
    "ㆁ": [([(110, 26), (110, 58)], "①위 꼭지"),
           (_O_UNDER, "②ㅇ 반시계")],

    # 여린히읗 — 위 가로획을 먼저, ㅇ 을 나중에
    "ㆆ": [([(62, 46), (158, 46)], "①위 가로획"),
           (_O_UNDER, "②ㅇ 반시계")],
}


# ★복합모음 — 획 표에 없어 W1-2 v3 에서 걸렸다(2026-08-14).
#   ㅘ = ㅗ + ㅏ, ㅝ = ㅜ + ㅓ. 획순은 **먼저 쓰는 모음을 다 긋고 나중 것**을 긋는다.
#   좌표계는 220 상자. ㅗ/ㅜ 는 왼쪽 아래·위로 밀고, ㅏ/ㅓ 는 오른쪽에 세운다.
def _shift(pts, dx, dy, sx=1.0, sy=1.0, cx=110.0, cy=110.0):
    return [((x - cx) * sx + cx + dx, (y - cy) * sy + cy + dy) for x, y in pts]


def _compound(v1, v2):
    """왼쪽(또는 아래) 모음 v1 + 오른쪽 모음 v2 → 획 목록."""
    out = []
    for pts, desc in HW.strokes_of(v1):
        out.append((_shift(pts, -34, 0, 0.62, 0.86), "①" + desc))
    for pts, desc in HW.strokes_of(v2):
        out.append((_shift(pts, 46, 0, 0.86, 0.94), "②" + desc))
    return out


def register():
    HW.C_STROKES.update(OLD)
    # ㅘ·ㅝ 는 모음이라 V_STROKES 쪽을 봐야 하지만, strokes_of 가 C_STROKES 를
    # 먼저 뒤지므로 여기에 얹어도 그대로 걸린다.
    HW.C_STROKES.setdefault("ㅘ", _compound("ㅗ", "ㅏ"))
    HW.C_STROKES.setdefault("ㅝ", _compound("ㅜ", "ㅓ"))
    HW.C_STROKES.setdefault("ㅚ", _compound("ㅗ", "ㅣ"))
    HW.C_STROKES.setdefault("ㅟ", _compound("ㅜ", "ㅣ"))
    return sorted(OLD) + ["ㅘ", "ㅝ", "ㅚ", "ㅟ"]


register()


if __name__ == "__main__":
    from PIL import Image, ImageDraw, ImageFont
    F = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 24)
    S = 240
    ks = ["ㆍ", "ㅿ", "ㆁ", "ㆆ"]
    sh = Image.new("RGB", (S * len(ks), S + 40), (250, 249, 245))
    d = ImageDraw.Draw(sh)
    for i, k in enumerate(ks):
        im = HW.render_char(k, S)
        sh.paste(im, (i * S, 36), im)
        d.text((i * S + S // 2, 6), "%s  %d획" % (k, len(OLD[k])),
               fill=(20, 20, 20), font=F, anchor="ma")
    sh.save("W1_2/_check/old_jamo.png")
    print("W1_2/_check/old_jamo.png", sh.size, "· 등록", register())
