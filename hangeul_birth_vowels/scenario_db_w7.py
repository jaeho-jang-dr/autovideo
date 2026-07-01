#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""scenario_db_w7.py — 초급 7주차 "인사말과 자기소개" 졸라걸 영상 → content.db.
캐릭터 졸라걸(stickman_zw_*). 11포즈 순환, 왼손 가리키기. 흔들림 0.
재실행: python hangeul_birth_vowels/scenario_db_w7.py
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
EP = "KO-W07"
PROJECT = "hangeul_w7_stickman"
LOCAL_DIR = os.path.join(ROOT, "hangeul_birth_vowels")
SCENARIO = os.path.join(ROOT, "scratch", "w7_scenario.json")

STYLE = {
    "look": "ZOLLA-GIRL (zollanyeo) ink line-art on cream→pastel radial bg",
    "method": "flat-layered compositing + zolla-girl pose rotation (no idle shake)",
    "narration": "edge-tts SunHi female, 1.1x; DB phrase clips boosted; bilingual KR/EN",
    "font": "C:/Windows/Fonts/malgun.ttf", "canvas": [1280, 720],
}

GESTURES = {
    1:  ["zw_waving", "zw_cheering", "zw_base"],
    2:  ["zw_sitting", "zw_reading", "zw_thinking"],
    3:  ["zw_point_l", "zw_base", "zw_thinking"],
    4:  ["zw_base", "zw_point_l", "zw_thinking"],
    5:  ["zw_point_l", "zw_clapping", "zw_base"],
    6:  ["zw_thinking", "zw_point_l", "zw_base"],
    7:  ["zw_raising_hand", "zw_point_l", "zw_base"],
    8:  ["zw_point_l", "zw_base", "zw_clapping"],
    9:  ["zw_base", "zw_point_l", "zw_thinking"],
    10: ["zw_point_l", "zw_studying", "zw_base"],
    11: ["zw_jumping", "zw_cheering", "zw_clapping"],
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
         "인사 한마디로 마음이 가까워진다",
         "졸라걸과 함께 필수 인사말과 '저는 ~입니다' 자기소개를 배운다 (초급 7주차).",
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
        (PROJECT, "인사말과 자기소개 (졸라걸 · 초급 7주차)",
         "훈민정음 앱 초급 7주차. 졸라걸이 11포즈를 순환하며 인사말·자기소개를 설명, 이중언어.",
         LOCAL_DIR, len(scenes), runtime, "scripting",
         f"episode={EP}; character=zolla-girl; rotating poses; narration KR/EN"))

    con.commit()
    print(f"episode {EP}: {len(scenes)} scenes, runtime ~{runtime}s ({runtime/60:.1f}min)")
    con.close()


if __name__ == "__main__":
    main()
