# -*- coding: utf-8 -*-
"""scenario.txt 의 25씬 제작정보를 content.db (video_projects/video_clips)에 미리 적재.
영상 바이너리는 저장하지 않고 경로/이름/프롬프트 등 제작정보만 링크 저장."""
import os, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "channel"))
import content_db as cdb
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

PROJECT = "pianoduo"
PDIR = os.path.join(ROOT, "pianoduo")
HV = os.path.join(ROOT, "home_vocab")
SCENARIO = os.path.join(PDIR, "scenario.txt")
CHUNKS = [[1], [2,3,4,5,6], [7,8,9,10,11], [12,13,14,15],
          [16,17,18], [19,20], [21,22,23,24], [25]]
ANCHOR = {k: os.path.join(HV, f"injun_jieun_{k}.png")
          for k in ("piano_stand","piano_back","piano_front","piano_side")}

def chunk_of(n):
    for i, g in enumerate(CHUNKS):
        if n in g: return i
    return -1

def main():
    pat = re.compile(r"\[Scene\s+(\d+)\s*\|\s*ref=([A-Za-z_]+)\s*\]\s*(.*)", re.I)
    scenes = {}
    for line in open(SCENARIO, encoding="utf-8"):
        m = pat.match(line.strip())
        if m: scenes[int(m.group(1))] = (m.group(2).strip(), m.group(3).strip())

    cdb.upsert_project(PROJECT, title_kr="인준·지은 피아노 연탄 연주",
        description="four-hands 피아노 연탄곡 25씬 / 2분30초 (v2 재작업)",
        local_dir=PDIR, final_path=os.path.join(PDIR, "pianoduo.mp4"),
        bgm_path=os.path.join(PDIR, "pianoduo_bgm.wav"),
        n_scenes=len(scenes), status="generating",
        notes="영상 바이너리는 로컬/유튜브에만, 제작정보는 DB에 링크 저장")

    for n in sorted(scenes):
        ref_tag, motion = scenes[n]
        is_prev = ref_tag.lower() == "prev"
        base = (os.path.join(PDIR, f"scene_{n-1}_last.png") if is_prev
                else ANCHOR.get(ref_tag, ""))
        mp4 = os.path.join(PDIR, f"scene_{n}.mp4")
        last = os.path.join(PDIR, f"scene_{n}_last.png")
        cdb.log_clip(PROJECT, n,
            scene_name=f"{PROJECT}_scene_{n}", chunk=chunk_of(n),
            ref_anchor=ref_tag, base_image=base, motion_prompt=motion,
            image_prompt=ref_tag,
            transition_in=("last_frame" if is_prev else "fast"),
            file_path=mp4 if os.path.exists(mp4) else None,
            last_frame_path=last if os.path.exists(last) else None,
            status="planned",
            distortion_check="needs_redo")  # v2 재작업 대상
    print(f"[OK] {len(scenes)}개 씬 제작정보 적재 완료 -> content.db")

if __name__ == "__main__":
    main()
