import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + '/'
import bpy, math, sys
from mathutils import Vector
n=sys.argv[-2]; out=sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
with bpy.data.libraries.load(ROOT+f'models/blend/{n}.blend') as (src,dst): dst.collections=[n.upper()]
c=dst.collections[0]; sc.collection.children.link(c)
arm=[o for o in c.objects if o.type=='ARMATURE'][0]
bpy.context.view_layer.update()
meshes=[o for o in c.objects if o.type=='MESH']
pts=[m.matrix_world@Vector(b) for m in meshes for b in m.bound_box]
top=max(p.z for p in pts); h=top
hb=arm.data.bones.get('head')
tgt=(arm.matrix_world@hb.head_local) if hb else Vector((0,0,top*0.8))
if n=='sobble': tgt=Vector((0,0,top*0.6))
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam
d=h*1.1
cam.location=tgt+Vector((d*0.5,-d,d*0.15))
cam.rotation_euler=(tgt-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=50
sun=bpy.data.objects.new('sun',bpy.data.lights.new('sun','SUN')); sc.collection.objects.link(sun)
sun.data.energy=3.5; sun.rotation_euler=(math.radians(50),0,math.radians(-30))
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True
w.node_tree.nodes['Background'].inputs[0].default_value=(0.5,0.65,0.9,1)
sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=480; sc.render.resolution_y=480
sc.view_settings.view_transform='AgX'
sc.render.filepath=out; bpy.ops.render.render(write_still=True)
