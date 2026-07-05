# -*- coding: utf-8 -*-
"""blender_face3d.py — 얼굴 요소(눈·입·머리)를 머리 본에 3D로 parent → 머리와 함께 움직임.
그 뒤 라인아트 렌더. 덮어씌우기(2D)가 아니라 진짜 부착. 사용:
  python blender_face3d.py <fbx> <out_dir> <res> <stride>
"""
import bpy, os, sys, math
from mathutils import Vector

FBX = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "scratch/mocap/char_walk.fbx")
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else "scratch/face3d")
RES = int(sys.argv[3]) if len(sys.argv) > 3 else 640
STRIDE = int(sys.argv[4]) if len(sys.argv) > 4 else 4
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX)
scene = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
scene.frame_set(scene.frame_start)
bpy.context.view_layer.update()

# 머리 본 월드 위치
hb_name = next(b.name for b in arm.pose.bones if b.name.lower().endswith("head"))
hb = arm.pose.bones[hb_name]
head_pos = (arm.matrix_world @ hb.matrix).translation
# ★월드 머리 크기: 목(head_pos.z) 위 메시 정점들로 실제 크기 산출(본길이 단위 안 믿음)
deps0 = bpy.context.evaluated_depsgraph_get()
hv = []
for o in bpy.data.objects:
    if o.type == "MESH" and o.name.startswith("Beta"):
        oe = o.evaluated_get(deps0)
        for v in oe.data.vertices:
            w = oe.matrix_world @ v.co
            if w.z > head_pos.z + 0.005:
                hv.append(w)
hx = [v.x for v in hv]; hy = [v.y for v in hv]; hz = [v.z for v in hv]
head_top = max(hz)
center = Vector((sum(hx)/len(hx), sum(hy)/len(hy), (head_pos.z + head_top)/2))
Rr = max((max(hx)-min(hx))/2, (head_top - head_pos.z)/2)  # 월드 머리 반경
fwd = Vector((0, -1, 0)); right = Vector((1, 0, 0)); up = Vector((0, 0, 1))
print(f"HEAD center={tuple(round(x,3) for x in center)} Rr={Rr:.3f}")

# 재질
def mat(name, col):
    m = bpy.data.materials.new(name); m.diffuse_color = (*col, 1); m.use_nodes = False; return m
ink = mat("ink", (0.02, 0.02, 0.02))
orange = mat("orange", (0.91, 0.49, 0.23))

_hb_bind = (arm.matrix_world @ hb.matrix).copy()          # 바인드 시점 머리 본 월드행렬
def add_ball(loc, r, material, flat_z=1.0, name="e"):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=16, ring_count=8)
    o = bpy.context.object; o.name = name
    o.scale.z *= flat_z
    o.data.materials.clear(); o.data.materials.append(material)
    # Child Of 제약: 머리 본을 따라감(월드 위치 유지) — tail 오프셋 문제 없음
    con = o.constraints.new("CHILD_OF")
    con.target = arm; con.subtarget = hb_name
    con.inverse_matrix = _hb_bind.inverted()
    return o

# ★얼굴 요소(표정용): 눈·코·입·귀+머리. 머리 표면에 밀착(fwd~0.95, 작게) → 머리 젖혀도 안 떨어짐
eye_r = Rr * 0.11
skin = mat("skin", (0.97, 0.965, 0.955))
for sx in (-1, 1):
    add_ball(center + fwd*Rr*0.95 + right*(sx*Rr*0.30) + up*Rr*0.10, eye_r, ink, 1.0, f"eye{sx}")
add_ball(center + fwd*Rr*1.0 - up*Rr*0.06, Rr*0.07, ink, 1.0, "nose")         # 코(앞 작은 점)
add_ball(center + fwd*Rr*0.95 - up*Rr*0.30, Rr*0.16, ink, 0.4, "mouth")       # 입(납작)
for sx in (-1, 1):
    add_ball(center + right*(sx*Rr*0.88) + up*Rr*0.0, Rr*0.14, skin, 0.7, f"ear{sx}")  # 귀
add_ball(center + up*Rr*0.9 - fwd*Rr*0.15, Rr*0.42, orange, 1.0, "bun")       # 머리묶음(정수리에 밀착)

# ── 라인 렌더 ──
meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("Beta", "Alpha", "mesh"))]
body = [o for o in bpy.data.objects if o.type == "MESH" and o.name not in ("eye-1","eye1","mouth","bun","hair")]
white = mat("w", (0.97, 0.965, 0.955))
for o in bpy.data.objects:
    if o.type == "MESH" and o.name.startswith("Beta"):
        o.data.materials.clear(); o.data.materials.append(white)

# 카메라
deps = bpy.context.evaluated_depsgraph_get()
mn = Vector((1e9,)*3); mx = Vector((-1e9,)*3)
for o in bpy.data.objects:
    if o.type == "MESH" and o.name.startswith("Beta"):
        oe = o.evaluated_get(deps)
        for v in oe.bound_box:
            w = oe.matrix_world @ Vector(v)
            mn = Vector((min(mn[i], w[i]) for i in range(3))); mx = Vector((max(mx[i], w[i]) for i in range(3)))
c = (mn + mx)/2; height = max(mx.z-mn.z, 0.1)
camd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", camd)
scene.collection.objects.link(cam); scene.camera = cam
cam.location = (c.x, c.y - height*1.7, c.z + height*0.15); cam.rotation_euler = (math.radians(90), 0, 0)
camd.type = "ORTHO"; camd.ortho_scale = height*1.45
scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.light = "FLAT"; sh.color_type = "MATERIAL"          # 재질색(눈검정·머리주황) 사용
sh.show_object_outline = True; sh.object_outline_color = (0.02, 0.02, 0.02)
scene.display.render_aa = "8"; scene.view_settings.view_transform = "Standard"
world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = False; world.color = (0.955, 0.95, 0.94)
scene.render.resolution_x = RES; scene.render.resolution_y = int(RES*1.35)
scene.render.image_settings.file_format = "PNG"
count = 0
for f in range(scene.frame_start, scene.frame_end+1, STRIDE):
    scene.frame_set(f)
    scene.render.filepath = os.path.join(OUT, f"frame_{count:04d}.png")
    bpy.ops.render.render(write_still=True); count += 1
print(f"FACE3D_DONE {count} -> {OUT}")
