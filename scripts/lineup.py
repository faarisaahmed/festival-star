import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + '/'
import bpy, math, sys
from mathutils import Vector
names=['pikachu','piplup','sobble','raboot','greninja','charizard','garchomp','dragonite']
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
x=0
for n in names:
    with bpy.data.libraries.load(ROOT+f'models/blend/{n}.blend') as (src,dst):
        dst.collections=[n.upper()]
    c=dst.collections[0]; sc.collection.children.link(c)
    arm=[o for o in c.objects if o.type=='ARMATURE'][0]
    w={'pikachu':.5,'piplup':.5,'sobble':.5,'raboot':.6,'greninja':1.2,'charizard':2.4,'garchomp':1.8,'dragonite':1.6}[n]
    x+=w/2; arm.location.x=x; x+=w/2+0.1
bpy.ops.mesh.primitive_plane_add(size=40); 
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam
cam.location=(x/2,-16,1.1); cam.rotation_euler=(math.radians(86),0,0); cam.data.lens=50
sun=bpy.data.objects.new('sun',bpy.data.lights.new('sun','SUN')); sc.collection.objects.link(sun)
sun.data.energy=4; sun.rotation_euler=(math.radians(50),0,math.radians(-30))
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True
w.node_tree.nodes['Background'].inputs[0].default_value=(0.6,0.75,1,1); w.node_tree.nodes['Background'].inputs[1].default_value=1.0
sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=1920; sc.render.resolution_y=640
sc.view_settings.view_transform='AgX'
sc.render.filepath=sys.argv[-1]; bpy.ops.render.render(write_still=True)
