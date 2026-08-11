# -*- coding: utf-8 -*-
"""W1-2 배경 — 광화문광장 (korea 168경 week1/day2). **캐릭터와 상호작용하는 배경.**

★사장님 지시(2026-08-11): **"내가 극적으로 생각하는 것은 배경 동영상과 캐릭터가
  상호작용하는 것이다."**

그래서 배경을 '흔들리는 그림'으로 만들지 않는다. 배경 안에 **캐릭터가 건드릴 물체**를
심고, 그 물체가 **캐릭터 쪽으로 움직이게** 만든다. 합성 단계에서 캐릭터의 동작이 그
타이밍에 맞물린다(오이가 굴러오는 순간에 카드를 든다).

## 상호작용 설계
| 씬 | 배경이 하는 일 | 캐릭터가 하는 일 |
|---|---|---|
| S7  오이  | 좌판에서 **오이 하나가 굴러 내려온다** | 카드를 들어 받는다 |
| S9  우유  | 우유팩이 **톡 넘어져 미끄러진다** | 카드를 들어 받는다 |
| S12 오    | 분수가 **'오!' 하고 솟구친다** | 놀라는 포즈 |
| S15 여우  | 덤불에서 **여우가 고개를 내밀었다 숨는다** | 가리킨다 |
| S19 매칭  | 은행잎이 **세 갈래로 흩날린다** | 카드 세 장 부채 |
| S20 마무리| 광화문 **조명이 하나씩 켜진다** | 손을 든다 |

## 규칙
· **왼쪽 절반은 비운다**(텍스트박스·파라메트릭 한글 자리) — 움직임도 오른쪽에서
· 움직이는 물체는 **화면 오른쪽 아래**로 와서 멈춘다(캐릭터 손 높이)
· 카메라는 고정 — 물체가 움직이지 카메라가 움직이지 않는다
· 화면 안 글자 절대 금지
"""

STYLE = (
    "Flat 2D children's picture-book illustration, clean vector look, soft pastel palette, "
    "gentle warm daylight, simple shapes, bold clean outlines, flat cel shading. "
    "No photorealism, no harsh shadows, no film grain, no people, no animals except where "
    "stated. Wide 16:9 view with an empty paved ground strip across the bottom third. "
    "★The LEFT HALF of the frame stays calm and uncluttered - open sky or plain paving - "
    "so text can sit there later. All detail and all movement happen on the RIGHT. "
    "★Camera is locked: no pan, no zoom, no shake. Only the described object moves. "
    "Absolutely NO text, letters, numbers, signs or logos anywhere."
)

# (키, 종류, 장면, 동작)  종류: video / still
BGS = [
    ("gwanghwamun_wide", "video",
     "A broad open city plaza in Seoul on a clear morning. On the right stands a large bronze "
     "seated king statue on a stone pedestal, a traditional palace gate with tiled roof behind "
     "it, a green mountain ridge far beyond, and a low row of fountain jets. The left half is "
     "open sky and plain grey paving, empty.",
     "0-2s: the plaza is still, fountain jets low. 2-5s: the fountain jets rise one after "
     "another from left to right along the row, water climbing higher and higher. 5-8s: the "
     "jets settle back to a gentle steady spray and hold. Nothing else moves."),

    ("gwanghwamun_statue", "still",
     "The foot of the bronze king statue seen from ground level on the right of frame - stone "
     "pedestal, three shallow steps, a low guard rail, two potted pines. The left half is calm "
     "open paving and pale sky.",
     ""),

    ("gwanghwamun_stall", "video",
     "A small open-air market stall at the right edge of the plaza - striped awning, a wooden "
     "crate of green cucumbers tilted toward the viewer, cartons of milk stacked beside it, a "
     "basket of apples. The palace gate is small in the far background. The left half is empty "
     "paving and sky.",
     "0-1.5s: the stall is still. 1.5-4s: ONE green cucumber rolls out of the tilted crate, "
     "down the slope and across the paving toward the lower right foreground. 4-6s: it comes to "
     "rest on the paving at the lower right. 6-8s: a milk carton on the stack tips over and "
     "slides a short way down to rest beside the cucumber. Everything else stays still."),

    # ★상호작용용 — 캐릭터가 **걸터앉을** 자리가 또렷해야 앵커를 찍을 수 있다.
    ("gwanghwamun_bench", "still",
     "A long wooden park bench stands side-on in the RIGHT half of the plaza, seen from a "
     "straight-on eye-level view so its flat seat plank reads as a clear horizontal line. "
     "The bench has a plain slatted backrest and simple legs, and its seat is empty. "
     "Beside it on the far right is a low stone railing with a flat top rail at hand height. "
     "A young gingko tree stands behind the bench, a low flower bed in front, and the palace "
     "gate is small in the far distance. The paving in front of the bench is plain and open. "
     "The LEFT half is empty lawn and sky with nothing in it.",
     ""),

    ("gwanghwamun_fountain", "video",
     "A round stone fountain basin on the right side of the plaza, the palace gate behind it, "
     "shallow water and a ring of small jets. The left half is open sky and plain paving.",
     "0-1.5s: the basin is calm, jets barely trickling. 1.5-3.5s: a single tall jet bursts "
     "straight up from the centre, water climbing fast and spreading into a wide crown. "
     "3.5-6s: the crown falls back as glittering droplets. 6-8s: the water settles to a calm "
     "ripple. Camera locked, only the water moves."),

    ("gwanghwamun_path", "video",
     "A gingko-lined walking path along the side of the plaza, golden leaves on the trees and "
     "scattered on the ground, running from the right foreground into the distance. A low leafy "
     "bush sits at the right edge of the path. The left half is open sky and plain path surface.",
     "0-2s: the path is still. 2-4.5s: a small red fox pokes its head out of the bush on the "
     "right, looks toward the viewer, then ducks back in and disappears. 4.5-8s: golden gingko "
     "leaves drift down and scatter across the right side of the path. Nothing else moves."),

    ("gwanghwamun_dusk", "video",
     "The same plaza at dusk - warm amber sky, the palace gate on the right, the bronze statue "
     "in silhouette, the fountain row quiet. The left half is deep calm evening sky.",
     "0-2s: the plaza is dim, lights off. 2-5.5s: the lanterns along the palace gate switch on "
     "one after another from right to left, warm pools of light spreading across the stone. "
     "5.5-8s: the last lantern lights and everything holds, glowing softly."),
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
