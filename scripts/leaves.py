# Leaf-card foliage: scatters individual leaves over the canopy blobs of a
# tree/bush mesh with geometry nodes, realizes them, and darkens the blob core.
import bpy, math

_CACHE = {}


def leaf_mesh(kind='broad'):
    if kind in _CACHE:
        return _CACHE[kind]
    if kind == 'broad':
        # pointed ellipse with a slight fold along the midrib
        pts = [(0, 0, 0), (0.28, 0.18, 0.03), (0.62, 0.22, 0.05), (1.0, 0, 0.02), (0.62, -0.22, 0.05), (0.28, -0.18, 0.03)]
        faces = [(0, 1, 2, 3), (0, 3, 4, 5)]
    else:
        pts = [(0, 0, 0), (0.5, 0.06, 0.02), (1.0, 0, 0), (0.5, -0.06, 0.02)]
        faces = [(0, 1, 2, 3)]
    me = bpy.data.meshes.new('LeafCard_' + kind)
    me.from_pydata([(x - 0.15, y, z) for x, y, z in pts], [], faces)
    uv = me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (co.x, co.y + 0.5)
    ob = bpy.data.objects.new('LeafCard_' + kind, me)
    _CACHE[kind] = ob
    return ob


def mat_leafcard(name, c1, c2):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes['Principled BSDF']
    at = nt.nodes.new('ShaderNodeAttribute')
    at.attribute_name = 'leafvar'
    at.attribute_type = 'GEOMETRY'
    r = nt.nodes.new('ShaderNodeValToRGB')
    r.color_ramp.elements[0].color = (*c1, 1)
    r.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(at.outputs['Fac'], r.inputs[0])
    # midrib / edge darkening from UV
    uv = nt.nodes.new('ShaderNodeUVMap')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(uv.outputs[0], sep.inputs[0])
    d = nt.nodes.new('ShaderNodeMath')
    d.operation = 'SUBTRACT'
    nt.links.new(sep.outputs['Y'], d.inputs[0])
    d.inputs[1].default_value = 0.5
    a = nt.nodes.new('ShaderNodeMath')
    a.operation = 'ABSOLUTE'
    nt.links.new(d.outputs[0], a.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange')
    nt.links.new(a.outputs[0], mr.inputs['Value'])
    mr.inputs['From Min'].default_value = 0.0
    mr.inputs['From Max'].default_value = 0.2
    mr.inputs['To Min'].default_value = 1.15
    mr.inputs['To Max'].default_value = 0.8
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0
    nt.links.new(r.outputs[0], mix.inputs['A'])
    cc = nt.nodes.new('ShaderNodeCombineColor')
    for i in range(3):
        nt.links.new(mr.outputs[0], cc.inputs[i])
    nt.links.new(cc.outputs[0], mix.inputs['B'])
    nt.links.new(mix.outputs['Result'], bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value = 0.45
    bs.inputs['Specular IOR Level'].default_value = 0.45
    bs.inputs['Subsurface Weight'].default_value = 0.35
    bs.inputs['Subsurface Radius'].default_value = (0.4, 0.9, 0.15)
    bs.inputs['Subsurface Scale'].default_value = 0.05
    bs.inputs['Sheen Weight'].default_value = 0.2
    m.use_backface_culling = False
    return m


def mat_core(name, c):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = (*c, 1)
    bs.inputs['Roughness'].default_value = 0.9
    return m


def group(name, leaf_obj, leaf_mat_sel, leaf_mat, core_mat, density, size, jitter=0.35, seed=0, droop=0.0):
    ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N = ng.nodes
    L = ng.links.new
    gi = N.new('NodeGroupInput')
    go = N.new('NodeGroupOutput')
    ms = N.new('GeometryNodeMaterialSelection')
    ms.inputs['Material'].default_value = leaf_mat_sel
    dist = N.new('GeometryNodeDistributePointsOnFaces')
    dist.inputs['Density'].default_value = density
    dist.inputs['Seed'].default_value = seed
    L(gi.outputs[0], dist.inputs['Mesh'])
    L(ms.outputs[0], dist.inputs['Selection'])
    # rotation: align leaf X axis roughly along the surface normal (sticking out),
    # then random twist
    al = N.new('FunctionNodeAlignRotationToVector')
    al.axis = 'X'
    nrm_add = N.new('ShaderNodeVectorMath')
    nrm_add.operation = 'ADD'
    rv = N.new('FunctionNodeRandomValue')
    rv.data_type = 'FLOAT_VECTOR'
    rv.inputs['Min'].default_value = (-0.9, -0.9, -0.9 - droop)
    rv.inputs['Max'].default_value = (0.9, 0.9, 0.9 - droop)
    rv.inputs['Seed'].default_value = seed + 5
    L(dist.outputs['Normal'], nrm_add.inputs[0])
    L(rv.outputs[0], nrm_add.inputs[1])
    L(nrm_add.outputs[0], al.inputs['Vector'])
    tw = N.new('FunctionNodeRandomValue')
    tw.data_type = 'FLOAT_VECTOR'
    tw.inputs['Min'].default_value = (-3.14, 0, 0)
    tw.inputs['Max'].default_value = (3.14, 0, 0)
    tw.inputs['Seed'].default_value = seed + 6
    e2r = N.new('FunctionNodeEulerToRotation')
    L(tw.outputs[0], e2r.inputs[0])
    rr = N.new('FunctionNodeRotateRotation')
    rr.rotation_space = 'LOCAL'
    L(al.outputs[0], rr.inputs['Rotation'])
    L(e2r.outputs[0], rr.inputs['Rotate By'])
    oi = N.new('GeometryNodeObjectInfo')
    oi.inputs['Object'].default_value = leaf_obj
    inst = N.new('GeometryNodeInstanceOnPoints')
    L(dist.outputs['Points'], inst.inputs['Points'])
    L(oi.outputs['Geometry'], inst.inputs['Instance'])
    L(rr.outputs[0], inst.inputs['Rotation'])
    sz = N.new('FunctionNodeRandomValue')
    sz.data_type = 'FLOAT'
    sz.inputs[2].default_value = size * (1 - jitter)
    sz.inputs[3].default_value = size * (1 + jitter)
    sz.inputs['Seed'].default_value = seed + 7
    L(sz.outputs[1], inst.inputs['Scale'])
    # per-leaf colour variation
    var = N.new('FunctionNodeRandomValue')
    var.data_type = 'FLOAT'
    var.inputs['Seed'].default_value = seed + 8
    # brighter leaves toward the top/outside
    pos = N.new('GeometryNodeInputPosition')
    sp = N.new('ShaderNodeSeparateXYZ')
    L(pos.outputs[0], sp.inputs[0])
    bb = N.new('GeometryNodeBoundBox')
    L(gi.outputs[0], bb.inputs[0])
    spmax = N.new('ShaderNodeSeparateXYZ')
    L(bb.outputs['Max'], spmax.inputs[0])
    hz = N.new('ShaderNodeMath')
    hz.operation = 'DIVIDE'
    L(sp.outputs['Z'], hz.inputs[0])
    L(spmax.outputs['Z'], hz.inputs[1])
    mixv = N.new('ShaderNodeMath')
    mixv.operation = 'MULTIPLY_ADD'
    L(var.outputs[1], mixv.inputs[0])
    mixv.inputs[1].default_value = 0.6
    hz2 = N.new('ShaderNodeMath')
    hz2.operation = 'MULTIPLY'
    L(hz.outputs[0], hz2.inputs[0])
    hz2.inputs[1].default_value = 0.45
    L(hz2.outputs[0], mixv.inputs[2])
    st = N.new('GeometryNodeStoreNamedAttribute')
    st.data_type = 'FLOAT'
    st.domain = 'INSTANCE'
    st.inputs['Name'].default_value = 'leafvar'
    L(inst.outputs[0], st.inputs['Geometry'])
    L(mixv.outputs[0], st.inputs['Value'])
    real = N.new('GeometryNodeRealizeInstances')
    L(st.outputs[0], real.inputs[0])
    smat = N.new('GeometryNodeSetMaterial')
    smat.inputs['Material'].default_value = leaf_mat
    L(real.outputs[0], smat.inputs['Geometry'])
    # darken the blob core so it reads as depth inside the canopy
    core = N.new('GeometryNodeSetMaterial')
    core.inputs['Material'].default_value = core_mat
    L(gi.outputs[0], core.inputs['Geometry'])
    ms2 = N.new('GeometryNodeMaterialSelection')
    ms2.inputs['Material'].default_value = leaf_mat_sel
    L(ms2.outputs[0], core.inputs['Selection'])
    j = N.new('GeometryNodeJoinGeometry')
    L(smat.outputs[0], j.inputs[0])
    L(core.outputs[0], j.inputs[0])
    L(j.outputs[0], go.inputs[0])
    return ng


def apply(obj, leaf_mat_sel, c1, c2, core_c, density=40, size=0.3, kind='broad', seed=0, droop=0.0):
    key = (leaf_mat_sel.name, kind)
    lm = bpy.data.materials.get('LeafCard_' + leaf_mat_sel.name) or mat_leafcard('LeafCard_' + leaf_mat_sel.name, c1, c2)
    cm = bpy.data.materials.get('LeafCore_' + leaf_mat_sel.name) or mat_core('LeafCore_' + leaf_mat_sel.name, core_c)
    ng = group('GN_Leaves_' + obj.name, leaf_mesh(kind), leaf_mat_sel, lm, cm, density, size, seed=seed, droop=droop)
    md = obj.modifiers.new('Leaves', 'NODES')
    md.node_group = ng
    return md
