# Festival props for the giant tree: lanterns, bunting, the Star, picnic, ball.
# Glow is controlled by scene custom properties (keyframed per shot):
#   scene["lantern_glow"]  0..1     scene["star_glow"]  0..1
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
import terrain as T


def _driver(sock_owner, path, prop, expr, index=-1):
    fc = sock_owner.driver_add(path, index) if index >= 0 else sock_owner.driver_add(path)
    d = fc.driver
    d.type = 'SCRIPTED'
    v = d.variables.new()
    v.name = 'g'
    v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'SCENE'
    v.targets[0].id = bpy.context.scene
    v.targets[0].data_path = f'["{prop}"]'
    d.expression = expr
    return fc


def mat_lantern(name, col):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes['Principled BSDF']
    # vertical ribs from object-space angle
    tc = nt.nodes.new('ShaderNodeTexCoord')
    gr = nt.nodes.new('ShaderNodeTexGradient')
    gr.gradient_type = 'RADIAL'
    nt.links.new(tc.outputs['Object'], gr.inputs['Vector'])
    mth = nt.nodes.new('ShaderNodeMath')
    mth.operation = 'PINGPONG'
    mth.inputs[1].default_value = 1 / 16
    nt.links.new(gr.outputs['Fac'], mth.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = 0.0
    mr.inputs['From Max'].default_value = 0.012
    mr.inputs['To Min'].default_value = 0.35
    mr.inputs['To Max'].default_value = 1.0
    nt.links.new(mth.outputs[0], mr.inputs['Value'])
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0
    mix.inputs['A'].default_value = (*col, 1)
    cc = nt.nodes.new('ShaderNodeCombineColor')
    for i in range(3):
        nt.links.new(mr.outputs[0], cc.inputs[i])
    nt.links.new(cc.outputs[0], mix.inputs['B'])
    nt.links.new(mix.outputs['Result'], bs.inputs['Base Color'])
    nt.links.new(mix.outputs['Result'], bs.inputs['Emission Color'])
    bs.inputs['Roughness'].default_value = 0.6
    bs.inputs['Subsurface Weight'].default_value = 0.4
    bs.inputs['Subsurface Radius'].default_value = (1, 0.6, 0.3)
    bs.inputs['Subsurface Scale'].default_value = 0.1
    bs.inputs['Emission Strength'].default_value = 0.0
    _driver(bs.inputs['Emission Strength'], 'default_value', 'lantern_glow', 'g*9')
    return m


def lantern_mesh(r=0.26):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=r)
    for v in bm.verts:
        v.co.z *= 1.2
        # flatten top/bottom
        if abs(v.co.z) > r * 1.0:
            v.co.z = math.copysign(r * 1.0, v.co.z)
    me = bpy.data.meshes.new('LanternBody')
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    return me


def cyl(name, r, h, z0=0.0, seg=10):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, z0 + h / 2))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def star_mesh(R=0.75, r=0.34, depth=0.28):
    bm = bmesh.new()
    top, bot = [], []
    for k in range(10):
        a = math.pi / 2 + k * math.pi / 5
        rr = R if k % 2 == 0 else r
        top.append(bm.verts.new((math.cos(a) * rr, 0, math.sin(a) * rr)))
    cf = bm.verts.new((0, -depth, 0))
    cb = bm.verts.new((0, depth, 0))
    for k in range(10):
        a, b = top[k], top[(k + 1) % 10]
        bm.faces.new((cf, a, b))
        bm.faces.new((cb, b, a))
    me = bpy.data.meshes.new('Star')
    bm.to_mesh(me)
    bm.free()
    return me


def mat_star():
    m = bpy.data.materials.new('StarCrystal')
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = (1.0, 0.78, 0.25, 1)
    bs.inputs['Metallic'].default_value = 0.3
    bs.inputs['Roughness'].default_value = 0.08
    bs.inputs['Coat Weight'].default_value = 1.0
    bs.inputs['Emission Color'].default_value = (1.0, 0.8, 0.35, 1)
    _driver(bs.inputs['Emission Strength'], 'default_value', 'star_glow', 'g*28')
    return m


def mat_simple(name, color, rough=0.6, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    for k, v in kw.items():
        bs.inputs[k].default_value = v
    return m


def catenary(a, b, sag, n=24):
    pts = []
    for i in range(n + 1):
        u = i / n
        p = a.lerp(b, u)
        p.z -= sag * 4 * u * (1 - u)
        pts.append(p)
    return pts


def build(W, slots, tree_base):
    sc = bpy.context.scene
    sc['lantern_glow'] = 0.0
    sc['star_glow'] = 0.0
    r = random.Random(77)
    coll = bpy.data.collections.new('Festival')
    W.children.link(coll)
    cols = [(0.95, 0.15, 0.08), (1.0, 0.45, 0.05), (1.0, 0.75, 0.15), (0.95, 0.3, 0.45), (0.9, 0.2, 0.15)]
    mats = [mat_lantern(f'Lantern_{i}', c) for i, c in enumerate(cols)]
    cap = mat_simple('LanternCap', (0.05, 0.03, 0.02), 0.5)
    string = mat_simple('String', (0.25, 0.2, 0.15), 0.8)
    body = lantern_mesh()
    capm = cyl('LanternCap', 0.13, 0.06)
    capm.materials.append(cap)
    lamp_positions = []
    for i, s in enumerate(slots):
        L = r.uniform(1.1, 2.2)
        p = s - Vector((0, 0, L))
        o = bpy.data.objects.new(f'Lantern.{i:03d}', body.copy())
        o.data.materials.append(mats[i % len(mats)])
        o.location = p
        o.rotation_euler = (0, 0, r.uniform(0, 6.28))
        coll.objects.link(o)
        for z in (0.26, -0.32):
            c = bpy.data.objects.new('LCap', capm)
            c.location = p + Vector((0, 0, z))
            coll.objects.link(c)
        st = bpy.data.objects.new('LString', cyl('LString', 0.008, L - 0.3, 0.0, 5))
        st.data.materials.append(string)
        st.location = p + Vector((0, 0, 0.3))
        coll.objects.link(st)
        lamp_positions.append(p)
        # warm light inside
        li = bpy.data.lights.new(f'LanternLight.{i:03d}', 'POINT')
        li.color = tuple(min(1.0, c * 1.1 + 0.15) for c in cols[i % len(cols)])
        li.shadow_soft_size = 0.25
        li.use_shadow = False
        li.energy = 0.0
        _driver(li, 'energy', 'lantern_glow', 'g*35')
        lo = bpy.data.objects.new(f'LanternLight.{i:03d}', li)
        lo.location = p
        coll.objects.link(lo)
    # bunting between neighbouring lanterns-slots
    flagcols = [(0.9, 0.1, 0.1), (1.0, 0.8, 0.1), (0.1, 0.45, 0.9), (0.1, 0.7, 0.3), (1.0, 1.0, 1.0)]
    fmats = [mat_simple(f'Flag_{i}', c, 0.7, **{'Subsurface Weight': 0.3}) for i, c in enumerate(flagcols)]
    by_angle = sorted(slots, key=lambda p: math.atan2(p.y - tree_base.y, p.x - tree_base.x))
    ring = [p for p in by_angle if (Vector((p.x, p.y)) - tree_base.xy).length > 4.5]
    fi = 0
    for a, b in zip(ring, ring[1:] + ring[:1]):
        if (a - b).length > 10 or (a - b).length < 2:
            continue
        pts = catenary(a + Vector((0, 0, -0.2)), b + Vector((0, 0, -0.2)), 0.5 + 0.08 * (a - b).length)
        cu = bpy.data.curves.new('BuntLine', 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = 0.01
        sp = cu.splines.new('POLY')
        sp.points.add(len(pts) - 1)
        for q, p in zip(sp.points, pts):
            q.co = (*p, 1)
        lo = bpy.data.objects.new('BuntLine', cu)
        cu.materials.append(string)
        coll.objects.link(lo)
        for k in range(1, len(pts) - 1, 2):
            p0, p1 = pts[k], pts[k + 1]
            d = (p1 - p0)
            mid = (p0 + p1) / 2
            me = bpy.data.meshes.new('Flag')
            side = Vector((d.y, -d.x, 0)).normalized() * 0.0
            me.from_pydata([p0, p1, mid + Vector((0, 0, -0.32))], [], [(0, 1, 2)])
            me.materials.append(fmats[fi % len(fmats)])
            fi += 1
            fo = bpy.data.objects.new('Flag', me)
            coll.objects.link(fo)
    # the Star on top of the tree
    star = bpy.data.objects.new('Star', star_mesh())
    star.data.materials.append(mat_star())
    bev = star.modifiers.new('bev', 'BEVEL')
    bev.width = 0.03
    bev.segments = 2
    star.location = tree_base + Vector((0, 0, 16.6))
    coll.objects.link(star)
    sl = bpy.data.lights.new('StarLight', 'POINT')
    sl.color = (1.0, 0.82, 0.45)
    sl.shadow_soft_size = 0.4
    sl.use_shadow = False
    _driver(sl, 'energy', 'star_glow', 'g*1500')
    slo = bpy.data.objects.new('StarLight', sl)
    slo.parent = star
    coll.objects.link(slo)
    pole = bpy.data.objects.new('StarPole', cyl('StarPole', 0.07, 2.4, -2.4 + 0.1, 8))
    pole.data.materials.append(bpy.data.materials.get('GiantBark') or string)
    pole.location = tree_base + Vector((0, 0, 16.6 - 0.6))
    coll.objects.link(pole)
    # picnic blanket + berries in front of the tree
    bx, by = 5.0, 22.5
    bz = float(T.height(bx, by)) + 0.015
    bpy.ops.mesh.primitive_plane_add(size=1, location=(bx, by, bz))
    bl = bpy.context.active_object
    bl.name = 'Blanket'
    bl.scale = (2.6, 2.0, 1)
    bl.rotation_euler = (0, 0, 0.3)
    bm_ = bpy.data.materials.new('Blanket')
    bm_.use_nodes = True
    nt = bm_.node_tree
    ck = nt.nodes.new('ShaderNodeTexChecker')
    ck.inputs['Scale'].default_value = 8
    ck.inputs['Color1'].default_value = (0.75, 0.08, 0.06, 1)
    ck.inputs['Color2'].default_value = (0.9, 0.85, 0.75, 1)
    nt.links.new(ck.outputs[0], nt.nodes['Principled BSDF'].inputs['Base Color'])
    nt.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
    nt.nodes['Principled BSDF'].inputs['Sheen Weight'].default_value = 0.6
    bl.data.materials.append(bm_)
    for c in list(bl.users_collection):
        c.objects.unlink(bl)
    coll.objects.link(bl)
    berry_cols = [(0.1, 0.3, 0.9), (0.95, 0.4, 0.6), (0.95, 0.75, 0.1), (0.7, 0.1, 0.2)]
    bmats = [mat_simple(f'Berry_{i}', c, 0.25, **{'Coat Weight': 0.6, 'Subsurface Weight': 0.3}) for i, c in enumerate(berry_cols)]
    plate = bpy.data.objects.new('Plate', cyl('Plate', 0.35, 0.04, 0, 24))
    plate.data.materials.append(mat_simple('Wood', (0.3, 0.16, 0.07), 0.6))
    plate.location = (bx + 0.4, by, bz)
    coll.objects.link(plate)
    bmesh_ = bmesh.new()
    bmesh.ops.create_uvsphere(bmesh_, u_segments=12, v_segments=8, radius=0.07)
    berry = bpy.data.meshes.new('Berry')
    bmesh_.to_mesh(berry)
    bmesh_.free()
    berry.shade_smooth()
    for k in range(14):
        a = r.uniform(0, 6.28)
        rr = r.uniform(0, 0.24)
        o = bpy.data.objects.new('Berry', berry.copy())
        o.data.materials.append(bmats[k % 4])
        o.location = (bx + 0.4 + math.cos(a) * rr, by + math.sin(a) * rr, bz + 0.1 + (0.08 if k > 9 else 0))
        coll.objects.link(o)
    # ball (shots animate it)
    bmesh_ = bmesh.new()
    bmesh.ops.create_uvsphere(bmesh_, u_segments=32, v_segments=16, radius=0.16)
    ballm = bpy.data.meshes.new('Ball')
    bmesh_.to_mesh(ballm)
    bmesh_.free()
    ballm.shade_smooth()
    mb = bpy.data.materials.new('Ball')
    mb.use_nodes = True
    nt = mb.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord')
    gr = nt.nodes.new('ShaderNodeTexGradient')
    gr.gradient_type = 'RADIAL'
    nt.links.new(tc.outputs['Object'], gr.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB')
    cr.color_ramp.interpolation = 'CONSTANT'
    el = cr.color_ramp.elements
    el[0].color = (0.9, 0.1, 0.08, 1)
    el[1].position = 1 / 6
    el[1].color = (1, 1, 1, 1)
    for i, c in enumerate([(0.1, 0.4, 0.95, 1), (1, 1, 1, 1), (1.0, 0.8, 0.05, 1), (1, 1, 1, 1)]):
        e = el.new((i + 2) / 6)
        e.color = c
    nt.links.new(gr.outputs['Fac'], cr.inputs[0])
    nt.links.new(cr.outputs[0], nt.nodes['Principled BSDF'].inputs['Base Color'])
    nt.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.35
    nt.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = 0.5
    ballm.materials.append(mb)
    ball = bpy.data.objects.new('Ball', ballm)
    ball.location = (6.5, 21.5, float(T.height(6.5, 21.5)) + 0.16)
    coll.objects.link(ball)
    return coll
