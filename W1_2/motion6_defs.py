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
# ★LOCK 문자열은 m6_stick 572컷을 만들어 낸 검증된 값이다. 조각으로 나누되
#   LOCK 자체는 한 글자도 달라지면 안 된다(__main__ 에서 길이로 검산한다).
_STYLE = """Keep the drawing exactly as it is in the source image: a simple black line
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
stays attached to the neck."""

_TREADMILL = """TREADMILL RULE - the figure stays in the CENTRE of the frame the whole time and
does NOT travel across the screen. It walks/runs in place, like on a treadmill,
so the cycle can be looped. Camera is locked - no pan, no zoom, no shake.
No text, letters or numbers anywhere."""

LOCK = _STYLE + "\n\n" + _TREADMILL

# ★이동형 동작(앞구르기)은 제자리에 있을 수 없다 — 트레드밀 규칙만 갈아 끼운다.
_TRAVEL = """TRAVEL RULE - this action DOES move across the ground, so let it move: he
starts near the LEFT edge of the frame and ends near the RIGHT edge, and the whole
figure stays fully inside the frame at every moment - never cropped by an edge.
Camera is locked - no pan, no zoom, no shake, the camera never follows him.
No text, letters or numbers anywhere."""

LOCK_TRAVEL = _STYLE + "\n\n" + _TRAVEL

# ★한 번만 일어나는 동작(백플립·엉덩방아 등)은 순환이 아니다. 앞뒤에 정지 자세를
#   조금 남겨 두어야 컷을 골라낼 때 시작·끝을 찾을 수 있다.
_ONESHOT = """ONE ACTION, ONCE - this is not a loop. He performs the action a single time
and holds still before and after it, standing in the CENTRE of the frame. He does not
repeat it, does not travel across the screen, and does not drift sideways.
Camera is locked - no pan, no zoom, no shake.
No text, letters or numbers anywhere."""

LOCK_ONESHOT = _STYLE + "\n\n" + _ONESHOT

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

# ★★★ 개수 못 박기 강화 (사장님 지적 2026-08-12)
#   "살금살금 팔이 셋이다. 급정지도 다리가 셋이다. 해부학적 팔다리 반드시 두 개라고
#    명시하자. 그리고 캐릭터가 중간에 있어야 한다."
#   기존 ANATOMY LOCK 의 "EXACTLY two arms and two legs" 한 줄로는 뚫렸다. 원인은 빠른
#   동작에서 Flow 가 **잔상·모션블러를 팔다리 하나 더**로 그려 버리는 것이다.
#   그래서 ①맨 앞에 개수를 먼저 박고 ②잔상·복제를 이름 붙여 금지하고 ③맨 뒤에 다시 센다.
COUNT_HARD = """ANATOMICALLY THIS FIGURE HAS EXACTLY TWO ARMS AND EXACTLY TWO LEGS -
ONLY TWO OF EACH, NEVER MORE. He is a human body: ONE left arm, ONE right arm, ONE
left leg, ONE right leg. Two arms. Two legs. Four limbs in total and no more. That
count is the same in EVERY SINGLE FRAME of this clip, without exception.

NEVER DRAW A FIFTH LIMB. When a limb swings fast, do NOT draw a motion trail, a
smear, a ghost, an afterimage, a blurred copy, a doubled line or a faint second
version of it - any of those reads as an extra arm or an extra leg. When one limb
passes in front of or behind another, draw the two overlapping, not three separate
ones. When a limb is hidden by the body, simply leave it hidden - do not invent a
substitute so that something is visible.

BEFORE EVERY FRAME IS DRAWN, COUNT AGAIN: two arms, two legs, four limbs total.
If a frame would show five, redraw it with four."""

# ★측면 달리기의 팔·다리 (사장님 지적 2026-08-12 — 살금살금이 팔 셋으로 나온 뒤 정립)
#   측면에서 팔 둘을 **같은 자리**에 두라고 하면 모호해서 셋이 된다. 달리기는 팔이
#   앞뒤로 교차하는 동작이므로 "하나는 앞, 하나는 뒤"로 **갈라서** 못 박는다.
RUN_LIMBS = """ARMS - ONE FORWARD, ONE BACK, ALWAYS OPPOSITE.
He has two arms and both are visible from this side view, but they are never in the
same place. At every instant one arm is swung FORWARD in front of his chest and the
other is swung BACK behind his hip, both bent at the elbow. They swap over as he runs,
but they are ALWAYS on opposite sides of his body - never both forward, never both
back, never side by side, never overlapping into one shape, never lined up along the
same direction. Exactly two arm lines in every frame: one in front, one behind.

LEGS - ONE FORWARD, ONE BACK, ALWAYS OPPOSITE, exactly the same way. At every instant
one leg is reaching forward and the other is driving back. Exactly two leg lines in
every frame: one in front, one behind. Never three."""

# ★★구르기 3원칙 (사장님 확정 2026-08-13 — 1차본이 왜곡·팔다리 엉망으로 나온 뒤)
#   "해부학적으로 만들고, 팔 다리 절대로 2개 2개 이상 나오게 하지 말고,
#    얼굴 방향은 항상 회전하는 방향으로 고정한다."
#   구르기는 몸이 뒤집히는 동안 Flow 가 팔다리를 늘리고 개수를 늘린다. 그래서
#   ①사람 몸의 뼈대를 먼저 못 박고 ②개수를 맨 앞뒤로 두 번 세고 ③얼굴이 도는
#   방향을 프레임마다 다시 지정한다.
#   ★손은 **새로 만들지 않는다** (사장님 2026-08-13).
#     "앞구르기 뒷구르기 스틱맨에 손을 만들지 마라. **발은 이미 있는 것이고,
#      손은 새로 추가로 만들지 마.**"
#     스틱맨은 팔이 선 하나로 끝나는 그림이다. 발(신발)은 기준 이미지에 이미 있으니
#     그대로 두고, 없던 손만 붙이지 못하게 막는다. 손을 붙이면 검은 덩어리가 달려
#     나오고 구를 때 그게 다섯째 팔다리처럼 보인다.
ROLL_NO_HANDS = """DO NOT ADD HANDS - HE HAS NONE, AND NONE ARE TO BE INVENTED.
Each arm is a single plain line that simply ENDS at the wrist. Do not draw a hand, a
fist, a palm, fingers, a mitten, a glove, a blob, a circle or any thickening at the
end of the arm. The arm line just stops, exactly as it does in the source image, in
every frame including while he is upside down.

HIS FEET STAY EXACTLY AS THEY ARE IN THE SOURCE IMAGE. He already has feet/shoes
drawn there - keep them, unchanged in shape and size, on both legs, all the way
through. Do not remove them and do not restyle them. Only the HANDS are the thing
that must never appear."""

ROLL_HARD = """THIS IS A HUMAN BODY WITH HUMAN JOINTS - DRAW IT ANATOMICALLY.
Head, neck, chest, hips, two arms, two legs. The arm bends ONLY at the shoulder and
the elbow, the leg ONLY at the hip and the knee, and each joint bends the way a human
joint bends and no further. Upper arm and forearm are the same length in every frame;
thigh and shin are the same length in every frame. Nothing stretches, nothing shrinks,
nothing bends backwards, nothing turns to rubber or noodle. The neck never stretches
and the head never separates from it. Even while he is upside down, the skeleton is
the same skeleton - only its orientation changes.

EXACTLY TWO ARMS AND EXACTLY TWO LEGS. NEVER MORE - NOT ONE EXTRA, NOT EVER.
Two arms, two legs, four limbs, in every single frame of the clip without exception.
When a limb sweeps fast, do NOT draw a motion trail, a smear, a ghost, an afterimage,
a blurred copy, a doubled line or a faint second version of it - every one of those
reads as a fifth limb. When one limb crosses in front of another, draw the two
overlapping, never three. When a limb is hidden by the body, leave it hidden - do not
invent a replacement so that something is visible.
COUNT BEFORE DRAWING EVERY FRAME: two arms, two legs. If a frame would show five
limbs, redraw that frame with four.

THE FACE POINTS THE WAY HE IS ROLLING, AND IT NEVER SWAPS SIDES.
His nose, chin and the front of his chest stay on the SAME side of his body for the
whole clip - the side he was facing in the very first frame. As his body tumbles, his
head tumbles with it, so the nose sweeps around with the rotation - but it never jumps
to the other side of his head, and he never mirrors, never spins about the vertical
axis, never ends up facing the opposite way. If he faces right at 0.0s he faces right
at 8.0s, and at every moment in between the face is on the right-hand side of the head."""

# ★옷·신발·장갑은 **흰색으로 그리지 않는다** (사장님 지시 2026-08-13)
#   "이제 옷 신발 손장갑 등을 흰색을 하지 말고, **컷아웃 하기 힘드니 회색까지만** 하자."
#   흰 신발은 흰 배경과 같은 색이라 투명컷이 갈라내지 못해 신발 속이 뻥 뚫렸다.
#   밝은 회색으로 그리면 배경과 갈려 그대로 살아남는다(W1_2/strip_white.py 가 회색은 남긴다).
GREY_PARTS = """SHOES, HANDS AND ANY CLOTHING ARE LIGHT GREY - NEVER WHITE.
His shoes, his hands/gloves and any garment are filled with a light grey (about 80%
grey, clearly darker than the white background), with the usual black outline. They
must NOT be left white and must NOT be the same colour as the background, because the
frames get cut out onto transparency and a white shoe cannot be told apart from white
background - it ends up as a hole. The ONLY pure white in the picture is the inside of
the head circle (the face). Everything else that is not a black line is grey or a
colour."""

# ★캐릭터는 화면 중앙에 (사장님 지시 2026-08-12)
CENTER_HARD = """THE FIGURE STAYS IN THE MIDDLE OF THE FRAME. He is centred horizontally
and vertically for the whole clip, whole body inside the frame, never drifting to a
side, never touching or crossing an edge, never partly cut off. Camera is locked -
no pan, no zoom, no shake."""

# ★정면 0도 달리기 (사장님 지시 2026-08-12)
#   "정면 달리기를 만들어서 머리만 리버스 하면 후면 달려 나가기로 바꿀 수도 있다."
#   → 머리를 갈아 끼워 뒷모습으로 전용하려면 몸이 **정확히 0도**여서 좌우가 대칭이어야
#     한다. 3/4 인 run_toward 로는 실루엣이 맞지 않아 못 쓴다.
#   → EXIT_TURN 의 "180도 뒷모습" 규격을 거울처럼 뒤집은 것이다.
FRONT_LOCK = """BODY ROTATION - EXACTLY 0 DEGREES, DEAD ON. He faces the camera
square-on for the whole clip. Both shoulders are level and the same distance from the
camera, both hips are level, both arms are equally visible on either side of the body,
and both legs are equally visible. Nothing is foreshortened to one side. The centre
line of his body runs straight down the middle of the figure.

HE NEVER ROTATES - THIS IS STRICT. Not to a three-quarter angle, not to the side, not
a few degrees either way, not for a single frame. No turning, no twisting of the
shoulders, no glancing off to one side, no leaning left or right. Straight at the
camera from the first frame to the last.

THE FACE IS VISIBLE THE WHOLE TIME - two eyes and one mouth, drawn exactly as in the
source image, centred in the head circle, in every single frame. The head circle stays
level and does not tilt or rotate.

SYMMETRY IS THE POINT OF THIS CLIP. Individual frames will be lifted out and reused,
so at every moment the left and right halves of the figure must read as a clean mirror
of each other apart from the running cycle itself - one knee up while the other is
down, one arm forward while the other is back."""

# ★졸라맨·졸라걸 규격 (사장님 지시 2026-08-12)
#   스틱맨 LOCK 은 "검은 선 스틱맨"이라 졸라에게 못 쓴다 — 이쪽은 머리카락·손·신발이
#   있고, 졸라맨은 **검은 건 머리카락뿐**, 졸라걸은 **주황 머리가 유일한 색**이다
#   (`character-zollaman-face-design`). 얼굴이 검게 메워지는 사고를 막는 게 핵심.
#   기준 이미지는 W24R 가이드를 정규화한 것 → W1_2/make_zolla_guides.py
_ZOLLA_ANATOMY = """ANATOMY LOCK - the most important rule.
EXACTLY two arms and EXACTLY two legs, with exactly one hand at the end of each arm
and one shoe at the end of each leg. Never add a limb, never remove one, never let a
limb pass through the body. Limb LENGTH IS FIXED - arms and legs never stretch,
extend, shrink or rubber-band. Joints bend only the way a human body bends: elbows and
knees hinge one way only, shoulders and hips stay within a natural human range. No
hyperextension, no bending backwards, no rubbery or noodle-like motion. The head stays
a closed circle with the face inside it and stays attached to the neck."""

ZMAN_STYLE = """Keep the character exactly as he is in the source image: a hand-drawn
figure with a black outline, a round WHITE face carrying two dot eyes and one short
mouth line, and SPIKY BLACK HAIR on top. The hair is the ONLY solid black area
anywhere on him - his face and body never fill in black. Simple drawn hands, simple
drawn shoes, plain white background. Same line weight, same proportions, same hair
shape. Do not restyle, do not add colour, do not add shading, do not add a background,
do not add a floor line or shadow.

""" + _ZOLLA_ANATOMY

ZGIRL_STYLE = """Keep the character exactly as she is in the source image: a hand-drawn
figure with a black outline, a round WHITE face carrying two dot eyes and one short
mouth line, and ORANGE HAIR tied up in a small bun on top. The orange hair is the ONLY
colour anywhere on her, and her face and body never fill in black. Simple drawn hands,
simple drawn shoes, plain white background. Same line weight, same proportions, same
hair shape and the same bun. Do not restyle, do not add any other colour, do not add
shading, do not add a background, do not add a floor line or shadow.

★LIMB THICKNESS - STRICT: the arms and legs are drawn as THIN, SINGLE-WEIGHT LINES,
exactly as thin as they are in the source image - never thicker, never padded, never
filled in as solid shapes, never rendered as fat tubes or sausage-like limbs. Keep the
same razor-thin stick-figure line the whole clip, every single frame, even during fast
motion like running. Only the torso/body outline may have its normal shape - arms and
legs stay pure thin lines with no added bulk or muscle.

""" + _ZOLLA_ANATOMY

ZMAN_LOOP = ZMAN_STYLE + "\n\n" + _TREADMILL
ZMAN_ONCE = ZMAN_STYLE + "\n\n" + _ONESHOT
ZGIRL_LOOP = ZGIRL_STYLE + "\n\n" + _TREADMILL
ZGIRL_ONCE = ZGIRL_STYLE + "\n\n" + _ONESHOT

# (키, 기준이미지, 동작)
MOTIONS = [
    # ── 졸라맨·졸라걸 동작 (S15~S18 · S23~S25) ──────────────────────────
    # ★달리기는 팔이 **앞뒤로 교차**하는 동작이다. 살금살금처럼 팔이 모이지 않으므로
    #   "하나는 앞, 하나는 뒤"로 갈라 못 박는다 — 같은 자리에 두면 셋이 된다.
    ("zman_run_side", "zman_side",
     "Zollaman RUNS IN PLACE, seen from the SIDE, facing to the RIGHT. A clear running "
     "cycle with a long stride: knees lift high, the trailing leg kicks up behind, and "
     "both feet leave the ground at the airborne moment. Roughly five full strides over "
     "the eight seconds. The body leans slightly forward. Stay side-on - do not turn "
     "toward or away from the camera.\n\n" + RUN_LIMBS + "\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + ZMAN_LOOP),

    ("zgirl_run_side", "zgirl_side",
     "Zollagirl RUNS IN PLACE, seen from the SIDE, facing to the RIGHT. A clear running "
     "cycle with a long stride: knees lift high, the trailing leg kicks up behind, and "
     "both feet leave the ground at the airborne moment. Roughly five full strides over "
     "the eight seconds. The body leans slightly forward. Her hair bun stays put. Stay "
     "side-on.\n\n" + RUN_LIMBS + "\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + ZGIRL_LOOP),

    # ★W1-3(청계천) 신규 7종 — 사장님 지시(2026-08-31) "필요한 캐릭터 포즈와 모션 전부다
    #   만들자." 걷기(측면·정면·후면)·달리기(정면·후면)는 순환(LOOP, 한 스트라이드만 추출),
    #   block_touch·stumble_bounce는 1회 동작(ONCE, 64컷 추출).
    #   ★후면은 정면 컷에서 머리만 교체하는 파생(make_run_front_cuts.back_head 방식)을
    #     검토했으나, 그 함수는 **흰 머리(스틱맨 전용)** 라 주황 머리인 졸라걸엔 그대로
    #     못 쓴다(머리만 골라 칠하는 마스크가 없어 몸통까지 같이 칠해진다). 이번에 검증된
    #     guide_zgirl_back.png(2026-08-31, locator 방식으로 성공)를 기준 이미지로 그대로
    #     써서 **직접 생성**한다 — 이미 파이프라인이 안정적으로 검증됐으니 위험이 적다.
    ("zgirl_walk_side", "zgirl_side",
     "Zollagirl WALKS IN PLACE, seen from the SIDE, facing to the RIGHT. A clean, "
     "natural, unhurried walk cycle: the near leg swings forward and plants heel-first, "
     "the far leg pushes off behind, arms swinging gently in opposition to the legs, "
     "never both feet off the ground at once (unlike running). Roughly three full "
     "strides over the eight seconds, at an even relaxed pace. Her hair bun stays put. "
     "Stay side-on - do not turn toward or away from the camera.\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + ZGIRL_LOOP),

    ("zgirl_walk_front", "zgirl_front",
     "Zollagirl WALKS IN PLACE, seen from the FRONT, square-on to the camera, body at "
     "EXACTLY 0 degrees rotation (facing the camera dead-on, not a three-quarter angle). "
     "A clean, natural, unhurried walk cycle: her legs alternate stepping forward and "
     "back with a gentle knee bend and a small up-and-down bob, her arms swing gently "
     "opposite the legs, never both feet off the ground at once. Roughly three full "
     "strides over the eight seconds. Her hair bun stays put. Her body and shoulders "
     "stay square to the camera the entire time - never rotate to a side view.\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + ZGIRL_LOOP),

    ("zgirl_run_front", "zgirl_front",
     "Zollagirl RUNS IN PLACE, seen from the FRONT, square-on to the camera, body at "
     "EXACTLY 0 degrees rotation (facing the camera dead-on, not a three-quarter angle). "
     "A clear running cycle: knees lift high toward the chest alternately, arms pump "
     "energetically opposite the legs bent at the elbow, a clear airborne moment where "
     "both feet leave the ground. Roughly five full strides over the eight seconds. Her "
     "hair bun stays put. Her body and shoulders stay square to the camera the entire "
     "time - never rotate to a side view.\n\n" + RUN_LIMBS + "\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + ZGIRL_LOOP),

    ("zgirl_walk_back", "zgirl_back",
     "Zollagirl WALKS IN PLACE, seen from directly BEHIND - her back, the back of her "
     "head, and the back of her shoulders and legs face the camera, body at EXACTLY 180 "
     "degrees rotation from front-facing. NO face is visible anywhere, at any point in "
     "the clip - no eyes, no mouth peeking around either side of the head. The orange "
     "hair covers the entire back of her head exactly as in the reference image, with "
     "the bun on top. A clean, natural, unhurried walk cycle: her legs alternate "
     "stepping with a gentle knee bend and small up-and-down bob, her arms swing gently "
     "opposite the legs, never both feet off the ground at once. Roughly three full "
     "strides over the eight seconds. Her shoulders stay square, facing directly away "
     "from the camera the entire time - never rotate back around to show the face.\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + ZGIRL_LOOP),

    ("zgirl_run_back", "zgirl_back",
     "Zollagirl RUNS IN PLACE, seen from directly BEHIND - her back, the back of her "
     "head, and the back of her shoulders and legs face the camera, body at EXACTLY 180 "
     "degrees rotation from front-facing. NO face is visible anywhere, at any point in "
     "the clip - no eyes, no mouth peeking around either side of the head. The orange "
     "hair covers the entire back of her head exactly as in the reference image, with "
     "the bun on top. A clear running cycle: knees lift high alternately, arms pump "
     "energetically bent at the elbow, a clear airborne moment where both feet leave "
     "the ground. Roughly five full strides over the eight seconds. Her shoulders stay "
     "square, facing directly away from the camera the entire time - never rotate back "
     "around to show the face.\n\n" + RUN_LIMBS + "\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + ZGIRL_LOOP),

    ("zgirl_block_touch", "zgirl_front",
     "Zollagirl reaches out and touches something floating in front of her, seen from "
     "the FRONT, square-on to the camera. Nothing else is drawn - only she is in the "
     "frame, reaching into empty space.\n"
     "  0.0 - 1.5s  standing still, facing the camera, arms relaxed at her sides\n"
     "  1.5 - 3.5s  she raises her right arm smoothly and reaches forward at chest "
     "height, fingers opening as if about to touch something invisible\n"
     "  3.5 - 5.0s  she holds the reach, fingertips extended, a curious focused "
     "expression\n"
     "  5.0 - 6.5s  she draws her arm back in, as if pulling that invisible thing "
     "toward her chest\n"
     "  6.5 - 8.0s  standing still again, facing the camera\n\n"
     "★Both halves must be slow and clean enough to lift single frames out of.\n\n"
     + ZGIRL_ONCE),

    ("zgirl_stumble_bounce", "zgirl_side",
     "Zollagirl tries to place something in the wrong spot, gets bounced back, and "
     "stumbles, seen from the SIDE, facing RIGHT. Nothing else is drawn - only she is "
     "in the frame.\n"
     "  0.0 - 1.5s  standing still, side-on, leaning slightly forward reaching toward "
     "something invisible ahead of her\n"
     "  1.5 - 2.5s  THE BOUNCE. Her whole body is knocked backward sharply, as if "
     "pushed by an invisible spring - arms fly up and back, torso tips backward\n"
     "  2.5 - 4.0s  she stumbles backward off balance, legs stepping back to catch "
     "herself, arms flailing slightly for balance\n"
     "  4.0 - 5.2s  she loses the fight and sits down hard on the ground, landing on "
     "her seat, legs splayed out in front of her\n"
     "  5.2 - 6.5s  she sits there for a moment, a little dazed\n"
     "  6.5 - 8.0s  she pushes herself back up to standing, side-on, and settles\n\n"
     "★Both halves must be slow and clean enough to lift single frames out of. This is "
     "the same kind of beat as W1_2's butt_fall - a comedic backward tumble, not a "
     "violent fall. ANATOMY LOCK applies through every frame of the tumble, including "
     "while seated on the ground.\n\n" + ZGIRL_ONCE),

    # ★W1-3(청계천) v2 재설계 보강 3종 — 사장님 지시(2026-09-01) "캐릭터 동작 3개 지금 만들자."
    ("zgirl_stone_hop", "zgirl_side",
     "Zollagirl hops in place from one stepping stone to the next, seen from the SIDE, "
     "facing to the RIGHT. A clean, light hopping cycle: she crouches slightly, springs "
     "up and forward with both feet leaving the ground briefly, arms swinging up for "
     "balance, then lands softly with a small knee bend to absorb the landing. Roughly "
     "three full hops over the eight seconds, at a light, careful, playful pace (not a "
     "run - this is picking her way across stones one at a time). Her hair bun bounces "
     "slightly with each landing. Stay side-on - do not turn toward or away from the "
     "camera.\n\n" + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + ZGIRL_LOOP),

    ("zgirl_cold_flinch", "zgirl_front",
     "Zollagirl reacts to something cold touching her foot, seen from the FRONT, "
     "square-on to the camera. Nothing else is drawn - only she is in the frame.\n"
     "  0.0 - 1.8s  standing still, facing the camera, relaxed, one foot forward as if "
     "about to step into water\n"
     "  1.8 - 2.6s  THE FLINCH. She yanks that foot back up sharply, knee lifting high, "
     "shoulders hunching up, arms drawing in close to her body, an exaggerated startled "
     "expression\n"
     "  2.6 - 3.8s  she holds the flinch - foot still lifted, shivering slightly\n"
     "  3.8 - 5.0s  she lowers the foot back down slowly and carefully this time\n"
     "  5.0 - 8.0s  standing still again, facing the camera, a little wary but settled\n\n"
     "★Both halves must be slow and clean enough to lift single frames out of.\n\n"
     + ZGIRL_ONCE),

    ("zgirl_clap_together", "zgirl_front",
     "Zollagirl brings two things together in her hands like clapping blocks together, "
     "seen from the FRONT, square-on to the camera. Nothing else is drawn - only she is "
     "in the frame, her hands acting on empty space.\n"
     "  0.0 - 1.5s  standing still, facing the camera, both arms held out wide to her "
     "sides at chest height, palms facing inward, as if holding something invisible in "
     "each hand\n"
     "  1.5 - 3.5s  she brings both arms smoothly toward the centre of her chest, hands "
     "meeting together in the middle with a small decisive motion, like clapping two "
     "blocks together\n"
     "  3.5 - 5.0s  she holds her hands together at her chest, a pleased satisfied smile\n"
     "  5.0 - 6.5s  she opens her arms back outward, presenting the joined result to the "
     "viewer, palms up\n"
     "  6.5 - 8.0s  standing still, arms settled, facing the camera\n\n"
     "★Both halves must be slow and clean enough to lift single frames out of.\n\n"
     + ZGIRL_ONCE),

    ("zman_sit_stand", "zman_side",
     "Zollaman SITS DOWN and then STANDS BACK UP, seen from the SIDE, facing RIGHT. "
     "There is no bench drawn - he sits on an invisible seat at about knee height.\n"
     "  0.0 - 1.5s  standing still, side-on\n"
     "  1.5 - 3.2s  SITTING DOWN. Knees and hips bend and he lowers his seat smoothly "
     "onto the invisible seat, back straight, thighs horizontal, shins vertical\n"
     "  3.2 - 5.0s  seated, still\n"
     "  5.0 - 6.6s  STANDING UP. He leans forward a little, pushes through his feet and "
     "rises smoothly back to full standing height\n"
     "  6.6 - 8.0s  standing still, side-on\n\n"
     "★Both halves must be slow and clean enough to lift single frames out of.\n\n"
     + ZMAN_ONCE),

    ("zman_head_tilt", "zman_front",
     "Zollaman TILTS HIS HEAD to one side, puzzled, seen from the FRONT, square-on to "
     "the camera. He is SEATED on an invisible bench with his hands on his knees.\n"
     "  0.0 - 2.0s  sitting still, facing the camera\n"
     "  2.0 - 3.2s  THE TILT. His head tips over toward one shoulder, a clear puzzled "
     "angle, while his shoulders and body stay square to the camera\n"
     "  3.2 - 5.0s  he holds the tilt\n"
     "  5.0 - 6.0s  the head comes back upright\n"
     "  6.0 - 8.0s  sitting still, facing the camera\n\n"
     "★The head tips but never detaches and never rotates away from the camera - we see "
     "his face the whole time.\n\n" + ZMAN_ONCE),

    ("zgirl_high_five", "zgirl_front",
     "Zollagirl gives a HIGH FIVE, seen from the FRONT, square-on to the camera. The "
     "other person is NOT drawn - only she is in the frame.\n"
     "  0.0 - 1.5s  standing still, facing the camera\n"
     "  1.5 - 2.4s  she swings ONE arm up and back to wind up\n"
     "  2.4 - 3.2s  THE SLAP. That arm swings up and forward, straightening high above "
     "her shoulder with the hand open and flat, reaching up and slightly to the side - "
     "the moment of contact\n"
     "  3.2 - 4.2s  the arm springs back a little from the impact, then holds high\n"
     "  4.2 - 5.5s  the arm comes back down to her side\n"
     "  5.5 - 8.0s  standing still, facing the camera\n\n"
     "★The open hand at full stretch is the frame that gets lifted out - make that reach "
     "clean, high and unambiguous.\n\n" + ZGIRL_ONCE),

    ("run_front", "front",
     "The stickman RUNS in place, seen from the FRONT, square-on to the camera. "
     "A clear running cycle: the knees lift high one after the other toward the "
     "viewer, the heels kick up behind, the arms are bent at the elbow and pump "
     "forward and back in opposition to the legs, and both feet leave the ground at "
     "the airborne moment. Roughly five full strides over the eight seconds, at an "
     "even pace. The body stays upright.\n\n" + FRONT_LOCK),

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

    # ★뒷모습 걷기 — 라이브러리에 **순수 뒷모습 걷기가 없었다**(2026-08-17).
    #   `walk_exit` 는 걷다가 돌아서는 것이고, `walk_exit_back`(4장)은 거기서 잘라낸
    #   조각이라 한 발만 까딱거린다. 수문장 `perf_guard_away` 만 제대로 된 뒷모습이었다.
    #   그 프롬프트 규격(빈 원 머리·교대 걸음)을 스틱맨에 그대로 옮긴다.
    #   기준 이미지는 **기존 뒷모습 프레임**(m6_walk_exit_l_50)을 써서 머리 크기를 맞췄다.
    ("walk_back", "back",
     "The stickman is seen FROM DIRECTLY BEHIND, walking AWAY from the camera. "
     "He walks ON THE SPOT so the cycle can loop.\n"
     "  0.0 - 8.0s  a steady, even walk seen from straight behind: the two legs "
     "alternate CLEARLY and evenly, like a soldier marching - one heel lifts and the "
     "knee bends as that foot swings forward, while the other foot plants flat on the "
     "ground; then they swap. The arms swing in OPPOSITION to the legs, elbows nearly "
     "straight, hands passing close to the hips. The shoulders rock gently with each "
     "step. About SIX unhurried steps (three full strides) over the eight seconds, at "
     "an even tempo, never pausing.\n\n"
     "★WE ONLY EVER SEE HIS BACK. He never turns round, never looks over his shoulder. "
     "His head is an EMPTY CIRCLE - no eyes, no nose, no mouth, no ears, nothing inside "
     "it at any moment. That empty circle is the back of his head and it must stay "
     "empty in every single frame.\n"
     "★He stays centred in frame and does not drift left or right. Same thin black "
     "lines on plain white as the source image, same head size, same line weight."),

    ("walk_right_away", "front",
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

    # ────────────────────────────────────────────────────────────────────
    # ★W1-2 씬 동작 (사장님 지시 2026-08-12) — motion 문서 §3-A 의 A2~A12
    # ────────────────────────────────────────────────────────────────────
    ("skid_stop", "side",                                        # A2 · S1 · S15
     "The stickman RUNS IN PLACE and then SKIDS TO A STOP. Seen from the SIDE, facing "
     "to the RIGHT. He never travels across the screen - he stays in the middle.\n"
     "  0.0 - 2.5s  a clear running cycle IN PLACE, knees lifting, arms pumping\n"
     "  2.5 - 4.0s  THE SKID. He plants both heels forward and leans his upper body "
     "BACK against his own momentum, both arms flying forward for balance. This is the "
     "moment the clip exists for - make it big and readable.\n"
     "  4.0 - 5.5s  the lean springs back upright and he settles, feet together\n"
     "  5.5 - 8.0s  standing still, side-on, breathing\n\n"
     "★SEEN FROM THE SIDE, ONE LEG IS NEARER THE CAMERA AND ONE IS FURTHER AWAY. Draw "
     "those two and nothing else. During the skid both legs are extended forward - that "
     "is still exactly two legs, overlapping, not three.\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + LOCK_ONESHOT),

    ("back_flip", "side",                                        # A3 · S2 · S13
     "The stickman does ONE BACKFLIP on the spot, seen from the SIDE, facing RIGHT.\n"
     "  0.0 - 2.0s  standing still, side-on\n"
     "  2.0 - 2.6s  he crouches and swings both arms down and back\n"
     "  2.6 - 4.4s  THE FLIP. He springs straight up and rotates BACKWARDS through one "
     "complete turn - head goes back and over, knees tuck to the chest, then the legs "
     "extend again for the landing. Exactly one full rotation, no more, no less.\n"
     "  4.4 - 5.2s  he lands on both feet, knees absorbing, arms out\n"
     "  5.2 - 8.0s  he straightens up and stands still\n\n"
     "★THE ANATOMY LOCK MATTERS MOST DURING THE ROTATION. While he is upside down it "
     "must still be EXACTLY two arms and two legs, each the same fixed length, joints "
     "bending only the way a human body bends. Do not let a third limb appear as he "
     "turns over.\n\n" + LOCK_ONESHOT),

    # ★교정 4번 (사장님 2026-08-13)
    #   "백플립 할 때는 코가 항상 처음 시작한 방향으로 보고 있어야 한다.
    #    돌다가 중간에 얼굴 방향이 바뀌면 안 된다."
    #   원인 — 옛 back_flip 은 회전 중에 Flow 가 몸을 좌우로 뒤집어 버려, 착지하면
    #   코가 왼쪽을 보고 있었다. 회전축을 **몸을 좌우로 가로지르는 축**으로 못 박고,
    #   코가 어느 쪽인지를 구간마다 다시 세워 준다.
    ("back_flip2", "side",                                       # 교정4 대체본
     "The stickman does ONE BACKFLIP on the spot, seen from the SIDE. HIS NOSE POINTS "
     "TO THE RIGHT AT THE START AND POINTS TO THE RIGHT AT THE END.\n"
     "  0.0 - 2.0s  standing still, side-on, NOSE POINTING RIGHT\n"
     "  2.0 - 2.6s  he crouches and swings both arms down and back, NOSE STILL RIGHT\n"
     "  2.6 - 4.4s  THE FLIP. He springs straight up and rotates BACKWARDS through one "
     "complete turn - head goes back and over, knees tuck to the chest, then the legs "
     "extend again for the landing. Exactly one full rotation, no more, no less. "
     "Half way through he is fully upside down and HIS NOSE IS STILL ON THE RIGHT SIDE "
     "OF HIS HEAD, just pointing downward-right because he is inverted\n"
     "  4.4 - 5.2s  he lands on both feet, knees absorbing, arms out, NOSE POINTING "
     "RIGHT\n"
     "  5.2 - 8.0s  he straightens up and stands still, NOSE POINTING RIGHT\n\n"
     "★FACING LOCK - THIS IS THE WHOLE POINT OF THE CLIP.\n"
     "He rotates about ONE axis only: the horizontal axis that runs left-to-right "
     "THROUGH HIS HIPS, straight out of the screen's left edge and in through the right "
     "edge. He tumbles backwards around that bar like a gymnast on a high bar.\n"
     "HE NEVER SPINS ABOUT THE VERTICAL AXIS. He never turns to face the other way, "
     "never mirrors, never flips left-to-right, not for a single frame. The side of him "
     "we can see at 0.0s is the SAME side of him we can see at 8.0s - if we start "
     "looking at his right shoulder we are still looking at his right shoulder when he "
     "lands.\n"
     "His nose, his chin and the front of his chest all stay on the RIGHT-HAND side of "
     "his body through every frame of the rotation. At no moment does the nose swap to "
     "the left-hand side of the head.\n\n"
     "★THE ANATOMY LOCK MATTERS MOST DURING THE ROTATION. While he is upside down it "
     "must still be EXACTLY two arms and two legs, each the same fixed length, joints "
     "bending only the way a human body bends. Do not let a third limb appear as he "
     "turns over.\n\n" + COUNT_HARD + "\n\n" + LOCK_ONESHOT),

    # ★교정 14번 (사장님 2026-08-13)
    #   "스틱맨 달려와서 앉을 때는 **정면으로 앉기**로 다시 만들라."
    #   벤치에 졸라맨과 나란히 앉는 장면이라 옆모습 sit_stand 로는 안 맞는다.
    # ★★정면으로 되돌림 + Omni Flash (사장님 지시 2026-08-13 "앞모습을 다시 옴니플래시로")
    #   지금까지 세 번 —
    #     1차 정면 Veo Fast : 앉은 구간에서 **다리가 무릎에서 끊김**
    #     2차 정면 Veo Fast : 같은 증상 (발 규정을 세게 썼는데도)
    #     3차 3/4  Veo Fast : `FRONT_LOCK` 을 빼자 **몸이 옆모습까지 돌아가고**
    #                         화면을 가로지르는 **바닥선**까지 그려 컷터가 폭 1545 로 잡음
    #   → 각도를 푸는 게 아니라 **모델을 바꾼다.** Omni Flash 는 원래 스틱맨 64컷을
    #     만들어 낸 모델이고 선이 단정하다. 정면 고정(FRONT_LOCK)을 되살리고,
    #     ★바닥선 금지를 **맨 앞으로** 올린다 — 뒤에 두면 3/4 지시에 밀렸다.
    ("sit_stand_front", "front",                                 # 교정14 새 자산 (정면)
     "NOTHING IS DRAWN EXCEPT THE STICKMAN HIMSELF. No floor line, no ground line, no "
     "horizon line, no shadow, no chair, no bench, no seat, no props, no background of "
     "any kind - the background is plain empty white from edge to edge for the whole "
     "clip. Do not draw a line across the picture at any point.\n\n"
     "The stickman SITS DOWN and then STANDS BACK UP, seen from the FRONT, square-on to "
     "the camera. He sits on an invisible seat at about knee height - the seat itself is "
     "NOT drawn.\n"
     "This is a SLOW demonstration - the whole eight seconds is one unhurried sit and "
     "stand, with nothing rushed.\n"
     "  0.0 - 1.2s  standing still, facing the camera, feet apart\n"
     "  1.2 - 3.4s  SITTING DOWN, SLOWLY. His knees bend out to either side and he "
     "lowers his seat straight down onto the invisible seat. Back straight, shoulders "
     "square to the camera\n"
     "  3.4 - 5.0s  he stays seated, still, facing the camera\n"
     "  5.0 - 7.0s  STANDING UP, SLOWLY. He pushes through both feet and rises smoothly "
     "back to standing, still square to the camera\n"
     "  7.0 - 8.0s  standing still, facing the camera\n\n"
     "★SPREAD HIS LEGS APART A LITTLE SO THAT THE THIGHS, THE SHINS AND THE FEET ARE "
     "ALL VISIBLE. That is the single most important thing about the seated pose.\n"
     "His knees are open, roughly shoulder width or a bit wider, so nothing is hidden "
     "behind anything else: you can see the whole of both thighs, the whole of both "
     "shins, and both feet on the ground, all at the same time.\n\n"
     "★HE SITS HIGH, NOT LOW - THE SEAT IS AT KNEE HEIGHT, LIKE A LOW STONE LEDGE.\n"
     "He is NOT squatting, NOT crouching, NOT sitting on the floor and NOT folding up "
     "into a ball. His hips stay at about knee height, so when he is seated:\n"
     "  · his thighs are roughly HORIZONTAL, going forward from the hips\n"
     "  · his shins are roughly VERTICAL, dropping from the knees to the ground\n"
     "  · that makes a clean right angle at the knee, and BOTH shins keep their FULL "
     "LENGTH on screen - they are as long as they are when he stands\n"
     "The seated figure is only a little shorter than the standing one - about "
     "three-quarters of his standing height. If he ends up as a small crouched blob "
     "with no shins, that is wrong.\n\n"
     "★THE WHOLE LEG IS VISIBLE WHILE HE IS SEATED - THIGH, KNEE, SHIN AND FOOT.\n"
     "This is the rule that broke twice already: the legs were cut off at the knees and "
     "the feet vanished. Seen from the front, draw the seated pose like this so it "
     "cannot happen -\n"
     "  · the two KNEES are spread apart, one to the left and one to the right of the "
     "body, so the thighs are not hidden behind the torso\n"
     "  · from each knee the SHIN drops STRAIGHT DOWN, its full length drawn\n"
     "  · at the bottom of each shin a FOOT rests flat on the ground. BOTH feet are "
     "drawn and they are the LOWEST part of the whole figure - lower than the seat, "
     "lower than the knees, the very bottom of the drawing\n"
     "  · the gap of empty white between the two shins stays open the whole time\n"
     "If a frame would show the legs ending at the knees, it is wrong - draw it again "
     "with both shins and both feet all the way down to the ground.\n"
     "★Because it is slow, every single frame must be a clean readable drawing - no "
     "smearing, no blurring, no rushed frames.\n\n"
     + ROLL_NO_HANDS + "\n\n" + FRONT_LOCK + "\n\n"
     + COUNT_HARD + "\n\n" + LOCK_ONESHOT),

    # ★교정 16번 (사장님 2026-08-13)
    #   "하이 파이브는 정면 보다가 스틱맨과 졸라걸이 **마주 보고** 손을 들어
    #    하이 파이브 하고 **다시 정면으로 돌아서는 것**으로 만들어 보라."
    #   → 스틱맨은 오른쪽(졸라걸 쪽)을 보고, 졸라걸은 왼쪽을 본다. 짝이 맞아야 한다.
    ("high_five_turn", "front",                                  # 교정16 스틱맨 몫
     "The stickman turns to his side, gives a HIGH FIVE, and turns back to the camera. "
     "The other person is NOT drawn - only he is in the frame, and the partner he slaps "
     "is off to his RIGHT (the right-hand side of the screen).\n"
     "  0.0 - 1.2s  standing still, FACING THE CAMERA square-on, arms at his sides\n"
     "  1.2 - 2.4s  HE TURNS. His whole body rotates to his right so that he ends up "
     "side-on, in profile, LOOKING OFF TO THE RIGHT of the frame at his partner\n"
     "  2.4 - 3.2s  he swings his right arm up and back to wind up, still in profile\n"
     "  3.2 - 4.0s  THE SLAP. That arm swings up and forward and straightens high above "
     "his shoulder, hand open and flat, palm facing right - the moment of contact with "
     "the partner's hand\n"
     "  4.0 - 4.8s  the arm springs back a little from the impact, then holds high\n"
     "  4.8 - 5.6s  the arm comes back down to his side\n"
     "  5.6 - 6.8s  HE TURNS BACK. His whole body rotates back to the left until he is "
     "FACING THE CAMERA square-on again\n"
     "  6.8 - 8.0s  standing still, facing the camera, arms at his sides\n\n"
     "★The two turns and the slap must each be slow and clean enough to lift single "
     "frames out of. He turns about the vertical axis running down through his head and "
     "body - he stays on the same spot on the ground and never travels sideways.\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + LOCK_ONESHOT),

    # ★교정 16·17번 (사장님 2026-08-13)
    #   16 "마주 보고 하이 파이브 하고 다시 정면으로 돌아서는 것"
    #   17 "졸라걸은 다리가 움직이면서 **한 다리가 자꾸 없어지는데** 그렇지 않게"
    #   → 옛 zgirl_high_five 는 몸을 틀 때 먼 쪽 다리가 몸에 먹혔다. 다리 둘이 항상
    #     **따로 보이게** 못 박는다(측면일 때도 가까운 다리·먼 다리를 갈라 그린다).
    ("zgirl_high_five_turn", "zgirl_front",                      # 교정16·17 졸라걸 몫
     "Zollagirl turns to her side, gives a HIGH FIVE, and turns back to the camera. The "
     "other person is NOT drawn - only she is in the frame, and the partner she slaps is "
     "off to her LEFT (the left-hand side of the screen).\n"
     "  0.0 - 1.2s  standing still, FACING THE CAMERA square-on, arms at her sides\n"
     "  1.2 - 2.4s  SHE TURNS. Her whole body rotates to her left so that she ends up "
     "side-on, in profile, LOOKING OFF TO THE LEFT of the frame at her partner\n"
     "  2.4 - 3.2s  she swings her left arm up and back to wind up, still in profile\n"
     "  3.2 - 4.0s  THE SLAP. That arm swings up and forward and straightens high above "
     "her shoulder, hand open and flat, palm facing left - the moment of contact\n"
     "  4.0 - 4.8s  the arm springs back a little from the impact, then holds high\n"
     "  4.8 - 5.6s  the arm comes back down to her side\n"
     "  5.6 - 6.8s  SHE TURNS BACK. Her whole body rotates back to the right until she "
     "is FACING THE CAMERA square-on again\n"
     "  6.8 - 8.0s  standing still, facing the camera, arms at her sides\n\n"
     "★BOTH LEGS ARE VISIBLE IN EVERY SINGLE FRAME - THIS IS THE RULE THAT KEEPS "
     "BREAKING.\n"
     "She has exactly two legs and BOTH of them must be drawn, separately, in every "
     "frame including while she is turning and while she is in profile. When she is "
     "side-on, the far leg is NOT hidden behind the near leg and is NOT absorbed into "
     "the body - it is drawn slightly offset so two distinct legs are visible, one "
     "nearer and one further. A leg never fades out, never merges into the torso, never "
     "disappears for a frame and comes back. Two legs, two shoes, always.\n"
     "Her hair bun stays put on top of her head through both turns.\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + ZGIRL_ONCE),

    # ══ 2026-08-13 재제작 4종 (사장님 지시) ═══════════════════════════
    #   "앞구르기 뒷구르기, 발과 발 사이(졸라맨에 제일 많고), 졸라걸 다리 하나 없는 것
    #    저것 다시 만들자. 넷 다 플로우로 만들어서 컷아웃하고 64컷 투명컷 스틸 동영상."
    #   공통으로 GREY_PARTS 를 넣어 **신발·손·옷을 회색**으로 그리게 한다 —
    #   흰 신발은 흰 배경과 갈리지 않아 컷아웃이 발 속을 뚫어 버렸다.

    # ★사장님 지시(2026-08-13) — "천천히 구르라 하고, 일어서서 → 구르기 시작 →
    #   다시 일어서기, **총 8초 동안 천천히 한 번만** 해서 만든다."
    #   빨리 구르면 Flow 가 프레임을 뭉개고 팔다리를 넷·다섯으로 터뜨린다. 8초를
    #   통째로 한 번의 구르기에 쓰면 프레임마다 자세가 또렷하게 남는다.
    ("forward_roll2", "side",                                    # 앞구르기 재제작
     "The stickman does ONE SINGLE FORWARD ROLL, VERY SLOWLY, over the whole eight "
     "seconds, seen from the SIDE, moving to the RIGHT. This is a slow-motion "
     "demonstration roll - there is no hurry anywhere in the clip.\n"
     "  0.0 - 1.0s  STANDING near the LEFT edge, side-on, facing right, still\n"
     "  1.0 - 2.5s  he slowly bends forward and lowers both arms down to the ground in "
     "front of his feet\n"
     "  2.5 - 6.0s  THE ROLL, SLOWLY - three and a half seconds for one single "
     "somersault. He tucks his head in, rolls over his shoulders, then his back, then "
     "his hips, and comes over onto his feet, travelling to the right. Every stage is "
     "unhurried and clearly readable.\n"
     "  6.0 - 7.0s  he rises slowly back up to STANDING, near the RIGHT of the frame\n"
     "  7.0 - 8.0s  standing still, side-on, facing right\n\n"
     "★ONE ROLL ONLY, AND IT IS SLOW. He does not roll twice, does not roll fast, does "
     "not bounce, does not spin. The whole eight seconds contains exactly one unhurried "
     "somersault, book-ended by standing still. Because it is slow, every single frame "
     "must be a clean readable drawing - no smearing, no blurring, no rushed frames.\n\n"
     "★THE TWO FEET NEVER FUSE INTO ONE. Through the whole roll - tucked, upside down, "
     "and landing - the two shoes stay as TWO separate shapes with a clear open gap "
     "between them. They never merge into a single blob, never overlap into one outline, "
     "and neither one disappears behind the other.\n\n"
     "★WHERE EACH LIMB IS, MOMENT BY MOMENT, THROUGH THE ROLL. Follow this exactly - "
     "the roll is where extra arms and legs keep appearing, so nothing is left to "
     "guess:\n"
     "  · hands down    — BOTH arms reach down together to the ground in FRONT of his "
     "feet, side by side, elbows almost straight. Two arm lines, parallel, not crossed.\n"
     "  · tuck          — BOTH arms stay bent close in beside his head, and BOTH knees "
     "come up together to his chest. Two arms, two legs, all four folded IN toward the "
     "body - none of them sticking out sideways, none fanned out, none spread apart.\n"
     "  · upside down   — he is a compact tucked ball. The two legs stay together as a "
     "pair; the two arms stay together as a pair. Four limb lines in total and they are "
     "SHORT because they are folded, never long spokes radiating out from the body.\n"
     "  · coming up     — the two legs unfold together and plant, the two arms swing "
     "forward together. Still exactly two of each.\n"
     "★HE IS NEVER A STAR SHAPE. At no moment do limbs radiate out from the middle like "
     "spokes of a wheel or the legs of a spider. If a frame starts to look like five or "
     "six lines fanning out of one point, that frame is wrong - draw it again as a "
     "tucked human body with two folded arms and two folded legs.\n\n"
     + ROLL_HARD + "\n\n" + ROLL_NO_HANDS + "\n\n" + COUNT_HARD + "\n\n" + LOCK_TRAVEL),

    # ★1차본이 앞구르기로 나왔다(2026-08-13). 원인 — "뒤로 구른다"만 적고 **몸이 도는
    #   방향**을 안 박았다. 회전 방향을 신체 부위가 지나가는 순서로 못 박는다.
    ("back_roll", "side",                                        # 뒷구르기 새로
     "The stickman does ONE BACKWARD ROLL along the ground, seen from the SIDE. He is "
     "side-on and FACING RIGHT the whole time, and he travels to the LEFT — backwards, "
     "the way he is NOT looking.\n"
     "  0.0 - 1.5s  standing near the RIGHT edge, side-on, facing right\n"
     "  1.5 - 2.4s  he squats down and sits back onto the ground behind his heels, "
     "putting both hands up beside his ears with the palms turned up and back\n"
     "  2.4 - 4.8s  THE ROLL — BACKWARDS. His bottom touches the ground first, then his "
     "lower back, then his upper back and shoulders, then the back of his head passes "
     "the ground, and finally his legs swing over his head and his feet land on the "
     "ground BEHIND where his head was. He pushes with both hands as his hips pass over. "
     "One roll only, travelling to the LEFT.\n"
     "  4.8 - 5.8s  he rises to standing, near the LEFT of the frame, still facing right\n"
     "  5.8 - 8.0s  standing still, side-on\n\n"
     "★THE DIRECTION OF THE ROLL IS THE POINT OF THIS CLIP.\n"
     "Seen from this side view with his nose pointing RIGHT, his body rotates CLOCKWISE "
     "— the top of his head travels BACKWARD and DOWN toward the ground behind him, "
     "while his feet travel FORWARD and UP over the top. This is the OPPOSITE of a "
     "forward roll. He must NOT tip forward, must NOT put his head down in front of his "
     "feet, and must NOT dive over his own shoulders. The order the body touches the "
     "ground is: BOTTOM, then BACK, then SHOULDERS, then head — never hands-then-head "
     "first.\n"
     "★HE FACES RIGHT AT THE START AND FACES RIGHT AT THE END. He rotates only about "
     "the horizontal axis through his hips, never about the vertical axis — his nose is "
     "on the right-hand side of his head in every frame, even while inverted.\n"
     "★THE TWO FEET NEVER FUSE INTO ONE. Two separate shoes with a clear gap between "
     "them in every frame, including while tucked and inverted.\n"
     "★HIS HEAD STAYS THE SAME SIZE in every frame — it is a circle of constant "
     "diameter, never enlarged as it comes toward the camera, never drawn bigger than "
     "the head in the first frame.\n\n"
     + ROLL_HARD + "\n\n" + ROLL_NO_HANDS + "\n\n" + COUNT_HARD + "\n\n" + LOCK_TRAVEL),

    ("zman_run_side2", "zman_side",                              # 졸라맨 재제작
     "Zollaman RUNS IN PLACE, seen from the SIDE, facing to the RIGHT. A clear running "
     "cycle with a long stride: knees lift high, the trailing leg kicks up behind, and "
     "both feet leave the ground at the airborne moment. Roughly five full strides over "
     "the eight seconds. The body leans slightly forward. Stay side-on - do not turn "
     "toward or away from the camera.\n\n"
     "★THE TWO FEET NEVER FUSE INTO ONE - THIS IS THE RULE THAT KEEPS BREAKING.\n"
     "At every instant his two shoes are TWO separate shapes with a clear open gap of "
     "background between them. When the legs cross in the middle of the stride, draw the "
     "near shoe in front of the far shoe with the outline of each still complete - never "
     "merge them into one blob, never let the gap between them close up, never let one "
     "shoe vanish inside the other. The same for the two hands.\n"
     "The gap between his two legs is likewise always open - the far leg is drawn "
     "separately from the near leg and is never absorbed into the body.\n\n"
     + RUN_LIMBS + "\n\n" + GREY_PARTS + "\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + ZMAN_LOOP),

    ("zgirl_high_five2", "zgirl_front",                          # 졸라걸 재제작
     "Zollagirl gives a HIGH FIVE, seen from the FRONT, square-on to the camera. The "
     "other person is NOT drawn - only she is in the frame.\n"
     "  0.0 - 1.5s  standing still, facing the camera, feet apart\n"
     "  1.5 - 2.4s  she swings ONE arm up and back to wind up\n"
     "  2.4 - 3.2s  THE SLAP. That arm swings up and forward, straightening high above "
     "her shoulder with the hand open and flat, reaching up and slightly to the side - "
     "the moment of contact\n"
     "  3.2 - 4.2s  the arm springs back a little from the impact, then holds high\n"
     "  4.2 - 5.5s  the arm comes back down to her side\n"
     "  5.5 - 8.0s  standing still, facing the camera, feet apart\n\n"
     "★BOTH LEGS ARE VISIBLE IN EVERY SINGLE FRAME - THIS IS THE RULE THAT KEEPS "
     "BREAKING. In the old clip her far leg vanished for the whole second half.\n"
     "She has exactly two legs and BOTH are drawn, separately, in every frame from the "
     "first to the last. Her feet stay planted apart, about shoulder width, so that the "
     "gap of background between her two legs and between her two shoes is OPEN in every "
     "frame. A leg never merges into the other leg, never merges into the torso, never "
     "fades out, never disappears for a few frames and comes back. Two legs, two shoes, "
     "always, and always separated by a visible gap.\n"
     "Her hair bun stays put on top of her head.\n\n"
     + GREY_PARTS + "\n\n" + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + ZGIRL_ONCE),

    # ══ 광화문광장 퍼포먼스 4종 (사장님 지시 2026-08-13) ═════════════════
    #   "이 광화문 광장에서 분수대 앞에서 어떤 퍼포먼스를 한번 해 보면 좋을지,
    #    또 실제로 한 것 중에서 어떤 게 멋진 것이 있는지 한번 찾아보고 그것을 만들어 보자."
    #   → 조사 결과 **실제로 그 광장에서 하는 것**만 골랐다.
    #     ① 터널분수(77물줄기 아치) 뛰어 통과 — 여름마다 아이들이 뛰어다닌다
    #     ② 한글분수(노즐 225개·천지인 배치) 위에서 — 한글 28자를 물줄기로 뿜는 글자 분수
    #     ③ 태권도 시범 발차기 — 국기원 시범단이 광화문에서 공연
    #     ④ 수문장 교대의식 행진 — 광장 북쪽 끝에서 하루 두 번
    #   배경은 따로 만들고(bg_defs), 여기서는 **캐릭터 동작만** 만든다.

    ("perf_tunnel_jump", "side",                                 # ① 터널분수 통과
     "The stickman RUNS and then LEAPS through an archway, seen from the SIDE, moving "
     "to the RIGHT. The archway itself is NOT drawn - only he is in the frame.\n"
     "  0.0 - 1.5s  standing near the LEFT edge, side-on, facing right\n"
     "  1.5 - 3.5s  he runs to the right with a long, happy stride\n"
     "  3.5 - 5.0s  THE LEAP. He pushes off one foot and throws BOTH ARMS STRAIGHT UP "
     "over his head in a big cheer as he sails through the air, body stretched long, "
     "both legs trailing then tucking\n"
     "  5.0 - 6.0s  he lands on both feet near the RIGHT of the frame, knees absorbing, "
     "arms coming down\n"
     "  6.0 - 8.0s  he straightens up, gives one big WAVE with one arm, and stands\n\n"
     "★The leap with both arms overhead is the frame that gets lifted out - make it "
     "clean, high and joyful.\n\n" + GREY_PARTS + "\n\n" + COUNT_HARD + "\n\n"
     + LOCK_TRAVEL),

    ("perf_hangeul_point", "front",                              # ② 한글분수 위에서
     "The stickman stands on the spot and POINTS DOWN then UP four times in turn, seen "
     "from the FRONT, square-on to the camera. He is showing something rising from the "
     "ground around him - the thing itself is NOT drawn.\n"
     "  0.0 - 1.0s  standing still, facing the camera, arms at his sides\n"
     "  1.0 - 2.0s  he STAMPS one foot on the ground and points DOWN with one hand\n"
     "  2.0 - 3.5s  that arm sweeps UP and out to his right, following something rising\n"
     "  3.5 - 5.0s  the other arm sweeps UP and out to his left in the same way\n"
     "  5.0 - 6.5s  BOTH arms go up and out wide together, a delighted 'look at this' "
     "gesture, head tipping back a little\n"
     "  6.5 - 8.0s  arms come down and he stands still, facing the camera\n\n"
     "★He never leaves his spot and never turns - the sweeps are big and readable.\n\n"
     + FRONT_LOCK + "\n\n" + GREY_PARTS + "\n\n" + COUNT_HARD + "\n\n" + LOCK_ONESHOT),

    ("perf_taekwondo", "side",                                   # ③ 태권도 발차기
     "The stickman performs ONE TAEKWONDO KICK, seen from the SIDE, facing RIGHT. There "
     "is no target and no board drawn - only he is in the frame.\n"
     "  0.0 - 1.5s  he stands in a ready stance, side-on, fists held at his waist\n"
     "  1.5 - 2.5s  he steps forward and coils, weight onto the back leg, arms guarding\n"
     "  2.5 - 4.5s  THE KICK. He drives one knee up and snaps that leg out straight and "
     "HIGH - the foot goes above head height - while the other foot stays planted and "
     "both arms swing for balance. Hold the extended kick for a beat.\n"
     "  4.5 - 6.0s  the leg comes down under control and he settles back into stance\n"
     "  6.0 - 8.0s  he brings his feet together and BOWS from the waist to the camera\n\n"
     "★The high extended kick is the frame that gets lifted out. Exactly one leg kicks "
     "and one leg stands - never three legs, never a blurred trail behind the kick.\n\n"
     + GREY_PARTS + "\n\n" + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + LOCK_ONESHOT),

    # ★수문장을 **옆모습으로 돌려세우는** 클립 (사장님 지시 2026-08-13 "가로 하자")
    #   정지 이미지를 옆모습으로 두 번 시도했으나 Flow 가 두 번 다 정면으로 그렸다.
    #   [[flow-fixed-angle-fails-use-rotation]] — **각도는 고정 못 하지만 회전은 잘 된다.**
    #   그래서 8초 동안 정면 → 측면으로 도는 클립을 만들고 **측면 프레임을 골라 쓴다.**
    ("guard_turn", "guard",
     "The stickman palace guard TURNS ON THE SPOT, from facing the camera round to an "
     "exact side profile. He keeps holding the tall pole upright beside him the whole "
     "time.\n"
     "  0.0 - 1.5s  FRONT view, square-on to the camera - exactly the pose in the source "
     "image, held still\n"
     "  1.5 - 5.0s  HE TURNS SLOWLY to his left, rotating about the vertical axis that "
     "runs straight down through his hat and body. He passes through three-quarters and "
     "keeps going\n"
     "  5.0 - 8.0s  EXACT SIDE PROFILE, 90 degrees, FACING RIGHT, held perfectly still "
     "for these three full seconds. Now his nose and chin break the head circle on the "
     "right, only one eye shows, his shoulders line up one behind the other so the body "
     "is a narrow vertical line, the hat brim reads as a flat line either side of the "
     "head, and the robe hangs narrow down his side\n\n"
     "★THE LAST THREE SECONDS ARE THE POINT OF THIS CLIP - single frames get lifted out "
     "of them, so the profile must be clean, still and unmistakable.\n"
     "★He stays on the same spot and does not walk. The pole stays vertical throughout, "
     "never tilting. The hat, robe, belt and sword stay exactly as drawn in the source "
     "image - do not restyle them, do not add detail.\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + LOCK_ONESHOT),

    # ★기준 이미지 = `guard_turn` 클립의 **96번 프레임**(4.0초 · 사장님이 고르심).
    #   수문장 옷·갓·검·창이 다 갖춰지고 얼굴이 오른쪽을 본 자세다.
    #   ※정지 이미지를 옆모습으로 두 번 뽑았으나 Flow 가 두 번 다 정면으로 그렸다 →
    #     회전 클립을 만들어 **프레임을 골라내는** 방식으로 얻었다.
    ("perf_guard_march", "guard_side",                           # ④ 수문장 행진
     "The palace guard stickman in the source image MARCHES ON THE SPOT, keeping the "
     "same costume and the same tall straight POLE held upright in his hand.\n"
     "  0.0 - 6.5s  a slow, formal ceremonial march ON THE SPOT: each knee lifts HIGH to "
     "waist height in turn, the foot placed down flat and deliberate, back straight, "
     "chin level. Roughly five slow steps over these seconds. The pole stays VERTICAL "
     "beside him the whole time, its bottom tapping the ground with each step.\n"
     "  6.5 - 8.0s  he halts with his feet together, STAMPS once, and stands to "
     "attention, pole vertical, perfectly still\n\n"
     "★KEEP HIM EXACTLY AS HE IS IN THE SOURCE IMAGE. Same wide-brimmed hat, same long "
     "open robe with the spine line showing through, same belt, same short sword at the "
     "hip, same tall pole. Same thin black lines on plain white, same empty circle for a "
     "head with two dot eyes and one mouth line. Do not restyle him, do not add colour, "
     "shading, patterns or detail, do not turn him into a drawn person.\n"
     "★HE KEEPS HOLDING THE POLE THE WHOLE TIME - he never lets go of it and it never "
     "disappears. It stays a plain straight vertical line from the ground to above his "
     "hat, never tilting and never crossing his body.\n"
     "★HIS FACE STAYS ON. Two dot eyes and one mouth line are visible in every single "
     "frame - they never fade out while he moves.\n"
     "★The high knee lift and the vertical pole are what make this read as a ceremonial "
     "guard - keep both unmistakable.\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + LOCK),

    # ★기준 이미지 = `guard_turn` 클립의 **88번 프레임**(3.67초 · 사장님이 고르심).
    #   뒤통수가 빈 동그라미인 후면 자세다. 얼굴이 없다는 것이 이 컷의 핵심이라
    #   프롬프트에서 몇 번이고 못 박는다 — Flow 는 놔두면 얼굴을 그려 넣는다.
    # ★제자리 걷기(트레드밀)로 만든다. 멀어지는 것은 2.5D 무대 엔진이 발 y 로
    #   키를 줄여 주므로(stage2d.h_at), 클립이 직접 작아지면 오히려 컷마다 키가
    #   달라져 규격(740)에 못 맞춘다.
    ("perf_guard_away", "guard_back",                            # ④-2 멀어지는 뒷모습
     "The palace guard stickman in the source image is seen FROM BEHIND, walking AWAY "
     "from the camera. He walks ON THE SPOT so the cycle can loop.\n"
     "  0.0 - 8.0s  a steady, even walk seen from directly behind: the legs alternate "
     "clearly below the hem, one heel lifting as the other foot plants, the shoulders "
     "rocking gently with each step, the robe swinging a little at the hem. About six "
     "unhurried steps over the eight seconds. The pole stays VERTICAL in his hand the "
     "whole time, its bottom tapping the ground with each step.\n\n"
     "★WE ONLY EVER SEE HIS BACK. He never turns round, never looks over his shoulder, "
     "and his head NEVER shows a face. The head is an EMPTY CIRCLE - no eyes, no nose, "
     "no mouth, nothing inside it at any moment. That empty circle is the back of his "
     "head and it must stay empty in every single frame.\n"
     "★KEEP HIM EXACTLY AS HE IS IN THE SOURCE IMAGE. Same wide-brimmed hat seen from "
     "behind, same long robe with the spine line down the back, same belt, same short "
     "sword hanging at his side, same tall pole. Same thin black lines on plain white. "
     "Do not restyle him, do not add colour, shading, patterns or detail.\n"
     "★HE KEEPS HOLDING THE POLE THE WHOLE TIME - it never disappears and never tilts.\n"
     "★HE DOES NOT SHRINK AND DOES NOT DRIFT. He stays the same size in the middle of "
     "the frame from the first frame to the last - the walking-away feeling comes from "
     "the back view alone, not from the camera or from him getting smaller.\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + LOCK),

    ("forward_roll", "side",                                     # A4 · S4
     "The stickman does ONE FORWARD ROLL along the ground, seen from the SIDE, moving "
     "to the RIGHT.\n"
     "  0.0 - 1.5s  standing near the LEFT edge, side-on, facing right\n"
     "  1.5 - 2.2s  he bends forward and puts both hands down on the ground\n"
     "  2.2 - 4.5s  THE ROLL. He tucks his head in, rolls over his shoulders and back "
     "in one smooth forward somersault along the ground, travelling to the right. One "
     "roll only.\n"
     "  4.5 - 5.5s  the roll carries him up onto his feet and he stands, near the "
     "RIGHT of the frame\n"
     "  5.5 - 8.0s  standing still, side-on\n\n" + LOCK_TRAVEL),

    ("sit_stand", "side",                                        # A5 · S5·S6·S15·S17
     "The stickman SITS DOWN and then STANDS BACK UP, seen from the SIDE, facing "
     "RIGHT. There is no chair and no bench - he sits on an invisible seat at "
     "about knee height.\n"
     "  0.0 - 1.5s  standing still, side-on\n"
     "  1.5 - 3.2s  SITTING DOWN. He bends his knees and hips and lowers his seat "
     "smoothly onto the invisible seat, back straight, thighs coming horizontal, "
     "shins vertical, feet flat on the ground\n"
     "  3.2 - 5.0s  he stays seated, still\n"
     "  5.0 - 6.6s  STANDING UP. He leans forward slightly, pushes through his feet "
     "and rises smoothly back to standing\n"
     "  6.6 - 8.0s  standing still, side-on\n\n"
     "★Both halves must be clean and slow enough to lift single frames out of, because "
     "the sitting half will also be played BACKWARDS to make other transitions.\n\n"
     + LOCK_ONESHOT),

    ("hop_down", "side",                                         # A6 · S6
     "The stickman HOPS DOWN one step, seen from the SIDE, facing RIGHT. There is no "
     "staircase drawn - he simply drops a short distance, as if off an invisible step.\n"
     "  0.0 - 1.5s  standing still, side-on\n"
     "  1.5 - 2.1s  he bends his knees to load\n"
     "  2.1 - 3.2s  THE HOP. He steps off and drops a short way, both feet leaving the "
     "ground, arms lifting a little for balance\n"
     "  3.2 - 4.0s  he lands on both feet, knees bending to absorb, then straightens\n"
     "  4.0 - 8.0s  standing still, side-on\n\n"
     "★One hop only. It will be played twice in a row to make two steps, so the last "
     "pose must match the first.\n\n" + LOCK_ONESHOT),

    ("reach_catch", "front",                                     # A7 · S10 · S22
     "The stickman REACHES OUT AND CATCHES something, seen from the FRONT, square-on "
     "to the camera. Nothing is drawn in his hand - only the reaching and catching.\n"
     "  0.0 - 1.5s  standing still, facing the camera\n"
     "  1.5 - 2.2s  he suddenly looks up and to his left\n"
     "  2.2 - 3.4s  THE REACH. He lunges, extending ONE arm up and out to the side, "
     "the other arm swinging back for balance, his weight shifting onto the near foot\n"
     "  3.4 - 4.2s  the hand CLOSES on something and he pulls it in toward his chest\n"
     "  4.2 - 5.4s  he brings both hands together in front of his chest, cradling it\n"
     "  5.4 - 8.0s  standing still, hands held at the chest\n\n"
     "★The arm never stretches - it reaches by rotating at the shoulder and "
     "straightening at the elbow, keeping its fixed length.\n\n" + LOCK_ONESHOT),

    ("tiptoe", "side",                                           # A8 · S19
     "The stickman CREEPS FORWARD ON TIPTOE, seen from the SIDE, facing RIGHT. He is "
     "sneaking up on something quietly.\n\n"
     "The whole eight seconds are one continuous tiptoe cycle, repeated IN PLACE: he is "
     "up on the balls of his feet with the heels off the ground, his knees stay bent, "
     "and his upper body is CROUCHED FORWARD and lowered. Each step is slow, high and "
     "exaggerated: the knee comes up, the toe reaches out and is placed down carefully, "
     "then the weight rolls onto it. Roughly four slow steps over the eight seconds.\n\n"
     "★He stays crouched the whole time - he never straightens up to full height.\n\n"
     "★★TWO ARMS, AND THEY ARE HELD APART SO YOU CAN TELL THEM APART - MOST IMPORTANT.\n"
     "He has two arms and BOTH are visible, but they are never in the same place and "
     "never lie along the same line:\n"
     "  - the NEAR arm (the one on the camera side) is bent at the elbow and raised "
     "HIGH, its hand up near his chin, in front of his chest\n"
     "  - the FAR arm is bent and held LOW, its hand down beside his hip, behind and "
     "below the near one\n"
     "There is a clear, obvious vertical GAP between the two hands at all times - about "
     "the height of his head. They never cross, never line up, never touch, never merge "
     "into each other, and never swap places.\n"
     "So each frame has EXACTLY TWO arm lines: one high, one low. Count them: high arm, "
     "low arm, that is all. If a third line appears anywhere near the shoulders - a "
     "parallel line, a trailing line, a spare line between the two - that is wrong; "
     "there are only ever two arms.\n\n"
     "★Legs: BOTH legs are visible and they swing apart when he steps. Exactly two leg "
     "lines, never three.\n\n"
     + COUNT_HARD + "\n\n" + CENTER_HARD + "\n\n" + LOCK),

    ("butt_fall", "side",                                        # A9 · S20
     "The stickman is startled, FALLS BACKWARDS ONTO HIS BOTTOM, and gets up again. "
     "Seen from the SIDE, facing RIGHT.\n"
     "  0.0 - 1.2s  crouching low, peering forward\n"
     "  1.2 - 1.8s  THE FRIGHT. He jerks upright and both arms fly up\n"
     "  1.8 - 2.8s  THE FALL. He topples backwards and lands sitting on the ground, "
     "legs out in front of him, hands planted behind for support\n"
     "  2.8 - 4.0s  he sits on the ground and scratches his head with one hand\n"
     "  4.0 - 5.6s  he rolls his weight forward, plants his feet and STANDS BACK UP\n"
     "  5.6 - 8.0s  standing still, side-on\n\n" + LOCK_ONESHOT),

    ("pick_up", "side",                                          # A10 · S8
     "The stickman CROUCHES DOWN, PICKS SOMETHING UP off the ground, and stands back "
     "up holding it. Seen from the SIDE, facing RIGHT. Nothing is drawn in his hand.\n"
     "  0.0 - 1.2s  standing still, side-on\n"
     "  1.2 - 2.6s  CROUCHING. He bends his knees deeply and squats right down, back "
     "leaning forward, one hand going toward the ground in front of his feet\n"
     "  2.6 - 3.4s  the hand closes on something on the ground\n"
     "  3.4 - 5.0s  STANDING UP. He rises smoothly back to full height, bringing the "
     "closed hand up with him\n"
     "  5.0 - 6.2s  he lifts the hand to chest height and holds it out a little, as if "
     "showing what he found\n"
     "  6.2 - 8.0s  standing still, hand held out at chest height\n\n" + LOCK_ONESHOT),

    ("high_five", "front",                                       # A11 · S17
     "The stickman gives a HIGH FIVE, seen from the FRONT, square-on to the camera. "
     "The other person is NOT drawn - only he is in the frame.\n"
     "  0.0 - 1.5s  standing still, facing the camera\n"
     "  1.5 - 2.4s  he swings ONE arm up and back to wind up\n"
     "  2.4 - 3.2s  THE SLAP. That arm swings up and forward, straightening high above "
     "his shoulder with the palm open and flat, reaching up and slightly to the side - "
     "the moment of contact\n"
     "  3.2 - 4.2s  the arm springs back a little from the impact, then holds high\n"
     "  4.2 - 5.5s  the arm comes back down to his side\n"
     "  5.5 - 8.0s  standing still, facing the camera\n\n"
     "★The open palm at full stretch is the frame that will be lifted out - make that "
     "reach clean, high and unambiguous.\n\n" + LOCK_ONESHOT),

    ("shoulder_arm", "front",                                    # A12 · S15
     "The stickman puts an ARM AROUND SOMEONE'S SHOULDERS, seen from the FRONT, "
     "square-on to the camera. The other person is NOT drawn - only he is in the frame, "
     "and he is SEATED on an invisible bench.\n"
     "  0.0 - 1.8s  sitting on the invisible bench, hands on his knees, facing the "
     "camera\n"
     "  1.8 - 3.2s  he lifts ONE arm out to his side and up to shoulder height\n"
     "  3.2 - 4.4s  THE ARM AROUND. That arm reaches out sideways and the forearm bends "
     "forward, as if laying across the shoulders of someone sitting beside him. The "
     "elbow stays out, the hand hangs down past where the other person's far shoulder "
     "would be.\n"
     "  4.4 - 8.0s  he HOLDS that pose, sitting, facing the camera, completely still\n\n"
     "★The long held pose at the end is what gets used - keep it steady and identical "
     "from 4.4s onward.\n\n" + LOCK_ONESHOT),

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
