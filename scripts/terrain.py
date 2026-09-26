# Island heightfield.  Pure numpy so both the world builder and the animation
# code (ground snapping) can use exactly the same surface.
import numpy as np

SEA = -1.6
LAKE_LEVEL = -0.55
LAKE_C = np.array([-48.0, -14.0])
LAKE_R = 24.0
TREE_C = np.array([0.0, 34.0])          # giant festival tree
CLIFF_C = np.array([27.0, 24.0])        # Greninja's rock outcrop
FALLS_C = np.array([-80.0, -8.0])       # waterfall cliff (west of lake)
PEAK_C = np.array([135.0, 175.0])       # Charizard's peak
PEAK_TOP = np.array([128.0, 165.0])     # ledge where Charizard sleeps


def _hash(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + seed * 144269504) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return h


def _grad(ix, iy, seed):
    h = _hash(ix, iy, seed)
    a = (h & 0xFFFF) / 65535.0 * 2 * np.pi
    return np.cos(a), np.sin(a)


def perlin(x, y, seed=0):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    fx = x - x0
    fy = y - y0

    def dot(ix, iy, dx, dy):
        gx, gy = _grad(ix, iy, seed)
        return gx * dx + gy * dy

    n00 = dot(x0, y0, fx, fy)
    n10 = dot(x0 + 1, y0, fx - 1, fy)
    n01 = dot(x0, y0 + 1, fx, fy - 1)
    n11 = dot(x0 + 1, y0 + 1, fx - 1, fy - 1)
    u = fx * fx * fx * (fx * (fx * 6 - 15) + 10)
    v = fy * fy * fy * (fy * (fy * 6 - 15) + 10)
    return (n00 * (1 - u) + n10 * u) * (1 - v) + (n01 * (1 - u) + n11 * u) * v


def fbm(x, y, octaves=5, seed=0, lac=2.0, gain=0.5):
    s = 0.0
    a = 1.0
    f = 1.0
    for i in range(octaves):
        s = s + a * perlin(x * f, y * f, seed + i * 17)
        f *= lac
        a *= gain
    return s


def ridged(x, y, octaves=5, seed=0):
    s = 0.0
    a = 1.0
    f = 1.0
    w = 1.0
    for i in range(octaves):
        n = 1.0 - np.abs(perlin(x * f, y * f, seed + i * 31))
        n = n * n * w
        w = np.clip(n * 2, 0, 1)
        s = s + a * n
        f *= 2.1
        a *= 0.5
    return s


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def height(x, y):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    r = np.sqrt(x * x + y * y)
    # gentle rolling land
    h = fbm(x / 90.0, y / 90.0, 4, seed=3) * 6.0 + 1.5
    # mountain ring (higher to the north-east)
    ang_bias = 0.6 + 0.4 * np.clip((x + y) / (np.abs(x) + np.abs(y) + 1e-6), -1, 1)
    ring = smoothstep(95, 230, r) * (1 - smoothstep(330, 420, r))
    mnt = (25 + 95 * ridged(x / 110.0, y / 110.0, 5, seed=7)) * ang_bias
    h = h + ring * mnt
    # Charizard's peak
    dp = np.hypot(x - PEAK_C[0], y - PEAK_C[1])
    h = h + 85 * np.exp(-(dp / 48.0) ** 2) + 6 * ridged(x / 25, y / 25, 3, seed=11) * np.exp(-(dp / 60) ** 2)
    # flat rocky ledge near the top where Charizard sleeps
    dl = np.hypot(x - PEAK_TOP[0], y - PEAK_TOP[1])
    ledge_h = height_ledge()
    wl = 1 - smoothstep(7, 14, dl)
    h = h * (1 - wl) + (ledge_h + 0.25 * fbm(x / 3, y / 3, 2, seed=5)) * wl
    # central meadow: flatten
    wm = 1 - smoothstep(38, 70, np.hypot(x - 2, y - 5))
    meadow = 0.25 * fbm(x / 14.0, y / 14.0, 3, seed=1)
    h = h * (1 - wm) + meadow * wm
    # festival tree hill
    dt = np.hypot(x - TREE_C[0], y - TREE_C[1])
    h = h + 2.2 * np.exp(-(dt / 13.0) ** 2)
    # Greninja's outcrop (steep rock pillar with a flat top)
    dc = np.hypot((x - CLIFF_C[0]) * 1.0, (y - CLIFF_C[1]) * 1.4)
    crag = 1.6 * perlin(x / 3.0, y / 3.0, 9) + 0.6 * perlin(x / 1.1, y / 1.1, 19)
    cliff = (7.5 + 0.8 * perlin(x / 2.5, y / 2.5, 29)) * (1 - smoothstep(3.8, 6.2, dc + crag))
    h = np.maximum(h, h * 0 + cliff + 0.2 * fbm(x / 2, y / 2, 2, seed=4))
    # waterfall plateau west of the lake with a sharp east-facing edge
    ex = x - FALLS_C[0] + 3.5 * perlin(y / 9.0, 0.5, 21)
    plateau = 17.0 * (1 - smoothstep(-4.0, 1.0, ex)) * (1 - smoothstep(35, 70, np.abs(y - FALLS_C[1])))
    h = np.maximum(h, plateau + (fbm(x / 20, y / 20, 3, seed=8) * 3 + 2) * (1 - smoothstep(-6.0, 0.0, ex)) * (1 - smoothstep(35, 70, np.abs(y - FALLS_C[1]))))
    # river channel on the plateau leading to the falls edge
    dr = np.abs(y - FALLS_C[1] - 1.5 * np.sin(x / 9.0))
    chan = (1 - smoothstep(2.0, 5.0, dr)) * (1 - smoothstep(-2.0, 0.5, ex)) * smoothstep(-60, -5, ex)
    h = h - chan * 3.5
    # lake bowl
    dlk = np.hypot((x - LAKE_C[0]) * 1.0, (y - LAKE_C[1]) * 1.25) + 3.0 * perlin(x / 12, y / 12, 13)
    bowl = LAKE_LEVEL - 2.8 * (1 - smoothstep(0, LAKE_R, dlk))
    wlk = 1 - smoothstep(LAKE_R - 3, LAKE_R + 7, dlk)
    h = h * (1 - wlk) + np.minimum(h, bowl + 0.4) * wlk
    # plunge pool under the falls connects to the lake
    dpp = np.hypot(x - (FALLS_C[0] + 4.5), (y - FALLS_C[1]) * 0.7)
    h = np.minimum(h, LAKE_LEVEL - 2.5 + (dpp / 6.0) ** 2 * 10)
    # outflow channel from the plunge pool into the lake
    ax, ay = FALLS_C[0] + 4.5, FALLS_C[1]
    bx, by = LAKE_C[0], LAKE_C[1]
    t = np.clip(((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2), 0, 1)
    dseg = np.hypot(x - (ax + t * (bx - ax)), y - (ay + t * (by - ay)))
    h = np.minimum(h, LAKE_LEVEL - 1.3 + 500 * smoothstep(4.0, 12.0, dseg) + 500 * (1 - smoothstep(-8, -4, x - ax)))
    # island edge -> beach -> sea
    edge = smoothstep(360, 430, r + 25 * perlin(x / 60, y / 60, 17))
    h = h * (1 - edge) + (SEA - 6) * edge
    return h


_LEDGE = [None]


def height_ledge():
    if _LEDGE[0] is None:
        x, y = PEAK_TOP
        dp = np.hypot(x - PEAK_C[0], y - PEAK_C[1])
        r = np.hypot(x, y)
        base = fbm(x / 90.0, y / 90.0, 4, seed=3) * 6.0 + 1.5
        ang_bias = 0.6 + 0.4 * np.clip((x + y) / (abs(x) + abs(y)), -1, 1)
        ring = smoothstep(95, 230, r) * (1 - smoothstep(330, 420, r))
        mnt = (25 + 95 * ridged(x / 110.0, y / 110.0, 5, seed=7)) * ang_bias
        _LEDGE[0] = float(base + ring * mnt + 85 * np.exp(-(dp / 48.0) ** 2) - 4.0)
    return _LEDGE[0]


def normal_z(x, y, e=0.3):
    hx = (height(x + e, y) - height(x - e, y)) / (2 * e)
    hy = (height(x, y + e) - height(x, y - e)) / (2 * e)
    return 1.0 / np.sqrt(1 + hx * hx + hy * hy)
