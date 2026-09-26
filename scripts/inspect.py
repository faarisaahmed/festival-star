import bpy, sys, os, glob
path = sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
if path.endswith('.dae'): bpy.ops.wm.collada_import(filepath=path)
else: bpy.ops.import_scene.fbx(filepath=path)
arms=[o for o in bpy.data.objects if o.type=='ARMATURE']
meshes=[o for o in bpy.data.objects if o.type=='MESH']
print("RESULT", os.path.basename(path), "arms", [(a.name,len(a.data.bones)) for a in arms], "meshes", len(meshes))
for m in meshes:
    print("  mesh", m.name, len(m.data.vertices), "mats", [s.material.name if s.material else None for s in m.material_slots], "vg", len(m.vertex_groups), "parent", m.parent.name if m.parent else None, [md.type for md in m.modifiers])
import mathutils
pts=[m.matrix_world@mathutils.Vector(c) for m in meshes for c in m.bound_box]
mn=[min(p[i] for p in pts) for i in range(3)]; mx=[max(p[i] for p in pts) for i in range(3)]
print("  bbox", [round(x,3) for x in mn],[round(x,3) for x in mx])
if arms: print("  bones", [b.name for b in arms[0].data.bones][:80])
for mat in bpy.data.materials:
    imgs=[n.image.name for n in (mat.node_tree.nodes if mat.node_tree else []) if n.type=='TEX_IMAGE' and n.image]
    print("  mat", mat.name, imgs)
