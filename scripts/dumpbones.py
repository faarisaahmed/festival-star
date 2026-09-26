import bpy, sys
n=sys.argv[-1]
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
lines=[]
def rec(b,d):
    h=b.head_local; t=b.tail_local; v=(t-h).normalized()
    lines.append('  '*d+f'{b.name} h=({h.x:.3f},{h.y:.3f},{h.z:.3f}) len={b.length:.3f} dir=({v.x:.2f},{v.y:.2f},{v.z:.2f})')
    for c in b.children: rec(c,d+1)
for b in arm.data.bones:
    if b.parent is None: rec(b,0)
open(f'models/bones/{n}.txt','w').write('\n'.join(lines)+'\n')
