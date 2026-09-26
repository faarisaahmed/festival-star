import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + '/'
import bpy, sys, math, time
sys.path.insert(0, ROOT + 'scripts')
import look, terrain as T
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=ROOT + 'world.blend')
sc = bpy.context.scene
preset = sys.argv[-3]; tag = sys.argv[-2]; which = sys.argv[-1].split(',')
look.setup_render(sc, (960, 540), 16)
look.compositor(sc)
look.set_time(sc, preset)
if preset in ('night', 'dusk'):
    sc['lantern_glow'] = 1.0; sc['star_glow'] = 1.0
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
H = lambda x, y: float(T.height(x, y))
views = {
 'aerial': ((20, -150, 70), (-10, 20, 5), 28),
 'meadow': ((3, -18, H(3, -18) + 1.2), (0, 30, 5), 30),
 'tree': ((6, 8, H(6, 8) + 1.5), (0, 34, 9), 24),
 'lake': ((-20, -30, 3), (-75, -5, 8), 30),
 'falls': ((-62, -20, 2), (-82, -8, 7), 28),
 'peak': ((110, 120, 190), (128, 165, 166), 30),
 'low': ((0, -4, H(0, -4) + 0.3), (0, 10, 0.5), 35),
}
foc = bpy.data.objects['GrassFocus']
for name in which:
    loc, tgt, lens = views[name]
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(tgt) - cam.location).to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = lens
    cam.data.clip_end = 5000
    d = (Vector(tgt) - cam.location); d.z = 0
    foc.location = cam.location + d.normalized() * 15
    sc.render.filepath = ROOT + f'tmp/w2_{tag}_{name}.jpg'
    t = time.time(); bpy.ops.render.render(write_still=True); print('RENDERTIME', name, time.time() - t)
