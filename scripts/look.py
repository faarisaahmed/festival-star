# Lighting / sky / render settings per time of day.
import bpy, math
from mathutils import Vector, Euler

PRESETS = {
    #            sun elev, sun azim, sun strength, sky strength, sun color, air, dust, ozone, exposure
    'dawn':      dict(elev=6, azim=100, sun=4.0, sky=1.5, color=(1.0, 0.72, 0.45), air=1.4, dust=2.5, ozone=1.0, exposure=0.8, haze=0.0005, haze_col=(0.55, 0.45, 0.4)),
    'morning':   dict(elev=24, azim=115, sun=7.5, sky=1.5, color=(1.0, 0.9, 0.78), air=1.0, dust=1.2, ozone=1.0, exposure=0.35, haze=0.0007, haze_col=(0.42, 0.5, 0.62)),
    'noon':      dict(elev=55, azim=160, sun=7.5, sky=1.5, color=(1.0, 0.97, 0.92), air=1.0, dust=1.0, ozone=1.0, exposure=0.1, haze=0.0009, haze_col=(0.45, 0.52, 0.65)),
    'afternoon': dict(elev=30, azim=230, sun=7.0, sky=1.4, color=(1.0, 0.88, 0.7), air=1.1, dust=1.6, ozone=1.0, exposure=0.3, haze=0.0011, haze_col=(0.5, 0.5, 0.52)),
    'golden':    dict(elev=10, azim=255, sun=5.5, sky=1.4, color=(1.0, 0.7, 0.42), air=1.3, dust=2.5, ozone=1.1, exposure=0.6, haze=0.0009, haze_col=(0.55, 0.42, 0.32)),
    'sunset':    dict(elev=3, azim=265, sun=4.0, sky=1.6, color=(1.0, 0.52, 0.26), air=1.6, dust=3.5, ozone=1.2, exposure=0.9, haze=0.0008, haze_col=(0.5, 0.33, 0.26)),
    'dusk':      dict(elev=-2, azim=270, sun=0.0, sky=2.2, color=(1.0, 0.5, 0.3), air=2.0, dust=3.0, ozone=1.5, exposure=1.6, haze=0.0012, haze_col=(0.12, 0.12, 0.2)),
    'night':     dict(night=True, exposure=0.5, haze=0.0015, haze_col=(0.015, 0.022, 0.05)),
}


def setup_render(sc, res=(1920, 1080), samples=24, fast=False):
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.fps = 24
    ee = sc.eevee
    ee.taa_render_samples = samples
    ee.use_shadows = True
    ee.shadow_ray_count = 1
    ee.shadow_step_count = 6
    ee.use_raytracing = not fast
    ee.ray_tracing_method = 'SCREEN'
    ee.ray_tracing_options.resolution_scale = '2'
    ee.ray_tracing_options.trace_max_roughness = 0.4
    ee.use_fast_gi = True
    ee.fast_gi_method = 'GLOBAL_ILLUMINATION'
    ee.fast_gi_resolution = '2'
    ee.volumetric_tile_size = '8'
    ee.volumetric_samples = 48
    ee.volumetric_end = 600
    ee.volumetric_start = 0.5
    ee.use_volumetric_shadows = True
    ee.clamp_surface_indirect = 10
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Punchy'
    sc.render.film_transparent = False
    sc.render.use_motion_blur = False
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 92


def compositor(sc, glare=0.5, vignette=0.0):
    sc.use_nodes = True
    nt = sc.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new('CompositorNodeRLayers')
    rl.location = (-600, 0)
    gl = nt.nodes.new('CompositorNodeGlare')
    gl.location = (-300, 0)
    gl.glare_type = 'BLOOM' if hasattr(bpy.types.CompositorNodeGlare, 'glare_type') else 'FOG_GLOW'
    try:
        gl.glare_type = 'BLOOM'
    except Exception:
        gl.glare_type = 'FOG_GLOW'
    gl.quality = 'MEDIUM'
    try:
        gl.threshold = 1.0
        gl.size = 7
        gl.mix = -1 + glare
    except Exception:
        pass
    for k, v in (('Threshold', 1.0), ('Strength', glare), ('Size', 0.6)):
        if k in gl.inputs:
            gl.inputs[k].default_value = v
    nt.links.new(rl.outputs['Image'], gl.inputs['Image'])
    last = gl.outputs['Image']
    # vignette: elliptical mask blurred, multiply
    if vignette > 0:
        em = nt.nodes.new('CompositorNodeEllipseMask')
        em.location = (-300, -300)
        em.width = 0.95
        em.height = 0.9
        bl = nt.nodes.new('CompositorNodeBlur')
        bl.location = (-100, -300)
        bl.filter_type = 'FAST_GAUSS'
        bl.use_relative = True
        bl.factor_x = 0.35
        bl.factor_y = 0.35
        nt.links.new(em.outputs[0], bl.inputs[0])
        mr = nt.nodes.new('CompositorNodeMapRange')
        mr.location = (100, -300)
        mr.inputs['To Min'].default_value = 1 - vignette
        nt.links.new(bl.outputs[0], mr.inputs[0])
        mx = nt.nodes.new('CompositorNodeMixRGB')
        mx.location = (300, 0)
        mx.blend_type = 'MULTIPLY'
        nt.links.new(last, mx.inputs[1])
        nt.links.new(mr.outputs[0], mx.inputs[2])
        last = mx.outputs[0]
    hs = nt.nodes.new('CompositorNodeHueSat')
    hs.location = (450, 0)
    hs.inputs['Saturation'].default_value = 1.12
    nt.links.new(last, hs.inputs['Image'])
    last = hs.outputs[0]
    out = nt.nodes.new('CompositorNodeComposite')
    out.location = (600, 0)
    nt.links.new(last, out.inputs[0])


def add_haze(nt, out, p):
    """aerial perspective is done in the compositor (see fog()); remember settings"""
    sc = bpy.context.scene
    sc['haze'] = p.get('haze', 0.0)
    sc['haze_col'] = list(p.get('haze_col', (0.8, 0.85, 1.0)))
    fog(sc)


def fog(sc):
    """depth fog: mix toward haze colour by 1-exp(-density*depth), sky untouched"""
    if not sc.use_nodes or sc.node_tree is None:
        return
    nt = sc.node_tree
    comp = next((n for n in nt.nodes if n.type == 'COMPOSITE'), None)
    rl = next((n for n in nt.nodes if n.type == 'R_LAYERS'), None)
    if comp is None or rl is None:
        return
    for n in list(nt.nodes):
        if n.name.startswith('FOG_'):
            nt.nodes.remove(n)
    d = sc.get('haze', 0.0)
    if d <= 0:
        return
    sc.view_layers[0].use_pass_z = True
    col = sc.get('haze_col', [0.8, 0.85, 1.0])
    first = rl.outputs['Image'].links[0].to_socket if rl.outputs['Image'].links else comp.inputs[0]

    def mk(t, name, **kw):
        n = nt.nodes.new(t)
        n.name = 'FOG_' + name
        for k, v in kw.items():
            setattr(n, k, v)
        return n
    m1 = mk('CompositorNodeMath', 'mul', operation='MULTIPLY')
    nt.links.new(rl.outputs['Depth'], m1.inputs[0])
    m1.inputs[1].default_value = -d
    ex = mk('CompositorNodeMath', 'exp', operation='EXPONENT')
    nt.links.new(m1.outputs[0], ex.inputs[0])
    inv = mk('CompositorNodeMath', 'inv', operation='SUBTRACT')
    inv.inputs[0].default_value = 1.0
    nt.links.new(ex.outputs[0], inv.inputs[1])
    sky = mk('CompositorNodeMath', 'sky', operation='LESS_THAN')
    nt.links.new(rl.outputs['Depth'], sky.inputs[0])
    sky.inputs[1].default_value = 20000.0
    amt = mk('CompositorNodeMath', 'amt', operation='MULTIPLY')
    nt.links.new(inv.outputs[0], amt.inputs[0])
    nt.links.new(sky.outputs[0], amt.inputs[1])
    amt2 = mk('CompositorNodeMath', 'amt2', operation='MULTIPLY', use_clamp=True)
    nt.links.new(amt.outputs[0], amt2.inputs[0])
    amt2.inputs[1].default_value = 0.85
    mix = mk('CompositorNodeMixRGB', 'mix')
    nt.links.new(amt2.outputs[0], mix.inputs[0])
    nt.links.new(rl.outputs['Image'], mix.inputs[1])
    mix.inputs[2].default_value = (*col, 1)
    # haze colour brightness follows the scene's exposure-neutral sky level
    nt.links.new(mix.outputs[0], first)


def sun_dir(elev, azim):
    e, a = math.radians(elev), math.radians(azim)
    # direction *towards* the sun
    return Vector((math.cos(e) * math.sin(a), math.cos(e) * math.cos(a), math.sin(e)))


CLOUD = {'dawn': ((1.0, 0.75, 0.6), 0.7), 'morning': ((1.0, 0.97, 0.93), 1.1), 'noon': ((1, 1, 1), 1.2),
         'afternoon': ((1.0, 0.95, 0.88), 1.1), 'golden': ((1.0, 0.8, 0.6), 0.9), 'sunset': ((1.0, 0.55, 0.42), 0.75),
         'dusk': ((0.45, 0.38, 0.55), 0.3), 'night': ((0.3, 0.35, 0.5), 0.05)}


def set_clouds(preset):
    m = bpy.data.materials.get('CloudDeck')
    if not m:
        return
    c, e = CLOUD.get(preset, ((1, 1, 1), 1.0))
    m.node_tree.nodes['CloudTint'].outputs[0].default_value = (*c, 1)
    m.node_tree.nodes['CloudEmit'].inputs['Strength'].default_value = e


def set_time(sc, preset, overrides=None):
    p = dict(PRESETS[preset])
    if overrides:
        p.update(overrides)
    set_clouds(preset)
    w = sc.world or bpy.data.worlds.new('World')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    out.location = (800, 0)
    sun = bpy.data.objects.get('Sun')
    if sun is None:
        sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN'))
        sc.collection.objects.link(sun)
    moon = bpy.data.objects.get('MoonLight')
    sc.view_settings.exposure = p.get('exposure', 0.0)
    if p.get('night'):
        # deep blue gradient sky + stars + moon glow
        tc = nt.nodes.new('ShaderNodeTexCoord')
        tc.location = (-1200, 0)
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        sep.location = (-1000, 200)
        nt.links.new(tc.outputs['Generated'], sep.inputs[0])
        rp = nt.nodes.new('ShaderNodeValToRGB')
        rp.location = (-800, 200)
        rp.color_ramp.elements[0].position = 0.45
        rp.color_ramp.elements[0].color = (0.03, 0.05, 0.12, 1)
        rp.color_ramp.elements[1].position = 0.75
        rp.color_ramp.elements[1].color = (0.004, 0.008, 0.03, 1)
        e = rp.color_ramp.elements.new(0.52)
        e.color = (0.05, 0.065, 0.15, 1)
        nt.links.new(sep.outputs['Z'], rp.inputs[0])
        vor = nt.nodes.new('ShaderNodeTexVoronoi')
        vor.location = (-1000, -200)
        vor.inputs['Scale'].default_value = 400
        vor.feature = 'F1'
        nt.links.new(tc.outputs['Generated'], vor.inputs['Vector'])
        st = nt.nodes.new('ShaderNodeMapRange')
        st.location = (-800, -200)
        st.inputs['From Min'].default_value = 0.06
        st.inputs['From Max'].default_value = 0.0
        st.inputs['To Max'].default_value = 1.0
        nt.links.new(vor.outputs['Distance'], st.inputs['Value'])
        pw = nt.nodes.new('ShaderNodeMath')
        pw.operation = 'MULTIPLY'
        pw.location = (-600, -200)
        nt.links.new(st.outputs[0], pw.inputs[0])
        nt.links.new(vor.outputs['Color'], pw.inputs[1]) if False else None
        pw.inputs[1].default_value = 6.0
        # stars only above horizon
        hz = nt.nodes.new('ShaderNodeMapRange')
        hz.location = (-600, 0)
        hz.inputs['From Min'].default_value = 0.5
        hz.inputs['From Max'].default_value = 0.6
        nt.links.new(sep.outputs['Z'], hz.inputs['Value'])
        m2 = nt.nodes.new('ShaderNodeMath')
        m2.operation = 'MULTIPLY'
        m2.location = (-400, -200)
        nt.links.new(pw.outputs[0], m2.inputs[0])
        nt.links.new(hz.outputs[0], m2.inputs[1])
        add = nt.nodes.new('ShaderNodeMix')
        add.data_type = 'RGBA'
        add.blend_type = 'ADD'
        add.location = (-200, 100)
        add.inputs['Factor'].default_value = 1.0
        nt.links.new(rp.outputs[0], add.inputs['A'])
        cc = nt.nodes.new('ShaderNodeCombineColor')
        cc.location = (-300, -200)
        for i in range(3):
            nt.links.new(m2.outputs[0], cc.inputs[i])
        nt.links.new(cc.outputs[0], add.inputs['B'])
        bg = nt.nodes.new('ShaderNodeBackground')
        bg.location = (400, 0)
        nt.links.new(add.outputs['Result'], bg.inputs['Color'])
        bg.inputs['Strength'].default_value = 1.0
        nt.links.new(bg.outputs[0], out.inputs[0])
        add_haze(nt, out, p)
        # moon light (cool, soft)
        sun.data.energy = 2.0
        sun.data.color = (0.55, 0.68, 1.0)
        sun.data.angle = math.radians(1.0)
        d = sun_dir(35, 200)
        sun.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
        sun.hide_render = False
        # a visible moon disc
        mo = bpy.data.objects.get('MoonDisc')
        if mo is None:
            me = bpy.data.meshes.new('MoonDisc')
            import bmesh
            bm = bmesh.new()
            bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=40)
            bm.to_mesh(me)
            bm.free()
            mo = bpy.data.objects.new('MoonDisc', me)
            sc.collection.objects.link(mo)
            mm = bpy.data.materials.new('Moon')
            mm.use_nodes = True
            mm.node_tree.nodes.clear()
            em = mm.node_tree.nodes.new('ShaderNodeEmission')
            em.inputs['Color'].default_value = (1.0, 0.95, 0.85, 1)
            em.inputs['Strength'].default_value = 12
            o = mm.node_tree.nodes.new('ShaderNodeOutputMaterial')
            mm.node_tree.links.new(em.outputs[0], o.inputs[0])
            me.materials.append(mm)
            mo.visible_shadow = False
        mo.location = sun_dir(22, 200) * 3000
        mo.hide_render = False
        return p
    mo = bpy.data.objects.get('MoonDisc')
    if mo:
        mo.hide_render = True
    sky = nt.nodes.new('ShaderNodeTexSky')
    sky.location = (0, 0)
    sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(max(p['elev'], -3))
    sky.sun_rotation = math.radians(p['azim'])
    sky.air_density = p['air']
    sky.dust_density = p['dust']
    sky.ozone_density = p['ozone']
    sky.sun_disc = True
    sky.sun_size = math.radians(1.2)
    sky.sun_intensity = 0.4
    sky.altitude = 50
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.location = (400, 0)
    bg.inputs['Strength'].default_value = p['sky'] * 0.28
    add_haze(nt, out, p)
    nt.links.new(sky.outputs[0], bg.inputs['Color'])
    nt.links.new(bg.outputs[0], out.inputs[0])
    # Nishita sun_rotation: azimuth measured so that direction = (sin a, cos a)? match light to sky
    d = Vector((math.cos(math.radians(p['elev'])) * math.sin(math.radians(p['azim'])),
                math.cos(math.radians(p['elev'])) * math.cos(math.radians(p['azim'])),
                math.sin(math.radians(p['elev']))))
    sun.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    sun.data.energy = p['sun']
    sun.data.color = p['color']
    sun.data.angle = math.radians(2.5)
    sun.hide_render = p['sun'] <= 0
    try:
        sun.data.shadow_maximum_resolution = 0.001
    except Exception:
        pass
    return p
