# THE FESTIVAL STAR - sound effects, ambience and Pokémon voices, placed to the picture.
# Writes three stems (amb / fx / vox) at 48 kHz for the final mix.
import os, sys, math, random
from fractions import Fraction
from functools import lru_cache
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt, fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.dirname(HERE)
RAW = os.path.join(HERE, 'raw')
CRY = os.path.join(AUD, 'cries')
SR = 48000
DUR = 300.0
N = int(DUR * SR) + SR * 6
rng = np.random.default_rng(5)
R = random.Random(5)

BUS = {k: np.zeros((N, 2)) for k in ('amb', 'fx', 'vox')}
SEND = {k: np.zeros((N, 2)) for k in ('amb', 'fx', 'vox')}


# ----------------------------------------------------------------------------- io / dsp
@lru_cache(maxsize=None)
def load(path):
    if not os.path.isabs(path):
        for base in (RAW, CRY, os.path.join(CRY, 'extra')):
            for cand in (os.path.join(base, path), os.path.join(base, path + '.wav')):
                if os.path.exists(cand):
                    path = cand
                    break
    a, sr = sf.read(path, always_2d=True, dtype='float64')
    if a.shape[1] == 1:
        a = np.repeat(a, 2, axis=1)
    if sr != SR:
        fr = Fraction(SR, sr).limit_denominator(1000)
        a = resample_poly(a, fr.numerator, fr.denominator, axis=0)
    return a


def cry(name):
    """'pikachu' -> modern cry ; 'pikachu/pokken_laugh' -> extra clip"""
    if '/' in name:
        p = os.path.join(CRY, 'extra', name + '.wav')
        if os.path.exists(p):
            return load(p)
        print('missing voice clip', name, '- using the standard cry instead (run audio/tools/fetch_voices.py)')
        name = name.split('/')[0]
    return load(os.path.join(CRY, name + '.ogg'))


def filt(a, lp=None, hp=None, order=2):
    if hp:
        a = sosfilt(butter(order, hp, 'high', fs=SR, output='sos'), a, axis=0)
    if lp:
        a = sosfilt(butter(order, lp, 'low', fs=SR, output='sos'), a, axis=0)
    return a


def rate_shift(a, rate):
    if abs(rate - 1) < 1e-3:
        return a
    fr = Fraction(rate).limit_denominator(200)
    return resample_poly(a, fr.denominator, fr.numerator, axis=0)


def place(src, t, db=0.0, pan=0.0, rate=1.0, start=0.0, dur=None, fi=0.004, fo=0.04, lp=None, hp=None,
          rev=0.12, bus='fx', width=1.0, env=None):
    a = load(src) if isinstance(src, str) else src
    if a.ndim == 1:
        a = np.stack([a, a], axis=1)
    s0 = int(start * SR)
    a = a[s0:s0 + (int(dur * SR) if dur else len(a))].copy()
    a = rate_shift(a, rate)
    if lp or hp:
        a = filt(a, lp, hp)
    n = len(a)
    if n < 4:
        return
    g = np.ones(n)
    k = min(n // 2, int(fi * SR))
    if k > 0:
        g[:k] = np.linspace(0, 1, k) ** 2
    k = min(n // 2, int(fo * SR))
    if k > 0:
        g[-k:] *= np.linspace(1, 0, k) ** 1.5
    if env is not None:
        g *= np.interp(np.arange(n) / SR, env[0], env[1])
    a *= g[:, None] * 10 ** (db / 20)
    m = a.mean(axis=1)
    sd = (a[:, 0] - a[:, 1]) * 0.5 * width
    th = (pan + 1) * np.pi / 4
    a = np.stack([m * np.cos(th) * 1.4142 + sd, m * np.sin(th) * 1.4142 - sd], axis=1)
    i0 = int(t * SR)
    if i0 < 0:
        a = a[-i0:]
        i0 = 0
    i1 = min(N, i0 + len(a))
    BUS[bus][i0:i1] += a[:i1 - i0]
    SEND[bus][i0:i1] += a[:i1 - i0] * rev


def voice(name, t, db=-8, pan=0.0, rate=1.0, rev=0.1, lp=None, **k):
    place(cry(name), t, db, pan, rate, rev=rev, bus='vox', lp=lp, **k)


def loop_bed(src, t0, t1, db, start=0.0, fi=1.5, fo=1.5, lp=None, hp=None, rev=0.05, bus='amb', pan=0.0, env=None):
    """a stretch of a long recording laid from t0 to t1 (looped with crossfades if needed)"""
    a = load(src)
    need = t1 - t0
    seg = a[int(start * SR):]
    if len(seg) / SR < need + 0.1:
        # crossfade-loop
        out = seg.copy()
        xf = int(2 * SR)
        while len(out) / SR < need + 0.1:
            nxt = a[int(R.uniform(0, max(0.0, len(a) / SR - need - 3)) * SR):]
            w = np.linspace(0, 1, xf)[:, None]
            out = np.concatenate([out[:-xf], out[-xf:] * (1 - w) + nxt[:xf] * w, nxt[xf:]])
        seg = out
    place(seg, t0, db, pan, dur=need, fi=fi, fo=fo, lp=lp, hp=hp, rev=rev, bus=bus, env=env)


# ----------------------------------------------------------------------------- synthesis
def tvec(d):
    return np.arange(int(d * SR)) / SR


def noise(d, color='white'):
    x = rng.standard_normal(int(d * SR))
    if color == 'pink':
        X = np.fft.rfft(x)
        f = np.fft.rfftfreq(len(x), 1 / SR)
        X /= np.sqrt(np.maximum(f, 20))
        x = np.fft.irfft(X, len(x))
        x /= np.abs(x).max()
    return x


def sweep_bp(x, f0, f1, q=2.0, steps=60):
    """band-pass with a moving centre (block-wise)"""
    n = len(x)
    out = np.zeros(n)
    b = n // steps + 1
    zi = None
    for i in range(steps):
        a0, a1 = i * b, min(n, (i + 1) * b)
        if a0 >= n:
            break
        fc = f0 * (f1 / f0) ** (i / max(1, steps - 1))
        lo, hi = fc / (1 + 1 / q), min(SR / 2 - 100, fc * (1 + 1 / q))
        sos = butter(2, [max(20, lo), hi], 'band', fs=SR, output='sos')
        out[a0:a1] = sosfilt(sos, x[a0:a1])
    return out


def whoosh(d, f0=300, f1=2500, peak=0.5, q=1.6, stereo=0.4):
    t = tvec(d)
    env = np.where(t < peak * d, (t / (peak * d)) ** 2, ((d - t) / ((1 - peak) * d)) ** 1.6)
    x = sweep_bp(noise(d, 'pink'), f0, f1, q) * env
    x2 = sweep_bp(noise(d, 'pink'), f0 * 1.1, f1 * 1.1, q) * env
    x /= np.abs(x).max() + 1e-9
    x2 /= np.abs(x2).max() + 1e-9
    return np.stack([x * (1 - stereo / 2) + x2 * stereo / 2, x2 * (1 - stereo / 2) + x * stereo / 2], axis=1)


def bell(f, d=2.5, partials=((1, 1), (2.76, .5), (5.4, .25), (8.93, .12)), decay=1.6, detune=0.002):
    t = tvec(d)
    x = np.zeros(len(t))
    for r, a in partials:
        for dt in (-detune, detune):
            x += a * np.sin(2 * np.pi * f * r * (1 + dt) * t + R.random() * 6) * np.exp(-t * decay * (1 + r * 0.35))
    x *= np.clip(t / 0.002, 0, 1)
    return x / (np.abs(x).max() + 1e-9)


def shimmer(d=2.0, base=1760, n=14, spread=1.0, decay=2.2, seed=0):
    """cloud of tiny high bells - the Star's twinkle"""
    r = random.Random(seed)
    out = np.zeros((int((d + 1.5) * SR), 2))
    scale = [1, 9 / 8, 5 / 4, 3 / 2, 5 / 3, 2, 9 / 4, 5 / 2, 3, 10 / 3, 4]
    for i in range(n):
        f = base * r.choice(scale)
        b = bell(f, 1.4, ((1, 1), (2.0, .3), (4.1, .1)), decay=decay + r.random())
        t0 = int(r.uniform(0, d * spread) * SR)
        p = r.uniform(-0.8, 0.8)
        g = r.uniform(0.3, 1.0)
        seg = out[t0:t0 + len(b)]
        seg[:, 0] += b[:len(seg)] * g * (1 - p) / 2
        seg[:, 1] += b[:len(seg)] * g * (1 + p) / 2
    return out / (np.abs(out).max() + 1e-9)


def riser(d=2.5, f0=200, f1=4000):
    t = tvec(d)
    x = sweep_bp(noise(d, 'pink'), f0, f1, 3.0) * (t / d) ** 2.2
    ph = 2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (t / d) * 0.5) / SR
    tone = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3.01 * ph)) * (t / d) ** 3 * 0.25
    y = x / (np.abs(x).max() + 1e-9) + tone
    return y / (np.abs(y).max() + 1e-9)


def boom(d=2.5, f0=70, f1=32):
    t = tvec(d)
    ph = 2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (t / d)) / SR
    x = np.sin(ph) * np.exp(-t * 2.2) + 0.4 * filt(noise(d), lp=400) * np.exp(-t * 6)
    x *= np.clip(t / 0.003, 0, 1)
    return x / (np.abs(x).max() + 1e-9)


def thump(f=60, d=0.35, click=0.3):
    t = tvec(d)
    ph = 2 * np.pi * np.cumsum(f * 1.8 * np.exp(-t * 25) + f) / SR
    x = np.sin(ph) * np.exp(-t * 14) + click * filt(noise(d), lp=1800, hp=200) * np.exp(-t * 60)
    return x / (np.abs(x).max() + 1e-9)


def drop(f=900):
    d = 0.09
    t = tvec(d)
    ph = 2 * np.pi * np.cumsum(f * (1 + 2.2 * t / d)) / SR
    x = np.sin(ph) * np.exp(-t * 45) * np.clip(t / 0.001, 0, 1)
    return x / np.abs(x).max()


def zap(d=1.0, density=60, seed=0, low=True):
    """electric crackle (Pikachu's cheeks)"""
    r = np.random.default_rng(seed)
    n = int(d * SR)
    x = np.zeros(n)
    k = int(d * density)
    for _ in range(k):
        i = r.integers(0, n - 1000)
        L = r.integers(40, 900)
        burst = r.standard_normal(L) * np.exp(-np.arange(L) / (L / 4))
        x[i:i + L] += burst * r.uniform(0.2, 1)
    x = filt(x, hp=1500, lp=11000)
    if low:
        t = tvec(d)
        gate = (r.random(n // 480 + 1) > 0.55).repeat(480)[:n].astype(float)
        gate = np.convolve(gate, np.ones(96) / 96, 'same')
        saw = ((t * 118) % 1 - 0.5) + 0.5 * ((t * 236.5) % 1 - 0.5)
        x += filt(saw, lp=3000) * gate * 0.5
    return x / (np.abs(x).max() + 1e-9)


def clap():
    d = 0.18
    t = tvec(d)
    x = np.zeros(len(t))
    for j, dt in enumerate((0, 0.008, 0.017)):
        i = int(dt * SR)
        x[i:] += noise(d)[:len(x) - i] * np.exp(-t[:len(x) - i] * (40 if j < 2 else 18)) * (0.7 if j < 2 else 1)
    x = filt(x, lp=3500, hp=500)
    return x / np.abs(x).max()


def wingbeat(size=1.0, d=0.45):
    """one big leathery downstroke: low air whump + flutter"""
    t = tvec(d)
    env = np.minimum(t / (0.12 * d / 0.45), 1) ** 1.5 * np.exp(-np.maximum(0, t - 0.12) * 9)
    x = sweep_bp(noise(d, 'pink'), 900 / size, 140 / size, 1.2, steps=20) * env
    fl = filt(noise(d), lp=2500, hp=600) * env * (1 + np.sin(2 * np.pi * 38 * t)) * 0.12
    y = x / (np.abs(x).max() + 1e-9) + fl
    return y / (np.abs(y).max() + 1e-9)


def step_bank():
    """single footsteps cut from the grass recordings"""
    a = load('steps_run_grass')
    out = []
    for o in (9.91, 13.99, 14.86, 15.34, 16.10, 16.93, 17.80, 19.43, 21.07, 22.24):
        s = a[int((o - 0.03) * SR):int((o + 0.22) * SR)].copy()
        s *= np.linspace(1, 0, len(s))[:, None] ** 1.2
        out.append(s / (np.abs(s).max() + 1e-9))
    return out


STEPS = step_bank()


def steps(t0, t1, rate, db, pan=0.0, pitch=1.0, rev=0.06, jitter=0.02, lp=None, accel=None):
    t = t0
    i = 0
    while t < t1:
        place(R.choice(STEPS), t + R.uniform(-jitter, jitter), db + R.uniform(-2.5, 1), pan, pitch * R.uniform(0.94, 1.06),
              lp=lp, rev=rev)
        t += 1.0 / rate
        i += 1


def heavy_steps(times, db, pan=0.0, size=1.0):
    for k, t in enumerate(times):
        place(thump(46 / size, 0.6, 0.25), t, db, pan, rev=0.15)
        place(R.choice(STEPS), t + 0.005, db - 6, pan, 0.62, lp=2500, rev=0.1)


def flaps(t0, t1, rate, db, pan=0.0, size=1.0, start_ph=0.5, env=None, lp=None):
    """wingbeats from t0 to t1 (rate Hz); downstroke at phase start_ph of each cycle"""
    k = 0
    t = t0 + start_ph / rate
    while t < t1:
        g = db if env is None else db + env(t)
        w = wingbeat(size, 0.5 / max(0.6, rate) + 0.15)
        place(w, t - 0.1, g + R.uniform(-1.5, 0.5), pan, R.uniform(0.95, 1.05), lp=lp, rev=0.12)
        if k % 3 == 1:
            place('wings_takeoff', t - 0.05, g - 9, pan, 0.8, start=R.choice((11.40, 14.18, 22.06, 30.30)), dur=0.35,
                  fo=0.15, lp=lp, rev=0.1)
        t += 1.0 / rate
        k += 1


def firework(t_launch, t_burst, dist_db=0.0, pan=0.0, delay=0.3, big=False):
    # launch: thump + rising whistle
    place('fw_rocket', t_launch - 0.45, -14 + dist_db, pan, 1.0, start=0.0, dur=1.6, rev=0.25)
    d = max(0.3, t_burst - t_launch - 0.05)
    tt = tvec(d)
    f = 1400 + 1500 * (tt / d)
    wh = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, tt / 0.1) * (1 - 0.3 * tt / d)
    wh = wh + 0.3 * filt(noise(d), lp=6000, hp=2500) * (1 - tt / d)
    place(wh / np.abs(wh).max(), t_launch, -27 + dist_db, pan * 0.5, rev=0.35)
    # burst: big crack + boom tail + crackle, delayed by distance
    tb = t_burst + delay
    src = R.choice([('fw_explodes', 0.50), ('fw_cannon', 0.62), ('fw_rocket_exploding', 0.40), ('fw_four_cannons', 0.47),
                    ('fw_four_cannons', 3.50), ('fw_display_noisy', 5.55), ('fw_display_noisy', 14.36)])
    place(src[0], tb - 0.02, -6 + dist_db + (2 if big else 0), pan, R.uniform(0.92, 1.04), start=src[1], dur=3.2, fi=0.002,
          fo=0.8, lp=9000, rev=0.4)
    place(boom(3.0, 60, 28), tb, -9 + dist_db, pan, rev=0.3)
    place('fw_squibs', tb + 0.35, -20 + dist_db, pan + R.uniform(-0.2, 0.2), 1.0, start=R.choice((5.3, 7.4, 9.05)),
          dur=2.2, fi=0.2, fo=1.0, lp=7000, rev=0.4)
    place(shimmer(1.6, 1500, 18, seed=int(tb * 10)), tb + 0.1, -24 + dist_db, pan, rev=0.4)


def magic_burst(t, db=-6, size=1.0, seed=0, low=True):
    place(shimmer(2.2 * size, 1320, int(26 * size), seed=seed), t, db, 0, rev=0.45)
    place(bell(880, 4.0, decay=0.9), t, db - 6, -0.2, rev=0.5)
    place(bell(1318.5, 4.0, decay=0.9), t + 0.02, db - 8, 0.2, rev=0.5)
    if low:
        place(boom(3.5, 55, 30), t, db - 2, 0, rev=0.3)


def snore(t, db, pan=0.0, size=1.0, lp=None):
    d = 1.3
    tt = tvec(d)
    env = np.sin(np.pi * np.clip(tt / d, 0, 1)) ** 1.5
    buzz = ((tt * 52 / size) % 1 - 0.5) * (1 + 0.6 * np.sin(2 * np.pi * 7 * tt))
    x = filt(buzz, lp=700) * env + 0.5 * filt(noise(d, 'pink'), lp=1200, hp=150) * env
    place(x / np.abs(x).max(), t, db, pan, lp=lp, rev=0.15, bus='vox')
    ex = filt(noise(1.6, 'pink'), lp=2500, hp=200) * np.sin(np.pi * np.clip(tvec(1.6) / 1.6, 0, 1)) ** 2
    place(ex / np.abs(ex).max(), t + 1.4, db - 5, pan, lp=lp, rev=0.15, bus='vox')


# ============================================================================= AMBIENCE
A = loop_bed
# Act I morning
A('amb_high_gusting_wind', 0.0, 14.3, -26, start=8, fi=2.0, fo=0.6, lp=2500)
A('amb_dawn_chorus', 0.0, 29.3, -22, start=40, fi=3.0, fo=0.4)
A('amb_day_gusts_leaves', 13.8, 29.3, -28, start=30, fi=0.4, fo=0.4)
A('amb_countryside_birdsong', 28.9, 40.2, -21, start=60, fi=0.3, fo=0.3)
A('amb_lake_lapping', 39.9, 60.2, -19, start=10, fi=0.3, fo=0.4)
A('amb_countryside_birdsong', 39.9, 60.2, -29, start=200, fi=0.3, fo=0.4)
A('amb_countryside_birdsong', 59.9, 88.0, -22, start=320, fi=0.3, fo=0.6)
A('amb_day_gusts_leaves', 59.9, 88.0, -30, start=120, fi=0.3, fo=0.6)
# Act II midday
A('amb_countryside_birdsong', 88.0, 122.2, -23, start=500, fi=0.5, fo=0.3)
A('amb_wind_grass_crickets', 88.0, 122.2, -31, start=20, fi=0.5, fo=0.3)
A('amb_lake_lapping', 121.9, 152.6, -19, start=60, fi=0.3, fo=0.6)
A('amb_lake_wind', 121.9, 152.6, -27, start=5, fi=0.3, fo=0.6)
# Act III golden hour / sunset / mountain
A('amb_sunset_cicadas', 153.0, 168.2, -25, start=10, fi=0.6, fo=0.3)
A('amb_day_gusts_leaves', 153.0, 168.2, -31, start=200, fi=0.6, fo=0.3)
A('amb_mountain_wind', 167.9, 172.2, -21, start=20, fi=0.3, fo=0.3)
A('amb_sunset_cicadas', 171.9, 178.2, -25, start=60, fi=0.3, fo=0.3)
A('amb_high_gusting_wind', 177.9, 187.2, -15, start=20, fi=0.3, fo=0.4, hp=120)
A('amb_mountain_wind', 186.9, 209.2, -20, start=60, fi=0.3, fo=0.4)
A('amb_high_gusting_wind', 208.9, 216.4, -17, start=45, fi=0.3, fo=0.4, hp=120)
# Act IV night
A('amb_night_crickets', 217.0, 300.0, -23, start=5, fi=1.2, fo=2.0)
A('amb_night_treecrickets_wind', 217.0, 300.0, -27, start=5, fi=1.2, fo=2.0)
# the bonfire (lit at 246.79), receding as the camera cranes away in the finale
A('fire_bonfire_close', 246.75, 300.0, -16, start=30, fi=0.15, fo=2.0,
  env=([0, 3.4, 4.0, 9.2, 22.0, 30.0, 38.25, 46.0, 53.3], [0.6, 0.6, 1.0, 1.0, 1.0, 0.9, 0.85, 0.4, 0.2]))
A('fire_bonfire_close2', 246.75, 300.0, -22, start=20, fi=0.15, fo=2.0,
  env=([0, 38.25, 46.0, 53.3], [1.0, 1.0, 0.4, 0.2]))

# ============================================================================= ACT I
# s01 aerial: rushing air past the camera, the Star's twinkle, title shimmer
place(whoosh(6.0, 200, 900, 0.45), 0.2, -24, 0, lp=3000)
place(whoosh(5.0, 300, 1400, 0.6), 7.5, -27, 0, lp=4000)
place(shimmer(3.0, 1760, 14, seed=1), 2.0, -24, rev=0.5)
for t in (4.8, 9.4, 12.5):
    place(shimmer(1.2, 2093, 6, seed=int(t)), t, -32, R.uniform(-.3, .3), rev=0.5)
# s02 crown: the Star catching the sun; leaves; sleeping Pikachu breathing
place(shimmer(2.5, 1760, 16, seed=2), 14.3, -22, rev=0.5)
place(shimmer(2.0, 2349, 10, seed=3), 16.6, -28, rev=0.5)
voice('pikachu/letsgo_sleepy_low', 19.7, -24, 0.05, lp=4000)
# s03 wake: stir, stretch + yawn, look up
place('steps_undergrowth', 23.0, -28, 0.1, 1.2, start=4.9, dur=0.7, fo=0.3)
voice('pikachu/smash_sleepy_yawn', 24.0, -15, 0.0)
voice('pikachu/letsgo_sigh_yawn_low', 25.6, -19, 0.0, rate=1.05)
voice('pikachu/letsgo_pika_question_01', 27.2, -14, 0.0)
place(shimmer(1.4, 1760, 8, seed=4), 27.0, -28, rev=0.5)
# s04 excited: "Pikachu!" - cheek sparks crackle - dash
voice('pikachu/letsgo_pikachu_excited_high', 29.8, -10, 0.05)
place(zap(1.75, 70, seed=1), 30.0, -21, 0.05, rev=0.1, fi=0.05, fo=0.2)
voice('pikachu/letsgo_pika_pika_excited_fast', 30.85, -13, 0.05)
voice('pikachu/pokken_pi_short', 31.9, -12, 0.1)
place(whoosh(0.7, 500, 3500, 0.35), 31.85, -16, 0.3)
steps(32.1, 35.0, 7.5, -24, 0.4, 1.35)
# s05 run through the meadow grass
steps(35.0, 40.0, 7.5, -17, -0.1, 1.35)
place('steps_undergrowth', 35.0, -22, 0, 1.25, start=5.4, dur=5.0, fi=0.3, fo=0.4)          # grass brushing past
place(whoosh(1.2, 400, 2000, 0.5), 37.2, -24, 0.4)
# s06 the lake: Piplup splashes, Sobble giggles
voice('piplup/sv_happy_01', 40.5, -11, -0.25)
for t, s in ((41.58, ('splash_small', 0.49)), (42.33, ('splash_small3', 0.86)), (43.08, ('splash_small2', 0.75)),
             (43.83, ('splash_person_small', 1.05))):
    place(s[0], t - 0.03, -15, -0.25, R.uniform(1.05, 1.2), start=s[1] - 0.03, dur=1.6, fo=0.6, rev=0.12)
voice('piplup/sv_short_01', 42.0, -13, -0.25)
voice('piplup/sv_short_03', 43.5, -13, -0.25)
voice('sobble', 41.9, -15, 0.3, rate=1.25, dur=0.45, fo=0.15)              # giggles
voice('sobble/swsh_cry_standard', 43.1, -16, 0.3, rate=1.35, dur=0.4, fo=0.1)
voice('sobble', 44.6, -16, 0.3, rate=1.3, start=0.2, dur=0.4, fo=0.1)
voice('piplup/sv_special_attack_cry', 46.15, -10, -0.2)                    # the big belly-flop
place(whoosh(1.0, 300, 1500, 0.6), 47.1, -24, -0.2)
place('splash_person_large', 48.17 - 0.06, -6, -0.1, 1.05, start=0.55, dur=4.0, fo=1.5, rev=0.15)
place('splash_small2', 48.48, -16, 0.35, 1.3, start=0.72, dur=1.0, fo=0.4)     # the soaking
for k in range(8):
    place(drop(R.uniform(800, 1500)), 48.6 + k * 0.09 + R.uniform(0, .05), -27, 0.35)
voice('sobble/swsh_variant_04_short_rising', 48.55, -9, 0.35)
voice('sobble/swsh_variant_03_long_sob', 49.3, -9, 0.35)
voice('sobble/swsh_variant_01_whimper', 50.95, -11, 0.35)
voice('sobble/swsh_variant_02_falling_whine', 52.15, -11, 0.35)
for k in range(10):
    place(drop(R.uniform(1100, 1700)), 49.3 + k * 0.38 + R.uniform(0, .1), -31, 0.35)
voice('piplup/sv_sad', 51.6, -17, -0.3)
# s07 Pikachu arrives, Sobble cheers up, hop hop, off they go
steps(53.0, 54.6, 7.0, -20, 0.5, 1.35)
voice('pikachu/letsgo_pika_pika_happy', 54.6, -10, 0.2)
voice('sobble/swsh_cry_standard', 55.7, -12, -0.1, rate=1.1)
voice('piplup/sv_happy_02', 56.1, -13, 0.3)
for t in (56.55, 57.3):
    for p, pt in ((-0.2, 1.4), (0.1, 1.3), (0.3, 1.25)):
        place(R.choice(STEPS), t + 0.32 + R.uniform(0, .03), -21, p, pt)
voice('pikachu/letsgo_pikachu_cheer', 57.7, -11, 0.1)
steps(58.0, 60.0, 8, -22, 0.2, 1.3)
steps(58.1, 60.0, 8, -25, -0.2, 1.4)
# s08 Raboot juggling; Greninja on its rock
for k in range(9):
    t = 60.46 + 0.75 * k
    place('ball_kick_once', t - 0.02, -16, 0.0, R.uniform(1.25, 1.4), start=2.06, dur=0.5, fo=0.2, rev=0.08)
voice('raboot', 61.1, -12, 0.05)
voice('raboot/swsh_variant_02', 64.0, -14, 0.05)
voice('greninja/sv_ambient_call', 66.4, -18, 0.4, rev=0.2)
# s09 the friends arrive; pass, header, pass back
steps(67.0, 68.7, 7, -22, -0.4, 1.35)
steps(67.0, 69.5, 8, -25, -0.6, 1.45)
voice('raboot/swsh_variant_01', 68.7, -13, 0.3)
voice('pikachu/smash_taunt_pika_pika', 68.3, -13, -0.2)
place('ball_kicked', 69.33 - 0.02, -14, 0.3, 1.2, start=2.48, dur=0.6, fo=0.25)
place('ball_kick_once', 70.46 - 0.02, -15, -0.2, 1.6, start=2.06, dur=0.4, fo=0.2)
voice('pikachu/pokken_pi_short', 70.4, -12, -0.2)
place('ball_kick_once', 71.875 - 0.02, -15, 0.3, 1.3, start=2.06, dur=0.5, fo=0.2)
voice('sobble', 71.0, -18, -0.1, rate=1.15)
# s10 Greninja's leap
place('steps_undergrowth', 73.4, -24, 0.4, 0.9, start=5.5, dur=0.4, fo=0.2)
voice('greninja/smash_attack_hup', 73.85, -9, 0.4)
place(whoosh(0.9, 250, 2000, 0.45), 73.9, -12, 0.4)
place(whoosh(0.7, 600, 3000, 0.5), 74.8, -16, 0.0)                         # the flip
place(whoosh(0.5, 2000, 400, 0.6), 75.5, -15, -0.1)
place(thump(55, 0.6, 0.4), 76.0, -8, -0.1)
place(R.choice(STEPS), 76.0, -12, -0.1, 0.8)
place('steps_undergrowth', 76.0, -20, -0.1, 0.8, start=5.55, dur=0.8, fo=0.4)
voice('pikachu/letsgo_pi_surprised', 76.15, -12, -0.4)
voice('raboot/swsh_variant_04', 76.35, -14, 0.4)
voice('greninja/smash_taunt_01', 76.9, -12, 0.0)
# s11 Garchomp thunders in, skids, ROARS; Dragonite glides down
place('rumble_roar', 77.6, 4, 0.5, 1.0, start=5.0, dur=4.6, fi=1.2, fo=1.0, lp=500)
place(filt(noise(4.0, 'pink'), lp=90) * np.linspace(0.2, 1, int(4.0 * SR)) * 3, 77.0, -16, 0.5)
heavy_steps([78.05 + 0.33 * k for k in range(7)], -14, 0.55)
place('steps_undergrowth', 80.15, -14, 0.2, 0.7, start=4.9, dur=0.8, fi=0.02, fo=0.4)        # the skid
place(sweep_bp(noise(0.7, 'pink'), 1800, 300, 1.5), 80.15, -14, 0.2)
voice('piplup/sv_short_02', 80.55, -14, -0.4)
voice('sobble/swsh_variant_04_short_rising', 80.75, -14, -0.2)
voice('garchomp/pokken_roar_intro_01', 81.4, -4, 0.3, rev=0.18)
flaps(78.0, 84.2, 1.3, -24, -0.5, 1.6, env=lambda t: 10 * min(1, (t - 78) / 5.5) - 6)
place(whoosh(2.0, 200, 700, 0.6), 82.5, -22, -0.4)
place(thump(48, 0.5, 0.2), 84.45, -16, -0.4)
voice('dragonite/sv_happy_03_big', 85.25, -10, -0.4)
voice('pikachu/sv_happy_02', 85.5, -14, 0.0)

# ============================================================================= ACT II
# s12 game: Raboot boots it, Piplup heads it
place('ball_kicked2', 88.67 - 0.02, -12, 0.2, 1.1, start=1.81, dur=0.7, fo=0.3)
place(whoosh(1.4, 400, 1800, 0.4), 88.8, -24, 0.0)
place('ball_kick_once', 90.375 - 0.02, -14, -0.3, 1.5, start=2.06, dur=0.4, fo=0.2)
voice('piplup/sv_happy_02', 90.55, -12, -0.3)
voice('raboot/swsh_variant_03', 89.3, -16, 0.4)
# s13 Sobble ducks; Pikachu's tail-whack
place(whoosh(0.5, 800, 2500, 0.6), 92.55, -18, 0.2)
voice('sobble/swsh_variant_04_short_rising', 92.55, -11, 0.2)
place(whoosh(0.8, 300, 2400, 0.55), 93.25, -18, -0.2)                    # spin
place('ball_kicked', 93.79 - 0.02, -11, -0.2, 1.35, start=2.48, dur=0.5, fo=0.2)
place('ball_kick_once', 93.79 - 0.01, -16, -0.2, 2.2, start=2.06, dur=0.25, fo=0.1)    # crisp tail smack
voice('pikachu/stadium_anime_pika_02', 93.95, -11, -0.2)
voice('raboot/swsh_variant_02', 95.0, -14, 0.4)
# s14 Greninja's backflip kick, cheers, Dragonite claps
place(whoosh(1.0, 300, 2600, 0.6), 96.3, -18, 0.0)
place('ball_kicked2', 97.04 - 0.02, -10, 0.0, 1.0, start=1.81, dur=0.8, fo=0.3)
voice('greninja/smash_attack_shout', 96.95, -11, 0.0)
place(whoosh(2.5, 1500, 400, 0.15), 97.1, -20, 0.1)
for i, (n, t, p) in enumerate((('pikachu/pokken_win_cheer_03', 97.75, -0.3), ('piplup/sv_happy_03_big', 98.05, -0.5),
                                ('sobble/swsh_cry_standard', 98.4, -0.2), ('raboot/swsh_variant_01', 98.65, 0.2),
                                ('garchomp/sv_happy_01', 99.0, 0.5), ('greninja/sv_happy_02', 99.35, 0.1))):
    voice(n, t, -13 - (i > 0) * 2, p)
for k in range(10):
    place(clap(), 97.6 + (0.25 + k) / 2.8, -18, 0.5, 0.75, rev=0.1)
# s15 Garchomp wants a turn
place('steps_undergrowth', 101.0, -26, 0.0, 1.0, start=8.8, dur=1.3, fi=0.1, fo=0.5)     # ball rolling in grass
voice('garchomp/pokken_happy', 101.7, -11, 0.0)
voice('garchomp/pokken_laugh', 103.0, -16, 0.0)
voice('garchomp/sv_attack_grunt', 104.2, -15, 0.0)
place('rumble_roar', 104.0, -2, 0, 1.0, start=12, dur=2.5, fi=1.5, fo=0.2, lp=400)
# s16 KICK!
voice('garchomp/pokken_roar_attack_max', 106.05, -6, 0.0)
place('ball_kicked2', 106.46 - 0.02, -4, 0.0, 0.9, start=1.81, dur=1.0, fo=0.4)
place(boom(1.6, 80, 35), 106.46, -6, 0.0)
place(thump(50, 0.6, 0.5), 106.46, -6, 0.0)
place(whoosh(2.1, 500, 4500, 0.2), 106.5, -12, 0.0)
place(sweep_bp(noise(2.0), 3000, 9000, 4) * np.linspace(1, 0, int(2.0 * SR)), 106.6, -24, 0.2)
# s16b the ball smacks the Star off the treetop
place('ball_kicked', 108.54 - 0.02, -9, 0.0, 0.9, start=2.48, dur=0.7, fo=0.3, rev=0.3)
place(bell(1567, 3.0, ((1, 1), (2.41, .7), (3.93, .5), (5.6, .3), (7.3, .2)), decay=1.2), 108.54, -7, 0.1, rev=0.45)
place(bell(2093, 3.0, ((1, 1), (2.6, .6), (4.2, .4)), decay=1.5), 108.56, -10, -0.1, rev=0.45)
place(shimmer(1.8, 1760, 26, seed=9), 108.56, -12, rev=0.45)
place(boom(1.5, 90, 40), 108.54, -14)
place(whoosh(2.3, 3000, 500, 0.3), 108.7, -19, 0.1)
place(thump(70, 0.3, 0.3), 110.33, -26, 0.4)                                 # ball lands far off
# s17 the Star tumbles down through the branches
voice('pikachu/pokken_surprised', 111.5, -10, -0.2)
place('branch_drag', 111.0, -14, 0.0, 1.1, start=3.0, dur=1.7, fi=0.1, fo=0.4)
place(shimmer(1.6, 1760, 10, seed=10), 111.0, -22)
for t, dbv in ((112.6, -11), (114.3, -10), (115.3, -15)):
    place(thump(90, 0.3, 0.6), t, dbv, 0.1)
    place(bell(1975, 1.4, decay=2.5), t, dbv - 6, 0.1, rev=0.35)
    place('steps_undergrowth', t, dbv - 6, 0.1, 0.9, start=5.55, dur=0.6, fo=0.3)
place('branch_drag', 112.6, -16, -0.1, 1.0, start=9.0, dur=1.5, fi=0.05, fo=0.5)
voice('sobble/swsh_variant_04_short_rising', 114.45, -12, -0.4)
voice('garchomp/pokken_sad', 115.2, -14, 0.5)
# s18 the chase: the Star rolls away, everybody runs
place('steps_undergrowth', 116.8, -18, 0.0, 1.3, start=8.0, dur=5.5, fi=0.4, fo=0.3)       # rolling through grass
place(shimmer(5.0, 1760, 22, seed=11), 117.0, -27)
steps(117.0, 122.0, 7.5, -19, -0.3, 1.3)
steps(117.05, 122.0, 6.5, -21, 0.3, 1.15)
steps(117.1, 122.0, 5.5, -23, 0.0, 1.0)
heavy_steps([117.3 + 0.42 * k for k in range(12)], -21, 0.2, 0.8)
voice('pikachu/letsgo_pika_pika_excited_fast', 117.8, -11, -0.2)
voice('raboot/swsh_variant_03', 119.4, -16, 0.3)
voice('piplup/sv_angry', 120.6, -17, 0.4)
# s19 across the beach - PLOP - the light fades
place('steps_sand', 122.0, -20, 0.0, 1.4, start=1.5, dur=1.3, fi=0.1, fo=0.2)
place(whoosh(0.6, 800, 2500, 0.5), 123.2, -20, -0.1)
place('splash_in_water2', 123.79 - 0.05, -7, -0.1, 1.15, start=1.12, dur=2.6, fo=1.0, rev=0.2)
place(drop(500), 123.82, -12, -0.1)
place('underwater_bubbles', 124.0, 2, -0.1, 1.0, start=2.0, dur=2.6, fi=0.2, fo=1.2, lp=2500)
tt = tvec(1.6)
fade = np.sin(2 * np.pi * np.cumsum(1760 * (0.5 ** (tt / 1.6))) / SR) * np.exp(-tt * 1.5)
place(fade, 123.9, -24, -0.1, rev=0.6)
place(shimmer(1.5, 1320, 10, decay=4.0, seed=12), 123.85, -24, rev=0.5)

# s20 shocked faces
voice('pikachu/pokken_surprised', 126.15, -12, -0.1)
voice('sobble/swsh_variant_04_short_rising', 126.45, -14, 0.2)
voice('piplup/sv_short_02', 126.75, -15, 0.3)
voice('garchomp/sv_sad', 128.7, -12, 0.4)
voice('raboot/swsh_variant_04', 129.6, -19, -0.3)
# s21 Sobble cries; Greninja and Piplup dive in
voice('sobble/swsh_variant_03_long_sob', 132.1, -8, 0.0)
voice('sobble/swsh_variant_02_falling_whine', 133.5, -10, 0.0)
for k in range(7):
    place(drop(R.uniform(1100, 1700)), 132.3 + k * 0.4, -29, 0.0)
voice('greninja/smash_attack_shout', 134.05, -12, 0.3)
place(whoosh(0.9, 300, 2000, 0.5), 134.1, -15, 0.2)
voice('piplup/sv_attack_grunt', 134.85, -13, 0.3)
place(whoosh(0.8, 400, 2200, 0.5), 134.9, -18, 0.3)
place('splash_large', 135.04 - 0.4, -6, 0.1, 1.0, start=0.0, dur=4.0, fo=1.5, rev=0.2)
place('splash_person_small', 135.875 - 1.05, -9, 0.2, 1.2, start=0.0, dur=3.0, fo=1.2, rev=0.2)
voice('sobble/swsh_variant_01_whimper', 136.4, -15, -0.3)
place('underwater_bubbles', 136.6, -2, 0.1, 1.0, start=8.0, dur=2.6, fi=0.6, fo=0.5, lp=1800)
# s22 Greninja surfaces holding the Star high - cheers - then silence: it's dark
place('splash_in_water', 140.08 - 1.47, -8, 0.0, 1.0, start=0.0, dur=3.6, fo=1.2, rev=0.2)
place('splash_small3', 140.5 - 0.86, -14, -0.3, 1.0, start=0.0, dur=2.2, fo=0.8)
place('wading', 141.0, -16, 0.0, 1.0, start=5.0, dur=4.9, fi=0.3, fo=0.8)
place('wading_shallow', 141.5, -19, -0.3, 1.1, start=15.0, dur=4.2, fi=0.3, fo=0.8)
voice('greninja/sv_happy_01', 140.9, -12, 0.0)
voice('pikachu/letsgo_pika_pika_cheer', 140.75, -12, 0.4)
voice('raboot/swsh_variant_01', 141.3, -15, 0.5)
voice('sobble/swsh_cry_standard', 141.7, -14, 0.5, rate=1.12)
voice('dragonite/sv_happy_01', 142.2, -16, 0.6)
voice('pikachu/stadium_anime_falling_09', 144.35, -11, 0.4)
voice('sobble/swsh_variant_01_whimper', 145.4, -15, 0.5)
for k in range(12):
    place(drop(R.uniform(700, 1300)), 145.6 + k * 0.12 + R.uniform(0, 0.05), -30, 0.0)        # water dripping off
# s23 Garchomp's apology; Dragonite's comforting pat
voice('garchomp/pokken_sad', 147.5, -10, 0.2)
heavy_steps([147.3, 147.9], -24, -0.2, 0.9)
for k in range(5):
    t = 148.75 + k * 0.7
    place(thump(110, 0.18, 0.5), t, -23, 0.0)
voice('dragonite/sv_ambient_call', 149.2, -13, -0.2)
voice('pikachu/sv_happy_01', 150.9, -18, 0.4)
voice('garchomp/swsh_variant_01', 151.2, -12, 0.2)

# ============================================================================= ACT III
# s24 golden hour: Pikachu tries to recharge the Star
steps(154.2, 155.5, 5, -25, 0.0, 1.35)
voice('pikachu/pokken_strain_effort', 156.25, -10, 0.0)
place(zap(2.8, 90, seed=2), 156.3, -14, 0.0, fi=0.3, fo=0.3)
voice('pikachu/smash_charge_strain', 157.55, -11, 0.0)
place(zap(1.85, 60, seed=3, low=False), 157.1, -17, 0.2, fi=0.1, fo=0.2)
for t, g in ((157.46, -20), (157.71, -16), (158.38, -13)):
    place(shimmer(0.6, 1760, 6, seed=int(t * 10)), t, g, 0.2, rev=0.4)
tt = tvec(1.2)
fizz = np.sin(2 * np.pi * np.cumsum(900 * (0.25 ** (tt / 1.2))) / SR) * np.exp(-tt * 2.5) + 0.3 * zap(1.2, 40, 4, False) * np.exp(-tt * 3)
place(fizz / np.abs(fizz).max(), 159.0, -18, 0.2, rev=0.3)
voice('pikachu/pokken_sad_short', 159.95, -11, 0.0)
voice('sobble/swsh_variant_01_whimper', 160.7, -17, -0.4)
voice('piplup/sv_sad', 161.2, -18, -0.5)
# s25 Dragonite's idea
voice('dragonite/swsh_variant_03', 162.45, -11, 0.0)
voice('dragonite/sv_short_04', 163.5, -12, 0.0)
voice('pikachu/letsgo_pikaaa_rising', 164.8, -12, -0.4)
# s26 Charizard asleep on its far-off peak
snore(168.3, -26, 0.1, 1.2, lp=1500)
snore(170.6, -27, 0.1, 1.2, lp=1500)
# s27 take-off
voice('dragonite/sv_happy_03_big', 172.6, -11, 0.0)
flaps(173.25, 178.2, 1.5, -12, 0.0, 1.5, env=lambda t: -max(0, t - 175.5) * 3)
place(whoosh(1.5, 150, 900, 0.4), 173.6, -14, 0.0)
place('steps_undergrowth', 173.6, -22, 0.0, 0.8, start=4.9, dur=0.8, fo=0.4)
voice('pikachu/pokken_win_cheer_01', 174.0, -12, 0.0)
for n, t, p in (('piplup/sv_happy_01', 174.8, -0.6), ('sobble/swsh_cry_standard', 175.2, -0.3), ('raboot/swsh_variant_02', 175.6, 0.3),
                ('greninja/sv_happy_01', 176.0, 0.6), ('garchomp/sv_happy_01', 176.4, 0.7)):
    voice(n, t, -17, p)
# s28 soaring at sunset
flaps(178.0, 187.0, 1.2, -16, 0.2, 1.5)
place(whoosh(4.0, 150, 1200, 0.5), 178.2, -17, 0.0)
voice('pikachu/heyyou_chatter_high', 179.6, -13, 0.2)
voice('pikachu/letsgo_pikachu_excited_high', 183.4, -13, 0.2)
voice('dragonite/sv_ambient_call', 185.0, -16, 0.2)
# s29 the ledge: Charizard snoring smoke; Dragonite lands softly
for k in range(4):
    snore(187.3 + k * 2.6, -14, 0.25, 1.2)
flaps(187.0, 192.3, 1.4, -15, -0.4, 1.5, env=lambda t: min(0, (t - 191.0) * 3) if t > 191 else (t - 191) * 1.5)
place(thump(50, 0.6, 0.2), 192.25, -16, -0.4)
place('steps_sand', 192.25, -22, -0.4, 0.8, start=1.55, dur=0.5, fo=0.3)
# s30 tiptoe... poke... SNORT
snore(195.2, -14, 0.3, 1.2)
for k in range(6):
    place(R.choice(STEPS), 195.25 + k * 0.4, -30, -0.1, 1.6, lp=3000)
place(thump(300, 0.12, 0.1), 197.98, -20, 0.2)                      # the poke
voice('pikachu/letsgo_pi_tiny', 197.85, -18, 0.0)
place(sweep_bp(noise(0.45, 'pink'), 120, 400, 2), 198.3, -24, 0.3)        # an eye opens (low rumble)
voice('charizard/pokken_surprised_snort', 198.78, -6, 0.3)
voice('charizard/smash_snort_short', 199.15, -9, 0.3)
place(whoosh(0.7, 300, 1200, 0.2), 198.85, -14, 0.25)               # smoke puff
voice('pikachu/smash_whoa_teeter', 198.95, -10, -0.1)
voice('charizard/smash_taunt_growl', 199.8, -12, 0.3, rate=0.95)
# s31 the promise
voice('pikachu/heyyou_low_rising', 202.7, -12, -0.2)
voice('pikachu/stadium_anime_falling_09', 204.6, -15, -0.2)
voice('charizard/pokken_happy_01', 205.9, -10, 0.3)
voice('charizard/smash_victory_rumble', 206.3, -12, 0.3)
voice('pikachu/letsgo_pika_pika_happy', 206.8, -11, -0.2)
place(whoosh(1.3, 120, 700, 0.5), 207.0, -10, 0.3)                  # wings unfurl
place('wings_takeoff2', 207.0, -14, 0.3, 0.7, start=5.4, dur=1.4, fo=0.6)
voice('charizard/pokken_roar_intro_02', 207.7, -6, 0.3, rev=0.25)
voice('dragonite/sv_happy_01', 208.6, -16, -0.4)
# s32 homeward at dusk
flaps(209.0, 216.5, 1.2, -18, -0.3, 1.5)
flaps(209.2, 216.5, 1.0, -19, 0.3, 1.6, start_ph=0.2)
place(whoosh(4.0, 150, 900, 0.5), 209.2, -20, 0.0)
voice('charizard/sv_happy_01', 212.0, -16, 0.3)
voice('pikachu/sv_happy_03_big', 213.2, -15, -0.2)

# ============================================================================= ACT IV
# s33 night; waiting; wingbeats - they're back!
voice('sobble/swsh_variant_01_whimper', 218.6, -21, -0.2)
for k in range(6):
    place(shimmer(0.4, 2637, 2, seed=300 + k), 217.5 + k * 1.4 + R.uniform(0, .6), -38, R.uniform(-.6, .6), rev=0.5)   # fireflies
flaps(220.5, 225.6, 1.4, -14, -0.4, 1.5, env=lambda t: -14 * max(0, (224.5 - t) / 4.0))
flaps(220.7, 226.0, 1.2, -15, 0.3, 1.6, env=lambda t: -14 * max(0, (224.8 - t) / 4.0))
voice('pikachu/pokken_intro_pikachu_02', 222.9, -14, -0.3, rev=0.25)
for n, t, p in (('piplup/sv_happy_03_big', 224.25, -0.5), ('sobble/swsh_cry_standard', 224.6, -0.2),
                ('raboot/swsh_variant_01', 224.95, 0.2), ('garchomp/sv_happy_03_big', 225.3, 0.6), ('greninja/sv_happy_02', 225.65, 0.4)):
    voice(n, t, -15, p)
place(thump(48, 0.5, 0.2), 225.55, -17, -0.3)
place(thump(44, 0.5, 0.2), 226.0, -17, 0.4)
# s34 Charizard's flame relights the Star
voice('charizard/swsh_variant_03', 227.6, -14, 0.4)
place(whoosh(0.8, 200, 800, 0.8), 228.1, -20, 0.4)                    # deep breath in
place('fire_blowlamp_roar', 228.75, -8, 0.2, 0.85, start=12.0, dur=2.6, fi=0.08, fo=0.5, rev=0.15)
place('fire_ignition_petrol', 228.75, -12, 0.2, 1.0, start=2.0, dur=2.5, fi=0.05, fo=0.6)
place(whoosh(2.4, 200, 2500, 0.3), 228.75, -14, 0.1)
place(riser(1.6, 300, 5000), 229.7, -16, 0.0, rev=0.4)
magic_burst(231.29, -4, 1.4, seed=21)
place(whoosh(1.8, 3000, 300, 0.1), 231.3, -14)
voice('pikachu/pokken_surprised', 231.55, -12, -0.2)
voice('sobble/swsh_variant_04_short_rising', 231.8, -14, 0.2)
voice('piplup/sv_short_02', 232.0, -15, -0.4)
voice('pikachu/pokken_win_cheer_02_long', 232.9, -11, -0.2)
voice('sobble/swsh_cry_standard', 233.6, -14, 0.2, rate=1.12)
tt = tvec(10.0)
hum = sum(np.sin(2 * np.pi * f * tt + R.random() * 6) * a for f, a in ((220, .5), (330, .3), (440, .2), (660.5, .1)))
hum *= (0.7 + 0.3 * np.sin(2 * np.pi * 0.35 * tt)) * np.minimum(1, tt / 1.5) * np.minimum(1, (10 - tt) / 2)
place(hum / np.abs(hum).max(), 231.5, -34, 0.0, rev=0.5)               # the Star's warm hum
for k in range(5):
    place(shimmer(1.2, 1760, 6, seed=400 + k), 233.0 + k * 1.6, -30, R.uniform(-.3, .3), rev=0.5)
# s35 warm light on happy faces
voice('sobble/swsh_variant_01_whimper', 237.2, -17, 0.2, rate=1.15)      # happy tears
voice('raboot/swsh_variant_02', 238.6, -18, 0.5)
for k in range(3):
    place(shimmer(1.2, 1760, 6, seed=500 + k), 236.4 + k * 1.6, -30, R.uniform(-.3, .3), rev=0.5)
# s36 Dragonite carries the Star home; the lanterns; the bonfire roars
flaps(241.0, 250.0, 1.5, -15, 0.0, 1.5, env=lambda t: -4 * min(1, max(0, (t - 241) / 5)))
voice('dragonite/sv_happy_01', 241.6, -14, 0.0)
place(riser(4.5, 200, 3000), 241.9, -24, 0.0, rev=0.4)
magic_burst(246.42, -5, 1.6, seed=31)
for k in range(16):                                                      # lanterns blooming one by one
    t = 246.5 + k * 0.073
    place(sweep_bp(noise(0.25, 'pink'), 300, 1200, 2) * np.hanning(int(0.25 * SR)), t, -26, R.uniform(-.8, .8))
    place(bell(R.choice((1760, 1975.5, 2217.5, 2637, 2960)), 1.2, decay=3.0), t, -30, R.uniform(-.8, .8), rev=0.4)
place('fire_ignition_petrol', 246.7, -6, 0.0, 1.0, start=0.0, dur=2.5, fi=0.03, fo=1.4)       # WHOOMP
place(boom(1.5, 70, 40), 246.79, -10)
place(whoosh(1.2, 150, 1200, 0.15), 246.79, -12)
voice('pikachu/letsgo_pikachu_cheer', 247.3, -10, -0.2)
voice('piplup/sv_happy_03_big', 247.8, -15, -0.5)
voice('greninja/sv_happy_03_big', 248.2, -15, 0.5)
voice('sobble/swsh_cry_standard', 248.5, -15, -0.3, rate=1.1)
voice('garchomp/sv_happy_03_big', 248.9, -14, 0.6)
# s37 the whole tree glows; cheering round the bonfire
voice('charizard/pokken_roar_powerup', 250.4, -7, 0.3, rev=0.25)
voice('pikachu/pokken_win_cheer_01', 251.8, -12, -0.1)
voice('raboot/swsh_variant_03', 252.6, -15, 0.2)
voice('dragonite/sv_happy_03_big', 253.2, -14, -0.4)
voice('piplup/sv_happy_01', 253.9, -15, -0.3)
voice('greninja/sv_happy_01', 254.6, -16, 0.5)
# s38 the festival dance
for k in range(int((269.0 - 256.5) / 0.545)):
    t = 256.6 + k * 0.545
    place(R.choice(STEPS), t, -24, R.uniform(-.5, .5), R.uniform(1.0, 1.3))
    place(R.choice(STEPS), t + 0.27, -27, R.uniform(-.5, .5), R.uniform(0.8, 1.1))
voice('pikachu/heyyou_giggle', 257.6, -13, -0.2)
voice('piplup/sv_happy_03_big', 260.25, -13, 0.3)
place(whoosh(0.7, 500, 2000, 0.5), 260.2, -22, 0.3)
voice('garchomp/sv_happy_03_big', 262.6, -14, -0.4)
place(whoosh(1.2, 200, 900, 0.5), 262.4, -22, -0.4)
voice('greninja/smash_taunt_02', 264.75, -13, 0.4)
place(whoosh(0.8, 400, 2400, 0.5), 264.8, -18, 0.4)
voice('pikachu/letsgo_pika_pika_cheer', 265.6, -12, -0.1)
voice('raboot/swsh_variant_02', 266.3, -15, 0.2)
voice('sobble/swsh_cry_standard', 267.3, -16, 0.1, rate=1.15)
voice('charizard/sv_happy_03_big', 268.1, -15, 0.5)
# s39 Charizard sends fire into the sky; fireworks
voice('charizard/smash_taunt_roar', 269.45, -8, 0.0)
place('fire_blowlamp_roar', 269.9, -9, 0.0, 0.8, start=40.0, dur=1.75, fi=0.06, fo=0.5)
place(whoosh(1.7, 200, 3500, 0.3), 269.9, -12, 0.0)
s39 = 269.0
for i in range(5):
    firework(s39 + (39 + i * 12) / 24, s39 + (69 + i * 14) / 24, -2, R.uniform(-.5, .5), 0.25, big=(i == 4))
voice('pikachu/letsgo_pikachu_high_falling', 274.7, -13, -0.2)
voice('dragonite/sv_happy_02', 275.6, -15, 0.4)
# s40 side by side, watching
for i in range(4):
    firework(277 + i * 38 / 24, 277 + (25 + i * 40) / 24, -5, R.uniform(-.4, .4), 0.35)
voice('pikachu/sv_happy_01', 280.4, -17, -0.1)
voice('sobble/swsh_cry_standard', 281.3, -18, 0.05, rate=1.1)
# s41 the finale: crane up and away
for i in range(5):
    firework(285 + (19 + i * 50) / 24, 285 + (47 + i * 52) / 24, -6 - i * 1.0, R.uniform(-.5, .5), 0.45, big=(i == 4))
voice('pikachu/letsgo_pika_pika_happy', 287.5, -22, 0.0, rev=0.3)


# Charizard's tail flame, softly crackling in its close-ups
A('fire_small_cracks', 187.0, 209.0, -27, start=10, fi=0.4, fo=0.4, bus='fx', pan=0.3)
A('fire_small_cracks', 227.0, 236.0, -29, start=50, fi=0.4, fo=0.4, bus='fx', pan=0.4)
# Pikachu breathing softly in its sleep
for k in range(3):
    place(filt(noise(1.1, 'pink'), lp=1500, hp=250) * np.sin(np.pi * np.clip(tvec(1.1) / 1.1, 0, 1)) ** 2, 19.8 + k * 1.15 + 1.8 * (k > 0), -38, 0.05)

# ============================================================================= render
def outdoor_ir(sec, seed):
    r = np.random.default_rng(seed)
    n = int(sec * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2))
    for c in range(2):
        x = r.standard_normal(n) * np.exp(-6.91 * t / sec)
        x = sosfilt(butter(2, 4500, 'low', fs=SR, output='sos'), x)
        x *= np.clip(t / 0.02, 0, 1)
        for k in range(6):
            ir[int(r.uniform(0.01, 0.09) * SR), c] += r.uniform(0.3, 0.7)
        ir[:, c] += x * 0.6
    return ir / np.sqrt((ir ** 2).sum(axis=0, keepdims=True))


IR = outdoor_ir(1.4, 2)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
fade = np.ones(N)
end = int(DUR * SR)
fade[end - int(1.5 * SR):end] = np.linspace(1, 0, int(1.5 * SR)) ** 1.5
fade[end:] = 0
for k in BUS:
    wet = np.stack([fftconvolve(SEND[k][:, c], IR[:, c])[:N] for c in range(2)], axis=1)
    wet *= 0.8
    y = (BUS[k] + wet) * fade[:, None]
    y = y[:end]
    sf.write(os.path.join(HERE, 'out', f'sfx_{k}.wav'), y.astype(np.float32), SR, subtype='FLOAT')
    print(k, 'peak', round(float(np.abs(y).max()), 3), 'rms', round(float(np.sqrt(np.mean(y ** 2))), 4))
