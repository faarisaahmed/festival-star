import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + '/'
# Shot framework: a Shot's build(S) authors actors, camera, props and fx on
# top of world.blend.  render.py opens the world, calls build, bakes and renders.
import bpy, math, random, os
from mathutils import Vector, Matrix, Euler, Quaternion, noise
import rig, anim, fx, look
import terrain as T
from rig import Actor, load_character, R, V, D, smooth, FPS

SHOTS = []


def shot(name, seconds, preset, **opts):
    def deco(fn):
        SHOTS.append(dict(name=name, frames=int(round(seconds * FPS)), preset=preset, build=fn, **opts))
        return fn
    return deco


def get(name):
    for s in SHOTS:
        if s['name'] == name:
            return s
    raise KeyError(name)


def H(x, y):
    return float(T.height(x, y))


def G(x, y, dz=0.0):
    return Vector((x, y, H(x, y) + dz))


# story locations
TREE = Vector((0.0, 34.0, H(0, 34)))
BLANKET = Vector((5.0, 22.5, H(5, 22.5)))
MEADOW = Vector((2.0, 5.0, H(2, 5)))
ROCK = Vector((27.0, 24.0, H(27, 24)))
SHORE = Vector((-23.0, -12.0, H(-23, -12)))
LEDGE = Vector((128.0, 165.0, H(128, 165)))
STAR_HOME = TREE + Vector((0, 0, 16.6))


class Scene:
    def __init__(self, sc, info, mode):
        self.sc = sc
        self.info = info
        self.N = info['frames']
        self.mode = mode
        self.actors = {}
        self.post = []
        self.cam = None
        self.focus = None
        self.rng = random.Random(hash(info['name']) % 10000)

    # ---- characters --------------------------------------------------------
    def actor(self, name, blink=True):
        arm, coll = load_character(name)
        A = Actor(name, arm)
        if blink:
            A.auto_blinks(1, self.N)
        self.actors[name] = A
        if name == 'charizard':
            tail_flame(A)
        if name == 'sobble':
            for o in coll.objects:
                if o.name.startswith('sobble_tear'):
                    A.tear_obj = o
        return A

    # ---- camera ------------------------------------------------------------
    def camera(self, lens=35, fstop=2.8, sensor=36):
        cd = bpy.data.cameras.new('ShotCam')
        cam = bpy.data.objects.new('ShotCam', cd)
        self.sc.collection.objects.link(cam)
        tgt = bpy.data.objects.new('CamTarget', None)
        self.sc.collection.objects.link(tgt)
        c = cam.constraints.new('TRACK_TO')
        c.target = tgt
        c.track_axis = 'TRACK_NEGATIVE_Z'
        c.up_axis = 'UP_Y'
        cd.lens = lens
        cd.sensor_width = sensor
        cd.clip_start = 0.05
        cd.clip_end = 6000
        cd.dof.use_dof = fstop > 0
        cd.dof.aperture_fstop = max(fstop, 0.1)
        cd.dof.focus_object = tgt
        self.sc.camera = cam
        self.cam = cam
        self.tgt = tgt
        self.cam_roll = None
        return cam

    def cam_keys(self, keys, interp='BEZIER'):
        """keys: (f, loc, target, lens|None)"""
        if self.cam is None:
            self.camera()
        for f, loc, tg, lens in keys:
            self.cam.location = Vector(loc)
            self.cam.keyframe_insert('location', frame=f)
            self.tgt.location = Vector(tg)
            self.tgt.keyframe_insert('location', frame=f)
            if lens:
                self.cam.data.lens = lens
                self.cam.data.keyframe_insert('lens', frame=f)
        for ob in (self.cam, self.tgt, self.cam.data):
            if ob.animation_data and ob.animation_data.action:
                for fc in ob.animation_data.action.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = interp
                        if interp == 'BEZIER':
                            kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
        self._set_focus_default()

    def cam_fn(self, fn, f0=1, f1=None, step=1):
        """fn(f) -> (loc, target, lens|None); sampled every `step` frames"""
        f1 = f1 or self.N
        self.post.append(lambda: self._cam_fn(fn, f0, f1, step))

    def _cam_fn(self, fn, f0, f1, step):
        if self.cam is None:
            self.camera()
        fr = list(range(f0, f1 + 1, step))
        if fr[-1] != f1:
            fr.append(f1)
        self.cam_keys([(f, *fn(f)) for f in fr], 'LINEAR' if step == 1 else 'BEZIER')

    def shake(self, amount=0.02, speed=0.6):
        """handheld camera: noise on the target and camera position"""
        def do():
            for ob, amt in ((self.cam, amount), (self.tgt, amount * 1.5)):
                if not ob.animation_data or not ob.animation_data.action:
                    ob.keyframe_insert('location', frame=1)
                for fc in ob.animation_data.action.fcurves:
                    if fc.data_path != 'location':
                        continue
                    m = fc.modifiers.new('NOISE')
                    m.strength = amt
                    m.scale = 24 / speed
                    m.phase = self.rng.uniform(0, 100)
        self.post.append(do)

    def _set_focus_default(self):
        if self.focus is None and self.tgt is not None:
            fc = [k for k in (self.tgt.animation_data.action.fcurves if self.tgt.animation_data else [])]
            self.focus_point = self.tgt.location.copy()

    def dof(self, fstop):
        self.cam.data.dof.aperture_fstop = fstop
        self.cam.data.dof.use_dof = fstop > 0

    # ---- props / world state -----------------------------------------------
    def obj(self, name):
        return bpy.data.objects[name]

    def key_obj(self, ob, f, loc=None, rot=None, scale=None, interp=None):
        if loc is not None:
            ob.location = Vector(loc)
            ob.keyframe_insert('location', frame=f)
        if rot is not None:
            ob.rotation_euler = Euler(rot) if not isinstance(rot, Euler) else rot
            ob.keyframe_insert('rotation_euler', frame=f)
        if scale is not None:
            ob.scale = (scale,) * 3 if isinstance(scale, (int, float)) else scale
            ob.keyframe_insert('scale', frame=f)
        if interp and ob.animation_data:
            for fc in ob.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = interp

    def glow(self, f, lantern=None, star=None):
        for k, v in (('lantern_glow', lantern), ('star_glow', star)):
            if v is not None:
                self.sc[k] = float(v)
                self.sc.keyframe_insert(f'["{k}"]', frame=f)

    def attach(self, ob, A, bone, f0, f1, offset=(0, 0, 0), rotate=False, step=1):
        """key an object to follow a bone (world offset in bone space)"""
        def do():
            for f in list(range(int(f0), int(f1) + 1, step)):
                M = A.bone_matrix(f, bone)
                ob.location = M @ Vector(offset)
                ob.keyframe_insert('location', frame=f)
                if rotate:
                    ob.rotation_mode = 'QUATERNION'
                    ob.rotation_quaternion = M.to_quaternion()
                    ob.keyframe_insert('rotation_quaternion', frame=f)
        self.post.append(do)

    def ride(self, rider, mount, bone, offset, f0, f1, heading_offset=0.0):
        """rider's root follows a bone of the mount (must be set before bake)"""
        rider.fly = True
        for f in range(int(f0), int(f1) + 1):
            M = mount.bone_matrix(f, bone) if bone else mount.root_full(f)
            p = M @ Vector(offset)
            rider.key(f, (p.x, p.y, p.z), math.degrees(mount.heading(f)) + heading_offset)

    def fade_title(self, text, f0, f1, size=0.06, y=0.0, fin=18, fout=18):
        """title text in front of the camera"""
        def do():
            cu = bpy.data.curves.new('Title', 'FONT')
            cu.body = text
            cu.align_x = 'CENTER'
            cu.align_y = 'CENTER'
            cu.size = size
            try:
                cu.font = bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Georgia Bold.ttf')
            except Exception:
                pass
            ob = bpy.data.objects.new('Title', cu)
            self.sc.collection.objects.link(ob)
            ob.parent = self.cam
            ob.location = (0, y, -1.0)
            m = fx.mat_glow('FX_Title', 3.0, 0.0)
            cu.materials.append(m)
            ob.color = (1, 0.95, 0.85, 0)
            ob.keyframe_insert('color', frame=f0)
            ob.color = (1, 0.95, 0.85, 1)
            ob.keyframe_insert('color', frame=f0 + fin)
            ob.keyframe_insert('color', frame=f1 - fout)
            ob.color = (1, 0.95, 0.85, 0)
            ob.keyframe_insert('color', frame=f1)
        self.post.append(do)


# ---------------------------------------------------------------------------
def tail_flame(A):
    """replace Charizard's tail-fire material with a flickering flame + light"""
    fire = [o for o in A.arm.children if 'fire' in o.name]
    m = bpy.data.materials.new('TailFlame')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.noise_dimensions = '4D'
    nz.inputs['Scale'].default_value = 18
    nz.inputs['Detail'].default_value = 3
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    d = nz.inputs['W'].driver_add('default_value').driver
    d.expression = 'frame/7'
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (1.0, 0.25, 0.02, 1)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (1.0, 0.9, 0.5, 1)
    nt.links.new(nz.outputs['Fac'], ramp.inputs[0])
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 25
    nt.links.new(ramp.outputs[0], em.inputs['Color'])
    lw = nt.nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.4
    inv = nt.nodes.new('ShaderNodeMath')
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1
    nt.links.new(lw.outputs['Facing'], inv.inputs[1])
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    mul.use_clamp = True
    nt.links.new(inv.outputs[0], mul.inputs[0])
    mul.inputs[1].default_value = 2.2
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(mul.outputs[0], mx.inputs['Fac'])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    m.surface_render_method = 'BLENDED'
    for o in fire:
        for sl in o.material_slots:
            sl.material = m
    li = bpy.data.lights.new('TailLight', 'POINT')
    li.color = (1.0, 0.55, 0.2)
    li.energy = 60
    li.shadow_soft_size = 0.15
    fl = li.driver_add('energy').driver
    fl.expression = '45 + 20*noise.noise((frame*0.35, 0, 0))' if False else '48 + 14*sin(frame*1.7) + 9*sin(frame*3.1)'
    lo = bpy.data.objects.new('TailLight', li)
    lo.parent = A.arm
    lo.parent_type = 'BONE'
    lo.parent_bone = 'tail_07'
    bpy.context.scene.collection.objects.link(lo)
    A.tail_light = lo


def eye_points(A):
    """left/right eye centres in head-bone local space (from eye mesh verts)"""
    head = A.c['head']
    hb = A.arm.data.bones[head]
    inv = hb.matrix_local.inverted()
    eyes = [o for o in A.arm.children if o.type == 'MESH' and 'eye' in o.name and not o.hide_render]
    pts = []
    for o in eyes:
        for v in o.data.vertices:
            pts.append(o.matrix_world @ v.co)
    if not pts:
        h = A.rest_head[head]
        return inv @ (h + V(0.03, -0.05, 0.02)), inv @ (h + V(-0.03, -0.05, 0.02))
    L = [p for p in pts if p.x > 0]
    Rr = [p for p in pts if p.x < 0]
    cl = sum(L, Vector()) / len(L)
    cr = sum(Rr, Vector()) / len(Rr)
    return inv @ cl, inv @ cr
