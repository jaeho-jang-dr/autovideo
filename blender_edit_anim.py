# -*- coding: utf-8 -*-
"""blender_edit_anim.py — Mixamo 애니(FBX)를 '스크립트로 편집'해 새 동작 생성 + 라인렌더.
본 회전 fcurve를 프로그램으로 수정 → 다른 동작. 사용:
  python blender_edit_anim.py <fbx> <out_dir> <res> <stride> <edit>
  edit: raise_arms | wave | none
"""
import bpy, os, sys, math
from mathutils import Vector, Quaternion

FBX = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "scratch/mocap/char_walk.fbx")
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else "scratch/edit")
RES = int(sys.argv[3]) if len(sys.argv) > 3 else 640
STRIDE = int(sys.argv[4]) if len(sys.argv) > 4 else 3
EDIT = sys.argv[5] if len(sys.argv) > 5 else "raise_arms"
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX)
scene = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")

# ── 애니 편집: 본 rotation_quaternion fcurve를 프로그램으로 수정 ──
def get_channelbag():
    act = arm.animation_data.action; slot = arm.animation_data.action_slot
    for lay in act.layers:
        for st in lay.strips:
            return st.channelbag(slot)
cb = get_channelbag()

def quat_fcurves(bone):
    dp = f'pose.bones["{bone}"].rotation_quaternion'
    fcs = {fc.array_index: fc for fc in cb.fcurves if fc.data_path == dp}
    return [fcs.get(i) for i in range(4)]

def edit_bone_rotation(bone, offset_quat):
    """본의 모든 키프레임 쿼터니언에 offset을 곱해 회전 추가(=동작 변경)."""
    fcs = quat_fcurves(bone)
    if any(f is None for f in fcs): return
    n = len(fcs[0].keyframe_points)
    for k in range(n):
        w, x, y, z = (fcs[i].keyframe_points[k].co[1] for i in range(4))
        q = Quaternion((w, x, y, z)) @ offset_quat
        for i, val in enumerate((q.w, q.x, q.y, q.z)):
            fcs[i].keyframe_points[k].co[1] = val
            fcs[i].keyframe_points[k].handle_left[1] = val
            fcs[i].keyframe_points[k].handle_right[1] = val
    for f in fcs: f.update()

if EDIT == "raise_arms":
    # 양팔 들어올리기(어깨 본 로컬축 회전) — 좌우 반대 부호
    edit_bone_rotation("mixamorig:LeftArm", Quaternion((0, 0, 1), math.radians(75)))
    edit_bone_rotation("mixamorig:RightArm", Quaternion((0, 0, 1), math.radians(-75)))
elif EDIT == "wave":
    edit_bone_rotation("mixamorig:RightArm", Quaternion((0, 0, 1), math.radians(-110)))
    edit_bone_rotation("mixamorig:RightForeArm", Quaternion((1, 0, 0), math.radians(-40)))

# ── 라인 렌더(Workbench 외곽선) ──
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
white = bpy.data.materials.new("w"); white.diffuse_color = (0.97, 0.965, 0.955, 1)
for o in meshes:
    o.data.materials.clear(); o.data.materials.append(white)
scene.frame_set(scene.frame_start)
deps = bpy.context.evaluated_depsgraph_get()
mn = Vector((1e9,)*3); mx = Vector((-1e9,)*3)
for o in meshes:
    oe = o.evaluated_get(deps)
    for v in oe.bound_box:
        w = oe.matrix_world @ Vector(v)
        mn = Vector((min(mn[i], w[i]) for i in range(3))); mx = Vector((max(mx[i], w[i]) for i in range(3)))
center = (mn + mx) / 2; height = max(mx.z - mn.z, 0.1)
camd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", camd)
scene.collection.objects.link(cam); scene.camera = cam
cam.location = (center.x, center.y - height*1.7, center.z + height*0.15)
cam.rotation_euler = (math.radians(90), 0, 0)
camd.type = "ORTHO"; camd.ortho_scale = height * 1.5
scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.light = "FLAT"; sh.color_type = "SINGLE"; sh.single_color = (0.97, 0.965, 0.955)
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
print(f"EDIT_DONE edit={EDIT} {count} frames -> {OUT}")
