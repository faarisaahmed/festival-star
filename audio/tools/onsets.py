import soundfile as sf, numpy as np, sys
for f in sys.argv[1:]:
    a,sr=sf.read(f,always_2d=True); m=a.mean(1)
    hop=int(sr*0.01); n=len(m)//hop
    e=np.sqrt(np.mean(m[:n*hop].reshape(n,hop)**2,axis=1))+1e-9
    db=20*np.log10(e); floor=np.percentile(db,10)
    # onsets: rise > 12 dB over 50 ms
    ons=[]
    i=5
    while i<n:
        if db[i]-db[max(0,i-5):i].min()>12 and db[i]>floor+20:
            j=i+np.argmax(db[i:i+20]); ons.append((j*0.01,db[j])); i=j+40
        else: i+=1
    print(f"{f.split('/')[-1]:34s} {len(m)/sr:6.1f}s sr{sr} peak {20*np.log10(np.abs(m).max()+1e-9):5.1f}dB floor {floor:5.1f}  onsets: "+' '.join(f"{t:.2f}({d:.0f})" for t,d in ons[:14]))
