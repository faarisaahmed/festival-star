# Action clips for rig.Actor.  Every factory returns fn(A, f, u, t) that
# yields a pose dict (bone -> rotation vector, armature rest frame) or a tuple
# (pose, root_loc_local, root_rotvec_local).  Conventions (see rig.py):
#   +X rot: legs swing back / head nods down / jaw opens / body pitches forward
#   +Y rot: LEFT arm/wing goes down        +Z rot: turn toward character's left
# Character faces -Y, its left is +X.
import math, random
from mathutils import Vector, Matrix
from rig import R, V, D, smooth, smoother, clamp, mirror_name, mirror_rv, FPS

TAU = 2 * math.pi


def sym(p):
    """add mirrored right-side entries for every left_ bone"""
    out = dict(p)
    for b, rv in p.items():
        m = mirror_name(b)
        if m and m not in p:
            out[m] = mirror_rv(rv)
    return out


def side(bone, s):
    return bone.replace('left_', s + '_') if s != 'left' else bone


def sidev(rv, s):
    return rv if s == 'left' else mirror_rv(rv)


def ramp(t, a, b):
    """0 before a, 1 after b, smooth in between"""
    return smooth((t - a) / (b - a)) if b > a else float(t >= a)


def bell(u, a=0.15, b=0.85):
    return min(ramp(u, 0, a), 1 - ramp(u, b, 1))


def _chain(A, key):
    return A.c.get(key) or []


def has(A, b):
    return b in A.bones


def put(p, A, bone, rv):
    if bone and has(A, bone):
        p[bone] = p.get(bone, V()) + rv
    return p


# ---------------------------------------------------------------------------
# face / head
# ---------------------------------------------------------------------------
def talk(amp=1.0, rate=4.2, seed=0):
    rng = random.Random(seed)
    ph = [rng.uniform(0, 6) for _ in range(3)]

    def fn(A, f, u, t):
        s = 0.5 + 0.5 * math.sin(t * TAU * rate + ph[0]) * (0.6 + 0.4 * math.sin(t * TAU * 1.3 + ph[1]))
        s *= 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * TAU * 0.7 + ph[2]))
        p = {}
        put(p, A, A.c['jaw'], R(22 * amp * s))
        put(p, A, A.c['head'], R(-3 * amp * s, 0, 2 * math.sin(t * 3)))
        return p
    return fn


def jaw(deg):
    return lambda A, f, u, t: put({}, A, A.c['jaw'], R(deg))


def _target(tgt, f):
    if callable(tgt):
        return Vector(tgt(f))
    if hasattr(tgt, 'head_world'):
        return tgt.head_world(f)
    return Vector(tgt)


def look(tgt, amount=1.0, body=0.25, pitch_scale=1.0):
    """turn head/neck (and a bit of spine) toward a world point / actor / fn(f)"""
    def fn(A, f, u, t):
        T = _target(tgt, f)
        M = A.root_matrix(f)
        loc = M.inverted() @ T
        h = A.rest_head.get(A.c['head'], V(0, 0, A.c['height'] * 0.8)) * A.scale
        d = loc - h
        yaw = math.atan2(d.x, -d.y)
        yaw = clamp(yaw, -D(120), D(120))
        hz = math.hypot(d.x, d.y)
        pitch = -math.atan2(d.z, max(hz, 1e-4)) * pitch_scale
        pitch = clamp(pitch, -D(55), D(45))
        p = {}
        neck = A.c['neck']
        sp = A.c['spine']
        yh = yaw * (1 - body) * amount
        ph = pitch * amount
        if neck:
            put(p, A, A.c['head'], V(ph * 0.55, 0, yh * 0.55))
            for n in neck:
                put(p, A, n, V(ph * 0.45 / len(neck), 0, yh * 0.45 / len(neck)))
        else:
            put(p, A, A.c['head'], V(ph, 0, yh))
        put(p, A, sp[-1], V(0, 0, yaw * body * amount))
        return p
    return fn


def nod(n=2, deg=14, period=0.45):
    def fn(A, f, u, t):
        s = math.sin(min(t / period, n) * TAU) if t / period < n else 0
        return put({}, A, A.c['head'], R(deg * max(0, s)))
    return fn


def shake(n=3, deg=18, period=0.35):
    def fn(A, f, u, t):
        s = math.sin(t / period * TAU) if t / period < n else 0
        return put({}, A, A.c['head'], R(0, 0, deg * s))
    return fn


def tilt(deg=14):
    """curious head tilt"""
    return lambda A, f, u, t: put({}, A, A.c['head'], R(0, deg, 0))


def smile_eyes(A, f, u, t):
    """happy squint: lids half closed"""
    p = {}
    for b, rv in A.c['lids']:
        p = sym(put(p, A, b, rv * 0.45))
    return p


def ears(deg_x=0, deg_y=0):
    def fn(A, f, u, t):
        p = {}
        e = _chain(A, 'ears')
        for i, b in enumerate(e):
            put(p, A, b, R(deg_x, deg_y) * (1.0 if i == 0 else 0.5))
        return sym(p)
    return fn


# ---------------------------------------------------------------------------
# arms
# ---------------------------------------------------------------------------
_ARM = {}


def _arm_rest(A):
    if A.name not in _ARM:
        a = A.c['arm']
        h0 = A.rest_head[a[0]]
        h1 = A.rest_head[a[1]] if len(a) > 1 else A.rest_head[a[0]] + V(1, 0, 0)
        if len(a) > 2 and (h1 - h0).length < 1e-4:
            h1 = A.rest_head[a[2]]
        d0 = (h1 - h0).normalized()
        base = A.c['base'].get(a[0], V())
        base_e = A.c['base'].get(a[1], V()) if len(a) > 1 else V()
        ax = d0.cross(V(0, -1, 0))
        if ax.length < 1e-3:
            ax = V(-1, 0, 0)
        _ARM[A.name] = (d0, base, ax.normalized(), base_e)
    return _ARM[A.name]


def arm_pose(A, s, up=-60.0, fwd=10.0, bend=0.0, twist=0.0):
    """absolute arm direction: up = elevation above horizontal (deg),
    fwd = swing from sideways (0) toward straight forward (90).
    bend = elbow bend (deg, forearm toward the front), twist about the arm."""
    d0, base, eax, base_e = _arm_rest(A)
    e, fw = math.radians(up), math.radians(fwd)
    d = V(math.cos(e) * math.cos(fw), -math.cos(e) * math.sin(fw), math.sin(e))
    q = d0.rotation_difference(d)
    rv = q.axis * q.angle if q.angle > 1e-6 else V()
    rv = rv - base + d * math.radians(twist)
    a = A.c['arm']
    p = {side(a[0], s): sidev(rv, s)}
    if len(a) > 1:
        p[side(a[1], s)] = sidev(eax * math.radians(bend), s)
    return {k: v for k, v in p.items() if has(A, k)}


def wave(s='left', up=65, rate=2.2, amp=25):
    def fn(A, f, u, t):
        w = math.sin(t * TAU * rate)
        p = arm_pose(A, s, up=up, fwd=25 + 12 * w, bend=35 + amp * w)
        return p
    return fn


def arms_up(deg=65, fwd=20, wiggle=0.0):
    def fn(A, f, u, t):
        p = {}
        for s in ('left', 'right'):
            w = math.sin(t * TAU * 3 + (0 if s == 'left' else 1.5)) * wiggle
            p.update(arm_pose(A, s, up=deg + w, fwd=fwd, bend=15))
        return p
    return fn


def arms_out(deg=10, fwd=30):
    def fn(A, f, u, t):
        p = {}
        for s in ('left', 'right'):
            p.update(arm_pose(A, s, up=deg, fwd=fwd, bend=10))
        return p
    return fn


def arms_forward(fwd=75, up=5, bend=25):
    """holding something out in front"""
    def fn(A, f, u, t):
        p = {}
        for s in ('left', 'right'):
            p.update(arm_pose(A, s, up=up, fwd=fwd, bend=bend, twist=-20))
        return p
    return fn


def arms_cross(A, f, u, t):
    p = {}
    for s in ('left', 'right'):
        p.update(arm_pose(A, s, up=-35, fwd=65, bend=95))
    return p


def point(s, tgt, extra_up=0):
    """point an arm toward a world target"""
    def fn(A, f, u, t):
        T = _target(tgt, f)
        M = A.root_matrix(f)
        d = M.inverted() @ T - V(0, 0, A.c['height'] * 0.6 * A.scale)
        yaw = math.degrees(math.atan2(d.x, -d.y))
        el = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
        sgn = 1 if s == 'left' else -1
        p = arm_pose(A, s, up=el * 0.8 + extra_up, fwd=clamp(90 - abs(yaw), 10, 90), bend=5)
        put(p, A, A.c['spine'][-1], R(0, 0, yaw * 0.25))
        return p
    return fn


def clap(rate=2.6):
    def fn(A, f, u, t):
        c = 0.5 + 0.5 * math.sin(t * TAU * rate)
        p = {}
        for s in ('left', 'right'):
            p.update(arm_pose(A, s, up=-10, fwd=60 + 20 * c, bend=30 + 30 * c, twist=-30))
        return p
    return fn


def rub_head(s='right', rate=2.5):
    """sheepish: hand behind head"""
    def fn(A, f, u, t):
        p = arm_pose(A, s, up=55, fwd=10, bend=110 + 12 * math.sin(t * TAU * rate))
        put(p, A, A.c['head'], R(8, 0, 0))
        return p
    return fn


# ---------------------------------------------------------------------------
# whole body
# ---------------------------------------------------------------------------
def pose(**bones):
    """static pose given as bone=R(...)"""
    return lambda A, f, u, t: sym({b: v for b, v in bones.items() if has(A, b)})


def lean(fwd=0.0, sideways=0.0):
    def fn(A, f, u, t):
        p = {}
        sp = A.c['spine']
        for b in sp:
            put(p, A, b, R(fwd / len(sp), sideways / len(sp), 0))
        return p
    return fn


def breathe_big(period=3.5, deg=5):
    def fn(A, f, u, t):
        s = 0.5 + 0.5 * math.sin(t * TAU / period)
        p = {}
        sp = A.c['spine']
        put(p, A, sp[-1], R(-deg * s))
        put(p, A, A.c['head'], R(deg * 0.5 * s))
        return p, V(0, 0, 0.004 * s * A.c['height'])
    return fn


def sad(A, f, u, t):
    p = {}
    put(p, A, A.c['head'], R(22, 0, 0))
    for n in A.c['neck']:
        put(p, A, n, R(8, 0, 0))
    put(p, A, A.c['spine'][-1], R(10, 0, 0))
    for s in ('left', 'right'):
        p.update(arm_pose(A, s, up=-75, fwd=15, bend=10))
    e = _chain(A, 'ears')
    for i, b in enumerate(e):
        put(p, A, b, R(18 if i == 0 else 6))
    for b, rv in A.c['lids']:
        put(p, A, b, rv * 0.35)
    return sym(p)


def happy_bounce(rate=2.0, h=0.06):
    """excited little bounce in place (root), arms up a bit"""
    def fn(A, f, u, t):
        s = abs(math.sin(t * TAU * rate / 2))
        p = {}
        for sd in ('left', 'right'):
            p.update(arm_pose(A, sd, up=10 + 40 * s, fwd=30, bend=30))
        for sd in ('left', 'right'):
            L = A.c['leg']
            put(p, A, side(L[0], sd), R(-25 * (1 - s)))
            if len(L) > 1:
                put(p, A, side(L[1], sd), R(40 * (1 - s)))
        return p, V(0, 0, h * s * A.c['height'])
    return fn


def hop(n=1, period=0.5, h=0.25, travel=None):
    """n hops (h in body heights); crouch before each"""
    def fn(A, f, u, t):
        k = t / period
        if k >= n:
            return {}
        ph = k % 1.0
        z = 4 * ph * (1 - ph)
        tuck = max(0, 1 - z * 1.6)
        p = {}
        L = A.c['leg']
        for sd in ('left', 'right'):
            put(p, A, side(L[0], sd), R(-30 * tuck))
            if len(L) > 1:
                put(p, A, side(L[1], sd), R(50 * tuck))
            p.update(arm_pose(A, sd, up=-30 + 80 * z, fwd=25, bend=25))
        return p, V(0, 0, h * A.c['height'] * z)
    return fn


def jump_arc(h, crouch=0.35, air_tuck=0.5):
    """a single jump across the clip (u 0..1): crouch-launch-air-land.
    Use with root keys for horizontal travel. h in metres."""
    def fn(A, f, u, t):
        a, b = crouch, 1 - 0.15  # air phase between a and b
        p = {}
        L = A.c['leg']
        if u < a:
            c = math.sin(u / a * math.pi) if u > a * 0.5 else smooth(u / (a * 0.5))
            c = smooth(u / a) if u < a * 0.7 else 1 - smooth((u - a * 0.7) / (a * 0.3))
            z = 0
            bend = c
        elif u < b:
            w = (u - a) / (b - a)
            z = 4 * w * (1 - w)
            bend = air_tuck * math.sin(w * math.pi)
        else:
            w = (u - b) / (1 - b)
            z = 0
            bend = math.sin(w * math.pi) * 0.8
        for sd in ('left', 'right'):
            put(p, A, side(L[0], sd), R(-45 * bend))
            if len(L) > 1:
                put(p, A, side(L[1], sd), R(80 * bend))
            if len(L) > 2:
                put(p, A, side(L[2], sd), R(-30 * bend))
            p.update(arm_pose(A, sd, up=-40 + 90 * z, fwd=30, bend=25))
        put(p, A, A.c['spine'][0], R(20 * bend))
        return p, V(0, 0, h * z - 0.12 * A.c['height'] * bend * (u < a or u > b))
    return fn


def crouch(amount=1.0):
    def fn(A, f, u, t):
        p = {}
        L = A.c['leg']
        for sd in ('left', 'right'):
            put(p, A, side(L[0], sd), R(-40 * amount))
            if len(L) > 1:
                put(p, A, side(L[1], sd), R(70 * amount))
            if len(L) > 2:
                put(p, A, side(L[2], sd), R(-30 * amount))
        put(p, A, A.c['spine'][0], R(15 * amount))
        return p, V(0, 0, -0.12 * A.c['height'] * amount)
    return fn


def surprised(A, f, u, t):
    """startle: little jump back, arms up, jaw open"""
    z = max(0.0, math.sin(min(t / 0.35, 1) * math.pi)) if t < 0.35 else 0
    p = {}
    put(p, A, A.c['jaw'], R(24))
    put(p, A, A.c['head'], R(-10))
    put(p, A, A.c['spine'][-1], R(-10))
    for sd in ('left', 'right'):
        p.update(arm_pose(A, sd, up=25, fwd=40, bend=50))
    e = _chain(A, 'ears')
    for b in e[:1]:
        put(p, A, b, R(-15))
    return sym(p), V(0, 0.15 * A.c['height'] * z, 0.12 * A.c['height'] * z)


def stretch(A, f, u, t):
    """morning stretch + yawn over the clip"""
    k = bell(u, 0.3, 0.75)
    p = {}
    for sd in ('left', 'right'):
        p.update({b: v * k for b, v in arm_pose(A, sd, up=80, fwd=15, bend=0).items()})
    put(p, A, A.c['spine'][-1], R(-18 * k))
    put(p, A, A.c['head'], R(-25 * k))
    put(p, A, A.c['jaw'], R(26 * bell(u, 0.4, 0.7)))
    for b, rv in A.c['lids']:
        put(p, A, b, rv * bell(u, 0.35, 0.75))
    return sym(p), V(0, 0, 0.04 * A.c['height'] * k)


def lie(side_deg=82, lift=0.2, curl=25):
    """lie on the side (sleeping). lift: fraction of height to raise root."""
    def fn(A, f, u, t):
        p = {}
        put(p, A, A.c['spine'][0], R(curl * 0.5))
        put(p, A, A.c['head'], R(curl * 0.6))
        L = A.c['leg']
        for sd in ('left', 'right'):
            put(p, A, side(L[0], sd), R(-50))
            if len(L) > 1:
                put(p, A, side(L[1], sd), R(60))
            p.update(arm_pose(A, sd, up=-50, fwd=50, bend=50))
        tl = A.c['tail']
        for i, b in enumerate(tl):
            put(p, A, b, R(0, 0, 14))
        return p, V(0, 0, lift * A.c['height']), R(0, side_deg, 0)
    return fn


def sleep(A, f, u, t):
    """eyes shut + slow deep breathing (combine with lie or crouch)"""
    s = 0.5 + 0.5 * math.sin(t * TAU / 3.8)
    p = {}
    put(p, A, A.c['spine'][-1], R(-4 * s))
    put(p, A, A.c['jaw'], R(3 * s))
    for b, rv in A.c['lids']:
        put(p, A, b, rv)
    return sym(p)


def kick(s='right', contact=0.45, power=1.0):
    """leg wind-up then kick through (contact at u=contact)"""
    def fn(A, f, u, t):
        L = A.c['leg']
        if u < contact:
            w = smooth(u / contact)
            th = 45 * w           # swing back
            kn = 60 * w
        else:
            w = (u - contact) / (1 - contact)
            sw = math.sin(min(1, w * 2.5) * math.pi / 2)
            th = 45 - (45 + 75 * power) * sw * (1 - smooth(max(0, w - 0.5) * 2))
            kn = 60 * (1 - sw) * (1 - smooth(max(0, w - 0.5) * 2))
        p = {}
        put(p, A, side(L[0], s), R(th))
        if len(L) > 1:
            put(p, A, side(L[1], s), R(kn))
        other = 'left' if s == 'right' else 'right'
        put(p, A, side(L[0], other), R(-10))
        put(p, A, A.c['spine'][0], R(-th * 0.15))
        p.update(arm_pose(A, other, up=-20, fwd=20 + th * 0.5, bend=20))
        p.update(arm_pose(A, s, up=-20, fwd=20 - th * 0.5, bend=20))
        return p
    return fn


def dance(rate=1.8, amp=1.0):
    def fn(A, f, u, t):
        s = math.sin(t * TAU * rate / 2)
        b = abs(math.sin(t * TAU * rate / 2))
        p = {}
        sp = A.c['spine']
        put(p, A, A.c['hips'], R(0, 10 * s * amp, 8 * s * amp))
        put(p, A, sp[-1], R(0, -12 * s * amp, 0))
        put(p, A, A.c['head'], R(0, 8 * s * amp, 0))
        p.update(arm_pose(A, 'left', up=20 + 45 * s * amp, fwd=25, bend=40))
        p.update(arm_pose(A, 'right', up=20 - 45 * s * amp, fwd=25, bend=40))
        L = A.c['leg']
        put(p, A, side(L[0], 'left'), R(-20 * max(0, s)))
        put(p, A, side(L[0], 'right'), R(-20 * max(0, -s)))
        return p, V(0, 0, 0.05 * A.c['height'] * b * amp)
    return fn


def spin(turns=1.0, h=0.0):
    def fn(A, f, u, t):
        w = smoother(u)
        z = 4 * u * (1 - u) * h
        return {}, V(0, 0, z * A.c['height']), R(0, 0, 360 * turns * w)
    return fn


def tail_wag(rate=3.0, deg=18):
    def fn(A, f, u, t):
        p = {}
        for i, b in enumerate(A.c['tail']):
            put(p, A, b, R(0, 0, deg * math.sin(t * TAU * rate - i * 0.7)))
        return p
    return fn


def sit(A, f, u, t):
    """sit on the ground: legs forward, body low"""
    p = {}
    L = A.c['leg']
    for sd in ('left', 'right'):
        put(p, A, side(L[0], sd), R(-80))
        if len(L) > 1:
            put(p, A, side(L[1], sd), R(20))
    put(p, A, A.c['spine'][0], R(-8))
    return p, V(0, 0, -0.2 * A.c['height'])


def ride(A, f, u, t):
    """sitting astride something (legs apart and forward)"""
    p = {}
    L = A.c['leg']
    for sd in ('left', 'right'):
        put(p, A, side(L[0], sd), sidev(R(-70, -25, 0), sd))
        if len(L) > 1:
            put(p, A, side(L[1], sd), R(45))
    return p


# ---------------------------------------------------------------------------
# flying / fire
# ---------------------------------------------------------------------------
def flap(rate=1.6, amp=1.0, glide=0.0, pitch=18):
    """wing flapping + dangling legs + forward pitch (root)"""
    def fn(A, f, u, t):
        p = {}
        w = _chain(A, 'wing')
        ph = t * TAU * rate
        s = math.sin(ph)
        a = amp * (1 - glide)
        wts = [1.0, 0.45, 0.25, 0.15, 0.1, 0.1]
        for i, b in enumerate(w):
            lag = i * 0.6
            k = wts[min(i, len(wts) - 1)]
            put(p, A, b, R(0, (42 * math.sin(ph - lag) - 5) * a * k + (-12 * glide if i == 0 else 0), 8 * math.cos(ph - lag) * a * k))
        w = sym(p)
        p = dict(w)
        L = A.c['leg']
        for sd in ('left', 'right'):
            put(p, A, side(L[0], sd), R(35))
            if len(L) > 1:
                put(p, A, side(L[1], sd), R(25))
        for i, b in enumerate(A.c['tail']):
            put(p, A, b, R(-6 + 4 * math.sin(ph - 1 - i * 0.4), 0, 0))
        p.update(arm_pose(A, 'left', up=-50, fwd=45, bend=40))
        p.update(arm_pose(A, 'right', up=-50, fwd=45, bend=40))
        bob = -0.05 * A.c['height'] * math.sin(ph) * a
        return p, V(0, 0, bob), R(pitch, 0, 0)
    return fn


def wings_spread(deg=-20):
    def fn(A, f, u, t):
        p = {}
        w = _chain(A, 'wing')
        for i, b in enumerate(w[:2]):
            put(p, A, b, R(0, deg if i == 0 else deg * 0.3, 0))
        return sym(p)
    return fn


def breathe_fire(A, f, u, t):
    k = bell(u, 0.1, 0.9)
    p = {}
    put(p, A, A.c['jaw'], R(32 * k))
    put(p, A, A.c['head'], R(-8 * k + 3 * math.sin(t * 20) * k))
    for n in A.c['neck']:
        put(p, A, n, R(6 * k))
    put(p, A, A.c['spine'][-1], R(10 * k))
    return p


def roar(A, f, u, t):
    k = bell(u, 0.2, 0.8)
    p = {}
    put(p, A, A.c['jaw'], R(30 * k))
    put(p, A, A.c['head'], R(-25 * k))
    for n in A.c['neck']:
        put(p, A, n, R(-8 * k))
    for sd in ('left', 'right'):
        p.update({b: v * k for b, v in arm_pose(A, sd, up=30, fwd=30, bend=50).items()})
    return p


def curl(A, f, u, t):
    """resting curled on the belly: deep crouch, head down on the ground,
    wings folded, tail wrapped around"""
    p = {}
    L = A.c['leg']
    for sd in ('left', 'right'):
        put(p, A, side(L[0], sd), R(-70))
        if len(L) > 1:
            put(p, A, side(L[1], sd), R(110))
        if len(L) > 2:
            put(p, A, side(L[2], sd), R(-40))
        p.update(arm_pose(A, sd, up=-60, fwd=70, bend=60))
    put(p, A, A.c['spine'][0], R(35))
    for n in A.c['neck']:
        put(p, A, n, R(12))
    put(p, A, A.c['head'], R(10))
    w = _chain(A, 'wing')
    wp = {}
    for i, b in enumerate(w[:2]):
        put(wp, A, b, R(0, 35 if i == 0 else 15, 30 if i == 0 else 10))
    p.update(sym(wp))
    for i, b in enumerate(A.c['tail']):
        put(p, A, b, R(8, 0, 22))
    return p, V(0, 0, -0.3 * A.c['height'])
