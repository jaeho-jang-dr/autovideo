#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scenario_db_w3.py — 훈민정음 앱 초급 3주차 "거센소리와 된소리" 졸라맨 영상 시나리오 → content.db.
나레이션 초안은 Gemini가 작성(scratch/w3_scenario.json), 감독(Claude)이 검수 + 연출(포즈/제스처) 부여.
캐릭터는 **졸라맨**(꽉 찬 검은 머리). 캐릭터가 사람처럼 손짓하며 설명하도록 씬마다 gesture_seq 부여.
~7분, 16씬. 거센소리(ㅋㅌㅍㅊ·가획) + 된소리(ㄲㄸㅃㅆㅉ·쌍자음) + 휴지 실험 + 최소대립쌍.
재실행: python hangeul_birth_vowels/scenario_db_w3.py
"""
import os
import sys
import json
import sqlite3

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "channel", "content.db")
EP = "KO-W03"
PROJECT = "hangeul_w3_stickman"
LOCAL_DIR = os.path.join(ROOT, "hangeul_birth_vowels")
SCENARIO = os.path.join(ROOT, "scratch", "w3_scenario_v3.json")   # v2 확장본 + 교정(Jay 자기소개·조사 받침)

STYLE = {
    "look": "ZOLLA-MAN (solid black head, white face) line-art on cream→pastel radial bg",
    "method": "flat-layered PIL/MoviePy compositing + per-character idle motion & gesture swaps",
    "narration": "edge-tts SunHi female, 1.1x; jamo/word spliced with DB pronunciation (tight gaps); bilingual KR/EN",
    "font": "C:/Windows/Fonts/malgun.ttf", "canvas": [1280, 720],
}

# seq -> 연출: 메인 졸라맨 제스처 시퀀스(사람처럼 차분히 손짓하며 설명). 캐릭터는 build_scene_objects_w3 에서 배치.
# 사용자 요청: 오른편 가리키기(zm_point_r/zm_pointing) 금지 — 가리킬 대상이 없음. 중립 설명 포즈만 사용.
GESTURES = {   # DB의 실제 졸라맨 포즈(zm_*) — 씬마다 차분한 손짓 전환(가리키기 없음)
    1:  ["zm_waving", "zm_cheering", "zm_base"],        # 인트로
    2:  ["zm_sitting", "zm_thinking", "zm_base"],       # 복습(앉아 회상)
    3:  ["zm_cheering", "zm_base", "zm_thinking"],      # 거센소리란(힘찬)
    4:  ["zm_base", "zm_thinking", "zm_base"],          # 가획
    5:  ["zm_thinking", "zm_base", "zm_thinking"],      # 가획 더
    6:  ["zm_base", "zm_thinking", "zm_cheering"],      # 발음연습 ㅋ
    7:  ["zm_thinking", "zm_base", "zm_thinking"],      # 발음연습 ㅌㅍㅊ
    8:  ["zm_cheering", "zm_base", "zm_thinking"],      # 된소리란(목 힘)
    9:  ["zm_base", "zm_thinking", "zm_base"],          # 쌍자음
    10: ["zm_thinking", "zm_base", "zm_thinking"],      # 쌍자음 더
    11: ["zm_base", "zm_thinking", "zm_cheering"],      # 발음연습 ㄲ
    12: ["zm_thinking", "zm_base", "zm_thinking"],      # 발음연습 ㄸㅃㅆㅉ
    13: ["zm_thinking", "zm_base", "zm_thinking"],      # 휴지 실험
    14: ["zm_thinking", "zm_base", "zm_cheering"],      # 비교+연습 개캐깨(통합)
    15: ["zm_cheering", "zm_clapping", "zm_waving"],    # 마무리(축하)
}


def main():
    data = json.load(open(SCENARIO, encoding="utf-8"))
    scenes = data["scenes"]
    con = sqlite3.connect(DB)
    cur = con.cursor()
    runtime = sum(s["duration_sec"] for s in scenes)
    nar_kr = "\n".join(s["script_kr"] for s in scenes)
    nar_en = "\n".join(s["script_en"] for s in scenes)

    cur.execute("DELETE FROM episodes WHERE code=?", (EP,))
    cur.execute(
        "INSERT INTO episodes (code, category, title_kr, title_en, hook_kr, logline_kr, status, "
        "runtime_sec, narration_kr, narration_en, style_profile, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?, datetime('now'))",
        (EP, "KO", data["title_ko"], data["title_en"],
         "휴지가 흔들리면 거센소리, 안 흔들리면 된소리?",
         "졸라맨과 함께 거센소리(ㅋㅌㅍㅊ)와 된소리(ㄲㄸㅃㅆㅉ)를 휴지 실험·최소대립쌍으로 배운다 (초급 3주차).",
         "scripting", runtime, nar_kr, nar_en, json.dumps(STYLE, ensure_ascii=False)))

    cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
    for s in scenes:
        seq = s["seq"]
        spec = {"pose": "stickman_" + GESTURES[seq][0], "gesture_seq": GESTURES[seq],
                "cap_ko": s["cap_ko"], "cap_en": s["cap_en"], "motion": "static",
                "visual_note": s.get("visual_note", "")}
        cur.execute(
            "INSERT INTO scenes (episode, seq, script_kr, script_en, image_prompt, veo_prompt, sfx, duration_sec) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (EP, seq, s["script_kr"], s["script_en"], json.dumps(spec, ensure_ascii=False), "", None, s["duration_sec"]))

    cur.execute("DELETE FROM video_projects WHERE name=?", (PROJECT,))
    cur.execute(
        "INSERT INTO video_projects (name, title_kr, description, local_dir, n_scenes, runtime_sec, status, notes, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?, datetime('now'), datetime('now'))",
        (PROJECT, "거센소리와 된소리 (졸라맨 · 초급 3주차)",
         "훈민정음 앱 초급 3주차. 졸라맨 캐릭터가 사람처럼 손짓하며 거센소리·된소리를 설명, 이중언어.",
         LOCAL_DIR, len(scenes), runtime, "scripting",
         f"episode={EP}; character=zolla-man; dynamic gestures; narration draft=Gemini, reviewed by Claude"))

    con.commit()
    print(f"episode {EP}: {len(scenes)} scenes, runtime ~{runtime}s ({runtime/60:.1f}min)")
    con.close()


if __name__ == "__main__":
    main()
