# Import a Scarlet/Violet model (DAE), rebuild materials, normalize, save as .blend
import bpy, sys, os, json, re, math
import numpy as np
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index('--')+1:]
name, dae, out = args[0], args[1], args[2]
d = os.path.dirname(dae)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.collada_import(filepath=dae)

matinfo = {}
stem = os.path.basename(dae)[:-4]
mt = os.path.join(d, stem + '_mat.txt')
if os.path.exists(mt):
    for m in json.load(open(mt)):
        matinfo[m['name']] = m

def tex_path(base):
    for ext in ('.png', '.tga'):
        p = os.path.join(d, base + ext)
        if os.path.exists(p): return p
    return None

def load(p, noncolor=False):
    img = bpy.data.images.load(p, check_existing=True)
    if noncolor: img.colorspace_settings.name = 'Non-Color'
    return img

def parse_col(s):
    v = [float(x) for x in s.strip('()').split(',')]
    return v[:3]

def img_uniform(p):
    img = bpy.data.images.load(p, check_existing=True)
    if img.size[0] * img.size[1] <= 32*32: return True
    px = np.array(img.pixels[:]).reshape(-1, 4)[::97, :3]
    return px.std() < 0.03

def find_tex(matname, kind):
    """Fallback texture search when there's no mat.txt (FBX-style exports)."""
    import glob
    base = re.sub(r'_\d\d$', '', matname)
    base = re.sub(r'^[lr]_', '', base)
    if base.startswith('eye'): base = re.sub(r'_a$', '', base)
    files = [os.path.basename(f) for f in glob.glob(os.path.join(d, '*.png'))]
    def pick(b):
        c = [f for f in files if re.search(rf'_{b}_{kind}', f) and 'rare' not in f and '_AO' not in f]
        if kind == 'alb':
            if b == 'eye':
                c = [f for f in files if re.search(r'_eye_lym_backed\.png$', f)] + c
            comp = [f for f in c if 'Composite' in f]
            c = comp + c
        return os.path.join(d, c[0]) if c else None
    return pick(base) or pick(base.split('_')[0])

def fix_normal(p):
    """Two-channel (RG) normal maps: rebuild Z so Blender's Normal Map node reads them right."""
    out = p[:-4] + '_z.png'
    if os.path.exists(out): return out
    img = bpy.data.images.load(p, check_existing=True)
    px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)
    if px[::53, 2].max() > 0.05: return p
    x = px[:, 0] * 2 - 1; y = px[:, 1] * 2 - 1
    px[:, 2] = np.sqrt(np.clip(1 - x*x - y*y, 0, 1)) * 0.5 + 0.5
    new = bpy.data.images.new(os.path.basename(out), img.size[0], img.size[1], alpha=True)
    new.pixels = px.ravel(); new.filepath_raw = out; new.file_format = 'PNG'; new.save()
    bpy.data.images.remove(new)
    return out

def build(mat):
    info = matinfo.get(mat.name, {})
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (500, 0)
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    is_eye = 'eye' in mat.name
    uv = nt.nodes.new('ShaderNodeUVMap'); uv.location = (-900, 0)

    def texnode(p, noncolor=False, y=0):
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = load(p, noncolor); n.location = (-600, y)
        nt.links.new(uv.outputs[0], n.inputs[0])
        return n

    alb = tex_path(info['BaseColorMap']) if 'BaseColorMap' in info else find_tex(mat.name, 'alb')
    col_socket = None; alpha_socket = None
    lym = tex_path(info['LayerMaskMap']) if 'LayerMaskMap' in info else None
    if alb or lym:
        if alb:
            t = texnode(alb, y=300)
            col_socket = t.outputs[0]; alpha_socket = t.outputs[1]
        else:
            rgb = nt.nodes.new('ShaderNodeRGB'); rgb.outputs[0].default_value = (1, 1, 1, 1)
            col_socket = rgb.outputs[0]
        if lym and 'BaseColorLayer1' in info and (not alb or img_uniform(alb)):
            lt = texnode(lym, True, y=600)
            sep = nt.nodes.new('ShaderNodeSeparateColor'); sep.location = (-300, 600)
            nt.links.new(lt.outputs[0], sep.inputs[0])
            for i in range(3):
                key = f'BaseColorLayer{i+1}'
                if key not in info: continue
                mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.location = (-100 + i*120, 400)
                nt.links.new(sep.outputs[i], mix.inputs['Factor'])
                nt.links.new(col_socket, mix.inputs['A'])
                mix.inputs['B'].default_value = parse_col(info[key]) + [1]
                col_socket = mix.outputs['Result']
        ao = tex_path(info['AOMap']) if 'AOMap' in info else find_tex(mat.name, 'ao')
        if ao and not is_eye:
            at = texnode(ao, True, y=0)
            mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.location = (300, 300)
            mul.inputs['Factor'].default_value = 0.8
            nt.links.new(col_socket, mul.inputs['A']); nt.links.new(at.outputs[0], mul.inputs['B'])
            col_socket = mul.outputs['Result']
        nt.links.new(col_socket, bsdf.inputs['Base Color'])
    nrm = tex_path(info['NormalMap']) if 'NormalMap' in info else find_tex(mat.name, 'nrm')
    if nrm:
        nrm = fix_normal(nrm)
        nt_ = texnode(nrm, True, y=-300)
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.location = (200, -300)
        nm.inputs['Strength'].default_value = float(info.get('NormalHeight') or 1) * (0.6 if is_eye else 1.0)
        nt.links.new(nt_.outputs[0], nm.inputs['Color']); nt.links.new(nm.outputs[0], bsdf.inputs['Normal'])
    if is_eye:
        bsdf.inputs['Roughness'].default_value = 0.12
        bsdf.inputs['Coat Weight'].default_value = 1.0
        bsdf.inputs['Coat Roughness'].default_value = 0.03
        bsdf.inputs['Specular IOR Level'].default_value = 0.6
    else:
        bsdf.inputs['Roughness'].default_value = 0.55
        bsdf.inputs['Subsurface Weight'].default_value = 0.08 if 'SSS' in str(info.get('layers', '')) or not info else 0.0
        bsdf.inputs['Subsurface Radius'].default_value = (0.05, 0.02, 0.01)
        bsdf.inputs['Subsurface Scale'].default_value = 0.05
        bsdf.inputs['Sheen Weight'].default_value = 0.15
        bsdf.inputs['Sheen Roughness'].default_value = 0.5
    if 'fire' in mat.name and col_socket is not None:
        nt.links.new(col_socket, bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 6.0
        if alpha_socket: nt.links.new(alpha_socket, bsdf.inputs['Alpha'])
        mat.surface_render_method = 'BLENDED'
    if info.get('type', '').startswith('Blend') and 'Transparent' in str(info.get('layers', '')):
        bsdf.inputs['Alpha'].default_value = 0.35
        mat.surface_render_method = 'BLENDED'
    if is_eye and alb and 'backed' in alb and alpha_socket:
        nt.links.new(alpha_socket, bsdf.inputs['Alpha'])
        mat.surface_render_method = 'DITHERED'

for mat in list(bpy.data.materials):
    build(mat)

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
# drop anything not parented to the armature (stray shapes)
for o in list(bpy.data.objects):
    if o.type not in ('ARMATURE', 'MESH'):
        bpy.data.objects.remove(o)
arm.name = name.upper() + '_rig'
arm.data.name = name.upper() + '_armdata'
for m in meshes:
    m.name = name + '_' + m.name.split('_mesh')[0].split('_')[-1] if '_mesh' in m.name else name + '_' + m.name
    if m.parent is None:
        m.parent = arm
    m.data.shade_smooth() if hasattr(m.data, 'shade_smooth') else None

if name == 'greninja':
    # this export ships broken custom split normals
    for m in meshes:
        with bpy.context.temp_override(object=m, active_object=m):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
        m.data.shade_smooth()
        if any(sl.material and sl.material.name == 'eye_d' for sl in m.material_slots):
            m.name = 'greninja_eyeclosed'; m.hide_render = True
if name == 'sobble':
    for m in meshes:
        if 'tear' in m.name: m.hide_render = True; m.hide_viewport = True

coll = bpy.data.collections.new(name.upper())
bpy.context.scene.collection.children.link(coll)
for o in [arm] + meshes:
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o)

# bake the Y-up -> Z-up rotation into the rig so the armature has identity transform
bpy.context.view_layer.update()
for o in bpy.context.view_layer.objects: o.select_set(o in [arm] + meshes)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.context.view_layer.update()
# report facing: head bone position vs origin
bones = arm.data.bones
def bpos(n):
    b = bones.get(n)
    return (arm.matrix_world @ b.head_local) if b else None
print('FACING', name, 'head', bpos('head'), 'waist', bpos('waist'), 'tail', bpos('tail_01'), 'arm scale', arm.scale, arm.rotation_euler)
bpy.ops.wm.save_as_mainfile(filepath=out)
