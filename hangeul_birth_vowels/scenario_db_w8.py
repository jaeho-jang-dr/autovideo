#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""scenario_db_w8.py — 초급 8주차 "숫자·날짜·시간" 졸라맨 영상 → content.db.
캐릭터 졸라맨(stickman_zm_*). 11포즈 순환, 왼손 가리키기. 흔들림 0.
재실행: python hangeul_birth_vowels/scenario_db_w8.py
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
EP = "KO-W08"
PROJECT = "hangeul_w8_stickman"
LOCAL_DIR = os.path.join(ROOT, "hangeul_birth_vowels")
SCENARIO = os.path.join(ROOT, "scratch", "w8_scenario.json")

STYLE = {
    "look": "ZOLLA-MAN (zollaman, solid black head) ink line-art on cream→pastel radial bg",
    "method": "flat-layered compositing + zolla-man pose rotation (no idle shake)",
    "narration": "edge-tts SunHi female, 1.1x; DB number clips boosted; bilingual KR/EN",
    "font": "C:/Windows/Fonts/malgun.ttf", "canvas": [1280, 720],
}

GESTURES = {
    1:  ["zm_waving", "zm_cheering", "zm_base"],
    2:  ["zm_sitting", "zm_reading", "zm_thinking"],
    3:  ["zm_point_l", "zm_base", "zm_clapping"],
    4:  ["zm_clapping", "zm_point_l", "zm_base"],
    5:  ["zm_point_l", "zm_base", "zm_thinking"],
    6:  ["zm_base", "zm_point_l", "zm_clapping"],
    7:  ["zm_thinking", "zm_point_l", "zm_base"],
    8:  ["zm_point_l", "zm_studying", "zm_base"],
    9:  ["zm_studying", "zm_point_l", "zm_cheering"],
    10: ["zm_thinking", "zm_point_l", "zm_base"],
    11: ["zm_jumping", "zm_cheering", "zm_clapping"],
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
         "한국어 숫자는 왜 두 가지일까?",
         "졸라맨과 함께 고유어·한자어 숫자, 요일, 시간 말하기를 배운다 (초급 8주차).",
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
        (PROJECT, "숫자·날짜·시간 (졸라맨 · 초급 8주차)",
         "훈민정음 앱 초급 8주차. 졸라맨이 11포즈를 순환하며 고유어·한자어 숫자, 요일, 시간을 설명, 이중언어.",
         LOCAL_DIR, len(scenes), runtime, "scripting",
         f"episode={EP}; character=zolla-man; rotating poses; narration KR/EN"))

    con.commit()
    print(f"episode {EP}: {len(scenes)} scenes, runtime ~{runtime}s ({runtime/60:.1f}min)")
    con.close()


if __name__ == "__main__":
    main()
