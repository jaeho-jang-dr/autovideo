#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MD-003 (거북목 과학) 에피소드의 시나리오를 파싱하여 content.db에 등록한다.
"""
import os
import sqlite3
import sys
import re

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content.db")
SCENARIO_PATH = r"d:\Entertainments\DevEnvironment\autovideo\turtle_neck_science\scenario.txt"

def parse_scenario(scenario_path):
    scenes = []
    if not os.path.exists(scenario_path):
        print(f"Error: Scenario path not found: {scenario_path}")
        return scenes
        
    with open(scenario_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split by scenes [Scene X]
    raw_blocks = re.split(r'\[Scene\s+(\d+)\]', content, flags=re.IGNORECASE)
    
    for i in range(1, len(raw_blocks), 2):
        scene_id = int(raw_blocks[i])
        block_text = raw_blocks[i+1]
        
        # Extract text, text_en, image, motion
        text_match = re.search(r'text:\s*(.*)', block_text, re.IGNORECASE)
        text_en_match = re.search(r'text_en:\s*(.*)', block_text, re.IGNORECASE)
        image_match = re.search(r'image:\s*(.*)', block_text, re.IGNORECASE)
        motion_match = re.search(r'motion:\s*(.*)', block_text, re.IGNORECASE)
        
        text = text_match.group(1).strip() if text_match else ""
        text_en = text_en_match.group(1).strip() if text_en_match else ""
        image_prompt = image_match.group(1).strip() if image_match else ""
        veo_prompt = motion_match.group(1).strip() if motion_match else ""
        
        # motion_prompt에서 '::' 제거
        if veo_prompt.startswith("::"):
            veo_prompt = veo_prompt[2:].strip()
            
        scenes.append({
            "seq": scene_id,
            "script_kr": text,
            "script_en": text_en,
            "image_prompt": image_prompt,
            "veo_prompt": veo_prompt
        })
    return scenes

def estimate_duration(text_kr):
    return round(len(text_kr) / 7.0, 1)

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return
        
    scenes = parse_scenario(SCENARIO_PATH)
    if not scenes:
        print("No scenes parsed. Exiting.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    
    # MD-003의 기존 씬 삭제
    cur.execute("DELETE FROM scenes WHERE episode='MD-003'")
    
    total_duration = 0.0
    for s in scenes:
        dur = estimate_duration(s['script_kr'])
        total_duration += dur
        cur.execute(
            "INSERT INTO scenes(episode, seq, script_kr, script_en, image_prompt, veo_prompt, duration_sec) "
            "VALUES ('MD-003', ?, ?, ?, ?, ?, ?)",
            (s['seq'], s['script_kr'], s['script_en'], s['image_prompt'], s['veo_prompt'], dur)
        )
    
    # 에피소드 메타데이터 업데이트
    # status -> published, render_kr -> turtle_neck_science/turtle_neck_science.mp4, runtime_sec -> total_duration
    runtime = int(round(total_duration))
    cur.execute(
        "UPDATE episodes SET status='published', render_kr='turtle_neck_science/turtle_neck_science.mp4', runtime_sec=? "
        "WHERE code='MD-003'", (runtime,)
    )
    
    conn.commit()
    conn.close()
    
    print(f"[OK] MD-003 에피소드 씬 {len(scenes)}개 동기화 완료 (추정 런타임: {runtime}초)")
    print("[OK] MD-003 에피소드 status -> published 업데이트 완료")

if __name__ == "__main__":
    main()
