# -*- coding: utf-8 -*-
"""W1-2 배경 — 광화문광장 (korea 168경 week1/day2). **캐릭터와 상호작용하는 배경.**

★사장님 지시(2026-08-11): **"내가 극적으로 생각하는 것은 배경 동영상과 캐릭터가
  상호작용하는 것이다."**

그래서 배경을 '흔들리는 그림'으로 만들지 않는다. 배경 안에 **캐릭터가 건드릴 물체**를
심고, 그 물체가 **캐릭터 쪽으로 움직이게** 만든다. 합성 단계에서 캐릭터의 동작이 그
타이밍에 맞물린다(오이가 굴러오는 순간에 카드를 든다).

## ★2씬당 배경 하나 (사장님 지시 2026-08-12)
26씬 → **14개**. 장소 경계를 지키면서 두 씬씩 갈랐다.

| # | 키 | 씬 | 종류 | 배경이 하는 일 ↔ 캐릭터가 하는 일 |
|---|---|---|---|---|
| 1 | `plaza_arrive`  | S1–S2   | 동영상 | 분수 줄이 차례로 솟는다 ↔ 소실점에서 달려와 손을 든다 `5.0s` |
| 2 | `plaza_gate`    | S3–S4   | 동영상 | 비둘기 떼가 일제히 날아오른다 ↔ 앞구르기 착지 `2.2s` |
| 3 | `steps_seat`    | S5–S6   | 정지  | 걸터앉을 넓은 계단 |
| 4 | `steps_rail`    | S7      | 정지  | 손 높이 난간 — 잡고 몸을 기울인다 |
| 5 | `stall_cuke`    | S8–S9   | 동영상 | **오이가 굴러 내려와 멈춘다** ↔ 쭈그려 집는다 `4.0s` |
| 6 | `stall_milk`    | S10–S11 | 동영상 | **우유팩이 기울어 미끄러진다** ↔ 손을 뻗어 받는다 `5.2s` |
| 7 | `stall_rail`    | S12     | 정지  | 좌판 옆 난간 — 기댄다 |
| 8 | `fountain_burst`| S13–S14 | 동영상 | **물기둥이 솟구쳤다 흩어진다** ↔ 놀라 백플립 `3.5s`, 물방울 다섯 짚기 `4~6s` |
| 9 | `bench_pair`    | S15–S16 | 정지  | 둘이 앉을 벤치 |
| 10| `bench_open`    | S17–S18 | 정지  | 벤치 앞 넓은 바닥 — 셋이 나란히 선다 |
| 11| `path_fox`      | S19–S20 | 동영상 | **여우가 고개를 내밀었다 숨는다** ↔ 살금살금 `2.5s`, 엉덩방아 `4.5s` |
| 12| `path_leaves`   | S21–S22 | 동영상 | **잎 하나가 손 높이로 내려온다** ↔ 점프해서 잡는다 `3.4s` |
| 13| `dusk_lanterns` | S23–S24 | 동영상 | **등이 하나씩 켜진다** ↔ 셋이 동시에 손을 든다 `5.5s` |
| 14| `dusk_calm`     | S25–S26 | 동영상 | 하늘이 어두워지며 별이 돋는다 ↔ 거울 · 퇴장 |

## 규칙
· ★**어느 쪽도 비우지 않는다.** 캐릭터가 좌우를 다 쓰며 움직인다 —
  넓게 쓸수록 동선이 산다 [[bg-never-empty-left-side]]
· ★**층·줄·칸·수직경계 금지.** 한 장면이 화면 전체에 끊김 없이 이어진다
· 상호작용 물체는 **화면 아래쪽 손 높이**로 와서 멈춘다(좌우는 가리지 않는다)
· 카메라는 고정 — 물체가 움직이지 카메라가 움직이지 않는다
· 화면 안 글자 절대 금지
"""

STYLE = (
    "Flat 2D children's picture-book illustration, clean vector look, soft pastel palette, "
    "gentle warm daylight, simple shapes, bold clean outlines, flat cel shading. "
    "No photorealism, no harsh shadows, no film grain, no people, no animals except where "
    "stated. "
    "★ONE CONTINUOUS SCENE ACROSS THE WHOLE 16:9 FRAME. Left, middle and right all belong "
    "to the same place: the ground line, the horizon and the perspective run unbroken all "
    "the way across, edge to edge. "
    "★THE PICTURE IS NEVER DIVIDED. No hard vertical edge splitting it into a detailed "
    "side and a flat blank side. No horizontal banding or stepped layers stacked up the "
    "frame. No stripes, no panels, no compartments, no boxes, no framing borders, no "
    "split-screen, no diptych. Not a single seam or dividing line anywhere in the image - "
    "wherever one area meets another it blends or overlaps naturally, the way real "
    "scenery does. "
    "Open, restful areas are welcome and soft colour gradients in sky, water and paving "
    "are welcome; they simply have to be part of the same scene, easing gently into the "
    "rest of it rather than being cut off from it. "
    "★DO NOT RESERVE AN AREA for anything - not for lettering, not for a figure. "
    "Compose the scene for its own sake. "
    "★Camera is locked: no pan, no zoom, no shake. Only the described object moves. "
    "Absolutely NO text, letters, numbers, signs or logos anywhere."
)

# ★상호작용 배경의 공통 규격 — 물체가 **캐릭터 손이 닿는 곳**으로 와서 멈춰야 한다.
REACH = (
    "★THE MOVING OBJECT IS WHAT THIS CLIP EXISTS FOR. It travels clearly and unhurriedly, "
    "big enough to read at a glance, and it comes to rest LOW IN THE FRAME - in the "
    "bottom third, at about the height a standing child's hand would reach down to. "
    "It settles somewhere in the open middle of the picture, not tucked into a corner and "
    "not hidden behind anything, so a figure can be placed beside it later and appear to "
    "touch it. Once it stops it stays perfectly still for the rest of the clip."
)

# ★★관중은 **실루엣**으로 (사장님 지시 2026-08-13)
#   "내 캐릭터 이외의 등장인물들이 많이 필요한데 **실루엣 처리** 한다."
#   → 배경에 사람을 그리면 우리 스틱맨과 그림체가 싸운다. 어두운 실루엣으로 두면
#     인파가 있는 광장이 되면서도 주인공이 또렷하게 읽힌다.
CROWD = (
    "★THE OTHER PEOPLE ARE PLAIN DARK SILHOUETTES - THIS IS IMPORTANT.\n"
    "Every other person in the picture is a flat, solid, dark grey-blue silhouette with "
    "no face, no features, no clothing detail and no outline drawing - just a filled "
    "shape. They are clearly people by their posture alone: standing, watching, "
    "clapping, holding a child's hand, raising a phone to take a photo. They are placed "
    "AROUND THE EDGES and in the MIDDLE DISTANCE, never in the open centre foreground, "
    "so the main character can stand there later. Vary their heights so it reads as a "
    "real crowd. They do not move."
)

# ★태권도 시범 — **움직이는 사람도 전원 실루엣**, 다만 인체는 정확해야 한다.
#   (사장님 지시 2026-08-14) "보조사람들과 격파하는 선수까지 모두 **해부학적 인체를
#   가진 실루엣**으로 한다."
#   CROWD 는 '가만히 선 구경꾼'이라 가운데서 움직이는 선수까지 덮지 못한다.
TKD_FIGURES = (
    "★EVERY PERSON IN THIS SHOT IS A PLAIN DARK SILHOUETTE - the kicker and the "
    "assistants holding the boards just as much as the watching crowd. Flat, solid, "
    "dark grey-blue filled shapes with no face, no features, no clothing detail, no "
    "outline. Their white uniforms and belts are NOT drawn - only the shape.\n"
    "★BUT THE BODIES MUST BE ANATOMICALLY CORRECT. Each silhouette has exactly ONE "
    "head, TWO arms and TWO legs - never three, never a spare limb. Elbows, knees, "
    "shoulders and hips bend only the way a real body bends: no hyperextension, no "
    "bending backwards, no rubbery or noodle-like limbs, no limb passing through "
    "another. Hands and feet stay attached. The pose must read as a real athlete's "
    "body at every instant, because the silhouette has nothing else to read by."
)

# ★격파는 **닿는 그 순간 한 번에** 깨진다 (사장님 지적 2026-08-14)
#   1세트에서 발이 송판에 닿았는데 안 깨지고 **두 번째 접촉에서** 깨졌다. 그건 실패한
#   격파로 보인다. 닿음=깨짐이 한 프레임에 붙어야 한다.
TKD_BREAK_HARD = (
    "★THE BOARD BREAKS ON THE FIRST AND ONLY CONTACT. The instant the foot reaches the "
    "board it snaps - contact and break are the same moment. The foot NEVER touches the "
    "board, bounces off, and comes back for a second try; there is no failed first "
    "attempt. The foot carries straight on THROUGH the space where the board was, "
    "following through past it, while the two halves fly apart behind the foot."
)

# ★격파가 끝나면 **다음 세트 준비까지** 한 호흡에 이어 그린다 (사장님 2026-08-14)
#   "격파 후 준비는 사람들이 흩어진 파편을 모으고 다시 모여서 대열을 만들어
#    준비하는 과정까지 연속으로 자연스럽게 그린다."
#   "준비 과정은 **달리면서 아주 빠르게** 파편을 정리하고 대열을 정비해서 새로 선다."
# ★뒷정리는 **흩어진 조각만** 줍는다 (사장님 지적 2026-08-14)
#   앞판에서는 송판을 들고 있던 사람 손에서 송판이 사라지고, 사람도 하나만 남고
#   다 사라졌다. 줍는 것은 **깨져서 바닥에 떨어진 조각**뿐이다.
# ★깨진 뒤에는 **손이 비어야 한다** (사장님 지적 2026-08-14)
#   "송판을 들고 있던 사람이 격파가 되고 나면 빈손이어야 한다. 격파된 송판은
#    바닥에 흩어지지만 손에는 없어져야 한다."
TKD_HANDS_EMPTY = (
    "★THE MOMENT A BOARD IS BROKEN, THE HANDS THAT HELD IT ARE EMPTY. Both halves leave "
    "the holder's grip and fly away; nothing is left pinched between his fingers, no "
    "stub, no half board, no fragment. From that instant on, that assistant is standing "
    "there WITH BOTH HANDS EMPTY and open, arms lowering to his sides. The only wood "
    "left anywhere is the broken pieces lying scattered on the mat."
)

TKD_RESET = (
    "4.6-6.6s: THE CLEAR-UP, DONE AT A RUN AND VERY FAST. The assistants - now "
    "empty-handed - sprint in the instant the pieces land and pick up ONLY THE BROKEN "
    "PIECES LYING ON THE MAT, scooping the jagged halves and splinters up at a run and "
    "carrying them off to the side. Nobody walks, everybody jogs or sprints.\n"
    "★NOBODY LEAVES THE SHOT. The same number of people who were there at the break are "
    "still there afterwards - none of them fade out, walk off or disappear.\n"
    "6.6-8s: still at speed, they wheel into a NEW FORMATION - a clean straight line "
    "across the mat, evenly spaced - snap to attention and stand ready with empty hands. "
    "The mat is clean and bare again. It runs on without a pause, one continuous motion."
)

# ★송판만 **리얼 모드**로 (사장님 지시 2026-08-13)
#   "격파용 송판을 **리얼 모드**로 가서 깨지는 것을 극대화한다. **송판만.**"
BOARD = (
    "★THE BREAKING BOARD IS RENDERED REALISTICALLY - IT IS THE ONLY REALISTIC THING IN "
    "THE PICTURE.\n"
    "A taekwondo breaking board of pale pine, held horizontally at about chest height in "
    "the middle of the frame. Unlike everything else, THIS ONE OBJECT is painted with "
    "real wood grain, real thickness, real light and shadow on its edges - a photographic "
    "level of detail on the board alone.\n"
    "MOTION: it hangs still, then SNAPS CLEAN IN TWO across the grain with an explosive "
    "burst - the two halves fly apart and outward, splinters and pale wood dust spraying "
    "in all directions, jagged broken fibres visible along the fracture. Make the break "
    "as big and dramatic as possible. Everything else in the frame stays flat and simple."
)


# (키, 종류, 장면, 동작)  종류: video / still
BGS = [
    # ── 1막 광장 S1–S4 ────────────────────────────────────────────────
    ("plaza_arrive", "video",
     "A broad open city plaza in Seoul on a clear morning, seen wide. A traditional palace "
     "gate with a tiled roof stands across the far side, a green mountain ridge rises beyond "
     "it, and a long low row of fountain jets runs across the middle distance. Paving stones "
     "spread from edge to edge with their perspective lines converging far away, and the sky "
     "opens above the whole width.",
     "0-2s: the plaza is still, the fountain jets barely trickling. 2-5s: the jets rise one "
     "after another all the way along the row, water climbing higher and higher. 5-8s: every "
     "jet is up and they hold, swaying gently. Nothing else moves."),

    ("plaza_gate", "video",
     "The great palace gate seen closer and straight on, its tiled roof and red timber posts "
     "filling the upper frame, stone steps at its base, a pair of stone guardian lions, and "
     "open paving stretching toward the viewer across the whole width. A flock of pigeons is "
     "scattered over the paving, pecking.",
     "0-1.5s: the pigeons peck quietly across the paving. 1.5-2.2s: THEY ALL TAKE OFF AT ONCE, "
     "a burst of wings lifting off the stones and scattering upward and outward across the "
     "frame. 2.2-5s: they climb away and thin out into the sky. 5-8s: the paving is empty and "
     "calm again, a few feathers drifting down. Camera locked."),

    # ── 2막 계단 S5–S7 ────────────────────────────────────────────────
    # ★S5 는 계단에 **걸터앉고** S7 은 **난간을 잡는다**. 그 두 자리가 또렷해야
    #   앵커(step_seat · rail_grip)를 찍을 수 있다.
    # ★동상이 **유럽 왕**으로 나왔다 (사장님 지적 2026-08-14).
    #   "한글 만든 분이 세종대왕인데 동상을 유럽 왕으로 떡하니 만들어서."
    #   "지금 광화문에 있는 동상을 그대로 표현해."
    #   실물 실측(서울시·문화포털) — 좌상, 높이 6.2m·폭 4.3m, 기단 4.2m, 남향.
    #   **왼손에 훈민정음 해례본**(용자례 면), **오른손은 가볍게 들어** 백성에게
    #   훈민정음을 널리 쓰라는 뜻. 두 팔을 벌린 자세, 부드러운 표정 —
    #   '백성과 소통하는 온화한 군주'.
    # ★계단·돌판을 새로 그리게 하면 넓은 돌판 평상이 사라진다(두 번 겪음).
    #   그래서 **원래 그림을 물려주고 동상만 바꾼다** (사장님 지시 2026-08-14
    #   "이전 그림을 보여주고 세종대왕만 바꾸라고 해").
    #   → `flow_make_bg_guided.py steps_seat --guide W1_2/motion_src/guide_steps_seat.png`
    ("steps_seat", "still",
     "Draw a flight of broad stone steps in Gwanghwamun Square, Seoul, seen straight on "
     "at eye level, with the statue from the reference picture standing at the top.\n\n"
     "★★ THE MOST IMPORTANT THING - A BIG FLAT STONE LANDING PARTWAY UP THE STEPS.\n"
     "The flight is not one unbroken run of steps. It goes: a few steps up from the "
     "paving, then THE STEPS STOP and open out into a WIDE FLAT STONE LANDING - a broad "
     "bare terrace that runs right across the middle of the picture, far deeper than any "
     "step, wide enough for several people to stand side by side on it. Then above the "
     "landing the steps start again and carry on up to the pedestal. So it reads "
     "clearly as: STEPS - BIG FLAT LANDING - STEPS. The landing is plain grey stone and "
     "completely empty, with nothing standing on it.\n\n"
     "★THE STATUE ON TOP IS THE ONE IN THE REFERENCE PICTURE - the bronze seated King "
     "Sejong of Gwanghwamun Square. Copy it: seated on a carved throne, wide-sleeved "
     "Korean dragon robe, black winged crown-hat, gentle bearded face, RIGHT hand raised "
     "open, LEFT hand holding an open book on his knee, dark weathered bronze, on a plain "
     "square stone pedestal. Not a European king - no European crown, no ermine, no "
     "sceptre, no orb, no armour, no horse.\n\n"
     "★THE STATUE, EXACTLY: a Korean king SEATED on a low throne on a tall square stone "
     "pedestal, facing straight out towards the viewer. He wears the Joseon dragon robe "
     "with wide sleeves falling in long straight folds and a black winged crown-hat. His "
     "face is gentle and calm - a warm ruler, not a stern one. His arms are OPEN to both "
     "sides: his LEFT hand holds an open book resting on his knee, and his RIGHT hand is "
     "RAISED lightly, palm forward, as if telling the people to go and use the new "
     "letters. The whole figure is dark weathered bronze.\n"
     "★NOT EUROPEAN. No European crown, no ermine, no sceptre, no orb, no ruff, no "
     "baroque throne, no laurel wreath, no armour, no horse, no marble.\n"
     "The steps below him are seen straight on at eye level so the treads read as clear "
     "horizontal lines running right across the picture. They are WIDE and DEEP - the "
     "kind you sit down on.\n"
     "★★ PARTWAY UP THE FLIGHT THE STEPS OPEN OUT INTO A BIG FLAT STONE LANDING - this "
     "is the most important part of the picture and it must be there. About a third of "
     "the way up, the steps STOP and give way to a WIDE BARE STONE TERRACE that runs "
     "right across the middle of the frame, far broader and deeper than any tread - a "
     "flat empty platform you could walk along or sit down on. Above it the steps begin "
     "again and carry on up to the pedestal. So the flight reads as: STEPS - LANDING - "
     "STEPS. The landing is plain and completely empty, with nothing standing on it. "
     "(The character's positions on the stairs are measured from it, so it must not be "
     "left out.)\n"
     "Korean stone balustrades run up both sides, potted pines stand at the foot, and "
     "open paving spreads toward the viewer across the full width.",
     ""),

    ("steps_rail", "still",
     "The upper part of the same stone steps, closer in, with a stone railing running across "
     "the picture at about the height of a standing child's hands - a flat, smooth top rail on "
     "simple square posts, clearly drawn and completely unobstructed so it is obvious you "
     "could grip it and lean out. Beyond and below the rail the plaza drops away into the "
     "distance, the palace gate small and far off. Steps, railing and distant plaza carry "
     "across the whole width.",
     ""),

    # ── 3막 좌판 S8–S12 ───────────────────────────────────────────────
    ("stall_cuke", "video",
     "A small open-air market stall in a plaza - a striped awning, a wooden crate of green "
     "cucumbers tilted toward the viewer, baskets of apples, and a sloping wooden ramp running "
     "down from the crate to the paving. Open paving spreads across the rest of the picture "
     "with the palace gate small in the far distance.",
     "0-1.5s: the stall is still. 1.5-4s: ONE fat green cucumber rolls out of the tilted "
     "crate, down the ramp and out across the paving toward the viewer, turning over and over. "
     "4-8s: it comes to rest and lies there, still. Everything else stays motionless.\n\n"
     + REACH),

    ("stall_milk", "video",
     "The same market stall seen a little closer, with a stack of white milk cartons on the "
     "counter at the right of the crate, the striped awning above, and open paving spreading "
     "across the rest of the picture toward the viewer.",
     "0-4.5s: the stall is still, the cartons stacked neatly. 4.5-5.2s: the TOP MILK CARTON "
     "tips off the stack and falls. 5.2-6.5s: it lands on the paving and slides a short way "
     "toward the viewer. 6.5-8s: it lies still where it stopped. Nothing else moves.\n\n"
     + REACH),

    ("stall_rail", "still",
     "Beside the market stall, a low stone railing runs across the picture at about elbow "
     "height on simple posts, its flat top rail clearly drawn and clear of obstructions so it "
     "is obvious you could lean back against it. The stall and its striped awning sit to one "
     "side, the plaza opens out behind, and the paving spreads across the full width.",
     ""),

    # ── 4막 분수 S13–S14 ──────────────────────────────────────────────
    ("fountain_burst", "video",
     "A round stone fountain basin standing in the open plaza, its carved rim at about waist "
     "height, shallow water inside and a ring of small jets. The palace gate and a line of "
     "trees sit behind it, and the paving spreads out around the basin across the full width "
     "of the picture.",
     "0-1.5s: the basin is calm, the jets barely trickling. 1.5-3.5s: a single tall jet bursts "
     "straight up from the centre, water climbing fast and spreading into a wide crown at the "
     "top. 3.5-6s: the crown falls back as FIVE distinct large droplets that drop one after "
     "another in a slow, clearly readable row, low enough to reach. 6-8s: the water settles to "
     "a calm ripple. Camera locked, only the water moves."),

    # ── 5막 벤치 S15–S18 ──────────────────────────────────────────────
    ("bench_pair", "still",
     "A long wooden park bench stands side-on, seen straight on at eye level so its flat seat "
     "plank reads as one clear horizontal line, LONG ENOUGH FOR TWO to sit side by side and "
     "completely empty. It has a plain slatted backrest and simple legs. A young gingko tree "
     "rises behind it, a low flower bed runs in front, lawn and paving spread away on both "
     "sides, and the palace gate is small in the far distance.",
     ""),

    ("bench_open", "still",
     "The same park corner seen a little wider, with the wooden bench off to one side and a "
     "BROAD STRETCH OF OPEN PAVING running right across the foreground - flat, unobstructed "
     "and level, wide enough for three to stand side by side. Gingko trees, a low flower bed "
     "and a stone railing sit behind, and the plaza and sky carry on across the whole width.",
     ""),

    # ── 6막 산책로 S19–S22 ────────────────────────────────────────────
    ("path_fox", "video",
     "A gingko-lined walking path receding into the distance, golden leaves on the trees and "
     "scattered over the ground. ★The trees line BOTH sides of the path and their canopies "
     "meet overhead, so trees, fallen leaves and the receding path carry on across the whole "
     "width - no bare stretch on one side, no vertical edge where the trees begin. A low leafy "
     "bush sits close to the path near the foreground.",
     "0-2s: the path is still. 2-2.5s: a small red fox pokes its head out of the bush and "
     "looks toward the viewer. 2.5-4.5s: it holds there, watching, ears up. 4.5-5s: it ducks "
     "back into the bush and is gone. 5-6s: the bush shakes once, sharply, then goes still. "
     "6-8s: nothing moves. Camera locked."),

    ("path_leaves", "video",
     "The same gingko path a little further along, the canopies meeting overhead and golden "
     "leaves thick on the ground, trees and path carrying on across the whole width of the "
     "picture.",
     "0-2s: a few leaves drift quietly. 2-3.4s: ONE large golden gingko leaf separates from "
     "the others and floats down slowly through the middle of the picture, turning as it "
     "falls, coming down to about the height a jumping child could reach. 3.4-5s: it drifts "
     "on down and settles on the path. 5-8s: more leaves drift down gently all across the "
     "frame. Camera locked."),

    # ── 7막 해질녘 S23–S26 ────────────────────────────────────────────
    # ★유럽풍 석조 궁전과 서양식 분수가 나왔다 (사장님 지적 2026-08-14).
    #   'the plaza' 라고만 써서 Flow 가 유럽 광장을 그렸다 — 광화문광장이라고 못박는다.
    # ★노을이 주인공이다 (사장님 지시 2026-08-14)
    #   "등보다 노을이 강조되어야지. 광화문과 광장은 적어도 되지만 하늘의 노을과
    #    구름이 엄청 멋지게 표현되게. 등은 밤을 상징하니 두 줄로 길이로 죽 작게
    #    켜지면서 다 보이게. 멀리 하늘의 노을이 주인공이 되게."
    ("dusk_lanterns", "video",
     "★THE SUNSET SKY IS THE SUBJECT OF THIS PICTURE. It fills the UPPER TWO THIRDS of "
     "the frame - a huge, breathtaking evening sky over Seoul. Long bands of cloud "
     "stretch right across it, lit from below in deep crimson, orange, gold and rose, "
     "shading up into violet and deep blue at the top. The clouds are big and dramatic, "
     "with light pouring between them and the last of the sun glowing low behind the "
     "mountains. Make this sky as beautiful as you can - it is what the shot is for.\n"
     "★THE GROUND IS SMALL AND LOW. Along the bottom third, in near silhouette against "
     "that blazing sky, sits GWANGHWAMUN SQUARE in Seoul: a traditional Korean palace "
     "gate with a deep tiled roof, low Korean tiled roofs and a stone wall to either "
     "side, and a dark mountain ridge behind. Keep it modest and simple - it must not "
     "compete with the sky. NO European stone palaces, no baroque facades, no arcades.\n"
     "★TWO LONG ROWS OF SMALL LANTERNS run away from the camera down both sides of the "
     "paving, one row on the left and one on the right, going far into the distance and "
     "getting smaller as they recede - every lantern in both rows is visible. They are "
     "small and modest, not tall posts. Wide empty paving lies between the two rows.",
     "0-2s: the sunset burns quietly, the clouds drifting very slowly, every lantern "
     "still dark. 2-5.5s: THE LANTERNS LIGHT UP ONE AFTER ANOTHER, starting at the far "
     "end of both rows and running towards the camera, each one a small warm point of "
     "light, until at 5.5s the nearest pair lights and both full rows are glowing. "
     "5.5-8s: the whole avenue of little lights holds steady while the clouds keep "
     "drifting and the colours deepen. Camera locked - the sky never leaves the frame."),

    ("dusk_calm", "video",
     "The same GWANGHWAMUN SQUARE later, the sky deepening from amber into blue-violet, "
     "the Korean tiled palace gate and the mountain ridge in soft silhouette, the Korean "
     "lanterns glowing warmly along their row, the paving stretching away empty across "
     "the full width.\n"
     "★THE PLACE IS KOREAN - no European palaces, arcades or fountains anywhere.",
     "0-3s: the sky slowly deepens, the lantern glow strengthening against it. 3-6s: the first "
     "stars come out one by one, high across the sky. 6-8s: everything holds, calm and still, "
     "the lanterns steady. Camera locked, nothing else moves."),

    # ══ 광화문광장 퍼포먼스 배경 4종 (사장님 지시 2026-08-13) ═══════════
    #   실제로 그 광장에서 하는 것만 골랐다(조사 2026-08-13).
    #   관중은 전부 **실루엣**, 송판만 **리얼**.

    # ★터널분수 — 터널이 **안쪽으로 뻗어야** 한다.
    #   전에는 물 아치가 화면을 좌우로 가로질러, 캐릭터가 통과할 길이 없었다.
    #   아치를 여러 겹 겹쳐 카메라 발치에서 저 멀리까지 이어 놓으면 그 자체가
    #   원근의 눈금이 되고, 그 속을 달려 나올 수 있다(수문장 마당과 같은 짜임).
    #   ※바닥은 턱 없이 전폭으로 이어 두고, 가운데 통로를 비운다.
    ("perf_tunnel", "video",                                  # ① 터널분수
     "KEEP THE PLACE IN THE SOURCE IMAGE: the same Korean palace square, the same "
     "traditional tiled gate standing at the far end, the same green mountain ridge "
     "behind it, the same pale stone paving and the same soft daylight. Do not put "
     "European stone buildings, arcades or balconies anywhere - the buildings that show "
     "at the sides are low Korean tiled roofs and trees, exactly as in the source.\n\n"
     "ADD ONE THING: a long TUNNEL OF WATER running straight AWAY FROM THE CAMERA down "
     "the centre of the square, ending at the distant gate.\n"
     "★HOW ONE JET GOES - THIS IS THE WHOLE POINT: there is a line of nozzles along the "
     "LEFT edge of the walkway and another line along the RIGHT edge. A jet leaves a "
     "LEFT nozzle, rises steeply, sweeps in one long unbroken curve high over the heads "
     "of the people in the middle, CARRIES ON RIGHT OVER THE TOP OF THE NOZZLE LINE ON "
     "THE RIGHT, and only comes down and lands on the paving BEYOND it, OUTSIDE the "
     "tunnel on the far right. It overshoots the opposite nozzles - it does not land on "
     "them and does not stop short of them. Every jet from the right does the mirror "
     "image, overshooting the left nozzles and landing outside on the far left. So the "
     "two streams cross high overhead and each one throws itself clean over to the other "
     "side of the picture.\n"
     "★NO JET EVER FALLS BACK ON ITS OWN SIDE. Nothing rises and drops beside the nozzle "
     "it came from - that would look like separate fountains standing in a row instead "
     "of one tunnel.\n"
     "★NO WATER TOUCHES THE MIDDLE. There are no nozzles in the centre of the walkway - "
     "the paving down the middle is bare, dry and clear, with no jet rising from it and "
     "no water splashing down onto it. The water lands only OUTSIDE both nozzle lines, "
     "and only there do rings and splashes appear.\n"
     "★MANY ARCHES, ONE BEHIND ANOTHER: at least a dozen of these crossing curves stand "
     "in a row going back into the distance. The nearest is huge and fills the top of "
     "the frame; each one behind is smaller and closer to the next, so it reads as a "
     "deep corridor of water with a small bright opening far away. Each curve is made of "
     "many FINE THREADLIKE JETS side by side, not a few thick ropes of water.\n"
     "★PEOPLE WALK THROUGH THE MIDDLE - small dark silhouettes strolling down the dry "
     "centre, some near and large, some far and tiny, showing how big the tunnel is.\n\n"
     + CROWD,
     "THE TUNNEL IS ALREADY COMPLETE IN THE VERY FIRST FRAME - every arch is standing "
     "at full height from frame one, nothing rises into place after the clip starts. "
     "The water never stops. "
     "0-8s: every arch stands complete and unbroken for the whole eight seconds - the "
     "jets never switch off, never sag, never drop out one by one, and the tunnel is "
     "never empty at any moment. The water arcs over steadily, spray drifting through "
     "the light, small rings spreading where it lands in the side channels, while the "
     "silhouetted people stroll through the middle of the tunnel. The last frame looks "
     "just like the first. Camera locked - it never moves down the tunnel, never pans, "
     "never zooms."),

    # ★한글분수 — **글자는 Flow 가 그리지 않는다.**
    #   물줄기로 ㄱㄴㄷ 모양을 흉내 내게 시켰더니 될 리가 없다(LOCK 에 글자 금지가
    #   박혀 있고, Flow 는 한글을 못 쓴다). 배경은 **물이 솟는 분수 마당**까지만 맡고,
    #   자모는 획순 엔진(`hangeul_write.py`)이 물빛 획으로 그려 얹는다.
    #   사장님 말씀 "여기는 애니메이션이니까 현실보다 더 정확하게 크게 과장해서
    #   표현할 수도 있겠다" — 그 과장은 우리 획이 한다.
    #   그래서 **화면 가운데를 비워 둔다** — 거기에 자모가 솟는다.
    #   ※왼편을 비우거나 세로로 가르지 않는다. 캐릭터가 좌우를 다 쓴다.
    ("perf_hangeul_fountain", "video",                        # ② 한글분수
     "A wide flat plaza floor of pale stone on a bright day, the ground filling most of "
     "the frame and running unbroken from edge to edge with no step, kerb or wall across "
     "it. Set flush into the paving is a large FLOOR FOUNTAIN - rows of small nozzles "
     "level with the stone, no basin and no rim, so the plaza stays walkable everywhere. "
     "The jets stand along the LEFT and RIGHT thirds of the picture and the MIDDLE OF "
     "THE FRAME IS LEFT CLEAR AND OPEN. Behind the plaza the ground carries on to a "
     "distant tiled palace gate and a green ridge under a clear sky. The stone is wet "
     "and glossy, with shallow reflections.\n\n" + CROWD,
     "0-1.5s: the floor is still and wet, the nozzles quiet, only faint ripples on the "
     "stone. 1.5-5s: THE WATER COMES UP HARD - tall clean columns leap from the nozzles "
     "on both sides, far higher than the watching figures, rising and swaying, throwing "
     "spray and catching the light. 5-6.5s: the columns fall back and burst into a low "
     "rolling mist that spreads across the wet stone. 6.5-8s: the water settles and the "
     "floor lies still and shining again. Camera locked - no pan, no zoom, no tilt."),

    # ★한글분수 네온 — 자모를 **네온으로 밝게** 세우기 위한 무대 두 벌.
    #   실제 광화문 한글분수는 물줄기가 글자 모양을 만드는 게 아니라, 바닥에 박힌
    #   노즐 225개가 천(○)·지(□)·인(△) 모양으로 배치돼 **노즐 배열 자체가 한글 28자**다.
    #   그래서 무대에는 그 ○□△ 노즐 자국만 깔고, 자모는 획순 엔진이 그 위에 긋는다.
    #   ※Flow 에 글자를 시키지 않는다(LOCK 에 글자 금지, 한글도 못 쓴다).
    #   ※가운데를 비워 둔다 — 거기에 네온 자모가 선다. 왼편만 비우지는 않는다.
    ("perf_hangeul_neon_a", "video",                          # ②-A 네온 · 물기둥이 선다
     "The same wide stone plaza AT NIGHT, the ground filling most of the frame and "
     "running unbroken from edge to edge with no step, kerb or wall. Set flush into the "
     "wet paving are rings of small nozzles laid out as plain GEOMETRIC MARKS - circles, "
     "squares and triangles - glowing softly from beneath like cool blue-white light "
     "lines in the stone. They are simple shapes only, never letters or symbols. The "
     "marks lie flat on the ground and get smaller and closer together towards the back, "
     "so the depth of the plaza reads clearly. Behind, the plaza carries on to a distant "
     "tiled palace gate lit warm against a deep night sky. The wet stone mirrors every "
     "light.\n\n" + CROWD,
     "0-1.5s: night, still water, the geometric floor marks pulsing faintly. "
     "1.5-4.5s: BRILLIANT NEON WATER LEAPS UP from the marks on the LEFT and RIGHT "
     "thirds - tall columns of glowing blue-white and pink light water, far taller than "
     "the watching figures, lighting the whole plaza and throwing coloured reflections "
     "across the wet stone. The MIDDLE OF THE FRAME STAYS OPEN. "
     "4.5-6.5s: the columns hold and sway, spray glittering in the light. "
     "6.5-8s: they sink back and the floor marks glow on alone. Camera locked."),

    ("perf_hangeul_neon_b", "video",                          # ②-B 네온 · 물이 무너져 비친다
     "The same wide stone plaza AT NIGHT seen a little lower, so the WET STONE FLOOR "
     "fills the lower two thirds of the frame like a black mirror, reflecting the lights "
     "above. Flush in the paving are the same plain glowing GEOMETRIC MARKS - circles, "
     "squares, triangles - never letters or symbols, shrinking towards the back so the "
     "depth reads clearly. Low neon mist drifts across the stone. Behind, a distant "
     "tiled palace gate glows warm against a deep night sky. The ground runs unbroken "
     "from edge to edge with nothing to step over.\n\n" + CROWD,
     "0-2s: low glowing mist rolls slowly across the mirror-wet floor, the marks "
     "pulsing. 2-5s: SHEETS OF NEON WATER FALL from above at the left and right sides, "
     "splashing wide and sending bright ripples racing outward across the whole floor, "
     "the reflections breaking and re-forming. The MIDDLE OF THE FRAME STAYS OPEN. "
     "5-8s: the ripples settle, the mist thickens and glows, the floor becomes a still "
     "bright mirror again. Camera locked."),

    # ★태권도 최고 난이도 격파 3종 (사장님 지시 2026-08-14)
    #   실제 국기원 시범단 광화문 상설 시범을 보고 골랐다 — 매트를 깔고 관객이 둘러선다.
    #   "보조사람들과 격파하는 선수까지 모두 **해부학적 인체를 가진 실루엣**으로 한다.
    #    격파되는 송판과 흩어지는 파편과 그 소리만 리얼하게."
    #   ※사람은 전원 실루엣이라 CROWD 를 쓰되, **선수·보조자는 가운데서 움직인다**는
    #     점이 다르다. 그래서 CROWD 뒤에 움직이는 실루엣 규격을 따로 덧붙인다.
    ("perf_tkd_jump_side", "video",                           # ③-1 뛰어 옆차기 3단 격파
     "A taekwondo demonstration ground in front of a Korean palace gate on a clear day: a "
     "large flat MAT of blue and red laid on the paving, the tiled gate and a green ridge "
     "behind, a ring of watching people around the edges.\n"
     + TKD_FIGURES +
     "\nTHE PERFORMANCE - A FLYING SIDE KICK OVER TWO ASSISTANTS:\n"
     "Two assistant silhouettes crouch side by side in the middle of the mat. A third "
     "assistant stands beyond them holding a board up HIGH above head height.\n"
     "THE MECHANICS, BEAT BY BEAT - follow them exactly:\n"
     "0-1.0s: the kicker stands far back on the mat, still, then takes three quick "
     "running steps in, getting faster.\n"
     "1.0-1.6s: on the last step he PLANTS his left foot hard on the mat just in front of "
     "the crouching assistants and drives his right knee up sharply - that knee drive is "
     "what lifts him.\n"
     "1.6-2.2s: he rises off that one planted foot, brushes the crouching assistants' "
     "shoulders with the ball of his right foot, and keeps climbing. As he climbs his "
     "body TURNS SIDE-ON so his hip leads the way, his left knee folds tight to his "
     "chest, and his right arm stays down across his body for balance.\n"
     "2.2-2.5s: at the top of the arc, level with the board, the folded LEFT leg SNAPS "
     "OUT STRAIGHT along the line of his body - a side kick, the blade of the foot "
     "leading, the whole leg in one straight line from hip to heel.\n"
     "2.5-2.7s: THE BREAK - the foot arrives and the board snaps in the same instant.\n"
     "2.7-3.4s: the foot follows through past where the board was, the leg still "
     "straight, and he starts to drop.\n"
     "3.4-4.6s: he lands on the far side of the mat, right foot down first then left, "
     "knees bending deep to absorb it, one hand touching the mat, then he stands.\n"
     + TKD_BREAK_HARD + "\n" + TKD_HANDS_EMPTY + "\n"
     + TKD_RESET + "\n\n"
     + BOARD + "\n\n" + CROWD,
     "One continuous shot, camera locked - no pan, no zoom, no cut. The whole run-up, "
     "flight, break and landing happen inside the frame."),

    ("perf_tkd_540", "video",                                 # ③-2 540도 뒤후려차기
     "A taekwondo demonstration ground in front of a Korean palace gate on a clear day: a "
     "large flat MAT of blue and red laid on the paving, the tiled gate and a green ridge "
     "behind, a ring of watching people around the edges.\n"
     + TKD_FIGURES +
     "\nTHE PERFORMANCE - A 540 DEGREE SPINNING HOOK KICK:\n"
     "One assistant silhouette stands to the side holding a board up at head height, arm "
     "straight out.\n"
     "0-1.2s: the kicker silhouette stands facing the board, gathering himself.\n"
     "1.2-2.6s: he winds up and JUMPS, spinning in the air - one and a half full turns, "
     "the body horizontal at the peak, one leg sweeping round in a long hooking arc.\n"
     "2.6-3.2s: THE BREAK, struck by the heel at the end of the sweep.\n"
     "3.2-4.6s: he completes the rotation and lands facing the other way, one knee down, "
     "the broken halves spinning away, then rises.\n"
     + TKD_RESET + "\n\n"
     + BOARD + "\n\n" + CROWD,
     "One continuous shot, camera locked - no pan, no zoom, no cut. The spin reads "
     "clearly as one and a half turns, never a blur."),

    ("perf_tkd_multi", "video",                               # ③-3 사방 연속 격파
     "A taekwondo demonstration ground in front of a Korean palace gate on a clear day: a "
     "large flat MAT of blue and red laid on the paving, the tiled gate and a green ridge "
     "behind, a ring of watching people around the edges.\n"
     + TKD_FIGURES +
     "\nTHE PERFORMANCE - FOUR BOARDS BROKEN IN ONE JUMP:\n"
     "Four assistant silhouettes stand spaced around the middle of the mat - left, right, "
     "front and back - each holding a board out at head height, so the boards face in four "
     "different directions.\n"
     "0-1s: the kicker silhouette stands still in the centre of the ring of boards.\n"
     "1-1.6s: he leaps straight up, high.\n"
     "1.6-3.6s: STILL IN THE AIR, he turns and kicks each board in turn - one, two, three, "
     "four - each kick snapping out to a different side, his body rotating between them. "
     "HIS FEET NEVER TOUCH THE GROUND UNTIL ALL FOUR ARE BROKEN.\n"
     "3.6-4.6s: he drops and lands square on both feet in the centre, wood raining down "
     "around him.\n"
     "★THIS IS THE LAST SET, SO IT ENDS WITH THE CLOSING BOW - not with another reset.\n"
     "4.6-6.4s: THE CLEAR-UP, DONE AT A RUN. All the assistant silhouettes sprint in, "
     "sweep up every piece of broken wood with quick low scoops and carry it off the mat "
     "at a jog. Nobody walks. The mat is left clean and bare.\n"
     "6.4-8s: they run back and fall into ONE STRAIGHT LINE beside the kicker, shoulder "
     "to shoulder facing the crowd, snap to attention, and ALL BOW TOGETHER from the "
     "waist in one sharp movement, then straighten up.\n\n"
     + BOARD + "\n\n" + CROWD,
     "One continuous shot, camera locked - no pan, no zoom, no cut. All four breaks are "
     "visible inside the frame."),

    # ★2·3세트는 **Last Image Transition** 으로 잇는다 (사장님 지시 2026-08-14
    #   "연결해서 잘 하려면 키프레임 써야 하고 라스트신 연결을 사용해야 한다").
    #   앞 컷의 **마지막 프레임**을 기준 그림으로 물리고, 프롬프트는 장면을 다시
    #   묘사하지 않는다 — **이어받는 동작만** 말한다. 장면을 다시 그리면 매트 색·
    #   사람 수·문 위치가 달라져 이음매가 튄다.
    ("perf_tkd_540_chain", "video",                           # ③-2 (이어받기)
     "CONTINUE EXACTLY FROM THE SOURCE IMAGE. Same mat, same gate, same ridge, same "
     "watching crowd, same silhouette people standing in the line they finished in - do "
     "not redraw the place, do not move the camera, do not change the colours.\n"
     + TKD_FIGURES,
     "The line breaks and they run to their places for the second set. "
     "0-0.8s: one assistant sprints out to the right and holds a board up at HEAD HEIGHT, "
     "arm straight out, board facing left; the kicker jogs out to face him a few paces "
     "away. "
     "★THE 540 HOOK KICK, BEAT BY BEAT - this is a specific technique, follow it exactly. "
     "0.8-1.3s: he takes two quick steps in towards the board and PLANTS his left foot, "
     "already starting to turn his back on the target, arms winding across his body. "
     "1.3-1.6s: he SWINGS HIS RIGHT LEG UP HARD AND FORWARD, knee driving high - that leg "
     "swing is what throws him into the air. He leaves the ground OFF THE SINGLE PLANTED "
     "LEFT FOOT, not off both feet. "
     "1.6-2.2s: airborne and rising, he turns a full circle with his back to the target "
     "at the halfway point, the swung right leg still folded high, body leaning back, "
     "shoulders whipping round ahead of the hips. "
     "2.2-2.6s: as the turn comes back round, the LEFT leg - the one he took off from - "
     "whips out and round in a long HOOK, the heel leading, sweeping horizontally at head "
     "height. That heel is the striking surface. "
     "2.6-2.8s: THE BOARD SNAPS CLEAN IN TWO the instant the heel arrives, halves and "
     "splinters flying outward. "
     "2.8-3.4s: the heel carries on through and the turn completes - one and a half turns "
     "in all. "
     "3.4-4.6s: HE LANDS ON THE KICKING LEG FIRST, that foot taking the weight, the other "
     "foot following down, knees bending to absorb it, facing away from where he started. "
     "Then he rises to a stance. "
     + TKD_BREAK_HARD.replace("\n", " ") + " " + TKD_HANDS_EMPTY.replace("\n", " ") + " "
     # ★이 세트가 끝나는 **배치**가 다음 세트의 시작 그림이 된다 (사장님 2026-08-14).
     #   3세트에서 배치를 바꾸려 들면 안 된다 — 이어받기는 앞 그림을 **유지**하는
     #   기술이라 정반대로 쓴 셈이었다. 바꾸고 싶은 것은 **앞 클립의 끝에서** 만든다.
     "4.6-6.2s: THE CLEAR-UP AT A RUN. Everyone sprints in, scoops the broken wood off "
     "the mat and carries it away at a jog. Nobody walks. "
     "6.2-8s: ★NOW THE MAT EMPTIES OUT. All but FIVE people run right off the mat and "
     "join the watching crowd at the far edges. The five who stay take up the setting "
     "for the next break, and they are: FOUR board holders standing at the four sides "
     "of the mat - one near the front, one on the right, one at the back, one on the "
     "left - spread wide apart in a ring, EACH HOLDING ONE FRESH BOARD UP ABOVE HIS OWN "
     "HEAD in both hands with the flat face turned inwards; and ONE kicker standing "
     "alone in the middle of that ring, BOTH HANDS EMPTY at his sides, feet set, ready. "
     "The last frame of the clip shows exactly those five on an otherwise bare mat - "
     "four raised boards around the edge of a ring and one empty-handed man in the "
     "centre of it. Nobody else is standing on the mat. "
     " Camera locked - no pan, no zoom, no cut."),

    # ★3세트는 한 번 **흰 도복에 검은 띠**로 그려져 나왔다(2026-08-14). 마지막 프레임을
    #   물리면 Flow 가 실루엣 규격을 놓친다 — 그래서 맨 앞에 다시 못박는다.
    ("perf_tkd_multi_chain", "video",                         # ③-3 (이어받기 · 마무리 인사)
     "★★ EVERY PERSON STAYS A FLAT DARK SILHOUETTE, EXACTLY AS IN THE SOURCE IMAGE. "
     "Nobody turns into a drawn person. NO WHITE UNIFORMS, no black belts, no faces, no "
     "hair, no folds, no outlines, no shading - each body is one solid dark grey-blue "
     "filled shape and nothing more. If a figure would show a white dobok, draw it as "
     "the same dark silhouette instead. This applies to the kicker and every assistant, "
     "in every single frame including the very last one.\n"
     "★★ THE DANGEROUS MOMENT IS WHEN THEY LINE UP. A row of taekwondo people standing "
     "to attention is exactly where white doboks and black belts creep back in - they "
     "must NOT. When they are standing in line at the start, and again when they line up "
     "to bow at the end, they are still the SAME FLAT DARK SHAPES as when they are "
     "kicking. A dark row against the mat, with only their posture readable. Do not draw "
     "a single white uniform anywhere in this shot.\n\n"
     "CONTINUE EXACTLY FROM THE SOURCE IMAGE. Same mat, same gate, same ridge, same "
     "watching crowd, same silhouette people standing in the line they finished in - do "
     "not redraw the place, do not move the camera, do not change the colours.\n"
     + TKD_FIGURES,
     # ★배치는 **앞 클립 끝에서 이미 만들어져 있다.** 여기서 바꾸려 들지 않는다 —
     #   이어받기는 앞 그림을 유지하는 기술이라, 바꾸라고 시키면 넷 다 실패한다.
     "★THEY ARE ALREADY IN POSITION IN THE SOURCE IMAGE - five people on the mat, four "
     "of them holding a board up above their heads and one standing empty-handed in the "
     "middle of them. KEEP EXACTLY THOSE FIVE AND KEEP THEM WHERE THEY ARE. Nobody runs "
     "on, nobody runs off, nobody new appears, and the four holders do not move from "
     "their spots - they stand steady, boards held high, until their own board is "
     "struck. The clip opens straight into the technique, not into people getting ready. "
     "0-0.8s: the kicker settles his feet and dips into a crouch. "
     "★FOUR BREAKS IN ONE JUMP, BEAT BY BEAT - keep the order and the footwork exact. "
     "0.8-1.1s: he dips into a crouch, both knees bending, arms swinging back. "
     "1.1-1.4s: he explodes STRAIGHT UP off both feet, rising higher than the assistants' "
     "heads, and immediately tucks both knees up under him. "
     "1.4-1.8s: BREAK 1 - FRONT. His RIGHT knee lifts to his chest and the leg snaps "
     "straight forward, ball of the foot into the board in front. It breaks and the leg "
     "re-folds at once. "
     "1.8-2.3s: BREAK 2 - RIGHT. He twists his hips a quarter turn to the right in the "
     "air and the same RIGHT leg snaps out sideways, blade of the foot into the board on "
     "the right. It breaks and the leg re-folds. "
     "2.3-2.8s: BREAK 3 - BEHIND. He keeps turning, now looking back over his shoulder, "
     "and drives his LEFT heel straight back into the board behind him. It breaks. "
     "2.8-3.4s: BREAK 4 - LEFT. He completes the turn and the LEFT leg whips round in a "
     "hook, heel first, into the last board on the left. It breaks. "
     "★HIS FEET NEVER TOUCH THE GROUND FROM THE TAKE-OFF UNTIL ALL FOUR ARE BROKEN - it "
     "is one single jump, he does not land and jump again between boards. Between each "
     "kick the leg folds back in tight; he never leaves a leg hanging out straight. "
     "★★ ALL FOUR BREAKS HAPPEN IN ONE SINGLE JUMP. He leaves the ground ONCE and comes "
     "down ONCE. He does NOT kick one board, land, walk to the next and kick again - that "
     "is wrong and must not happen. From take-off to landing is one unbroken flight of "
     "about two and a half seconds, and all four boards are struck inside it, one after "
     "another, while he hangs in the air turning. His body stays UP at head height the "
     "whole way through the four kicks; he does not sink towards the mat between them. "
     "★KEEP THE FOUR HOLDERS CLEARLY VISIBLE. Everyone else stays WELL BACK at the far "
     "edges, so the ground holds only the kicker and his four board holders, each one "
     "plainly separate. Nobody crowds in, nobody stands in front of a holder. "
     + TKD_HANDS_EMPTY.replace("\n", " ") + " ALL FOUR HOLDERS END UP EMPTY-HANDED - "
     "after his own board is struck each one lowers both open, empty hands to his sides. "
     "3.4-4.6s: he drops and lands square on both feet in the centre, knees bending deep, "
     "wood raining down all around him, the four holders standing empty-handed around "
     "him. "
     "4.6-6.4s: THE CLEAR-UP AT A RUN - every assistant sprints in, sweeps up the broken "
     "wood with quick low scoops and carries it off the mat at a jog. Nobody walks. The "
     "mat is left clean and bare. "
     "6.4-8s: they run back and fall into ONE STRAIGHT LINE beside the kicker, shoulder "
     "to shoulder facing the crowd, snap to attention, and ALL BOW TOGETHER from the "
     "waist in one sharp movement, then straighten up. ★EVERY ONE OF THEM IS "
     "EMPTY-HANDED IN THAT LINE - not a single board, half board or splinter is left in "
     "anybody's hands, arms hanging straight at their sides as they bow. "
     "Camera locked - no pan, no zoom, no cut."),

    # ★사방 격파의 **배치 기준 그림** (사장님 지시 2026-08-14).
    #   3세트를 앞 클립의 마지막 프레임에서 이어받게 했더니, 그 그림에 사람들이 좌우
    #   일렬로 서 있어 Flow 가 그 배치를 계속 유지했다 — "사방으로 서라"는 글보다
    #   그림을 따른다. 그래서 **사방 배치를 그린 정지 그림을 따로 뽑아** 시작 프레임으로
    #   삼는다. 매트·문·산은 앞 클립 것을 물려주므로 이음매는 안 튄다.
    ("perf_tkd_quad_setup", "still",                          # ③-3 배치 기준 그림
     "KEEP THE PLACE EXACTLY AS IN THE SOURCE IMAGE - same blue and red mat, same Korean "
     "tiled gate, same green ridge, same watching crowd around the edges, same colours "
     "and light. Only the people ON the mat are arranged differently.\n\n"
     "★THE CAMERA IS HIGH UP AND TILTED DOWN, looking at the mat from ABOVE AND TO ONE "
     "SIDE, as if from a balcony - a three-quarter bird's eye view. You can see the flat "
     "surface of the mat spread out below like a table top, and you can see the ground "
     "all the way around the person in the middle. It is NOT a straight-on eye-level "
     "view from the side of the mat.\n"
     "★THE SOURCE IMAGE ALREADY HAS EXACTLY FIVE PEOPLE ON THE MAT. Keep those same "
     "five and only move them into position - DO NOT ADD ANYONE. Nobody walks on from "
     "the sides, nobody appears in the background of the mat. Five in, five out.\n"
     "★COUNT THE PEOPLE ON THE MAT: THERE ARE FIVE. Exactly five, no more, no fewer. "
     "Do not add a sixth. They are:\n"
     "  · ONE kicker, alone in the very centre of the mat, standing at ease with BOTH "
     "HANDS EMPTY and open at his sides - he holds nothing at all\n"
     "  · FOUR board holders, one at each of the four sides around him, spaced far "
     "apart: one BELOW him in the picture (between him and the camera), one to his "
     "RIGHT, one ABOVE him in the picture (further from the camera), one to his LEFT\n"
     "Because the camera looks down, all four are separate and none is hidden behind the "
     "kicker. The four of them plus the kicker make a shape like a cross or a diamond on "
     "the mat, with wide empty mat showing in the four gaps between them.\n"
     "★EACH HOLDER HOLDS ONE BOARD UP HIGH - both arms raised so the board is ABOVE HIS "
     "OWN HEAD, the flat face turned inwards towards the kicker. Four people, four "
     "boards, one each.\n"
     "★THE REST OF THE TEAM HAS LEFT THE MAT COMPLETELY and is standing off at the far "
     "edges among the watching crowd. Apart from those five, the mat is bare.\n\n"
     + TKD_FIGURES + "\n\n" + BOARD + "\n\n" + CROWD,
     ""),

    ("perf_taekwondo_board", "video",                         # ③ 태권도 격파
     "A broad city plaza on a clear afternoon, seen wide. The open paving spreads from "
     "edge to edge with a distant tiled palace gate and a green ridge beyond. The middle "
     "of the picture is left open and clear.\n\n" + BOARD + "\n\n" + CROWD,
     "0-3s: everything is still - the board hangs steady in the middle of the frame, the "
     "silhouettes watching. 3-4.5s: THE BREAK. The board snaps clean in two and the "
     "halves burst apart with splinters and wood dust flying outward. 4.5-6.5s: the "
     "pieces tumble down and out of the frame, dust drifting. 6.5-8s: empty open plaza, "
     "settled and still. Camera locked."),

    # ★수문장이 저 문 앞에서 걸어 나와 카메라 앞까지 오고, 돌아서서 다시 문 쪽으로
    #   멀어졌다가 되돌아온다. 그러려면 배경에 **깊이**가 있어야 한다 —
    #   문은 중경에 두고, 돌바닥 참배로가 카메라 발치까지 길게 밀려 나오게 잡는다.
    #   깃대 줄이 좌우에서 문 쪽으로 좁아지며 원근의 눈금 노릇을 한다.
    #   ※왼편을 비우거나 세로로 가르지 않는다 — 캐릭터가 좌우를 다 쓴다.
    ("perf_guard_gate", "video",                              # ④ 수문장 교대의식
     "A long stone-paved processional approach seen straight down its length, running "
     "from right under the camera far back to a large traditional palace gate that "
     "stands in the MIDDLE DISTANCE, its deep tiled roof and red-painted timber clearly "
     "visible but small. The paving slabs are large in the foreground and shrink "
     "steadily towards the gate, their joint lines converging - the perspective must be "
     "unmistakable and even, with no step, wall, kerb or edge anywhere across the "
     "walkway. Tall flagpoles with plain coloured banners stand in two rows down the "
     "left and right sides, each pole shorter than the one before as they recede, and "
     "low stone lanterns line the paving outside them. Clear daylight, a green ridge "
     "showing above the roof.\n\n" + CROWD,
     "0-3s: the banners lift and ripple slowly in the breeze, everything else still. "
     "3-5.5s: the great gate doors swing slowly open in the middle distance. "
     "5.5-8s: the doors stand open, the banners still rippling, everything else holding. "
     "Camera locked - it never pans, zooms, tilts or moves down the walkway."),
]

BY = {k: (kind, scene, motion) for k, kind, scene, motion in BGS}


def prompt(key):
    kind, scene, motion = BY[key]
    if kind == "video":
        return "%s\n\n%s\n\nMOTION (fill all 8 seconds): %s" % (STYLE, scene, motion)
    return "%s\n\n%s" % (STYLE, scene)


if __name__ == "__main__":
    for k, kind, _, _ in BGS:
        print("%-24s %-6s %5d자" % (k, kind, len(prompt(k))))
