# -*- coding: utf-8 -*-
"""fbx_to_charang.py — Mixamo FBX 동작을 캐릭터랑 스켈레톤+머리회전으로 변환(bpy 사용).
FBX 임포트→본 월드좌표 프레임별 추출→2D 투영→60x80 매핑 + 머리/몸 회전(turn) 추출→anim_mocap 저장.
사용: python fbx_to_charang.py scratch/mocap/Walking.fbx walk_mx [front|side]
"""
import os, sys, json, sqlite3, math
import numpy as np
import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")


def _find(bones, *cands):
    for c in cands:
        for b in bones:
            if b.lower().endswith(c.lower()):
                return b
    return None


def convert(fbx, seq_name, view="front", stride=2):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.abspath(fbx))
    arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
    if arm is None:
        print("아마추어 없음"); return None
    scene = bpy.context.scene
    bones = [b.name for b in arm.pose.bones]
    JM = {
        "head": _find(bones, "Head"), "chest": _find(bones, "Spine2", "Spine1", "Chest"),
        "body": _find(bones, "Spine1", "Spine"), "pelvis": _find(bones, "Hips", "Pelvis"),
        "elbowLeft": _find(bones, "LeftForeArm"), "handLeft": _find(bones, "LeftHand"),
        "elbowRight": _find(bones, "RightForeArm"), "handRight": _find(bones, "RightHand"),
        "kneeLeft": _find(bones, "LeftLeg"), "feetLeft": _find(bones, "LeftFoot", "LeftToeBase"),
        "kneeRight": _find(bones, "RightLeg"), "feetRight": _find(bones, "RightFoot", "RightToeBase"),
    }
    neck = _find(bones, "Neck")
    miss = [k for k, v in JM.items() if v is None]
    if miss:
        print("본 매핑 실패:", miss, "| 본들:", bones[:16]); return None

    def wp(bone):                                    # 애니 적용된 본 월드 좌표(pose.matrix)
        pb = arm.pose.bones[bone]
        return arm.matrix_world @ pb.matrix.translation

    frames = []
    turns = []
    f0, f1 = scene.frame_start, scene.frame_end
    for f in range(f0, f1 + 1, stride):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        P = {k: wp(v) for k, v in JM.items()}
        # 몸 정면 방향: 골반 좌우축이 카메라를 향하는 정도로 turn 추정
        pb = arm.pose.bones[JM["pelvis"]]
        rmat = (arm.matrix_world @ pb.matrix).to_3x3()
        right = rmat @ Vector((1, 0, 0))            # 몸의 오른쪽 방향(월드)
        # 카메라=+Y(앞). 몸 오른쪽이 +X면 정면, +Z(카메라쪽 회전)면 옆.
        ang = math.atan2(right.y, right.x)          # 0=정면, ±90=옆
        turn = min(1.0, abs(ang) / (math.pi))       # 0정면~0.5옆~1뒤 근사
        # 2D 투영
        def proj(name):
            p = P[name]
            u = p.x if view == "front" else p.y
            return (u, p.z)                          # Blender Z=위
        frames.append({k: proj(k) for k in JM})
        turns.append(round(turn, 3))

    # 정규화 60x80
    allx = [p[0] for fr in frames for p in fr.values()]
    ally = [p[1] for fr in frames for p in fr.values()]
    y0, y1 = min(ally), max(ally)
    scale = 58.0 / ((y1 - y0) or 1)
    cx = (min(allx) + max(allx)) / 2
    norm = []
    for fr, tn in zip(frames, turns):
        d = {}
        for k, (x, y) in fr.items():
            nx = 30 + (x - cx) * scale
            ny = 8 + (y1 - y) * scale               # z위→이미지 아래로
            d[k] = (round(nx, 2), round(ny, 2))
        norm.append({"joints": d, "turn": tn})
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS anim_mocap(id INTEGER PRIMARY KEY, seq_name TEXT UNIQUE, frames_json TEXT, source TEXT, updated_at TEXT)")
    cur.execute("INSERT OR REPLACE INTO anim_mocap(seq_name,frames_json,source,updated_at) VALUES (?,?,?,datetime('now'))",
                (seq_name, json.dumps(norm), os.path.basename(fbx)))
    con.commit(); con.close()
    print(f"{seq_name}: {len(norm)}프레임 (turn 범위 {min(turns):.2f}~{max(turns):.2f}, source={os.path.basename(fbx)})")
    return norm


if __name__ == "__main__":
    fbx = sys.argv[1] if len(sys.argv) > 1 else "scratch/mocap/Walking.fbx"
    name = sys.argv[2] if len(sys.argv) > 2 else "walk_mx"
    view = sys.argv[3] if len(sys.argv) > 3 else "front"
    convert(fbx, name, view=view)
