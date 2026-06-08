"""Bake a natural walk cycle onto HumanFigure_game.glb for Raylib."""
import math
import bpy
import mathutils

INPUT = "/workspace/Assets/Models/HumanFigure_game.glb"
OUTPUT = "/workspace/Assets/Models/HumanFigure_walk.glb"
FRAMES = 24

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=INPUT)
mesh = next(o for o in bpy.data.objects if o.type == "MESH")
bpy.context.view_layer.objects.active = mesh
mesh.select_set(True)

corners = [mesh.matrix_world @ mathutils.Vector(c) for c in mesh.bound_box]
min_v = mathutils.Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
max_v = mathutils.Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
center = (min_v + max_v) * 0.5
height = max_v.y - min_v.y
foot_y = min_v.y
width = max_v.x - min_v.x

bpy.ops.object.armature_add(enter_editmode=True, location=center)
arm = bpy.context.active_object
arm.name = "WalkRig"
eb = arm.data.edit_bones

root = eb[0]
root.name = "root"
root.head = (center.x, foot_y, center.z)
root.tail = (center.x, foot_y + height * 0.45, center.z)

hips = eb.new("hips")
hips.parent = root
hips.head = root.tail
hips.tail = (center.x, foot_y + height * 0.62, center.z)

spine = eb.new("spine")
spine.parent = hips
spine.head = hips.tail
spine.tail = (center.x, foot_y + height * 0.88, center.z)


def leg(name, side):
    hip_x = center.x + side * width * 0.18
    thigh = eb.new(f"{name}_thigh")
    thigh.parent = hips
    thigh.head = (hip_x, foot_y + height * 0.56, center.z)
    thigh.tail = (hip_x, foot_y + height * 0.34, center.z)
    shin = eb.new(f"{name}_shin")
    shin.parent = thigh
    shin.head = thigh.tail
    shin.tail = (hip_x, foot_y + height * 0.12, center.z)
    foot = eb.new(f"{name}_foot")
    foot.parent = shin
    foot.head = shin.tail
    foot.tail = (hip_x, foot_y + 0.01, center.z + side * 0.04)
    return thigh, shin, foot


leg("L", -1)
leg("R", 1)
bpy.ops.object.mode_set(mode="OBJECT")

for name in [b.name for b in arm.data.bones]:
    mesh.vertex_groups.new(name=name)


def weight_for_vertex(co):
    x, y, z = co.x, co.y, co.z
    weights = {}

    def add(name, w):
        if w > 0.001:
            weights[name] = weights.get(name, 0.0) + w

    y_norm = (y - foot_y) / max(height, 0.001)
    side = -1.0 if x < center.x else 1.0
    side_strength = min(1.0, abs(x - center.x) / max(width * 0.22, 0.01))

    add("root", max(0.0, 1.0 - y_norm * 1.2))
    add("hips", max(0.0, 1.0 - abs(y_norm - 0.58) * 4.0))
    add("spine", max(0.0, (y_norm - 0.62) * 2.5))

    if y_norm < 0.66:
        leg_prefix = "L" if side < 0 else "R"
        leg_w = min(1.0, max(0.35, side_strength * 1.35))
        if y_norm < 0.2:
            add(f"{leg_prefix}_foot", leg_w * 1.4)
        elif y_norm < 0.42:
            add(f"{leg_prefix}_shin", leg_w * 1.4)
        else:
            add(f"{leg_prefix}_thigh", leg_w * 1.4)

    total = sum(weights.values())
    if total < 0.001:
        weights = {"root": 1.0}
        total = 1.0
    return {k: v / total for k, v in weights.items()}


for vert in mesh.data.vertices:
    wts = weight_for_vertex(vert.co)
    for name, w in wts.items():
        mesh.vertex_groups[name].add([vert.index], w, "REPLACE")

mod = mesh.modifiers.new("Armature", "ARMATURE")
mod.object = arm
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
mesh.select_set(True)
bpy.ops.object.parent_set(type="ARMATURE")

bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = FRAMES
bpy.context.scene.render.fps = 24
pb = arm.pose.bones


def pose_leg(prefix, phase):
    """Forward/back leg swing only — no side roll (that caused the waddle)."""
    thigh = pb[f"{prefix}_thigh"]
    shin = pb[f"{prefix}_shin"]
    foot = pb[f"{prefix}_foot"]
    for bone in (thigh, shin, foot):
        bone.rotation_mode = "XYZ"
    thigh.rotation_euler = (math.radians(24.0) * phase, 0.0, 0.0)
    shin.rotation_euler = (math.radians(-36.0) * max(0.0, phase), 0.0, 0.0)
    foot.rotation_euler = (math.radians(6.0) * max(0.0, -phase), 0.0, 0.0)
    thigh.keyframe_insert("rotation_euler")
    shin.keyframe_insert("rotation_euler")
    foot.keyframe_insert("rotation_euler")


for f in range(1, FRAMES + 1):
    bpy.context.scene.frame_set(f)
    t = (f - 1) / FRAMES * math.pi * 2.0
    pb["hips"].location = (0.0, abs(math.sin(t * 2.0)) * height * 0.006, 0.0)
    pb["hips"].keyframe_insert("location")
    pb["spine"].rotation_euler = (math.radians(2.5) * math.sin(t), 0.0, 0.0)
    pb["spine"].keyframe_insert("rotation_euler")
    pose_leg("L", math.sin(t))
    pose_leg("R", math.sin(t + math.pi))

bpy.ops.export_scene.gltf(
    filepath=OUTPUT,
    export_format="GLB",
    export_animations=True,
    export_skins=True,
    export_def_bones=True,
    export_texcoords=True,
    export_materials="EXPORT",
    export_image_format="AUTO",
)
print("Wrote", OUTPUT)
