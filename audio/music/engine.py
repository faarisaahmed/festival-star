# Tiny film-scoring engine: notes in absolute seconds -> one MIDI file per instrument
# -> fluidsynth stems -> mix (pan, reverb, master).
import math, os, random, re, subprocess
import mido
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
SF2 = os.path.join(ROOT, '..', 'sf2', 'MuseScore_General.sf2')
SR = 48000
TPS = 1920          # MIDI ticks per second (tempo 120 bpm, 960 tpb)

# name: (bank, program, pan -1..1, gain dB, reverb send, drum)
INSTR = {
    'vln1':   (21, 49, -0.45, 5, 0.30, False),   # Violins Slow Expr.
    'vln1f':  (21, 48, -0.45, 4, 0.26, False),   # Violins Fast Expr.
    'vln2':   (26, 49, -0.20, -1, 0.30, False),
    'vln2f':  (26, 48, -0.20, -1, 0.26, False),
    'vla':    (31, 49, 0.12, -1, 0.30, False),
    'vlaf':   (31, 48, 0.12, -1, 0.26, False),
    'vc':     (41, 49, 0.32, 0, 0.28, False),
    'vcf':    (41, 48, 0.32, 0, 0.24, False),
    'cb':     (51, 49, 0.45, -4, 0.24, False),
    'trem':   (17, 44, 0.0, -2, 0.30, False),    # Strings Trem Expr.
    'pizz':   (0, 45, 0.15, -9, 0.26, False),
    'vlnpizz': (20, 45, -0.35, -4, 0.26, False),
    'solovn': (18, 40, -0.15, 0, 0.30, False),   # Slow Violin Expr.
    'fl':     (17, 73, -0.10, 0, 0.30, False),
    'picc':   (17, 72, -0.05, -4, 0.30, False),
    'ob':     (17, 68, 0.05, 0, 0.30, False),
    'cl':     (17, 71, -0.25, 2, 0.30, False),
    'bsn':    (17, 70, 0.20, -4, 0.26, False),
    'hn':     (17, 60, -0.30, -7, 0.36, False),
    'tpt':    (17, 56, 0.10, 2, 0.32, False),
    'tbn':    (17, 57, 0.35, -7, 0.32, False),
    'tuba':   (17, 58, 0.40, -4, 0.28, False),
    'timp':   (0, 47, 0.0, 0, 0.30, False),
    'harp':   (0, 46, -0.55, -8, 0.32, False),
    'cel':    (0, 8, 0.35, 0, 0.36, False),
    'glock':  (0, 9, 0.40, -3, 0.36, False),
    'xylo':   (0, 13, 0.25, -3, 0.24, False),
    'marimba': (0, 12, -0.30, 0, 0.24, False),
    'bells':  (0, 14, 0.30, -4, 0.40, False),
    'piano':  (8, 0, 0.0, 3, 0.30, False),       # Mellow Grand
    'choir':  (17, 52, 0.0, -3, 0.40, False),
    'oohs':   (17, 53, 0.0, -3, 0.40, False),
    'shaku':  (17, 77, -0.15, 0, 0.36, False),
    'koto':   (0, 107, 0.25, 0, 0.30, False),
    'taiko':  (0, 116, 0.0, 0, 0.26, False),
    'fiddle': (17, 110, -0.25, 8, 0.26, False),
    'accord': (18, 21, 0.25, -4, 0.24, False),
    'pad':    (17, 89, 0.0, -12, 0.40, False),    # Warm Pad
    'perc':   (128, 48, 0.0, 0, 0.26, True),     # Orchestra kit
    'kit':    (128, 0, 0.0, 0, 0.18, True),      # standard kit (tambourine etc.)
}
SUSTAIN = {'vln1', 'vln2', 'vla', 'vc', 'cb', 'trem', 'solovn', 'fl', 'picc', 'ob', 'cl', 'bsn', 'hn',
           'tpt', 'tbn', 'tuba', 'choir', 'oohs', 'shaku', 'fiddle', 'accord', 'pad', 'vln1f', 'vln2f', 'vlaf', 'vcf'}


# ---------------------------------------------------------------------------
# real sampled instruments (Virtual Playing Orchestra 3 / Salamander piano) played by sfizz
VPO = os.path.join(ROOT, '..', 'vpo', 'Virtual-Playing-Orchestra3')
SFIZZ = os.path.join(ROOT, '..', 'tools', 'sfizz', 'build', 'library', 'bin', 'sfizz_render')
_pg = sorted(__import__('glob').glob(os.path.join(ROOT, '..', 'piano', '**', '*.sfz'), recursive=True))
PIANO_SFZ = next((p for p in _pg if 'V3' in os.path.basename(p) and 'Accurate' in p), _pg[0] if _pg else None)
SFZ = {
    'vln1': 'Strings/1st-violin-SEC-PERF.sfz', 'vln1f': 'Strings/1st-violin-SEC-PERF.sfz',
    'vln2': 'Strings/2nd-violin-SEC-PERF.sfz', 'vln2f': 'Strings/2nd-violin-SEC-PERF.sfz',
    'vla': 'Strings/viola-SEC-PERF.sfz', 'vlaf': 'Strings/viola-SEC-PERF.sfz',
    'vc': 'Strings/cello-SEC-PERF.sfz', 'vcf': 'Strings/cello-SEC-PERF.sfz',
    'cb': 'Strings/bass-SEC-PERF.sfz', 'trem': 'Strings/all-strings-SEC-PERF-tremolo.sfz',
    'pizz': 'Strings/all-strings-SEC-pizzicato.sfz', 'vlnpizz': 'Strings/1st-violin-SEC-pizzicato.sfz',
    'solovn': 'Strings/1st-violin-SOLO-PERF.sfz', 'fiddle': 'Strings/1st-violin-SOLO-PERF.sfz',
    'harp': 'Strings/harp-sustain.sfz',
    'fl': 'Woodwinds/flute-SOLO-PERF.sfz', 'picc': 'Woodwinds/piccolo-SOLO-PERF.sfz',
    'ob': 'Woodwinds/oboe-SOLO-PERF.sfz', 'cl': 'Woodwinds/clarinet-SOLO-PERF.sfz',
    'bsn': 'Woodwinds/bassoon-SOLO-PERF.sfz', 'shaku': 'Woodwinds/alto-flute-SOLO-PERF.sfz',
    'hn': 'Brass/french-horn-SEC-PERF.sfz', 'tpt': 'Brass/trumpet-SEC-PERF.sfz', 'tbn': 'Brass/trombone-SEC-PERF.sfz',
    'btbn': 'Brass/bass-trombone-SOLO-PERF.sfz', 'tuba': 'Brass/tuba-SOLO-PERF.sfz',
    'timp': 'Percussion/timpani-hit.sfz', 'timproll': 'Percussion/timpani-roll.sfz',
    'cym': 'Percussion/cymbals.sfz', 'bdrum': 'Percussion/bassdrum-snare-cymbals.sfz',
    'snare': 'Percussion/bassdrum-snare-cymbals.sfz',
    'cel': 'Keys/celesta.sfz', 'glock': 'Percussion/glockenspiel.sfz', 'xylo': 'Percussion/xylophone.sfz',
    'bells': 'Percussion/tubular-bells.sfz', 'choir': 'Vocals/choir-MIXED-PERF.sfz', 'oohs': 'Vocals/choir-FEMALE-PERF.sfz',
}
if PIANO_SFZ:
    SFZ['piano'] = PIANO_SFZ
# dB range of the mod wheel (cc1) in each Performance patch
CC1_RANGE = {'Strings': 34, 'Woodwinds': 29, 'Brass': 24, 'Vocals': 24}
INSTR.update({
    'btbn': (0, 0, 0.40, -2, 0.30, False), 'timproll': (0, 0, 0.0, 0, 0.30, False),
    'cym': (0, 0, 0.10, -2, 0.36, False), 'bdrum': (0, 0, 0.0, 0, 0.30, False), 'snare': (0, 0, -0.1, -4, 0.26, False),
})
SUSTAIN |= {'btbn', 'timproll'}
# continuous slides (true glissando) are played on their own channel with a wide bend range
GLIDE = {'vln1': 'gl_vln', 'vln1f': 'gl_vln', 'vln2': 'gl_vln2', 'vln2f': 'gl_vln2', 'vla': 'gl_vla', 'vlaf': 'gl_vla',
         'vc': 'gl_vc', 'vcf': 'gl_vc', 'fl': 'gl_fl', 'picc': 'gl_picc', 'cl': 'gl_cl', 'ob': 'gl_ob', 'bsn': 'gl_bsn',
         'shaku': 'gl_shaku', 'tbn': 'gl_tbn', 'hn': 'gl_hn', 'solovn': 'gl_solovn', 'trem': 'gl_trem'}
GLIDE_RANGE = 2400   # cents
for _src, _g in GLIDE.items():
    for _k in ('a', 'b'):
        INSTR[_g + _k] = INSTR[_src]
        SFZ[_g + _k] = ('bend', SFZ[_src])
        SUSTAIN.add(_g + _k)
PLUCK = {'harp', 'cel', 'glock', 'xylo', 'marimba', 'koto', 'pizz', 'vlnpizz', 'bells', 'piano'}


def sfz_path(ins):
    v = SFZ[ins]
    if isinstance(v, tuple):          # wrapper with a wide pitch-bend range
        orig = os.path.join(VPO, v[1])
        w = os.path.join(os.path.dirname(orig), '_bend_' + os.path.basename(orig))
        if not os.path.exists(w):
            open(w, 'w').write(f'<global> bend_up={GLIDE_RANGE} bend_down=-{GLIDE_RANGE}\n#include "{os.path.basename(orig)}"\n')
        return w
    if ins == 'timproll':             # make the roll respond to cc1 for real crescendos
        orig = os.path.join(VPO, v)
        w = os.path.join(os.path.dirname(orig), '_cc_' + os.path.basename(orig))
        if not os.path.exists(w):
            open(w, 'w').write(f'<global> amplitude_oncc1=100\n#include "{os.path.basename(orig)}"\n')
        return w
    return v if os.path.isabs(v) else os.path.join(VPO, v)


_RANGE = {}


def sfz_range(path):
    """lowest / highest playable MIDI note of an sfz (follows #include)"""
    if path in _RANGE:
        return _RANGE[path]
    keys = []

    def nn(x):
        x = x.strip().lower()
        if x.lstrip('-').isdigit():
            return int(x)
        m = re.fullmatch(r'([a-g])([#b]?)(-?\d)', x)
        if not m:
            return None
        return NOTE[m.group(1).upper()] + {'#': 1, 'b': -1, '': 0}[m.group(2)] + 12 * (int(m.group(3)) + 1)

    def walk(p):
        txt = open(p, errors='ignore').read()
        txt = re.sub(r'//.*', '', txt)
        for inc in re.findall(r'#include\s+"([^"]+)"', txt):
            walk(os.path.join(os.path.dirname(p), inc.replace('\\', '/')))
        for k, v in re.findall(r'\b(lokey|hikey|key)=(\S+)', txt):
            n = nn(v)
            if n is not None and 0 <= n <= 127:
                keys.append(n)
    walk(path)
    _RANGE[path] = (min(keys), max(keys)) if keys else (0, 127)
    return _RANGE[path]


def cc1_of(ins, v):
    """map my expression value (fluidsynth CC11 law) to the patch's cc1 dB range"""
    v = max(1, v)
    db = 40 * math.log10(v / 127)
    sec = os.path.dirname(SFZ[ins][1] if isinstance(SFZ[ins], tuple) else SFZ[ins]).split('/')[-1]
    rng = CC1_RANGE.get(sec, 30)
    return int(max(0, min(127, round(127 + 127 / rng * db))))

NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def P(s):
    """'C#4' -> midi; ints pass through"""
    if isinstance(s, int):
        return s
    if s.isdigit():
        return int(s)
    m = re.fullmatch(r'([A-G])([#b]*)(-?\d)', s)
    n = NOTE[m.group(1)] + m.group(2).count('#') - m.group(2).count('b')
    return n + 12 * (int(m.group(3)) + 1)


QUAL = {
    '': (0, 4, 7), 'm': (0, 3, 7), '7': (0, 4, 7, 10), 'maj7': (0, 4, 7, 11), 'm7': (0, 3, 7, 10),
    'sus4': (0, 5, 7), 'sus2': (0, 2, 7), 'add9': (0, 4, 7, 14), 'madd9': (0, 3, 7, 14), 'dim': (0, 3, 6),
    'dim7': (0, 3, 6, 9), 'aug': (0, 4, 8), '6': (0, 4, 7, 9), 'm6': (0, 3, 7, 9), '9': (0, 4, 7, 10, 14),
    'maj9': (0, 4, 7, 11, 14), 'm9': (0, 3, 7, 10, 14), '7sus4': (0, 5, 7, 10), 'm7b5': (0, 3, 6, 10),
    '5': (0, 7), '6/9': (0, 4, 7, 9, 14), 'maj7#11': (0, 4, 7, 11, 18),
}


def chord(sym):
    """'F#m7/C#' -> (root pc, [pcs], bass pc)"""
    s, _, b = sym.partition('/')
    m = re.fullmatch(r'([A-G][#b]?)(.*)', s)
    r = NOTE[m.group(1)[0]] + m.group(1)[1:].count('#') - m.group(1)[1:].count('b')
    iv = QUAL[m.group(2)]
    bass = r
    if b:
        bass = NOTE[b[0]] + b[1:].count('#') - b[1:].count('b')
    return r % 12, [(r + i) % 12 for i in iv], bass % 12


def voicing(sym, lo=55, hi=79, n=4, prev=None):
    """close-ish voicing of a chord within [lo,hi], voice-led to prev"""
    r, pcs, _ = chord(sym)
    cands = sorted({p for p in range(lo, hi + 1) if p % 12 in pcs})
    best, bs = None, 1e9
    import itertools
    for combo in itertools.combinations(cands, n):
        got = {c % 12 for c in combo}
        need = set(pcs[:3]) if len(pcs) >= 3 else set(pcs)
        if not need <= got:
            continue
        spread = combo[-1] - combo[0]
        if spread > 19:
            continue
        cost = 0.0
        if prev:
            cost += sum(abs(a - b) for a, b in zip(combo, prev))
        else:
            cost += abs(sum(combo) / n - (lo + hi) / 2) * 0.5
        cost += 0.15 * spread
        if cost < bs:
            best, bs = combo, cost
    return list(best)


def bass_of(sym, lo=36, hi=50):
    _, _, b = chord(sym)
    for p in range(lo, hi + 1):
        if p % 12 == b:
            return p
    return lo


class Sec:
    """a tempo grid anchored at absolute time t0"""

    def __init__(self, t0, bpm, meter=4):
        self.t0, self.bpm, self.meter = t0, bpm, meter
        self.spb = 60.0 / bpm

    def t(self, bar, beat=0.0):
        return self.t0 + (bar * self.meter + beat) * self.spb

    def d(self, beats):
        return beats * self.spb


class Score:
    def __init__(self, seed=7):
        self.notes = {k: [] for k in INSTR}
        self.ccs = {k: [] for k in INSTR}
        self.bends = {k: [] for k in INSTR}
        self.rng = random.Random(seed)
        for k in INSTR:
            self.notes.setdefault(k, [])
            self.ccs.setdefault(k, [])
            self.bends.setdefault(k, [])

    # --- primitives -----------------------------------------------------
    def n(self, ins, t, dur, pitch, vel=80, human=True):
        if t is None:
            return
        p = P(pitch)
        if ins == 'perc' and p in (49, 57, 52, 55):
            ins, p = 'cym', {49: P('F#4'), 57: P('C#4'), 52: P('G#4'), 55: P('A#4')}[p]
        elif ins == 'perc' and p in (35, 36):
            ins, p = 'bdrum', P('D2')
        elif ins == 'tbn' and p < 40:
            ins = 'btbn'
        if human and ins not in SUSTAIN:
            t += self.rng.uniform(-0.006, 0.010)
            vel += self.rng.randint(-5, 5)
        elif human:
            t += self.rng.uniform(-0.004, 0.008)
            vel += self.rng.randint(-3, 3)
        self.notes[ins].append((max(0.0, t), max(0.03, dur), p, int(max(1, min(127, vel)))))

    def cc(self, ins, t0, t1, v0, v1, num=(11, 2), shape='lin', step=0.03):
        """expression ramp (CC11 + CC2 for the Expr. presets)"""
        nums = num if isinstance(num, tuple) else (num,)
        k = max(1, int((t1 - t0) / step))
        for i in range(k + 1):
            u = i / k
            if shape == 'exp':
                u = u * u
            elif shape == 'log':
                u = 1 - (1 - u) ** 2
            elif shape == 's':
                u = u * u * (3 - 2 * u)
            v = int(round(v0 + (v1 - v0) * u))
            for c in nums:
                self.ccs[ins].append((t0 + (t1 - t0) * i / k, c, max(0, min(127, v))))

    def ccset(self, ins, t, v, num=(11, 2)):
        for c in (num if isinstance(num, tuple) else (num,)):
            self.ccs[ins].append((t, c, v))

    def bend(self, ins, t0, t1, c0, c1, step=0.01):
        """pitch bend in cents (range +-200)"""
        k = max(1, int((t1 - t0) / step))
        for i in range(k + 1):
            u = i / k
            c = c0 + (c1 - c0) * u
            self.bends[ins].append((t0 + (t1 - t0) * u, int(max(-8192, min(8191, c / 200 * 8192)))))

    # --- phrases ----------------------------------------------------------
    def mel(self, ins, sec, bar, text, vel=80, legato=1.0, oct=0, beat=0.0, accent=None):
        """'D5:1.5 E5:.5 r:1 F#5+A5:2 ...' durations in beats; '~' ties (legato overlap)"""
        pos = bar * sec.meter + beat
        out = []
        for tok in text.split():
            p, _, d = tok.partition(':')
            d = float(eval(d)) if d else 1.0
            v = vel
            if p.endswith('!'):
                p, v = p[:-1], vel + 14
            if p.endswith('.'):
                p, lg = p[:-1], 0.45
            else:
                lg = legato
            if p not in ('r', '-'):
                for q in p.split('+'):
                    pp = P(q) + 12 * oct
                    t = sec.t0 + pos * sec.spb
                    self.n(ins, t, d * sec.spb * lg, pp, v)
                    out.append((t, pp))
            pos += d
        return pos

    def pad(self, ins_list, sec, prog, vel=64, lo=55, hi=79, n=4, beats=None):
        """prog: list of (bar, beat, beats, chord) or chord strings one per bar; spreads voices over ins_list"""
        prev = None
        for item in prog:
            bar, bt, ln, sym = item
            v = voicing(sym, lo, hi, n, prev)
            prev = v
            t = sec.t(bar, bt)
            for i, p in enumerate(v):
                ins = ins_list[min(i, len(ins_list) - 1)] if isinstance(ins_list, list) else ins_list
                self.n(ins, t, sec.d(ln) * 1.02, p, vel)

    def bassline(self, ins, sec, prog, vel=70, lo=36, hi=50, pattern=None, oct_double=None):
        for bar, bt, ln, sym in prog:
            p = bass_of(sym, lo, hi)
            if pattern is None:
                self.n(ins, sec.t(bar, bt), sec.d(ln) * 0.98, p, vel)
                if oct_double:
                    self.n(oct_double, sec.t(bar, bt), sec.d(ln) * 0.98, p - 12 if p - 12 >= 28 else p, vel - 6)
            else:
                for off, dd, dv in pattern:
                    if off < ln:
                        self.n(ins, sec.t(bar, bt + off), sec.d(dd), p, vel + dv)

    def arp(self, ins, sec, prog, step=0.5, vel=60, lo=50, hi=86, shape='updown', span=None):
        """broken-chord figuration over each (bar,beat,beats,chord)"""
        for bar, bt, ln, sym in prog:
            r, pcs, b = chord(sym)
            ps = [p for p in range(lo, hi + 1) if p % 12 in pcs]
            if span:
                ps = ps[:span]
            seq = ps + ps[-2:0:-1] if shape == 'updown' else ps
            k = int(round(ln / step))
            for i in range(k):
                p = seq[i % len(seq)]
                acc = 8 if i == 0 else 0
                self.n(ins, sec.t(bar, bt + i * step), sec.d(step) * 2.2, p, vel + acc)

    def gliss(self, ins, t0, t1, p0, p1, vel=60, scale=None, dur_mult=None):
        """glissando from p0 to p1 between t0 and t1.
        plucked/struck instruments: an even sweep of scale notes that all ring on;
        bowed/blown instruments: one continuous slide (pitch bend), like a real glissando."""
        p0, p1 = P(p0), P(p1)
        if ins in PLUCK:
            sc = list(range(12)) if scale == 'chrom' else (scale or [0, 2, 4, 5, 7, 9, 11])
            if scale == 'chrom':
                sc = [0, 2, 4, 5, 7, 9, 11]          # a chromatic smear on a harp/mallet is a diatonic sweep
            root = 2 if scale is None else 0
            ps = [p for p in range(min(p0, p1), max(p0, p1) + 1) if (p - root) % 12 in sc]
            if p1 < p0:
                ps = ps[::-1]
            d = max(0.05, t1 - t0)
            cap = int(d * 16) + 1                    # never faster than ~16 notes a second
            if len(ps) > cap:
                idx = sorted({round(i * (len(ps) - 1) / (cap - 1)) for i in range(cap)})
                ps = [ps[i] for i in idx]
            k = len(ps)
            for i, p in enumerate(ps):
                u = i / max(1, k - 1)
                t = t0 + d * (0.85 * u + 0.15 * u * u)     # very slight acceleration, like a real sweep
                v = vel - 8 + int(14 * math.sin(math.pi * min(1, u * 1.15)))
                ring = 2.2 if ins in ('harp', 'cel', 'glock', 'bells', 'piano') else 0.6
                self.n(ins, t, ring, p, v, human=False)
            return
        self.slide(ins, t0, t1, p0, p1, vel)

    def slide(self, ins, t0, t1, p0, p1, vel=80, hold=0.12):
        """continuous glissando on a dedicated channel (one bowed/blown note, bent smoothly)"""
        g = GLIDE.get(ins)
        if g is None:
            return
        busy = getattr(self, '_glbusy', {})
        self._glbusy = busy
        ch = g + 'a' if busy.get(g + 'a', -1) < t0 - 0.05 else g + 'b'
        c = int(round((p0 + p1) / 2))
        span = max(abs(p0 - c), abs(p1 - c)) * 100
        if span > GLIDE_RANGE:
            c = p1 - 24 if p1 > p0 else p1 + 24
        lead = 0.08                                  # let the bow/breath speak before the slide
        self.bends[ch].append((t0 - lead - 0.02, int(max(-8192, min(8191, (p0 - c) * 100 / GLIDE_RANGE * 8192)))))
        self.n(ch, t0 - lead, (t1 - t0) + lead + hold, c, min(118, vel + 10), human=False)
        k = max(2, int((t1 - t0) / 0.008))
        for i in range(k + 1):
            u = i / k
            e = u * u * (3 - 2 * u)                  # ease in / ease out
            cents = ((p0 - c) + (p1 - p0) * e) * 100
            self.bends[ch].append((t0 + (t1 - t0) * u, int(max(-8192, min(8191, cents / GLIDE_RANGE * 8192)))))
        # gentle swell through the slide, settling at the end
        self.cc(ch, t0 - lead, t0 + (t1 - t0) * 0.7, 70, 112, shape='s')
        self.cc(ch, t0 + (t1 - t0) * 0.7, t1 + hold, 112, 80, shape='s')
        busy[ch] = t1 + hold + 1.0

    def roll(self, ins, t0, t1, pitch, v0=30, v1=100, rate=14):
        """a real roll: looped timpani roll / suspended-cymbal swell / snare roll samples"""
        L = t1 - t0
        if ins == 'timp':
            self.n('timproll', t0, L + 0.25, pitch, 100, human=False)
            self.cc('timproll', t0, t1, max(8, v0), min(127, v1 + 10), num=(1,), shape='exp')
            return
        if ins == 'perc':                            # suspended cymbal swell, timed so its peak lands on t1
            for key, peak in ((P('A4'), 7.2), (P('G4'), 3.57), (P('F4'), 1.42)):
                if peak <= L + 0.35:
                    break
            self.n('cym', t1 - peak, peak + 0.5, key, int(min(127, 40 + v1 * 0.7)), human=False)
            return
        if ins == 'kit':
            self.n('snare', t0, L + 0.1, P('A3'), int(min(120, v1)), human=False)
            return
        k = int(L * rate)
        for i in range(k):
            u = i / max(1, k - 1)
            self.n(ins, t0 + i / rate, 1.2 / rate, pitch, int(v0 + (v1 - v0) * u * u), human=False)

    # --- output -----------------------------------------------------------
    def write_midis(self, outdir):
        if not os.path.isdir(VPO):
            raise SystemExit('Sample libraries not found - run audio/fetch_assets.sh first (see audio/README.md)')
        os.makedirs(outdir, exist_ok=True)
        files = []
        for ins, notes in self.notes.items():
            if not notes:
                continue
            bank, prog, pan, gain, rev, drum = INSTR[ins]
            ch = 9 if drum else 0
            ev = []
            ev.append((0, 0, mido.Message('control_change', channel=ch, control=0, value=bank if not drum else 0)))
            ev.append((0, 0, mido.Message('control_change', channel=ch, control=32, value=0)))
            if drum:
                ev.append((0, 0, mido.Message('program_change', channel=ch, program=prog)))
            else:
                ev.append((0, 0, mido.Message('program_change', channel=ch, program=prog)))
            ev.append((0, 0, mido.Message('control_change', channel=ch, control=7, value=100)))
            ev.append((0, 0, mido.Message('control_change', channel=ch, control=10, value=64)))
            ev.append((0, 0, mido.Message('control_change', channel=ch, control=91, value=0)))
            ev.append((0, 0, mido.Message('control_change', channel=ch, control=93, value=0)))
            ev.append((0, 0, mido.Message('control_change', channel=ch, control=101, value=0)))
            ev.append((0, 0, mido.Message('control_change', channel=ch, control=100, value=0)))
            ev.append((0, 0, mido.Message('control_change', channel=ch, control=6, value=2)))
            sfz = ins in SFZ
            perf = sfz and 'PERF' in (SFZ[ins][1] if isinstance(SFZ[ins], tuple) else SFZ[ins])
            if sfz:
                ev.append((0, 0, mido.Message('control_change', channel=ch, control=7, value=127)))
                ev.append((0, 0, mido.Message('control_change', channel=ch, control=11, value=127)))
                ev.append((0, 0, mido.Message('control_change', channel=ch, control=1, value=cc1_of(ins, 104) if perf else 100)))
            else:
                ev.append((0, 0, mido.Message('control_change', channel=ch, control=11, value=104)))
                ev.append((0, 0, mido.Message('control_change', channel=ch, control=2, value=104)))
            for t, c, v in self.ccs[ins]:
                if sfz:
                    if c == 2:
                        continue
                    if c == 11 and perf:
                        c, v = 1, cc1_of(ins, v)
                ev.append((int(t * TPS), 1, mido.Message('control_change', channel=ch, control=c, value=v)))
            if sfz:
                lo, hi = sfz_range(sfz_path(ins))
                folded = []
                for t, d, p, v in notes:
                    while p < lo and p + 12 <= hi:
                        p += 12
                    while p > hi and p - 12 >= lo:
                        p -= 12
                    folded.append((t, d, p, v))
                notes = folded
            for t, b in self.bends[ins]:
                ev.append((int(t * TPS), 1, mido.Message('pitchwheel', channel=ch, pitch=b)))
            for t, d, p, v in notes:
                a = int(t * TPS)
                e = int((t + d) * TPS)
                ev.append((a, 2, mido.Message('note_on', channel=ch, note=p, velocity=v)))
                ev.append((e, 0, mido.Message('note_off', channel=ch, note=p, velocity=0)))
            ev.sort(key=lambda x: (x[0], x[1]))
            mf = mido.MidiFile(ticks_per_beat=960)
            tr = mido.MidiTrack()
            mf.tracks.append(tr)
            tr.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
            last = 0
            for tk, _, msg in ev:
                msg.time = tk - last
                last = tk
                tr.append(msg)
            f = os.path.join(outdir, f'{ins}.mid')
            mf.save(f)
            files.append((ins, f))
        return files


def render_stem(midi, wav, gain=0.6, ins=None):
    if ins in SFZ:
        subprocess.run([SFIZZ, '--sfz', sfz_path(ins), '--midi', midi, '--wav', wav, '-s', str(SR), '-q', '3',
                        '-p', '256'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    subprocess.run(['fluidsynth', '-ni', '-q', '-g', str(gain), '-r', str(SR), '-R', '0', '-C', '0',
                    '-o', 'synth.polyphony=512', '-F', wav, SF2, midi], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def hall_ir(sec=2.8, seed=3, pre=0.018):
    """synthetic stereo concert-hall impulse response"""
    r = np.random.default_rng(seed)
    n = int(sec * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for c in range(2):
        noise = r.standard_normal(n)
        # frequency-dependent decay: split into bands with different RT60
        from scipy.signal import butter, sosfilt
        bands = [(None, 300, 2.6), (300, 2000, 2.3), (2000, 6000, 1.7), (6000, None, 1.0)]
        sig = np.zeros(n)
        for lo, hi, rt in bands:
            if lo is None:
                sos = butter(4, hi, 'low', fs=SR, output='sos')
            elif hi is None:
                sos = butter(4, lo, 'high', fs=SR, output='sos')
            else:
                sos = butter(4, [lo, hi], 'band', fs=SR, output='sos')
            sig += sosfilt(sos, noise) * np.exp(-6.91 * t / rt)
        # soft onset
        sig *= np.clip(t / 0.06, 0, 1) ** 1.5
        # early reflections
        for k in range(14):
            d = int((pre + r.uniform(0.004, 0.07)) * SR)
            sig[d] += r.uniform(0.2, 0.6) * (1 if r.random() > 0.5 else -1)
        out[:, c] = sig
    out /= np.max(np.abs(out))
    return out
