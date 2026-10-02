# Final mix: score + ambience + effects + voices -> master WAV -> muxed into the movie (video stream copied, not re-rendered)
import os, subprocess
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy.signal import butter, sosfilt

A = os.path.dirname(os.path.abspath(__file__))
MOVIE = os.path.join(A, '..', 'The_Festival_Star.mp4')
OUT_MP4 = os.path.join(A, '..', 'The_Festival_Star_with_sound.mp4')
SR = 48000
DUR = 300.0
N = int(DUR * SR)
meter = pyln.Meter(SR)


def rd(p):
    a, sr = sf.read(p, always_2d=True)
    assert sr == SR, p
    out = np.zeros((N, 2))
    out[:min(N, len(a))] = a[:N]
    return out


music = rd(os.path.join(A, 'music', 'score_mix.wav'))
amb = rd(os.path.join(A, 'sfx', 'out', 'sfx_amb.wav'))
fx = rd(os.path.join(A, 'sfx', 'out', 'sfx_fx.wav'))
vox = rd(os.path.join(A, 'sfx', 'out', 'sfx_vox.wav'))


def to_lufs(x, target):
    l = meter.integrated_loudness(x)
    return x * 10 ** ((target - l) / 20), l


music, lm = to_lufs(music, -19.0)
amb, la = to_lufs(amb, -29.0)
fx, lf = to_lufs(fx, -25.0)
vox, lv = to_lufs(vox, -24.0)
print('source loudness  music %.1f  amb %.1f  fx %.1f  vox %.1f LUFS' % (lm, la, lf, lv))

def compress(x, thr_db, ratio, att=0.005, rel=0.25):
    lvl = np.sqrt(np.convolve((x ** 2).mean(axis=1), np.ones(480) / 480, 'same'))
    hop = 240
    e = lvl[:len(lvl) // hop * hop].reshape(-1, hop).max(axis=1)
    out = np.zeros_like(e)
    a, r = np.exp(-hop / SR / att), np.exp(-hop / SR / rel)
    v = 0.0
    for i, s in enumerate(e):
        v = a * v + (1 - a) * s if s > v else r * v + (1 - r) * s
        out[i] = v
    env = np.pad(np.repeat(out, hop), (0, len(x) - len(out) * hop), 'edge')
    over = np.maximum(0, 20 * np.log10(env + 1e-9) - thr_db)
    return x * (10 ** (-over * (1 - 1 / ratio) / 20))[:, None]


fx = compress(fx, -30, 3.0)
vox = compress(vox, -26, 2.0)
fx, _ = to_lufs(fx, -24.0)
vox, _ = to_lufs(vox, -24.0)

# duck the score under voices (and, a little, under big effects)
def envelope(x, att=0.02, rel=0.35):
    e = np.abs(x).max(axis=1)
    hop = 240
    e = e[:len(e) // hop * hop].reshape(-1, hop).max(axis=1)
    out = np.zeros_like(e)
    a, r = np.exp(-hop / SR / att), np.exp(-hop / SR / rel)
    v = 0.0
    for i, s in enumerate(e):
        v = a * v + (1 - a) * s if s > v else r * v + (1 - r) * s
        out[i] = v
    return np.repeat(out, hop)[:len(x)] if len(out) * hop >= len(x) else np.pad(np.repeat(out, hop), (0, len(x) - len(out) * hop), 'edge')


ev = envelope(vox)
ef = envelope(fx)
thr_v = 0.03
duck_db = -4.5 * np.clip((20 * np.log10(ev + 1e-9) - 20 * np.log10(thr_v)) / 12, 0, 1) \
          - 2.0 * np.clip((20 * np.log10(ef + 1e-9) - 20 * np.log10(0.08)) / 12, 0, 1)
duck = 10 ** (np.maximum(duck_db, -6) / 20)
music *= duck[:, None]

mix = music + amb + fx + vox
mix = sosfilt(butter(2, 25, 'high', fs=SR, output='sos'), mix, axis=0)
mix, lt = to_lufs(mix, -15.0)

# look-ahead peak limiter at -1.0 dBFS (4x oversampled peak estimate is overkill here; use sample peak w/ margin)
ceil = 10 ** (-1.2 / 20)
pk = np.abs(mix).max(axis=1)
w = int(0.004 * SR)
from scipy.ndimage import maximum_filter1d, uniform_filter1d
need = np.maximum(1.0, maximum_filter1d(pk, 2 * w + 1) / ceil)
g = 1 / need
g = np.minimum(g, uniform_filter1d(g, 2 * w + 1))
rel = np.exp(-1 / (0.08 * SR))
gs = g.copy()
for i in range(1, len(gs)):
    gs[i] = min(g[i], rel * gs[i - 1] + (1 - rel) * g[i])
mix *= gs[:, None]
mix = np.clip(mix, -ceil, ceil)
print('final integrated loudness %.1f LUFS, peak %.2f dBFS, max limiting %.1f dB' % (
    meter.integrated_loudness(mix), 20 * np.log10(np.abs(mix).max()), 20 * np.log10(gs.min())))

os.makedirs(os.path.join(A, 'final'), exist_ok=True)
wav = os.path.join(A, 'final', 'The_Festival_Star_soundtrack.wav')
sf.write(wav, mix.astype(np.float32), SR, subtype='PCM_24')
for name, x in (('music', music), ('ambience', amb), ('effects', fx), ('voices', vox)):
    sf.write(os.path.join(A, 'final', f'stem_{name}.wav'), x.astype(np.float32), SR, subtype='PCM_24')

subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', MOVIE, '-i', wav, '-map', '0:v:0', '-map', '1:a:0',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-shortest', '-movflags', '+faststart',
                OUT_MP4], check=True)
print('WROTE', os.path.abspath(OUT_MP4))
