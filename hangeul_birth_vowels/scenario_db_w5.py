#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scenario_db_w5.py — 훈민정음 앱 초급 5주차 "이중모음과 반모음 활주" 졸라걸 영상 시나리오 → content.db.
캐릭터 졸라걸(stickman_zw_*). 11포즈 순환(반복 최소화), 왼손 가리키기로 오른쪽 콘텐츠 지시. 흔들림 0.
재실행: python hangeul_birth_vowels/scenario_db_w5.py
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
EP = "KO-W05"
PROJECT = "hangeul_w5_stickman"
LOCAL_DIR = os.path.join(ROOT, "hangeul_birth_vowels")
SCENARIO = os.path.join(ROOT, "scratch", "w5_scenario.json")

STYLE = {
    "look": "ZOLLA-GIRL (zollanyeo, orange bun) ink line-art on cream→pastel radial bg",
    "method": "flat-layered PIL/MoviePy compositing + zolla-girl pose rotation (no idle shake)",
    "narration": "edge-tts SunHi female, 1.1x; DB pronunciation clips boosted; bilingual KR/EN",
    "font": "C:/Windows/Fonts/malgun.ttf", "canvas": [1280, 720],
}

# 졸라걸 11포즈 순환(연속 반복 금지). 콘텐츠 우측 → 왼손 가리키기 zw_point_l.
GESTURES = {
    1:  ["zw_waving", "zw_cheering", "zw_base"],
    2:  ["zw_sitting", "zw_reading", "zw_thinking"],
    3:  ["zw_thinking", "zw_point_l", "zw_base"],
    4:  ["zw_point_l", "zw_base", "zw_thinking"],
    5:  ["zw_thinking", "zw_point_l", "zw_base"],
    6:  ["zw_point_l", "zw_clapping", "zw_base"],
    7:  ["zw_base", "zw_point_l", "zw_raising_hand"],
    8:  ["zw_point_l", "zw_base", "zw_thinking"],
    9:  ["zw_thinking", "zw_point_l", "zw_base"],
    10: ["zw_point_l", "zw_clapping", "zw_base"],
    11: ["zw_point_l", "zw_thinking", "zw_base"],
    12: ["zw_studying", "zw_point_l", "zw_cheering"],
    13: ["zw_jumping", "zw_cheering", "zw_clapping"],
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
         "두 모음이 미끄러지면 한 소리?",
         "졸라걸과 함께 이중모음(ㅑㅕㅛㅠ ㅘㅝㅟㅚㅢ)과 반모음 활주(y·w 활음)를 배운다 (초급 5주차).",
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
        (PROJECT, "이중모음과 반모음 활주 (졸라걸 · 초급 5주차)",
         "훈민정음 앱 초급 5주차. 졸라걸이 11포즈를 순환하며 이중모음·반모음 활주를 설명, 이중언어.",
         LOCAL_DIR, len(scenes), runtime, "scripting",
         f"episode={EP}; character=zolla-girl(zollanyeo); rotating poses + left-hand point; narration KR/EN"))

    con.commit()
    print(f"episode {EP}: {len(scenes)} scenes, runtime ~{runtime}s ({runtime/60:.1f}min)")
    con.close()


if __name__ == "__main__":
    main()
