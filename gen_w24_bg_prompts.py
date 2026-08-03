# -*- coding: utf-8 -*-
"""W24 배경 프롬프트 12키 생성 — 동영상 4 + 정지 8 (2026-08-03).

출처: `W24/W24_scenario.md` A-1 / A-2 표.
공통 규칙(사장님 확정):
  · 왼편은 단순하게 — 인물이 서는 자리다
  · 바닥은 가로로 끊김 없이 — 인물이 걸어갈 수 있어야 한다
  · **글자·간판 문자 절대 금지** (W23 깨진 한글 사고)
  · 인물·캐릭터 등장 금지 — 배경은 배경만
  · 동영상은 **획기적 변화** 규격: 0~2초 시작 → 2~6초 대변화 → 6~8초 안착

사용:
  python gen_w24_bg_prompts.py
  python gen_w24_bg_prompts.py --list
"""
import argparse
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
OUT_DIR = "W24/bg_prompts"

TAIL = ("Flat 2D cartoon illustration in a warm storybook style, bold clean outlines, flat cel "
        "shading, no gradients, no photographic realism. "
        "★ABSOLUTELY NO TEXT: no letters, no Korean characters, no numbers, no signage lettering, "
        "no shop names, no posters with writing, no logos, no watermark. Every sign, board, banner "
        "and screen is BLANK - plain coloured panels with nothing written on them. "
        "NO PEOPLE, no human figures, no cartoon characters, no silhouettes of people, no animals. "
        "★Keep the LEFT THIRD of the frame visually calm and uncluttered - that is where a character "
        "will stand. The ground runs continuously from the left edge to the right edge across the "
        "bottom of the frame with no break, so a figure could walk along it. "
        "16:9, 1280x720.")

# (키, 종류, 프롬프트 본문)
BGS = [
    # ── 배경 동영상 4 (획기적 변화) ──
    ("ddp_arrive", "VIDEO",
     "0-2s: a wide establishing shot of a huge silver curved-metal design museum seen from across "
     "an empty morning plaza, its smooth aluminium skin catching low sunlight. "
     "2-6s: the camera accelerates forward and slides along the curving wall, the building sweeping "
     "past on the left, and dives through a wide glass entrance into the interior. "
     "6-8s: it decelerates and settles into a locked wide view of a silver curved lobby - a smooth "
     "curved handrail on the left, a plain information column on the right. The location changes "
     "from outside the building to inside the lobby. Strong forward dolly, no Ken Burns zoom."),

    # ★재생성(2026-08-03): 앞판은 "chalk-like strokes" 라는 말 때문에 모델이 **글자를 그렸다.**
    #   화면 글자는 글씨랑이 파라메트릭으로 그리는 게 원칙이라 배경에 글자가 있으면 못 쓴다.
    #   → 획·필기 같은 낱말을 전부 빼고 **기하 도형**으로만 말한다.
    ("board_time", "VIDEO",
     "0-2s: a close view of a plain smooth WHITE gallery wall, completely bare and clean, with a "
     "few small flat GEOMETRIC SHAPES resting against it - a circle, a square and a triangle, like "
     "plain paper cut-outs. Nothing is drawn or painted on the wall. "
     "2-6s: those flat shapes LIFT AWAY FROM THE WALL and float forward into the room, turning "
     "slowly in the air and catching the light, while the camera pulls back to reveal the whole "
     "white exhibition hall. "
     "6-8s: the shapes settle, hovering gently in the middle of the hall, and the camera stops on a "
     "locked wide view of the white gallery. "
     "★THEY ARE ONLY A CIRCLE, A SQUARE AND A TRIANGLE - simple geometry. They are NEVER letters, "
     "never handwriting, never calligraphy, never brush strokes, never symbols, never signs. There "
     "is NO writing anywhere in this shot at any moment."),

    ("classroom_sejong", "VIDEO",
     "0-2s: a locked straight-on view of the far wall of a MODERN ART GALLERY EXHIBITION ROOM - "
     "smooth white gallery wall with track lighting, a plain blackboard standing against the left "
     "wall, a wooden lectern, and in the centre of the wall a large ornate framed portrait of a "
     "dignified Korean king in traditional red royal robes and a black winged hat, painted in flat "
     "cartoon style, sitting perfectly still like a painting. "
     "2-6s: ★the portrait comes subtly alive - the king slowly raises one hand and STROKES HIS BEARD "
     "once, a small quiet gesture, still inside the frame of the painting. "
     "6-8s: he BREAKS INTO A GENTLE WARM SMILE, holds it for a moment, and settles back into "
     "stillness as a painting again. The camera never moves. Nothing else in the room moves."),

    # ★사장님 지시(2026-08-03) — 전시실 빈 액자에서 캐릭터가 하나씩 튀어나와 자기 자리에 모인다.
    #   캐릭터는 합성으로 얹으므로, 배경 동영상은 **액자가 깨어나는 것**까지만 담당한다.
    ("gallery_wake", "VIDEO",
     "0-2s: a locked view of a quiet modern art gallery room - white walls, track lighting, a plain "
     "blank blackboard against the left wall, a wooden lectern, several empty wooden chairs in a "
     "loose arc on the right, and a row of LARGE EMPTY PICTURE FRAMES on the walls, each holding a "
     "flat panel of solid pale colour with nothing in it. Everything is still. "
     "2-6s: ★one by one, from left to right, the blank panels inside the frames WAKE UP - each one "
     "brightens, its surface ripples outward like water, and a soft glow spills from the frame onto "
     "the wall and floor beneath it. The frames stay on the wall; nothing steps out of them. "
     "6-8s: all the panels are gently glowing and rippling, the room is warmer and brighter, and "
     "the camera holds perfectly still on the same framing, waiting."),

    ("gallery_out", "VIDEO",
     "0-2s: a locked view of the same modern art gallery room, but now every picture frame on the "
     "wall holds a plain EMPTY pale panel again and the wooden chairs stand empty and slightly "
     "askew, as if everyone has just got up and left. Warm low light. "
     "2-6s: the camera begins to PULL BACKWARD smoothly, the gallery room receding, and glides out "
     "through a tall open doorway; the white walls sweep past on both sides and bright daylight "
     "grows from behind the camera. "
     "6-8s: the camera emerges into the open air and settles into a locked wide view of a broad "
     "sunlit public square with pale stone paving. The location changes from inside the gallery to "
     "outside in the square."),

    # ★재생성(2026-08-03): 앞판은 카메라가 바닥에 너무 붙어 **바닥 클로즈업**이 됐다.
    #   군중이 모이는 넓은 공간감이 안 나온다 → 눈높이 와이드로 못박고 건물·하늘을 반드시 넣는다.
    ("plaza_gather", "VIDEO",
     "★A WIDE ESTABLISHING SHOT AT EYE LEVEL. The horizon and the sky must be visible in the upper "
     "half of the frame at all times, with low buildings around the edges of the square. Never point "
     "the camera down at the ground; never fill the frame with paving. "
     "0-2s: a broad empty public square at sunset seen straight on from across it - pale stone "
     "paving stretching away, low buildings around the far side, warm orange sky above, deserted. "
     "2-6s: lights embedded in the paving switch on in sequence, sweeping outward from the centre in "
     "a widening ring, while the camera rises a little and pulls back so MORE of the square and the "
     "surrounding buildings come into view. "
     "6-8s: it settles into a locked wide view of the whole square with a bright empty circle in the "
     "middle and glowing rings around it, sky and buildings still clearly visible, ready for a crowd "
     "to gather in the centre."),

    # ── ★장소 전환 6 (사장님 지시 2026-08-03) ──
    #   배경이 갑자기 바뀌지 않게 이어 준다. ★기법을 **전부 다르게** 써서 반복돼 보이지 않게 한다:
    #     ① 휩 팬 ② 유리 통과 ③ 크레인 다운+바닥 통과 ④ 틸트 업+상승
    #     ⑤ 시간경과+푸시 인 ⑥ 매치 컷(둥근 빛 → 둥근 빛)
    #   인물은 없다(합성으로 얹는다).
    ("to_hall", "VIDEO",
     "★TRANSITION BY WHIP PAN. "
     "0-2s: a locked view of a silver curved museum lobby with a smooth curved handrail, held still. "
     "2-4s: the camera WHIPS violently to the right - the image smears into horizontal motion blur, "
     "colours streaking, so fast that nothing is readable. "
     "4-6s: the whip decelerates and the blur resolves into a different room. "
     "6-8s: it settles, locked and sharp, on a bright exhibition hall with large smooth WHITE curved "
     "walls, a low display plinth on the left and a glass balustrade on the right."),

    ("to_path", "VIDEO",
     "★TRANSITION BY PASSING THROUGH GLASS. "
     "0-2s: a locked view of a bright white-walled exhibition hall, a tall glass door ahead. "
     "2-5s: the camera accelerates straight at the glass door and PASSES THROUGH IT - for a moment "
     "the frame is filled with a white bloom of daylight and a soft lens flare as the interior is "
     "washed out. "
     "5-8s: the bloom fades and the camera settles, locked, on an outdoor walkway curving around a "
     "silver metal building in the afternoon, a curved handrail on the left, a lamp post on the right."),

    ("to_ruins", "VIDEO",
     "★TRANSITION BY CRANE DOWN THROUGH THE FLOOR. "
     "0-2s: a high looking-down view of a sunlit stone walkway beside a silver curved building. "
     "2-5s: the camera CRANES STRAIGHT DOWN toward the paving, keeps going and SINKS THROUGH the "
     "stone floor - the frame darkens as the daylight is cut off above and warm spot lighting rises "
     "from below. "
     "5-8s: it comes to rest, locked and level, in an underground gallery with an excavated old "
     "Korean stone fortress wall of stacked grey granite across the back, a low stone block on the "
     "left and a blank exhibit panel on the right."),

    ("to_grass", "VIDEO",
     "★TRANSITION BY TILT UP AND RISE. "
     "0-2s: a locked view of the underground stone-wall gallery, warm spot lighting. "
     "2-5s: the camera TILTS UP toward the dark ceiling and then RISES straight through it, the "
     "stone falling away below and daylight flooding in from above as the frame opens to sky. "
     "5-8s: it tilts back down and settles, locked, on a gentle green grass hill in a city park with "
     "a silver curved building rising behind it, a low stone kerb on the left, a wooden bench on the "
     "right. Warm late afternoon light."),

    ("to_rose", "VIDEO",
     "★TRANSITION BY TIME LAPSE AND SLOW PUSH IN. The camera never changes location. "
     "0-2s: a locked view of a green grass hill in warm late afternoon light. "
     "2-6s: TIME PASSES QUICKLY - the sun sinks, shadows stretch and vanish, the sky runs from gold "
     "through orange to deep blue dusk, and hundreds of small rose-shaped lights switch on across the "
     "ground ahead in a spreading wave. At the same time the camera PUSHES IN slowly and steadily. "
     "6-8s: the push settles into a locked view of a garden of glowing LED roses at early evening, a "
     "low planting kerb on the left, a glowing lamp post on the right."),

    ("to_gallery", "VIDEO",
     "★TRANSITION BY MATCH CUT - a round glow becomes another round glow. "
     "0-3s: a very close view of ONE glowing LED rose at night, its soft round halo of warm light "
     "filling the centre of the frame against deep blue darkness. "
     "3-5s: the camera pushes in until that round halo fills almost the whole frame and everything "
     "else is dark - and then the halo SLOWLY RESOLVES into a different round glow: the pool of warm "
     "light cast by a gallery ceiling spotlight on a white wall. "
     "5-8s: the camera pulls back from that spot of light to reveal a modern art gallery room with "
     "white walls and track lighting - a blank blackboard against the left wall, a wooden lectern, "
     "empty wooden chairs on the right and empty picture frames on the walls."),

    # ── 배경 정지 8 ──
    ("ddp_lobby", "STILL",
     "The interior lobby of a silver curved-metal design museum in the morning. Smooth flowing "
     "aluminium walls, soft daylight from a skylight, pale polished floor. A simple curved handrail "
     "low on the left, a plain smooth column on the right. Calm, airy, uncluttered."),

    ("ddp_hall", "STILL",
     "An exhibition hall inside a curved design museum - large smooth WHITE curved walls filling "
     "most of the frame, bright even daylight, pale grey floor. A low plain display plinth on the "
     "left, a simple glass balustrade on the right. The white wall is broad and empty, ideal for "
     "showing drawings against."),

    ("ddp_ruins", "STILL",
     "An underground archaeological gallery beneath a modern museum: an excavated old Korean stone "
     "fortress wall of stacked grey granite blocks running across the back, warm spot lighting from "
     "above, a dark stone floor. A low stone block on the left, a plain blank exhibit panel on the "
     "right. Quiet and reverent."),

    ("ddp_path", "STILL",
     "An outdoor walkway curving around the outside of a silver curved-metal building in the "
     "afternoon. The paved path sweeps from the lower left up to the right, the building's smooth "
     "metal skin rising on one side, open sky on the other. A simple curved handrail on the left, "
     "a plain lamp post on the right. Warm afternoon light."),

    ("ddp_grass", "STILL",
     "A gentle grass hill in a city park in the late afternoon, soft green lawn sloping across the "
     "frame, a silver curved building rising behind it, warm low sun. A low stone kerb on the left, "
     "a simple wooden bench on the right. Calm and open."),

    ("ddp_rose", "STILL",
     "A garden of glowing LED roses at early evening - hundreds of small softly luminous rose lights "
     "on slender stems filling the middle and right of the frame, deep blue dusk sky above, warm "
     "pink and white glow. A low planting kerb on the left, a plain glowing lamp post on the right. "
     "The left third stays open and calm."),

    # ★사장님 지시(2026-08-03): 교실이 아니라 **미술관 전시실**이다. 캐릭터가 전시실 벽의
    #   빈 액자에서 튀어나와 하나씩 모여드는 자리다. 그래서 전시실 안에 칠판과 의자가 놓여 있다.
    ("classroom", "STILL",
     "The inside of a MODERN ART GALLERY EXHIBITION ROOM, not a school. Tall smooth white gallery "
     "walls with soft track lighting from above and a pale polished concrete floor, seen from a "
     "slightly angled three-quarter view.\n"
     "★Set up INSIDE the gallery, as if it were an art installation: a plain dark green blackboard "
     "standing against the LEFT wall with a chalk tray beneath it, a simple wooden lectern in front "
     "of it, and several simple wooden chairs arranged in a loose arc on the right half of the room. "
     "The blackboard is completely BLANK - not one mark or letter on it.\n"
     "★On the white walls hang SEVERAL LARGE EMPTY PICTURE FRAMES of different sizes, each one "
     "holding a plain flat panel of solid pale colour with NOTHING drawn inside it - completely "
     "blank canvases waiting for something to step out of them. "
     "One larger ornate frame in the centre of the far wall holds a painted portrait of a dignified "
     "Korean king in red royal robes and a black winged hat, in flat cartoon style - he is the only "
     "figure in the whole picture, and he is a painting inside a frame, not a person in the room."),

    ("plaza_day", "STILL",
     "A wide open public square in daylight, broad pale stone paving stretching from edge to edge, "
     "low modern buildings set back around it, bright clear sky. A low stone step on the left, a "
     "simple lamp post on the right. Very open and uncluttered - a place where a crowd could gather."),
]


def main(listonly=False):
    os.makedirs(OUT_DIR, exist_ok=True)
    nv = sum(1 for _k, t, _p in BGS if t == "VIDEO")
    for key, kind, body in BGS:
        path = f"{OUT_DIR}/{key}.txt"
        if listonly:
            mark = "有" if os.path.exists(path) else "  "
            print(f"[{mark}] {key:18s} [{kind:5s}]")
            continue
        open(path, "w", encoding="utf-8").write(f"{body}\n\n{TAIL}\n")
        print(f"  {key:18s} [{kind:5s}] → {path}")
    if not listonly:
        print(f"\n✅ 배경 프롬프트 {len(BGS)}키 (동영상 {nv} · 정지 {len(BGS)-nv}) → {OUT_DIR}/")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    main(a.list)
