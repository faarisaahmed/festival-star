# THE FESTIVAL STAR  -  shot list (5:00 @ 24 fps)
#
# ACT I   morning   Pikachu wakes under the festival tree and gathers friends
# ACT II  midday    a ball game; Garchomp's super-kick knocks the Star into the lake
#                   Greninja rescues it but its light has gone out
# ACT III sunset    Pikachu's sparks can't relight it; Dragonite flies Pikachu to
#                   Charizard's peak; Charizard agrees to help
# ACT IV  night     Charizard's flame relights the Star, lanterns glow, fireworks
import math
from shotlib import *
from anim import *
import fx


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def face(a, b):
    """heading (deg) for something at a to face b"""
    return math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1])))


def head_of(A, f, up=0.0):
    return A.head_world(f) + Vector((0, 0, up))


def mid(A, f, k=0.55):
    p = A.pos(f)
    return p + Vector((0, 0, A.c['height'] * k * A.scale))


def looks(actors, tgt, f0, f1, fin=8, fout=8, amount=1.0):
    for A in actors:
        A.add(f0, f1, look(tgt, amount), fin, fout)


def ballistic(S, ob, p0, p1, f0, f1, apex, spin=(0, 0, 0), step=1, bounce=None):
    """key a projectile from p0 to p1 with an apex height above the higher end"""
    p0, p1 = Vector(p0), Vector(p1)
    top = max(p0.z, p1.z) + apex
    n = max(1, int((f1 - f0) / step))
    # solve parabola through p0 (u=0), apex, p1 (u=1)
    a0 = top - p0.z
    a1 = top - p1.z
    s = math.sqrt(a0) / (math.sqrt(a0) + math.sqrt(a1)) if (a0 + a1) > 0 else 0.5
    for i in range(n + 1):
        u = i / n
        f = f0 + (f1 - f0) * u
        xy = p0.lerp(p1, u)
        if u <= s:
            z = top - a0 * ((s - u) / s) ** 2 if s > 0 else p0.z
        else:
            z = top - a1 * ((u - s) / (1 - s)) ** 2
        rot = Euler((spin[0] * u, spin[1] * u, spin[2] * u))
        S.key_obj(ob, f, (xy.x, xy.y, z), rot)
    if ob.animation_data:
        for fc in ob.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'


def roll(S, ob, pts, f0, f1, radius, z_off=None):
    """roll along ground points (x,y) - keyed per frame, spinning like a wheel"""
    pts = [Vector((p[0], p[1])) for p in pts]
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + (b - a).length)
    tot = L[-1]
    for f in range(int(f0), int(f1) + 1):
        u = (f - f0) / (f1 - f0)
        u = u * (2 - u)  # decelerate
        d = tot * u
        i = max(j for j in range(len(L)) if L[j] <= d) if d < tot else len(L) - 2
        i = min(i, len(pts) - 2)
        w = (d - L[i]) / max(1e-6, L[i + 1] - L[i])
        p = pts[i].lerp(pts[i + 1], w)
        dirv = (pts[i + 1] - pts[i]).normalized()
        hd = math.atan2(dirv.y, dirv.x)
        z = H(p.x, p.y) + (radius if z_off is None else z_off)
        S.key_obj(ob, f, (p.x, p.y, z), Euler((0, d / radius, hd), 'XYZ'))
    for fc in ob.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'


def orbit(center, radius, h, a0, a1, lens, N, tgt_off=(0, 0, 0), ease=True):
    center = Vector(center)

    def fn(f):
        u = (f - 1) / max(1, N - 1)
        if ease:
            u = smooth(u)
        a = math.radians(a0 + (a1 - a0) * u)
        loc = center + Vector((math.sin(a) * radius, -math.cos(a) * radius, h))
        return loc, center + Vector(tgt_off), lens
    return fn


def star_scale(S, f, s=0.6):
    S.key_obj(S.obj('Star'), f, scale=s)


def star_at(S, f, loc, rot=(0, 0, 0)):
    S.key_obj(S.obj('Star'), f, loc, rot)


def hide_ball(S, f=1):
    S.key_obj(S.obj('Ball'), f, (0, 0, -50))


def setup_star(S, lit=True, home=True, glow=0.35):
    st = S.obj('Star')
    st.scale = (0.6,) * 3
    S.glow(1, star=glow if lit else 0.0, lantern=0.0)
    return st


def grass_at(S, p):
    S.grass_at = Vector(p)


def fwd_of(p, q):
    """unit ground vector from p toward q"""
    d = Vector((q[0] - p[0], q[1] - p[1], 0))
    return d.normalized()


def left_of(d):
    return Vector((-d.y, d.x, 0))


def front_cam(p, look_to, dist, side=0.0, h=0.3, lens=35):
    """camera in front of something at p that faces look_to"""
    d = fwd_of(p, look_to)
    P = Vector((p[0], p[1], H(p[0], p[1]) if len(p) < 3 else p[2]))
    return P + d * dist + left_of(d) * side + Vector((0, 0, h))


def bonfire(S, pos, f_on=1, scale=1.0):
    """festival bonfire: logs, animated flames, flickering warm light"""
    pos = Vector(pos)
    wood = bpy.data.materials.get('GiantBark') or fx.mat_smoke()
    for k in range(6):
        a = k / 6 * 2 * math.pi
        bpy.ops.mesh.primitive_cylinder_add(radius=0.07 * scale, depth=0.9 * scale, location=pos + Vector((math.cos(a) * 0.22, math.sin(a) * 0.22, 0.25)) * 1)
        lg = bpy.context.active_object
        lg.rotation_euler = (math.radians(55) * math.cos(a + 1.57) * 0, math.radians(60), a)
        lg.data.materials.append(wood)
    ring = bpy.data.materials.get('Rock')
    for k in range(10):
        a = k / 10 * 2 * math.pi
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.12 * scale, location=pos + Vector((math.cos(a) * 0.55, math.sin(a) * 0.55, 0.04)) * 1)
        st = bpy.context.active_object
        st.scale = (1.0, 0.8, 0.6)
        if ring:
            st.data.materials.append(ring)
    flame_m = bpy.data.materials.get('TailFlame')
    if flame_m is None:
        class _A: pass
    tm = _flame_material()
    for k, (dx, dy, s) in enumerate(((0, 0, 1.0), (0.12, 0.05, 0.7), (-0.1, 0.08, 0.75), (0.03, -0.12, 0.65), (-0.05, -0.02, 0.5))):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.22 * scale * s, location=pos + Vector((dx, dy, 0.35 + 0.25 * s)) * 1)
        fl = bpy.context.active_object
        fl.scale = (1.0, 1.0, 2.6)
        fl.data.materials.append(tm)
        fl.visible_shadow = False
        fl.scale = (0.0, 0.0, 0.0)
        fl.keyframe_insert('scale', frame=f_on - 1)
        fl.scale = (1.0, 1.0, 2.6)
        fl.keyframe_insert('scale', frame=f_on + 6)
    li = bpy.data.lights.new('Bonfire', 'POINT')
    li.color = (1.0, 0.55, 0.22)
    li.shadow_soft_size = 0.3
    li.energy = 0
    li.keyframe_insert('energy', frame=f_on - 1)
    li.energy = 260 * scale
    li.keyframe_insert('energy', frame=f_on + 6)
    fc = li.animation_data.action.fcurves[0]
    m = fc.modifiers.new('NOISE')
    m.strength = 90 * scale
    m.scale = 2.0
    lo = bpy.data.objects.new('Bonfire', li)
    lo.location = pos + Vector((0, 0, 0.8))
    S.sc.collection.objects.link(lo)
    S.post.append(lambda: fx.smoke(lambda f: pos + Vector((0, 0, 1.3)), f_on + 6, S.N, 10, 123, 0.18, 0.6, (0.25, 0.23, 0.22), 0.25, 60, (0.1, 0.05, 0)))


def _flame_material():
    m = bpy.data.materials.get('BonfireFlame')
    if m:
        return m
    m = bpy.data.materials.new('BonfireFlame')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (3, 3, 1.2)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    d = mp.inputs['Location'].driver_add('default_value', 2).driver
    d.expression = '-frame*0.09'
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.noise_dimensions = '4D'
    nz.inputs['Scale'].default_value = 2.5
    nz.inputs['Detail'].default_value = 4
    nt.links.new(mp.outputs[0], nz.inputs['Vector'])
    d2 = nz.inputs['W'].driver_add('default_value').driver
    d2.expression = 'frame/9'
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    hgt = nt.nodes.new('ShaderNodeMath')
    hgt.operation = 'MULTIPLY_ADD'
    nt.links.new(nz.outputs['Fac'], hgt.inputs[0])
    hgt.inputs[1].default_value = 1.0
    inv = nt.nodes.new('ShaderNodeMath')
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    nt.links.new(sep.outputs['Z'], inv.inputs[1])
    nt.links.new(inv.outputs[0], hgt.inputs[2])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.55
    ramp.color_ramp.elements[0].color = (0.8, 0.12, 0.01, 1)
    ramp.color_ramp.elements[1].position = 1.25
    ramp.color_ramp.elements[1].color = (1.0, 0.92, 0.6, 1)
    e = ramp.color_ramp.elements.new(0.85)
    e.color = (1.0, 0.45, 0.05, 1)
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = 0.0
    mr.inputs['From Max'].default_value = 1.6
    nt.links.new(hgt.outputs[0], mr.inputs['Value'])
    nt.links.new(mr.outputs[0], ramp.inputs[0])
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 18
    nt.links.new(ramp.outputs[0], em.inputs['Color'])
    al = nt.nodes.new('ShaderNodeMapRange')
    al.inputs['From Min'].default_value = 0.75
    al.inputs['From Max'].default_value = 1.05
    nt.links.new(hgt.outputs[0], al.inputs['Value'])
    lw = nt.nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.4
    fi = nt.nodes.new('ShaderNodeMath')
    fi.operation = 'SUBTRACT'
    fi.inputs[0].default_value = 1.0
    nt.links.new(lw.outputs['Facing'], fi.inputs[1])
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    mul.use_clamp = True
    nt.links.new(al.outputs[0], mul.inputs[0])
    nt.links.new(fi.outputs[0], mul.inputs[1])
    mul2 = nt.nodes.new('ShaderNodeMath')
    mul2.operation = 'MULTIPLY'
    mul2.use_clamp = True
    nt.links.new(mul.outputs[0], mul2.inputs[0])
    mul2.inputs[1].default_value = 2.5
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(mul2.outputs[0], mx.inputs['Fac'])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    m.surface_render_method = 'BLENDED'
    return m


def star_pos_fn(st):
    return lambda f: _ballpos(st, f)

# ---------------------------------------------------------------------------
# ACT I - MORNING
# ---------------------------------------------------------------------------
@shot('s01_aerial', 14, 'morning', samples=16)
def s01(S):
    """dawn flyover of the island toward the festival tree; title"""
    setup_star(S, glow=0.5)
    S.camera(28, 0)
    N = S.N
    path = [(1, (-160, -260, 95), (-20, 40, 10)), (N * 0.55, (-40, -120, 55), (0, 34, 10)),
            (N, (8, -38, 16), (0, 34, 12))]
    S.cam_keys([(int(f), Vector(p), Vector(t), 28 if i < 2 else 30) for i, (f, p, t) in enumerate(path)])
    S.fade_title('The Festival Star', 50, 230, size=0.085, y=0.05, fin=8, fout=8)
    grass_at(S, (0, 20, 0))
    fx.twinkles(lambda f: STAR_HOME, 1, N, 1.2, 10, 3)


@shot('s02_crown', 8, 'morning')
def s02(S):
    """tree crown and the Star catching the sun; tilt down to sleeping Pikachu"""
    setup_star(S, glow=0.45)
    P = S.actor('pikachu', blink=False)
    P.key(1, (BLANKET.x - 0.3, BLANKET.y - 0.2), 70)
    P.add(1, S.N, lie(80, 0.18, 25), 0, 0)
    P.add(1, S.N, sleep, 0, 0)
    P.close_eyes(0, S.N + 1)
    S.camera(30, 4)
    b = BLANKET + Vector((-0.3, -0.2, 0.15))
    S.cam_keys([(1, TREE + Vector((9, -24, 15.5)), STAR_HOME + Vector((0, 0, -0.3)), 60),
                (80, TREE + Vector((9, -23, 13.5)), STAR_HOME + Vector((0, 0, -3.0)), 55),
                (135, TREE + Vector((9, -20, 3.0)), TREE + Vector((1, -6, 3.5)), 40),
                (S.N, b + Vector((1.2, -2.2, 0.5)), b, 40)])
    fx.twinkles(lambda f: STAR_HOME, 1, S.N, 1.0, 12, 5)
    grass_at(S, BLANKET)


@shot('s03_wake', 7, 'morning')
def s03(S):
    """Pikachu wakes, sits up, stretches and yawns"""
    setup_star(S)
    P = S.actor('pikachu', blink=False)
    p = (BLANKET.x - 0.3, BLANKET.y - 0.2)
    P.key(1, p, 70)
    P.key(60, p, 70)
    P.key(80, p, 20)
    P.add(1, 40, lie(80, 0.18, 25), 0, 14)
    P.add(1, 40, sleep, 0, 6)
    P.close_eyes(0, 34)
    P.blinks += [52, 70, 112]
    P.add(44, 112, stretch, 6, 8)
    P.add(112, S.N, look(STAR_HOME), 10, 0)
    S.camera(45, 2.0)
    b = BLANKET + Vector((-0.3, -0.2, 0.2))
    S.cam_keys([(1, b + Vector((1.3, -1.6, 0.35)), b + Vector((0, 0, -0.05)), 45),
                (S.N, b + Vector((1.0, -1.35, 0.3)), b + Vector((0, 0, 0.05)), 45)])
    S.shake(0.004)
    grass_at(S, BLANKET)


@shot('s04_excited', 6, 'morning')
def s04(S):
    """Pikachu gazes up at the Star, cheeks spark with excitement, dashes off"""
    setup_star(S)
    P = S.actor('pikachu')
    p = Vector((BLANKET.x - 0.3, BLANKET.y - 0.2))
    hd = face(p, STAR_HOME)
    P.key(1, p, hd)
    P.key(72, p, hd)
    P.key(100, p + Vector((-0.8, -2.8)))
    P.key(S.N, p + Vector((-2.0, -7.5)))
    P.add(1, 76, look(STAR_HOME), 0, 8)
    P.add(18, 64, happy_bounce(2.2, 0.12), 6, 6)
    P.add(18, 64, smile_eyes, 4, 4)
    P.add(40, 64, arms_up(55, 30), 6, 6)
    S.post.append(lambda: fx.sparks(lambda f: P.head_world(f) + Vector((0, 0, -0.06)), 24, 64, 0.22, 6, 7))
    S.camera(40, 2.4)
    d = Vector((math.sin(math.radians(hd)), -math.cos(math.radians(hd)), 0))  # Pikachu's forward
    c = Vector((p.x, p.y, H(p.x, p.y) + 0.28))
    S.cam_keys([(1, c + d * 1.25 + Vector((0.35, 0, -0.1)), c, 42),
                (72, c + d * 1.1 + Vector((0.3, 0, -0.08)), c + Vector((0, 0, 0.03)), 42),
                (S.N, c + d * 1.1 + Vector((0.3, 0, 0.05)), c + Vector((-1.4, -5.0, -0.1)), 42)])
    grass_at(S, BLANKET)


@shot('s05_run', 5, 'morning')
def s05(S):
    """low tracking shot: Pikachu racing through the meadow grass"""
    setup_star(S)
    P = S.actor('pikachu')
    pts = [(8, 14), (5, 6), (0, -1), (-8, -5)]
    for i, q in enumerate(pts):
        P.key(1 + int(i * (S.N - 1) / 3), q)

    def cam(f):
        p = P.pos(f)
        v = P.vel(f)
        d = Vector((v.x, v.y, 0)).normalized() if v.length > 0.1 else Vector((0, -1, 0))
        side = Vector((-d.y, d.x, 0))
        loc = p - side * 1.4 + d * 0.9 + Vector((0, 0, 0.25))
        return loc, p + Vector((0, 0, 0.22)) + d * 0.2, 35
    S.cam_fn(cam)
    S.camera(35, 2.0)
    S.shake(0.01, 1.2)
    grass_at(S, (2, 4, 0))


LAKE_P = Vector((-30.3, -13.1))   # Piplup in ankle-deep water
LAKE_S = Vector((-28.6, -12.5))   # Sobble on the sand


@shot('s06_lake', 13, 'morning')
def s06(S):
    """lake: Piplup splashes in the shallows; a belly-flop soaks Sobble, who bursts into tears"""
    setup_star(S)
    Pp = S.actor('piplup')
    Sb = S.actor('sobble')
    wz = T.LAKE_LEVEL
    hp = face(LAKE_P, LAKE_S)
    Pp.key(1, (LAKE_P.x - 0.6, LAKE_P.y - 0.5), hp + 40)
    Pp.key(70, (LAKE_P.x, LAKE_P.y), hp)
    Pp.key(S.N, (LAKE_P.x, LAKE_P.y), hp)
    Pp.add(1, 120, wave('left', 15, 3.2, 40), 6, 6)
    Pp.add(1, 120, wave('right', 15, 3.2, 40), 6, 6)
    Pp.add(20, 110, hop(4, 0.75, 0.25), 3, 3)
    Pp.add(20, 120, smile_eyes, 4, 4)
    Pp.add(150, 196, jump_arc(0.7, 0.35, 0.8), 3, 3)
    Pp.add(196, 214, crouch(0.6), 2, 8)
    Pp.add(210, S.N, look(lambda f: Sb.head_world(f)), 6, 0)
    Pp.add(228, S.N, rub_head('left'), 8, 0)
    for f in (38, 56, 74, 92):
        S.post.append(lambda f=f: fx.splash((LAKE_P.x, LAKE_P.y, wz), f, 0.35, 14, f, water_z=wz, rings=1))
    S.post.append(lambda: fx.splash((LAKE_P.x + 0.1, LAKE_P.y + 0.1, wz), 196, 1.3, 70, 2, water_z=wz))
    # Sobble watches, laughs, gets soaked, cries
    hs = face(LAKE_S, LAKE_P)
    Sb.key(1, (LAKE_S.x, LAKE_S.y), hs)
    Sb.add(1, 200, look(lambda f: Pp.head_world(f)), 0, 6)
    Sb.add(40, 140, happy_bounce(2.0, 0.08), 8, 8)
    Sb.add(40, 140, smile_eyes, 6, 6)
    Sb.add(40, 140, talk(0.6, 3.5, 2), 6, 6)
    Sb.add(204, 218, surprised, 2, 6)
    Sb.add(218, S.N, sad, 8, 0)
    Sb.add(218, S.N, talk(0.8, 5.5, 3), 8, 0)
    Sb.close_eyes(222, S.N + 2)
    Sb.tear_obj.hide_render = True
    Sb.tear_obj.keyframe_insert('hide_render', frame=1)
    Sb.tear_obj.hide_render = False
    Sb.tear_obj.keyframe_insert('hide_render', frame=222)
    el, er = eye_points(Sb)
    hb = Sb.c['head']

    def tears():
        fx.tears(lambda f: Sb.bone_matrix(f, hb) @ el, 222, S.N, lambda f: (Sb.bone_matrix(f, hb).to_3x3() @ Vector((1, 0, 0))).normalized(), 2, 31)
        fx.tears(lambda f: Sb.bone_matrix(f, hb) @ er, 223, S.N, lambda f: (Sb.bone_matrix(f, hb).to_3x3() @ Vector((-1, 0, 0))).normalized(), 2, 32)
        fx.splash((LAKE_S.x - 0.2, LAKE_S.y, H(*LAKE_S) + 1.2), 204, 0.3, 30, 3, water_z=H(*LAKE_S) - 5, rings=0)
    S.post.append(tears)
    S.camera(42, 3.0)
    c = Vector(((LAKE_P.x + LAKE_S.x) / 2, (LAKE_P.y + LAKE_S.y) / 2, wz + 0.3))
    S.cam_keys([(1, c + Vector((1.9, -2.9, 0.35)), c + Vector((-0.3, 0.0, 0.0)), 40),
                (160, c + Vector((1.6, -2.6, 0.3)), c + Vector((-0.2, 0.1, 0.05)), 42),
                (S.N, c + Vector((1.9, -1.6, 0.25)), Vector((LAKE_S.x, LAKE_S.y, H(*LAKE_S) + 0.25)), 50)])
    grass_at(S, (-26, -12, 0))


@shot('s07_arrive', 7, 'morning')
def s07(S):
    """Pikachu arrives waving; Sobble cheers up; the three hop and run off"""
    setup_star(S)
    P = S.actor('pikachu')
    Pp = S.actor('piplup')
    Sb = S.actor('sobble')
    sb = LAKE_S
    pp = LAKE_P
    pk_stop = sb + Vector((0.95, -0.35))
    P.key(1, (sb.x + 5, sb.y + 1.0))
    P.key(40, (pk_stop.x, pk_stop.y))
    P.key(120, (pk_stop.x, pk_stop.y), face(pk_stop, sb))
    P.key(S.N, (sb.x + 6, sb.y + 4.5))
    P.face_frames = [(40, 120)]
    P.add(36, 80, wave('left', 70, 2.5, 30), 6, 8)
    P.add(40, 125, look(lambda f: Sb.head_world(f)), 6, 6)
    P.add(84, 120, hop(2, 0.7, 0.3), 2, 2)
    Pp.key(1, (pp.x, pp.y), face(pp, sb))
    Pp.key(30, (pp.x + 0.6, pp.y + 0.1), face(pp, sb))
    Pp.key(120, (pp.x + 0.6, pp.y + 0.1), face(pp, pk_stop))
    Pp.key(S.N, (sb.x + 5, sb.y + 5.5))
    Pp.add(1, 125, look(lambda f: P.head_world(f)), 6, 6)
    Pp.add(84, 120, hop(2, 0.7, 0.3), 2, 2)
    Sb.key(1, (sb.x, sb.y), face(sb, pp))
    Sb.key(40, (sb.x, sb.y), face(sb, pk_stop))
    Sb.key(120, (sb.x, sb.y), face(sb, pk_stop))
    Sb.key(S.N, (sb.x + 5.5, sb.y + 5))
    Sb.add(1, 50, sad, 0, 10)
    Sb.add(30, 125, look(lambda f: P.head_world(f)), 8, 6)
    Sb.add(60, 120, smile_eyes, 6, 6)
    Sb.add(84, 120, hop(2, 0.7, 0.35), 2, 2)
    S.camera(40, 3.0)
    c = Vector((sb.x - 0.3, sb.y - 0.2, H(*sb) + 0.22))
    S.cam_keys([(1, c + Vector((0.6, -3.4, 0.3)), c + Vector((0.6, 0.0, 0.0)), 38),
                (110, c + Vector((0.4, -3.2, 0.3)), c + Vector((0.2, 0.0, 0.0)), 38),
                (S.N, c + Vector((0.6, -3.0, 0.7)), c + Vector((3.0, 3.0, 0.1)), 34)])
    grass_at(S, (sb.x + 2, sb.y + 2, 0))


GAME = Vector((13.0, 14.0))     # where the ball game happens (meadow, NE)
ROCK_TOP = Vector((ROCK.x - 0.5, ROCK.y - 1.0, H(ROCK.x - 0.5, ROCK.y - 1.0)))


@shot('s08_raboot', 7, 'morning')
def s08(S):
    """Raboot juggles the ball; Greninja watches from atop its rock"""
    setup_star(S)
    Rb = S.actor('raboot')
    Gr = S.actor('greninja')
    ball = S.obj('Ball')
    rb = GAME
    Rb.key(1, (rb.x, rb.y), face(rb, (rb.x - 1, rb.y - 3)))
    g = H(rb.x, rb.y)
    foot = Vector((rb.x - 0.1, rb.y - 0.25, g))
    # juggling: kick every 18 frames, alternating feet
    f = 1
    k = 0
    while f + 18 <= S.N:
        s = 'right' if k % 2 == 0 else 'left'
        Rb.add(f + 2, f + 20, kick(s, 0.5, 0.35), 2, 2)
        ballistic(S, ball, foot + Vector((0, 0, 0.18)), foot + Vector((0.02 * (-1) ** k, 0, 0.18)), f + 11, f + 29, 0.9, (3, 0, 1))
        f += 18
        k += 1
    Rb.add(1, S.N, look(lambda f: ball.location.copy() if False else foot + Vector((0, 0, 0.7))), 0, 0, 0.5)
    Gr.key(1, (ROCK_TOP.x, ROCK_TOP.y, ROCK_TOP.z), face(ROCK_TOP, rb))
    Gr.add(1, S.N, arms_cross, 0, 0)
    Gr.add(1, S.N, look((rb.x, rb.y, g + 0.6), 0.8), 0, 0)
    S.camera(50, 2.8)
    c = Vector((rb.x, rb.y, g + 0.6))
    S.cam_keys([(1, c + Vector((2.2, -3.6, -0.15)), c + Vector((0, 0, 0.1)), 45),
                (S.N * 0.6, c + Vector((2.0, -3.3, -0.1)), c + Vector((0.2, 0, 0.25)), 45),
                (S.N, c + Vector((2.6, -4.2, 0.3)), ROCK_TOP + Vector((0, 0, 1.2)), 45)])
    grass_at(S, (rb.x, rb.y, g))


@shot('s09_pass', 6, 'morning')
def s09(S):
    """friends arrive; Raboot passes to Pikachu, who bounces it back off its head"""
    setup_star(S)
    Rb = S.actor('raboot')
    P = S.actor('pikachu')
    Pp = S.actor('piplup')
    Sb = S.actor('sobble')
    ball = S.obj('Ball')
    rb = GAME
    g = H(rb.x, rb.y)
    pk = rb + Vector((-2.2, -1.2))
    Rb.key(1, (rb.x, rb.y), face(rb, pk))
    P.key(1, (pk.x - 3, pk.y - 3))
    P.key(40, (pk.x, pk.y))
    P.key(S.N, (pk.x, pk.y), face(pk, rb))
    Pp.key(1, (pk.x - 4.5, pk.y - 3.0))
    Pp.key(60, (pk.x - 0.8, pk.y - 0.7))
    Pp.key(S.N, (pk.x - 0.8, pk.y - 0.7), face(pk, rb))
    Sb.key(1, (pk.x - 4.0, pk.y - 4.5))
    Sb.key(64, (pk.x + 0.2, pk.y - 1.1))
    Sb.key(S.N, (pk.x + 0.2, pk.y - 1.1), face(pk, rb))
    Rb.add(44, 70, kick('right', 0.5, 0.8), 3, 3)
    Rb.add(1, S.N, look(lambda f: P.head_world(f)), 6, 6)
    Rb.add(40, 60, wave('left', 60, 2.5, 20), 4, 4)
    kick_p = Vector((rb.x - 0.2, rb.y - 0.2, g + 0.16))
    S.key_obj(ball, 1, kick_p)
    S.key_obj(ball, 56, kick_p)
    ballistic(S, ball, kick_p, Vector((pk.x, pk.y, g + 0.55)), 57, 84, 1.6, (6, 0, 2))
    P.add(76, 96, hop(1, 0.8, 0.45), 2, 2)
    ballistic(S, ball, Vector((pk.x, pk.y, g + 0.55)), kick_p + Vector((0.1, 0.1, 0.3)), 84, 118, 2.2, (8, 2, 0))
    ballistic(S, ball, kick_p + Vector((0.1, 0.1, 0.3)), kick_p + Vector((0.5, 1.2, 0)), 118, S.N, 0.3, (2, 0, 0))
    Rb.add(110, 126, kick('left', 0.5, 0.4), 2, 2)
    looks([Pp, Sb], lambda f: _ballpos(ball, f), 50, S.N)
    S.camera(34, 3.2)
    c = Vector(((rb.x + pk.x) / 2, (rb.y + pk.y) / 2, g + 0.4))
    S.cam_keys([(1, c + Vector((0.6, -4.0, 0.2)), c + Vector((-0.6, 0, 0)), 32),
                (S.N, c + Vector((1.0, -3.6, 0.3)), c + Vector((0.2, 0, 0.1)), 32)])
    grass_at(S, c)


# ---------------------------------------------------------------------------
# shared staging for the ball game (ACT II)
# ---------------------------------------------------------------------------
SPOT = {
    'raboot': Vector((13.0, 14.0)),
    'pikachu': Vector((10.4, 12.4)),
    'piplup': Vector((9.6, 11.3)),
    'sobble': Vector((10.9, 10.9)),
    'greninja': Vector((12.6, 10.4)),
    'garchomp': Vector((16.2, 11.0)),
    'dragonite': Vector((16.8, 14.9)),
}
RING_C = Vector((13.0, 12.6))


def gpos(n, dx=0.0, dy=0.0):
    p = SPOT[n]
    return Vector((p.x + dx, p.y + dy, H(p.x + dx, p.y + dy)))


def cast(S, names, face_to=RING_C, look_at=None):
    out = {}
    for n in names:
        A = S.actor(n)
        p = SPOT[n]
        A.key(1, (p.x, p.y), face(p, face_to))
        out[n] = A
    return out


def leap(A, pts, f0, f1, apex, flip=0.0, tuck=0.6):
    """airborne arc from ground point p0 to p1 (Vector3); keys every frame"""
    p0, p1 = pts
    top = max(p0.z, p1.z) + apex
    a0, a1 = top - p0.z, top - p1.z
    sp = math.sqrt(a0) / (math.sqrt(a0) + math.sqrt(a1))
    hd = face(p0, p1)
    for f in range(int(f0), int(f1) + 1):
        u = (f - f0) / (f1 - f0)
        xy = p0.lerp(p1, u)
        z = top - a0 * ((sp - u) / sp) ** 2 if u <= sp else top - a1 * ((u - sp) / (1 - sp)) ** 2
        A.key(f, (xy.x, xy.y, z), hd)
    A.no_walk.append((f0 - 2, f1 + 2))

    def air(A_, f, u, t):
        k = math.sin(u * math.pi)
        p = {}
        L = A_.c['leg']
        for sd in ('left', 'right'):
            put(p, A_, side(L[0], sd), R(-50 * tuck * k))
            if len(L) > 1:
                put(p, A_, side(L[1], sd), R(90 * tuck * k))
            p.update(arm_pose(A_, sd, up=-10 + 50 * k, fwd=40, bend=40))
        return p, None, R(360 * flip * smoother(u), 0, 0)
    A.add(f0, f1, air, 2, 2)
    A.add(f0 - 10, f0 + 1, crouch(0.8), 4, 1)
    A.add(f1 - 1, f1 + 12, crouch(0.9), 1, 6)


def fly_keys(A, keys):
    """keys: list of (f, (x,y,z)) absolute; heading follows velocity"""
    A.fly = True
    for f, p in keys:
        A.key(f, p)


# ---------------------------------------------------------------------------
# ACT I (cont.)
# ---------------------------------------------------------------------------
@shot('s10_leap', 5, 'morning')
def s10(S):
    """Greninja leaps from its rock in one huge bound and lands by the group"""
    setup_star(S)
    Gr = S.actor('greninja')
    P = S.actor('pikachu')
    Rb = S.actor('raboot')
    P.key(1, (SPOT['pikachu'].x, SPOT['pikachu'].y), face(SPOT['pikachu'], ROCK_TOP))
    Rb.key(1, (SPOT['raboot'].x, SPOT['raboot'].y), face(SPOT['raboot'], ROCK_TOP))
    land = gpos('greninja')
    Gr.key(1, (ROCK_TOP.x, ROCK_TOP.y, ROCK_TOP.z), face(ROCK_TOP, land))
    Gr.key(20, (ROCK_TOP.x, ROCK_TOP.y, ROCK_TOP.z), face(ROCK_TOP, land))
    leap(Gr, (ROCK_TOP, land), 22, 72, 5.0, flip=1.0)
    Gr.key(S.N, (land.x, land.y), face(land, RING_C))
    Gr.add(84, S.N, arms_cross, 8, 0)
    Gr.add(90, S.N, nod(1, 12, 0.6), 2, 2)
    for A in (P, Rb):
        A.add(1, S.N, look(lambda f: Gr.head_world(f)), 0, 0)
        A.add(74, 100, surprised, 2, 8)
    S.camera(40, 0)
    base = land + Vector((-4.0, -5.5, 0.9))

    def cam(f):
        g = Gr.pos(min(max(f, 1), S.N)) + Vector((0, 0, 0.9))
        u = smooth((f - 1) / (S.N - 1))
        return base + Vector((0, 0, 0.6 * (1 - u))), g, 48 - 16 * u
    S.cam_fn(cam, step=2)
    grass_at(S, land)


@shot('s11_bigfriends', 10, 'morning')
def s11(S):
    """the ground rumbles: Garchomp sprints in and skids to a halt; Dragonite glides down and waves"""
    setup_star(S)
    cs = cast(S, ['pikachu', 'raboot', 'piplup', 'sobble', 'greninja'])
    Gc = S.actor('garchomp')
    Dn = S.actor('dragonite')
    g = SPOT['garchomp']
    Gc.key(1, (g.x + 26, g.y - 18))
    Gc.key(52, (g.x + 3.0, g.y - 1.5))
    Gc.key(64, (g.x, g.y))
    Gc.key(S.N, (g.x, g.y), face(g, RING_C))
    Gc.add(56, 80, lean(-25), 4, 10)
    Gc.add(84, 150, roar, 6, 10)
    S.post.append(lambda: fx.smoke(lambda f: Gc.pos(f) + Vector((0, 0, 0.1)), 20, 70, 3, 5, 0.25, 0.4, (0.45, 0.38, 0.28), 0.45, 30))
    d = SPOT['dragonite']
    dz = H(d.x, d.y)
    fly_keys(Dn, [(1, (d.x - 30, d.y + 25, dz + 22)), (90, (d.x - 8, d.y + 6, dz + 7)), (140, (d.x, d.y, dz + 0.9)), (160, (d.x, d.y, dz))])
    Dn.key(S.N, (d.x, d.y, dz), face(d, RING_C))
    Dn.face_frames = [(150, S.N)]
    Dn.add(1, 150, flap(1.3, 1.0, 0.0, 15), 0, 10)
    Dn.add(150, 168, crouch(0.6), 4, 6)
    Dn.add(168, S.N, wave('left', 60, 2.0, 30), 8, 0)
    Dn.add(168, S.N, smile_eyes, 6, 0)
    for n, A in cs.items():
        A.add(1, 100, look(lambda f: Gc.head_world(f)), 0, 8)
        A.add(100, S.N, look(lambda f: Dn.head_world(f)), 8, 0)
    cs['sobble'].add(60, 90, surprised, 2, 6)
    cs['piplup'].add(60, 90, surprised, 2, 6)
    cs['pikachu'].add(170, S.N, happy_bounce(2, 0.1), 6, 0)
    S.camera(24, 0)
    c = RING_C.to_3d() + Vector((0, 0, H(*RING_C) + 0.7))
    S.cam_keys([(1, c + Vector((-7, -8, 0.6)), c + Vector((8, -6, 0.5)), 24),
                (70, c + Vector((-6.5, -8.5, 0.8)), c + Vector((3, -1, 0.6)), 24),
                (130, c + Vector((-6.5, -9, 1.2)), c + Vector((3, 2, 1.8)), 24),
                (S.N, c + Vector((-5.5, -9, 1.0)), c + Vector((1.5, 1.2, 0.7)), 24)])
    grass_at(S, c)


# ---------------------------------------------------------------------------
# ACT II - THE GAME
# ---------------------------------------------------------------------------
ALL7 = ['pikachu', 'raboot', 'piplup', 'sobble', 'greninja', 'garchomp', 'dragonite']


def cheer_all(cs, f0, f1, skip=()):
    for i, (n, A) in enumerate(cs.items()):
        if n in skip:
            continue
        A.add(f0 + i * 2, f1, happy_bounce(2.0 + 0.2 * i, 0.1 if A.c['height'] < 1 else 0.04), 6, 6)
        A.add(f0 + i * 2, f1, smile_eyes, 4, 4)


@shot('s12_game_a', 4, 'noon')
def s12(S):
    """Raboot boots the ball high; Piplup heads it"""
    setup_star(S)
    cs = cast(S, ALL7)
    ball = S.obj('Ball')
    rb, pp = gpos('raboot'), gpos('piplup')
    cs['raboot'].add(4, 30, kick('right', 0.5, 1.0), 2, 4)
    kp = rb + Vector((-0.2, -0.2, 0.16))
    S.key_obj(ball, 1, kp)
    S.key_obj(ball, 16, kp)
    head = pp + Vector((0, 0, 0.45))
    ballistic(S, ball, kp, head, 17, 58, 3.0, (8, 0, 3))
    ballistic(S, ball, head, gpos('sobble', 0.3, 0.9) + Vector((0, 0, 0.16)), 58, S.N + 10, 1.4, (5, 1, 0))
    cs['piplup'].add(46, 70, hop(1, 0.8, 0.35), 2, 4)
    cs['piplup'].add(62, S.N, smile_eyes, 4, 4)
    for n, A in cs.items():
        A.add(1, S.N, look(lambda f: _ballpos(ball, f)), 4, 4, 0.9)
    S.camera(30, 3.5)
    c = (rb + pp) / 2 + Vector((0, 0, 0.6))
    S.cam_keys([(1, c + Vector((-5.0, -3.4, 0.0)), c + Vector((0.6, 0.6, 0.3)), 30),
                (S.N, c + Vector((-5.2, -2.8, 0.3)), c + Vector((-0.4, 0.2, 0.6)), 30)])
    grass_at(S, c)


def _ballpos(ball, f):
    """sample the ball's keyed location at frame f (fcurves)"""
    ad = ball.animation_data
    if not ad or not ad.action:
        return ball.location.copy()
    v = [0, 0, 0]
    for fc in ad.action.fcurves:
        if fc.data_path == 'location':
            v[fc.array_index] = fc.evaluate(f)
    return Vector(v)


@shot('s13_game_b', 4, 'noon')
def s13(S):
    """Sobble ducks the ball with a squeak; Pikachu spins and whacks it with its tail"""
    setup_star(S)
    cs = cast(S, ['pikachu', 'sobble', 'piplup', 'raboot'])
    ball = S.obj('Ball')
    sb, pk = gpos('sobble'), gpos('pikachu')
    start = gpos('piplup') + Vector((0, 0, 0.45))
    ballistic(S, ball, start, sb + Vector((0.05, 0.1, 0.3)), 1, 22, 0.8, (5, 1, 0))
    ballistic(S, ball, sb + Vector((0.05, 0.1, 0.3)), pk + Vector((0.15, -0.1, 0.22)), 22, 44, 0.6, (5, 1, 0))
    ballistic(S, ball, pk + Vector((0.15, -0.1, 0.22)), gpos('raboot', 0, 0) + Vector((0, 0, 0.5)), 44, S.N + 6, 2.2, (9, 0, 4))
    cs['sobble'].add(10, 36, crouch(1.0), 3, 6)
    cs['sobble'].add(10, 36, surprised, 3, 6)
    cs['sobble'].close_eyes(14, 30)
    cs['pikachu'].add(28, 56, spin(1.0, 0.3), 2, 2)
    cs['pikachu'].add(56, S.N, smile_eyes, 4, 0)
    cs['raboot'].add(70, S.N, happy_bounce(), 4, 0)
    for n in ('piplup', 'raboot'):
        cs[n].add(1, S.N, look(lambda f: _ballpos(ball, f)), 4, 4, 0.9)
    S.camera(40, 2.8)
    c = (sb + pk) / 2 + Vector((0, 0, 0.3))
    S.cam_keys([(1, c + Vector((0.8, -2.8, 0.1)), c + Vector((0.1, 0, 0)), 40),
                (S.N, c + Vector((-0.2, -2.6, 0.2)), c + Vector((-0.2, 0.1, 0.05)), 40)])
    grass_at(S, c)


@shot('s14_game_c', 5, 'noon')
def s14(S):
    """Greninja backflip-kicks the ball skyward; everyone cheers, Dragonite claps"""
    setup_star(S)
    cs = cast(S, ALL7)
    ball = S.obj('Ball')
    gr = gpos('greninja')
    Gr = cs['greninja']
    ballistic(S, ball, gpos('raboot') + Vector((0, 0, 0.5)), gr + Vector((0.1, -0.2, 1.0)), 1, 24, 1.2, (6, 0, 2))
    Gr.add(18, 44, lambda A, f, u, t: ({}, V(0, 0, 1.0 * math.sin(u * math.pi)), R(-360 * smoother(u))), 2, 2)
    Gr.add(18, 44, kick('right', 0.3, 1.3), 2, 2)
    Gr.no_walk.append((1, S.N))
    ballistic(S, ball, gr + Vector((0.1, -0.2, 1.0)), gr + Vector((-1.0, 6.0, 0.2)), 26, 90, 12.0, (15, 3, 0))
    cheer_all(cs, 40, S.N, skip=('dragonite',))
    cs['dragonite'].add(36, S.N, clap(2.8), 6, 0)
    cs['dragonite'].add(36, S.N, smile_eyes, 6, 0)
    for n, A in cs.items():
        A.add(1, 60, look(lambda f: _ballpos(ball, f)), 4, 6, 0.8)
    S.camera(22, 0)
    c = gr + Vector((0, 0, 1.0))
    S.cam_keys([(1, c + Vector((2.5, -5.0, -0.4)), c + Vector((0, 0, 0.2)), 24),
                (46, c + Vector((2.3, -5.0, -0.4)), c + Vector((0, 0.5, 1.8)), 24),
                (S.N, c + Vector((3.0, -7.5, 0.8)), RING_C.to_3d() + Vector((0, 0, H(*RING_C) + 0.9)), 22)])
    grass_at(S, c)


@shot('s15_garchomp_wants', 5, 'afternoon')
def s15(S):
    """Garchomp wants a turn: it lines up the ball and winds up a mighty kick"""
    setup_star(S)
    cs = cast(S, ALL7)
    Gc = cs['garchomp']
    ball = S.obj('Ball')
    g = gpos('garchomp')
    kick_spot = g + Vector((-0.4, 0.9, 0.16))
    ballistic(S, ball, g + Vector((-6, 4, 0.16)), kick_spot, 1, 30, 1.0, (6, 0, 0))
    S.key_obj(ball, S.N, kick_spot)
    Gc.key(1, (g.x, g.y), face(g, kick_spot))
    Gc.key(S.N, (g.x + 0.4, g.y - 0.3), face(g, TREE))
    Gc.add(10, 60, tail_wag(3.5, 25), 6, 6)
    Gc.add(20, 60, smile_eyes, 4, 4)
    Gc.add(64, S.N, crouch(0.5), 6, 0)
    Gc.add(64, S.N, lean(20), 6, 0)
    for n, A in cs.items():
        if n != 'garchomp':
            A.add(1, S.N, look(lambda f: Gc.head_world(f)), 4, 0)
    cs['greninja'].add(40, S.N, arms_cross, 6, 0)
    cs['sobble'].add(60, S.N, crouch(0.4), 6, 0)
    S.camera(35, 2.8)
    c = g + Vector((0, 0, 1.2))
    S.cam_keys([(1, c + Vector((-3.5, -3.5, -0.6)), c + Vector((0, 0.5, -0.1)), 32),
                (S.N, c + Vector((-2.2, -2.2, -0.9)), c + Vector((0, 0.3, 0)), 32)])
    grass_at(S, c)


@shot('s16_superkick', 2, 'afternoon')
def s16(S):
    """KICK! Garchomp sends the ball rocketing skyward"""
    setup_star(S)
    cs = cast(S, ['garchomp', 'pikachu', 'raboot', 'dragonite'])
    Gc = cs['garchomp']
    ball = S.obj('Ball')
    g = gpos('garchomp')
    Gc.key(1, (g.x + 0.4, g.y - 0.3), face(g, TREE))
    kick_spot = g + Vector((-0.4, 0.9, 0.16))
    Gc.add(1, 26, kick('right', 0.45, 1.6), 0, 6)
    S.key_obj(ball, 12, kick_spot)
    ballistic(S, ball, kick_spot, STAR_HOME + Vector((0.25, -0.25, 0.0)), 12, 62, 1.5, (25, 4, 0))
    S.post.append(lambda: fx.glow_burst(kick_spot, 12, (1.0, 0.95, 0.8), 0.5, 12, 6, 2e3))
    for n, A in cs.items():
        if n != 'garchomp':
            A.add(1, S.N, look(lambda f: _ballpos(ball, f)), 4, 0)
    S.camera(22, 0)
    S.cam_keys([(1, kick_spot + Vector((-2.6, -2.2, 0.1)), kick_spot + Vector((0.4, 0.6, 0.6)), 22),
                (12, kick_spot + Vector((-2.6, -2.2, 0.1)), kick_spot + Vector((0.4, 0.6, 0.9)), 22),
                (S.N, kick_spot + Vector((-2.8, -2.4, 0.0)), kick_spot + Vector((-1.0, 3.5, 5.0)), 22)])
    S.shake(0.03, 3.0)
    grass_at(S, g)


@shot('s17_starfall', 6, 'afternoon')
def s17(S):
    """the Star tumbles down through the branches; faces follow it down"""
    setup_star(S)
    cs = cast(S, ALL7, face_to=TREE)
    st = S.obj('Star')
    p0 = STAR_HOME + Vector((-1.2, 1.0, -3.0))
    p1 = TREE + Vector((-3.0, -3.5, 8.0))
    p2 = G(2.5, 27.5, 0.45)
    ballistic(S, st, p0, p1, 1, 40, 0.5, (5, 8, 2))
    ballistic(S, st, p1, p2, 40, 80, 1.2, (4, 6, 1))
    ballistic(S, st, p2, G(3.4, 25.5, 0.45), 80, 104, 0.7, (2, 3, 0))
    S.key_obj(st, S.N, G(3.9, 24.5, 0.45), (7, 9.2, 1))
    for n, A in cs.items():
        A.add(1, S.N, look(lambda f: _ballpos(st, f)), 4, 0)
    cs['pikachu'].add(20, 60, arms_up(40, 40), 6, 6)
    cs['sobble'].add(80, 100, surprised, 2, 6)
    cs['garchomp'].add(90, S.N, rub_head('right'), 8, 0)
    S.camera(28, 0)
    c = TREE + Vector((0, 0, 7))
    S.cam_keys([(1, TREE + Vector((9, -20, 3.0)), p0, 45),
                (70, TREE + Vector((8, -19, 2.0)), p1 + Vector((0, 0, -3)), 32),
                (S.N, TREE + Vector((7, -15, 0.2)), G(3.4, 25.5, 0.4), 30)])
    grass_at(S, G(3, 24))


ROLL = [(3.9, 24.5), (2.6, 19.0), (1.6, 12.0), (1.0, 5.0), (-6.0, 2.5), (-12.0, 0.0), (-18.0, -4.0), (-24.0, -8.0), (-28.6, -11.2), (-31.8, -13.6)]


@shot('s18_chase', 5, 'afternoon')
def s18(S):
    """the Star rolls away down the meadow path - everyone gives chase"""
    setup_star(S)
    st = S.obj('Star')
    roll(S, st, ROLL[:6], 1, S.N, 0.45)
    spos = star_pos_fn(st)
    names = ['pikachu', 'raboot', 'garchomp', 'sobble', 'piplup', 'greninja']
    lags = [14, 20, 34, 26, 30, 18]
    sides = [-0.9, 1.0, 0.2, -1.6, 1.8, -2.4]
    d0 = (spos(2) - spos(1))
    d0.z = 0
    v0 = d0.length
    d0.normalize()
    for i, n in enumerate(names):
        A = S.actor(n)
        for f in list(range(1, S.N + 1, 6)) + [S.N]:
            fl = f - lags[i]
            if fl >= 1:
                p = spos(fl)
                d = spos(fl + 1) - spos(fl)
                d.z = 0
                d = d.normalized() if d.length > 1e-4 else d0
            else:
                p = spos(1) - d0 * v0 * (1 - fl)
                d = d0
            p = p + left_of(d) * sides[i]
            A.key(f, (p.x, p.y))
    S.camera(28, 0)

    def cam(f):
        b = spos(f)
        d = spos(f + 2) - spos(max(1, f - 2))
        d.z = 0
        d = d.normalized() if d.length > 1e-4 else d0
        return b + d * 5.5 + left_of(d) * 2.4 + Vector((0, 0, 0.6)), b - d * 2.5 + Vector((0, 0, 0.3)), 28
    S.cam_fn(cam, step=2)
    grass_at(S, G(1, 8))


@shot('s19_plop', 4, 'afternoon')
def s19(S):
    """...across the beach and PLOP into the lake. Its light fades as it sinks"""
    setup_star(S)
    st = S.obj('Star')
    S.glow(1, star=0.35)
    roll(S, st, ROLL[6:9], 1, 30, 0.45)
    wz = T.LAKE_LEVEL
    ballistic(S, st, G(*ROLL[8], 0.45), Vector((ROLL[9][0], ROLL[9][1], wz + 0.1)), 30, 44, 0.5, (2, 6, 0))
    S.key_obj(st, 60, Vector((ROLL[9][0] - 0.2, ROLL[9][1] - 0.1, wz - 0.5)), (3, 8, 0))
    S.key_obj(st, S.N, Vector((ROLL[9][0] - 0.3, ROLL[9][1] - 0.2, wz - 1.4)), (3.2, 8.3, 0))
    S.glow(44, star=0.35)
    S.glow(80, star=0.0)
    S.post.append(lambda: fx.splash((ROLL[9][0], ROLL[9][1], wz), 44, 1.1, 50, 4, water_z=wz))
    S.camera(32, 2.0)
    spos = star_pos_fn(st)
    endp = Vector((ROLL[9][0], ROLL[9][1], wz + 0.2))

    def cam(f):
        b = spos(min(f, 44))
        u = smooth((f - 1) / 44)
        loc = Vector((-25.5, -12.5, wz + 0.9)).lerp(Vector((-27.5, -10.6, wz + 0.7)), u)
        return loc, b.lerp(endp, smooth((f - 30) / 20)) + Vector((0, 0, 0.1)), 32
    S.cam_fn(cam, step=2)
    grass_at(S, (-28, -11, 0))


LAKE_GROUP = {
    'pikachu': (-27.4, -11.0), 'raboot': (-26.8, -10.0), 'sobble': (-28.2, -11.8), 'piplup': (-28.7, -11.0),
    'greninja': (-27.9, -9.6), 'garchomp': (-25.6, -11.8), 'dragonite': (-25.2, -9.2)}
SPLASH_PT = Vector((ROLL[9][0], ROLL[9][1]))


def lake_cast(S, names):
    out = {}
    for n in names:
        A = S.actor(n)
        p = LAKE_GROUP[n]
        A.key(1, p, face(p, SPLASH_PT))
        out[n] = A
    return out


@shot('s20_shock', 6, 'afternoon')
def s20(S):
    """shocked faces at the water's edge; Garchomp hangs its head, sheepish"""
    setup_star(S)
    S.glow(1, star=0.0)
    cs = lake_cast(S, ALL7)
    for n, A in cs.items():
        A.add(1, 50, surprised, 0, 10)
        A.add(1, S.N, look(Vector((SPLASH_PT.x, SPLASH_PT.y, T.LAKE_LEVEL))), 0, 0)
    cs['garchomp'].add(60, S.N, sad, 10, 0)
    cs['garchomp'].add(70, S.N, rub_head('right'), 10, 0)
    for n in ('pikachu', 'raboot', 'dragonite'):
        cs[n].add(70, S.N, look(lambda f: cs['garchomp'].head_world(f)), 10, 0)
    S.camera(30, 2.8)
    lk = Vector((SPLASH_PT.x, SPLASH_PT.y, T.LAKE_LEVEL + 0.4))
    grp = Vector((-26.8, -10.6, H(-26.8, -10.6) + 0.6))
    S.cam_keys([(1, lk + Vector((-0.8, -2.2, 0.1)), grp, 30),
                (60, lk + Vector((-0.6, -1.8, 0.15)), grp + Vector((0.4, 0, 0.3)), 34),
                (S.N, grp + Vector((-1.2, -4.0, 0.3)), gpos_lake('garchomp', 0.9), 45)])
    grass_at(S, grp)


def gpos_lake(n, dz=0.0):
    p = LAKE_GROUP[n]
    return Vector((p[0], p[1], H(*p) + dz))


@shot('s21_dive', 7, 'afternoon')
def s21(S):
    """Sobble bursts into tears; Piplup and Greninja dive in after the Star"""
    setup_star(S)
    S.glow(1, star=0.0)
    cs = lake_cast(S, ALL7)
    Sb = cs['sobble']
    Sb.add(1, S.N, sad, 0, 0)
    Sb.add(1, S.N, talk(0.8, 5.5, 3), 0, 0)
    Sb.close_eyes(0, S.N + 1)
    Sb.tear_obj.hide_render = False
    el, er = eye_points(Sb)
    hb = Sb.c['head']
    S.post.append(lambda: fx.tears(lambda f: Sb.bone_matrix(f, hb) @ el, 1, S.N, lambda f: (Sb.bone_matrix(f, hb).to_3x3() @ Vector((1, 0, 0))).normalized(), 2, 41))
    S.post.append(lambda: fx.tears(lambda f: Sb.bone_matrix(f, hb) @ er, 2, S.N, lambda f: (Sb.bone_matrix(f, hb).to_3x3() @ Vector((-1, 0, 0))).normalized(), 2, 42))
    wz = T.LAKE_LEVEL
    for n, f0, d in (('greninja', 50, (-38.5, -15.4)), ('piplup', 70, (-36.8, -16.6))):
        A = cs[n]
        p0 = gpos_lake(n)
        p1 = Vector((d[0], d[1], wz - 1.9))
        A.key(f0 - 12, LAKE_GROUP[n], face(LAKE_GROUP[n], d))
        leap(A, (p0, p1), f0, f0 + 30, 1.6 if n == 'greninja' else 1.0, flip=0.0, tuck=0.2)
        A.add(f0, f0 + 30, lambda A_, f, u, t: ({}, None, R(80 * u, 0, 0)), 4, 0)
        A.key(S.N, (d[0] - 1, d[1], wz - 2.2))
        S.post.append(lambda d=d, f0=f0, n=n: fx.splash((d[0] + 0.6, d[1] + 0.2, wz), f0 + 24, 1.0 if n == 'greninja' else 0.6, 45, f0, water_z=wz))
    for n in ('pikachu', 'raboot', 'garchomp', 'dragonite'):
        cs[n].add(1, 50, look(lambda f: Sb.head_world(f)), 0, 6)
        cs[n].add(50, S.N, look(Vector((-37.0, -15.6, wz))), 6, 0)
    S.camera(40, 2.5)
    sb = gpos_lake('sobble', 0.22)
    cf = front_cam(LAKE_GROUP['sobble'], SPLASH_PT, 1.1, 0.25, 0.28)
    S.cam_keys([(1, cf, sb, 42),
                (40, cf + Vector((0.05, 0.05, 0.02)), sb, 42),
                (52, Vector((-30.5, -9.5, wz + 1.4)), Vector((-36.0, -15.0, wz + 0.4)), 30),
                (S.N, Vector((-30.8, -9.9, wz + 1.3)), Vector((-37.0, -15.6, wz + 0.1)), 30)], 'LINEAR')
    grass_at(S, sb)


@shot('s22_rescue', 8, 'afternoon')
def s22(S):
    """Greninja surfaces holding the Star high - but its light has gone out"""
    setup_star(S)
    S.glow(1, star=0.0)
    wz = T.LAKE_LEVEL
    cs = lake_cast(S, ['pikachu', 'raboot', 'sobble', 'garchomp', 'dragonite'])
    Gr = S.actor('greninja')
    Pp = S.actor('piplup')
    g0 = Vector((-37.4, -15.2, wz - 1.8))
    g1 = Vector((-36.2, -14.8, wz - 1.0))
    gs = Vector((-29.4, -12.4))
    Gr.fly = True
    Gr.key(1, g0, face(g0, gs))
    Gr.key(30, g1, face(g0, gs))
    Gr.key(120, (-31.2, -13.3, wz - 0.35), face(g0, gs))
    Gr.key(160, (gs.x, gs.y, H(gs.x, gs.y)), face(g0, gs))
    Gr.key(S.N, (gs.x, gs.y, H(gs.x, gs.y)), face(gs, (-27.4, -11.0)))
    Gr.add(10, S.N, arms_up(70, 10), 10, 0)
    Pp.fly = True
    Pp.key(1, (-36.0, -16.4, wz - 1.2), face((-36.0, -16.4), gs))
    Pp.key(40, (-35.4, -16.0, wz - 0.3))
    Pp.key(150, (-30.0, -13.4, H(-30.0, -13.4)), face((-36.0, -16.4), gs))
    Pp.key(S.N, (-30.0, -13.4, H(-30.0, -13.4)), face((-30.0, -13.4), (-27.4, -11.0)))
    st = S.obj('Star')
    S.post.append(lambda: _hold_above(S, st, Gr, 1, S.N))
    S.post.append(lambda: fx.splash((g1.x, g1.y, wz), 26, 0.8, 35, 51, water_z=wz))
    S.post.append(lambda: fx.splash((-35.4, -16.0, wz), 36, 0.5, 25, 52, water_z=wz))
    for n, A in cs.items():
        A.add(1, S.N, look(lambda f: _ballpos(st, f)), 0, 0)
        A.add(40, 100, happy_bounce(2.2, 0.06), 6, 10)
        A.add(120, S.N, sad, 20, 0)
    S.camera(34, 2.8)

    def cam(f):
        g = Gr.pos(f) + Vector((0, 0, 1.3))
        g.z = max(g.z, wz + 0.9)
        d = fwd_of(g, (-27.4, -11.0))
        loc = g + d * 4.8 + left_of(d) * 1.8
        loc.z = max(wz + 0.9, H(loc.x, loc.y) + 0.8)
        return loc, g, 36
    S.cam_fn(cam, step=3)
    grass_at(S, (-28, -12, 0))


def _hold_above(S, st, A, f0, f1):
    """key the Star centred above the actor's head, held in both hands"""
    for f in range(int(f0), int(f1) + 1):
        hw = A.head_world(f)
        l = A.bone_pos(f, A.c['arm'][-1])
        r = A.bone_pos(f, A.c['arm'][-1].replace('left_', 'right_'))
        c = (l + r) / 2
        p = c + Vector((0, 0, 0.3)) if c.z > hw.z else hw + Vector((0, 0, 0.55))
        S.key_obj(st, f, p, (0, 0, A.heading(f)))


@shot('s23_sorry', 6, 'afternoon')
def s23(S):
    """Garchomp apologises; Dragonite gives it a comforting pat"""
    setup_star(S)
    S.glow(1, star=0.0)
    cs = lake_cast(S, ['garchomp', 'dragonite', 'pikachu', 'raboot'])
    Gc, Dn = cs['garchomp'], cs['dragonite']
    g = LAKE_GROUP['garchomp']
    d = (g[0] + 1.3, g[1] + 0.9)
    Dn.key(1, LAKE_GROUP['dragonite'])
    Dn.key(40, d, face(d, g))
    Dn.key(S.N, d, face(d, g))
    Gc.key(1, g, face(g, SPLASH_PT))
    Gc.key(50, g, face(g, d))
    Gc.key(S.N, g, face(g, d))
    Gc.add(1, S.N, sad, 0, 0)
    Gc.add(1, S.N, look(lambda f: Dn.head_world(f), 0.5), 20, 0)
    Dn.add(40, S.N, lambda A, f, u, t: arm_pose(A, 'right', 10 + 8 * math.sin(t * 9), 70, 60), 10, 0)
    Dn.add(40, S.N, smile_eyes, 10, 0)
    Dn.add(40, S.N, look(lambda f: Gc.head_world(f)), 10, 0)
    Gc.add(100, S.N, nod(1, 10, 0.7), 2, 2)
    for n in ('pikachu', 'raboot'):
        cs[n].add(1, S.N, look(lambda f: Gc.head_world(f)), 0, 0)
    cs['pikachu'].add(90, S.N, smile_eyes, 8, 0)
    S.camera(38, 2.8)
    mid_ = Vector(((g[0] + d[0]) / 2, (g[1] + d[1]) / 2))
    ax = fwd_of(g, d)
    perp = left_of(ax)
    c = Vector((mid_.x, mid_.y, H(*g) + 1.5))
    S.cam_keys([(1, c - perp * 5.2 + Vector((0, 0, -0.5)), c, 38),
                (S.N, c - perp * 4.4 + Vector((0, 0, -0.5)), c + Vector((0, 0, 0.1)), 40)])
    grass_at(S, c)


# ---------------------------------------------------------------------------
# ACT III - JOURNEY
# ---------------------------------------------------------------------------
CAMP = {
    'pikachu': (4.2, 21.0), 'raboot': (5.8, 20.4), 'sobble': (3.2, 21.9), 'piplup': (3.4, 20.2),
    'greninja': (6.9, 21.9), 'garchomp': (7.6, 19.4), 'dragonite': (2.2, 18.8)}
STAR_REST = Vector((5.0, 22.9, H(5.0, 22.9) + 0.45))     # dark Star leaning on the berry plate


def camp_cast(S, names, look_star=True):
    out = {}
    for n in names:
        A = S.actor(n)
        p = CAMP[n]
        A.key(1, p, face(p, STAR_REST))
        out[n] = A
    return out


def star_rest(S, f=1):
    S.key_obj(S.obj('Star'), f, STAR_REST, (math.radians(-12), 0, math.radians(15)))


PEAK = Vector((T.PEAK_C[0], T.PEAK_C[1], H(*T.PEAK_C)))
RIDE_OFF = (0.0, 0.34, 1.48)     # Pikachu's seat on Dragonite's back (actor space)


@shot('s24_sparks', 9, 'golden')
def s24(S):
    """golden hour: Pikachu tries to recharge the Star - it flickers... and dies"""
    setup_star(S)
    star_rest(S)
    S.glow(1, star=0.0)
    cs = camp_cast(S, ['pikachu', 'raboot', 'sobble', 'piplup', 'greninja'])
    P = cs['pikachu']
    p = Vector(CAMP['pikachu'])
    pk = Vector((STAR_REST.x - 0.2, STAR_REST.y - 0.75))
    P.key(30, p, face(p, STAR_REST))
    P.key(60, pk, face(pk, STAR_REST))
    P.key(S.N, pk, face(pk, STAR_REST))
    P.add(66, 150, crouch(0.5), 8, 8)
    P.add(66, 150, arms_forward(60, 0, 20), 8, 8)
    P.close_eyes(80, 140)
    S.post.append(lambda: fx.sparks(lambda f: P.head_world(f) + Vector((0, 0, -0.08)), 80, 145, 0.28, 8, 17))
    S.post.append(lambda: fx.sparks(lambda f: STAR_REST, 100, 142, 0.5, 6, 18))
    for f, g in ((100, 0.0), (108, 0.4), (112, 0.1), (118, 0.55), (124, 0.2), (130, 0.7), (138, 0.25), (146, 0.05), (160, 0.0)):
        S.glow(f, star=g)
    P.add(166, S.N, sad, 10, 0)
    for n, A in cs.items():
        if n != 'pikachu':
            A.add(1, 160, look(STAR_REST), 0, 8)
            A.add(100, 150, happy_bounce(2.0, 0.05), 6, 6)
            A.add(160, S.N, sad, 12, 0)
            A.add(170, S.N, look(lambda f: P.head_world(f)), 10, 0)
    S.camera(40, 2.2)
    ph = Vector((pk.x, pk.y, H(*pk) + 0.28))
    S.cam_keys([(1, STAR_REST + Vector((1.9, 1.1, 0.25)), (ph + STAR_REST) / 2, 34),
                (90, STAR_REST + Vector((0.9, 0.55, 0.0)), ph, 42),
                (S.N, STAR_REST + Vector((1.0, 0.7, 0.05)), ph + Vector((0, 0, -0.03)), 45)])
    grass_at(S, STAR_REST)


@shot('s25_idea', 6, 'golden')
def s25(S):
    """Dragonite has an idea: it points to the mountain peak where Charizard lives"""
    setup_star(S)
    star_rest(S)
    S.glow(1, star=0.0)
    cs = camp_cast(S, ['pikachu', 'raboot', 'sobble', 'piplup', 'greninja', 'garchomp', 'dragonite'])
    Dn = cs['dragonite']
    pk = (STAR_REST.x - 0.2, STAR_REST.y - 0.75)
    cs['pikachu'].key(1, pk, face(pk, CAMP['dragonite']))
    Dn.key(1, CAMP['dragonite'], face(CAMP['dragonite'], STAR_REST))
    Dn.key(40, CAMP['dragonite'], face(CAMP['dragonite'], PEAK))
    Dn.key(S.N, CAMP['dragonite'], face(CAMP['dragonite'], PEAK))
    Dn.add(30, S.N, point('right', PEAK), 10, 0)
    Dn.add(10, 60, talk(1.0, 3.5, 5), 4, 4)
    Dn.add(10, S.N, smile_eyes, 6, 0)
    for n, A in cs.items():
        if n != 'dragonite':
            A.add(1, 60, look(lambda f: Dn.head_world(f)), 0, 10)
            A.add(60, S.N, look(PEAK), 10, 0)
    S.camera(34, 2.8)
    d = gpos_camp('dragonite', 1.7)
    cf = front_cam(CAMP['dragonite'], PEAK, 3.6, 1.4, 1.1)
    S.cam_keys([(1, cf, d, 34), (S.N, cf + Vector((0, 0, 0.3)), d + Vector((0, 0, 0.4)), 30)])
    grass_at(S, d)


def gpos_camp(n, dz=0.0):
    p = CAMP[n]
    return Vector((p[0], p[1], H(*p) + dz))


@shot('s26_peak', 4, 'golden')
def s26(S):
    """high on the distant peak, Charizard sleeps on its ledge; a thread of smoke rises"""
    setup_star(S)
    Cz = S.actor('charizard', blink=False)
    cz = LEDGE + Vector((1.0, 2.0, 0))
    Cz.key(1, (cz.x, cz.y), 140)
    Cz.add(1, S.N, curl, 0, 0)
    Cz.add(1, S.N, sleep, 0, 0)
    Cz.close_eyes(0, S.N + 1)
    S.post.append(lambda: fx.smoke(lambda f: cz + Vector((-0.6, -0.9, 0.5)), -60, S.N, 5, 61, 0.2, 0.7, (0.55, 0.52, 0.5), 0.45, 90, (0.3, 0.1, 0)))
    S.camera(60, 0)
    S.cam_keys([(1, cz + Vector((-13, -17, 4.5)), cz + Vector((0, 0, 0.8)), 45),
                (S.N, cz + Vector((-11.5, -15, 4.0)), cz + Vector((0, 0, 0.7)), 52)])
    grass_at(S, cz)


def dn_carry_pose(A, f, u, t):
    """Dragonite hugging the Star to its chest"""
    p = {}
    for sd in ('left', 'right'):
        p.update(arm_pose(A, sd, -5, 80, 70))
    return p


def star_on_chest(S, Dn, f0, f1):
    def do():
        st = S.obj('Star')
        for f in range(int(f0), int(f1) + 1):
            M = Dn.root_full(f)
            c = M @ Vector((0, -0.55, 1.25))
            S.key_obj(st, f, c, (0, 0, Dn.heading(f)))
    S.post.append(do)


@shot('s27_takeoff', 6, 'sunset')
def s27(S):
    """Dragonite takes off, hugging the Star, with Pikachu riding on its back"""
    setup_star(S)
    S.glow(1, star=0.0)
    cs = camp_cast(S, ['raboot', 'sobble', 'piplup', 'greninja', 'garchomp'])
    Dn = S.actor('dragonite')
    P = S.actor('pikachu')
    d = Vector(CAMP['dragonite'])
    dz = H(*d)
    Dn.key(1, (d.x, d.y, dz), face(d, PEAK))
    Dn.key(40, (d.x, d.y, dz), face(d, PEAK))
    to = (PEAK.xy - d).normalized()
    fly_keys(Dn, [(70, (d.x + to.x * 1.5, d.y + to.y * 1.5, dz + 2.5)), (110, (d.x + to.x * 8, d.y + to.y * 8, dz + 8)),
                  (S.N, (d.x + to.x * 20, d.y + to.y * 20, dz + 16))])
    Dn.add(1, 40, crouch(0.5), 6, 4)
    Dn.add(30, S.N, flap(1.5, 1.0, 0.0, 22), 10, 0)
    Dn.add(1, S.N, dn_carry_pose, 0, 0)
    star_on_chest(S, Dn, 1, S.N)
    S.ride(P, Dn, None, RIDE_OFF, 1, S.N)
    P.add(1, S.N, ride, 0, 0)
    P.add(40, S.N, wave('left', 70, 2.5, 30), 8, 0)
    P.add(40, S.N, smile_eyes, 6, 0)
    for n, A in cs.items():
        A.add(1, S.N, look(lambda f: Dn.head_world(f)), 0, 0)
        A.add(50, S.N, wave('left', 60, 2.2 + 0.2 * (len(n) % 3), 25), 8, 0)
    S.camera(26, 0)
    side = left_of(Vector((to.x, to.y, 0)))
    c0 = Vector((d.x, d.y, dz + 1.4))
    cam0 = c0 + side * -6.5 + Vector((to.x, to.y, 0)) * 2.5 + Vector((0, 0, -0.6))
    S.cam_keys([(1, cam0, c0, 30),
                (60, cam0, c0 + Vector((0, 0, 2.0)), 28),
                (S.N, cam0 + Vector((0, 0, 0.4)), Vector((d.x + to.x * 18, d.y + to.y * 18, dz + 15)), 30)])
    grass_at(S, c0)


@shot('s28_flight', 9, 'sunset', samples=16)
def s28(S):
    """soaring across the valley at sunset"""
    setup_star(S)
    S.glow(1, star=0.0)
    Dn = S.actor('dragonite')
    P = S.actor('pikachu')
    a = Vector((35, 60, 70))
    b = LEDGE + Vector((-26, -32, 22))
    fly_keys(Dn, [(1, a), (S.N // 2, a.lerp(b, 0.5) + Vector((8, -8, 8))), (S.N, b)])
    Dn.add(1, S.N, flap(1.2, 0.9, 0.35, 12), 0, 0)
    Dn.add(1, S.N, dn_carry_pose, 0, 0)
    star_on_chest(S, Dn, 1, S.N)
    S.ride(P, Dn, None, RIDE_OFF, 1, S.N)
    P.add(1, S.N, ride, 0, 0)
    P.add(1, S.N, arms_up(20, 40), 0, 0)
    P.add(1, S.N, smile_eyes, 0, 0)
    P.add(80, S.N, look(PEAK), 10, 0)
    S.camera(40, 0)

    def cam(f):
        p = Dn.pos(f)
        v = Dn.vel(f).normalized()
        side = Vector((-v.y, v.x, 0)).normalized()
        u = (f - 1) / (S.N - 1)
        return p + side * (6.0 - 2 * u) + v * (2.5 - 4 * u) + Vector((0, 0, 1.0)), p + Vector((0, 0, 1.3)), 38
    S.cam_fn(cam, step=2)
    S.grass_at = Vector((500, 500, 0))


@shot('s29_ledge', 8, 'sunset')
def s29(S):
    """high on the peak, Charizard is fast asleep, snoring smoke. Dragonite lands softly"""
    setup_star(S)
    S.glow(1, star=0.0)
    Cz = S.actor('charizard', blink=False)
    Dn = S.actor('dragonite')
    P = S.actor('pikachu')
    cz = LEDGE + Vector((1.0, 2.0, 0))
    Cz.key(1, (cz.x, cz.y), 140)
    Cz.add(1, S.N, curl, 0, 0)
    Cz.add(1, S.N, sleep, 0, 0)
    Cz.close_eyes(0, S.N + 1)
    hb = 'center_nose' if 'center_nose' in Cz.bones else Cz.c['head']
    S.post.append(lambda: fx.smoke(lambda f: Cz.bone_pos(f, hb), 1, S.N, 22, 71, 0.06, 0.25, (0.55, 0.55, 0.57), 0.5, 50, (0.05, 0.05, 0)))
    land = LEDGE + Vector((-3.5, -3.0, 0))
    ap = land + Vector((-18, -22, 14))
    fly_keys(Dn, [(1, ap), (60, land + Vector((-4, -5, 4))), (110, land + Vector((0, 0, 0.8))), (130, land)])
    Dn.key(S.N, land, face(land, cz))
    Dn.face_frames = [(125, S.N)]
    Dn.add(1, 125, flap(1.4, 1.0, 0.2, 15), 0, 10)
    Dn.add(1, S.N, dn_carry_pose, 0, 0)
    Dn.add(125, 145, crouch(0.6), 4, 8)
    star_on_chest(S, Dn, 1, S.N)
    S.ride(P, Dn, None, RIDE_OFF, 1, S.N)
    P.add(1, S.N, ride, 0, 0)
    P.add(130, S.N, look(lambda f: Cz.head_world(f)), 10, 0)
    S.camera(30, 3.0)
    c = cz + Vector((0, 0, 0.6))
    S.cam_keys([(1, c + Vector((3.5, -4.0, 0.8)), c, 34),
                (90, c + Vector((3.2, -4.5, 1.0)), (c + land) / 2 + Vector((0, 0, 0.8)), 30),
                (S.N, c + Vector((3.6, -5.5, 1.2)), (c + land) / 2 + Vector((0, 0, 0.6)), 28)])
    grass_at(S, cz)


@shot('s30_poke', 7, 'sunset')
def s30(S):
    """Pikachu tiptoes over and pokes Charizard's nose. One eye opens... a grumpy snort"""
    setup_star(S)
    S.glow(1, star=0.0)
    Cz = S.actor('charizard', blink=False)
    Dn = S.actor('dragonite')
    P = S.actor('pikachu')
    cz = LEDGE + Vector((1.0, 2.0, 0))
    land = LEDGE + Vector((-3.5, -3.0, 0))
    Cz.key(1, (cz.x, cz.y), 140)
    Cz.add(1, 80, curl, 0, 16)
    Cz.add(1, 80, sleep, 0, 10)
    Cz.close_eyes(0, 70)
    Cz.add(80, S.N, crouch(0.5), 16, 0)
    Cz.add(92, 110, lambda A, f, u, t: put({}, A, A.c['jaw'], R(12 * math.sin(u * math.pi))), 2, 2)
    Dn.key(1, land, face(land, cz))
    Dn.add(1, S.N, dn_carry_pose, 0, 0)
    star_on_chest(S, Dn, 1, S.N)
    hd_p = cz + Vector((-1.25, -1.0, 0))
    P.key(1, (land.x + 0.8, land.y + 0.6), face(land, cz))
    P.key(60, (hd_p.x - 0.35, hd_p.y - 0.35), face(hd_p, cz))
    P.key(S.N, (hd_p.x - 0.35, hd_p.y - 0.35), face(hd_p, cz))
    P.add(1, 60, crouch(0.35), 6, 6)
    P.add(62, 84, lambda A, f, u, t: arm_pose(A, 'left', 0, 80 + 10 * math.sin(u * math.pi), 10), 4, 6)
    P.add(92, 120, surprised, 2, 8)
    P.add(1, S.N, look(lambda f: Cz.head_world(f)), 0, 0)
    Cz.add(90, S.N, look(lambda f: P.head_world(f), 0.7), 12, 0)
    hb = 'center_nose' if 'center_nose' in Cz.bones else Cz.c['head']
    S.post.append(lambda: fx.smoke(lambda f: Cz.bone_pos(f, hb), 94, 104, 2, 72, 0.08, 0.3, (0.5, 0.5, 0.5), 0.6, 30, (0.2, -0.1, 0)))
    S.camera(38, 2.4)
    c = (cz + hd_p) / 2 + Vector((0, 0, 0.5))
    S.cam_keys([(1, c + Vector((0.3, -3.8, 0.3)), c + Vector((-0.6, -0.3, 0)), 36),
                (80, c + Vector((0.0, -2.6, 0.1)), c + Vector((-0.2, 0, 0)), 40),
                (S.N, c + Vector((0.2, -2.2, 0.1)), c + Vector((0.1, 0.1, 0.1)), 45)])
    grass_at(S, cz)


@shot('s31_promise', 7, 'sunset')
def s31(S):
    """Pikachu shows the dark Star; Charizard's gaze softens - it nods and spreads its wings"""
    setup_star(S)
    S.glow(1, star=0.0)
    Cz = S.actor('charizard')
    Dn = S.actor('dragonite')
    P = S.actor('pikachu')
    cz = LEDGE + Vector((1.0, 2.0, 0))
    land = LEDGE + Vector((-3.5, -3.0, 0))
    hd_p = cz + Vector((-1.25, -1.0, 0))
    Cz.key(1, (cz.x, cz.y), 140)
    Cz.key(60, (cz.x, cz.y), face(cz, hd_p))
    Cz.key(S.N, (cz.x, cz.y), face(cz, hd_p))
    Cz.add(1, 30, crouch(0.5), 0, 20)
    Cz.add(1, S.N, look(lambda f: P.head_world(f), 0.8), 0, 0)
    Cz.add(90, S.N, smile_eyes, 10, 0)
    Cz.add(100, 130, nod(1, 16, 0.9), 2, 2)
    Cz.add(120, S.N, wings_spread(-35), 16, 0)
    Dn.key(1, land, face(land, cz))
    Dn.key(S.N, (hd_p.x - 1.8, hd_p.y + 0.6), face((hd_p.x - 1.8, hd_p.y + 0.6), cz))
    Dn.add(1, S.N, dn_carry_pose, 0, 20)
    P.key(1, (hd_p.x - 0.35, hd_p.y - 0.35), face(hd_p, cz))
    P.add(10, 110, arms_up(45, 50), 10, 10)
    P.add(20, 90, sad, 10, 10)
    P.add(110, S.N, happy_bounce(2.2, 0.12), 8, 0)
    P.add(110, S.N, smile_eyes, 6, 0)
    P.add(1, S.N, look(lambda f: Cz.head_world(f)), 0, 0)
    # the star is set down in front of Pikachu for this beat
    st = S.obj('Star')
    S.key_obj(st, 1, Vector((hd_p.x + 0.35, hd_p.y - 0.15, hd_p.z + 0.45)), (0, 0, math.radians(face(hd_p, cz))))
    S.camera(34, 2.4)
    c = cz + Vector((0, 0, 1.1))
    S.cam_keys([(1, Vector((hd_p.x - 0.9, hd_p.y - 1.3, hd_p.z + 0.35)), c, 34),
                (95, Vector((hd_p.x - 0.8, hd_p.y - 1.2, hd_p.z + 0.3)), c + Vector((0, 0, 0.2)), 36),
                (S.N, Vector((hd_p.x - 2.6, hd_p.y - 3.2, hd_p.z + 0.8)), c + Vector((0, 0, 0.3)), 28)])
    grass_at(S, cz)


@shot('s32_dusk', 8, 'dusk', samples=16)
def s32(S):
    """flying home at dusk: Charizard, and Dragonite with Pikachu and the Star"""
    setup_star(S)
    S.glow(1, star=0.0)
    Dn = S.actor('dragonite')
    Cz = S.actor('charizard')
    P = S.actor('pikachu')
    a = Vector((95, 120, 120))
    b = Vector((25, 50, 35))
    fly_keys(Dn, [(1, a), (S.N, b)])
    fly_keys(Cz, [(1, a + Vector((4, -3, 3))), (S.N, b + Vector((4.5, -3, 3.2)))])
    Dn.add(1, S.N, flap(1.2, 0.9, 0.3, 12), 0, 0)
    Dn.add(1, S.N, dn_carry_pose, 0, 0)
    Cz.add(1, S.N, flap(1.0, 1.0, 0.4, 14), 0, 0)
    star_on_chest(S, Dn, 1, S.N)
    S.ride(P, Dn, None, RIDE_OFF, 1, S.N)
    P.add(1, S.N, ride, 0, 0)
    P.add(1, S.N, look(lambda f: Cz.head_world(f)), 0, 0)
    P.add(1, S.N, smile_eyes, 0, 0)
    S.camera(32, 0)

    def cam(f):
        p = (Dn.pos(f) + Cz.pos(f)) / 2
        v = (b - a).normalized()
        side = Vector((-v.y, v.x, 0)).normalized()
        return p - side * 9 + v * 5 + Vector((0, 0, -1.0)), p + Vector((0, 0, 1.0)), 32
    S.cam_fn(cam, step=2)
    S.grass_at = Vector((500, 500, 0))


# ---------------------------------------------------------------------------
# ACT IV - FESTIVAL NIGHT
# ---------------------------------------------------------------------------
NIGHT = {
    'pikachu': (4.2, 21.0), 'raboot': (6.0, 20.2), 'sobble': (3.0, 21.6), 'piplup': (3.3, 20.0),
    'greninja': (7.2, 21.8), 'garchomp': (7.9, 19.2), 'dragonite': (1.8, 23.2), 'charizard': (2.2, 25.0)}
IGNITE = Vector((4.6, 23.4, H(4.6, 23.4) + 0.45))


def night_cast(S, names):
    out = {}
    for n in names:
        A = S.actor(n)
        p = NIGHT[n]
        A.key(1, p, face(p, IGNITE))
        out[n] = A
    return out


def gpos_night(n, dz=0.0):
    p = NIGHT[n]
    return Vector((p[0], p[1], H(*p) + dz))


def fireflies_bg(S, n=90):
    S.post.append(lambda: fx.fireflies((4, 22, 0), 16, n, -20, S.N, 0.3, 2.5, 55, ground=H))


@shot('s33_return', 10, 'night')
def s33(S):
    """night falls; the friends wait by the tree among fireflies - then wingbeats: they're back!"""
    setup_star(S)
    S.glow(1, star=0.0, lantern=0.0)
    cs = night_cast(S, ['raboot', 'sobble', 'piplup', 'greninja', 'garchomp'])
    Dn = S.actor('dragonite')
    Cz = S.actor('charizard')
    P = S.actor('pikachu')
    dl = gpos_night('dragonite')
    cl = gpos_night('charizard')
    fly_keys(Dn, [(1, dl + Vector((-30, -40, 25))), (140, dl + Vector((-3, -4, 3))), (190, dl + Vector((0, 0, 0.4))), (205, dl)])
    fly_keys(Cz, [(1, cl + Vector((-26, -44, 28))), (150, cl + Vector((-3, -3, 3.5))), (200, cl + Vector((0, 0, 0.4))), (215, cl)])
    Dn.key(S.N, dl, face(dl, IGNITE))
    Cz.key(S.N, cl, face(cl, IGNITE))
    Dn.face_frames = [(200, S.N)]
    Cz.face_frames = [(210, S.N)]
    Dn.add(1, 200, flap(1.4, 1.0, 0.2, 14), 0, 10)
    Cz.add(1, 210, flap(1.2, 1.0, 0.2, 14), 0, 10)
    Dn.add(1, S.N, dn_carry_pose, 0, 0)
    star_on_chest(S, Dn, 1, S.N)
    S.ride(P, Dn, None, RIDE_OFF, 1, 200)
    P.add(1, S.N, ride, 0, 0)
    for n, A in cs.items():
        A.add(1, 100, sad, 0, 10)
        A.add(100, S.N, look(lambda f: Dn.head_world(f)), 10, 0)
        A.add(170, S.N, happy_bounce(2.2, 0.08 if A.c['height'] < 1 else 0.03), 8, 0)
        A.add(170, S.N, smile_eyes, 6, 0)
    fireflies_bg(S)
    S.camera(30, 2.8)
    grp = Vector((5.2, 20.6, H(5.2, 20.6) + 0.45))
    S.cam_keys([(1, grp + Vector((-0.4, -4.2, 0.1)), grp + Vector((0, 0, 0.1)), 32),
                (120, grp + Vector((-0.3, -4.4, 0.2)), grp + Vector((-1.5, 1.5, 1.6)), 28),
                (S.N, grp + Vector((-0.2, -5.2, 0.5)), grp + Vector((-2.4, 2.8, 1.2)), 26)])
    grass_at(S, grp)


@shot('s34_ignite', 9, 'night')
def s34(S):
    """the Star is set down; Charizard breathes a gentle flame... and the Star blazes to life!"""
    setup_star(S)
    S.glow(1, star=0.0, lantern=0.0)
    cs = night_cast(S, ['pikachu', 'raboot', 'sobble', 'piplup', 'greninja', 'garchomp', 'dragonite', 'charizard'])
    Cz = cs['charizard']
    st = S.obj('Star')
    S.key_obj(st, 1, IGNITE, (0, 0, math.radians(face(IGNITE, NIGHT['charizard']))))
    Cz.add(30, 110, breathe_fire, 10, 10)
    nose = 'center_nose' if 'center_nose' in Cz.bones else Cz.c['head']

    def fire():
        src = lambda f: Cz.bone_pos(f, nose)
        dirf = lambda f: (IGNITE + Vector((0, 0, 0.1)) - src(f)).normalized()
        fx.fire_stream(src, dirf, 44, 100, 4, 3.0, 14, 0.12, 0.05, 0.6, 81, True, True)
        fx.glow_burst(IGNITE, 104, (1.0, 0.85, 0.45), 2.5, 60, 82, 1.2e4)
        fx.twinkles(lambda f: IGNITE, 104, S.N, 0.9, 16, 83)
    S.post.append(fire)
    for f, g in ((1, 0.0), (80, 0.0), (96, 0.3), (104, 1.3), (130, 0.9)):
        S.glow(f, star=g)
    for n, A in cs.items():
        if n != 'charizard':
            A.add(1, S.N, look(IGNITE), 0, 0)
            A.add(104, 130, surprised, 2, 8)
            A.add(130, S.N, smile_eyes, 8, 0)
    cs['pikachu'].add(140, S.N, happy_bounce(2.4, 0.14), 8, 0)
    cs['sobble'].add(140, S.N, happy_bounce(2.0, 0.1), 8, 0)
    fireflies_bg(S)
    S.camera(30, 2.0)
    c = IGNITE
    S.cam_keys([(1, c + Vector((2.2, -2.6, 0.5)), (c + gpos_night('charizard', 1.4)) / 2, 30),
                (100, c + Vector((1.8, -2.0, 0.35)), c + Vector((-0.4, 0.4, 0.3)), 34),
                (S.N, c + Vector((1.2, -1.5, 0.2)), c + Vector((0, 0, 0.05)), 38)])
    grass_at(S, c)


@shot('s35_faces', 5, 'night')
def s35(S):
    """warm starlight on amazed, happy faces"""
    setup_star(S)
    S.glow(1, star=0.9, lantern=0.0)
    cs = night_cast(S, ['pikachu', 'sobble', 'piplup', 'raboot'])
    st = S.obj('Star')
    S.key_obj(st, 1, IGNITE, (0, 0, math.radians(face(IGNITE, NIGHT['pikachu']))))
    for n, A in cs.items():
        A.add(1, S.N, look(IGNITE), 0, 0)
        A.add(1, S.N, smile_eyes, 0, 0)
    cs['sobble'].tear_obj.hide_render = False
    cs['sobble'].add(20, S.N, happy_bounce(1.6, 0.06), 8, 0)
    S.post.append(lambda: fx.twinkles(lambda f: IGNITE, 1, S.N, 0.9, 16, 84))
    S.camera(50, 1.8)
    a = gpos_night('sobble', 0.3)
    b = gpos_night('raboot', 0.5)
    S.cam_keys([(1, IGNITE + Vector((-0.4, -0.3, 0.1)), a, 45),
                (S.N, IGNITE + Vector((0.3, -0.5, 0.15)), b, 45)])
    grass_at(S, IGNITE)


@shot('s36_lanterns', 9, 'night')
def s36(S):
    """Dragonite carries the Star back to the treetop - every lantern lights up, and the bonfire roars to life"""
    setup_star(S)
    S.glow(1, star=0.9, lantern=0.0)
    cs = night_cast(S, ['pikachu', 'raboot', 'sobble', 'piplup', 'greninja', 'garchomp', 'charizard'])
    Dn = S.actor('dragonite')
    fly_keys(Dn, [(1, IGNITE + Vector((-0.6, 0.6, 0))), (30, IGNITE + Vector((-0.6, 0.8, 1.5))),
                  (110, STAR_HOME + Vector((0, -1.0, -0.4))), (150, STAR_HOME + Vector((0, -1.0, -0.6))), (S.N, STAR_HOME + Vector((3, -3, 0.5)))])
    Dn.add(1, S.N, flap(1.5, 1.0, 0.0, 10), 0, 0)
    Dn.add(1, 130, dn_carry_pose, 0, 10)
    st = S.obj('Star')

    def carry():
        for f in range(1, 131):
            M = Dn.root_full(f)
            c = M @ Vector((0, -0.55, 1.25))
            if f > 110:
                c = c.lerp(STAR_HOME, (f - 110) / 20)
            S.key_obj(st, f, c, (0, 0, 0))
        S.key_obj(st, 131, STAR_HOME, (0, 0, 0))
        fx.glow_burst(STAR_HOME, 132, (1.0, 0.85, 0.45), 3.0, 80, 91, 3e4)
    S.post.append(carry)
    bonfire(S, IGNITE + Vector((0, 0, -0.45)), 140)
    for f, g in ((1, 0.0), (132, 0.0), (160, 1.0)):
        S.glow(f, lantern=g)
    for f, g in ((1, 0.9), (130, 0.9), (134, 1.4), (160, 1.0)):
        S.glow(f, star=g)
    for n, A in cs.items():
        A.add(1, S.N, look(lambda f: _ballpos(st, f)), 0, 0)
        A.add(140, S.N, arms_up(60, 20, 10), 8, 0)
        A.add(140, S.N, smile_eyes, 8, 0)
    fireflies_bg(S)
    S.camera(22, 0)
    c = gpos_night('pikachu', 0.3)
    S.cam_keys([(1, c + Vector((0.3, -4.5, 0.1)), IGNITE + Vector((0, 0, 1.0)), 24),
                (90, c + Vector((0.5, -6.5, 0.3)), STAR_HOME + Vector((0, 0, -5)), 22),
                (S.N, c + Vector((0.8, -9.5, 0.5)), TREE + Vector((0, 0, 9.5)), 20)])
    grass_at(S, c)


@shot('s37_glow', 6, 'night')
def s37(S):
    """the whole tree glows; everyone cheers around the bonfire"""
    setup_star(S)
    S.glow(1, star=1.0, lantern=1.0)
    cs = night_cast(S, ALL7 + ['charizard'])
    cheer_all(cs, 1, S.N)
    cs['charizard'].add(1, S.N, roar, 10, 10)
    cs['charizard'].add(1, S.N, wings_spread(-30), 10, 0)
    bonfire(S, IGNITE + Vector((0, 0, -0.45)), -10)
    fireflies_bg(S)
    S.post.append(lambda: fx.twinkles(lambda f: STAR_HOME, 1, S.N, 1.2, 14, 85))
    S.camera(22, 0)
    S.cam_keys([(1, TREE + Vector((3, -20, 0.9)), TREE + Vector((0, 0, 7.5)), 22),
                (S.N, TREE + Vector((1.5, -17, 1.1)), TREE + Vector((0, 0, 8.0)), 22)])
    grass_at(S, TREE + Vector((0, -12, 0)))


@shot('s38_dance', 13, 'night')
def s38(S):
    """the festival dance around the bonfire"""
    setup_star(S)
    S.glow(1, star=1.0, lantern=1.0)
    ring_names = ['pikachu', 'raboot', 'sobble', 'piplup', 'greninja', 'garchomp', 'dragonite', 'charizard']
    fire = IGNITE + Vector((0, 0, -0.45))
    bonfire(S, fire, -10)
    rates = {'pikachu': 2.2, 'raboot': 2.2, 'sobble': 1.8, 'piplup': 2.0, 'greninja': 1.1, 'garchomp': 1.4, 'dragonite': 1.2, 'charizard': 1.2}
    rad = {'pikachu': 1.6, 'raboot': 1.8, 'sobble': 1.6, 'piplup': 1.6, 'greninja': 2.6, 'garchomp': 3.0, 'dragonite': 3.2, 'charizard': 3.0}
    cs = {}
    for i, n in enumerate(ring_names):
        A = S.actor(n)
        a0 = i / len(ring_names) * 2 * math.pi
        # everyone circles slowly around the fire while dancing
        for f in range(1, S.N + 1, 12):
            a = a0 + (f / S.N) * 1.2
            p = (fire.x + math.cos(a) * rad[n], fire.y + math.sin(a) * rad[n])
            A.key(f, p, face(p, fire))
        A.face_frames = [(1, S.N)]
        A.add(1, S.N, dance(rates[n], 1.0 if A.c['height'] < 1 else 0.6), 10, 10)
        A.add(1, S.N, smile_eyes, 0, 0)
        A.add(1, S.N, tail_wag(2.5, 20), 0, 0)
        cs[n] = A
    cs['piplup'].add(100, 150, spin(2, 0.3), 4, 4)
    cs['garchomp'].add(150, 210, spin(1, 0.1), 6, 6)
    cs['greninja'].add(200, 250, lambda A, f, u, t: ({}, V(0, 0, 1.2 * math.sin(u * math.pi)), R(-360 * smoother(u))), 3, 3)
    cs['pikachu'].add(220, 280, hop(3, 0.6, 0.35), 4, 4)
    cs['raboot'].add(220, 280, hop(3, 0.6, 0.25), 4, 4)
    fireflies_bg(S, 120)
    S.camera(28, 2.8)
    S.cam_fn(orbit(fire + Vector((0, 0, 0.3)), 8.5, 2.6, -20, 50, 30, S.N), step=3)
    grass_at(S, fire)


@shot('s39_fireworks', 8, 'night')
def s39(S):
    """Charizard launches flames into the sky - fireworks bloom over the festival tree"""
    setup_star(S)
    S.glow(1, star=1.0, lantern=1.0)
    cs = night_cast(S, ['charizard', 'pikachu', 'raboot', 'dragonite'])
    bonfire(S, IGNITE + Vector((0, 0, -0.45)), -10)
    Cz = cs['charizard']
    cl = NIGHT['charizard']
    Cz.key(1, cl, 180)
    Cz.add(10, 70, breathe_fire, 6, 6)
    Cz.add(10, 70, lambda A, f, u, t: put(put({}, A, A.c['head'], R(-35)), A, A.c['neck'][0], R(-15)), 8, 8)
    nose = 'center_nose' if 'center_nose' in Cz.bones else Cz.c['head']
    sky = [TREE + Vector((-8, 12, 34)), TREE + Vector((10, 18, 40)), TREE + Vector((0, 25, 46)), TREE + Vector((-14, 22, 42)), TREE + Vector((14, 6, 36))]

    def fw():
        src = lambda f: Cz.bone_pos(f, nose)
        fx.fire_stream(src, lambda f: (Vector((0, 0.35, 1)).normalized()), 22, 60, 4, 9.0, 20, 0.08, 0.1, 0.7, 86)
        for i, b in enumerate(sky):
            fx.firework(src(40), b, 40 + i * 12, 70 + i * 14, i, 170, 13, 90 + i)
    S.post.append(fw)
    for n, A in cs.items():
        if n != 'charizard':
            A.add(30, S.N, look(TREE + Vector((0, 20, 40))), 10, 0)
            A.add(80, S.N, arms_up(60, 20, 8), 8, 0)
    S.camera(22, 0)
    S.cam_keys([(1, TREE + Vector((6, -24, 1.5)), TREE + Vector((0, 4, 12)), 22),
                (S.N, TREE + Vector((5, -22, 1.4)), TREE + Vector((0, 6, 18)), 22)])
    grass_at(S, TREE + Vector((0, -12, 0)))


@shot('s40_watch', 8, 'night')
def s40(S):
    """side by side, the eight friends watch the fireworks"""
    setup_star(S)
    S.glow(1, star=1.0, lantern=1.0)
    line = [('garchomp', -3.6), ('greninja', -2.3), ('raboot', -1.25), ('pikachu', -0.45), ('sobble', 0.15), ('piplup', 0.75), ('dragonite', 2.0), ('charizard', 3.5)]
    base = Vector((3.0, 20.6))
    sky = [TREE + Vector((-6, 20, 36)), TREE + Vector((8, 26, 42)), TREE + Vector((-12, 30, 40)), TREE + Vector((4, 34, 48))]
    for n, dx in line:
        A = S.actor(n)
        p = (base.x + dx, base.y + 0.25 * abs(dx))
        A.key(1, p, 180 + dx * 2)
        A.add(1, S.N, look(TREE + Vector((0, 24, 40)), 0.9), 0, 0)
        A.add(1, S.N, smile_eyes, 0, 0)
    S.actors['pikachu'].add(60, S.N, lambda A, f, u, t: arm_pose(A, 'left', 0, 30, 60), 12, 0)
    S.actors['sobble'].add(60, S.N, lambda A, f, u, t: arm_pose(A, 'right', 0, 30, 60), 12, 0)

    def fw():
        for i, b in enumerate(sky):
            fx.firework(TREE + Vector((0, 10, 0)), b, 1 + i * 38, 26 + i * 40, i + 1, 170, 14, 95 + i)
    S.post.append(fw)
    bonfire(S, IGNITE + Vector((0, 0, -0.45)), -10)
    S.camera(24, 0)
    c = Vector((base.x, base.y, H(*base) + 0.4))
    S.cam_keys([(1, c + Vector((0.2, -6.5, 0.9)), c + Vector((0, 8, 5.0)), 24),
                (S.N, c + Vector((0.2, -5.8, 0.8)), c + Vector((0, 8, 6.0)), 24)])
    grass_at(S, c)


@shot('s41_finale', 15, 'night', samples=16)
def s41(S):
    """crane up and away over the glowing tree and the sleeping island. The End."""
    setup_star(S)
    S.glow(1, star=1.0, lantern=1.0)
    fire = IGNITE + Vector((0, 0, -0.45))
    bonfire(S, fire, -10)
    ring_names = ['pikachu', 'raboot', 'sobble', 'piplup', 'greninja', 'garchomp', 'dragonite', 'charizard']
    rad = {'pikachu': 1.6, 'raboot': 1.8, 'sobble': 1.6, 'piplup': 1.6, 'greninja': 2.6, 'garchomp': 3.0, 'dragonite': 3.2, 'charizard': 3.0}
    for i, n in enumerate(ring_names):
        A = S.actor(n)
        a0 = i / len(ring_names) * 2 * math.pi + 1.2
        for f in range(1, S.N + 1, 12):
            a = a0 + (f / S.N) * 1.6
            p = (fire.x + math.cos(a) * rad[n], fire.y + math.sin(a) * rad[n])
            A.key(f, p, face(p, fire))
        A.face_frames = [(1, S.N)]
        A.add(1, S.N, dance(1.6, 0.5), 10, 10)
    sky = [TREE + Vector((-10, 30, 50)), TREE + Vector((12, 36, 56)), TREE + Vector((0, 50, 62)), TREE + Vector((-18, 45, 54)),
           TREE + Vector((20, 20, 52))]

    def fw():
        for i, b in enumerate(sky):
            fx.firework(TREE + Vector((0, 10, 0)), b, 20 + i * 50, 48 + i * 52, i + 2, 170, 16, 100 + i)
        fx.fireflies((4, 22, 0), 22, 150, 1, S.N, 0.3, 4.0, 101, ground=H, rise=0.05)
    S.post.append(fw)
    S.camera(26, 0)
    S.cam_keys([(1, fire + Vector((2, -9, 1.2)), fire + Vector((0, 2, 1.0)), 26),
                (150, TREE + Vector((10, -40, 22)), TREE + Vector((0, 0, 9)), 26),
                (S.N, TREE + Vector((40, -120, 70)), TREE + Vector((0, 10, 14)), 28)])
    S.fade_title('The End', 250, S.N, size=0.07, y=0.0, fin=8, fout=1)
    grass_at(S, TREE + Vector((0, -10, 0)))


@shot('s16b_starhit', 3, 'afternoon')
def s16b(S):
    """...and smacks the Star right off the top of the tree"""
    setup_star(S)
    ball = S.obj('Ball')
    g = gpos('garchomp')
    kick_spot = g + Vector((-0.4, 0.9, 0.16))
    hit = STAR_HOME + Vector((0.25, -0.25, 0.0))
    o = -48
    ballistic(S, ball, kick_spot, hit, 12 + o, 62 + o, 1.5, (25, 4, 0))
    ballistic(S, ball, hit, TREE + Vector((9, -5, 2.0)), 62 + o, 104 + o, 3.5, (8, 0, 3))
    st = S.obj('Star')
    S.key_obj(st, 13, STAR_HOME, (0, 0, 0))
    ballistic(S, st, STAR_HOME, STAR_HOME + Vector((-1.2, 1.0, -3.0)), 14, S.N + 20, 1.6, (3, 5, 2))
    S.post.append(lambda: fx.glow_burst(hit, 14, (1.0, 0.85, 0.5), 1.2, 30, 7, 6e3))
    S.camera(40, 0)
    S.cam_keys([(1, STAR_HOME + Vector((5.0, -13.0, -1.0)), STAR_HOME + Vector((0.3, -0.6, -1.2)), 40),
                (20, STAR_HOME + Vector((5.0, -13.0, -1.1)), STAR_HOME + Vector((0, 0, -0.4)), 40),
                (S.N, STAR_HOME + Vector((5.0, -13.0, -1.6)), STAR_HOME + Vector((-0.8, 0.6, -2.4)), 38)])
    S.shake(0.015, 2.0)
    grass_at(S, TREE)
