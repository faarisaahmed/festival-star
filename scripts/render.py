import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + '/'
# blender -b --python scripts/render.py -- SHOT MODE [ARG]
#   MODE preview  : small, fast, every 4th frame  -> frames/preview/SHOT/
#   MODE stills   : ARG = "1,40,80" final-quality stills -> frames/stills/SHOT_####.jpg
#   MODE final    : all frames, resumable            -> frames/final/SHOT/
#   MODE blend    : just save the built scene to tmp/SHOT.blend for inspection
import bpy, sys, os, time, importlib
sys.path.insert(0, ROOT + 'scripts')
import rig, look, shotlib
import terrain as T
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
name, mode = argv[0], argv[1]
arg = argv[2] if len(argv) > 2 else ''
ROOT = shotlib.ROOT

import shots  # registers SHOTS
info = shotlib.get(name)

bpy.ops.wm.open_mainfile(filepath=ROOT + 'world.blend')
sc = bpy.context.scene
FINAL_RES = (1920, 1080)
if mode in ('preview', 'pstills'):
    look.setup_render(sc, (640, 360), 6, fast=True)
else:
    look.setup_render(sc, FINAL_RES, info.get('samples', 20))
look.compositor(sc, glare=info.get('glare', 0.5))
# tone down the Star (drivers baked into world.blend)
for idb, path in ((bpy.data.lights.get('StarLight'), 'energy'),):
    if idb and idb.animation_data:
        for d in idb.animation_data.drivers:
            d.driver.expression = 'g*380'
m = bpy.data.materials.get('StarCrystal')
if m and m.node_tree.animation_data:
    for d in m.node_tree.animation_data.drivers:
        d.driver.expression = 'g*16'
look.set_time(sc, info['preset'], info.get('light'))
rig.GROUND[0] = lambda x, y: float(T.height(x, y))
sc.frame_start = 1
sc.frame_end = info['frames']

S = shotlib.Scene(sc, info, mode)
t0 = time.time()
info['build'](S)
N = info['frames']
for A in S.actors.values():
    A.bake(0, N + 1)
for fn in S.post:
    fn()
print('BUILD', name, 'secs', round(time.time() - t0, 1), 'frames', N)

# dense grass follows the action
foc = bpy.data.objects.get('GrassFocus')
if foc is not None:
    if getattr(S, 'grass_at', None) is not None:
        foc.location = Vector(S.grass_at)
    elif S.tgt is not None:
        sc.frame_set(N // 2)
        foc.location = S.tgt.matrix_world.translation.copy()
    sc.frame_set(1)

sc.render.use_motion_blur = mode not in ('preview', 'pstills')
sc.render.motion_blur_shutter = 0.5
try:
    sc.eevee.motion_blur_steps = 1
except Exception:
    pass

if mode == 'blend':
    bpy.ops.wm.save_as_mainfile(filepath=ROOT + f'tmp/{name}.blend')
elif mode == 'preview':
    out = ROOT + f'frames/preview/{name}/'
    os.makedirs(out, exist_ok=True)
    step = int(arg) if arg else 4
    for f in range(1, N + 1, step):
        sc.frame_set(f)
        sc.render.filepath = out + f'{f:04d}.jpg'
        bpy.ops.render.render(write_still=True)
elif mode in ('stills', 'pstills'):
    out = ROOT + ('frames/stills/' if mode == 'stills' else 'frames/pstills/')
    if arg in ('', 'auto'):
        arg = ','.join(str(int(1 + (N - 1) * k / 5)) for k in range(6))
    os.makedirs(out, exist_ok=True)
    for f in [int(x) for x in arg.split(',')]:
        sc.frame_set(f)
        sc.render.filepath = out + f'{name}_{f:04d}.jpg'
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print('STILL', f, round(time.time() - t, 1))
elif mode == 'final':
    out = ROOT + f'frames/final/{name}/'
    os.makedirs(out, exist_ok=True)
    sc.render.filepath = out + '####'
    sc.render.use_overwrite = False
    sc.render.use_placeholder = True
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 94
    t = time.time()
    bpy.ops.render.render(animation=True)
    print('FINAL', name, 'secs', round(time.time() - t, 1), 'per frame', round((time.time() - t) / N, 2))
