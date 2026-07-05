# -*- coding: utf-8 -*-
"""bvh_to_charang.py — 무료 모션캡처(BVH)를 캐릭터랑 스켈레톤 동작으로 변환.
BVH 파싱→FK(3D 관절)→2D 투영(정면)→60x80 단위 매핑→anim_sequences 저장/캐릭터랑 재생.
사용: python bvh_to_charang.py scratch/mocap/test_freebvh.bvh walk_mocap [front|side]
"""
import os, sys, json, sqlite3
import numpy as np
from bvh import Bvh

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")

# Mixamo/CMU 관절 이름 → 캐릭터랑 관절
def find(names, *cands):
    for c in cands:
        for n in names:
            if n.lower().endswith(c.lower()) or n.lower() == c.lower():
                return n
    return None


def _rot(axis, deg):
    r = np.radians(deg); c, s = np.cos(r), np.sin(r)
    if axis == "X": return np.array([[1,0,0],[0,c,-s],[0,s,c]])
    if axis == "Y": return np.array([[c,0,s],[0,1,0],[-s,0,c]])
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])


def _children_map(mocap):
    names = mocap.get_joints_names()
    ch = {n: [] for n in names}
    for n in names:
        try:
            p = mocap.joint_parent(n)
            if p is not None and getattr(p, "name", None) in ch:
                ch[p.name].append(n)
        except Exception:
            pass
    return ch


def fk_positions(mocap, frame, chmap):
    """한 프레임의 모든 관절 3D 월드좌표 {joint: (x,y,z)}."""
    pos = {}
    def walk(joint, pT, pR):
        off = np.array([float(x) for x in mocap.joint_offset(joint)])
        chans = mocap.joint_channels(joint)
        vals = mocap.frame_joint_channels(frame, joint, chans)
        t = np.zeros(3); R = np.eye(3); vi = 0
        for ch in chans:
            v = vals[vi]; vi += 1
            if ch.endswith("position"):
                idx = {"X":0,"Y":1,"Z":2}[ch[0]]; t[idx] = v
            else:
                R = R @ _rot(ch[0], v)
        world_pos = pT + pR @ (off + t)
        world_R = pR @ R
        pos[joint] = world_pos
        for child in chmap.get(joint, []):
            walk(child, world_pos, world_R)
    root = mocap.get_joints_names()[0]
    walk(root, np.zeros(3), np.eye(3))
    return pos


def convert(bvh_path, seq_name, view="front", stride=2):
    mocap = Bvh(open(bvh_path).read())
    names = mocap.get_joints_names()
    JM = {
        "head": find(names, "Head"), "chest": find(names, "Spine2", "Spine1", "Chest"),
        "body": find(names, "Spine", "Spine1"), "pelvis": find(names, "Hips", "Pelvis"),
        "elbowLeft": find(names, "LeftForeArm", "LeftElbow"), "handLeft": find(names, "LeftHand"),
        "elbowRight": find(names, "RightForeArm", "RightElbow"), "handRight": find(names, "RightHand"),
        "kneeLeft": find(names, "LeftLeg", "LeftKnee"), "feetLeft": find(names, "LeftFoot", "LeftToeBase"),
        "kneeRight": find(names, "RightLeg", "RightKnee"), "feetRight": find(names, "RightFoot", "RightToeBase"),
    }
    miss = [k for k, v in JM.items() if v is None]
    if miss:
        print("매핑 실패:", miss); print("관절:", names[:20]); return None
    nf = mocap.nframes
    chmap = _children_map(mocap)
    frames = []
    for f in range(0, nf, stride):
        P = fk_positions(mocap, f, chmap)
        # 2D 투영: front=(X,Y), side=(Z,Y). Y=위 → 이미지 y는 아래로 뒤집기
        def proj(name):
            p = P[JM[name]]
            u = p[0] if view == "front" else p[2]
            return (u, -p[1])
        pts = {k: proj(k) for k in JM}
        frames.append(pts)
    # 정규화: 전체 프레임 통해 키(머리~발) 기준 60x80 단위로. Mixamo 좌우=화면 반대 → x 미러
    allx = [p[0] for fr in frames for p in fr.values()]
    ally = [p[1] for fr in frames for p in fr.values()]
    y0, y1 = min(ally), max(ally)
    H = (y1 - y0) or 1
    scale = 58.0 / H                      # 캐릭터 세로 ~58단위
    cx = (min(allx) + max(allx)) / 2
    norm = []
    for fr in frames:
        d = {}
        for k, (x, y) in fr.items():
            nx = 30 + (cx - x) * scale     # x 미러(30 중심)
            ny = 8 + (y - y0) * scale
            d[k] = (round(nx, 2), round(ny, 2))
        norm.append((d, 0.0))              # (joints, turn=0)
    # DB 저장
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS anim_mocap(id INTEGER PRIMARY KEY, seq_name TEXT UNIQUE, frames_json TEXT, source TEXT, updated_at TEXT)")
    cur.execute("INSERT OR REPLACE INTO anim_mocap(seq_name,frames_json,source,updated_at) VALUES (?,?,?,datetime('now'))",
                (seq_name, json.dumps([f[0] for f in norm]), os.path.basename(bvh_path)))
    con.commit(); con.close()
    print(f"{seq_name}: {len(norm)}프레임 저장 (source={os.path.basename(bvh_path)}, view={view})")
    return norm


def preview(char_key, seq_name, cols=8):
    import characterang as ca
    from PIL import Image
    ca.extract_head(char_key, os.path.join(ROOT, "assets", "graphics", "poses", "stickman_zw_base.png"))
    con = sqlite3.connect(DB)
    r = con.execute("SELECT frames_json FROM anim_mocap WHERE seq_name=?", (seq_name,)).fetchone()
    con.close()
    frames_j = json.loads(r[0])
    idxs = np.linspace(0, len(frames_j)-1, cols).astype(int)
    ims = [ca.render(char_key, frames_j[i], H=280, turn=0.0) for i in idxs]
    w, h = ims[0].size
    strip = Image.new("RGB", (w*len(ims), h), (245, 244, 240))
    for i, im in enumerate(ims):
        bg = Image.new("RGB", (w, h), (245, 244, 240)); bg.paste(im, (0, 0), im); strip.paste(bg, (i*w, 0))
    out = os.path.join(ROOT, "scratch", f"_mocap_{seq_name}.png")
    strip.save(out); print("preview ->", out)


if __name__ == "__main__":
    bvh = sys.argv[1] if len(sys.argv) > 1 else "scratch/mocap/test_freebvh.bvh"
    name = sys.argv[2] if len(sys.argv) > 2 else "walk_mocap"
    view = sys.argv[3] if len(sys.argv) > 3 else "front"
    convert(bvh, name, view=view)
    preview("zolla_girl", name)
