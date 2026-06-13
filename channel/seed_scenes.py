#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
발행 완료된 에피소드의 컷 단위 대본(scenes)을 content.db에 시드한다.

웹사이트의 한/영 대조 학습 뷰어(Side-by-Side)가 이 데이터를 읽으므로,
한국어 나레이션 원본(make_video_hypnosis.py의 SCENES)과 동일한 의미의
영어 번역을 seq 순서대로 짝지어 넣는다.

사용법:
    python channel/seed_scenes.py        # MD-000 씬 시드(재실행 안전: 덮어쓰기)
"""
import os
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content.db")

# (seq, script_kr, script_en) — 한국어는 실제 발행본 나레이션, 영어는 동일 의미 번역.
MD_000_SCENES = [
    (1,
     "천천히 회전하는 회중시계를 바라봅니다. 최면술사의 부드러운 목소리를 따라가다 보면, 어느새 깊은 몰입 상태에 빠지게 됩니다.",
     "You gaze at a slowly spinning pocket watch. As you follow the hypnotist's soft voice, you slip almost unknowingly into a deep state of absorption."),
    (2,
     "많은 이들이 최면을 단순한 마술쇼나 타인을 마음대로 조종하는 기이한 눈속임으로 생각하곤 합니다.",
     "Many people think of hypnosis as a mere magic show, or a bizarre trick for bending other people to one's will."),
    (3,
     "하지만 과연 이 최면술은 대중의 인식처럼 실제로 우리 뇌와 몸에 효과가 있는 과학적 현상일까요?",
     "But is hypnosis really a scientific phenomenon that affects our brain and body, the way popular belief assumes?"),
    (4,
     "최면의 기원은 18세기 오스트리아의 의사 프란츠 안톤 메스머의 황당한 주장으로 거슬러 올라갑니다.",
     "The origins of hypnosis trace back to the outlandish claims of an 18th-century Austrian physician, Franz Anton Mesmer."),
    (5,
     "그는 우주로부터 흐르는 눈에 보이지 않는 힘인 '동물 자기'를 조절해 만병을 고칠 수 있다고 선전했습니다.",
     "He proclaimed that by manipulating an invisible force flowing from the cosmos — \"animal magnetism\" — he could cure every illness."),
    (6,
     "하지만 그의 화려한 치료실과 신비주의 치료법은 곧 프랑스 왕실의 큰 의심을 사게 되었습니다.",
     "But his lavish treatment rooms and mystical cures soon drew deep suspicion from the French royal court."),
    (7,
     "이에 따라 프랑스 왕실은 벤자민 프랭클린을 필두로 당대 최고의 과학자들로 구성된 위원회를 소집했습니다.",
     "In response, the French crown convened a commission of the era's finest scientists, led by Benjamin Franklin."),
    (8,
     "그들은 과학사 최초로 환자의 눈을 가리고 진짜 자석인 척 속이는 '맹검 실험'을 최초로 시도했습니다.",
     "They ran the first blind experiment in scientific history — blindfolding patients and deceiving them about whether a real magnet was even present."),
    (9,
     "실험 결과, 환자가 에너지가 흐른다고 착각했을 때만 몸이 반응했고, 동물 자기는 실체가 없는 사기로 판명났습니다.",
     "The body reacted only when patients believed energy was flowing — and animal magnetism was exposed as a baseless fraud."),
    (10,
     "비록 사기극으로 끝났지만, 이는 인간의 상상력과 기대가 몸에 반응을 일으키는 '플라시보 효과'의 시초가 되었습니다.",
     "Though it ended as a hoax, it marked the dawn of the \"placebo effect\" — proof that imagination and expectation can stir real bodily responses."),
    (11,
     "그 뒤 19세기 의사 제임스 브레이드가 나타나 최면을 마법이나 종교가 아닌 신경 생리학적 관점으로 재정의했습니다.",
     "Later, the 19th-century physician James Braid redefined hypnosis not as magic or religion, but through the lens of neurophysiology."),
    (12,
     "그는 특정 물체에 고도로 주의를 집중하면, 뇌가 일시적인 신경성 수면과 강한 몰입 상태에 빠진다는 사실을 밝혀냈습니다.",
     "He found that intense focus on a single object can send the brain into a temporary \"nervous sleep\" and a powerful state of absorption."),
    (13,
     "오늘날 현대 과학은 fMRI 장치를 이용해 최면 상태의 뇌를 들여다봄으로써 그 작동 기전을 완벽히 규명했습니다.",
     "Today, modern science has mapped its mechanism by peering into the hypnotized brain with fMRI scanners."),
    (14,
     "놀랍게도 최면 상태에서는 통증 신호를 인지하는 뇌의 전대상피질 부위 활성도가 극적으로 감소합니다.",
     "Remarkably, under hypnosis the activity of the anterior cingulate cortex — the region that registers pain — drops dramatically."),
    (15,
     "덕분에 현대 의학에서는 약물 마취가 어려운 환자들의 무마취 수술이나 극심한 심리 치료에 최면을 직접 활용하고 있습니다.",
     "Thanks to this, modern medicine now uses hypnosis directly for anesthesia-free surgery in patients who can't tolerate drugs, and for intensive psychotherapy."),
    (16,
     "최면은 초자연적 마법이 아닌, 인간의 상상력과 뇌 과학이 만들어내는 정교하고 강력한 우리 마음의 도구입니다.",
     "Hypnosis is no supernatural magic, but a precise and powerful tool of the mind — forged by human imagination and the science of the brain."),
]


def estimate_duration(text_kr):
    """한국어 나레이션 글자수 기반 대략적 컷 길이(초). 표시·합계용 근사값."""
    return round(len(text_kr) / 7.0, 1)


def seed_episode(cur, code, scenes):
    cur.execute("DELETE FROM scenes WHERE episode=?", (code,))
    total = 0.0
    for seq, kr, en in scenes:
        dur = estimate_duration(kr)
        total += dur
        cur.execute(
            "INSERT INTO scenes(episode, seq, script_kr, script_en, duration_sec) "
            "VALUES (?,?,?,?,?)",
            (code, seq, kr, en, dur))
    cur.execute("UPDATE episodes SET runtime_sec=? WHERE code=?",
                (int(round(total)), code))
    return len(scenes), int(round(total))


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    n, runtime = seed_episode(cur, "MD-000", MD_000_SCENES)
    conn.commit()
    conn.close()
    print(f"[OK] MD-000 씬 {n}개 시드 (runtime ~{runtime}s)")


if __name__ == "__main__":
    main()
