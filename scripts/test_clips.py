import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + '/'
# Render every clip on a character as a contact sheet (one frame per clip).
import bpy, sys, math
sys.path.insert(0, ROOT + 'scripts')
import importlib, rig, anim; importlib.reload(rig); importlib.reload(anim)
from rig import *
from anim import *
name = sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
arm, coll = load_character(name)
A = Actor(name, arm)
h = A.c['height']
tests = [
    ('rest', None, 0.5), ('talk', talk(), 0.3), ('look_L', look((3, -3, h)), 0.5), ('look_up', look((0, -2, h * 4)), 0.5),
    ('wave', wave('left'), 0.5), ('arms_up', arms_up(), 0.5), ('arms_fwd', arms_forward(), 0.5), ('cross', arms_cross, 0.5),
    ('point', point('right', (-3, -3, h)), 0.5), ('clap', clap(), 0.3), ('rubhead', rub_head(), 0.5), ('sad', sad, 0.5),
    ('bounce', happy_bounce(), 0.25), ('jump_air', jump_arc(h * 0.5), 0.55), ('crouch', crouch(), 0.5), ('surprised', surprised, 0.4),
    ('stretch', stretch, 0.5), ('lie+sleep', [lie(), sleep], 0.5), ('kick_wind', kick('right'), 0.4), ('kick_thru', kick('right'), 0.6),
    ('dance', dance(), 0.25), ('sit', sit, 0.5), ('flap_up', flap(), 0.0), ('flap_dn', flap(), 0.3),
    ('fire', breathe_fire, 0.5), ('roar', roar, 0.5), ('ride', ride, 0.5), ('curl+sleep', [curl, sleep], 0.5),
]
N = len(tests)
F = 40
for i, (nm, fn, u) in enumerate(tests):
    if fn is None: continue
    f0 = i * F + 1
    fns = fn if isinstance(fn, list) else [fn]
    for g in fns:
        A.add(f0, f0 + F - 1, g, 0, 0)
A.key(1, (0, 0), 0)
A.bake(1, N * F)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
tgt = Vector((0, 0, h * 0.5))
cam.location = tgt + Vector((h * 0.6, -h * 2.6, h * 0.3)); cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = 35
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sc.collection.objects.link(sun); sun.data.energy = 3; sun.rotation_euler = (D(50), 0, D(-30))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.4, 0.5, 0.7, 1)
bpy.ops.mesh.primitive_plane_add(size=h * 20)
sc.render.engine = 'BLENDER_EEVEE_NEXT'; sc.render.resolution_x = 256; sc.render.resolution_y = 256
sc.eevee.taa_render_samples = 4
sc.render.image_settings.file_format = 'PNG'
import os
os.makedirs(ROOT + 'tmp/clips', exist_ok=True)
for i, (nm, fn, u) in enumerate(tests):
    fr = int(i * F + 1 + u * (F - 1))
    sc.frame_set(fr); sc.render.filepath = ROOT + f'tmp/clips/{name}_{i:02d}_{nm}.png'
    bpy.ops.render.render(write_still=True)
