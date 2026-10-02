# render every instrument stem with fluidsynth, then mix: pan, hall reverb, gentle mastering
import os, sys, glob
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt
from engine import INSTR, SFZ, SR, render_stem, hall_ir

ROOT = os.path.dirname(os.path.abspath(__file__))
MID = os.path.join(ROOT, 'midi')
WAV = os.path.join(ROOT, 'wav')
DUR = 300.0
os.makedirs(WAV, exist_ok=True)

mids = sorted(glob.glob(os.path.join(MID, '*.mid')))
with ThreadPoolExecutor(6) as ex:
    def _r(m):
        w = os.path.join(WAV, os.path.basename(m)[:-4] + '.wav')
        last = m + '.last'
        if not os.path.exists(w) or not os.path.exists(last) or open(m, 'rb').read() != open(last, 'rb').read():
            render_stem(m, w, ins=os.path.basename(m)[:-4])
            open(m + '.last', 'wb').write(open(m, 'rb').read())
    list(ex.map(_r, mids))

N = int(DUR * SR) + SR * 4
dry = np.zeros((N, 2))
send = np.zeros((N, 2))
GROUP = {}
for m in mids:
    ins = os.path.basename(m)[:-4]
    a, sr = sf.read(os.path.join(WAV, ins + '.wav'), always_2d=True)
    assert sr == SR
    bank, prog, pan, gain, rev, drum = INSTR[ins]
    mono = a.mean(axis=1)
    side = (a[:, 0] - a[:, 1]) * 0.5
    th = (pan + 1) * np.pi / 4
    gl, gr = np.cos(th) * np.sqrt(2), np.sin(th) * np.sqrt(2)
    g = 10 ** (gain / 20)
    st = np.stack([mono * gl + side, mono * gr - side], axis=1) * g
    n = min(len(st), N)
    dry[:n] += st[:n]
    send[:n] += st[:n] * rev * (0.7 if ins in SFZ else 1.0)
    print(f'{ins:8s} peak {np.abs(st).max():.3f} rms {np.sqrt(np.mean(st ** 2)):.4f}')

ir = hall_ir(2.9)
wet = np.stack([fftconvolve(send[:, c], ir[:, c])[:N] for c in range(2)], axis=1)
# keep the reverb out of the mud
wet = sosfilt(butter(2, 180, 'high', fs=SR, output='sos'), wet, axis=0)
wet *= np.sqrt(np.mean(send ** 2)) / max(1e-9, np.sqrt(np.mean(wet ** 2))) * 1.1
mix = dry * 0.82 + wet
# gentle master: low-cut, a touch of air, slow compression, peak limit
mix = sosfilt(butter(2, 32, 'high', fs=SR, output='sos'), mix, axis=0)
air = sosfilt(butter(2, 7000, 'high', fs=SR, output='sos'), mix, axis=0)
mix = mix + 0.18 * air
env = np.sqrt(np.convolve((mix ** 2).mean(axis=1), np.ones(SR // 2) / (SR // 2), 'same'))
thr = np.percentile(env[env > 1e-4], 90)
gr = np.where(env > thr, (thr / np.maximum(env, 1e-9)) ** 0.35, 1.0)
mix *= gr[:, None]
mix = mix[:int(DUR * SR)]
peak = np.abs(mix).max()
mix *= 0.89 / peak
sf.write(os.path.join(ROOT, 'score_mix.wav'), mix.astype(np.float32), SR, subtype='FLOAT')
print('wrote score_mix.wav  peak-normalised from', round(float(peak), 3))
