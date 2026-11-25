import bpy
import os
import re
import sys
import math
import traceback
from mathutils import Vector

LOG_FILE = r"C:\Users\caner\OpenBot\Shared\3d-assets\props_build.log"
sys.stdout = open(LOG_FILE, "w", buffering=1, encoding="utf-8")
sys.stderr = sys.stdout

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = r"C:\Users\caner\.agent-office\premium\models"
ASSETS = r"C:\Users\caner\OpenBot\Shared\3d-assets"

KENNEY = os.path.join(ASSETS, "kenney", "Models", "GLTF format")
OFFICE_PACK = os.path.join(ASSETS, "office_pack", "gLTF")
VNB = os.path.join(ASSETS, "vnb_office", "OBJ")
DOWNTOWN = os.path.join(ASSETS, "downtown_city", "Exports", "glTF (Godot)")

def k(f): return os.path.join(KENNEY, f)
def op(f): return os.path.join(OFFICE_PACK, f)
def vnb(f): return os.path.join(VNB, f)
def dt(f): return os.path.join(DOWNTOWN, f)

# Pattern -> (source_file_path, target_dimensions (w, h, d) or None to use fit())
PROP_SOURCES = [
    (r"^SM_Prop_Desk_Standing", vnb("Desk_2.obj"), (1.6, 1.05, 0.8)),
    (r"^SM_Prop_Desk_0[123]$", vnb("Desk.obj"), (1.6, 0.75, 0.8)),
    (r"^SM_Prop_Desk_0[456]$", k("desk.glb"), (1.6, 0.75, 0.8)),
    (r"^SM_Prop_Chair_BeanBag", k("loungeChairRelax.glb"), (0.85, 0.65, 0.85)),
    (r"^SM_Prop_Chair_0[1-5]$", k("chairDesk.glb"), (0.6, 0.92, 0.6)),
    (r"^SM_Prop_Chair_0[6-9]$", k("chairCushion.glb"), (0.58, 0.9, 0.58)),
    (r"^SM_Prop_Chair_1[01]$", k("chairModernCushion.glb"), (0.58, 0.88, 0.58)),
    (r"^SM_Prop_Couch_0[123]$", k("loungeSofa.glb"), (1.9, 0.82, 0.85)),
    (r"^SM_Prop_Couch_0[456]$", k("loungeDesignSofa.glb"), (1.9, 0.82, 0.85)),
    (r"^SM_Prop_Benchseat|^SM_Prop_Outdoor_Seat", k("benchCushion.glb"), (1.4, 0.55, 0.5)),
    (r"^SM_Prop_Computer_Monitor_Double|^SM_Prop_Computer_Monitor_Triple|^SM_Prop_Computer_Monitor_Curved", k("computerScreen.glb"), (0.95, 0.48, 0.22)),
    (r"^SM_Prop_Computer_Monitor_", k("computerScreen.glb"), (0.62, 0.46, 0.20)),
    (r"^SM_Prop_Monitor_Crt", k("computerScreen.glb"), (0.5, 0.45, 0.4)),
    (r"^SM_Prop_TV_Wall|^SM_Prop_Rolling_TV", k("televisionModern.glb"), (1.3, 0.78, 0.14)),
    (r"^SM_Prop_Laptop", k("laptop.glb"), (0.36, 0.26, 0.28)),
    (r"^SM_Prop_Computer_Keyboard_", k("computerKeyboard.glb"), (0.44, 0.05, 0.16)),
    (r"^SM_Prop_Computer_Mouse_", k("computerMouse.glb"), (0.08, 0.04, 0.12)),
    (r"^SM_Prop_Computer_Mousepad", op("mousepad.glb"), (0.32, 0.01, 0.26)),
    (r"^SM_Prop_Computer_Tower_Modern|^SM_Prop_Computer_Tower_0", op("desktop.glb"), (0.22, 0.46, 0.45)),
    (r"^SM_Prop_Computer_Tower_Flat", op("mini_pc.glb"), (0.24, 0.08, 0.24)),
    (r"^SM_Prop_Printer_01|^SM_Prop_Printer_Mini", op("printer_desktop.glb"), (0.45, 0.32, 0.38)),
    (r"^SM_Prop_Photocopier|^SM_Prop_Printer_3D", op("printer_big.glb"), (0.7, 1.15, 0.65)),
    (r"^SM_Prop_Table_Conference", k("table.glb"), (2.4, 0.75, 1.1)),
    (r"^SM_Prop_Table_Round", k("tableRound.glb"), (1.1, 0.75, 1.1)),
    (r"^SM_Prop_Table_", k("tableGlass.glb"), (1.3, 0.75, 0.8)),
    (r"^SM_Prop_CoffeeTable", k("tableCoffee.glb"), (1.1, 0.45, 0.65)),
    (r"^SM_Prop_Shelf_0[1-4]$", k("bookcaseOpen.glb"), (1.0, 1.7, 0.4)),
    (r"^SM_Prop_Shelf_0[5-7]$|^SM_Prop_Cabinets", k("bookcaseClosed.glb"), (1.0, 1.6, 0.42)),
    (r"^SM_Prop_Shelf_Wall", k("bookcaseOpenLow.glb"), (0.9, 0.45, 0.28)),
    (r"^SM_Prop_Kitchen_CounterSink", k("kitchenSink.glb"), (1.0, 0.9, 0.6)),
    (r"^SM_Prop_Kitchen_Counter", k("kitchenCabinet.glb"), (1.0, 0.9, 0.6)),
    (r"^SM_Prop_Kitchen_Cabinet", k("kitchenCabinetUpper.glb"), (1.0, 0.75, 0.4)),
    (r"^SM_Prop_Fridge_0", k("kitchenFridgeLarge.glb"), (0.85, 1.85, 0.75)),
    (r"^SM_Prop_MiniFridge", k("kitchenFridgeSmall.glb"), (0.55, 0.85, 0.55)),
    (r"^SM_Prop_CoffeeMachine", k("kitchenCoffeeMachine.glb"), (0.28, 0.36, 0.28)),
    (r"^SM_Prop_Microwave", k("kitchenMicrowave.glb"), (0.48, 0.30, 0.35)),
    (r"^SM_Prop_Toaster", k("toaster.glb"), (0.26, 0.20, 0.18)),
    (r"^SM_Prop_Plant_0[1-7]$|^SM_Prop_Tree_Round", k("pottedPlant.glb"), (0.5, 1.1, 0.5)),
    (r"^SM_Prop_Plant_0[89]$|^SM_Prop_Plant_1[0-4]$|^SM_Prop_Plant_Flowers|^SM_Prop_Flowers", k("plantSmall1.glb"), (0.35, 0.45, 0.35)),
    (r"^SM_Prop_Desklamp_0[12]|^SM_Prop_DeskLamp_0[56]", op("lamp_architect.glb"), (0.22, 0.48, 0.22)),
    (r"^SM_Prop_Desklamp|^SM_Prop_DeskLamp", op("lamp.glb"), (0.20, 0.40, 0.20)),
    (r"^SM_Prop_Light_Fluorescent|^SM_Prop_Light_0", k("lampSquareCeiling.glb"), (0.8, 0.12, 0.35)),
    (r"^SM_Prop_Rug_0[123]$", k("rugRectangle.glb"), (2.0, 0.02, 1.3)),
    (r"^SM_Prop_Rug_0[45]$", k("rugRound.glb"), (1.5, 0.02, 1.5)),
    (r"^SM_Prop_Cup_", op("mug.glb"), (0.10, 0.11, 0.10)),
    (r"^SM_Prop_Donut_", vnb("Simple_Donut.obj"), (0.12, 0.05, 0.12)),
    (r"^SM_Prop_Book_", k("books.glb"), (0.28, 0.24, 0.20)),
    (r"^SM_Prop_Trashbin|^SM_Prop_Bin_", k("trashcan.glb"), (0.32, 0.48, 0.32)),
    (r"^SM_Prop_CardboardBox", k("cardboardBoxClosed.glb"), (0.45, 0.38, 0.45)),
    (r"^SM_Prop_CoatRack", k("coatRackStanding.glb"), (0.45, 1.75, 0.45)),
    (r"^SM_Prop_CeilingFan", k("ceilingFan.glb"), (1.1, 0.35, 1.1)),
    (r"^SM_Prop_Speaker_Bluetooth", op("speaker_bookshelf.glb"), (0.16, 0.24, 0.16)),
    (r"^SM_Prop_Speaker_", op("speaker_desktop.glb"), (0.14, 0.24, 0.16)),
    (r"^SM_Prop_Microphone_0[23]", op("boom_mic.glb"), (0.28, 0.45, 0.28)),
    (r"^SM_Prop_Microphone", op("mic_desktop.glb"), (0.14, 0.28, 0.14)),
    (r"^SM_Prop_GraphicsTablet", op("tablet.glb"), (0.30, 0.03, 0.22)),
    (r"^SM_Prop_Webcam", op("camera.glb"), (0.08, 0.08, 0.08)),
    (r"^SM_Prop_PencilCup|^SM_Prop_Cup_Pens", op("pencil_holder.glb"), (0.10, 0.14, 0.10)),
    (r"^SM_Prop_Pen_", op("pen.glb"), (0.02, 0.02, 0.15)),
    (r"^SM_Prop_Pencil_", op("pencil.glb"), (0.02, 0.02, 0.15)),
    (r"^SM_Prop_Radio", k("radio.glb"), (0.32, 0.22, 0.16)),
    (r"^SM_Prop_Toilet_0", k("toilet.glb"), (0.45, 0.78, 0.65)),
    (r"^SM_Prop_Bathroom_Sink|^SM_Prop_Sink_01", k("bathroomSink.glb"), (0.6, 0.85, 0.5)),
    (r"^SM_Prop_Bathroom_Mirror", k("bathroomMirror.glb"), (0.65, 0.8, 0.05)),
    (r"^SM_Prop_Aircon", dt("Prop_ACUnit.gltf"), (0.85, 0.55, 0.32)),
    # Downtown City MegaKit structural pieces (4-tuple = corner-aligned: w, h, d, y)
    (r"^SM_Bld_Wall_Brick_Window_", dt("Brick_Window_Trim.gltf"), (2.5, 3.0, 0.14, 0.0)),
    (r"^SM_Bld_Wall_.*_Window_", dt("Brick_Inset_Window.gltf"), (2.5, 3.0, 0.14, 0.0)),
    (r"^SM_Bld_Wall_.*_Door_", dt("DoorFrame_Trim.gltf"), (2.5, 3.0, 0.14, 0.0)),
    (r"^SM_Bld_Wall_.*_Elevator", dt("DoorFrame_Metal_Single.gltf"), (2.5, 3.0, 0.14, 0.0)),
    (r"^SM_Bld_Wall_Brick_", dt("Brick_Plain_1.gltf"), (2.5, 3.0, 0.14, 0.0)),
    (r"^SM_Bld_Wall_Blank_", dt("Brick_InteriorWall_1.gltf"), (2.5, 3.0, 0.14, 0.0)),
    (r"^SM_Bld_Wall_Trim_|^SM_Bld_Wall_Baseboard_", dt("Trim_Plain_3.gltf"), (2.5, 3.0, 0.14, 0.0)),
    (r"^SM_Bld_FeatureWall_Wood", dt("Brick_InteriorWall_3.gltf"), (2.5, 3.0, 0.14, 0.0)),
    (r"^SM_Bld_FeatureWall_", dt("Brick_InteriorWall_4.gltf"), (2.5, 3.0, 0.14, 0.0)),
    (r"^SM_Bld_Wall_Glass_0|^SM_Bld_Wall_Glass_Large_0", dt("Metal_FullWindow.gltf"), (2.5, 3.0, 0.14, 0.0)),
    (r"^SM_Bld_Pillar_|^SM_Bld_Wall_Glass_Pillar", dt("Metal_Column_Center.gltf"), (0.28, 3.0, 0.28, 0.0)),
    (r"^SM_Bld_Door_0[12]", dt("Door_1.gltf"), (0.9, 2.2, 0.06, 0.0)),
    (r"^SM_Bld_Door_0[345]", dt("Door_2.gltf"), (0.9, 2.2, 0.06, 0.0)),
    (r"^SM_Bld_Door_Large_", dt("Door_3.gltf"), (0.9, 2.2, 0.06, 0.0)),
    (r"^SM_Bld_Floor_Concrete", dt("Entrance_Concrete_2x2.gltf"), (2.5, 0.04, 2.5, -0.04)),
    (r"^SM_Bld_Floor_", dt("Floor_2x2.gltf"), (2.5, 0.04, 2.5, -0.04)),
    (r"^SM_Bld_Roof_", dt("Roof_2x2.gltf"), (2.5, 0.12, 2.5, 2.9)),
    (r"^SM_Bld_Stairs_", dt("Stairs_Entrance_Concrete.gltf"), (2.5, 0.12, 2.5, 0.0)),
]

def fit_fallback(name):
    n = re.sub(r"^SM_(Prop|Bld|Chr)_", "", name)
    def corner(w, h, d, y=0.0):
        # glTF (X=w, Y=h, Z=d) -> Blender (X=w, Y=-d, Z=h) or handle in glTF coords
        return ("corner", w, h, d, y)
    def sit(w, h, d):
        return ("sit", w, h, d, 0.0)
    if re.match(r"^Floor_|^Ceiling_", n):
        return corner(2.5, 0.04, 2.5, 2.96 if "Ceiling" in n else -0.04)
    if re.match(r"^Wall_|^FeatureWall|^Window_|^Pillar_|^Baseboard|^Trim_|^Garden|^Weather|^Awning", n):
        return corner(2.5, 3.0, 0.14)
    if re.match(r"^Door_|^Elevator", n):
        return corner(0.9, 2.2, 0.06)
    if re.match(r"^Roof_|^Stairs_", n):
        return corner(2.5, 0.12, 2.5, 2.9)
    if "Desk_" in n: return sit(1.6, 0.75, 0.8)
    if re.search(r"Chair_|BeanBag|Couch_|Bench", n):
        return sit(1.8 if "Couch" in n else 0.55, 0.45 if "BeanBag" in n else 0.9, 0.8 if "Couch" in n else 0.55)
    if re.search(r"Monitor|Screen|TV_|Whiteboard|CorkBoard|Poster|Sign_|Darkboard|Blackboard", n):
        return sit(0.7, 0.45, 0.06)
    if "Table_" in n:
        return sit(2.4 if "Conference" in n else 1.1, 0.75, 1.1 if "Conference" in n else 0.7)
    if re.search(r"Server_Cabinet|Fridge|Photocopier|Vending|Arcade|Jukebox|Locker", n):
        return sit(0.7, 1.8, 0.55)
    if re.search(r"Plant|Tree|Hedge|LampPost", n):
        return sit(0.45, 1.8 if re.search(r"Tree|LampPost", n) else 0.7, 0.45)
    if "Keyboard" in n: return sit(0.4, 0.03, 0.14)
    if "Mouse_" in n: return sit(0.08, 0.03, 0.12)
    if re.search(r"PoolTable|TableFootball|TableTennis", n): return sit(1.8, 0.75, 1.0)
    if "CubicalWall" in n: return sit(1.5, 1.3, 0.05)
    if re.search(r"Shelf|Cabinet|Counter", n): return sit(1.0, 1.1, 0.4)
    if "Rug_" in n: return sit(1.6, 0.02, 1.1)
    if re.search(r"Light_|Fluorescent|Aircon|CeilingFan", n):
        return ("sit", 0.8, 0.08, 0.3, 2.7)
    return sit(0.22, 0.18, 0.18)

def color_for(name):
    n = name.lower()
    if re.search(r"screen|monitor|tv_", n): return (0.15, 0.45, 0.75, 1.0)
    if re.search(r"floor_wood|desk|door|shelf|table", n): return (0.55, 0.38, 0.22, 1.0)
    if re.search(r"floor_carpet|couch|chair|rug", n): return (0.35, 0.42, 0.55, 1.0)
    if re.search(r"floor_tile|floor_panel|kitchen|fridge", n): return (0.75, 0.78, 0.80, 1.0)
    if re.search(r"floor_concrete|server|tower", n): return (0.45, 0.47, 0.50, 1.0)
    if re.search(r"floor_grass|plant|tree|hedge", n): return (0.25, 0.48, 0.28, 1.0)
    if re.search(r"wall|pillar|ceiling|trim|baseboard", n): return (0.82, 0.80, 0.75, 1.0)
    if re.search(r"glass|window", n): return (0.55, 0.70, 0.78, 0.45)
    if "brick" in n: return (0.55, 0.32, 0.26, 1.0)
    return (0.62, 0.64, 0.68, 1.0)

def get_prop_names():
    props_txt = os.path.join(HERE, "props.txt")
    with open(props_txt, "r", encoding="utf-8") as f:
        names = [x for x in f.read().split() if x.startswith("SM_")]
    src_root = os.path.normpath(os.path.join(HERE, "..", "..", "premium-app", "src"))
    for root, _, files in os.walk(src_root):
        for fn in files:
            if fn.endswith((".ts", ".tsx")):
                with open(os.path.join(root, fn), "r", encoding="utf-8") as f:
                    txt = f.read()
                for m in re.finditer(r"""['"]((?:SM_[A-Za-z0-9_]+)|(?:B:[A-Za-z0-9_]+))['"]""", txt):
                    raw = m.group(1)
                    names.append(f"SM_Bld_{raw[2:]}" if raw.startswith("B:") else raw)
    return sorted(set(names))

def match_source(name):
    for pat, src_path, dims in PROP_SOURCES:
        if re.search(pat, name) and os.path.exists(src_path):
            return src_path, dims
    return None, None

def import_and_join(src_path):
    before = set(bpy.context.scene.objects)
    if src_path.lower().endswith((".glb", ".gltf")):
        bpy.ops.import_scene.gltf(filepath=src_path)
    elif src_path.lower().endswith(".obj"):
        bpy.ops.wm.obj_import(filepath=src_path)
    new_objs = [o for o in bpy.context.scene.objects if o not in before]
    meshes = [o for o in new_objs if o.type == 'MESH']
    if not meshes:
        for o in new_objs:
            bpy.data.objects.remove(o, do_unlink=True)
        return None

    # Apply transforms on each mesh and join into one
    bpy.ops.object.select_all(action='DESELECT')
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active

    # Remove non-mesh empties/lights/cameras from import
    for o in new_objs:
        try:
            if o != obj:
                bpy.data.objects.remove(o, do_unlink=True)
        except ReferenceError:
            pass
    return obj

def _vert_bounds(obj):
    mw = obj.matrix_world
    xs, ys, zs = [], [], []
    for v in obj.data.vertices:
        co = mw @ v.co
        xs.append(co.x)
        ys.append(co.y)
        zs.append(co.z)
    if not xs:
        return 0, 0, 0, 0, 0, 0
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)

def normalize_mesh_to_sit(obj, target_w, target_h, target_d):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    x0, x1, y0, y1, z0, z1 = _vert_bounds(obj)
    w, d, h = x1 - x0, y1 - y0, z1 - z0
    if w < 1e-5 or d < 1e-5 or h < 1e-5:
        obj.select_set(False)
        return

    # Align long horizontal axis if target is wider than deep
    if target_w > target_d * 1.15 and d > w * 1.1:
        obj.rotation_euler = (0.0, 0.0, math.pi * 0.5)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        x0, x1, y0, y1, z0, z1 = _vert_bounds(obj)
        w, d, h = x1 - x0, y1 - y0, z1 - z0

    s = min(target_w / w, target_h / h, target_d / d)
    obj.scale = (s, s, s)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    x0, x1, y0, y1, z0, z1 = _vert_bounds(obj)
    cx = (x0 + x1) * 0.5
    cy = (y0 + y1) * 0.5
    obj.location = (-cx, -cy, -z0)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    obj.select_set(False)

def normalize_mesh_to_corner(obj, target_w, target_h, target_d, y_offset=0.0):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    x0, x1, y0, y1, z0, z1 = _vert_bounds(obj)
    w, d, h = x1 - x0, y1 - y0, z1 - z0
    if w < 1e-5 or d < 1e-5 or h < 1e-5:
        obj.select_set(False)
        return

    if target_w > target_d * 1.15 and d > w * 1.1:
        obj.rotation_euler = (0.0, 0.0, math.pi * 0.5)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        x0, x1, y0, y1, z0, z1 = _vert_bounds(obj)
        w, d, h = x1 - x0, y1 - y0, z1 - z0

    obj.scale = (target_w / w, target_d / d, target_h / h)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    x0, x1, y0, y1, z0, z1 = _vert_bounds(obj)
    # Corner-aligned in glTF: X in [0, w], Y_blender in [-d, 0] (Z_gltf in [0, d]), Z_blender in [y, y+h]
    obj.location = (-x0, -y1, y_offset - z0)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    obj.select_set(False)

mat_cache = {}
def get_mat(rgba):
    key = tuple(round(x, 3) for x in rgba)
    if key in mat_cache:
        return mat_cache[key]
    m = bpy.data.materials.new(name="Glass" if key[3] < 1.0 else f"Mat_{len(mat_cache)}")
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.85
        bsdf.inputs["Metallic"].default_value = 0.05
        if rgba[3] < 1.0:
            bsdf.inputs["Alpha"].default_value = rgba[3]
            m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else 'HASHED'
    mat_cache[key] = m
    return m

def make_fallback_box(name):
    mode, w, h, d, y = fit_fallback(name)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.name = name
    # In Blender Z-up: X=w, Y=d, Z=h
    obj.scale = (w, d, h)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mode == "corner":
        obj.location = (w * 0.5, -d * 0.5, y + h * 0.5)
    else:
        obj.location = (0.0, 0.0, y + h * 0.5)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    obj.data.materials.append(get_mat(color_for(name)))
    return obj

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    names = get_prop_names()
    print(f"Total props to build: {len(names)}")

    # Cache imported templates by (src_path, dims) so we duplicate mesh data instead of re-importing
    template_cache = {}
    real_count = 0
    fallback_count = 0

    for name in names:
        src_path, dims = match_source(name)
        if src_path:
            key = (src_path, dims)
            if key not in template_cache:
                tmpl = import_and_join(src_path)
                if tmpl:
                    if len(dims) == 4:
                        normalize_mesh_to_corner(tmpl, dims[0], dims[1], dims[2], dims[3])
                    else:
                        normalize_mesh_to_sit(tmpl, dims[0], dims[1], dims[2])
                    tmpl.name = name
                    template_cache[key] = tmpl
                    real_count += 1
                else:
                    template_cache[key] = None
                    obj = make_fallback_box(name)
                    fallback_count += 1
            else:
                tmpl = template_cache[key]
                if tmpl:
                    dup = tmpl.copy()
                    dup.data = tmpl.data
                    dup.name = name
                    bpy.context.collection.objects.link(dup)
                    real_count += 1
                else:
                    make_fallback_box(name)
                    fallback_count += 1
        else:
            make_fallback_box(name)
            fallback_count += 1

    print(f"Built {real_count} real-model props + {fallback_count} structural/fallback props")
    out_path = os.path.join(OUT_DIR, "office_props.gltf")
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLTF_SEPARATE',
        export_animations=False,
    )
    print("DONE_PROPS")

try:
    main()
except Exception:
    traceback.print_exc()
