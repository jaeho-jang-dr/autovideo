# -*- coding: utf-8 -*-
"""kf_shots.tsv(읽기전용)에서 각 샷 장면설명을 추출 → kf_motions.tsv (key \t 모션프롬프트).
키프레임을 첫 프레임으로 애니메이션할 때 쓸 Veo 모션 프롬프트(카메라 무빙 + 실제 물리 동작)."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, "kf_shots.tsv")
OUT = os.path.join(HERE, "kf_motions.tsv")

SUFFIX = (" Bring this scene to life with gentle, subtle REAL physical motion and the camera movement "
          "described; people breathe and move naturally, cloth and light shift softly, smooth cinematic; "
          "NO sudden whole-frame shake, no flashing; no on-screen text, no watermark.")

def extract_desc(prompt):
    m = re.search(r"16:9 scene:\s*(.*?)\.\s*(cinematic semi-realistic|warm friendly modern)", prompt)
    return m.group(1).strip() if m else prompt

rows = []
for line in open(TSV, encoding="utf-8"):
    parts = line.rstrip("\n").split("\t")
    if len(parts) < 3: continue
    key, ref, prompt = parts[0], parts[1], parts[2]
    desc = extract_desc(prompt)
    rows.append((key, desc + "." + SUFFIX))

with open(OUT, "w", encoding="utf-8") as f:
    for key, mot in rows:
        f.write(f"{key}\t{mot}\n")
print(f"wrote {OUT}: {len(rows)} motions")
print("예시:", rows[0][0], "->", rows[0][1][:120], "...")
