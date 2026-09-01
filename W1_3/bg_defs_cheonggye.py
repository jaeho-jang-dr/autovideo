# -*- coding: utf-8 -*-
"""W1-3 배경 — 청계천(Cheonggyecheon Stream), 서울. `W1_3/W1_3_motion.md` §4·§5 의 씬별
카메라 무빙을 그대로 옮겨 적은 프롬프트 데이터다(사장님 확정 — 이 회차부터 배경 카메라는
항상 움직인다. 정적 Ken-Burns 줌·고정 카메라 금지. W1-2 의 "camera is locked" 규칙은
여기서 쓰지 않는다 — 이번엔 정반대다).

캐릭터(졸라걸)는 합성 단계에서 별도로 얹는다 — 이 배경엔 사람을 그리지 않는다
(먼 배경의 행인은 실루엣 허용, 필수는 아님).

    python W1_3/flow_make_bg_cheonggye.py cheonggye_entrance   # 하나만
    python W1_3/flow_make_bg_cheonggye.py --all                # 미생성분 전부
"""

STYLE = (
    # ★2026-09-01 사장님 지적 — "지금껏 모든 배경은 만화 애니 형식인데 이번만 실사로
    #   만들었다." 임의로 사진 다큐멘터리 스타일을 썼던 걸 폐기하고, W1_2/bg_defs.py의
    #   확정 하우스 스타일(Flat 2D picture-book illustration)로 되돌린다.
    "Flat 2D children's picture-book illustration, clean vector look, soft pastel palette, "
    "gentle warm daylight, simple shapes, bold clean outlines, flat cel shading. "
    "No photorealism, no harsh shadows, no film grain, no photographic texture. "
    "★ONE CONTINUOUS SCENE ACROSS THE WHOLE 16:9 FRAME. Left, middle and right all belong "
    "to the same place: the ground line, the horizon and the perspective run unbroken all "
    "the way across, edge to edge. No split screen, no panel borders, no letterboxing. "
    "★THE CAMERA ACTIVELY MOVES the whole 8 seconds exactly as described below — this is a "
    "real dolly / pan / tilt / zoom move, NOT a static locked shot and NOT a simple linear "
    "Ken-Burns crop on a still illustration. The motion must reveal or change something in "
    "the frame, not just get closer to the same fixed view. "
    "★The walking surface (steps, stepping stones, path, bridge deck) runs continuously "
    "from one side of the frame toward the camera so a character can be composited "
    "standing/walking on it later — never let the ground disappear behind an object or "
    "cut off awkwardly. "
    "If distant pedestrians appear, they are plain dark silhouettes with no facial detail "
    "— never a foreground person, never posed toward camera. "
    "Absolutely NO text, letters, numbers, signage lettering, logos, or watermarks anywhere. "
    "16:9, 1280x720, 8 seconds."
)

# BGS: (key, kind, scene(장소·정적 묘사), motion(0-2s/2-6s/6-8s 카메라 무빙 지시))
BGS = [
    ("cheonggye_entrance", "video",
     "A stone stairway entrance leading down from a city bridge into the sunken "
     "Cheonggyecheon stream corridor in central Seoul — modern high-rise buildings "
     "visible at street level above, shallow clear water running below, smooth paved "
     "steps in the middle ground.",
     "0-2s: a wide establishing view from the bridge railing looking down across the "
     "stream corridor. 2-6s: the camera dollies forward and tilts down, moving toward "
     "the top of the stairway as if about to descend, the bridge structure sliding out "
     "of the top of frame. 6-8s: the camera settles into a locked-off view centered on "
     "the stairway landing, steps running from the top of frame down toward the bottom "
     "center. Bold forward+down move, not a simple zoom."),

    ("cheonggye_stairs", "video",
     "Continuing down the same stone stairway, closer to stream level now — individual "
     "steps visible in the foreground, the shallow stream and a row of trimmed shrubs "
     "along the walkway visible ahead.",
     "0-2s: view from partway down the stairway, steps descending toward the bottom of "
     "frame. 2-6s: the camera continues a slow forward dolly and tilts further down, "
     "following the line of the steps, the stream corridor walkway opening up ahead. "
     "6-8s: settles on a view of the last few steps meeting the flat walkway, water "
     "visible on the right. The steps stay in continuous contact with the ground the "
     "whole time — no jump cuts in geometry."),

    ("cheonggye_stones", "video",
     "A classic Cheonggyecheon stepping-stone crossing (jingeomdari) — flat round "
     "stones spaced across the shallow stream, clear running water flowing between "
     "them, concrete embankment walls on both sides, some reeds and grass at the "
     "water's edge.",
     "0-2s: a wide view along the stream showing the full line of stepping stones "
     "receding into the distance. 2-7s: the camera pans slowly to the right at a "
     "steady speed, following the direction the water flows, keeping the stepping "
     "stones in the lower-middle of frame throughout — never reverse the pan direction. "
     "7-8s: settles on a view centered on one stone. Continuous rightward drift, water "
     "always flowing the same direction as the pan."),

    ("cheonggye_stones_midstream", "video",
     "The same Cheonggyecheon stepping-stone crossing, a little further downstream — "
     "the stones here sit flatter and closer together, willow branches from the bank "
     "casting faint shadows onto the water's edge, clear water flowing between the "
     "stones, concrete embankment walls on both sides.",
     "0-2s: a wide view along this stretch of stones. 2-7s: the camera pans slowly to "
     "the right at a steady speed, the SAME direction as the water flows (matching the "
     "original stepping-stone background — never reverse the pan, it would make the "
     "river look like it flows backward), keeping the stones in the lower-middle of "
     "frame throughout. 7-8s: settles on a view centered on one stone."),

    ("cheonggye_stones_downstream", "video",
     "The Cheonggyecheon stream widens slightly here — the stepping stones continue, "
     "but the far bank is clearly visible in the distance with a low footbridge crossing "
     "in the background, giving a sense of open depth across the water for something to "
     "approach from far away.",
     "0-2s: a wide view showing the stones in the foreground and the distant far bank "
     "with the low bridge behind. 2-7s: the camera pans slowly to the right, matching "
     "the water's flow direction, keeping both the near stones and the distant bank "
     "visible throughout (do not zoom in so far that the far bank disappears — depth is "
     "the point of this shot). 7-8s: settles on a view with clear foreground stones and "
     "background depth intact."),

    ("cheonggye_willow_bench", "video",
     "A low wooden bench framed straight-on beneath drooping willow branches at the "
     "Cheonggyecheon, dappled shade falling across the seat and the paving in front of "
     "it, calm and unhurried.",
     "0-2s: a straight-on view of the bench in dappled shade. 2-6s: only the willow "
     "leaves and their shadows drift gently in a light breeze — the camera itself barely "
     "moves, at most a very slow, almost imperceptible creep forward (this is a "
     "deliberately calm, low-motion shot to match a restful moment, unlike the other "
     "backgrounds). 6-8s: settles, leaves still swaying softly. Even here the shot is "
     "not perfectly frozen — leaf shadows must keep moving the whole 8 seconds."),

    ("cheonggye_underpass", "video",
     "The dim, shaded underside of a wide road bridge crossing over the Cheonggyecheon "
     "walkway — concrete bridge-deck ceiling overhead, cooler bluish light, the bright "
     "sunlit walkway visible continuing beyond the underpass on the far side, water "
     "running alongside the path.",
     "0-2s: a view approaching the underpass from the sunlit side, the dark opening "
     "ahead. 2-6s: the camera moves forward into the shade and pulls back / zooms out "
     "slightly as it goes, widening the shot to reveal the full width and height of the "
     "underpass space (a deliberate zoom-out, not zoom-in, to make the tunnel feel "
     "larger). 6-8s: settles on a locked-off wide view from inside the underpass "
     "looking back toward the bright opening. The path and water stay continuous "
     "underfoot the whole time."),

    ("cheonggye_willow", "video",
     "A calm bend of the Cheonggyecheon stream lined with weeping willow trees, their "
     "branches trailing near the water surface, a low wooden bench set back from the "
     "path in dappled shade, smooth flat paving stones along the water's edge.",
     "0-2s: a wide view of the willow-lined bend, branches swaying gently in a light "
     "breeze. 2-6s: the camera dollies forward slowly and zooms in gently toward the "
     "water's edge near the bench, the willow branches drifting past the top of frame. "
     "6-8s: settles on a calmer, closer view of the water's surface and the bench area, "
     "leaves still swaying — motion is gentle throughout, but never fully static."),

    ("cheonggye_mural", "video",
     "A long tiled mural wall along the Cheonggyecheon walkway, decorated with colorful "
     "abstract patterned tiles (no readable text or letters, pure pattern and color), "
     "the paved walkway running along its base.",
     "0-2s: a close view on one section of the tiled mural. 2-6s: the camera zooms out "
     "and pulls back steadily, revealing the full length of the mural wall and the open "
     "walkway in front of it, leaving clear open paved space in the lower-middle of "
     "frame for a figure to stand. 6-8s: settles on a wide, locked-off view of the "
     "whole mural with open foreground space. Motion is a clean pull-back, not a crop-zoom."),

    ("cheonggye_bridge_dusk", "video",
     "A wide pedestrian bridge crossing the Cheonggyecheon stream at dusk, string "
     "lights and lantern-style lamps mounted along the railings, the sky transitioning "
     "from orange sunset to deep blue, city lights beginning to glow on the buildings "
     "above the stream corridor.",
     "0-2s: a view of the bridge deck in late orange sunset light, lamps still off. "
     "2-6s: the camera slowly zooms out and rises slightly, pulling back from the "
     "bridge deck to reveal the wider corridor, while the lanterns switch on one by one "
     "in sequence along the railing as the sky visibly darkens from orange to blue. "
     "6-8s: settles on a wide dusk view of the fully lit bridge. Day-to-dusk lighting "
     "change happens within the one clip, camera pulling back the whole time."),
]

BY = {k: (kind, scene, motion) for k, kind, scene, motion in BGS}


def prompt(key):
    kind, scene, motion = BY[key]
    return "%s\n\n%s\n\nMOTION (fill all 8 seconds): %s" % (STYLE, scene, motion)


if __name__ == "__main__":
    for k, kind, _, _ in BGS:
        print("%-24s %-6s %5d자" % (k, kind, len(prompt(k))))
