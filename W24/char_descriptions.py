# -*- coding: utf-8 -*-
"""W24 — Flow 캐릭터 등록용 상세 설명 7종 (2026-07-28).

★첫 클립에서 캐릭터가 왜곡된 원인 = 설명이 한 줄뿐이라 Flow가 인물을 못 잡았다.
  키·체형·얼굴·머리·상의·하의·신발 색까지 못 박아야 일관성이 유지된다.
  색은 실제 등록 이미지에서 샘플링한 값이다.
"""

DESC = {
"injun": """A cartoon Korean young man in his early twenties, drawn in a flat 2D illustration style with bold clean black outlines and flat colours - no gradients, no shading, no texture.

HEIGHT AND BUILD: 180cm tall, the tallest of the group. Slim and upright with a small head relative to the body, roughly seven-and-a-half heads tall, narrow shoulders, straight posture.

FACE: light peach skin (#FCC0A8), simple round face, small black dot eyes, thin black eyebrows, a small closed smile drawn as a short curved line.

HAIR: short black hair (#242424), neatly cut, straight fringe across the forehead, slightly rounded silhouette.

TOP: a plain navy blue short-sleeve t-shirt (#243C60), no pattern, no logo, no text. Round crew neckline, sleeves ending just above the elbow, loose fit.

BOTTOM: beige-khaki straight trousers (#CCB490), full length to the ankle, plain flat colour.

SHOES: pure white low-top sneakers (#FCFCFC), plain, no stripes, no logo, white soles.

CONSISTENCY: keep this exact face, hair, clothing and colour palette in every shot. Only the pose and viewing angle change. Exactly one head, two arms with two hands (five fingers each) and two legs in white sneakers.""",

"zollaman": """A hand-drawn black ink stick figure, drawn like a marker sketch on white paper with visible hand-drawn wobble in every line - not a clean vector shape.

HEIGHT AND BUILD: 178cm tall, the second tallest of the group. Long thin limbs, a large round head relative to the body.

HEAD: a large circle filled with SOLID BLACK hair (#000000) covering the top and sides like a bowl cut, with short spiky strokes along the hairline. The face area is white (#FCFCFC) with two small black oval eyes and a short straight black line for the mouth. No nose.

BODY: a single thick black vertical ink stroke for the torso. No clothes at all - naked line art, no shirt, no trousers.

ARMS AND LEGS: thin black ink strokes, slightly curved, with a wobbling hand-drawn quality. Each hand is a small open oval loop; each foot is a small flattened oval loop pointing outward.

CONSISTENCY: pure black ink on white, no colour anywhere. Keep the SOLID BLACK BOWL-CUT HEAD - this is what distinguishes him from the other two line figures. Exactly one head, two arms with two hands and two legs.""",

"zollagirl": """A hand-drawn black ink stick figure with orange hair, drawn like a marker sketch on white paper with visible hand-drawn wobble.

HEIGHT AND BUILD: 163cm tall, second shortest of the group. Thin limbs, a large round head, lighter lines than zollaman.

HEAD: a large circle OUTLINED in black with a white face inside (#FCFCFC), two small black oval eyes and a short straight black line for the mouth. On top and behind the head is ORANGE HAIR (#E48430) drawn as a rounded cap with a round bun tied at the top-back.

BODY: a thin black vertical ink stroke for the torso. No clothes at all - naked line art, no dress, no skirt.

ARMS AND LEGS: thin delicate black ink strokes. Each hand is a small open oval loop; each foot is a small flattened oval loop pointing outward.

CONSISTENCY: black ink on white with ORANGE as the only colour, used solely for the hair and bun. Keep the outlined white face and the ORANGE BUN - this is what distinguishes her. Exactly one head, two arms with two hands and two legs.""",

"stickman": """The simplest hand-drawn stick figure, drawn with a THICK BLACK MARKER on white paper.

HEIGHT AND BUILD: 175cm tall. Very simple proportions - a round head and four straight limbs, nothing else.

HEAD: a large circle drawn as a bold black OUTLINE only, empty white inside. Two small solid black dot eyes and one short curved line for a small smile. NO HAIR AT ALL, no nose, no ears.

BODY: one thick straight black vertical stroke from the head down to the hips.

ARMS AND LEGS: four thick straight black strokes. The lines simply END - there are NO HANDS, NO FEET, no loops, no shoes.

CONSISTENCY: pure black thick ink on white, no colour anywhere, no clothes. He is the plainest of the three line figures - no hair, no hands, no feet. That bareness is what distinguishes him. Exactly one head, two arms and two legs.""",

"jieun": """A cartoon Korean young woman, drawn in a flat 2D illustration style with clean black outlines and flat colours - no gradients, no shading.

HEIGHT AND BUILD: 165cm tall. Slim, gentle posture, small head relative to the body.

FACE: cream-ivory skin (#F0E4D8), soft round face, small black dot eyes, thin eyebrows, a small closed smile, light pink cheeks.

HAIR: long wavy light brown hair (#B4906C) parted in the middle, falling past the shoulders down to the chest, with soft rounded waves at the ends.

DRESS: a pale yellow sleeveless summer dress (#F0E490) scattered with small darker yellow flower dots (#D8B460). Round neckline, thin shoulder straps, the skirt flaring gently and ending just below the knee. No belt, no logo, no text.

SHOES: simple flat cream shoes (#F0E4D8) with black outlines, no laces, no logo.

CONSISTENCY: keep this exact face, LONG WAVY BROWN HAIR and YELLOW FLORAL DRESS in every shot. Only the pose and viewing angle change. Exactly one head, two arms with two hands (five fingers each) and two legs.""",

"madamjay": """A cartoon Korean woman teacher IN HER FORTIES, drawn in a flat 2D illustration style with clean black outlines and flat colours - no gradients, no shading.

AGE: middle-aged, about 45 years old - a composed, capable homeroom teacher. NOT elderly, NO grey hair, NO wrinkles, NO glasses, NO stooping. She looks healthy and energetic, just older and calmer than the young students.

HEIGHT AND BUILD: 162cm tall, the shortest of the group. Small and neat, upright confident posture.

FACE: ivory skin (#FCFCF0), round friendly face, small black dot eyes, thin eyebrows, a warm closed smile, small pink cheeks. Smooth skin with no age lines.

HAIR: dark brown hair (#483C30), no grey, pulled back and tied in a round BUN at the back of the head, with a few loose strands framing the face.

TOP: a coral-salmon sleeveless apron-vest (#F0786C) worn over a white blouse, with a small chest pocket. No pattern, no logo, no text.

BOTTOM: a plain white knee-length skirt (#FCFCFC), simple A-line shape.

SHOES: plain white flat shoes (#FCFCFC) with black outlines, no laces, no logo.

CONSISTENCY: keep this exact face, BROWN BUN and CORAL APRON over white in every shot. She is a woman in her forties - never draw her as an old woman. Exactly one head, two arms with two hands (five fingers each) and two legs.""",

"teacherjay": """A cartoon Korean man teacher, drawn in a flat 2D illustration style with clean black outlines and flat colours - no gradients, no shading.

HEIGHT AND BUILD: 175cm tall. Slim, friendly, slightly rounded silhouette, small head relative to the body.

FACE: pale ivory skin (#E4E4D8), round face, small black dot eyes, thin eyebrows, a gentle closed smile, no beard.

HAIR: BALD head with a SINGLE THIN CURL of hair sticking up from the crown - one curved black line only. This single curl is his signature and must always be present.

TOP: a blue-and-white CHECKED shirt (#F0FCFC base with blue grid lines), long sleeves rolled up to just below the elbow, collar open at the neck, buttons down the front. No logo, no text.

BOTTOM: beige-khaki straight trousers (#D8C090), full length to the ankle, plain flat colour.

SHOES: white low-top sneakers (#FCFCFC) with black outlines and pale grey soles, no stripes, no logo.

CONSISTENCY: keep this exact BALD HEAD WITH ONE CURL, the BLUE CHECKED SHIRT and beige trousers in every shot. Exactly one head, two arms with two hands (five fingers each) and two legs.""",
}

if __name__ == "__main__":
    import os
    os.makedirs("W24/descriptions", exist_ok=True)
    for k, v in DESC.items():
        p = f"W24/descriptions/{k}.txt"
        open(p, "w", encoding="utf-8").write(v)
        print(f"{k:12s} {len(v):5d}자 → {p}")
