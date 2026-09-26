# Keyframed particle-style effects built from plain objects (deterministic,
# render-order independent).  Colour/alpha of each piece is driven by the
# object colour (Object Info node) so one material serves many objects.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler, noise

FPS = 24
_M = {}
_ME = {}


def _coll():
    c = bpy.data.collections.get('FX')
    if c is None:
        c = bpy.data.collections.new('FX')
        bpy.context.scene.collection.children.link(c)
    return c


def mat_glow(name='FX_Glow', strength=12.0, soft=1.5):
    """emissive, colour & alpha from object colour, soft edges by facing ratio"""
    key = (name, strength, soft)
    if key in _M:
        return _M[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    oi = nt.nodes.new('ShaderNodeObjectInfo')
    lw = nt.nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.5
    fac = nt.nodes.new('ShaderNodeMath')
    fac.operation = 'SUBTRACT'
    fac.inputs[0].default_value = 1.0
    nt.links.new(lw.outputs['Facing'], fac.inputs[1])
    pw = nt.nodes.new('ShaderNodeMath')
    pw.operation = 'POWER'
    nt.links.new(fac.outputs[0], pw.inputs[0])
    pw.inputs[1].default_value = soft
    a = nt.nodes.new('ShaderNodeMath')
    a.operation = 'MULTIPLY'
    a.use_clamp = True
    nt.links.new(pw.outputs[0], a.inputs[0])
    nt.links.new(oi.outputs['Alpha'], a.inputs[1])
    em = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(oi.outputs['Color'], em.inputs['Color'])
    st = nt.nodes.new('ShaderNodeMath')
    st.operation = 'MULTIPLY'
    nt.links.new(oi.outputs['Alpha'], st.inputs[0])
    st.inputs[1].default_value = strength
    nt.links.new(st.outputs[0], em.inputs['Strength'])
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(a.outputs[0], mx.inputs['Fac'])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    m.surface_render_method = 'BLENDED'
    m.use_transparency_overlap = False
    _M[key] = m
    return m


def mat_fire():
    """fire puff: emissive with noisy breakup; colour/alpha from object colour"""
    if 'fire' in _M:
        return _M['fire']
    m = bpy.data.materials.new('FX_Fire')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    oi = nt.nodes.new('ShaderNodeObjectInfo')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.noise_dimensions = '4D'
    nz.inputs['Scale'].default_value = 2.5
    nz.inputs['Detail'].default_value = 4
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    nt.links.new(oi.outputs['Random'], nz.inputs['W'])
    lw = nt.nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.45
    inv = nt.nodes.new('ShaderNodeMath')
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    nt.links.new(lw.outputs['Facing'], inv.inputs[1])
    edge = nt.nodes.new('ShaderNodeMath')
    edge.operation = 'MULTIPLY'
    nt.links.new(inv.outputs[0], edge.inputs[0])
    nt.links.new(nz.outputs['Fac'], edge.inputs[1])
    mr = nt.nodes.new('ShaderNodeMapRange')
    nt.links.new(edge.outputs[0], mr.inputs['Value'])
    mr.inputs['From Min'].default_value = 0.08
    mr.inputs['From Max'].default_value = 0.4
    a = nt.nodes.new('ShaderNodeMath')
    a.operation = 'MULTIPLY'
    a.use_clamp = True
    nt.links.new(mr.outputs[0], a.inputs[0])
    nt.links.new(oi.outputs['Alpha'], a.inputs[1])
    em = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(oi.outputs['Color'], em.inputs['Color'])
    st = nt.nodes.new('ShaderNodeMath')
    st.operation = 'MULTIPLY'
    nt.links.new(oi.outputs['Alpha'], st.inputs[0])
    st.inputs[1].default_value = 14.0
    nt.links.new(st.outputs[0], em.inputs['Strength'])
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(a.outputs[0], mx.inputs['Fac'])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    m.surface_render_method = 'BLENDED'
    _M['fire'] = m
    return m


def mat_water_fx():
    if 'water' in _M:
        return _M['water']
    m = bpy.data.materials.new('FX_Water')
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = (0.75, 0.88, 0.95, 1)
    bs.inputs['Roughness'].default_value = 0.05
    bs.inputs['Coat Weight'].default_value = 0.5
    bs.inputs['Emission Color'].default_value = (0.6, 0.8, 0.9, 1)
    bs.inputs['Emission Strength'].default_value = 0.15
    oi = nt.nodes.new('ShaderNodeObjectInfo')
    nt.links.new(oi.outputs['Alpha'], bs.inputs['Alpha'])
    m.surface_render_method = 'BLENDED'
    _M['water'] = m
    return m


def mat_smoke():
    if 'smoke' in _M:
        return _M['smoke']
    m = bpy.data.materials.new('FX_Smoke')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    oi = nt.nodes.new('ShaderNodeObjectInfo')
    df = nt.nodes.new('ShaderNodeBsdfDiffuse')
    nt.links.new(oi.outputs['Color'], df.inputs['Color'])
    lw = nt.nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.5
    inv = nt.nodes.new('ShaderNodeMath')
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    nt.links.new(lw.outputs['Facing'], inv.inputs[1])
    pw = nt.nodes.new('ShaderNodeMath')
    pw.operation = 'POWER'
    pw.inputs[1].default_value = 2.0
    nt.links.new(inv.outputs[0], pw.inputs[0])
    a = nt.nodes.new('ShaderNodeMath')
    a.operation = 'MULTIPLY'
    a.use_clamp = True
    nt.links.new(pw.outputs[0], a.inputs[0])
    nt.links.new(oi.outputs['Alpha'], a.inputs[1])
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(a.outputs[0], mx.inputs['Fac'])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(df.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    m.surface_render_method = 'BLENDED'
    _M['smoke'] = m
    return m


def sphere_mesh(name='fx_sphere', sub=2, r=1.0, bumpy=0.0, seed=0):
    key = (name, sub, r, bumpy, seed)
    if key in _ME:
        return _ME[key]
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    if bumpy:
        off = Vector((seed * 3.1, seed * 1.7, seed * 5.3))
        for v in bm.verts:
            v.co *= 1 + bumpy * noise.noise(v.co * 1.8 + off)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    _ME[key] = me
    return me


def bolt_mesh(seed, length=1.0, width=0.025, segs=7):
    """jagged lightning ribbon (two crossed ribbons so it reads from any angle)"""
    key = ('bolt', seed)
    if key in _ME:
        return _ME[key]
    r = random.Random(seed)
    pts = [Vector((0, 0, 0))]
    for i in range(1, segs + 1):
        u = i / segs
        pts.append(Vector((u * length, r.uniform(-0.12, 0.12) * length, r.uniform(-0.12, 0.12) * length)))
    verts, faces = [], []
    for axis in (Vector((0, 0, 1)), Vector((0, 1, 0))):
        base = len(verts)
        for i, p in enumerate(pts):
            w = width * (1 - 0.7 * i / segs)
            verts += [p + axis * w, p - axis * w]
        for i in range(segs):
            k = base + i * 2
            faces.append((k, k + 1, k + 3, k + 2))
    me = bpy.data.meshes.new('bolt')
    me.from_pydata(verts, [], faces)
    _ME[key] = me
    return me


def ring_mesh(r=1.0, w=0.08, seg=48):
    key = ('ring', r, w, seg)
    if key in _ME:
        return _ME[key]
    verts, faces = [], []
    for i in range(seg):
        a = i / seg * 2 * math.pi
        c, s = math.cos(a), math.sin(a)
        verts += [((r - w) * c, (r - w) * s, 0), ((r + w) * c, (r + w) * s, 0)]
        j = (i + 1) % seg
        faces.append((2 * i, 2 * i + 1, 2 * j + 1, 2 * j))
    me = bpy.data.meshes.new('ring')
    me.from_pydata(verts, [], faces)
    _ME[key] = me
    return me


def spawn(me, mat, name='fx'):
    ob = bpy.data.objects.new(name, me)
    if not me.materials:
        me.materials.append(mat)
    ob.material_slots[0].link = 'OBJECT'
    ob.material_slots[0].material = mat
    ob.visible_shadow = False
    _coll().objects.link(ob)
    return ob


def keyframes(ob, keys, interp='LINEAR'):
    """keys: list of (frame, loc, scale(float or Vector), rgba, rot(Euler or None))"""
    for f, loc, sc, col, rot in keys:
        ob.location = loc
        ob.scale = (sc, sc, sc) if isinstance(sc, (int, float)) else sc
        ob.color = col
        ob.keyframe_insert('location', frame=f)
        ob.keyframe_insert('scale', frame=f)
        ob.keyframe_insert('color', frame=f)
        if rot is not None:
            ob.rotation_euler = rot
            ob.keyframe_insert('rotation_euler', frame=f)
    if ob.animation_data and ob.animation_data.action:
        for fc in ob.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = interp


def hidden_key(ob, f):
    ob.scale = (0, 0, 0)
    ob.color = (0, 0, 0, 0)
    ob.keyframe_insert('scale', frame=f)
    ob.keyframe_insert('color', frame=f)


def lerp_col(stops, u):
    """stops: [(u, (r,g,b,a)), ...]"""
    if u <= stops[0][0]:
        return stops[0][1]
    for (u0, c0), (u1, c1) in zip(stops, stops[1:]):
        if u <= u1:
            w = (u - u0) / (u1 - u0)
            return tuple(a + (b - a) * w for a, b in zip(c0, c1))
    return stops[-1][1]


def point_light(name, loc, color, energy_keys, radius=0.2):
    li = bpy.data.lights.new(name, 'POINT')
    li.color = color
    li.shadow_soft_size = radius
    li.use_shadow = False
    ob = bpy.data.objects.new(name, li)
    ob.location = loc
    _coll().objects.link(ob)
    for f, e in energy_keys:
        li.energy = e
        li.keyframe_insert('energy', frame=f)
    return ob


# ---------------------------------------------------------------------------
# effects
# ---------------------------------------------------------------------------
FIRE_STOPS = [(0.0, (1.0, 0.95, 0.75, 1.0)), (0.2, (1.0, 0.7, 0.2, 1.0)), (0.55, (1.0, 0.35, 0.05, 0.8)),
              (0.85, (0.6, 0.1, 0.02, 0.35)), (1.0, (0.2, 0.05, 0.02, 0.0))]


def fire_stream(src_fn, dir_fn, f0, f1, rate=5, speed=7.0, life=16, spread=0.14, size=0.12, grow=0.9, seed=1,
                light=True, gentle=False):
    """src_fn(f)->Vector mouth position, dir_fn(f)->unit Vector"""
    r = random.Random(seed)
    mat = mat_fire()
    meshes = [sphere_mesh('fx_puff', 2, 1.0, 0.35, k) for k in range(4)]
    for f in range(int(f0), int(f1)):
        for k in range(rate):
            t0 = f + k / rate
            o = src_fn(f)
            d = dir_fn(f).copy()
            d += Vector((r.gauss(0, spread), r.gauss(0, spread), r.gauss(0, spread)))
            d.normalize()
            sp = speed * r.uniform(0.8, 1.15)
            lf = life * r.uniform(0.8, 1.2)
            ob = spawn(meshes[r.randrange(4)], mat, 'flame')
            rot0 = Euler((r.uniform(0, 6), r.uniform(0, 6), r.uniform(0, 6)))
            keys = []
            for j in range(6):
                u = j / 5
                age = u * lf / FPS
                dist = sp * age * (1 - 0.35 * u)
                p = o + d * dist + Vector((0, 0, 0.9 * age * age * 4))
                s = size * (1 + grow * 6 * u) * (1 - 0.3 * u * u)
                col = lerp_col(FIRE_STOPS, u)
                if gentle:
                    col = (col[0], col[1], col[2], col[3] * 0.8)
                keys.append((t0 + u * lf, p, s, col, Euler((rot0.x + u * 2, rot0.y, rot0.z + u))))
            hidden_key(ob, t0 - 1)
            keyframes(ob, keys)
            hidden_key(ob, t0 + lf + 1)
    if light:
        ek = [(f0 - 3, 0)]
        for f in range(int(f0), int(f1) + 1, 2):
            ek.append((f, (2500 if not gentle else 900) * r.uniform(0.75, 1.0)))
        ek.append((f1 + 8, 0))
        lo = point_light('FireLight', src_fn(f0), (1.0, 0.55, 0.2), ek, 0.5)
        for f in range(int(f0), int(f1) + 1, 3):
            lo.location = src_fn(f) + dir_fn(f) * speed * 0.15
            lo.keyframe_insert('location', frame=f)


def sparks(center_fn, f0, f1, radius=0.25, n=6, seed=3, color=(1.0, 0.92, 0.3), light=True, prob=0.55):
    """flickering electric bolts around a moving point"""
    r = random.Random(seed)
    mat = mat_glow('FX_Spark', 30.0, 0.3)
    obs = [spawn(bolt_mesh(seed * 10 + k), mat, 'bolt') for k in range(n)]
    for ob in obs:
        hidden_key(ob, f0 - 1)
    for f in range(int(f0), int(f1) + 1):
        c = center_fn(f)
        for ob in obs:
            if r.random() < prob:
                ob.location = c + Vector((r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-0.5, 1))) * radius * 0.4
                ob.rotation_euler = (r.uniform(0, 6.3), r.uniform(0, 6.3), r.uniform(0, 6.3))
                s = radius * r.uniform(0.6, 1.3)
                ob.scale = (s, s, s)
                ob.color = (*color, 1.0)
            else:
                ob.scale = (0, 0, 0)
                ob.color = (0, 0, 0, 0)
            for path in ('location', 'rotation_euler', 'scale', 'color'):
                ob.keyframe_insert(path, frame=f)
    for ob in obs:
        hidden_key(ob, f1 + 1)
        for fc in ob.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'CONSTANT'
    if light:
        ek = [(f0 - 1, 0)] + [(f, r.uniform(20, 120) * radius * 4) for f in range(int(f0), int(f1) + 1)] + [(f1 + 1, 0)]
        lo = point_light('SparkLight', center_fn(f0), color, ek, 0.1)
        for f in range(int(f0), int(f1) + 1, 2):
            lo.location = center_fn(f)
            lo.keyframe_insert('location', frame=f)
        for fc in lo.data.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'CONSTANT'


def splash(pos, f0, size=1.0, n=40, seed=5, water_z=None, rings=3):
    r = random.Random(seed)
    pos = Vector(pos)
    wz = pos.z if water_z is None else water_z
    wm = mat_water_fx()
    drop = sphere_mesh('fx_drop', 2, 1.0)
    for i in range(n):
        ob = spawn(drop, wm, 'drop')
        a = r.uniform(0, 2 * math.pi)
        up = r.uniform(2.5, 5.0) * math.sqrt(size)
        out = r.uniform(0.6, 1.8) * math.sqrt(size)
        v = Vector((math.cos(a) * out, math.sin(a) * out, up))
        p0 = pos + Vector((math.cos(a), math.sin(a), 0)) * 0.15 * size
        s0 = r.uniform(0.02, 0.05) * size
        keys = []
        t = 0.0
        tmax = 2 * v.z / 9.81
        steps = max(3, int(tmax * FPS / 2))
        for j in range(steps + 1):
            t = tmax * j / steps
            p = p0 + Vector((v.x * t, v.y * t, v.z * t - 4.905 * t * t))
            keys.append((f0 + t * FPS, p, s0 * (1 - 0.4 * j / steps), (1, 1, 1, 0.9), None))
        hidden_key(ob, f0 - 1)
        keyframes(ob, keys)
        hidden_key(ob, f0 + tmax * FPS + 1)
    # central column
    col = spawn(sphere_mesh('fx_col', 3, 1.0, 0.3, 2), wm, 'splashcol')
    hidden_key(col, f0 - 1)
    keyframes(col, [(f0, pos, Vector((0.15, 0.15, 0.2)) * size, (1, 1, 1, 0.8), None),
                    (f0 + 6, pos + Vector((0, 0, 0.35 * size)), Vector((0.25, 0.25, 0.6)) * size, (1, 1, 1, 0.6), None),
                    (f0 + 16, pos + Vector((0, 0, 0.1 * size)), Vector((0.3, 0.3, 0.15)) * size, (1, 1, 1, 0.0), None)])
    hidden_key(col, f0 + 17)
    gm = mat_glow('FX_Foam', 1.2, 0.8)
    for k in range(rings):
        ring = spawn(ring_mesh(1.0, 0.06), gm, 'ripple')
        fs = f0 + k * 7
        hidden_key(ring, fs - 1)
        keyframes(ring, [(fs, Vector((pos.x, pos.y, wz + 0.01)), 0.2 * size, (0.9, 0.95, 1.0, 0.9), None),
                         (fs + 40, Vector((pos.x, pos.y, wz + 0.01)), 2.2 * size, (0.9, 0.95, 1.0, 0.0), None)])
        hidden_key(ring, fs + 41)


def tears(eye_fn, f0, f1, side_dir_fn, rate=2, seed=9, size=0.018):
    """fountain tears: eye_fn(f)->Vector, side_dir_fn(f)->outward unit vector"""
    r = random.Random(seed)
    wm = mat_water_fx()
    drop = sphere_mesh('fx_drop', 2, 1.0)
    for f in range(int(f0), int(f1), rate):
        o = eye_fn(f)
        d = side_dir_fn(f)
        v = d * r.uniform(0.35, 0.6) + Vector((0, 0, r.uniform(0.6, 1.0)))
        ob = spawn(drop, wm, 'tear')
        tmax = (v.z + math.sqrt(v.z * v.z + 2 * 9.81 * 0.35)) / 9.81
        keys = []
        for j in range(6):
            t = tmax * j / 5
            keys.append((f + t * FPS, o + Vector((v.x * t, v.y * t, v.z * t - 4.905 * t * t)), size, (1, 1, 1, 0.9), None))
        hidden_key(ob, f - 1)
        keyframes(ob, keys)
        hidden_key(ob, f + tmax * FPS + 1)


def fireflies(center, radius, count, f0, f1, zmin=0.3, zmax=3.0, seed=11, ground=None, rise=0.0):
    r = random.Random(seed)
    mat = mat_glow('FX_Firefly', 25.0, 0.6)
    me = sphere_mesh('fx_ff', 1, 1.0)
    center = Vector(center)
    for i in range(count):
        ob = spawn(me, mat, 'firefly')
        a = r.uniform(0, 2 * math.pi)
        rr = radius * math.sqrt(r.random())
        x, y = center.x + math.cos(a) * rr, center.y + math.sin(a) * rr
        gz = ground(x, y) if ground else center.z
        z0 = gz + r.uniform(zmin, zmax)
        off = Vector((r.uniform(0, 100), r.uniform(0, 100), r.uniform(0, 100)))
        ph = r.uniform(0, 6.28)
        keys = []
        born = f0 + r.uniform(0, 40)
        for f in range(int(born), int(f1) + 1, 4):
            t = (f - f0) / FPS
            dp = noise.noise_vector(off + Vector((t * 0.25, 0, 0))) * 1.2
            p = Vector((x, y, z0 + rise * t)) + dp
            glow = 0.5 + 0.5 * math.sin(t * r.uniform(2, 4) + ph)
            fade = min(1.0, (f - born) / 20)
            keys.append((f, p, 0.022, (0.85, 1.0, 0.35, (0.15 + 0.85 * glow) * fade), None))
        hidden_key(ob, born - 1)
        keyframes(ob, keys)


PALETTES = [((1.0, 0.3, 0.2), (1.0, 0.8, 0.3)), ((0.3, 0.6, 1.0), (0.8, 0.9, 1.0)), ((0.4, 1.0, 0.4), (1.0, 1.0, 0.6)),
            ((1.0, 0.4, 0.9), (1.0, 0.8, 0.9)), ((1.0, 0.75, 0.2), (1.0, 1.0, 0.8))]


def firework(launch, burst, f_launch, f_burst, pal=0, n=110, speed=14.0, seed=13, life=48):
    r = random.Random(seed)
    launch, burst = Vector(launch), Vector(burst)
    c1, c2 = PALETTES[pal % len(PALETTES)]
    mat = mat_glow('FX_Firework', 40.0, 0.4)
    me = sphere_mesh('fx_spark', 1, 1.0)
    # rocket
    rk = spawn(me, mat, 'rocket')
    keys = []
    for j in range(8):
        u = j / 7
        p = launch.lerp(burst, 1 - (1 - u) ** 2)
        keys.append((f_launch + u * (f_burst - f_launch), p, 0.12, (1.0, 0.85, 0.5, 1.0), None))
    hidden_key(rk, f_launch - 1)
    keyframes(rk, keys)
    hidden_key(rk, f_burst + 1)
    # trail
    for j in range(10):
        u = j / 10
        tf = f_launch + u * (f_burst - f_launch)
        p = launch.lerp(burst, 1 - (1 - u) ** 2)
        tb = spawn(me, mat, 'trail')
        hidden_key(tb, tf - 1)
        keyframes(tb, [(tf, p, 0.09, (1.0, 0.7, 0.3, 0.8), None), (tf + 10, p + Vector((0, 0, -0.3)), 0.05, (0.6, 0.3, 0.1, 0.0), None)])
        hidden_key(tb, tf + 11)
    # burst
    for i in range(n):
        ob = spawn(me, mat, 'spark')
        d = Vector((r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 1))).normalized()
        sp = speed * r.uniform(0.85, 1.05)
        lf = life * r.uniform(0.8, 1.2)
        keys = []
        for j in range(9):
            u = j / 8
            t = u * lf / FPS
            k = 1.6
            dist = sp * (1 - math.exp(-k * t)) / k
            p = burst + d * dist + Vector((0, 0, -2.2 * t * t))
            col = c1 if u < 0.45 else c2
            a = 1.0 if u < 0.6 else max(0.0, 1 - (u - 0.6) / 0.4)
            tw = 0.7 + 0.3 * math.sin(i + j * 2.3)
            keys.append((f_burst + u * lf, p, 0.2 * (1 - 0.5 * u), (*col, a * tw), None))
        hidden_key(ob, f_burst - 1)
        keyframes(ob, keys)
        hidden_key(ob, f_burst + lf + 1)
    point_light('BurstLight', burst, c1, [(f_burst - 1, 0), (f_burst, 2.5e4), (f_burst + 8, 1e4), (f_burst + 40, 0)], 3.0)


def smoke(src_fn, f0, f1, every=6, seed=17, size=0.12, rise=0.5, color=(0.5, 0.5, 0.52), alpha=0.5, life=48, drift=(0.1, 0, 0)):
    r = random.Random(seed)
    mat = mat_smoke()
    for f in range(int(f0), int(f1), every):
        o = src_fn(f)
        ob = spawn(sphere_mesh('fx_smoke', 2, 1.0, 0.35, r.randrange(4)), mat, 'smoke')
        keys = []
        for j in range(5):
            u = j / 4
            t = u * life / FPS
            p = o + Vector((drift[0] * t + r.gauss(0, 0.05) * u, drift[1] * t, rise * t))
            keys.append((f + u * life, p, size * (1 + 3 * u), (*color, alpha * math.sin(math.pi * min(1, u * 1.3 + 0.1)) * (1 - u)), None))
        hidden_key(ob, f - 1)
        keyframes(ob, keys)
        hidden_key(ob, f + life + 1)


def glow_burst(pos, f0, color=(1.0, 0.85, 0.4), size=2.0, n_sparkles=40, seed=21, light=4e4):
    """flash sphere + expanding ring + floating sparkles"""
    r = random.Random(seed)
    pos = Vector(pos)
    mat = mat_glow('FX_Burst', 20.0, 1.2)
    me = sphere_mesh('fx_glowball', 3, 1.0)
    b = spawn(me, mat, 'flash')
    hidden_key(b, f0 - 1)
    keyframes(b, [(f0, pos, 0.1, (*color, 1.0), None), (f0 + 5, pos, size * 0.6, (*color, 0.9), None), (f0 + 24, pos, size, (*color, 0.0), None)])
    hidden_key(b, f0 + 25)
    ring = spawn(ring_mesh(1.0, 0.05), mat_glow('FX_Ring', 15.0, 0.1), 'ring')
    hidden_key(ring, f0 - 1)
    keyframes(ring, [(f0, pos, 0.2, (*color, 1.0), Euler((math.pi / 2, 0, 0))), (f0 + 20, pos, size * 2.5, (*color, 0.0), Euler((math.pi / 2, 0, 0)))])
    hidden_key(ring, f0 + 21)
    sm = sphere_mesh('fx_spark', 1, 1.0)
    smat = mat_glow('FX_Sparkle', 30.0, 0.4)
    for i in range(n_sparkles):
        ob = spawn(sm, smat, 'sparkle')
        d = Vector((r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 1) * 0.6 + 0.3)).normalized()
        lf = r.uniform(30, 70)
        dist = size * r.uniform(0.8, 1.8)
        hidden_key(ob, f0 - 1)
        keyframes(ob, [(f0, pos, 0.03, (*color, 1.0), None), (f0 + lf * 0.5, pos + d * dist, 0.035, (*color, 0.9), None),
                       (f0 + lf, pos + d * dist * 1.2 + Vector((0, 0, 0.4)), 0.01, (*color, 0.0), None)])
        hidden_key(ob, f0 + lf + 1)
    point_light('BurstLight', pos, color, [(f0 - 1, 0), (f0 + 2, light), (f0 + 30, light * 0.15)], 0.5)


def twinkles(center_fn, f0, f1, radius=0.8, n=12, seed=23, color=(1.0, 0.9, 0.6)):
    """little glints orbiting around a (moving) glowing object"""
    r = random.Random(seed)
    mat = mat_glow('FX_Twinkle', 30.0, 0.3)
    me = sphere_mesh('fx_spark', 1, 1.0)
    for i in range(n):
        ob = spawn(me, mat, 'twinkle')
        ph = r.uniform(0, 6.28)
        sp = r.uniform(0.4, 1.0)
        rr = radius * r.uniform(0.5, 1.0)
        keys = []
        for f in range(int(f0), int(f1) + 1, 3):
            t = (f - f0) / FPS
            c = center_fn(f)
            p = c + Vector((math.cos(ph + t * sp) * rr, math.sin(ph + t * sp) * rr, math.sin(ph * 2 + t * 1.3) * rr * 0.5))
            a = max(0.0, math.sin(t * r.uniform(2, 5) + ph)) ** 3
            keys.append((f, p, 0.02, (*color, a), None))
        hidden_key(ob, f0 - 1)
        keyframes(ob, keys)
