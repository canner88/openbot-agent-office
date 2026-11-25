import bpy
import os
import sys
import math
import traceback

LOG_FILE = r"C:\Users\caner\OpenBot\Shared\3d-assets\chars_build.log"
sys.stdout = open(LOG_FILE, "w", buffering=1, encoding="utf-8")
sys.stderr = sys.stdout

OUT_DIR = r"C:\Users\caner\.agent-office\premium\models"
CHARS_DIR = r"C:\Users\caner\OpenBot\Shared\3d-assets\quaternius_chars\Universal Base Characters[Standard]\Base Characters\Godot - UE"
HAIR_DIR = r"C:\Users\caner\OpenBot\Shared\3d-assets\quaternius_chars\Universal Base Characters[Standard]\Hairstyles\Origin at 0\glTF (Godot)"
OUTFITS_DIR = r"C:\Users\caner\OpenBot\Shared\3d-assets\quaternius_outfits\Modular Character Outfits - Fantasy[Standard]\Exports\glTF (Godot-Unreal)\Outfits"
ANIM_GLB = r"C:\Users\caner\OpenBot\Shared\3d-assets\quaternius_anims\Universal Animation Library[Standard]\Unreal-Godot\UAL1_Standard.glb"
ANIM2_GLB = r"C:\Users\caner\OpenBot\Shared\3d-assets\ual2\UAL2_Standard.glb"

BONE_MAP = {
    "pelvis": "Pelvis",
    "Head": "head",
    "upperarm_l": "UpperArm_L",
    "hand_l": "Hand_L",
    "upperarm_r": "UpperArm_R",
    "hand_r": "Hand_R",
    "thigh_l": "Thigh_L",
    "foot_l": "Foot_L",
    "thigh_r": "Thigh_R",
    "foot_r": "Foot_R",
}

CHARACTERS = [
    ("Boss_Female_01", True, "Hair_Buns.gltf", (0.14, 0.16, 0.24, 1), (0.35, 0.35, 0.38, 1), (0.86, 0.70, 0.56, 1)),
    ("Boss_Male_01", False, "Hair_SimpleParted.gltf", (0.12, 0.14, 0.20, 1), (0.55, 0.55, 0.58, 1), (0.85, 0.69, 0.55, 1)),
    ("Business_Female_01", True, "Hair_Long.gltf", (0.45, 0.24, 0.38, 1), (0.22, 0.14, 0.09, 1), (0.88, 0.72, 0.58, 1)),
    ("Business_Female_02", True, "Hair_SimpleParted.gltf", (0.22, 0.38, 0.52, 1), (0.12, 0.10, 0.09, 1), (0.76, 0.56, 0.42, 1)),
    ("Business_Female_03", True, "Hair_Buns.gltf", (0.52, 0.30, 0.28, 1), (0.68, 0.52, 0.28, 1), (0.90, 0.75, 0.62, 1)),
    ("Business_Female_04", True, "Hair_Long.gltf", (0.26, 0.42, 0.40, 1), (0.15, 0.12, 0.10, 1), (0.62, 0.44, 0.32, 1)),
    ("Business_Male_01", False, "Hair_SimpleParted.gltf", (0.24, 0.28, 0.36, 1), (0.18, 0.12, 0.08, 1), (0.86, 0.70, 0.56, 1)),
    ("Business_Male_02", False, "Hair_Buzzed.gltf", (0.30, 0.34, 0.42, 1), (0.10, 0.09, 0.08, 1), (0.68, 0.48, 0.36, 1)),
    ("Business_Male_03", False, "Hair_Beard.gltf", (0.38, 0.26, 0.22, 1), (0.28, 0.18, 0.12, 1), (0.88, 0.72, 0.58, 1)),
    ("Business_Male_04", False, "Hair_SimpleParted.gltf", (0.22, 0.32, 0.28, 1), (0.55, 0.42, 0.22, 1), (0.84, 0.68, 0.54, 1)),
    ("Cleaner_Female_01", True, "Hair_BuzzedFemale.gltf", (0.20, 0.42, 0.32, 1), (0.16, 0.12, 0.10, 1), (0.82, 0.65, 0.50, 1)),
    ("Cleaner_Male_01", False, "Hair_Buzzed.gltf", (0.18, 0.38, 0.28, 1), (0.20, 0.16, 0.12, 1), (0.78, 0.60, 0.46, 1)),
    ("Developer_Female_01", True, "Hair_Long.gltf", (0.20, 0.34, 0.62, 1), (0.48, 0.20, 0.14, 1), (0.88, 0.72, 0.58, 1)),
    ("Developer_Female_02", True, "Hair_Buns.gltf", (0.34, 0.24, 0.56, 1), (0.12, 0.10, 0.12, 1), (0.84, 0.68, 0.54, 1)),
    ("Developer_Male_01", False, "Hair_SimpleParted.gltf", (0.18, 0.32, 0.62, 1), (0.22, 0.15, 0.10, 1), (0.86, 0.70, 0.56, 1)),
    ("Developer_Male_02", False, "Hair_Beard.gltf", (0.24, 0.40, 0.54, 1), (0.14, 0.11, 0.09, 1), (0.72, 0.54, 0.40, 1)),
    ("Security_Female_01", True, "Hair_BuzzedFemale.gltf", (0.10, 0.16, 0.32, 1), (0.14, 0.12, 0.10, 1), (0.85, 0.69, 0.55, 1)),
    ("Security_Male_01", False, "Hair_Buzzed.gltf", (0.10, 0.16, 0.32, 1), (0.12, 0.10, 0.09, 1), (0.74, 0.56, 0.42, 1)),
]

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def rename_armature_bones(arm_obj):
    for bone in arm_obj.data.bones:
        if bone.name in BONE_MAP:
            bone.name = BONE_MAP[bone.name]

def make_mat(name, color, roughness=0.75, metallic=0.0):
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return m

def build_character(name, is_female, hair_file, cloth_col, hair_col, skin_col):
    clear_scene()
    base_file = "Superhero_Female_FullBody.gltf" if is_female else "Superhero_Male_FullBody.gltf"
    bpy.ops.import_scene.gltf(filepath=os.path.join(CHARS_DIR, base_file))

    arm = None
    body_objs = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            arm = obj
        elif obj.type == 'MESH':
            body_objs.append(obj)

    if arm:
        rename_armature_bones(arm)

    cloth_mat = make_mat("Cloth", cloth_col, 0.8)
    skin_mat = make_mat("Skin", skin_col, 0.65)
    hair_mat = make_mat("Hair", hair_col, 0.7)
    eye_mat = make_mat("Eye", (0.08, 0.08, 0.1, 1), 0.3)

    for obj in body_objs:
        n = obj.name.lower()
        if "eye" in n and "eyebrow" not in n:
            obj.data.materials.clear()
            obj.data.materials.append(eye_mat)
        elif "eyebrow" in n:
            obj.data.materials.clear()
            obj.data.materials.append(hair_mat)
        else:
            # Body mesh: tint materials by slot name or index
            for i, mat in enumerate(obj.data.materials):
                if mat and "skin" in mat.name.lower():
                    obj.data.materials[i] = skin_mat
                elif mat and ("suit" in mat.name.lower() or "cloth" in mat.name.lower() or i == 0):
                    obj.data.materials[i] = cloth_mat
                else:
                    obj.data.materials[i] = skin_mat if i > 0 else cloth_mat

    # Import modular outfit (Peasant for Business/Cleaner/Developer, Ranger for Security/Boss)
    outfit_style = "Ranger" if ("Security" in name or "Boss" in name) else "Peasant"
    outfit_file = f"{'Female' if is_female else 'Male'}_{outfit_style}.gltf"
    outfit_path = os.path.join(OUTFITS_DIR, outfit_file)
    if os.path.exists(outfit_path) and arm:
        pants_mat = make_mat("Pants", (0.14, 0.16, 0.20, 1), 0.85)
        shoes_mat = make_mat("Shoes", (0.10, 0.08, 0.07, 1), 0.6)
        before = set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=outfit_path)
        after = [o for o in bpy.context.scene.objects if o not in before]
        for o in after:
            if o.type == 'MESH':
                on = o.name.lower()
                if "hood" in on or "pauldron" in on:
                    bpy.data.objects.remove(o, do_unlink=True)
                    continue
                o.parent = arm
                for mod in o.modifiers:
                    if mod.type == 'ARMATURE':
                        mod.object = arm
                o.data.materials.clear()
                if "legs" in on:
                    o.data.materials.append(pants_mat)
                elif "feet" in on or "boots" in on:
                    o.data.materials.append(shoes_mat)
                elif "arms" in on:
                    o.data.materials.append(skin_mat if outfit_style == "Peasant" else cloth_mat)
                else:
                    o.data.materials.append(cloth_mat)
            elif o.type == 'ARMATURE':
                bpy.data.objects.remove(o, do_unlink=True)

    # Import hairstyle and parent to head bone
    hair_path = os.path.join(HAIR_DIR, hair_file)
    if os.path.exists(hair_path) and arm and "head" in arm.data.bones:
        before = set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=hair_path)
        after = [o for o in bpy.context.scene.objects if o not in before]
        for o in after:
            if o.type == 'MESH':
                o.data.materials.clear()
                o.data.materials.append(hair_mat)
                # Parent to head bone keeping world transform
                mat_world = o.matrix_world.copy()
                o.parent = arm
                o.parent_type = 'BONE'
                o.parent_bone = 'head'
                o.matrix_world = mat_world

    out_path = os.path.join(OUT_DIR, f"SK_Chr_{name}.gltf")
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLTF_SEPARATE',
        export_animations=False,
    )

def build_animations():
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=ANIM_GLB)
    arm = None
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            arm = obj
            break
    if not arm:
        raise RuntimeError("No armature in UAL1_Standard.glb")

    rename_armature_bones(arm)

    # Rename actions to what SyntyAvatar.tsx expects
    CLIP_MAP = {
        "Idle_Loop": "breathing_idle",
        "Walk_Loop": "walking",
        "Jog_Fwd_Loop": "running",
        "Sitting_Idle_Loop": "sitting_idle",
        "Sitting_Talking_Loop": "sitting_talking",
        "Idle_Talking_Loop": "talking",
        "Jump_Loop": "jumping",
        "Interact": "typing",
    }
    keep = set()
    for act in list(bpy.data.actions):
        if act.name in CLIP_MAP:
            act.name = CLIP_MAP[act.name]
            act.use_fake_user = True
            keep.add(act)
        else:
            bpy.data.actions.remove(act)

    if os.path.exists(ANIM2_GLB):
        before_objs = set(bpy.data.objects)
        before_acts = set(bpy.data.actions)
        bpy.ops.import_scene.gltf(filepath=ANIM2_GLB)
        new_objs = [o for o in bpy.data.objects if o not in before_objs]
        arm2 = next((o for o in new_objs if o.type == 'ARMATURE'), None)
        if arm2:
            rename_armature_bones(arm2)
        UAL2_CLIP_MAP = {
            "Consume": "drinking",
            "Idle_Rail_Call": "waving",
            "Yes": "clapping",
        }
        for act in list(bpy.data.actions):
            if act in before_acts:
                continue
            if act.name in UAL2_CLIP_MAP:
                act.name = UAL2_CLIP_MAP[act.name]
                act.use_fake_user = True
                keep.add(act)
            else:
                bpy.data.actions.remove(act)
        for o in new_objs:
            bpy.data.objects.remove(o, do_unlink=True)

    # Push kept actions to NLA tracks so glTF exporter exports all of them
    if not arm.animation_data:
        arm.animation_data_create()
    for act in sorted(keep, key=lambda a: a.name):
        track = arm.animation_data.nla_tracks.new()
        track.name = act.name
        track.strips.new(act.name, int(act.frame_range[0]), act)

    # Remove mesh objects from anims file to keep synty_anims.glb lightweight
    for obj in list(bpy.context.scene.objects):
        if obj.type == 'MESH':
            bpy.data.objects.remove(obj, do_unlink=True)

    out_path = os.path.join(OUT_DIR, "synty_anims.glb")
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        export_animations=True,
        export_nla_strips=True,
    )

os.makedirs(OUT_DIR, exist_ok=True)
anims_only = "--anims-only" in sys.argv
try:
    if not anims_only:
        for char_spec in CHARACTERS:
            build_character(*char_spec)
            print(f"Built SK_Chr_{char_spec[0]}.gltf")

    build_animations()
    print("Built synty_anims.glb")
    print("DONE_CHARS")
except Exception:
    traceback.print_exc()
