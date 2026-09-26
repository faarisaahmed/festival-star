import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + '/'
# Procedural character animation for the Scarlet/Violet rigs.
#
# Conventions (all rigs after prep.py): armature has identity transform, Z up,
# character faces -Y, character's left side is +X.
# A pose is a dict  bone -> rotation vector (radians) expressed in the
# armature's *rest* frame.  Layers are summed (rotation-vector blending), then
# converted into each bone's local space when baked.
#   +X rot: legs swing back / head nods down / jaw opens / upper lid closes
#   +Y rot: LEFT arm/wing goes down (mirrored for right side automatically)
#   +Z rot: turn toward the character's left
import bpy, math, random
import numpy as np
from mathutils import Vector, Quaternion, Matrix

FPS = 24
D = math.radians


def V(x=0.0, y=0.0, z=0.0):
    return Vector((x, y, z))


def R(x=0.0, y=0.0, z=0.0):
    """rotation vector from degrees"""
    return Vector((D(x), D(y), D(z)))


def clamp(x, a, b):
    return a if x < a else b if x > b else x


def smooth(x):
    x = clamp(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def smoother(x):
    x = clamp(x, 0.0, 1.0)
    return x * x * x * (x * (x * 6 - 15) + 10)


def envelope(f, f0, f1, fin, fout):
    if f < f0 or f > f1:
        return 0.0
    a = smooth((f - f0) / fin) if fin > 0 else 1.0
    b = smooth((f1 - f) / fout) if fout > 0 else 1.0
    return min(a, b)


def mirror_name(n):
    if n.startswith('left_'):
        return 'right_' + n[5:]
    if n.startswith('right_'):
        return 'left_' + n[6:]
    return None


def mirror_rv(v):
    return Vector((v.x, -v.y, -v.z))


def wrap_angle(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


# ---------------------------------------------------------------------------
# Per-character rig description.  Chains are given for the LEFT side.
# base: rest-pose corrections (degrees) - e.g. lowering T-pose arms.
# ---------------------------------------------------------------------------
CFG = {
    'pikachu': dict(
        spine=['spine_01', 'spine_02'], neck=[], head='head', hips='hips', waist='waist',
        arm=['left_arm_01', 'left_arm_02', 'left_hand'],
        leg=['left_leg_01', 'left_leg_02', 'left_foot'],
        tail=['tail_01', 'tail_02', 'tail_03'], ears=['left_ear_01', 'left_ear_02', 'left_ear_03'],
        jaw='lower_jaw', lids=[('left_upper_eyelid_01', R(38))],
        base={'left_arm_01': R(0, 25, 0)},
        stride=0.34, bob=0.012, legswing=38, knee=45, armswing=30, height=0.41, gait='biped',
    ),
    'piplup': dict(
        spine=['spine'], neck=['neck'], head='head', hips='hips', waist='waist',
        arm=['left_arm', 'left_hand'],
        leg=['left_leg_01', 'left_leg_02', 'left_foot'],
        tail=['feeler_a_01', 'feeler_a_02'], ears=[],
        jaw='lower_jaw', lids=[('left_upper_eyelid_01', R(38))],
        base={'left_arm': R(0, 15, 0)},
        stride=0.2, bob=0.008, legswing=30, knee=30, armswing=10, roll=10, height=0.4, gait='waddle',
    ),
    'sobble': dict(
        spine=['spine_01', 'spine_02'], neck=['neck'], head='head', hips='hips', waist='waist',
        arm=['left_arm_01', 'left_arm_02', 'left_hand'],
        leg=['left_leg_01', 'left_leg_02', 'left_foot'],
        tail=['tail_01', 'tail_02', 'tail_03', 'tail_04', 'tail_05'], ears=['feeler_b_01', 'feeler_b_02', 'feeler_b_03'],
        jaw='lower_jaw_01', lids=[('left_upper_eyelid_a_01', R(40)), ('left_upper_eyelid_b_01', R(40))],
        base={'left_arm_01': R(0, 55, 0), 'left_leg_01': R(0, 60, 0), 'left_leg_02': R(0, 10, 0)},
        stride=0.16, bob=0.006, legswing=35, knee=30, armswing=25, roll=6, height=0.41, gait='waddle',
    ),
    'raboot': dict(
        spine=['spine_01', 'spine_02'], neck=['neck'], head='head', hips='hips', waist='waist',
        arm=['left_arm_01', 'left_arm_02', 'left_hand'],
        leg=['left_leg_01', 'left_leg_02', 'left_foot'],
        tail=['tail'], ears=['left_ear_01', 'left_ear_02', 'left_ear_03', 'left_ear_04'],
        jaw='lower_jaw', lids=[('left_upper_eyelid', R(40))],
        base={'left_arm_01': R(-10, 72, 0), 'left_arm_02': R(0, 0, -25), 'left_ear_01': R(0, 12, 0)},
        stride=0.55, bob=0.02, legswing=34, knee=55, armswing=25, height=0.75, gait='biped',
    ),
    'greninja': dict(
        spine=['spine_01', 'spine_02'], neck=['neck'], head='head', hips='hips', waist='waist',
        arm=['left_arm_01', 'left_arm_02', 'left_hand'],
        leg=['left_leg_01', 'left_leg_02', 'left_foot'],
        tail=[], ears=[], jaw='jaw_01', lids=[],
        base={'left_arm_01': R(0, 68, -20), 'left_arm_02': R(0, 10, -20), 'left_leg_01': R(0, 14, 0), 'left_foot': R(0, -10, 0)},
        stride=1.2, bob=0.03, legswing=30, knee=50, armswing=20, height=1.6, gait='biped',
    ),
    'charizard': dict(
        spine=['spine_01', 'spine_02'], neck=['neck_01', 'neck_02', 'neck_03'], head='head', hips='hips', waist='waist',
        arm=['left_arm_01', 'left_arm_02', 'left_hand'],
        leg=['left_leg_01', 'left_leg_02', 'left_foot'],
        tail=['tail_01', 'tail_02', 'tail_03', 'tail_04', 'tail_05', 'tail_06', 'tail_07'],
        ears=[], wing=['left_wing_a_01', 'left_wing_a_02', 'left_wing_a_03', 'left_wing_a_04'],
        jaw='jaw', lids=[('left_upper_eyelid_a', R(35)), ('left_upper_eyelid_b', R(35)), ('left_upper_eyelid_c', R(35))],
        base={'left_wing_a_01': R(0, 10, -25)},
        stride=1.1, bob=0.03, legswing=26, knee=35, armswing=12, roll=5, height=1.7, gait='biped',
    ),
    'garchomp': dict(
        spine=['spine'], neck=['neck'], head='head', hips='hips', waist='waist',
        arm=['left_arm_01', 'left_arm_02', 'left_hand'],
        leg=['left_leg_01', 'left_leg_02', 'left_foot'],
        tail=['tail_01', 'tail_02', 'tail_03', 'tail_04'], ears=[],
        jaw='jaw', lids=[('left_upper_eyelid', R(40))],
        base={'left_arm_01': R(0, 45, 0), 'left_arm_02': R(-20, 10, 0)},
        stride=1.4, bob=0.035, legswing=28, knee=40, armswing=10, height=1.9, gait='biped',
    ),
    'dragonite': dict(
        spine=['spine_01', 'spine_02'], neck=['neck'], head='head', hips='hips', waist='waist',
        arm=['left_arm_01', 'left_arm_02', 'left_hand'],
        leg=['left_leg_01', 'left_leg_02', 'left_foot'],
        tail=['tail_01', 'tail_02', 'tail_03', 'tail_04', 'tail_05', 'tail_06'], ears=['left_feeler_01', 'left_feeler_02'],
        wing=['left_wing_01', 'left_wing_02', 'left_wing_03'],
        jaw='jaw', lids=[('left_upper_eyelid_01', R(40))],
        base={'left_arm_01': R(0, 62, -10), 'left_arm_02': R(0, 0, -25)},
        stride=0.9, bob=0.03, legswing=22, knee=30, armswing=15, roll=6, height=2.2, gait='waddle',
    ),
}


class Clip:
    def __init__(self, f0, f1, fn, fin=6, fout=6, w=1.0):
        self.f0, self.f1, self.fn, self.fin, self.fout, self.w = f0, f1, fn, fin, fout, w


# ground height function used for placing actors: set by the world module
GROUND = [lambda x, y: 0.0]


def ground(x, y):
    return GROUND[0](x, y)


class Actor:
    def __init__(self, name, arm, seed=0):
        self.name = name
        self.arm = arm
        self.c = CFG[name]
        self.clips = []
        self.keys = []          # (frame, Vector(x,y,z|None), heading_deg|None)
        self.fly = False
        self.scale = 1.0
        self.rng = random.Random(hash(name) % 1000 + seed)
        self.blinks = []
        self.eyes_closed = []   # (f0, f1)
        self.rest = {b.name: b.matrix_local.to_quaternion() for b in arm.data.bones}
        self.rest_head = {b.name: b.head_local.copy() for b in arm.data.bones}
        self.bones = set(self.rest)
        self.extra_root = []    # functions f -> (loc Vector, rotvec) in actor-local
        self._dist_cache = None
        self.no_walk = []

    # ---- authoring ---------------------------------------------------------
    def key(self, f, pos=None, heading=None):
        """Root waypoint.  pos=(x,y) snaps to ground, (x,y,z) is absolute."""
        if pos is not None:
            pos = Vector(pos) if len(pos) == 3 else Vector((pos[0], pos[1], float('nan')))
        self.keys.append((f, pos, heading))
        self.keys.sort(key=lambda k: k[0])
        self._dist_cache = None
        return self

    def add(self, f0, f1, fn, fin=6, fout=6, w=1.0):
        self.clips.append(Clip(f0, f1, fn, fin, fout, w))
        return self

    def nowalk(self, f):
        w = 0.0
        for a, b in self.no_walk:
            w = max(w, envelope(f, a, b, 3, 3))
        return w

    def close_eyes(self, f0, f1):
        self.eyes_closed.append((f0, f1))

    # ---- root path ---------------------------------------------------------
    def _pos_keys(self):
        return [(f, p) for f, p, h in self.keys if p is not None]

    def raw_pos(self, f):
        ks = self._pos_keys()
        if not ks:
            return Vector((0, 0, 0))
        if f <= ks[0][0]:
            p = ks[0][1].copy()
        elif f >= ks[-1][0]:
            p = ks[-1][1].copy()
        else:
            i = max(j for j in range(len(ks)) if ks[j][0] <= f)
            f0, p0 = ks[i]
            f1, p1 = ks[i + 1]
            pm = ks[i - 1][1] if i > 0 else p0
            pn = ks[i + 2][1] if i + 2 < len(ks) else p1
            u = (f - f0) / (f1 - f0)
            if xy_eq(p0, p1):
                return p0.copy()
            if xy_eq(pm, p0):
                pm = p0 - (p1 - p0)
            if xy_eq(pn, p1):
                pn = p1 + (p1 - p0)
            # ease at hold points (segment endpoints where the actor stops)
            stop0 = i == 0 or xy_eq(ks[i - 1][1], p0)
            stop1 = i + 2 >= len(ks) or xy_eq(ks[i + 2][1], p1)
            if stop0 and stop1:
                u = smooth(u)
            elif stop0:
                u = u * u * (2 - u)
            elif stop1:
                u = u + u * u - u ** 3
            p = catmull(pm, p0, p1, pn, u)
        return p

    def pos(self, f):
        p = self.raw_pos(f)
        if math.isnan(p.z):
            p.z = ground(p.x, p.y)
        return p

    def heading(self, f):
        """heading in radians; 0 = facing -Y"""
        hk = [(k[0], k[2]) for k in self.keys if k[2] is not None]
        explicit = None
        if hk:
            if f <= hk[0][0]:
                explicit = D(hk[0][1])
            elif f >= hk[-1][0]:
                explicit = D(hk[-1][1])
            else:
                i = max(j for j in range(len(hk)) if hk[j][0] <= f)
                (f0, h0), (f1, h1) = hk[i], hk[i + 1]
                u = smooth((f - f0) / (f1 - f0))
                a0, a1 = D(h0), D(h1)
                explicit = a0 + wrap_angle(a1 - a0) * u
        # velocity-based heading while moving (blended by speed)
        v = self.vel(f)
        sp = Vector((v.x, v.y)).length
        if sp > 0.05 * self.c['stride'] and not self.face_explicit(f):
            vh = math.atan2(v.x, -v.y)
            if explicit is None:
                return vh
            w = smooth(sp / (0.5 * self.c['stride']))
            return explicit + wrap_angle(vh - explicit) * w
        if explicit is None:
            # last movement direction
            for df in range(0, 400, 4):
                v = self.vel(f - df)
                if Vector((v.x, v.y)).length > 1e-4:
                    return math.atan2(v.x, -v.y)
            return 0.0
        return explicit

    face_frames = None

    def face_explicit(self, f):
        """frames where explicit heading overrides velocity (e.g. backing up)"""
        if not self.face_frames:
            return False
        return any(a <= f <= b for a, b in self.face_frames)

    def vel(self, f):
        a, b = self.raw_pos(f - 1), self.raw_pos(f + 1)
        a.z = 0 if math.isnan(a.z) else a.z
        b.z = 0 if math.isnan(b.z) else b.z
        return (b - a) * 0.5 * FPS  # units per second

    def speed(self, f):
        v = self.vel(f)
        return Vector((v.x, v.y)).length

    def dist(self, f):
        """distance travelled along the ground up to frame f (for gait phase)"""
        if self._dist_cache is None:
            self._dist_cache = {}
        fi = int(math.floor(f))
        if fi not in self._dist_cache:
            # integrate from the first key
            start = int(self.keys[0][0]) - 1 if self.keys else 0
            d = 0.0
            prev = self.raw_pos(start)
            self._dist_cache[start] = 0.0
            for g in range(start + 1, fi + 1):
                if g in self._dist_cache:
                    d = self._dist_cache[g]
                    prev = self.raw_pos(g)
                    continue
                p = self.raw_pos(g)
                d += Vector((p.x - prev.x, p.y - prev.y)).length
                self._dist_cache[g] = d
                prev = p
        frac = f - fi
        d0 = self._dist_cache.get(fi, 0.0)
        p0, p1 = self.raw_pos(fi), self.raw_pos(fi + 1)
        return d0 + frac * Vector((p1.x - p0.x, p1.y - p0.y)).length

    def root_matrix(self, f):
        return Matrix.Translation(self.pos(f)) @ Matrix.Rotation(self.heading(f), 4, 'Z')

    def world_point(self, f, local):
        return self.root_matrix(f) @ (Vector(local) * self.scale)

    def head_world(self, f):
        return self.world_point(f, self.rest_head.get(self.c['head'], V(0, 0, self.c['height'] * 0.8)))

    # ---- pose evaluation ---------------------------------------------------
    def evaluate(self, f):
        pose = {}
        root_loc = V()
        root_rot = V()

        def addp(p, w):
            for b, rv in p.items():
                pose[b] = pose.get(b, V()) + rv * w

        # base pose
        base = {}
        for b, rv in self.c['base'].items():
            base[b] = rv
            m = mirror_name(b)
            if m:
                base[m] = mirror_rv(rv)
        addp(base, 1.0)
        # idle breathing
        t = f / FPS
        br = math.sin(t * 2 * math.pi / 3.2 + self.rng.random() * 0) * 0.5 + 0.5
        sp = self.c['spine']
        addp({sp[-1]: R(-2.0 * br), self.c['head']: R(1.5 * br)}, 1.0)
        # tail idle sway
        if self.c['tail']:
            ph = t * 2 * math.pi / 2.6
            for i, b in enumerate(self.c['tail']):
                addp({b: R(0, 0, 4 * math.sin(ph - i * 0.6))}, 1.0)
        # locomotion
        if not self.fly and self.keys:
            nw = self.nowalk(f)
            if nw < 1.0:
                loco, rl = self.locomotion(f)
                addp(loco, 1.0 - nw)
                root_loc += rl * (1.0 - nw)
        # clips
        for c in self.clips:
            w = envelope(f, c.f0, c.f1, c.fin, c.fout) * c.w
            if w <= 0:
                continue
            u = (f - c.f0) / max(1e-6, (c.f1 - c.f0))
            res = c.fn(self, f, u, (f - c.f0) / FPS)
            if res is None:
                continue
            p = res[0] if isinstance(res, tuple) else res
            addp(p, w)
            if isinstance(res, tuple):
                if len(res) > 1 and res[1] is not None:
                    root_loc += res[1] * w
                if len(res) > 2 and res[2] is not None:
                    root_rot += res[2] * w
        # blinks / closed eyes
        lid = self.lid_amount(f)
        if lid > 0:
            for b, rv in self.c['lids']:
                addp({b: rv, mirror_name(b): mirror_rv(rv)}, lid)
        return pose, root_loc, root_rot

    def lid_amount(self, f):
        for a, b in self.eyes_closed:
            if a <= f <= b:
                return min(1.0, (f - a) / 3.0 + 0.0, (b - f) / 4.0) if b - a > 8 else 1.0
        for bf in self.blinks:
            d = f - bf
            if 0 <= d <= 7:
                return [0.5, 1.0, 1.0, 0.7, 0.4, 0.15, 0.05, 0.0][int(d)]
        return 0.0

    def auto_blinks(self, f0, f1):
        f = f0 + self.rng.uniform(10, 50)
        while f < f1:
            self.blinks.append(int(f))
            if self.rng.random() < 0.15:
                self.blinks.append(int(f) + 9)
            f += self.rng.uniform(55, 110)

    def locomotion(self, f):
        c = self.c
        spd = self.speed(f)
        st = c['stride']
        # cycle speed ~ 1 stride per 0.75 s at "walk"
        walk_speed = st / 0.8
        w = smooth(spd / (0.35 * walk_speed))
        if w <= 0.001:
            return {}, V()
        run = smooth((spd - 1.3 * walk_speed) / (0.8 * walk_speed))
        stride = st * (1 + 0.6 * run)
        p = 2 * math.pi * self.dist(f) / stride
        pose = {}
        L = c['leg']
        A = D(c['legswing']) * (1 + 0.35 * run)
        K = D(c['knee']) * (1 + 0.4 * run)
        for side, ph in (('left', 0.0), ('right', math.pi)):
            q = p + ph
            thigh = -A * math.sin(q)
            knee = K * max(0.0, math.cos(q)) ** 1.5
            names = [n.replace('left_', side + '_') for n in L]
            pose[names[0]] = V(thigh - knee * 0.35, 0, 0)
            if len(names) > 1:
                pose[names[1]] = V(knee, 0, 0)
            if len(names) > 2:
                pose[names[2]] = V(-(thigh + knee * 0.65) * 0.6, 0, 0)
            # arms counter swing
            arm0 = c['arm'][0].replace('left_', side + '_')
            aa = D(c['armswing']) * (1 + 0.5 * run)
            pose[arm0] = V(aa * math.sin(q), 0, 0)
        loc = V(0, 0, c['bob'] * (1 + run) * (0.5 + 0.5 * math.cos(2 * p)) * self.scale)
        sp = c['spine']
        pose[c['hips']] = R(0, 0, 6 * math.sin(p))
        pose[sp[0]] = R(4 + 8 * run, 0, -5 * math.sin(p))
        if c['gait'] == 'waddle':
            roll = D(c.get('roll', 8))
            pose[c['waist']] = V(0, roll * math.sin(p), 0)
            pose[c['head']] = V(0, -roll * 0.6 * math.sin(p), 0)
        for k in pose:
            pose[k] = pose[k] * w
        return pose, loc * w

    # ---- analytic evaluation of bone transforms -----------------------------
    def eval_cached(self, f):
        if not hasattr(self, '_ev'):
            self._ev = {}
        if f not in self._ev:
            self._ev[f] = self.evaluate(f)
        return self._ev[f]

    def root_full(self, f):
        pose, rl, rr = self.eval_cached(f)
        M = self.root_matrix(f)
        base_q = M.to_quaternion()
        rot_extra = Quaternion(rr.normalized(), rr.length) if rr.length > 1e-9 else Quaternion()
        q = base_q @ rot_extra
        loc = M.translation + base_q @ rl
        return Matrix.Translation(loc) @ q.to_matrix().to_4x4() @ Matrix.Scale(self.scale, 4)

    def bone_matrix(self, f, bone):
        """world matrix of a pose bone at frame f (same math Blender uses)"""
        pose = self.eval_cached(f)[0]
        bones = self.arm.data.bones
        chain = []
        b = bones[bone]
        while b:
            chain.append(b)
            b = b.parent
        M = Matrix.Identity(4)
        for b in reversed(chain):
            rel = (b.parent.matrix_local.inverted() @ b.matrix_local) if b.parent else b.matrix_local.copy()
            rv = pose.get(b.name)
            if rv is not None and rv.length > 1e-9:
                q = Quaternion(rv.normalized(), rv.length)
                rq = self.rest[b.name]
                ql = rq.inverted() @ q @ rq
                M = M @ rel @ ql.to_matrix().to_4x4()
            else:
                M = M @ rel
        return self.root_full(f) @ M

    def bone_pos(self, f, bone, local=(0, 0, 0)):
        return self.bone_matrix(f, bone) @ Vector(local)

    # ---- baking ------------------------------------------------------------
    def bake(self, f0, f1, step=1):
        arm = self.arm
        arm.rotation_mode = 'QUATERNION'
        for pb in arm.pose.bones:
            pb.rotation_mode = 'QUATERNION'
        arm.animation_data_create()
        act = bpy.data.actions.new(arm.name + '_act')
        arm.animation_data.action = act
        frames = list(range(int(f0), int(f1) + 1, step))
        if frames[-1] != int(f1):
            frames.append(int(f1))
        data = {}          # path -> list of values per frame
        used = set()
        evals = [self.eval_cached(f) for f in frames]
        for pose, _, _ in evals:
            used |= set(k for k in pose if k in self.bones)
        for b in used:
            rq = self.rest[b]
            rqi = rq.inverted()
            vals = []
            for pose, _, _ in evals:
                rv = pose.get(b, V())
                ang = rv.length
                q = Quaternion(rv.normalized(), ang) if ang > 1e-9 else Quaternion()
                ql = rqi @ q @ rq
                vals.append(ql)
            # keep quaternion continuity
            for i in range(1, len(vals)):
                if vals[i].dot(vals[i - 1]) < 0:
                    vals[i].negate()
            path = f'pose.bones["{b}"].rotation_quaternion'
            for idx in range(4):
                fc = act.fcurves.new(path, index=idx, action_group=b)
                fc.keyframe_points.add(len(frames))
                co = []
                for fr, q in zip(frames, vals):
                    co += [fr, q[idx]]
                fc.keyframe_points.foreach_set('co', co)
                fc.keyframe_points.foreach_set('interpolation', [2] * len(frames))  # LINEAR... set below
                fc.update()
        # root object transform
        locs, rots = [], []
        for fr, (pose, rl, rr) in zip(frames, evals):
            M = self.root_matrix(fr)
            # local offsets (bob / jumps) in actor frame, then extra rotation
            rot_extra = Quaternion(rr.normalized(), rr.length) if rr.length > 1e-9 else Quaternion()
            base_q = M.to_quaternion()
            q = base_q @ rot_extra
            loc = M.translation + base_q @ rl
            locs.append(loc)
            rots.append(q)
        for i in range(1, len(rots)):
            if rots[i].dot(rots[i - 1]) < 0:
                rots[i].negate()
        for idx in range(3):
            fc = act.fcurves.new('location', index=idx, action_group='root')
            fc.keyframe_points.add(len(frames))
            co = []
            for fr, l in zip(frames, locs):
                co += [fr, l[idx]]
            fc.keyframe_points.foreach_set('co', co)
            fc.update()
        for idx in range(4):
            fc = act.fcurves.new('rotation_quaternion', index=idx, action_group='root')
            fc.keyframe_points.add(len(frames))
            co = []
            for fr, q in zip(frames, rots):
                co += [fr, q[idx]]
            fc.keyframe_points.foreach_set('co', co)
            fc.update()
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'
        arm.animation_data.action_slot = act.slots[0]
        arm.scale = (self.scale,) * 3
        return act


def xy_eq(a, b):
    return abs(a.x - b.x) < 1e-6 and abs(a.y - b.y) < 1e-6 and (a.z == b.z or (math.isnan(a.z) and math.isnan(b.z)))


def catmull(p0, p1, p2, p3, u):
    def comp(a, b, c, d):
        if any(math.isnan(x) for x in (a, b, c, d)):
            return float('nan')
        return 0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (-a + 3 * b - 3 * c + d) * u ** 3)
    return Vector((comp(p0.x, p1.x, p2.x, p3.x), comp(p0.y, p1.y, p2.y, p3.y), comp(p0.z, p1.z, p2.z, p3.z)))


# ---------------------------------------------------------------------------
# Loading characters into the current scene
# ---------------------------------------------------------------------------
def load_character(name, suffix=''):
    path = ROOT + f'models/blend/{name}.blend'
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.collections = [name.upper()]
    coll = dst.collections[0]
    if suffix:
        coll.name = name.upper() + suffix
    bpy.context.scene.collection.children.link(coll)
    arm = [o for o in coll.objects if o.type == 'ARMATURE'][0]
    return arm, coll
