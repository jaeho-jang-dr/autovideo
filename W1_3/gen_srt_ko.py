# -*- coding: utf-8 -*-
"""W1-3 한국어 소프트 자막(.ko.srt) 생성 + 씬 타임라인 확정.
나레이션 실측 길이(edge-tts, 1.1배속 후) + 0.35초 패딩으로 각 씬 길이를 정하고
([[subtitle-sync-burn-drive]] 원칙의 단일언어판), 그 타임라인 그대로 SRT를 만든다.
compile_w1_3.py는 이 스크립트가 만든 `W1_3/timeline.json`을 그대로 읽어 씬 길이로 쓴다
— 자막·영상 두 산출물이 같은 시간표를 공유해야 어긋나지 않는다.

★2026-09-01 사장님 지시 — "자막은 한꺼번에 너무 길게 쓰지 말고 두 줄 정도로만 만든다."
한 씬(문장 2~4개)을 통째로 한 자막 큐에 몰아넣으면 3줄 이상 나온다. 문장 단위로
쪼개 **씬 하나 = 자막 여러 큐**로 만들고(글자수 비례로 씬 구간을 나눠 배분 —
compile_stickman.py의 sub_sched 방식과 동일 원칙), 큐 하나는 최대 2줄로 감싼다.

출력: W1_3/w1_3.ko.srt , W1_3/timeline.json
"""
import os
import json
import re

from narration_ko import NARR_KO, SCENE_ORDER
from annotate_ko import annotate_scene

PAD = 0.35
WRAP_WIDTH = 22
MAX_LINES = 2
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_audio_ko")

# 문장 끝(.!?) 뒤 공백에서 자른다. 인용부호 안 자모/단어에는 문장부호가 없어 안전.
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def split_sentences(text):
    parts = [p.strip() for p in _SENT_SPLIT.split(text) if p.strip()]
    return parts or [text]


def wrap_text(text, width=WRAP_WIDTH, max_lines=MAX_LINES):
    """공백 기준 그리디 줄바꿈. width를 넘겨도 max_lines를 넘기지 않도록
    필요하면 폭을 넓혀 다시 감싼다(한 문장이 짧으므로 대개 1~2줄에서 끝난다)."""
    def _wrap(w):
        words = text.split(" ")
        lines, cur = [], ""
        for word in words:
            cand = (cur + " " + word).strip()
            if len(cand) > w and cur:
                lines.append(cur)
                cur = word
            else:
                cur = cand
        if cur:
            lines.append(cur)
        return lines

    lines = _wrap(width)
    w = width
    while len(lines) > max_lines and w < len(text):
        w += 6
        lines = _wrap(w)
    if len(lines) > max_lines:
        # 그래도 넘치면(아주 긴 문장) 강제로 두 줄에 나눠 담는다.
        mid = len(text) // 2
        cut = text.rfind(" ", 0, mid) or mid
        lines = [text[:cut].strip(), text[cut:].strip()]
    return "\n".join(lines)


def main():
    with open(os.path.join(AUDIO_DIR, "durations.json"), encoding="utf-8") as f:
        durations = json.load(f)

    timeline = []
    srt_blocks = []
    idx = 0
    t = 0.0
    for scene in SCENE_ORDER:
        dur = durations[scene]
        scene_len = round(dur + PAD, 3)
        scene_start = t
        annotated = annotate_scene(scene, NARR_KO[scene])
        sentences = split_sentences(annotated)
        lens = [max(1, len(s)) for s in sentences]
        tot = sum(lens)
        acc = 0.0
        for sent, L in zip(sentences, lens):
            idx += 1
            portion = scene_len * L / tot
            start, end = scene_start + acc, scene_start + acc + portion
            acc += portion
            srt_blocks.append(
                "%d\n%s --> %s\n%s\n" % (idx, ts(start), ts(end), wrap_text(sent))
            )
        timeline.append({
            "scene": scene,
            "start": round(scene_start, 3),
            "end": round(scene_start + scene_len, 3),
            "len": scene_len,
            "narration_dur": dur,
            "audio": os.path.join("W1_3", "_audio_ko", "%s.mp3" % scene).replace("\\", "/"),
        })
        t = scene_start + scene_len

    srt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "w1_3.ko.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_blocks))

    timeline_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timeline.json")
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump({"pad": PAD, "total": round(t, 3), "scenes": timeline}, f,
                   ensure_ascii=False, indent=2)

    print("SRT  ->", srt_path, "(%d 큐)" % idx)
    print("타임라인 ->", timeline_path)
    print("총 러닝타임 = %.2f초 (%.1f분)" % (t, t / 60))


if __name__ == "__main__":
    main()
