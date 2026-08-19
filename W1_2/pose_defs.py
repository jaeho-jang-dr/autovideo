# -*- coding: utf-8 -*-
"""W1-2 졸라맨·졸라걸 **정지 포즈** 규격.

동작(동영상)이 아니라 **한 장짜리 포즈**다. 씬에서 가만히 서 있거나 물건을 든 채
말하는 구간에 쓴다. 동영상으로 뽑을 이유가 없는 것들이다.

기준 이미지는 동작 클립과 **같은 것**을 쓴다(`W1_2/motion_src/guide_z*_front.png`) —
그래야 정지와 무빙이 딴사람이 되지 않는다([[character-guide-image-flow-unify]]).
스타일 락도 `motion6_defs` 의 것을 그대로 물려받는다.

    python W1_2/flow_make_pose12.py --all
    python W1_2/flow_make_pose12.py zman_attention
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import motion6_defs as M  # noqa: E402

# 정지 포즈 공통 — 한 장이므로 시간 지시가 없고, 자세를 또렷하게 못 박는다
STILL = """A SINGLE STILL POSE, not a sequence. He holds this one pose, standing squarely
and steadily, seen from the FRONT, square-on to the camera, whole body inside the frame
and centred. Plain white background, nothing else in the picture.

""" + M.COUNT_HARD

STILL_F = STILL.replace(" He holds", " She holds")

# ★앉은 포즈 전용 — 공통 STILL 에는 "standing squarely" 가 박혀 있어서 그 위에 "sits" 를
#   얹으면 **서로 어긋나고 Flow 는 서 있는 쪽을 따른다**(zman_shoulder_recv 실패, 2026-08-12).
SIT = """A SINGLE STILL POSE, not a sequence. HE IS SEATED - he is NOT standing at any
point in this picture. He sits on an invisible seat at about knee height: knees bent,
thighs horizontal, shins vertical, both feet flat on the ground, back straight.
There is no chair, bench or stool drawn - only the figure, sitting as if one were there.
Seen from the FRONT, square-on to the camera, whole body inside the frame and centred.
Plain white background, nothing else in the picture.

""" + M.COUNT_HARD


# ★선이 **꽉 찬** 검은 획이어야 한다. 속 빈 윤곽선으로 그리면 몸 전체 안쪽이 하나의
#   큰 구멍이 되어 머리를 잴 수 없다(sm_greeting_wave 1차 실패 · 2026-08-12).
SOLID = """THE LINES ARE SOLID, FILLED BLACK STROKES - like ink from a thick marker pen.
Each arm, each leg, the torso and the neck is ONE solid black line. They are NOT hollow:
do not draw them as thin outlines with white inside, do not double the lines, do not leave
any limb as an empty tube. Only the inside of the head circle is white, so the eyes and
mouth can sit in it."""


def _p(style, body):
    return "%s\n\n%s" % (body, style)


# (키, 기준이미지, 프롬프트)
POSES = [
    # ── 졸라맨 ────────────────────────────────────────────────────────
    ("zman_attention", "zman_front", _p(M.ZMAN_STYLE + "\n\n" + STILL,
     "Zollaman STANDS TO ATTENTION - feet together, back straight, and BOTH ARMS "
     "held straight down flat against his sides, hands touching his thighs. His whole "
     "body makes one clean vertical line, like the letter I. He looks straight ahead.")),

    ("zman_hands_up", "zman_front", _p(M.ZMAN_STYLE + "\n\n" + STILL,
     "Zollaman THROWS BOTH ARMS STRAIGHT UP in celebration - both arms raised high above "
     "his head, elbows straight, hands open. His face is turned up and happy. Feet planted "
     "apart. Both arms go up together on either side of his head, symmetrical.")),

    ("zman_card_hold", "zman_front", _p(M.ZMAN_STYLE + "\n\n" + STILL,
     "Zollaman HOLDS UP A BLANK WHITE CARD with both hands, at chest height, the card "
     "turned to face the camera squarely so its front is fully visible. The card is a plain "
     "empty white rectangle with a thin outline - NOTHING is drawn or written on it. He "
     "stands behind it looking at the camera.")),

    ("zman_mirror", "zman_front", _p(M.ZMAN_STYLE + "\n\n" + STILL,
     "Zollaman HOLDS A SMALL HAND MIRROR up in one hand, at face height and slightly to "
     "the side, looking into it. The mirror is a simple oval with a short handle, its face "
     "blank white - nothing reflected in it, no drawing inside. His other arm hangs at his "
     "side.")),

    ("zman_arms_wide", "zman_front", _p(M.ZMAN_STYLE + "\n\n" + STILL,
     "Zollaman OPENS BOTH ARMS WIDE to the sides, as if showing the whole place around him "
     "- arms out level with his shoulders, elbows straight, palms open and facing forward, "
     "one arm to the left and one to the right, symmetrical. Feet planted apart, smiling.")),

    ("zman_shoulder_recv", "zman_front", _p(M.ZMAN_STYLE + "\n\n" + SIT,
     "Zollaman is SITTING DOWN, facing the camera, with both hands resting flat on his own "
     "knees. He is relaxed and pleased, looking straight at the camera. Nobody else is in "
     "the picture. ★He is sitting, not standing - his knees are bent and his thighs are "
     "level, so he is clearly lower than his standing height.")),

    ("zman_mouth_a", "zman_front", _p(M.ZMAN_STYLE + "\n\n" + STILL,
     "Zollaman stands relaxed with both arms at his sides, looking at the camera, and his "
     "MOUTH IS OPEN WIDE AND ROUNDED into a big open shape - the shape of saying 'AH'. The "
     "open mouth is large and unmistakable, drawn as a bold open oval. Everything else "
     "about his face is unchanged.")),

    ("zman_mouth_u", "zman_front", _p(M.ZMAN_STYLE + "\n\n" + STILL,
     "Zollaman stands relaxed with both arms at his sides, looking at the camera, and his "
     "MOUTH IS PUSHED FORWARD INTO A SMALL TIGHT CIRCLE, lips pursed - the shape of saying "
     "'OO'. The small round mouth is unmistakable. Everything else about his face is "
     "unchanged.")),

    # ── 스틱맨 ────────────────────────────────────────────────────────
    # ★모션 문서에 이름만 써 놓고 안 만들었던 것들. 스틱맨은 검은 선이라
    #   `M.LOCK` 계열 스타일을 쓴다(졸라 스타일을 쓰면 머리카락이 생긴다).
    # ★1차 생성이 **속 빈 윤곽선** 화풍으로 나와 못 썼다(몸 전체가 하나의 큰 구멍이 되어
    #   머리를 못 재고 크기가 5배 틀어졌다 · 2026-08-12). 선이 꽉 찼음을 따로 못 박는다.
    ("sm_greeting_wave", "front", _p(M._STYLE + "\n\n" + SOLID + "\n\n" + STILL,
     "The stickman WAVES HELLO - one arm raised up beside his head, elbow bent, hand open "
     "and turned toward the viewer in a wave. The other arm hangs relaxed at his side. He "
     "stands facing the camera, friendly and welcoming.")),

    ("sm_presenting", "front", _p(M._STYLE + "\n\n" + STILL,
     "The stickman PRESENTS with both hands - both arms held out in front of him at about "
     "chest height, elbows softly bent, palms open and turned upward, as if offering "
     "something to the viewer or introducing what comes next. He faces the camera.")),

    ("sm_pointing_left", "front", _p(M._STYLE + "\n\n" + STILL,
     "The stickman POINTS TO HIS OWN LEFT - which is the viewer's RIGHT side of the "
     "picture. That whole arm is raised and held straight out sideways at shoulder height, "
     "the index finger extended and clearly pointing. His head is turned to look the same "
     "way. The other arm hangs at his side.")),

    ("sm_counting_five", "front", _p(M._STYLE + "\n\n" + STILL,
     "The stickman HOLDS UP ONE HAND with ALL FIVE FINGERS SPREAD APART and clearly "
     "separated - thumb, index, middle, ring and little finger, five and no more. The arm "
     "is raised so the open hand is beside his head, palm turned toward the viewer. The "
     "other arm hangs at his side. He looks at the camera.")),

    ("sm_arms_out_wide", "front", _p(M._STYLE + "\n\n" + STILL,
     "The stickman OPENS BOTH ARMS WIDE to the sides - arms out level with his shoulders, "
     "elbows straight, hands open, one arm to the left and one to the right, symmetrical, "
     "as if weighing two things against each other. Feet planted apart, facing the camera.")),

    ("sm_holding_mirror", "front", _p(M._STYLE + "\n\n" + STILL,
     "The stickman HOLDS A SMALL HAND MIRROR up in one hand, at face height and slightly to "
     "the side, looking into it. The mirror is a simple oval with a short handle, its face "
     "blank white - nothing reflected in it, no drawing inside. His other arm hangs at his "
     "side.")),

    # ── 졸라걸 ────────────────────────────────────────────────────────
    ("zgirl_attention", "zgirl_front", _p(M.ZGIRL_STYLE + "\n\n" + STILL_F,
     "Zollagirl STANDS TO ATTENTION - feet together, back straight, and BOTH ARMS held "
     "straight down flat against her sides, hands touching her thighs. Her whole body makes "
     "one clean vertical line, like the letter I. She looks straight ahead.")),

    ("zgirl_hands_up", "zgirl_front", _p(M.ZGIRL_STYLE + "\n\n" + STILL_F,
     "Zollagirl THROWS BOTH ARMS STRAIGHT UP in celebration - both arms raised high above "
     "her head, elbows straight, hands open. Her face is turned up and happy. Feet planted "
     "apart. Both arms go up together on either side of her head, symmetrical.")),

    ("zgirl_card_hold", "zgirl_front", _p(M.ZGIRL_STYLE + "\n\n" + STILL_F,
     "Zollagirl HOLDS UP A BLANK WHITE CARD with both hands, at chest height, the card "
     "turned to face the camera squarely so its front is fully visible. The card is a plain "
     "empty white rectangle with a thin outline - NOTHING is drawn or written on it. She "
     "stands behind it looking at the camera.")),

    ("zgirl_mirror", "zgirl_front", _p(M.ZGIRL_STYLE + "\n\n" + STILL_F,
     "Zollagirl HOLDS A SMALL HAND MIRROR up in one hand, at face height and slightly to "
     "the side, looking into it. The mirror is a simple oval with a short handle, its face "
     "blank white - nothing reflected in it, no drawing inside. Her other arm hangs at her "
     "side.")),

    ("zgirl_arms_wide", "zgirl_front", _p(M.ZGIRL_STYLE + "\n\n" + STILL_F,
     "Zollagirl OPENS BOTH ARMS WIDE to the sides, as if showing the whole place around her "
     "- arms out level with her shoulders, elbows straight, palms open and facing forward, "
     "one arm to the left and one to the right, symmetrical. Feet planted apart, smiling.")),

    # ══ 수문장 스틱맨 (사장님 지시 2026-08-13) ═══════════════════════════
    #   "스틱맨을 수문장으로 만들 때는 기본 스틱맨에서 **수문장 스틱맨 정지 이미지를
    #    하나 그리고**, 모자·검·의복 등이 갖춰지되 **그러나 스틱맨이란 것이 잘 드러나는**
    #    그것으로 다시 동영상을 만든다."
    #   → 동영상을 바로 뽑으면 Flow 가 사람으로 그려 버린다. 먼저 **정지 한 장**을
    #     만들어 그것을 기준 이미지로 삼아야 스틱맨 그림체가 유지된다.
    #   ★핵심 — 몸은 여전히 **가는 검은 선**이고 머리는 **빈 동그라미**다.
    #     모자·옷·검은 그 선 위에 얹은 **몇 개의 단순한 도형**일 뿐이다.
    ("stickman_guard", "side", _p(M.LOCK + "\n\n" + STILL,
     "The stickman is dressed as a PALACE GATE GUARD, standing at attention with a tall "
     "pole held upright beside him.\n\n"
     "★★HE IS SEEN FROM THE SIDE - EXACT PROFILE, 90 DEGREES, FACING RIGHT.\n"
     "This is the most important thing about the picture and the first version got it "
     "wrong by drawing him front-on. We are looking at his LEFT side. Therefore:\n"
     "  · his NOSE and CHIN break the outline of the head circle on the RIGHT-hand side\n"
     "  · only ONE EYE is visible, near the right edge of the head\n"
     "  · his two shoulders line up one behind the other, so the body reads as a single "
     "narrow vertical line - NOT a wide front-facing torso\n"
     "  · the near arm is drawn fully; the far arm is mostly hidden behind the body\n"
     "  · his two feet point to the RIGHT, one slightly behind the other\n"
     "  · the hat brim is seen edge-on, so it reads as a long flat line either side of "
     "the head, not as a circle around it\n"
     "  · the robe hangs as a narrow shape down his side, not spread wide across him\n"
     "He does NOT face the camera. He does NOT stand three-quarters on. Exact profile.\n\n"
     "★HE IS STILL UNMISTAKABLY A STICKMAN - THAT MATTERS MORE THAN THE COSTUME.\n"
     "His body is the same thin black lines: a plain round head circle, one straight line "
     "for the spine, one line per arm, one line per leg. The costume is only a FEW SIMPLE "
     "SHAPES laid over those lines - it never thickens the limbs into a drawn body and "
     "never fills the figure in.\n\n"
     "What he wears, and nothing more:\n"
     "  · a wide flat-brimmed HAT sitting on top of the head circle - a simple dome with "
     "a straight brim, drawn in outline\n"
     "  · a long straight-sided ROBE hanging from the shoulders to just above the ankles, "
     "drawn as two simple lines down each side with a straight hem. It is OPEN enough "
     "that the stickman's spine line still shows through it\n"
     "  · a single BELT line across the waist\n"
     "  · a short straight SWORD hanging at the hip, a plain line with a small square "
     "hilt\n"
     "  · a tall straight POLE in his near hand, running from the ground to well above "
     "the hat, perfectly vertical\n\n"
     "★No face detail beyond the usual two dots and one mouth line. No armour plates, no "
     "patterns, no folds, no shading, no colour - everything is the same black line on "
     "plain white. If it stops looking like a stickman, it is wrong.")),
]

BY = {k: (g, p) for k, g, p in POSES}


def guide_of(key):
    return "W1_2/motion_src/guide_%s.png" % BY[key][0]


def prompt(key):
    return BY[key][1]


if __name__ == "__main__":
    for k, g, _ in POSES:
        print("%-20s 기준 %-12s %5d자  %s"
              % (k, g, len(prompt(k)), "OK" if os.path.exists(guide_of(k)) else "★가이드없음"))
