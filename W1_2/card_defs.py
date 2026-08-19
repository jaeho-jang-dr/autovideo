# -*- coding: utf-8 -*-
"""W1-2 **삽화 카드 8장** — 단어마다 글자 옆에 붙는 그림.

시나리오 §0 원칙 2: "**그림과 소리로 익힌다** — 단어마다 삽화 카드를 글자 옆에
붙인다(1:1 매칭)". 글자를 못 읽는 첫 주차라 그림이 뜻을 지고 간다.

## 규칙
· **물건 하나만** 크고 또렷하게. 배경도 소품도 없다
· 배경 그림과 **같은 그림체**(플랫 2D 그림책, 파스텔, 굵은 외곽선)
· ★**글자 절대 금지** — 한글도 영문도 숫자도. 글자는 파라메트릭으로 따로 얹는다
· 흰 바탕 — 나중에 투명컷 떠서 카드 틀 위에 얹는다
"""

STYLE = (
    "Flat 2D children's picture-book illustration of ONE SINGLE OBJECT, centred, drawn "
    "large and filling most of the frame. Clean vector look, soft pastel palette, simple "
    "shapes, bold clean outlines, flat cel shading. Plain pure white background with "
    "nothing else in it - no scenery, no props, no shadow, no frame, no border. "
    "Friendly and clear enough for a small child to recognise at a glance. "
    "★Absolutely NO text, NO letters, NO Korean characters, NO numbers, NO labels "
    "anywhere in the image."
)

# (키, 단어, 뜻, 그림)
CARDS = [
    ("ai",     "아이", "a child",
     "A cheerful little child standing and smiling, seen from the front, waving one hand. "
     "Simple round face, short hair, plain clothes."),

    ("i",      "이",   "a tooth",
     "ONE single clean white tooth - a simple molar shape with a rounded top and two short "
     "roots, drawn large and centred, with a soft blue-grey outline."),

    ("oi",     "오이", "a cucumber",
     "ONE fresh green cucumber lying horizontally, long and slightly curved, with a bumpy "
     "skin texture and a small stem at one end."),

    ("uyu",    "우유", "milk",
     "ONE white milk carton standing upright, a simple gable-top paper carton with a pale "
     "blue band around it and a small drawn milk-drop shape on the front - but NO letters "
     "or words on it at all."),

    ("o",      "오",   "oh! (surprise)",
     "A round friendly face with a big surprised expression - eyes wide open and round, "
     "eyebrows raised high, and the mouth open in a large round O shape. Just the face, "
     "large and centred."),

    ("o5",     "오",   "five",
     "ONE open hand held up palm-forward with ALL FIVE FINGERS spread apart and clearly "
     "separated - thumb, index, middle, ring and little finger, five and no more. Drawn "
     "large and centred, simple and rounded."),

    ("au",     "아우", "younger sibling",
     "Two brothers standing side by side, the taller one on the left with his arm around "
     "the shoulders of the smaller one on the right, both smiling warmly at the viewer. "
     "The size difference between them is clear."),

    ("yeou",   "여우", "a fox",
     "ONE red fox sitting upright and facing the viewer, with a pointed snout, upright "
     "triangular ears, orange-red fur, a white chest and a big bushy tail curled around "
     "beside it."),
]

BY = {k: (word, mean, pic) for k, word, mean, pic in CARDS}


def prompt(key):
    _, _, pic = BY[key]
    return "%s\n\n%s" % (pic, STYLE)


if __name__ == "__main__":
    for k, w, m, _ in CARDS:
        print("%-8s %-5s %-20s %5d자" % (k, w, m, len(prompt(k))))
