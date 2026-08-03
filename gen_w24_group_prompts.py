# -*- coding: utf-8 -*-
"""W24 그룹 동작 영상 프롬프트 11종 생성 (2026-08-03).

`W24_motion.md` 의 **캐릭터 개별 트랙**이 그대로 프롬프트 본문이 된다.
각자 무엇을 하는지 다 적혀 있어야 영상 안에서 따로 놀지 않는다.

★컷아웃을 전제로 한 촬영 규격 (이게 안 지켜지면 투명컷이 깨진다):
  - 배경은 **민무늬 밝은 회색**. 배경에 아무것도 없어야 인물만 오려낼 수 있다.
  - **카메라 완전 고정.** 줌·팬·돌리 금지. 카메라가 움직이면 64컷이 서로 안 맞는다.
  - 인물은 **제자리에서만** 움직인다. 걸어서 이동하지 않는다(걷기는 기존 자산을 쓴다).
  - **발끝까지 전신**이 프레임 안에. 잘리면 키 통일이 불가능하다.
  - 8초 = 24fps × 192프레임 → 3장 중 1장 = **64컷**

사용:
  python gen_w24_group_prompts.py          # W24/prompts/*.txt 11개
  python gen_w24_group_prompts.py --list
"""
import argparse
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
OUT_DIR = "W24/prompts"

# ── 캐릭터 묘사 — ★clip5_prompt.txt / Flow 등록 설명과 문구를 맞춘다(일관성) ──
DESC = {
    "zollaman": "@zollaman - a HAND-DRAWN BLACK INK STICK FIGURE with thin ink limbs and no clothes, "
                "his head filled SOLID BLACK like a bowl cut.",
    "zollagirl": "@zollagirl - a HAND-DRAWN BLACK INK STICK FIGURE with thin ink limbs and no clothes, "
                 "her head an open white circle with BRIGHT ORANGE hair tied in a bun.",
    "stickman": "@stickman - the plainest BLACK LINE STICK FIGURE drawn in thick smooth ink strokes: "
                "an empty white circle head with two dot eyes, a straight line body, thin line arms and "
                "legs, no hair, no hands, no feet, no clothes. He is a PERSON, never an object and "
                "NEVER A PEN OR MARKER. His ink lines glow softly cyan.",
    "injun": "@injun - a coloured cartoon young man, tall and slim, short black hair, navy blue "
             "t-shirt, beige trousers, white sneakers.",
    "jieun": "@jieun - a coloured cartoon young woman, long wavy light brown hair, pale yellow "
             "floral dress.",
    "madamjay": "@madamjay - a coloured cartoon woman who looks about forty, smooth youthful face, "
                "rosy cheeks, glossy dark brown hair in a neat bun, vivid coral sleeveless vest over "
                "a white blouse, white knee-length skirt.",
    "teacherjay": "@teacherjay - a coloured cartoon man, bald head with a single curl of hair, blue "
                  "and white checked shirt with rolled sleeves, beige trousers, white sneakers.",
}

HEIGHT_A = ("HEIGHT ORDER (keep exact): @zollaman is the tallest, @stickman is a little shorter, "
            "@zollagirl is the shortest.")
HEIGHT_B = "HEIGHT ORDER (keep exact): @injun is clearly taller than @jieun."
HEIGHT_C = "HEIGHT ORDER (keep exact): @teacherjay is clearly taller than @madamjay."

STYLE_A = ("All three are simple hand-drawn black ink line figures - never coloured people. "
           "Flat 2D cartoon illustration, bold clean black outlines.")
STYLE_HUMAN = ("Flat 2D cartoon illustration, bold clean black outlines, flat colours, no gradients.")

# ★공통 꼬리표 — 컷아웃 전제 촬영 규격
TAIL = """
SET: a completely EMPTY seamless studio backdrop of plain light grey (#e8e8e8). Nothing else at all -
no floor line, no furniture, no scenery, no props, no shadows cast on the backdrop. Only a soft
contact shadow directly under each pair of feet. The background must stay perfectly plain so the
figures can be cut out cleanly.

CAMERA: LOCKED OFF on a tripod. The camera does not move even slightly - no pan, no tilt, no zoom,
no dolly, no handheld shake, no rack focus. One single continuous shot, wide, straight-on at chest
height. The framing is identical in the first frame and the last frame.

STAGING: every character stays ON THE SPOT for the whole eight seconds. Nobody walks across the
frame, nobody enters, nobody leaves. Their feet stay planted in the same place; only the body,
arms, head and expression move. FULL BODY from the top of the head to below the shoes is inside
the frame at all times, with clear empty margin above the heads and below the feet.

ANATOMY LOCK: each character has exactly one head, two arms with two hands (five fingers each) and
two legs. No extra or missing limbs, no fused bodies, no floating hands, no duplicated characters.

NEGATIVE: no text, no letters, no numbers, no signage, no logos, no watermark, no captions,
no name labels, no motion blur, no lens flare.
★NOTHING IS EVER DRAWN IN THE AIR: when a character mimes writing or drawing, the hand moves through empty space and NO ink trail, NO stroke, NO letter, NO shape and NO glowing line appears. The air stays completely empty. Only the characters themselves are visible against the backdrop.
16:9, 1280x720, 8 seconds.
"""

# (키, 그룹, 참조 캐릭터, 쓰이는 씬, 액션 본문)
ACTS = [
    ("a_write_jamo", "A", ["zollaman", "zollagirl", "stickman"], "S5 S6",
     "The three ink figures stand side by side and MIME WRITING with one extended index finger. "
     "★Their fingertips move through EMPTY AIR and leave absolutely nothing behind - no ink, no "
     "line, no letter, no square, no circle, no glow. The air in front of them stays completely "
     "blank at every moment.\n"
     "0-3s: @zollaman on the left moves his fingertip right, then straight down, then brings that "
     "hand to the back of his own neck.\n"
     "3-5s: @zollagirl in the middle touches both fingertips to her mouth and opens them outward.\n"
     "5-8s: @stickman on the right sweeps his fingertip in one smooth round motion, then nods once. "
     "All three finish with arms lowered and hold still for the final half second."),

    ("a_stack_block", "A", ["zollaman", "zollagirl", "stickman"], "S7",
     "The three ink figures BUILD AN INVISIBLE STACK, passing it upward from one to the next.\n"
     "0-3s: @zollaman on the left crouches low, then lifts both arms and raises an imaginary block "
     "high above his own head.\n"
     "3-5s: @zollagirl in the middle reaches up and sets her own block on top of his, rising onto "
     "her toes to do it.\n"
     "5-8s: @stickman on the right points up at the top of the stack with one arm fully extended, "
     "lifting his heels off the ground, and holds that point to the end."),

    ("a_count_up", "A", ["zollaman", "zollagirl", "stickman"], "S9",
     "The three ink figures COUNT ONE, TWO, THREE, and the beat travels from left to right.\n"
     "0-2.5s: @zollaman on the left raises one finger and holds it up.\n"
     "2.5-5s: @zollagirl in the middle raises two fingers, half a beat later.\n"
     "5-8s: @stickman on the right raises three fingers, half a beat later again, so the three "
     "raised hands form a rising staircase from left to right. All three hold the final shape."),

    # ★사장님 지시(2026-08-03) — **같은 캐릭터가 이어지면서 씬만 바뀔 때는 점프 한 번으로 전환한다.**
    #   장소가 바뀌지 않는 연속 씬 사이에 이 64컷을 끼워 넣으면 툭 끊기지 않는다.
    ("a_jump", "A", ["zollaman", "zollagirl", "stickman"], "씬 전환용",
     "The three ink figures TRANSITION WITH ONE SHARED JUMP.\n"
     "0-2s: all three stand still side by side, arms at their sides.\n"
     "2-4s: they bend their knees together and spring straight up in one big jump, both arms "
     "thrown up over their heads, feet clearly off the ground at the top of the arc.\n"
     "4-6s: they land together, knees absorbing the landing.\n"
     "6-8s: they straighten up, settle, and hold still facing forward, ready for the next scene."),

    ("b_jump", "B", ["injun", "jieun"], "씬 전환용",
     "TWO PEOPLE TRANSITION WITH ONE SHARED JUMP.\n"
     "@injun stands on the left, @jieun stands on the right, both facing the camera.\n"
     "0-2s: both stand still, arms at their sides.\n"
     "2-4s: they bend their knees together and spring straight up in one big jump, arms thrown up, "
     "feet clearly off the ground at the top.\n"
     "4-6s: they land together and absorb the landing.\n"
     "6-8s: they straighten, settle, and hold still, ready for the next scene."),

    ("c_jump", "C", ["madamjay", "teacherjay"], "씬 전환용",
     "TWO PEOPLE STAND UP FROM THEIR CHAIRS AND HOP ONCE TO TRANSITION.\n"
     "@teacherjay is on the left, @madamjay on the right, both sitting on simple wooden chairs "
     "that are fully visible.\n"
     "0-2s: both sit still on their chairs.\n"
     "2-4s: they rise to their feet together, one hand pushing off the seat.\n"
     "4-6s: standing clear of the chairs, they give one small hop together, both feet off the "
     "ground, arms lifting.\n"
     "6-8s: they land, straighten, and hold still standing beside their chairs, ready for the next "
     "scene."),

    # ★사장님 지시(2026-08-03) — 벽에 걸린 액자(썸네일)에서 캐릭터가 걸어 나오는 장면.
    #   배경만으로는 안 되고 7캐릭터를 참조로 붙여 **통짜로** 만든다. 합성 없이 그대로 쓴다.
    ("gallery_emerge", "ALL",
     ["teacherjay", "zollaman", "zollagirl", "stickman", "injun", "jieun", "madamjay"], "S29",
     "INSIDE A MODERN ART GALLERY ROOM: white walls with track lighting, a plain blank blackboard "
     "against the left wall, a wooden lectern, and a row of SEVEN LARGE EMPTY PICTURE FRAMES hanging "
     "along the walls. Several empty wooden chairs stand in a loose arc on the right. The camera is "
     "LOCKED OFF and never moves. "
     "0-1.5s: the room is still and empty; each frame holds a flat blank pale panel with nothing in it. "
     "1.5-6s: ONE BY ONE, FROM LEFT TO RIGHT, A CHARACTER STEPS OUT OF A FRAME. The blank panel "
     "brightens, the character appears inside it as a flat picture, then CLIMBS FORWARD OVER THE "
     "BOTTOM EDGE OF THE FRAME and drops onto the gallery floor, turning from a flat picture into a "
     "solid figure as they land. The frame they came out of is left EMPTY and pale behind them. "
     "Order: teacherjay, zollaman, zollagirl, stickman, injun, jieun, madamjay - each about half a "
     "second after the one before. "
     "6-8s: all seven stand on the floor in front of the wall facing the camera and hold still. "
     "Every frame on the wall is now empty. "
     "EXACTLY SEVEN CHARACTERS, each appearing ONE TIME ONLY, each stepping out of a DIFFERENT frame. "
     "Nobody is duplicated and nobody stays inside a frame at the end."),

    ("b_ask_price", "B", ["injun", "jieun"], "S13",
     "TWO PEOPLE, ASKING AND ANSWERING A PRICE, facing each other.\n"
     "@injun stands on the left facing right; @jieun stands on the right facing left.\n"
     "0-3s: @injun holds his right hand out toward her, palm up, and raises his eyebrows - the "
     "gesture of asking.\n"
     "3-6s: @jieun lifts her left hand and opens three fingers toward him, telling him the price.\n"
     "6-8s: both hands stay out at the SAME HEIGHT, level with their chests, in the middle of the "
     "gap between them, and they hold still smiling."),

    ("b_hold_strap", "B", ["injun", "jieun"], "S15",
     "TWO PEOPLE RIDING A BUS, holding an invisible overhead strap.\n"
     "@injun stands on the left facing right; @jieun stands on the right facing left.\n"
     "0-8s: @injun raises his right arm straight up and closes his hand around an unseen handle; "
     "@jieun raises her left arm straight up and closes her hand around the same unseen rail at the "
     "SAME HEIGHT. Both of them sway gently from side to side IN THE SAME RHYTHM, about one sway "
     "every two seconds, knees loose, as if the vehicle is moving. Their feet never leave the spot."),

    ("b_point_way", "B", ["injun", "jieun"], "S16",
     "TWO PEOPLE GIVING AND FOLLOWING DIRECTIONS.\n"
     "@jieun stands on the right, @injun stands on the left.\n"
     "0-3s: @jieun straightens her right arm and points firmly off to the RIGHT side of the frame, "
     "her whole body turning that way.\n"
     "3-6s: @injun turns his head and shoulders to follow her fingertip, looking off to the right.\n"
     "6-8s: both hold - her arm still extended, his gaze still following it, so her hand and his "
     "line of sight lie along one straight line."),

    ("b_highfive", "B", ["injun", "jieun"], "S18",
     "TWO PEOPLE GIVING EACH OTHER A HIGH FIVE.\n"
     "@injun stands on the left facing right; @jieun stands on the right facing left.\n"
     "0-3s: @injun raises his right hand to shoulder height, palm forward.\n"
     "3-5s: @jieun raises her left hand to EXACTLY THE SAME SHOULDER HEIGHT, palm forward.\n"
     "5-6s: their palms meet cleanly in the middle of the frame, at the same height, and both of "
     "them react with a laugh.\n"
     "6-8s: hands come down and they hold still, still smiling at each other."),

    # ★교실(전시실) 앉기 3종 — 사장님 승인 2026-08-03.
    #   한 편에 **세 박자**(듣기 → 박수 → 정면)를 넣어 64컷에서 포즈 3종을 한꺼번에 뽑는다.
    #   추출 지점: sit_listen≈컷08 / sit_clap≈컷34 / sit_look_front≈컷56
    ("a_sit_class", "A", ["zollaman", "zollagirl", "stickman"], "S30~S32",
     "THE THREE INK FIGURES SIT SIDE BY SIDE ON SIMPLE WOODEN CHAIRS in a row, as if in a classroom. "
     "THE CHAIRS ARE PART OF THE PICTURE and must be fully visible under each of them.\n"
     "0-3s: all three sit up straight with their hands resting on their knees, heads turned to their "
     "LEFT as if listening to a teacher standing off-frame on that side. They hold this calmly.\n"
     "3-5.5s: still seated and still turned left, all three CLAP their hands in front of their "
     "chests, several clear claps, shoulders lifting a little.\n"
     "5.5-8s: they stop clapping, turn their heads to face STRAIGHT AT THE CAMERA, hands back on "
     "their knees, and hold perfectly still looking forward."),

    ("b_sit_class", "B", ["injun", "jieun"], "S30~S32",
     "TWO PEOPLE SIT SIDE BY SIDE ON SIMPLE WOODEN CHAIRS, as if in a classroom. @injun on the left, "
     "@jieun on the right. THE CHAIRS ARE PART OF THE PICTURE and must be fully visible.\n"
     "0-3s: both sit up straight with hands resting on their knees, heads turned to their LEFT as if "
     "listening to a teacher standing off-frame on that side.\n"
     "3-5.5s: still seated and still turned left, both CLAP their hands in front of their chests, "
     "several clear claps, smiling.\n"
     "5.5-8s: they stop clapping, turn their heads to face STRAIGHT AT THE CAMERA, hands back on "
     "their knees, and hold perfectly still looking forward."),

    ("c_sit_class", "C", ["madamjay", "teacherjay"], "S30~S32",
     "TWO PEOPLE SIT SIDE BY SIDE ON SIMPLE WOODEN CHAIRS, as if in a classroom. @teacherjay on the "
     "left, @madamjay on the right. THE CHAIRS ARE PART OF THE PICTURE and must be fully visible.\n"
     "0-3s: both sit up straight with hands resting on their knees, heads turned to their LEFT as if "
     "listening to someone standing off-frame on that side.\n"
     "3-5.5s: still seated and still turned left, both CLAP their hands in front of their chests, "
     "several clear claps, smiling warmly.\n"
     "5.5-8s: they stop clapping, turn their heads to face STRAIGHT AT THE CAMERA, hands back on "
     "their knees, and hold perfectly still looking forward."),

    # ★수료식 꽃다발 — 주는 사람과 받는 사람이 한 장 안에서 완결된다(손이 허공에서 안 어긋난다)
    ("flower_give", "C", ["teacherjay", "injun"], "S32",
     "A GRADUATION MOMENT: ONE PERSON HANDS A BOUQUET OF FLOWERS TO ANOTHER.\n"
     "@teacherjay stands on the LEFT facing right, holding a simple bouquet of bright flowers in "
     "both hands. @injun stands on the RIGHT facing left, empty hands at his sides.\n"
     "0-2.5s: @teacherjay raises the bouquet and offers it forward with both hands, at chest height.\n"
     "2.5-5s: @injun reaches out and takes the bouquet with BOTH HANDS at exactly the SAME CHEST "
     "HEIGHT, so that four hands meet cleanly on the bouquet in the middle of the frame.\n"
     "5-8s: @teacherjay lets go and brings his hands together in front of him; @injun holds the "
     "bouquet against his chest and BOWS his head once in thanks, then straightens up. Both hold "
     "still, smiling."),

    ("c_talk_sit", "C", ["madamjay", "teacherjay"], "S20 S21 S27",
     "TWO PEOPLE SITTING ON SIMPLE WOODEN CHAIRS, FACING EACH OTHER, TALKING.\n"
     "@teacherjay sits on the left facing right; @madamjay sits on the right facing left. Their "
     "knees point toward each other. THE CHAIRS ARE PART OF THE PICTURE and must be fully visible.\n"
     "0-4s: @teacherjay counts things off on his fingers, one at a time, right hand in front of his "
     "chest; @madamjay nods once for each finger he folds, on the same beat.\n"
     "4-8s: both of them tap the open palm of one hand with the fingertips of the other, at the same "
     "point in the middle of the gap between them, as if settling on a date."),

    ("c_weather_look", "C", ["madamjay", "teacherjay"], "S22",
     "TWO PEOPLE SITTING ON SIMPLE WOODEN CHAIRS, LOOKING UP AT THE SKY.\n"
     "@teacherjay sits on the left, @madamjay sits on the right. The chairs are fully visible.\n"
     "0-4s: @teacherjay shades his eyes with one hand and tilts his head back to look up.\n"
     "4-8s: @madamjay looks up as well, then turns her palm face up and holds it out to check for "
     "rain. Both of their eyelines meet at the SAME POINT high above the frame. They hold that."),

    ("c_emotion_face", "C", ["madamjay", "teacherjay"], "S23",
     "TWO PEOPLE SITTING ON SIMPLE WOODEN CHAIRS - AN EMOTION PASSES FROM ONE TO THE OTHER.\n"
     "@teacherjay sits on the left, @madamjay sits on the right. The chairs are fully visible.\n"
     "0-3s: @teacherjay lets his eyebrows drop and his shoulders sag - clearly downcast.\n"
     "3-5s: @madamjay brings both hands to her chest and breaks into a wide warm smile, looking "
     "straight at him.\n"
     "5-8s: his shoulders lift again and he smiles back. The change spreads visibly from her to him."),

    ("c_nod_agree", "C", ["madamjay", "teacherjay"], "S25",
     "TWO PEOPLE SITTING ON SIMPLE WOODEN CHAIRS, AGREEING WITH EACH OTHER.\n"
     "@teacherjay sits on the left facing right; @madamjay sits on the right facing left. The chairs "
     "are fully visible.\n"
     "0-3s: @teacherjay gives one deep, slow nod toward her.\n"
     "3-6s: @madamjay nods back the same way, mirroring him, and smiles.\n"
     "6-8s: they nod once more together, at the same moment, and hold still."),
]

HEIGHT_ALL = ("HEIGHT ORDER (keep exact): @injun tallest, then @zollaman, then @teacherjay and "
              "@stickman, then @jieun, then @zollagirl, then @madamjay shortest.")
STYLE_ALL = ("@zollaman @zollagirl @stickman stay hand-drawn black ink line figures; @teacherjay "
             "@injun @jieun @madamjay stay fully coloured cartoon people. Do not blend the two styles. "
             "Flat 2D cartoon illustration, bold clean black outlines.")
STYLE_OF = {"A": (STYLE_A, HEIGHT_A), "B": (STYLE_HUMAN, HEIGHT_B), "C": (STYLE_HUMAN, HEIGHT_C),
            "ALL": (STYLE_ALL, HEIGHT_ALL)}


def build(key, grp, refs, scenes, action):
    style, height = STYLE_OF[grp]
    who = "\n".join(DESC[r] for r in refs)
    n = len(refs)
    head = (f"EXACTLY {['','ONE','TWO','THREE','FOUR','FIVE','SIX','SEVEN'][n]} CHARACTERS in the frame, no more and no fewer, "
            f"each appearing ONE TIME ONLY:\n{who}\n")
    return f"{head}\n{action}\n\nSTYLE: {style}\n{height}\n{TAIL}".strip() + "\n"


def main(listonly=False):
    os.makedirs(OUT_DIR, exist_ok=True)
    for key, grp, refs, scenes, action in ACTS:
        path = f"{OUT_DIR}/{key}.txt"
        if listonly:
            mark = "有" if os.path.exists(path) else "  "
            print(f"[{mark}] {key:16s} {grp}({len(refs)}인) 씬 {scenes:12s} {', '.join(refs)}")
            continue
        open(path, "w", encoding="utf-8").write(build(key, grp, refs, scenes, action))
        print(f"  {key:16s} {grp}({len(refs)}인) 씬 {scenes:12s} → {path}")
    if not listonly:
        print(f"\n✅ 그룹 동작 프롬프트 {len(ACTS)}종 → {OUT_DIR}/")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    main(a.list)
