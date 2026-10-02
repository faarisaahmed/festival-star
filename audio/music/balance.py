import soundfile as sf, numpy as np, glob, os, sys
from engine import INSTR, SR
st={}
for f in glob.glob('wav/*.wav'):
    a,_=sf.read(f,always_2d=True); ins=os.path.basename(f)[:-4]
    st[ins]=a.mean(1)*10**(INSTR[ins][3]/20)
checks=[(12.6,19.6,'fl','Pallet flute'),(19.6,26.6,'cl','Pallet clarinet'),(29.7,32,'xylo','pika xylo'),(32.7,38.6,'vln1f','Route1 vln'),
(40.1,46,'fl','lake flute'),(49.1,52,'ob','sobble lament'),(53,55,'cl','arrival cl'),(60.5,65,'cl','raboot cl'),(65.6,68,'shaku','greninja shaku'),
(83,87,'hn','dragonite hn'),(88.7,95,'fl','game fl'),(98.3,101.4,'tpt','game tutti'),(117,122,'vln1f','chase'),(132,134,'ob','lament'),(139.3,143,'hn','hope hn'),
(147,152,'piano','center piano'),(153.3,156,'solovn','solo vln'),(159.6,162,'vc','cello lament'),(168,172,'hn','charizard'),(178,186,'vln1','soar theme'),
(195,197.5,'vlnpizz','tiptoe'),(202.4,205.7,'ob','plea'),(209,215,'vln1','dusk'),(217,221,'cel','lullaby'),(233.6,236,'vln1','theme broad'),(246.4,254,'vln1','triumph'),
(256.4,269,'fiddle','jig fiddle'),(270,279,'vln1','ending'),(279.6,284,'fl','watch fl'),(289,294,'vln1','grand')]
for t0,t1,ins,name in checks:
    a,b=int(t0*SR),int(t1*SR)
    tot=sum(np.sum(v[a:b]**2) for v in st.values() if len(v)>a)
    me=np.sum(st[ins][a:b]**2) if ins in st else 0
    others=sorted(((np.sum(v[a:b]**2),k) for k,v in st.items() if k!=ins and len(v)>a),reverse=True)[:3]
    print(f"{name:16s} {ins:7s} share {100*me/max(tot,1e-12):5.1f}%  loudest others: "+', '.join(f"{k} {100*e/tot:.0f}%" for e,k in others))
