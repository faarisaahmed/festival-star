import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + '/'
# Builds world.blend: the island (terrain, water, waterfall, forests, grass,
# flowers, rocks, clouds, the giant festival tree).
import bpy, bmesh, math, random, sys, os
import numpy as np
from mathutils import Vector, Matrix, Euler, noise

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import terrain as T
import importlib

rng = random.Random(7)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def new_coll(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c


def link(obj, coll):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj


def grid_mesh(name, x0, x1, y0, y1, nx, ny, zfun):
    xs = np.linspace(x0, x1, nx)
    ys = np.linspace(y0, y1, ny)
    X, Y = np.meshgrid(xs, ys)
    Z = zfun(X, Y)
    verts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], -1).astype(np.float32)
    ii, jj = np.meshgrid(np.arange(nx - 1), np.arange(ny - 1))
    a = (jj * nx + ii).ravel()
    quads = np.stack([a, a + 1, a + nx + 1, a + nx], -1).astype(np.int32)
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(verts))
    me.vertices.foreach_set('co', verts.ravel())
    me.loops.add(quads.size)
    me.loops.foreach_set('vertex_index', quads.ravel())
    me.polygons.add(len(quads))
    me.polygons.foreach_set('loop_start', np.arange(0, quads.size, 4, dtype=np.int32))
    me.polygons.foreach_set('loop_total', np.full(len(quads), 4, dtype=np.int32))
    me.update(calc_edges=True)
    me.validate()
    uv = me.uv_layers.new(name='UVMap')
    lu = np.stack([X.ravel(), Y.ravel()], -1)[quads.ravel()]
    uv.data.foreach_set('uv', (lu / 10.0).astype(np.float32).ravel())
    me.shade_smooth()
    return me, X, Y, Z


def add_float_attr(me, name, values):
    at = me.attributes.new(name, 'FLOAT', 'POINT')
    at.data.foreach_set('value', np.asarray(values, dtype=np.float32).ravel())


def node(nt, typ, loc=(0, 0), **kw):
    n = nt.nodes.new(typ)
    n.location = loc
    for k, v in kw.items():
        if k in n.inputs.keys() if hasattr(n.inputs, 'keys') else False:
            n.inputs[k].default_value = v
        else:
            setattr(n, k, v)
    return n


def lnk(nt, a, b):
    nt.links.new(a, b)


def seg_dist(P, A, B):
    A = np.array(A, float)
    B = np.array(B, float)
    AB = B - A
    t = np.clip(((P[..., 0] - A[0]) * AB[0] + (P[..., 1] - A[1]) * AB[1]) / (AB @ AB), 0, 1)
    cx = A[0] + t * AB[0]
    cy = A[1] + t * AB[1]
    return np.hypot(P[..., 0] - cx, P[..., 1] - cy)


PATHS = [
    [(0, -40), (2, -15), (1, 5), (0, 20), (0, 27)],        # meadow -> festival tree
    [(1, 5), (-12, 0), (-24, -8)],                            # meadow -> lake shore
    [(2, -15), (15, 10), (22, 18)],                           # meadow -> Greninja rock
]


def path_mask(X, Y):
    P = np.stack([X, Y], -1)
    d = np.full(X.shape, 1e9)
    for pl in PATHS:
        for a, b in zip(pl[:-1], pl[1:]):
            d = np.minimum(d, seg_dist(P, a, b))
    wob = T.perlin(X / 4.0, Y / 4.0, 99) * 0.5
    return 1 - T.smoothstep(0.7, 1.5, d + wob)


# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------
def mat_terrain():
    m = bpy.data.materials.new('Terrain')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = node(nt, 'ShaderNodeOutputMaterial', (1600, 0))
    bs = node(nt, 'ShaderNodeBsdfPrincipled', (1300, 0))
    lnk(nt, bs.outputs[0], out.inputs[0])
    geo = node(nt, 'ShaderNodeNewGeometry', (-1200, 0))
    tc = node(nt, 'ShaderNodeTexCoord', (-1200, 300))
    sep = node(nt, 'ShaderNodeSeparateXYZ', (-1000, 200))
    lnk(nt, geo.outputs['Position'], sep.inputs[0])
    sepn = node(nt, 'ShaderNodeSeparateXYZ', (-1000, -100))
    lnk(nt, geo.outputs['Normal'], sepn.inputs[0])

    def noise_tex(scale, loc, detail=6, rough=0.55):
        n = node(nt, 'ShaderNodeTexNoise', loc)
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = detail
        n.inputs['Roughness'].default_value = rough
        lnk(nt, geo.outputs['Position'], n.inputs['Vector'])
        return n

    def ramp(loc, stops):
        r = node(nt, 'ShaderNodeValToRGB', loc)
        el = r.color_ramp.elements
        el[0].position, el[0].color = stops[0]
        el[1].position, el[1].color = stops[-1]
        for p, c in stops[1:-1]:
            e = el.new(p)
            e.color = c
        return r

    def mix(a, b, fac, loc, blend='MIX'):
        mx = node(nt, 'ShaderNodeMix', loc)
        mx.data_type = 'RGBA'
        mx.blend_type = blend
        lnk(nt, fac, mx.inputs['Factor'])
        lnk(nt, a, mx.inputs['A'])
        lnk(nt, b, mx.inputs['B'])
        return mx.outputs['Result']

    # grass colour: big patches + fine speckle
    n_big = noise_tex(0.035, (-800, 600), 4, 0.5)
    n_small = noise_tex(0.6, (-800, 400), 8, 0.6)
    grass_r = ramp((-550, 600), [(0.3, (0.035, 0.11, 0.012, 1)), (0.5, (0.08, 0.22, 0.02, 1)), (0.7, (0.17, 0.30, 0.03, 1))])
    lnk(nt, n_big.outputs['Fac'], grass_r.inputs[0])
    speck = ramp((-550, 400), [(0.35, (0.75, 0.75, 0.75, 1)), (0.65, (1.15, 1.1, 1.0, 1))])
    lnk(nt, n_small.outputs['Fac'], speck.inputs[0])
    grass = mix(grass_r.outputs[0], speck.outputs[0], n_small.outputs['Fac'], (-250, 550), 'MULTIPLY')
    # rock
    n_rock = noise_tex(0.12, (-800, 150), 12, 0.7)
    rock_r = ramp((-550, 150), [(0.3, (0.05, 0.05, 0.048, 1)), (0.5, (0.12, 0.115, 0.105, 1)), (0.62, (0.19, 0.18, 0.165, 1)), (0.8, (0.3, 0.29, 0.27, 1))])
    lnk(nt, n_rock.outputs['Fac'], rock_r.inputs[0])
    # sand / dirt
    n_sand = noise_tex(1.8, (-800, -2300), 6, 0.6)
    sand_r = ramp((-550, -2300), [(0.35, (0.36, 0.3, 0.2, 1)), (0.5, (0.47, 0.4, 0.27, 1)), (0.65, (0.55, 0.48, 0.34, 1))])
    lnk(nt, n_sand.outputs['Fac'], sand_r.inputs[0])
    wet = node(nt, 'ShaderNodeMapRange', (-550, -2500))
    lnk(nt, sep.outputs['Z'], wet.inputs['Value'])
    wet.inputs['From Min'].default_value = T.LAKE_LEVEL + 0.02
    wet.inputs['From Max'].default_value = T.LAKE_LEVEL + 0.22
    wet.inputs['To Min'].default_value = 0.55
    wet.inputs['To Max'].default_value = 1.0
    wetc = node(nt, 'ShaderNodeCombineColor', (-400, -2500))
    for i in range(3):
        lnk(nt, wet.outputs[0], wetc.inputs[i])
    sand = node(nt, 'ShaderNodeMix', (-300, -2300))
    sand.data_type = 'RGBA'
    sand.blend_type = 'MULTIPLY'
    sand.inputs['Factor'].default_value = 1.0
    lnk(nt, sand_r.outputs[0], sand.inputs['A'])
    lnk(nt, wetc.outputs[0], sand.inputs['B'])
    dirt = node(nt, 'ShaderNodeRGB', (-550, -250))
    dirt.outputs[0].default_value = (0.2, 0.12, 0.06, 1)
    snow = node(nt, 'ShaderNodeRGB', (-550, -400))
    snow.outputs[0].default_value = (0.85, 0.88, 0.95, 1)

    # masks
    # rock where steep: normal z < ~0.72 (noisy edge)
    nz = node(nt, 'ShaderNodeMath', (-800, -100), operation='SUBTRACT')
    lnk(nt, sepn.outputs['Z'], nz.inputs[0])
    lnk(nt, n_small.outputs['Fac'], nz.inputs[1])
    nz.inputs[1].default_value = 0
    rockm = node(nt, 'ShaderNodeMapRange', (-600, -600))
    lnk(nt, sepn.outputs['Z'], rockm.inputs['Value'])
    rockm.inputs['From Min'].default_value = 0.62
    rockm.inputs['From Max'].default_value = 0.48
    rockm.interpolation_type = 'SMOOTHSTEP'
    # sand near water level
    sandm = node(nt, 'ShaderNodeMapRange', (-600, -800))
    lnk(nt, sep.outputs['Z'], sandm.inputs['Value'])
    sandm.inputs['From Min'].default_value = T.LAKE_LEVEL + 0.55
    sandm.inputs['From Max'].default_value = T.LAKE_LEVEL + 0.2
    # snow high up
    snowm = node(nt, 'ShaderNodeMapRange', (-600, -1000))
    add = node(nt, 'ShaderNodeMath', (-800, -1000), operation='MULTIPLY_ADD')
    lnk(nt, n_rock.outputs['Fac'], add.inputs[0])
    add.inputs[1].default_value = 25
    lnk(nt, sep.outputs['Z'], add.inputs[2])
    lnk(nt, add.outputs[0], snowm.inputs['Value'])
    snowm.inputs['From Min'].default_value = 190
    snowm.inputs['From Max'].default_value = 205
    # path attribute
    pat = node(nt, 'ShaderNodeAttribute', (-600, -1200))
    pat.attribute_name = 'path'

    # horizontal strata + vertical streaks on cliffs
    mpz = node(nt, 'ShaderNodeMapping', (-1000, -1500))
    mpz.inputs['Scale'].default_value = (0.06, 0.06, 0.35)
    lnk(nt, geo.outputs['Position'], mpz.inputs['Vector'])
    strata = node(nt, 'ShaderNodeTexWave', (-800, -1500))
    strata.wave_type = 'BANDS'
    strata.bands_direction = 'Z'
    strata.inputs['Scale'].default_value = 1.2
    strata.inputs['Distortion'].default_value = 14
    strata.inputs['Detail'].default_value = 4
    lnk(nt, mpz.outputs[0], strata.inputs['Vector'])
    st_r = ramp((-550, -1500), [(0.0, (0.86, 0.86, 0.85, 1)), (0.5, (1.0, 1.0, 0.98, 1)), (1.0, (1.1, 1.08, 1.05, 1))])
    lnk(nt, strata.outputs['Fac'], st_r.inputs[0])
    mps = node(nt, 'ShaderNodeMapping', (-1000, -1750))
    mps.inputs['Scale'].default_value = (0.5, 0.5, 0.03)
    lnk(nt, geo.outputs['Position'], mps.inputs['Vector'])
    streak = node(nt, 'ShaderNodeTexNoise', (-800, -1750))
    streak.inputs['Scale'].default_value = 1.0
    streak.inputs['Detail'].default_value = 6
    lnk(nt, mps.outputs[0], streak.inputs['Vector'])
    sk_r = ramp((-550, -1750), [(0.35, (0.6, 0.62, 0.62, 1)), (0.65, (1.1, 1.05, 1.0, 1))])
    lnk(nt, streak.outputs['Fac'], sk_r.inputs[0])
    vor = node(nt, 'ShaderNodeTexVoronoi', (-800, -2000))
    vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 0.11
    lnk(nt, geo.outputs['Position'], vor.inputs['Vector'])
    crk = ramp((-550, -2000), [(0.0, (0.6, 0.6, 0.6, 1)), (0.04, (1.0, 1.0, 1.0, 1))])
    lnk(nt, vor.outputs['Distance'], crk.inputs[0])
    rock_c = mix(rock_r.outputs[0], st_r.outputs[0], rockm.outputs[0], (-300, -1500), 'MULTIPLY')
    rock_c = mix(rock_c, crk.outputs[0], rockm.outputs[0], (-200, -1700), 'MULTIPLY')
    rock_c = mix(rock_c, sk_r.outputs[0], rockm.outputs[0], (-150, -1600), 'MULTIPLY')
    # alpine grass: drier and more olive with altitude
    alp = node(nt, 'ShaderNodeMapRange', (-600, -1950))
    lnk(nt, sep.outputs['Z'], alp.inputs['Value'])
    alp.inputs['From Min'].default_value = 20
    alp.inputs['From Max'].default_value = 120
    alpc = node(nt, 'ShaderNodeRGB', (-550, -2100))
    alpc.outputs[0].default_value = (0.13, 0.15, 0.05, 1)
    grass = mix(grass, alpc.outputs[0], alp.outputs[0], (-150, 700))
    c = mix(grass, rock_c, rockm.outputs[0], (0, 300))
    c = mix(c, dirt.outputs[0], pat.outputs['Fac'], (150, 250))
    c = mix(c, sand.outputs['Result'], sandm.outputs[0], (300, 200))
    c = mix(c, snow.outputs[0], snowm.outputs[0], (450, 150))
    lnk(nt, c, bs.inputs['Base Color'])
    rgh = node(nt, 'ShaderNodeMapRange', (900, -200))
    lnk(nt, rockm.outputs[0], rgh.inputs['Value'])
    rgh.inputs['To Min'].default_value = 0.9
    rgh.inputs['To Max'].default_value = 0.75
    lnk(nt, rgh.outputs[0], bs.inputs['Roughness'])
    # bump
    bump = node(nt, 'ShaderNodeBump', (1000, -400))
    bump.inputs['Strength'].default_value = 0.35
    n_b = noise_tex(3.0, (800, -500), 8, 0.6)
    hb = node(nt, 'ShaderNodeMath', (900, -600), operation='MULTIPLY_ADD')
    lnk(nt, strata.outputs['Fac'], hb.inputs[0])
    lnk(nt, rockm.outputs[0], hb.inputs[1])
    lnk(nt, n_b.outputs['Fac'], hb.inputs[2])
    lnk(nt, hb.outputs[0], bump.inputs['Height'])
    bump.inputs['Distance'].default_value = 0.3
    lnk(nt, bump.outputs[0], bs.inputs['Normal'])
    bs.inputs['Specular IOR Level'].default_value = 0.25
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


def mat_leaves(name, c1, c2, scale=1.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes['Principled BSDF']
    geo = node(nt, 'ShaderNodeNewGeometry', (-1100, 200))
    oi = node(nt, 'ShaderNodeObjectInfo', (-1100, -200))
    vor = node(nt, 'ShaderNodeTexVoronoi', (-800, 200))
    vor.inputs['Scale'].default_value = scale * 3
    lnk(nt, geo.outputs['Position'], vor.inputs['Vector'])
    nz = node(nt, 'ShaderNodeTexNoise', (-800, 0))
    nz.inputs['Scale'].default_value = scale * 0.4
    lnk(nt, geo.outputs['Position'], nz.inputs['Vector'])
    r = node(nt, 'ShaderNodeValToRGB', (-500, 100))
    r.color_ramp.elements[0].color = (*c1, 1)
    r.color_ramp.elements[1].color = (*c2, 1)
    r.color_ramp.elements[0].position = 0.25
    r.color_ramp.elements[1].position = 0.75
    mm = node(nt, 'ShaderNodeMath', (-650, 100), operation='MULTIPLY_ADD')
    lnk(nt, nz.outputs['Fac'], mm.inputs[0])
    mm.inputs[1].default_value = 0.8
    rnd = node(nt, 'ShaderNodeMath', (-800, -200), operation='MULTIPLY')
    lnk(nt, oi.outputs['Random'], rnd.inputs[0])
    rnd.inputs[1].default_value = 0.35
    lnk(nt, rnd.outputs[0], mm.inputs[2])
    lnk(nt, mm.outputs[0], r.inputs[0])
    # AO-ish darkening in the crevices of the voronoi cells
    dark = node(nt, 'ShaderNodeMix', (-250, 100))
    dark.data_type = 'RGBA'
    dark.blend_type = 'MULTIPLY'
    cr = node(nt, 'ShaderNodeMapRange', (-500, 350))
    lnk(nt, vor.outputs['Distance'], cr.inputs['Value'])
    cr.inputs['From Min'].default_value = 0.0
    cr.inputs['From Max'].default_value = 0.8
    cr.inputs['To Min'].default_value = 0.0
    cr.inputs['To Max'].default_value = 1.0
    dark.inputs['Factor'].default_value = 0.45
    lnk(nt, r.outputs[0], dark.inputs['A'])
    inv = node(nt, 'ShaderNodeMath', (-350, 350), operation='SUBTRACT')
    inv.inputs[0].default_value = 1.0
    lnk(nt, cr.outputs[0], inv.inputs[1])
    cc = node(nt, 'ShaderNodeCombineColor', (-350, 250))
    for i in range(3):
        lnk(nt, inv.outputs[0], cc.inputs[i])
    lnk(nt, cc.outputs[0], dark.inputs['B'])
    lnk(nt, dark.outputs['Result'], bs.inputs['Base Color'])
    bump = node(nt, 'ShaderNodeBump', (-250, -250))
    bump.inputs['Strength'].default_value = 0.6
    lnk(nt, vor.outputs['Distance'], bump.inputs['Height'])
    lnk(nt, bump.outputs[0], bs.inputs['Normal'])
    bs.inputs['Roughness'].default_value = 0.65
    bs.inputs['Subsurface Weight'].default_value = 0.25
    bs.inputs['Subsurface Radius'].default_value = (0.3, 0.6, 0.1)
    bs.inputs['Subsurface Scale'].default_value = 0.2
    bs.inputs['Sheen Weight'].default_value = 0.3
    bs.inputs['Sheen Tint'].default_value = (0.8, 1.0, 0.6, 1)
    return m


def mat_bark(name='Bark', c=(0.16, 0.09, 0.05)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes['Principled BSDF']
    tc = node(nt, 'ShaderNodeTexCoord', (-1000, 0))
    mp = node(nt, 'ShaderNodeMapping', (-800, 0))
    mp.inputs['Scale'].default_value = (6, 6, 0.8)
    lnk(nt, tc.outputs['Object'], mp.inputs['Vector'])
    wv = node(nt, 'ShaderNodeTexWave', (-600, 0))
    wv.wave_type = 'BANDS'
    wv.bands_direction = 'X'
    wv.inputs['Scale'].default_value = 3
    wv.inputs['Distortion'].default_value = 12
    wv.inputs['Detail'].default_value = 6
    lnk(nt, mp.outputs[0], wv.inputs['Vector'])
    r = node(nt, 'ShaderNodeValToRGB', (-350, 0))
    r.color_ramp.elements[0].color = (c[0] * 0.4, c[1] * 0.4, c[2] * 0.4, 1)
    r.color_ramp.elements[1].color = (*c, 1)
    lnk(nt, wv.outputs['Fac'], r.inputs[0])
    lnk(nt, r.outputs[0], bs.inputs['Base Color'])
    bump = node(nt, 'ShaderNodeBump', (-300, -300))
    bump.inputs['Strength'].default_value = 0.8
    lnk(nt, wv.outputs['Fac'], bump.inputs['Height'])
    lnk(nt, bump.outputs[0], bs.inputs['Normal'])
    bs.inputs['Roughness'].default_value = 0.85
    return m


def mat_rock():
    m = bpy.data.materials.new('Rock')
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes['Principled BSDF']
    geo = node(nt, 'ShaderNodeNewGeometry', (-1000, 0))
    n = node(nt, 'ShaderNodeTexNoise', (-800, 0))
    n.inputs['Scale'].default_value = 1.5
    n.inputs['Detail'].default_value = 12
    n.inputs['Roughness'].default_value = 0.65
    lnk(nt, geo.outputs['Position'], n.inputs['Vector'])
    r = node(nt, 'ShaderNodeValToRGB', (-500, 0))
    r.color_ramp.elements[0].color = (0.07, 0.065, 0.06, 1)
    r.color_ramp.elements[1].color = (0.36, 0.34, 0.3, 1)
    lnk(nt, n.outputs['Fac'], r.inputs[0])
    sep = node(nt, 'ShaderNodeSeparateXYZ', (-800, -300))
    lnk(nt, geo.outputs['Normal'], sep.inputs[0])
    moss = node(nt, 'ShaderNodeMapRange', (-500, -300))
    lnk(nt, sep.outputs['Z'], moss.inputs['Value'])
    moss.inputs['From Min'].default_value = 0.6
    moss.inputs['From Max'].default_value = 0.9
    mx = node(nt, 'ShaderNodeMix', (-250, 0))
    mx.data_type = 'RGBA'
    mx.inputs['B'].default_value = (0.06, 0.16, 0.02, 1)
    lnk(nt, moss.outputs[0], mx.inputs['Factor'])
    lnk(nt, r.outputs[0], mx.inputs['A'])
    lnk(nt, mx.outputs['Result'], bs.inputs['Base Color'])
    bump = node(nt, 'ShaderNodeBump', (-250, -300))
    bump.inputs['Strength'].default_value = 0.7
    lnk(nt, n.outputs['Fac'], bump.inputs['Height'])
    lnk(nt, bump.outputs[0], bs.inputs['Normal'])
    bs.inputs['Roughness'].default_value = 0.8
    return m


def mat_water(name='Water', deep=(0.01, 0.08, 0.1), scale=0.6, strength=0.25):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes['Principled BSDF']
    geo = node(nt, 'ShaderNodeNewGeometry', (-1200, 0))
    # animated ripples: 4D noise, W driven by frame
    n1 = node(nt, 'ShaderNodeTexNoise', (-800, 0))
    n1.noise_dimensions = '4D'
    n1.inputs['Scale'].default_value = scale
    n1.inputs['Detail'].default_value = 6
    n1.inputs['Roughness'].default_value = 0.55
    lnk(nt, geo.outputs['Position'], n1.inputs['Vector'])
    d = n1.inputs['W'].driver_add('default_value').driver
    d.expression = 'frame/60'
    n2 = node(nt, 'ShaderNodeTexNoise', (-800, -300))
    n2.noise_dimensions = '4D'
    n2.inputs['Scale'].default_value = scale * 6
    n2.inputs['Detail'].default_value = 3
    lnk(nt, geo.outputs['Position'], n2.inputs['Vector'])
    d = n2.inputs['W'].driver_add('default_value').driver
    d.expression = 'frame/30'
    add = node(nt, 'ShaderNodeMath', (-550, -100), operation='MULTIPLY_ADD')
    lnk(nt, n2.outputs['Fac'], add.inputs[0])
    add.inputs[1].default_value = 0.35
    lnk(nt, n1.outputs['Fac'], add.inputs[2])
    bump = node(nt, 'ShaderNodeBump', (-300, -200))
    bump.inputs['Strength'].default_value = strength
    bump.inputs['Distance'].default_value = 0.2
    lnk(nt, add.outputs[0], bump.inputs['Height'])
    lnk(nt, bump.outputs[0], bs.inputs['Normal'])
    bs.inputs['Base Color'].default_value = (*deep, 1)
    bs.inputs['Roughness'].default_value = 0.03
    bs.inputs['Transmission Weight'].default_value = 0.85
    bs.inputs['IOR'].default_value = 1.33
    bs.inputs['Coat Weight'].default_value = 0.0
    m.surface_render_method = 'DITHERED'
    m.use_screen_refraction = True if hasattr(m, 'use_screen_refraction') else None
    try:
        m.use_raytrace_refraction = True
    except Exception:
        pass
    return m


# ---------------------------------------------------------------------------
# terrain
# ---------------------------------------------------------------------------
PATCHES = [
    # name, x0, x1, y0, y1, step
    ('core', -118.0, 108.0, -98.0, 128.0, 0.5),
    ('peak', 100.0, 156.0, 140.0, 190.0, 0.5),
]


def build_terrain(coll, mat):
    objs = []
    for name, x0, x1, y0, y1, st in PATCHES:
        nx = int(round((x1 - x0) / st)) + 1
        ny = int(round((y1 - y0) / st)) + 1
        me, X, Y, Z = grid_mesh('Terrain_' + name, x0, x1, y0, y1, nx, ny, T.height)
        pm = path_mask(X, Y)
        add_float_attr(me, 'path', pm)
        # grass density: meadow lush, fades farther away, none on paths/rock/sand/water
        nzv = T.normal_z(X, Y)
        dens = np.ones_like(X)
        rr = np.hypot(X - 2, Y - 5)
        dens *= 0.25 + 0.75 * (1 - T.smoothstep(55, 95, rr))
        dens *= T.smoothstep(0.8, 0.9, nzv) * T.smoothstep(0.85, 0.93, T.normal_z(X, Y, 1.5))
        dens *= T.smoothstep(T.LAKE_LEVEL + 0.5, T.LAKE_LEVEL + 0.9, Z)
        dens *= 1 - pm
        dens *= 1 - T.smoothstep(150, 185, Z)
        if name == 'peak':
            dens *= 0.35
        # keep the picnic blanket clear
        ca, sa = math.cos(-0.3), math.sin(-0.3)
        lx = (X - 5.0) * ca - (Y - 22.5) * sa
        ly = (X - 5.0) * sa + (Y - 22.5) * ca
        dbl = np.maximum(np.abs(lx) - 1.3, np.abs(ly) - 1.0)
        dens *= T.smoothstep(0.0, 0.2, dbl)
        add_float_attr(me, 'grass', dens)
        # mown meadow: shorter grass where the characters play
        gsc = 0.42 + 0.58 * T.smoothstep(30, 48, np.hypot(X - 4, Y - 12))
        gsc = np.minimum(gsc, 0.45 + 0.55 * T.smoothstep(8, 14, np.hypot(X + 27, Y + 12)))
        add_float_attr(me, 'gscale', gsc)
        # tall grass / flowers patches
        tall = T.smoothstep(0.15, 0.35, T.fbm(X / 18, Y / 18, 3, seed=42)) * dens
        tall *= T.smoothstep(12, 20, np.hypot(X - 2, Y + 5))   # keep the play area short
        add_float_attr(me, 'tall', tall)
        flw = T.smoothstep(0.0, 0.3, T.fbm(X / 10, Y / 10, 3, seed=77)) * dens
        add_float_attr(me, 'flowers', flw)
        ob = bpy.data.objects.new('Terrain_' + name, me)
        ob.data.materials.append(mat)
        link(ob, coll)
        objs.append(ob)

    # coarse outer terrain; sunk under the detailed patches to avoid z-fighting
    def outer_z(X, Y):
        Z = T.height(X, Y)
        for name, x0, x1, y0, y1, st in PATCHES:
            # distance inside the patch rectangle; sink deeper the further in
            din = np.minimum(np.minimum(X - x0, x1 - X), np.minimum(Y - y0, y1 - Y))
            Z = Z - 1.5 * T.smoothstep(0.0, 2.0, din) - 25.0 * T.smoothstep(4.0, 10.0, din)
        return Z
    me, X, Y, Z = grid_mesh('Terrain_outer', -480, 480, -480, 480, 481, 481, outer_z)
    OUTER[0] = (X[0, :].copy(), Y[:, 0].copy(), T.height(X, Y))
    add_float_attr(me, 'path', np.zeros_like(X))
    ob = bpy.data.objects.new('Terrain_outer', me)
    ob.data.materials.append(mat)
    link(ob, coll)
    objs.append(ob)
    return objs


OUTER = [None]


def surface_z(x, y):
    """height of the *rendered* surface (coarse outer mesh is linear between samples)"""
    for name, x0, x1, y0, y1, st in PATCHES:
        if x0 + 2 < x < x1 - 2 and y0 + 2 < y < y1 - 2:
            return float(T.height(x, y))
    xs, ys, Z = OUTER[0]
    st = xs[1] - xs[0]
    i = int(np.clip((x - xs[0]) // st, 0, len(xs) - 2))
    j = int(np.clip((y - ys[0]) // st, 0, len(ys) - 2))
    u = (x - xs[i]) / st
    v = (y - ys[j]) / st
    z = (Z[j, i] * (1 - u) * (1 - v) + Z[j, i + 1] * u * (1 - v) + Z[j + 1, i] * (1 - u) * v + Z[j + 1, i + 1] * u * v)
    # take the lowest corner-ish value so nothing floats over a triangle edge
    return float(min(z, Z[j:j + 2, i:i + 2].mean()))


# ---------------------------------------------------------------------------
# vegetation assets
# ---------------------------------------------------------------------------
def curve_tube(name, pts, radii, bevel_res=3, res=4):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 1.0
    cu.bevel_resolution = bevel_res
    cu.resolution_u = res
    cu.use_fill_caps = True
    sp = cu.splines.new('NURBS')
    sp.points.add(len(pts) - 1)
    for p, (x, y, z), r in zip(sp.points, pts, radii):
        p.co = (x, y, z, 1)
        p.radius = r
    sp.use_endpoint_u = True
    sp.order_u = min(4, len(pts))
    return cu


def blob(name, center, radius, seed, squash=0.8, subdiv=3, amp=0.28):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius)
    off = Vector((seed * 13.1, seed * 7.7, seed * 3.3))
    for v in bm.verts:
        n = v.co.normalized()
        d = noise.fractal(n * 1.6 + off, 0.5, 2.0, 4)
        v.co = v.co * (1 + amp * d)
        v.co.z *= squash
        v.co += Vector(center)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    return me


def join_meshes(name, parts):
    """parts: list of (mesh, material)"""
    bm = bmesh.new()
    mats = []
    for me, mat in parts:
        if mat not in mats:
            mats.append(mat)
        mi = mats.index(mat)
        tmp = bmesh.new()
        tmp.from_mesh(me)
        for f in tmp.faces:
            f.material_index = mi
        me2 = bpy.data.meshes.new('tmp')
        tmp.to_mesh(me2)
        tmp.free()
        bm.from_mesh(me2)
        bpy.data.meshes.remove(me2)
    out = bpy.data.meshes.new(name)
    bm.to_mesh(out)
    bm.free()
    for m in mats:
        out.materials.append(m)
    out.shade_smooth()
    return out


def curve_to_mesh(cu):
    ob = bpy.data.objects.new('tmpcurve', cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    return me


def make_broadleaf(i, bark, leaves, H):
    r = random.Random(100 + i)
    parts = []
    lean = Vector((r.uniform(-0.3, 0.3), r.uniform(-0.3, 0.3), 0))
    trunk_top = Vector((0, 0, H * 0.55)) + lean * H * 0.15
    pts = [(0, 0, -0.3), (0, 0, H * 0.2), tuple(lean * H * 0.08 + Vector((0, 0, H * 0.38))), tuple(trunk_top)]
    rad = H * 0.045
    parts.append((curve_to_mesh(curve_tube('trunk', pts, [rad * 1.5, rad, rad * 0.8, rad * 0.6])), bark))
    tips = []
    nb = r.randint(3, 5)
    for b in range(nb):
        a = b / nb * 2 * math.pi + r.uniform(-0.3, 0.3)
        el = r.uniform(0.35, 0.8)
        L = H * r.uniform(0.25, 0.38)
        s = trunk_top + Vector((0, 0, -H * r.uniform(0.0, 0.15)))
        d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el)))
        e = s + d * L
        m = s + d * L * 0.5 + Vector((0, 0, L * 0.12))
        parts.append((curve_to_mesh(curve_tube('br', [tuple(s), tuple(m), tuple(e)], [rad * 0.5, rad * 0.35, rad * 0.15])), bark))
        tips.append(e)
    tips.append(trunk_top + Vector((0, 0, H * 0.2)))
    for k, t in enumerate(tips):
        for j in range(r.randint(2, 3)):
            c = t + Vector((r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-0.3, 0.6))) * H * 0.08
            parts.append((blob('lf', c, H * r.uniform(0.16, 0.24), i * 31 + k * 7 + j), leaves))
    me = join_meshes(f'Broadleaf_{i}', parts)
    for p, _ in parts:
        bpy.data.meshes.remove(p)
    return me


def make_pine(i, bark, needles, H):
    r = random.Random(300 + i)
    parts = []
    rad = H * 0.03
    parts.append((curve_to_mesh(curve_tube('trunk', [(0, 0, -0.3), (0, 0, H * 0.5), (0, 0, H * 0.95)], [rad * 1.4, rad, rad * 0.3])), bark))
    n = r.randint(4, 6)
    for k in range(n):
        u = k / (n - 1)
        z0 = H * (0.18 + 0.72 * u)
        R = H * (0.3 * (1 - u) + 0.07)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=14, radius1=R, radius2=R * 0.05, depth=H * 0.32)
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
        off = Vector((i * 3.1, k * 5.3, 0))
        for v in bm.verts:
            d = noise.fractal(v.co * (3.0 / H) + off, 0.5, 2.0, 3)
            rr = Vector((v.co.x, v.co.y, 0))
            v.co += rr * 0.25 * d
            v.co.z += z0
            if v.co.z < z0 - H * 0.12:
                v.co.x *= 1.08
                v.co.y *= 1.08
        me = bpy.data.meshes.new('cone')
        bm.to_mesh(me)
        bm.free()
        parts.append((me, needles))
    me = join_meshes(f'Pine_{i}', parts)
    for p, _ in parts:
        bpy.data.meshes.remove(p)
    return me


def make_bush(i, leaves, S):
    r = random.Random(500 + i)
    parts = []
    for j in range(r.randint(3, 5)):
        c = Vector((r.uniform(-1, 1), r.uniform(-1, 1), 0.3)) * S * 0.5
        parts.append((blob('b', c, S * r.uniform(0.35, 0.55), i * 17 + j, 0.75), leaves))
    me = join_meshes(f'Bush_{i}', parts)
    for p, _ in parts:
        bpy.data.meshes.remove(p)
    return me


def make_rock(i, mat, S):
    r = random.Random(700 + i)
    me = blob(f'Rock_{i}', (0, 0, S * 0.2), S, 50 + i, squash=r.uniform(0.5, 0.8), subdiv=3, amp=0.45)
    me.materials.append(mat)
    return me


def grass_clump(i, mat, h, n, spread, width):
    r = random.Random(900 + i)
    verts, faces, tips = [], [], []
    for b in range(n):
        x, y = r.uniform(-spread, spread), r.uniform(-spread, spread)
        a = r.uniform(0, 2 * math.pi)
        hh = h * r.uniform(0.6, 1.2)
        bend = r.uniform(0.1, 0.45) * hh
        dx, dy = math.cos(a), math.sin(a)
        px, py = -dy, dx
        w = width * r.uniform(0.7, 1.2)
        segs = 3
        base = len(verts)
        for s in range(segs + 1):
            u = s / segs
            ww = w * (1 - u) * 0.5
            off = bend * u * u
            cx, cy, cz = x + dx * off, y + dy * off, hh * u
            if s < segs:
                verts += [(cx - px * ww, cy - py * ww, cz), (cx + px * ww, cy + py * ww, cz)]
                tips += [u, u]
            else:
                verts.append((cx, cy, cz))
                tips.append(1.0)
        for s in range(segs - 1):
            k = base + s * 2
            faces.append((k, k + 1, k + 3, k + 2))
        k = base + (segs - 1) * 2
        faces.append((k, k + 1, k + 2))
    me = bpy.data.meshes.new(f'Grass_{i}')
    me.from_pydata(verts, [], faces)
    add_float_attr(me, 'tip', tips)
    me.materials.append(mat)
    me.shade_smooth()
    return me


def mat_grass(name, base, tip):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes['Principled BSDF']
    at = node(nt, 'ShaderNodeAttribute', (-900, 0))
    at.attribute_name = 'tip'
    geo = node(nt, 'ShaderNodeNewGeometry', (-1100, -300))
    nz = node(nt, 'ShaderNodeTexNoise', (-900, -300))
    nz.inputs['Scale'].default_value = 0.035
    lnk(nt, geo.outputs['Position'], nz.inputs['Vector'])
    r = node(nt, 'ShaderNodeValToRGB', (-600, 0))
    r.color_ramp.elements[0].color = (*base, 1)
    r.color_ramp.elements[1].color = (*tip, 1)
    lnk(nt, at.outputs['Fac'], r.inputs[0])
    # large scale hue variation matching the terrain patches
    var = node(nt, 'ShaderNodeValToRGB', (-600, -300))
    var.color_ramp.elements[0].color = (0.55, 0.65, 0.5, 1)
    var.color_ramp.elements[1].color = (1.3, 1.15, 0.8, 1)
    var.color_ramp.elements[0].position = 0.3
    var.color_ramp.elements[1].position = 0.7
    lnk(nt, nz.outputs['Fac'], var.inputs[0])
    mx = node(nt, 'ShaderNodeMix', (-300, 0))
    mx.data_type = 'RGBA'
    mx.blend_type = 'MULTIPLY'
    mx.inputs['Factor'].default_value = 1.0
    lnk(nt, r.outputs[0], mx.inputs['A'])
    lnk(nt, var.outputs[0], mx.inputs['B'])
    lnk(nt, mx.outputs['Result'], bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value = 0.55
    bs.inputs['Subsurface Weight'].default_value = 0.3
    bs.inputs['Subsurface Radius'].default_value = (0.2, 0.5, 0.1)
    bs.inputs['Subsurface Scale'].default_value = 0.05
    bs.inputs['Specular IOR Level'].default_value = 0.35
    m.use_backface_culling = False
    return m


def make_flower(i, stem_mat, petal_col):
    r = random.Random(1100 + i)
    parts = []
    h = r.uniform(0.07, 0.16)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=5, radius1=0.004, radius2=0.003, depth=h)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, h / 2))
    me = bpy.data.meshes.new('stem')
    bm.to_mesh(me)
    bm.free()
    parts.append((me, stem_mat))
    pm = mat_simple(f'Petal_{i}', petal_col, 0.5, **{'Subsurface Weight': 0.3, 'Sheen Weight': 0.5})
    cm = mat_simple(f'FlowerCenter_{i}', (0.9, 0.6, 0.05), 0.6)
    npet = r.choice([5, 6, 8])
    for k in range(npet):
        a = k / npet * 2 * math.pi
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.012)
        for v in bm.verts:
            v.co.x *= 1.6
            v.co.z *= 0.25
            v.co.x += 0.016
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, 'Z') @ Matrix.Rotation(-0.25, 3, 'Y'))
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, h))
        me = bpy.data.meshes.new('pet')
        bm.to_mesh(me)
        bm.free()
        parts.append((me, pm))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.009)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, h + 0.003))
    me = bpy.data.meshes.new('ctr')
    bm.to_mesh(me)
    bm.free()
    parts.append((me, cm))
    out = join_meshes(f'Flower_{i}', parts)
    for p, _ in parts:
        bpy.data.meshes.remove(p)
    return out


# ---------------------------------------------------------------------------
# geometry-nodes scatter (grass / flowers) with wind
# ---------------------------------------------------------------------------
def scatter_tree(name, attr, coll, density, scale_min, scale_max, wind=0.25, seed=0, max_dist=None, far=0.1):
    ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nt = ng
    gi = node(nt, 'NodeGroupInput', (-1200, 0))
    go = node(nt, 'NodeGroupOutput', (900, 0))
    na = node(nt, 'GeometryNodeInputNamedAttribute', (-1200, -200))
    na.data_type = 'FLOAT'
    na.inputs['Name'].default_value = attr
    dist = node(nt, 'GeometryNodeDistributePointsOnFaces', (-900, 0))
    dist.distribute_method = 'RANDOM'
    dist.inputs['Density'].default_value = density
    dist.inputs['Seed'].default_value = seed
    mul = node(nt, 'ShaderNodeMath', (-1050, -200), operation='MULTIPLY')
    lnk(nt, na.outputs['Attribute'], mul.inputs[0])
    mul.inputs[1].default_value = density
    # density falls off away from the GrassFocus empty (moved per shot)
    foc = bpy.data.objects.get('GrassFocus')
    if foc is None:
        foc = bpy.data.objects.new('GrassFocus', None)
        bpy.context.scene.collection.objects.link(foc)
    oi = node(nt, 'GeometryNodeObjectInfo', (-1500, -500))
    oi.inputs['Object'].default_value = foc
    pos0 = node(nt, 'GeometryNodeInputPosition', (-1500, -700))
    dd = node(nt, 'ShaderNodeVectorMath', (-1350, -600), operation='DISTANCE')
    lnk(nt, pos0.outputs[0], dd.inputs[0])
    lnk(nt, oi.outputs['Location'], dd.inputs[1])
    fall = node(nt, 'ShaderNodeMapRange', (-1200, -600))
    fall.interpolation_type = 'SMOOTHSTEP'
    lnk(nt, dd.outputs['Value'], fall.inputs['Value'])
    fall.inputs['From Min'].default_value = 30.0
    fall.inputs['From Max'].default_value = 75.0
    fall.inputs['To Min'].default_value = 1.0
    fall.inputs['To Max'].default_value = far
    m2 = node(nt, 'ShaderNodeMath', (-1050, -350), operation='MULTIPLY')
    lnk(nt, mul.outputs[0], m2.inputs[0])
    lnk(nt, fall.outputs[0], m2.inputs[1])
    mul = m2
    nrm = node(nt, 'GeometryNodeInputNormal', (-1500, -900))
    sepn = node(nt, 'ShaderNodeSeparateXYZ', (-1350, -900))
    lnk(nt, nrm.outputs[0], sepn.inputs[0])
    slope = node(nt, 'ShaderNodeMapRange', (-1200, -900))
    slope.interpolation_type = 'SMOOTHSTEP'
    lnk(nt, sepn.outputs['Z'], slope.inputs['Value'])
    slope.inputs['From Min'].default_value = 0.82
    slope.inputs['From Max'].default_value = 0.93
    m3 = node(nt, 'ShaderNodeMath', (-1000, -450), operation='MULTIPLY')
    lnk(nt, mul.outputs[0], m3.inputs[0])
    lnk(nt, slope.outputs[0], m3.inputs[1])
    mul = m3
    lnk(nt, gi.outputs[0], dist.inputs['Mesh'])
    lnk(nt, mul.outputs[0], dist.inputs['Density'])
    ci = node(nt, 'GeometryNodeCollectionInfo', (-900, -400))
    ci.inputs['Collection'].default_value = coll
    ci.inputs['Separate Children'].default_value = True
    ci.inputs['Reset Children'].default_value = True
    ci.transform_space = 'ORIGINAL'
    inst = node(nt, 'GeometryNodeInstanceOnPoints', (-400, 0))
    lnk(nt, dist.outputs['Points'], inst.inputs['Points'])
    lnk(nt, ci.outputs[0], inst.inputs['Instance'])
    inst.inputs['Pick Instance'].default_value = True
    rid = node(nt, 'FunctionNodeRandomValue', (-650, -300))
    rid.data_type = 'INT'
    rid.inputs['Min'].default_value = 0
    rid.inputs['Max'].default_value = 100
    rid.inputs['Seed'].default_value = seed + 1
    lnk(nt, rid.outputs[2], inst.inputs['Instance Index'])
    rrot = node(nt, 'FunctionNodeRandomValue', (-650, -500))
    rrot.data_type = 'FLOAT_VECTOR'
    rrot.inputs['Min'].default_value = (-0.12, -0.12, 0)
    rrot.inputs['Max'].default_value = (0.12, 0.12, 6.283)
    rrot.inputs['Seed'].default_value = seed + 2
    lnk(nt, rrot.outputs[0], inst.inputs['Rotation'])
    rs = node(nt, 'FunctionNodeRandomValue', (-650, -700))
    rs.data_type = 'FLOAT'
    rs.inputs[2].default_value = scale_min
    rs.inputs[3].default_value = scale_max
    rs.inputs['Seed'].default_value = seed + 3
    gsa = node(nt, 'GeometryNodeInputNamedAttribute', (-650, -900))
    gsa.data_type = 'FLOAT'
    gsa.inputs['Name'].default_value = 'gscale'
    rsm = node(nt, 'ShaderNodeMath', (-450, -800), operation='MULTIPLY')
    lnk(nt, rs.outputs[1], rsm.inputs[0])
    lnk(nt, gsa.outputs['Attribute'], rsm.inputs[1])
    lnk(nt, rsm.outputs[0], inst.inputs['Scale'])
    last = inst.outputs[0]
    if wind > 0:
        # wind: rotate instances by a moving noise field
        pos = node(nt, 'GeometryNodeInputPosition', (-400, -400))
        st = node(nt, 'GeometryNodeInputSceneTime', (-400, -600))
        vm = node(nt, 'ShaderNodeVectorMath', (-200, -400), operation='ADD')
        cx = node(nt, 'ShaderNodeCombineXYZ', (-250, -600))
        tm = node(nt, 'ShaderNodeMath', (-300, -700), operation='MULTIPLY')
        lnk(nt, st.outputs['Seconds'], tm.inputs[0])
        tm.inputs[1].default_value = 1.6
        lnk(nt, tm.outputs[0], cx.inputs['X'])
        lnk(nt, tm.outputs[0], cx.inputs['Y'])
        lnk(nt, pos.outputs[0], vm.inputs[0])
        lnk(nt, cx.outputs[0], vm.inputs[1])
        nz = node(nt, 'ShaderNodeTexNoise', (0, -400))
        nz.inputs['Scale'].default_value = 0.25
        nz.inputs['Detail'].default_value = 2
        lnk(nt, vm.outputs[0], nz.inputs['Vector'])
        sub = node(nt, 'ShaderNodeVectorMath', (200, -400), operation='SUBTRACT')
        lnk(nt, nz.outputs['Color'], sub.inputs[0])
        sub.inputs[1].default_value = (0.5, 0.5, 0.5)
        sc = node(nt, 'ShaderNodeVectorMath', (350, -400), operation='SCALE')
        lnk(nt, sub.outputs[0], sc.inputs[0])
        sc.inputs['Scale'].default_value = wind
        mk = node(nt, 'ShaderNodeVectorMath', (500, -400), operation='MULTIPLY')
        lnk(nt, sc.outputs[0], mk.inputs[0])
        mk.inputs[1].default_value = (1, 1, 0)
        rot = node(nt, 'GeometryNodeRotateInstances', (500, 0))
        lnk(nt, last, rot.inputs['Instances'])
        lnk(nt, mk.outputs[0], rot.inputs['Rotation'])
        rot.inputs['Local Space'].default_value = True
        last = rot.outputs[0]
    if max_dist:
        pass
    j = node(nt, 'GeometryNodeJoinGeometry', (700, 0))
    lnk(nt, last, j.inputs[0])
    lnk(nt, gi.outputs[0], j.inputs[0])
    lnk(nt, j.outputs[0], go.inputs[0])
    return ng


# ---------------------------------------------------------------------------
# the giant festival tree
# ---------------------------------------------------------------------------
def build_giant_tree(coll, bark, leaves):
    r = random.Random(4242)
    base = Vector((T.TREE_C[0], T.TREE_C[1], float(T.height(*T.TREE_C)) - 0.3))
    parts = []
    H = 13.0
    trunk_pts = [(0, 0, -1), (0.2, 0.1, 2.5), (-0.3, 0.2, 5.5), (0.1, -0.2, 8.0), (0.0, 0.0, 9.5)]
    parts.append((curve_to_mesh(curve_tube('gtrunk', trunk_pts, [2.4, 1.9, 1.55, 1.3, 1.0], 6, 8)), bark))
    # twisting secondary trunk strands for character
    for k in range(5):
        a = k / 5 * 2 * math.pi
        pts = []
        for s in range(6):
            u = s / 5
            ang = a + u * 1.4
            rr = 1.7 - 0.6 * u
            pts.append((math.cos(ang) * rr, math.sin(ang) * rr, -0.8 + u * 9.0))
        parts.append((curve_to_mesh(curve_tube('strand', pts, [0.9, 0.7, 0.6, 0.5, 0.4, 0.3], 4, 6)), bark))
    # roots
    for k in range(9):
        a = k / 9 * 2 * math.pi + r.uniform(-0.2, 0.2)
        L = r.uniform(4.5, 7.5)
        d = Vector((math.cos(a), math.sin(a), 0))
        pts = [tuple(d * 1.2 + Vector((0, 0, 1.6))), tuple(d * 2.6 + Vector((0, 0, 0.6))),
               tuple(d * (L * 0.7) + Vector((0, 0, 0.05))), tuple(d * L + Vector((0, 0, -0.5)))]
        parts.append((curve_to_mesh(curve_tube('root', pts, [0.9, 0.7, 0.35, 0.1], 4, 6)), bark))
    # main branches + lantern slots
    slots = []
    tips = []
    nb = 7
    for k in range(nb):
        a = k / nb * 2 * math.pi + r.uniform(-0.25, 0.25)
        z0 = r.uniform(6.5, 8.8)
        L = r.uniform(7.5, 10.0)
        d = Vector((math.cos(a), math.sin(a), 0))
        s = Vector((0, 0, z0))
        m1 = s + d * L * 0.35 + Vector((0, 0, 1.4))
        m2 = s + d * L * 0.7 + Vector((0, 0, 1.6))
        e = s + d * L + Vector((0, 0, 2.6))
        parts.append((curve_to_mesh(curve_tube('gbr', [tuple(s), tuple(m1), tuple(m2), tuple(e)], [0.75, 0.5, 0.32, 0.15], 4, 6)), bark))
        tips += [e, m2 + Vector((0, 0, 1.0))]
        # sub-branch
        sd = Vector((math.cos(a + 0.7), math.sin(a + 0.7), 0.3)).normalized()
        ss = m1
        se = ss + sd * L * 0.4 + Vector((0, 0, 1.2))
        parts.append((curve_to_mesh(curve_tube('gsb', [tuple(ss), tuple((ss + se) / 2 + Vector((0, 0, 0.3))), tuple(se)], [0.3, 0.2, 0.08], 3, 5)), bark))
        tips.append(se)
        # lantern slots hang under the branch
        for u in (0.3, 0.5, 0.72, 0.9):
            p = s.lerp(e, u) + Vector((0, 0, 1.2 * math.sin(u * math.pi)))
            slots.append(p)
        slots.append((ss + se) / 2)
    tips.append(Vector((0, 0, 11)))
    for k, t in enumerate(tips):
        for j in range(r.randint(2, 3)):
            c = t + Vector((r.uniform(-1.5, 1.5), r.uniform(-1.5, 1.5), r.uniform(0.3, 2.0)))
            parts.append((blob('gl', c, r.uniform(2.3, 3.4), 9000 + k * 7 + j, 0.7, 3, 0.3), leaves))
    for j in range(8):
        a = j / 8 * 2 * math.pi
        c = Vector((math.cos(a) * 4, math.sin(a) * 4, 12.0 + r.uniform(-0.5, 0.8)))
        parts.append((blob('gl', c, 3.4, 9500 + j, 0.7, 3, 0.3), leaves))
    me = join_meshes('GiantTree', parts)
    for p, _ in parts:
        bpy.data.meshes.remove(p)
    ob = bpy.data.objects.new('GiantTree', me)
    ob.location = base
    link(ob, coll)
    # store lantern slots (world space) as empties
    sc = new_coll('LanternSlots', coll)
    for i, p in enumerate(slots):
        e = bpy.data.objects.new(f'LanternSlot.{i:03d}', None)
        e.location = base + p + Vector((0, 0, -0.3))
        e.empty_display_size = 0.2
        sc.objects.link(e)
    import festival
    festival.build(coll, slots_w := [base + p + Vector((0, 0, -0.3)) for p in slots], base)
    return ob


# ---------------------------------------------------------------------------
# water, waterfall, clouds
# ---------------------------------------------------------------------------
RIVER_LIP = [None]


def build_water(coll):
    wm = mat_water('LakeWater', (0.02, 0.12, 0.12), 0.5, 0.18)
    bpy.ops.mesh.primitive_circle_add(vertices=64, radius=45, fill_type='NGON', location=(T.LAKE_C[0], T.LAKE_C[1], T.LAKE_LEVEL))
    lake = bpy.context.active_object
    lake.name = 'Lake'
    lake.data.materials.append(wm)
    link(lake, coll)
    sm = mat_water('SeaWater', (0.01, 0.06, 0.12), 0.08, 0.4)
    bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, 0, T.SEA))
    sea = bpy.context.active_object
    sea.name = 'Sea'
    sea.data.materials.append(sm)
    link(sea, coll)
    # river on the plateau feeding the falls: follows the channel bed, always
    # flowing downhill, and stops exactly at the lip of the cliff
    xs = np.arange(-150.0, T.FALLS_C[0], 0.5)
    ycs = T.FALLS_C[1] + 1.5 * np.sin(xs / 9.0)
    hh = T.height(xs, ycs)
    zc = []
    for h in hh:
        z = h + 0.45 if not zc else min(zc[-1], h + 0.45)
        if zc and h < zc[-1] - 1.5:
            break
        zc.append(z)
    lip = len(zc) - 1
    zc = np.array(zc)
    xs, ycs = xs[:lip + 1], ycs[:lip + 1]
    RIVER_LIP[0] = (float(xs[-1]), float(ycs[-1]), float(zc[-1]))
    verts, faces = [], []
    for i, (x, yc, hz) in enumerate(zip(xs, ycs, zc)):
        verts += [(x, yc - 3.2, hz), (x, yc + 3.2, hz)]
        if i:
            k = 2 * i
            faces.append((k - 2, k - 1, k + 1, k))
    me = bpy.data.meshes.new('River')
    me.from_pydata(verts, [], faces)
    rv = bpy.data.objects.new('River', me)
    rv.data.materials.append(wm)
    link(rv, coll)
    return lake, sea


def mat_waterfall():
    m = bpy.data.materials.new('Waterfall')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = node(nt, 'ShaderNodeOutputMaterial', (900, 0))
    tc = node(nt, 'ShaderNodeTexCoord', (-1000, 0))
    sepuv = node(nt, 'ShaderNodeSeparateXYZ', (-800, 300))
    lnk(nt, tc.outputs['UV'], sepuv.inputs[0])
    mp = node(nt, 'ShaderNodeMapping', (-800, 0))
    mp.inputs['Scale'].default_value = (9.0, 0.5, 1.0)
    lnk(nt, tc.outputs['UV'], mp.inputs['Vector'])
    fc = mp.inputs['Location'].driver_add('default_value', 1).driver
    fc.expression = 'frame*0.06'
    nz = node(nt, 'ShaderNodeTexNoise', (-600, 0))
    nz.inputs['Scale'].default_value = 3.0
    nz.inputs['Detail'].default_value = 10
    nz.inputs['Roughness'].default_value = 0.65
    nz.inputs['Distortion'].default_value = 0.6
    lnk(nt, mp.outputs[0], nz.inputs['Vector'])
    mp2 = node(nt, 'ShaderNodeMapping', (-800, -250))
    mp2.inputs['Scale'].default_value = (25.0, 1.2, 1.0)
    lnk(nt, tc.outputs['UV'], mp2.inputs['Vector'])
    fc = mp2.inputs['Location'].driver_add('default_value', 1).driver
    fc.expression = 'frame*0.11'
    nz2 = node(nt, 'ShaderNodeTexNoise', (-600, -250))
    nz2.inputs['Scale'].default_value = 4.0
    nz2.inputs['Detail'].default_value = 4
    lnk(nt, mp2.outputs[0], nz2.inputs['Vector'])
    comb = node(nt, 'ShaderNodeMath', (-450, -100), operation='MULTIPLY_ADD')
    lnk(nt, nz2.outputs['Fac'], comb.inputs[0])
    comb.inputs[1].default_value = 0.6
    lnk(nt, nz.outputs['Fac'], comb.inputs[2])
    # whiter toward the bottom (aeration)
    foam = node(nt, 'ShaderNodeMapRange', (-450, 300))
    lnk(nt, sepuv.outputs['Y'], foam.inputs['Value'])
    foam.inputs['From Min'].default_value = 0.35
    foam.inputs['From Max'].default_value = 0.0
    foam.inputs['To Min'].default_value = 0.0
    foam.inputs['To Max'].default_value = 0.45
    tot = node(nt, 'ShaderNodeMath', (-300, 0), operation='ADD')
    lnk(nt, comb.outputs[0], tot.inputs[0])
    lnk(nt, foam.outputs[0], tot.inputs[1])
    rp = node(nt, 'ShaderNodeValToRGB', (-150, 0))
    rp.color_ramp.elements[0].position = 0.55
    rp.color_ramp.elements[0].color = (0.03, 0.12, 0.13, 1)
    rp.color_ramp.elements[1].position = 1.05
    rp.color_ramp.elements[1].color = (0.95, 0.98, 1.0, 1)
    e = rp.color_ramp.elements.new(0.8)
    e.color = (0.45, 0.62, 0.66, 1)
    lnk(nt, tot.outputs[0], rp.inputs[0])
    bs = node(nt, 'ShaderNodeBsdfPrincipled', (200, 0))
    lnk(nt, rp.outputs[0], bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value = 0.08
    bs.inputs['Coat Weight'].default_value = 0.3
    bs.inputs['Subsurface Weight'].default_value = 0.4
    bs.inputs['Subsurface Radius'].default_value = (0.4, 0.7, 0.8)
    al = node(nt, 'ShaderNodeMapRange', (0, -300))
    lnk(nt, tot.outputs[0], al.inputs['Value'])
    al.inputs['From Min'].default_value = 0.35
    al.inputs['From Max'].default_value = 0.85
    al.inputs['To Min'].default_value = 0.25
    al.inputs['To Max'].default_value = 1.0
    # fade the side edges
    edge = node(nt, 'ShaderNodeMath', (-300, -450), operation='PINGPONG')
    lnk(nt, sepuv.outputs['X'], edge.inputs[0])
    edge.inputs[1].default_value = 0.5
    edm = node(nt, 'ShaderNodeMapRange', (-150, -450))
    lnk(nt, edge.outputs[0], edm.inputs['Value'])
    edm.inputs['From Min'].default_value = 0.0
    edm.inputs['From Max'].default_value = 0.12
    am = node(nt, 'ShaderNodeMath', (150, -350), operation='MULTIPLY')
    lnk(nt, al.outputs[0], am.inputs[0])
    lnk(nt, edm.outputs[0], am.inputs[1])
    lnk(nt, am.outputs[0], bs.inputs['Alpha'])
    lnk(nt, bs.outputs[0], out.inputs[0])
    # rippled displacement of the sheet
    m.surface_render_method = 'BLENDED'
    return m


def build_waterfall(coll):
    x_top, yc, ztop = RIVER_LIP[0]
    zbot = T.LAKE_LEVEL - 0.2
    W = 6.4
    verts, faces, uvs = [], [], []
    n = 30
    for i in range(n + 1):
        u = i / n
        # parabolic fall: shoots out a bit then drops
        x = x_top + 3.0 * math.sqrt(u) + 3.0 * u
        z = ztop + (zbot - ztop) * u ** 1.15
        w = W * (1 + 0.25 * u)
        verts += [(x, yc - w / 2, z), (x, yc + w / 2, z)]
        uvs += [(0, 1 - u), (1, 1 - u)]
        if i:
            k = 2 * i
            faces.append((k - 2, k - 1, k + 1, k))
    me = bpy.data.meshes.new('Waterfall')
    me.from_pydata(verts, [], faces)
    uvl = me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        for li in poly.loop_indices:
            uvl.data[li].uv = uvs[me.loops[li].vertex_index]
    ob = bpy.data.objects.new('Waterfall', me)
    ob.data.materials.append(mat_waterfall())
    mod = ob.modifiers.new('sub', 'SUBSURF')
    mod.levels = 1
    mod.render_levels = 2
    link(ob, coll)
    # second, slightly offset sheet for depth
    ob2 = ob.copy()
    ob2.location = (0.25, 0.3, 0)
    ob2.scale = (1.0, 0.9, 1.0)
    link(ob2, coll)
    # foam at the base
    foam_m = mat_simple('Foam', (0.95, 0.97, 1.0), 0.4, **{'Subsurface Weight': 0.5})
    for k in range(10):
        c = Vector((x_top + 3.5 + rng.uniform(-1.5, 2.5), yc + rng.uniform(-5, 5), T.LAKE_LEVEL))
        me = blob(f'Foam_{k}', (0, 0, 0), rng.uniform(0.8, 1.8), 600 + k, 0.35, 3, 0.4)
        me.materials.append(foam_m)
        fo = bpy.data.objects.new(f'Foam_{k}', me)
        fo.location = c
        link(fo, coll)
    return ob
    # mist volume (disabled)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_top + 5, yc, T.LAKE_LEVEL + 3))
    mist = bpy.context.active_object
    mist.name = 'FallsMist'
    mist.scale = (12, 16, 7)
    mm = bpy.data.materials.new('Mist')
    mm.use_nodes = True
    nt = mm.node_tree
    nt.nodes.clear()
    out = node(nt, 'ShaderNodeOutputMaterial', (600, 0))
    vol = node(nt, 'ShaderNodeVolumePrincipled', (300, 0))
    tc = node(nt, 'ShaderNodeTexCoord', (-600, 0))
    grad = node(nt, 'ShaderNodeTexGradient', (-300, 0))
    grad.gradient_type = 'SPHERICAL'
    mp = node(nt, 'ShaderNodeMapping', (-450, 0))
    lnk(nt, tc.outputs['Object'], mp.inputs['Vector'])
    mp.inputs['Scale'].default_value = (2, 2, 2)
    lnk(nt, mp.outputs[0], grad.inputs['Vector'])
    mul = node(nt, 'ShaderNodeMath', (0, 0), operation='MULTIPLY')
    lnk(nt, grad.outputs['Fac'], mul.inputs[0])
    mul.inputs[1].default_value = 0.35
    lnk(nt, mul.outputs[0], vol.inputs['Density'])
    vol.inputs['Color'].default_value = (0.9, 0.95, 1, 1)
    lnk(nt, vol.outputs[0], out.inputs['Volume'])
    mist.data.materials.append(mm)
    link(mist, coll)
    return ob


def build_clouds(coll):
    """high procedural cloud deck: noise-alpha plane, sun/sky tinted"""
    cm = bpy.data.materials.new('CloudDeck')
    cm.use_nodes = True
    nt = cm.node_tree
    nt.nodes.clear()
    out = node(nt, 'ShaderNodeOutputMaterial', (1000, 0))
    geo = node(nt, 'ShaderNodeNewGeometry', (-1200, 0))
    mp = node(nt, 'ShaderNodeMapping', (-1000, 0))
    mp.inputs['Scale'].default_value = (0.0016, 0.0028, 0.0016)
    lnk(nt, geo.outputs['Position'], mp.inputs['Vector'])
    fc = mp.inputs['Location'].driver_add('default_value', 0).driver
    fc.expression = 'frame*0.0004'
    n1 = node(nt, 'ShaderNodeTexNoise', (-800, 0))
    n1.inputs['Scale'].default_value = 2.2
    n1.inputs['Detail'].default_value = 12
    n1.inputs['Roughness'].default_value = 0.62
    n1.inputs['Distortion'].default_value = 0.35
    lnk(nt, mp.outputs[0], n1.inputs['Vector'])
    cov = node(nt, 'ShaderNodeMapRange', (-600, 0))
    cov.interpolation_type = 'SMOOTHSTEP'
    lnk(nt, n1.outputs['Fac'], cov.inputs['Value'])
    cov.inputs['From Min'].default_value = 0.47
    cov.inputs['From Max'].default_value = 0.62
    # fade toward the horizon so the plane edge never shows
    sep = node(nt, 'ShaderNodeSeparateXYZ', (-1000, -300))
    lnk(nt, geo.outputs['Position'], sep.inputs[0])
    ln = node(nt, 'ShaderNodeVectorMath', (-800, -300), operation='LENGTH')
    cxy = node(nt, 'ShaderNodeCombineXYZ', (-900, -300))
    lnk(nt, sep.outputs['X'], cxy.inputs['X'])
    lnk(nt, sep.outputs['Y'], cxy.inputs['Y'])
    lnk(nt, cxy.outputs[0], ln.inputs[0])
    fade = node(nt, 'ShaderNodeMapRange', (-600, -300))
    lnk(nt, ln.outputs['Value'], fade.inputs['Value'])
    fade.inputs['From Min'].default_value = 1500
    fade.inputs['From Max'].default_value = 3800
    fade.inputs['To Min'].default_value = 1.0
    fade.inputs['To Max'].default_value = 0.0
    a = node(nt, 'ShaderNodeMath', (-400, -100), operation='MULTIPLY')
    lnk(nt, cov.outputs[0], a.inputs[0])
    lnk(nt, fade.outputs[0], a.inputs[1])
    # shading: denser parts slightly darker underneath
    shade = node(nt, 'ShaderNodeMapRange', (-400, 200))
    lnk(nt, n1.outputs['Fac'], shade.inputs['Value'])
    shade.inputs['From Min'].default_value = 0.5
    shade.inputs['From Max'].default_value = 0.7
    shade.inputs['To Min'].default_value = 1.0
    shade.inputs['To Max'].default_value = 0.62
    col = node(nt, 'ShaderNodeMix', (-200, 200))
    col.data_type = 'RGBA'
    col.blend_type = 'MULTIPLY'
    col.inputs['Factor'].default_value = 1.0
    col.inputs['A'].default_value = (1, 1, 1, 1)
    cc = node(nt, 'ShaderNodeCombineColor', (-300, 350))
    for i in range(3):
        lnk(nt, shade.outputs[0], cc.inputs[i])
    lnk(nt, cc.outputs[0], col.inputs['B'])
    tint = node(nt, 'ShaderNodeRGB', (-200, 450))
    tint.name = 'CloudTint'
    tint.outputs[0].default_value = (1.0, 1.0, 1.0, 1)
    tm = node(nt, 'ShaderNodeMix', (0, 300))
    tm.data_type = 'RGBA'
    tm.blend_type = 'MULTIPLY'
    tm.inputs['Factor'].default_value = 1.0
    lnk(nt, col.outputs['Result'], tm.inputs['A'])
    lnk(nt, tint.outputs[0], tm.inputs['B'])
    em = node(nt, 'ShaderNodeEmission', (200, 300))
    em.name = 'CloudEmit'
    em.inputs['Strength'].default_value = 1.0
    lnk(nt, tm.outputs['Result'], em.inputs['Color'])
    tr = node(nt, 'ShaderNodeBsdfTransparent', (200, 0))
    mx = node(nt, 'ShaderNodeMixShader', (500, 0))
    lnk(nt, a.outputs[0], mx.inputs['Fac'])
    lnk(nt, tr.outputs[0], mx.inputs[1])
    lnk(nt, em.outputs[0], mx.inputs[2])
    lnk(nt, mx.outputs[0], out.inputs[0])
    cm.surface_render_method = 'BLENDED'
    bpy.ops.mesh.primitive_plane_add(size=8000, location=(0, 0, 520))
    ob = bpy.context.active_object
    ob.name = 'CloudDeck'
    ob.data.materials.append(cm)
    ob.visible_shadow = False
    ob.rotation_euler = (math.pi, 0, 0)   # face down
    link(ob, coll)


# ---------------------------------------------------------------------------
# placement
# ---------------------------------------------------------------------------
def scatter_objects(coll, protos, n, accept, scale_rng, name, seed):
    r = random.Random(seed)
    placed = 0
    tries = 0
    while placed < n and tries < n * 40:
        tries += 1
        x, y = r.uniform(-430, 430), r.uniform(-430, 430)
        ok = accept(x, y, r)
        if not ok:
            continue
        z = surface_z(x, y)
        p = r.choice(protos)
        e = bpy.data.objects.new(f'{name}.{placed:04d}', None)
        e.instance_type = 'COLLECTION'
        e.instance_collection = p
        e.location = (x, y, z - 0.15)
        s = r.uniform(*scale_rng)
        e.scale = (s, s, s * r.uniform(0.9, 1.15))
        e.rotation_euler = (r.uniform(-0.04, 0.04), r.uniform(-0.04, 0.04), r.uniform(0, 6.283))
        coll.objects.link(e)
        placed += 1
    return placed


def in_clear_zone(x, y):
    if math.hypot(x - T.PEAK_TOP[0], y - T.PEAK_TOP[1]) < 16:
        return True    # Charizard's ledge
    if math.hypot(x - 2, y - 2) < 46:
        return True    # meadow
    if math.hypot(x - T.TREE_C[0], y - T.TREE_C[1]) < 16:
        return True
    if math.hypot((x - T.LAKE_C[0]), (y - T.LAKE_C[1]) * 1.25) < T.LAKE_R + 6:
        return True
    if abs(x - (T.FALLS_C[0] + 3)) < 8 and abs(y - T.FALLS_C[1]) < 12:
        return True
    return False


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    W = new_coll('World')
    terr = new_coll('Terrain', W)
    water = new_coll('Water', W)
    veg = new_coll('Vegetation', W)
    assets = new_coll('Assets', W)
    assets.hide_render = False
    tm = mat_terrain()
    terrains = build_terrain(terr, tm)
    build_water(water)
    build_waterfall(water)
    clouds = new_coll('Clouds', W)
    build_clouds(clouds)

    bark = mat_bark()
    leaf_mats = [mat_leaves('Leaves_A', (0.03, 0.12, 0.015), (0.12, 0.3, 0.03)),
                 mat_leaves('Leaves_B', (0.06, 0.14, 0.01), (0.22, 0.34, 0.03)),
                 mat_leaves('Leaves_C', (0.02, 0.09, 0.02), (0.08, 0.22, 0.05))]
    needles = mat_leaves('Needles', (0.01, 0.05, 0.02), (0.04, 0.14, 0.05), 3)
    giant_leaves = mat_leaves('GiantLeaves', (0.04, 0.14, 0.02), (0.18, 0.36, 0.04), 0.8)
    rock_m = mat_rock()

    # prototype collections (excluded from view layer, used as instances)
    proto_root = new_coll('Protos', W)
    def proto(me, cname):
        c = bpy.data.collections.new(cname)
        proto_root.children.link(c)
        o = bpy.data.objects.new(cname, me)
        c.objects.link(o)
        return c
    broad = [proto(make_broadleaf(i, bark, leaf_mats[i % 3], rng.uniform(7, 11)), f'P_Broad{i}') for i in range(6)]
    import leaves
    LEAF_COLS = {'Leaves_A': ((0.03, 0.1, 0.012), (0.16, 0.34, 0.04), (0.012, 0.035, 0.006)),
                 'Leaves_B': ((0.06, 0.13, 0.01), (0.26, 0.38, 0.04), (0.02, 0.04, 0.005)),
                 'Leaves_C': ((0.02, 0.08, 0.02), (0.1, 0.26, 0.06), (0.01, 0.03, 0.01))}
    for i, c in enumerate(broad):
        lm = leaf_mats[i % 3]
        leaves.apply(c.objects[0], lm, *LEAF_COLS[lm.name], density=45, size=0.32, seed=i)
    pines = [proto(make_pine(i, bark, needles, rng.uniform(10, 16)), f'P_Pine{i}') for i in range(4)]
    bushes = [proto(make_bush(i, leaf_mats[i % 3], rng.uniform(1.0, 1.8)), f'P_Bush{i}') for i in range(4)]
    for i, c in enumerate(bushes):
        lm = leaf_mats[i % 3]
        leaves.apply(c.objects[0], lm, *LEAF_COLS[lm.name], density=70, size=0.18, seed=50 + i)
    rocks = [proto(make_rock(i, rock_m, rng.uniform(0.6, 1.4)), f'P_Rock{i}') for i in range(5)]

    def forest_ok(x, y, r, pine=False):
        rr = math.hypot(x, y)
        if rr > 400 or in_clear_zone(x, y):
            return False
        z = float(T.height(x, y))
        if z < T.LAKE_LEVEL + 0.8 or z > (200 if pine else 120):
            return False
        if T.normal_z(x, y, 1.0) < 0.78 or T.normal_z(x, y, 3.0) < 0.8:
            return False
        if z > 25 and T.normal_z(x, y, 7.0) < 0.84:
            return False
        dens = 0.5 + 0.5 * float(T.fbm(x / 70, y / 70, 3, seed=55))
        if pine:
            dens *= float(T.smoothstep(20, 70, z)) + 0.1
        else:
            dens *= 1 - float(T.smoothstep(60, 110, z))
        # meadow edges get a ring of trees for framing
        if 46 < math.hypot(x - 2, y - 2) < 75:
            dens += 0.3
        return r.random() < dens
    trees = new_coll('Trees', veg)
    scatter_objects(trees, broad, 1800, lambda x, y, r: forest_ok(x, y, r), (0.8, 1.4), 'Tree', 1)
    scatter_objects(trees, pines, 2600, lambda x, y, r: forest_ok(x, y, r, True), (0.8, 1.5), 'Pine', 2)

    def bush_ok(x, y, r):
        if math.hypot(x - T.PEAK_TOP[0], y - T.PEAK_TOP[1]) < 16:
            return False
        if math.hypot(x - 2, y - 2) < 30 or in_clear_zone(x, y) and math.hypot(x - 2, y - 2) < 40:
            return False
        z = float(T.height(x, y))
        if T.normal_z(x, y, 1.5) < 0.82:
            return False
        return T.LAKE_LEVEL + 0.6 < z < 90 and math.hypot(x, y) < 250
    scatter_objects(trees, bushes, 900, bush_ok, (0.7, 1.4), 'Bush', 3)

    def rock_ok(x, y, r):
        if math.hypot(x - 2, y - 2) < 25 or math.hypot(x - T.PEAK_TOP[0], y - T.PEAK_TOP[1]) < 12:
            return False
        if T.normal_z(x, y, 1.5) < 0.7:
            return False
        return math.hypot(x, y) < 300 and float(T.height(x, y)) > T.LAKE_LEVEL - 1
    scatter_objects(trees, rocks, 500, rock_ok, (0.4, 2.2), 'Rock', 4)
    # a few meadow boulders to sit on / hide behind
    for i, (x, y, s) in enumerate([(-14, 12, 1.1), (16, -6, 0.8), (-6, -22, 1.3), (20, 30, 1.6), (-30, 20, 1.4),
                                   (21.5, 21.0, 1.5), (23.0, 18.5, 0.9), (32.5, 26.5, 1.8), (30.5, 20.0, 1.2), (25.0, 29.5, 1.3)]):
        e = bpy.data.objects.new(f'Boulder.{i}', None)
        e.instance_type = 'COLLECTION'
        e.instance_collection = rocks[i % len(rocks)]
        e.location = (x, y, float(T.height(x, y)) - 0.2)
        e.scale = (s, s, s)
        e.rotation_euler = (0, 0, i * 1.3)
        trees.objects.link(e)

    # grass / flowers via geometry nodes on the detailed terrain
    gm = mat_grass('Grass', (0.02, 0.07, 0.01), (0.2, 0.42, 0.06))
    gm_tall = mat_grass('GrassTall', (0.02, 0.06, 0.01), (0.25, 0.4, 0.08))
    gcoll = bpy.data.collections.new('P_Grass')
    proto_root.children.link(gcoll)
    for i in range(6):
        o = bpy.data.objects.new(f'GrassClump{i}', grass_clump(i, gm, 0.16, 16, 0.08, 0.012))
        gcoll.objects.link(o)
    tcoll = bpy.data.collections.new('P_TallGrass')
    proto_root.children.link(tcoll)
    for i in range(4):
        o = bpy.data.objects.new(f'TallClump{i}', grass_clump(10 + i, gm_tall, 0.45, 18, 0.12, 0.02))
        tcoll.objects.link(o)
    fcoll = bpy.data.collections.new('P_Flowers')
    proto_root.children.link(fcoll)
    stem = mat_simple('Stem', (0.05, 0.15, 0.02), 0.6)
    cols = [(0.9, 0.9, 0.95), (0.95, 0.75, 0.1), (0.9, 0.3, 0.5), (0.55, 0.3, 0.85), (0.95, 0.45, 0.2), (0.4, 0.6, 1.0)]
    for i, c in enumerate(cols):
        o = bpy.data.objects.new(f'Flower{i}', make_flower(i, stem, c))
        fcoll.objects.link(o)

    g_ng = scatter_tree('GN_Grass', 'grass', gcoll, 38.0, 0.7, 1.4, 0.35, 11, far=0.06)
    t_ng = scatter_tree('GN_TallGrass', 'tall', tcoll, 3.5, 0.7, 1.3, 0.25, 21, far=0.2)
    f_ng = scatter_tree('GN_Flowers', 'flowers', fcoll, 2.2, 0.8, 1.3, 0.2, 31, far=0.1)
    for t in terrains:
        if t.name == 'Terrain_outer':
            continue
        for ng, nm in ((g_ng, 'Grass'), (t_ng, 'TallGrass'), (f_ng, 'Flowers')):
            md = t.modifiers.new(nm, 'NODES')
            md.node_group = ng

    gt = build_giant_tree(W, mat_bark('GiantBark', (0.2, 0.12, 0.07)), giant_leaves)
    leaves.apply(gt, giant_leaves, (0.05, 0.14, 0.02), (0.3, 0.45, 0.06), (0.015, 0.04, 0.008), density=55, size=0.34, seed=99)

    # exclude prototype collections from rendering directly
    vl = bpy.context.view_layer
    def find_lc(lc, name):
        if lc.collection.name == name:
            return lc
        for ch in lc.children:
            r = find_lc(ch, name)
            if r:
                return r
    find_lc(vl.layer_collection, 'Protos').exclude = True

    bpy.ops.wm.save_as_mainfile(filepath=ROOT + 'world.blend')
    print('WORLD SAVED')


if __name__ == '__main__':
    main()
