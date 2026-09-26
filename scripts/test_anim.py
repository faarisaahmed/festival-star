import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + '/'
import bpy, sys, math
sys.path.insert(0, ROOT + 'scripts')
import importlib, rig; importlib.reload(rig)
from rig import *
name = sys.argv[-2]; out = sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
arm, coll = load_character(name)
a = Actor(name, arm)
h = a.c['height']; st = a.c['stride']
# frames: 1 rest, 10 blink, 20 jaw, 30.. walk
a.key(1, (0, 0), 0); a.key(24, (0, 0)); a.key(24+48, (0, -st*2.5)); a.key(100, (0, -st*2.5))
a.blinks.append(8)
a.add(14, 22, lambda A, f, u, t: {A.c['jaw']: R(25)}, 2, 2)
a.bake(1, 100)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
tgt = Vector((0, -st*1.2, h*0.5))
cam.location = tgt + Vector((h*1.6, -h*1.8, h*0.3)); cam.rotation_euler = (tgt-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens = 40
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun','SUN')); sc.collection.objects.link(sun); sun.data.energy = 3; sun.rotation_euler = (D(50), 0, D(-30))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.4,0.5,0.7,1)
bpy.ops.mesh.primitive_plane_add(size=h*20)
sc.render.engine = 'BLENDER_EEVEE_NEXT'; sc.render.resolution_x = 320; sc.render.resolution_y = 320
sc.render.image_settings.file_format = 'PNG'
for fr in [1, 9, 18, 36, 42, 48, 54]:
    sc.frame_set(fr); sc.render.filepath = f'{out}_{fr:03d}.png'; bpy.ops.render.render(write_still=True)
