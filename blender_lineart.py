# -*- coding: utf-8 -*-
"""blender_lineart.py — Mixamo 캐릭터 FBX(메시+애니)를 라인드로잉(흰몸+검은외곽선)으로 렌더.
Workbench 엔진(헤드리스 안정) + object outline. 사용:
  python blender_lineart.py <fbx> <out_dir> <res> <stride>
"""
import bpy, os, sys, math
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
FBX = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "scratch/mocap/char_walk.fbx")
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else "scratch/lineart")
RES = int(sys.argv[3]) if len(sys.argv) > 3 else 540
STRIDE = int(sys.argv[4]) if len(sys.argv) > 4 else 1
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX)
scene = bpy.context.scene
meshes = [o for o in bpy.data.objects if o.type == "MESH"]

# 평평한 흰 재질
white = bpy.data.materials.new("flatwhite")
white.diffuse_color = (0.97, 0.965, 0.955, 1)
for o in meshes:
    o.data.materials.clear(); o.data.materials.append(white)

# 바운딩박스 → 카메라(정면 -Y에서, Z-up)
scene.frame_set(scene.frame_start)
deps = bpy.context.evaluated_depsgraph_get()
mn = Vector((1e9,)*3); mx = Vector((-1e9,)*3)
for o in meshes:
    oe = o.evaluated_get(deps)
    for v in oe.bound_box:
        w = oe.matrix_world @ Vector(v)
        mn = Vector((min(mn[i], w[i]) for i in range(3))); mx = Vector((max(mx[i], w[i]) for i in range(3)))
center = (mn + mx) / 2
height = max(mx.z - mn.z, 0.1)
cam_data = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam); scene.camera = cam
cam.location = (center.x, center.y - height*1.7, center.z)
cam.rotation_euler = (math.radians(90), 0, 0)
cam_data.lens = 50; cam_data.clip_end = height*10
# 살짝 여백 위해 ortho
cam_data.type = "ORTHO"; cam_data.ortho_scale = height * 1.25

# Workbench: 평면 흰 셰이딩 + 검은 외곽선 = 선화
scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.light = "FLAT"; sh.color_type = "SINGLE"; sh.single_color = (0.97, 0.965, 0.955)
sh.show_object_outline = True; sh.object_outline_color = (0.02, 0.02, 0.02)
scene.display.render_aa = "8"
scene.view_settings.view_transform = "Standard"
scene.render.film_transparent = False
# 흰 배경
world = bpy.data.worlds.new("W"); scene.world = world
world.use_nodes = False; world.color = (0.955, 0.95, 0.94)

scene.render.resolution_x = RES; scene.render.resolution_y = int(RES * 1.35)
scene.render.image_settings.file_format = "PNG"

f0, f1 = scene.frame_start, scene.frame_end
count = 0
for f in range(f0, f1 + 1, STRIDE):
    scene.frame_set(f)
    scene.render.filepath = os.path.join(OUT, f"frame_{count:04d}.png")
    bpy.ops.render.render(write_still=True)
    count += 1
print(f"LINEART_DONE {count} frames -> {OUT}")
