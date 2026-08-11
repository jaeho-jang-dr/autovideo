# -*- coding: utf-8 -*-
"""스틱맨 이동 동작 6종 — 걷기 3 · 달리기 3.

★사장님 지시(2026-08-11): "오른편 걷기·달리기, 3/4 앞으로 걷기·달리기,
  3/4 뒤로 걷기·달리기 — 6개의 동영상을 스틱맨 정면과 측면 이미지를 기준으로
  (투명한 배경, 검정 라인) 만들고 프레임을 나누어 저장해서
  **스틱맨이 배경 안에서 완전히 자유로이 돌아다니게** 만든다."

## 왜 6개면 충분한가
좌우 반전으로 나머지 방향을 얻는다. **6개 → 실질 10방향.**

| 만드는 것 | 반전으로 얻는 것 |
|---|---|
| 측면 오른쪽 | 측면 왼쪽 |
| 3/4 앞 오른쪽(다가옴) | 3/4 앞 왼쪽 |
| 3/4 뒤 오른쪽(멀어짐) | 3/4 뒤 왼쪽 |

걷기·달리기 각각이므로 6개.

## 기준 이미지
`W1_2/motion_src/guide_front.png` (정면) · `guide_side.png` (측면)
— 흰 배경 · 검정 라인 · 1280x720 **정중앙**
"""

# 공통 규격 — 왜곡 금지 + 제자리 걷기(트레드밀)
LOCK = """Keep the drawing exactly as it is in the source image: a simple black line
stickman on a plain white background, same line weight, same head circle, same
proportions. Do not restyle, do not add colour, do not add shading, do not add
a background, do not add a floor line or shadow.

ANATOMY LOCK - the most important rule.
EXACTLY two arms and EXACTLY two legs, each a single unbroken line. Never add a
limb, never remove one, never let a limb pass through the body. Limb LENGTH IS
FIXED - arms and legs never stretch, extend, shrink or rubber-band. Joints bend
only the way a human body bends: elbows and knees hinge one way only, shoulders
and hips stay within a natural human range. No hyperextension, no bending
backwards, no rubbery or noodle-like motion. The head stays a closed circle and
stays attached to the neck.

TREADMILL RULE - the figure stays in the CENTRE of the frame the whole time and
does NOT travel across the screen. It walks/runs in place, like on a treadmill,
so the cycle can be looped. Camera is locked - no pan, no zoom, no shake.
No text, letters or numbers anywhere."""

# ★뒤로 가는 동작의 머리 규격 (사장님 지시 2026-08-11)
#   "뒤로 달리기면 얼굴이 없고 귀만 오른편에 보이고 코가 아주 조금 보이면 된다."
#   앞서 쓰던 "얼굴이 안 보인다"는 막연해서 Flow 가 제멋대로 해석했다.
BACK_HEAD = """BODY ROTATION - EXACTLY 135 DEGREES. Take the figure facing the camera
as 0 degrees and the figure with its back fully to the camera as 180 degrees. This
figure is rotated to EXACTLY 135 degrees: turned away from the camera and angled
toward the right. We therefore see his back and shoulders, plus a narrow sliver of
his right side. Hold this 135-degree rotation for the entire clip - it never rotates
back toward the camera and never goes flat to 180.

WHAT IS VISIBLE ON THE HEAD, AND NOTHING ELSE. At 135 degrees we are looking at the
back of his head. There are NO eyes and NO mouth anywhere - the face is absent.
Exactly two things show: the RIGHT EAR, a small shape on the right side of the head
circle, and the very TIP OF THE NOSE barely peeking past the right edge of the head.
That is the complete list. Draw nothing else on the head at any point in the clip."""

# ★몸이 돌아가는 과정을 통째로 만들고 **원하는 각도의 프레임을 골라낸다**
#   (사장님 지시 2026-08-11).
#   각도를 고정시키라고 하면 Flow 가 계속 옆모습으로 떨어졌다. 대신 90도→45도→0도로
#   **돌아가는 8초**를 만들게 하면, 그 사이 모든 각도가 프레임 안에 들어 있다.
#   기준 이미지도 guide_side.png 가 첫 프레임과 정확히 맞아떨어진다.
TURN = """THE THREE-QUARTER DIAGONAL IS THE POINT OF THIS CLIP - eight of the ten
seconds are spent holding it. Rotate the figure about the vertical axis that runs
straight down through the head and the body:

  0.0 - 1.0s   exact SIDE profile, facing to the RIGHT (90 degrees) - the pose in
               the source image. Just one second, then turn.
  1.0 - 9.0s   THE MAIN SECTION. He is at a THREE-QUARTER DIAGONAL of 45 degrees,
               half way between side-on and facing the camera, turned toward the
               camera and to the right. HOLD 45 DEGREES FOR THESE EIGHT FULL
               SECONDS. Do not drift back to side-on, do not creep round to the
               front, do not wobble between angles. At 45 degrees we see his chest
               at an angle, one shoulder nearer to us than the other, and the near
               side of his face - one eye clearly and the other eye close to the
               edge of the head, with the nose breaking the outline on the right.
  9.0 - 10.0s  only now turn the rest of the way to face the camera straight on
               (0 degrees), FRONT view, both eyes and the mouth visible.

The two turns are quick and smooth; the long middle is steady and still at exactly
45 degrees. Every frame of that middle section must be a clean, readable drawing on
its own, because single frames will be lifted out of it."""

# ★나가기 회전 (사장님 지시 2026-08-11)
#   "옆으로 걷거나 달리다가 135도 돌아서 나가면서 걷기·달리기."
#   45도를 붙잡아 두려는 시도는 8초·10초 둘 다 실패했다. 각도를 **고정**시키는 건
#   안 되고 **돌아가는 과정**은 잘 되므로, 회전 클립으로 목적지까지 가는 방식으로 간다.
EXIT_TURN = """TURN AND LEAVE - rotate about the vertical axis that runs straight
down through the head and the body. The rotation only ever goes ONE WAY, away from
the camera - 90 degrees, then round to 180 degrees, and it stops there:

  0.0 - 2.0s   exact SIDE profile, facing to the RIGHT (90 degrees) - the pose in
               the source image, held cleanly for the full two seconds
  2.0 - 4.0s   turning smoothly away from the camera, from 90 through 135 and on
               round to 180 degrees. Two seconds, one continuous turn.
  4.0 - 8.0s   THE MOST IMPORTANT PART OF THIS CLIP. He is now square-on FROM
               BEHIND - a full 180 degrees, his back straight to the camera - and
               he stays exactly there for these four whole seconds, walking or
               running IN PLACE the entire time. Do not let him drift back to
               135 degrees or to any angle at all. Straight back view, dead on,
               for four full seconds.

ONE-WAY ROTATION - THIS IS STRICT. He must never turn back toward the camera, never
swing left then right, never rotate past 180 and keep spinning, never face the
camera at any point. No wandering about, no changing his mind, no looking back over
his shoulder. The angle only increases: 90 to 180, then stays at 180.

THE FULL BACK VIEW AT 180 DEGREES - what the head looks like. It is a plain empty
circle. There are NO eyes, NO mouth and NO nose anywhere - we are behind him, so
none of the face is visible at any point in the last four seconds. Both shoulders
are level and symmetric, the arms swing evenly on either side of the body, and both
legs are equally visible - nothing is foreshortened to one side, because he is
exactly square-on.

That last four-second stretch has to be a clean, loopable walk or run cycle seen
from directly behind, because it will be repeated while the figure is scaled down
to make him walk off into the distance."""

# (키, 기준이미지, 동작)
MOTIONS = [
    ("walk_exit", "side",
     "The stickman WALKS in place at a steady, relaxed pace for the whole eight "
     "seconds - a natural walk cycle, legs swinging through, arms swinging in "
     "opposition, never pausing. While he keeps walking, his body turns as "
     "described below.\n\n" + EXIT_TURN),

    ("run_exit", "side",
     "The stickman RUNS in place for the whole eight seconds - a clear running cycle "
     "with knees lifting high, heels kicking up behind, arms bent at the elbow and "
     "pumping in opposition, never pausing. While he keeps running, his body turns "
     "as described below.\n\n" + EXIT_TURN),

    ("walk_turn10", "side",
     "The stickman WALKS in place at a steady, relaxed pace for the whole ten "
     "seconds - a natural walk cycle with the legs swinging through and the arms "
     "swinging in opposition, never pausing. While he keeps walking, his body turns "
     "through the angles described below.\n\n" + TURN),

    ("run_turn10", "side",
     "The stickman RUNS in place for the whole ten seconds - a clear running cycle "
     "with knees lifting high, heels kicking up behind, and arms bent at the elbow "
     "pumping in opposition, never pausing. While he keeps running, his body turns "
     "through the angles described below.\n\n" + TURN),

    ("walk_side", "side",
     "The stickman walks steadily in place, seen from the SIDE, facing to the RIGHT. "
     "A clean natural walk cycle: the near leg swings forward and plants, the far leg "
     "pushes off behind, arms swinging in opposition to the legs. Roughly three full "
     "strides over the eight seconds, at an even relaxed pace. The whole side profile "
     "stays visible - do not turn the body toward or away from the camera."),

    ("run_side", "side",
     "The stickman RUNS in place, seen from the SIDE, facing to the RIGHT. "
     "A clear running cycle with a longer stride than walking: knees lift high, the "
     "trailing leg kicks up behind, both feet leave the ground at the airborne moment, "
     "arms bent at the elbow and pumping hard in opposition. Roughly five full strides "
     "over the eight seconds. The body leans slightly forward. Stay side-on."),

    ("walk_away", "front",
     "The stickman walks steadily in place, seen from BEHIND at a THREE-QUARTER angle - "
     "we see mostly his back and a little of his right side, as if he is walking away "
     "from the camera and off to the right. A natural walk cycle, roughly three strides "
     "over the eight seconds, arms swinging in opposition. Keep the same "
     "three-quarter-from-behind angle throughout.\n\n" + BACK_HEAD),

    ("run_away", "front",
     "The stickman RUNS in place, seen from BEHIND at a THREE-QUARTER angle - mostly his "
     "back and a little of his right side, as if running away from the camera and off to "
     "the right. A clear running cycle: knees lift high, heels kick up behind, arms bent "
     "and pumping. Roughly five strides over the eight seconds. Keep the same "
     "three-quarter-from-behind angle throughout.\n\n" + BACK_HEAD),

    ("walk_toward", "front",
     "The stickman walks steadily in place, seen from the FRONT at a THREE-QUARTER angle - "
     "we see his face and chest turned slightly to his left, as if he is walking toward "
     "the camera and off to the right. The eyes and mouth stay visible. A natural walk "
     "cycle, roughly three strides over the eight seconds, the near leg swinging toward "
     "the viewer. Keep the same three-quarter-from-the-front angle throughout."),

    ("run_toward", "front",
     "The stickman RUNS in place, seen from the FRONT at a THREE-QUARTER angle - his face "
     "and chest turned slightly to his left, as if running toward the camera and off to "
     "the right. The face stays visible. A clear running cycle: knees lift high toward "
     "the viewer, arms bent at the elbow and pumping, body leaning slightly forward. "
     "Roughly five strides over the eight seconds. Keep the same angle throughout."),
]

BY = {k: (guide, motion) for k, guide, motion in MOTIONS}


def prompt(key):
    guide, motion = BY[key]
    return "%s\n\n%s" % (LOCK, motion)


def guide_of(key):
    return "W1_2/motion_src/guide_%s.png" % BY[key][0]


if __name__ == "__main__":
    for k, g, _ in MOTIONS:
        print("%-13s 기준 %-6s %5d자" % (k, g, len(prompt(k))))
