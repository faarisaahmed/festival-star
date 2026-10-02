# THE FESTIVAL STAR - original score (5:00), synced to the picture.
# Quoted motifs (re-harmonised / re-orchestrated): Pokémon R/B title fanfare ("da-da-DAA"),
# Pallet Town, Route 1, Pokémon Center, the healing jingle, and the R/B ending theme.
# Original themes: the Festival Star theme, the Star motif, Charizard/Dragonite/Greninja/Sobble motifs.
from engine import *

S = Score(seed=11)
STR = ['vln1', 'vln2', 'vla', 'vc']
STRF = ['vln1f', 'vln2f', 'vlaf', 'vcf']
SUS = ['vln1', 'vln2', 'vla', 'vc', 'cb', 'trem', 'solovn', 'fl', 'picc', 'ob', 'cl', 'bsn', 'hn', 'tpt', 'tbn',
       'tuba', 'choir', 'oohs', 'shaku', 'fiddle', 'accord', 'pad', 'vln1f', 'vln2f', 'vlaf', 'vcf']


def dyn(ins, t0, t1, v0, v1, shape='s'):
    for i in (ins if isinstance(ins, (list, tuple)) else [ins]):
        S.cc(i, t0, t1, v0, v1, shape=shape)


def setv(ins, t, v):
    for i in (ins if isinstance(ins, (list, tuple)) else [ins]):
        S.ccset(i, t, v)


def bars(bar0, syms, beats=4):
    """one chord per bar (a list item may itself be a list -> split the bar evenly)"""
    out = []
    for k, s in enumerate(syms):
        if isinstance(s, (list, tuple)):
            w = beats / len(s)
            for j, c in enumerate(s):
                out.append((bar0 + k, j * w, w, c))
        else:
            out.append((bar0 + k, 0, beats, s))
    return out


def strings_pad(sec, prog, vel=70, lo=55, hi=81, bass=True, cb_lo=33, cb_hi=47, vc=True):
    """sustained string choir: vln1/vln2/vla on the upper voicing, vc+cb on the bass"""
    S.pad(['vla', 'vln2', 'vln2', 'vln1'], sec, prog, vel, lo, hi, 4)
    if bass:
        S.bassline('cb', sec, prog, vel, cb_lo, cb_hi)
        if vc:
            S.bassline('vc', sec, prog, vel, cb_lo + 12, cb_hi + 12)


def star_motif(t, ins='cel', vel=78, step=0.16, notes=('A5', 'D6', 'E6', 'A6'), shimmer=True):
    for i, p in enumerate(notes):
        S.n(ins, t + i * step, 1.4, p, vel + 4 * i)
    if shimmer:
        for i, p in enumerate(('A6', 'D7', 'E7', 'F#7', 'A7')):
            S.n('glock', t + len(notes) * step + 0.05 + i * 0.07, 0.8, p, 46 - 4 * i)


def hit(t, chord_notes, vel=110, brass=True, cym=True, timp=None, low=None):
    """orchestral accent"""
    if brass:
        for i, p in enumerate(chord_notes):
            S.n(['hn', 'tpt', 'tbn', 'hn'][i % 4], t, 0.5, p, vel)
    for p in chord_notes:
        S.n('vln1f', t, 0.35, p, vel - 10)
    if low:
        S.n('cb', t, 0.6, low, vel)
        S.n('tuba', t, 0.6, low, vel - 10)
    if timp:
        S.n('timp', t, 0.8, timp, vel)
    if cym:
        S.n('perc', t, 2.0, 57, vel - 10)
        S.n('perc', t, 1.0, 36, vel - 20)


# ======================================================================
# ACT I - MORNING
# ======================================================================
# A. Dawn & title (0 - 29.7)  - D major, 68.57 bpm (bar = 3.5 s), bar 1 = title at 2.1 s
A = Sec(-1.4, 68.571)
setv(SUS, 0, 100)
# pre-roll: dawn shimmer
dyn(['vln1', 'vln2', 'vla'], 0.0, 2.2, 8, 72)
dyn(['vc', 'cb'], 0.0, 2.2, 10, 70)
for p, ins in (('D5', 'vla'), ('A5', 'vln2'), ('E6', 'vln2'), ('F#6', 'vln1'), ('A6', 'vln1')):
    S.n(ins, 0.05, 2.2, p, 60)
S.n('cb', 0.05, 2.2, 'D2', 60)
S.n('vc', 0.05, 2.2, 'D3', 60)
S.gliss('harp', 0.35, 1.85, 'D3', 'A6', 46, scale=[2, 4, 6, 9, 11])
S.roll('timp', 0.6, 2.05, 'D2', 18, 64)
star_motif(1.05, vel=56)

# bars 1-2: the R/B title fanfare, broad and noble (horns), strings answer
dyn(['hn'], 2.0, 9.2, 70, 104)
fan_top = ['A4', 'Bb4', 'A4', 'F#4']
fan_chd = ['D', 'Bb/D', 'D', 'D']
for k in range(4):
    bar, bt = 1 + k // 2, (k % 2) * 2
    S.n('hn', A.t(bar, bt), A.d(0.42), 'D4', 86)
    S.n('hn', A.t(bar, bt + 0.5), A.d(0.42), 'D4', 80)
    S.n('hn', A.t(bar, bt + 1), A.d(1.0), fan_top[k], 96)
    S.n('hn', A.t(bar, bt), A.d(0.42), 'A3', 76)
    S.n('hn', A.t(bar, bt + 0.5), A.d(0.42), 'A3', 72)
    S.n('hn', A.t(bar, bt + 1), A.d(1.0), {'A4': 'D4', 'Bb4': 'F4', 'F#4': 'D4'}[fan_top[k]], 84)
    S.n('timp', A.t(bar, bt), A.d(0.3), 'D2', 58 + 6 * k)
    S.n('timp', A.t(bar, bt + 0.5), A.d(0.3), 'D2', 52 + 6 * k)
    S.n('timp', A.t(bar, bt + 1), A.d(0.5), 'A2' if k != 1 else 'Bb2', 62 + 6 * k)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], 2.2, 9.1, 72, 96)
strings_pad(A, [(1, 0, 2, 'D'), (1, 2, 2, 'Bb/D'), (2, 0, 2, 'D'), (2, 2, 2, 'Bm')], vel=74, lo=57, hi=84)
S.arp('harp', A, [(1, 0, 2, 'D'), (1, 2, 2, 'Bb'), (2, 0, 2, 'D'), (2, 2, 2, 'Bm')], step=0.25, vel=56, lo=50, hi=81)
S.mel('fl', A, 2, 'r:2 F#5:.5 A5:.5 D6:1', vel=70)
# bar 3: the answering cadence  D - Bb - C - (D)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tpt', 'tbn'], 9.1, 12.6, 96, 112)
S.mel('tpt', A, 3, 'D5:2 Bb4+D5:1 C5+E5:1', vel=92)
S.mel('hn', A, 3, 'F#4+A4:2 F4+D4:1 G4+E4:1', vel=90)
S.mel('tbn', A, 3, 'D3+A3:2 Bb2+F3:1 C3+G3:1', vel=90)
strings_pad(A, [(3, 0, 2, 'D'), (3, 2, 1, 'Bb'), (3, 3, 1, 'C')], vel=90, lo=60, hi=86)
S.mel('vln1', A, 3, 'D6:2 D6:1 E6:1', vel=96)
S.roll('timp', A.t(3, 2.5), A.t(4, 0), 'A2', 40, 96)
S.roll('perc', A.t(3, 1.5), A.t(4, 0), 59, 20, 84)
S.n('perc', A.t(4, 0), 3.0, 57, 92)

# bars 4-7: Pallet Town (transposed to D) - the festival tree, the Star, sleeping Pikachu
pallet1 = 'A5:.5 G5:.5 F#5:.5 E5:.5 D6:.5 B5:.5 C#6:.5 B5:.5 A5:1.5 F#5:.5 D5:.5 D5:.5 E5:.5 F#5:.5'
pallet2 = 'G5:2.5 C#5:.5 D5:.5 E5:.5 F#5:1.5 G5:.25 F#5:.25 E5:2'
dyn(['fl'], A.t(4), A.t(6), 88, 84)
S.mel('fl', A, 4, pallet1, vel=84)
S.mel('cl', A, 6, pallet2, vel=74)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], A.t(4), A.t(4, 1), 112, 76)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], A.t(5, 2), A.t(6, 2), 76, 60)
pp = [(4, 0, 2, 'D'), (4, 2, 2, 'Gmaj7'), (5, 0, 2, 'D/F#'), (5, 2, 2, 'Em7'), (6, 0, 2, 'G'), (6, 2, 2, 'A7'),
      (7, 0, 2, 'Bm7'), (7, 2, 1, 'G'), (7, 3, 1, 'A')]
strings_pad(A, pp[:4], vel=64, lo=57, hi=79)
S.arp('harp', A, pp[:4], step=0.5, vel=50, lo=50, hi=79)
star_motif(A.t(4, 0.1), vel=64)
for t in (A.t(4, 2.2), A.t(5, 0.6), A.t(5, 3.1)):
    S.n('glock', t, 1.0, 'A6', 40)
    S.n('glock', t + 0.12, 1.0, 'E7', 36)
# bars 6-7 (19.6-26.6): down to sleeping Pikachu - waking, stretching (23.8-26.6)
dyn(['cl'], A.t(6), A.t(8), 80, 74)
strings_pad(A, pp[4:], vel=56, lo=55, hi=76)
S.arp('harp', A, pp[4:6], step=1.0, vel=42, lo=50, hi=74)
S.gliss('bsn', 23.85, 25.0, 'A2', 'A3', 38)                  # the stretch
S.n('bsn', 25.0, 0.9, 'B3', 50)
S.mel('bsn', Sec(25.35, 90), 0, 'A3:.5 F#3:.5 D3:1.5', vel=50)   # ...and a yawn
S.bend('bsn', 25.9, 26.6, 0, -120)
S.bend('bsn', 26.7, 26.8, -120, 0)
star_motif(26.7, vel=74)                                       # Pikachu looks up at the Star
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], 26.6, 29.6, 58, 84)
for p, ins in (('E4', 'vla'), ('A4', 'vln2'), ('C#5', 'vln2'), ('G5', 'vln1')):
    S.n(ins, 26.65, 3.05, p, 66)
S.n('cb', 26.65, 3.0, 'A1', 64)
S.n('vc', 26.65, 3.0, 'A2', 64)
S.roll('perc', 28.3, 29.7, 59, 12, 60)

# B. Excited! -> the run (29.71 - 40.08) - D major, 162 bpm
B = Sec(29.71, 162)
setv(['vln1', 'vln2', 'vla', 'vc', 'cb'], 29.70, 92)
pika = 'D5:.25 E5:.25 F#5:.5 F#5:.5 F#5:.5 D5:.25 E5:.25 F#5:.5 F#5:.5 F#5:.5'
S.mel('xylo', B, 0, pika, vel=88)
S.mel('fl', B, 0, pika, vel=80, legato=0.6)
S.mel('xylo', B, 1, 'D5:.25 E5:.25 F#5:.5 F#5:.5 G5:.75 F#5:.25', vel=90)
S.mel('fl', B, 1, 'D5:.25 E5:.25 F#5:.5 F#5:.5 G5:.75 F#5:.25', vel=82, legato=0.6)
for b in (0, 1):
    for bt, p in ((0, 'D3'), (1, 'A2'), (2, 'D3'), (3, 'A2')):
        if b == 1 and bt >= 2:
            continue
        S.n('pizz', B.t(b, bt), 0.3, p, 86)
        S.n('vlnpizz', B.t(b, bt + 0.5), 0.2, 'F#4', 70)
        S.n('vlnpizz', B.t(b, bt + 0.5), 0.2, 'A4', 70)
import random as _r
_g = _r.Random(4)
for i in range(16):                                           # cheek sparks 30.0 - 31.7
    S.n('glock', 30.0 + i * 0.105 + _g.uniform(0, 0.04), 0.3, _g.choice(['A6', 'B6', 'D7', 'E7', 'F#7']), 50 + _g.randint(0, 20))
# the dash (beat 6 = 31.93): whoosh up
S.gliss('vln1f', 31.75, 32.68, 'D4', 'D6', 84)
S.gliss('fl', 31.85, 32.68, 'A4', 'A6', 76)
S.n('perc', B.t(1, 3.8), 0.4, 38, 70)
# bars 2-5: Route 1 (in D) - galloping through the meadow
r1a = 'D5:.25 E5:.25 F#5:.5 F#5:.5 F#5:.5 D5:.25 E5:.25 F#5:.5 F#5:.5 F#5:.5'
r1b = 'D5:.25 E5:.25 F#5:.5 F#5:.5 G5:.5 r:.25 F#5:.25 E5:1.5'
r1c = 'C#5:.25 D5:.25 E5:.5 E5:.5 E5:.5 C#5:.25 D5:.25 E5:.5 E5:.5 E5:.5'
r1d = 'C#5:.25 D5:.25 E5:.5 E5:.5 F#5:.25 E5:.25 E5:.25 F#5:.25 D5:1 F#5:.5'
for k, ph in enumerate((r1a, r1b, r1c, r1d)):
    S.mel('vln1f', B, 2 + k, ph, vel=88, legato=0.7)
    S.mel('fl', B, 2 + k, ph, vel=84, legato=0.7, oct=1 if k % 2 else 0)
    S.mel('xylo', B, 2 + k, ph, vel=70, oct=1)
rp = bars(2, [['D', 'D/C#'], ['Bm', 'D/A'], ['A', 'A/G'], ['F#m', 'A7']])
for bar, bt, ln, sym in rp:
    p = bass_of(sym, 38, 50)
    for o in range(int(ln)):
        S.n('pizz', B.t(bar, bt + o), 0.25, p if o % 2 == 0 else p + 7 if p + 7 < 57 else p - 5, 84)
    v = voicing(sym, 57, 74, 3)
    for o in range(int(ln * 2)):
        if o % 2 == 1:
            for q in v:
                S.n('vln2f', B.t(bar, bt + o * 0.5), 0.15, q, 66)
                S.n('vlaf', B.t(bar, bt + o * 0.5), 0.15, q - 12, 60)
for b in range(2, 7):
    for bt in range(4):
        S.n('kit', B.t(b, bt + 0.5), 0.1, 42, 34)      # light hi-hat drive
    S.n('kit', B.t(b, 0), 0.1, 54, 44)                # tambourine on 1
S.mel('hn', B, 2, 'F#4:4 F#4:2 F#4:2 E4:4 C#4:2 E4:2', vel=66)
# bar 6: cadence into the lake (dominant of G)
S.mel('vln1f', B, 6, 'A5:.25 B5:.25 A5:.25 G5:.25 F#5:.5 E5:.5 D5:.5 C5:.5 B4:.5 A4:.5', vel=86)
S.mel('fl', B, 6, 'A5:.25 B5:.25 A5:.25 G5:.25 F#5:.5 E5:.5 D5:.5 C5:.5 B4:.5 A4:.5', vel=80, oct=1)
S.n('pizz', B.t(6), 0.3, 'D3', 86)
S.n('pizz', B.t(6, 2), 0.3, 'D3', 80)
for q in ('C4', 'F#4', 'A4'):
    S.n('vln2f', B.t(6, 1), 0.2, q, 70)
    S.n('vln2f', B.t(6, 3), 0.2, q, 64)

# C. The lake (40.08 - 52.96) - G major, 80 bpm (beat = Piplup's splash interval)
C = Sec(40.08, 80)
lake = bars(0, [['G', 'C/G'], ['G', 'D7/F#'], ['Em', 'C'], ['Gm', 'Eb']])
S.mel('marimba', C, 0, 'G4+B4:.5 r:.5 D5:.5 r:.5 G4+B4:.5 r:.5 D5:.5 r:.5', vel=70)
S.mel('marimba', C, 1, 'G4+B4:.5 r:.5 D5:.5 r:.5 F#4+A4:.5 r:.5 C5:.5 r:.5', vel=70)
for b, roots in ((0, ('G2', 'D3', 'G2', 'D3')), (1, ('G2', 'D3', 'F#2', 'D3'))):
    for i, p in enumerate(roots):
        S.n('pizz', C.t(b, i), 0.3, p, 82)
S.mel('fl', C, 0, 'G5:.5 D5:.5 G5:.5 B5:.5 A5:.75 G5:.25 F#5:.5 D5:.5', vel=82, legato=0.75)
S.mel('fl', C, 1, 'E5:.5 G5:.5 F#5:.5 A5:.5 G5:1 r:1', vel=82, legato=0.75)
S.mel('cl', C, 0, 'r:2 B4.:.5 C5.:.5 B4.:.5 A4.:.5', vel=64)        # Sobble giggling
S.mel('cl', C, 1, 'r:1 D5.:.25 C5.:.25 B4.:.25 C5.:.25 D5:.5 r:1.5', vel=62)
for t in (41.58, 42.33, 43.08, 43.83):                               # splashes: water-drop plinks
    S.n('harp', t, 0.6, 'D6', 70)
    S.n('cel', t + 0.04, 0.6, 'G6', 54)
# bar 2: Piplup winds up the belly-flop: rise (46.2-47.2), fall (47.2-48.1), SPLASH 48.17
S.gliss('cl', 46.2, 47.2, 'G4', 'G5', 60)
S.gliss('xylo', 46.25, 47.2, 'G4', 'G6', 64)
S.gliss('vln1f', 46.3, 47.25, 'B4', 'D6', 60)
S.n('fl', 47.2, 0.5, 'G6', 80)
S.n('picc', 47.2, 0.5, 'G6', 70)
S.gliss('xylo', 47.4, 48.1, 'G6', 'G4', 70, scale='chrom', dur_mult=1.0)
S.gliss('fl', 47.45, 48.1, 'D6', 'D5', 70, scale='chrom', dur_mult=1.0)
hit(48.17, ['G3', 'B3', 'D4', 'G4'], vel=96, timp='G2', low='G1')
S.n('oboe' if False else 'ob', 48.5, 0.18, 'E6', 92)                 # Sobble: "eep!"
# bar 3 (49.08): Sobble's comic lament
dyn(['ob'], 49.0, 52.6, 92, 70)
S.mel('ob', C, 3, 'Bb5:.75 A5:.25 Ab5:.75 G5:.25 F#5:2', vel=88)
S.bend('ob', C.t(3, 2.2), C.t(3, 3.6), 0, -60)
S.bend('ob', C.t(3, 3.7), C.t(3, 3.8), -60, 0)
dyn(['vln2', 'vla', 'vc', 'cb'], 49.0, 52.9, 70, 46)
strings_pad(C, [(3, 0, 2, 'Gm'), (3, 2, 2, 'Eb'), (4, 0, 0.9, 'D7')], vel=60, lo=55, hi=74)
_g = _r.Random(9)
for i in range(7):                                                   # tears
    S.n('cel', 49.3 + i * 0.45 + _g.uniform(0, 0.1), 0.5, _g.choice(['D6', 'Bb5', 'G5', 'A5']), 46)

# D. Pikachu cheers Sobble up (52.96 - 58.96) - D major, 120 bpm
D = Sec(52.96, 120)
setv(['vln1', 'vln2', 'vla', 'vc', 'cb'], 52.9, 78)
S.mel('cl', D, 0, 'D5:.25 E5:.25 F#5:.5 F#5:.5 F#5:.5 A5:1 G5:.5 F#5:.5', vel=80)
S.mel('fl', D, 1, 'B5:1.5 A5:.5 G5:1 E5:1', vel=80)
strings_pad(D, bars(0, ['D', ['G', 'A7']]), vel=66, lo=55, hi=76)
S.arp('harp', D, bars(0, ['D', ['G', 'A7']]), step=0.5, vel=50, lo=50, hi=79)
star_motif(55.5, vel=60, notes=('D6', 'F#6', 'A6'))                 # Sobble smiles
# bar 2: hop hop (56.5-58), off they run (58-59)
for t in (56.55, 57.3):
    S.gliss('xylo', t, t + 0.25, 'D5', 'A5', 70)
    S.n('pizz', t, 0.3, 'D3', 86)
    S.n('vlnpizz', t + 0.3, 0.2, 'A4', 74)
S.mel('fl', D, 2, 'D6:.5 A5:.5 D6:.5 A5:.5', vel=78, legato=0.5)
S.gliss('vln1f', D.t(2, 2.2), D.t(2, 3.8), 'D5', 'A6', 66)
S.mel('xylo', D, 2, 'r:2 A5:.25 B5:.25 C#6:.25 D6:.25 E6:.5 r:.5', vel=72)

# E. Raboot juggles; Greninja watches (58.96 - 73.5) - A mixolydian groove, 160 bpm, kicks every 2 beats
E = Sec(58.96, 160)
S.mel('kit', E, 0, '38:.25 38:.25 38:.5 38:.25 38:.25 38:.5 38:.25 38:.25 38:.25 38:.25', vel=50)   # snare pickup
riff = 'A2:.75 A2:.25 C#3:.5 D3:.5 E3:.75 G3:.25 E3:.5 D3:.5'
for b in range(1, 10):
    S.mel('pizz', E, b, riff, vel=72, legato=0.6)
    S.mel('bsn', E, b, 'A3:.75 A3:.25 C#4:.5 D4:.5 E4:.75 G4:.25 E4:.5 D4:.5', vel=58, legato=0.5) if b % 2 == 0 else None
    for bt in (0, 2):
        S.n('perc', E.t(b, bt), 0.15, 76, 70)        # woodblock on each kick
    S.n('perc', E.t(b, 1), 0.15, 77, 50)
    S.n('perc', E.t(b, 3), 0.15, 77, 50)
    S.n('kit', E.t(b, 1), 0.1, 38, 40)
    S.n('kit', E.t(b, 3), 0.1, 38, 44)
# clarinet + xylophone call/response
S.mel('cl', E, 1, 'r:2 E5:.25 F#5:.25 G5:.5 A5:.5 r:.5', vel=80)
S.mel('xylo', E, 2, 'r:2 A5:.25 G5:.25 E5:.5 D5:.5 r:.5', vel=78)
S.mel('cl', E, 3, 'r:2 E5:.25 F#5:.25 G5:.5 B5:.5 A5:.5', vel=82)
S.mel('xylo', E, 4, 'r:2 C#6:.25 B5:.25 A5:.5 G5:.5 E5:.5', vel=78)
S.mel('cl', E, 5, 'A5:.5 G5:.25 E5:.25 D5:.5 E5:1.5 r:1', vel=78)
# 65.5-67.9: camera finds Greninja on its rock - shakuhachi + koto
dyn(['shaku'], 65.4, 68.0, 70, 96)
S.mel('shaku', Sec(65.6, 80), 0, 'E5:.75 G5:.25 A5:1.5 B5:.5 D6:1 B5:.25 A5:.25', vel=86)
S.bend('shaku', 65.6, 65.75, -80, 0)
S.gliss('koto', 67.3, 67.8, 'E5', 'E4', 66, scale=[4, 6, 9, 11, 1])
# s09 (67-73): the friends arrive - the groove opens up with a Route-1 tag
S.mel('vln1f', E, 6, 'A5:.25 B5:.25 C#6:.5 C#6:.5 C#6:.5 A5:.25 B5:.25 C#6:.5 C#6:.5 C#6:.5', vel=78, legato=0.7)
S.mel('fl', E, 7, 'A5:.25 B5:.25 C#6:.5 C#6:.5 D6:.75 C#6:.25 B5:1.5', vel=80, legato=0.7)
S.mel('xylo', E, 8, 'E6:.5 C#6:.5 A5:.5 E5:.5 G5:.5 B5:.5 D6:.5 r:.5', vel=72)
S.mel('cl', E, 9, 'C#6:.5 B5:.5 A5:1 r:2', vel=72)
for b in range(6, 10):
    for bt in (0.5, 1.5, 2.5, 3.5):
        for q in ('C#4', 'E4', 'A4') if b % 2 == 0 else ('B3', 'D4', 'G4'):
            S.n('vln2f', E.t(b, bt), 0.12, q, 60)

# F1. Greninja's leap (73.4 - 77.9)
dyn(['trem'], 73.3, 75.9, 30, 100, 'exp')
for p in ('E5', 'B5', 'E6'):
    S.n('trem', 73.35, 2.65, p, 70)
S.n('taiko', 73.875, 0.6, 'C3', 100)
S.n('taiko', 73.875, 0.6, 'G2', 90)
dyn(['shaku'], 73.8, 75.2, 96, 112)
S.gliss('shaku', 73.95, 74.95, 'E5', 'E6', 84, scale=[4, 7, 9, 11, 2])
S.bend('shaku', 74.95, 75.3, 0, -60)
S.gliss('koto', 75.0, 75.9, 'E6', 'E4', 74, scale=[4, 6, 9, 11, 1])
S.gliss('harp', 75.0, 75.9, 'E6', 'E3', 60, scale=[4, 6, 9, 11, 1])
# landing 76.0
S.n('taiko', 76.0, 0.8, 'C3', 122)
S.n('taiko', 76.0, 0.8, 'G2', 116)
S.n('perc', 76.0, 0.8, 36, 100)
for p in ('E2', 'E3', 'B3', 'E4', 'G4'):
    S.n('vcf' if P(p) < 52 else 'vln1f', 76.0, 0.4, p, 104)
S.n('cb', 76.0, 0.6, 'E1', 104)
S.n('perc', 76.02, 0.5, 52, 70)
S.n('koto', 76.75, 0.6, 'B4', 76)                     # the cool nod
S.n('koto', 76.85, 0.6, 'E5', 70)
dyn(['shaku'], 76.6, 77.8, 90, 50)
S.n('shaku', 76.95, 0.8, 'E5', 76)
S.bend('shaku', 77.4, 77.75, 0, -100)

# F2. Big friends (78 - 88): Garchomp thunders in; Dragonite glides down
F = Sec(78.0, 96)
setv(['tuba', 'tbn', 'cb', 'vc', 'bsn', 'hn'], 77.9, 80)
dyn(['tuba', 'tbn', 'cb', 'vcf'], 77.9, 80.4, 50, 110)
for b in range(1):
    for bt in range(4):
        S.n('timp', F.t(b, bt), 0.4, 'D2', 62 + bt * 12)
        S.n('timp', F.t(b, bt + 0.5), 0.3, 'D2', 50 + bt * 10)
        S.n('perc', F.t(b, bt), 0.4, 35, 60 + bt * 12)
        for ins, p in (('cb', 'D1'), ('vcf', 'D2'), ('tuba', 'D1'), ('tbn', 'D2')):
            S.n(ins, F.t(b, bt), F.d(0.45), p, 76 + bt * 10)
            S.n(ins, F.t(b, bt + 0.5), F.d(0.4), p if bt % 2 == 0 else 'A1' if ins != 'tbn' else 'A2', 70 + bt * 10)
S.mel('bsn', F, 0, 'D2:.5 F2:.5 A2:.5 Bb2:.5 A2:.5 F2:.5 D2:1', vel=80)
S.bend('tbn', 80.2, 80.7, 0, -200)                     # the skid
S.n('tbn', 80.2, 0.55, 'A2', 96)
S.gliss('vln1f', 80.15, 80.8, 'D6', 'D4', 84)
hit(81.46, ['Bb3', 'D4', 'F4', 'Bb4'], vel=118, timp='Bb2', low='Bb1')   # ROAR
S.n('perc', 81.46, 3.0, 49, 100)
dyn(['hn', 'tbn', 'tuba'], 81.5, 83.4, 110, 60)
for p, ins in (('Bb2', 'tbn'), ('F3', 'tbn'), ('D4', 'hn'), ('F4', 'hn'), ('Bb1', 'tuba')):
    S.n(ins, 81.5, 1.9, p, 90)
# Dragonite's theme (F major, warm horn) - glides down, lands 84.3, waves & smiles
setv(['hn'], 83.4, 120)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], 82.6, 83.4, 40, 74)
S.mel('hn', F, 2, 'C4:1 F4:1 A4:1.5 G4:.5', vel=106)
S.mel('hn', F, 3, 'F4:.5 A4:.5 C5:3', vel=106)
S.mel('cel', F, 3, 'r:1 F6:.5 A6:.5 C7:1', vel=60)
strings_pad(F, bars(2, ['F', ['Bb', 'C7'], 'F']), vel=70, lo=53, hi=77)
S.arp('harp', F, bars(2, ['F', ['Bb', 'C7']]), step=0.25, vel=52, lo=53, hi=84)
S.gliss('harp', 83.85, 84.7, 'C6', 'F4', 56, scale=[5, 7, 9, 0, 2])         # soft landing
dyn(['hn', 'vln1', 'vln2', 'vla', 'vc', 'cb'], 86.0, 87.95, 90, 20)
for p in ('F3', 'C4', 'A4', 'F5'):
    S.n('harp', 85.5, 2.2, p, 50)


# ======================================================================
# ACT II - THE GAME
# ======================================================================
# G. The ball game (88.0 - 106.46) - G major scherzo, 150 bpm, bar 0 = Raboot's kick 88.67
G = Sec(88.67, 150)
setv(SUS, 87.99, 96)
S.roll('kit', 88.05, 88.6, 38, 20, 70)
S.mel('xylo', Sec(88.27, 150), 0, 'D5:.33 E5:.33 F#5:.34', vel=70)
game = [
    'G5:.5 B5:.5 D6:.5 B5:.5 C6:.5 A5:.5 F#5:.5 D5:.5',
    'E5:.5 G5:.5 B5:.75 A5:.25 G5:1 r:1',
    'G5:.5 B5:.5 D6:.5 B5:.5 E6:.5 C6:.5 A5:.5 F#5:.5',
    'G5:.5 D5:.5 B4:.5 D5:.5 G5:1 r:1',
]
gprog = bars(0, [['G', 'C'], ['Em', 'D7'], ['G', 'C'], ['D7', 'G']])
for k, ph in enumerate(game):
    S.mel('fl', G, k, ph, vel=84, legato=0.6)
    S.mel('xylo', G, k, ph, vel=70 if k != 3 else 64)
    S.mel('vlnpizz', G, k, ph, vel=62, oct=-1)
for bar, bt, ln, sym in gprog:                       # oom-pah (pizz + bassoon + harp)
    b = bass_of(sym, 40, 52)
    v = voicing(sym, 55, 71, 3)
    for o in range(int(ln)):
        S.n('pizz', G.t(bar, bt + o), 0.25, b if o % 2 == 0 else b + 7 if b + 7 < 57 else b - 5, 84)
        S.n('bsn', G.t(bar, bt + o), 0.2, b, 60)
        for q in v:
            S.n('harp', G.t(bar, bt + o + 0.5), 0.3, q, 50)
    S.n('kit', G.t(bar, bt), 0.1, 54, 40)
S.n('xylo', 90.375, 0.3, 'D6', 84)                 # Piplup's header
S.n('perc', 90.375, 0.2, 76, 66)
S.gliss('fl', 92.4, 92.95, 'G6', 'D5', 76)   # Sobble ducks...
S.n('ob', 92.9, 0.15, 'A6', 70)                                          # ...with a squeak
S.n('perc', 93.79, 0.2, 76, 90)                                          # Pikachu's tail-whack
S.n('xylo', 93.79, 0.2, 'G6', 90)
S.gliss('vln1f', 93.8, 94.55, 'G5', 'G6', 80)
# bar 4: everybody waits - ball sails to Greninja; bar 5 beat 1 (97.07) the backflip kick
S.mel('vln1f', G, 4, 'D5:.5 E5:.5 F#5:.5 G5:.5 A5:.5 B5:.5 C6:.5 C#6:.5', vel=76, legato=0.6)
S.roll('timp', G.t(4, 0), G.t(5, 1), 'D2', 30, 90)
for q in ('D4', 'F#4', 'A4', 'C5'):
    S.n('vln2f', G.t(4, 0), G.d(5), q, 60)
dyn(['vln2f'], G.t(4), G.t(5, 1), 50, 110)
S.n('taiko', 97.04, 0.4, 'C3', 96)
S.gliss('picc', 96.75, 97.55, 'D6', 'D7', 76)
S.gliss('harp', 96.7, 97.55, 'D4', 'D7', 60)
hit(97.6, ['G3', 'B3', 'D4', 'G4'], vel=104, timp='G2', low='G1')
# bars 6-7: cheers - the game tune in full, Dragonite claps along
for k, ph in enumerate(game[2:]):
    S.mel('tpt', G, 6 + k, ph, vel=88, legato=0.7, oct=-1)
    S.mel('vln1f', G, 6 + k, ph, vel=92, legato=0.7)
    S.mel('fl', G, 6 + k, ph, vel=84, legato=0.6, oct=0)
    S.mel('xylo', G, 6 + k, ph, vel=70)
for bar, bt, ln, sym in bars(6, [['G', 'C'], ['D7', 'G']]):
    b = bass_of(sym, 40, 52)
    v = voicing(sym, 55, 72, 4)
    for o in range(int(ln)):
        S.n('pizz', G.t(bar, bt + o), 0.25, b, 90)
        S.n('tuba', G.t(bar, bt + o), 0.25, b - 12, 70) if o % 2 == 0 else None
        for q in v:
            S.n('hn', G.t(bar, bt + o + 0.5), 0.2, q - 12 if q > 67 else q, 66)
    S.n('perc', G.t(bar, bt), 0.6, 57, 70) if bt == 0 else None
    S.n('kit', G.t(bar, bt), 0.1, 54, 50)
    S.n('kit', G.t(bar, bt + 1), 0.1, 39, 48)       # handclap with Dragonite
    S.n('kit', G.t(bar, bt + 0.0), 0.1, 39, 40)
# bar 8 (101.47): Garchomp wants a turn - the comic waddle (tuba + bassoon), tail wagging
W = Sec(101.4, 112)
dyn(['tuba', 'bsn'], 101.3, 103.6, 92, 92)
S.mel('tuba', W, 0, 'G1:.5 r:.5 D2:.5 r:.5 G1:.5 r:.5 B1:.5 C2:.5', vel=88, legato=0.7)
S.mel('bsn', W, 0, 'r:.5 B2.:.5 r:.5 B2.:.5 r:.5 D3.:.5 C3:.25 B2:.25 A2:.5', vel=78)
S.mel('cl', W, 0, 'r:1 G4:.5 A4:.5 B4:.75 A4:.25 G4:1', vel=66)
S.n('perc', 102.0, 0.1, 76, 60)
S.n('perc', 102.55, 0.1, 77, 60)
# 103.6 the wind-up: everything coils toward the KICK at 106.46
dyn(['trem'], 103.55, 106.4, 20, 124, 'exp')
for p in ('D3', 'A3', 'D4', 'A4', 'D5'):
    S.n('trem', 103.6, 2.86, p, 80)
S.roll('timp', 103.6, 106.4, 'A1', 26, 120)
S.roll('perc', 104.5, 106.42, 59, 14, 100)
dyn(['vln1', 'vla', 'vc'], 103.6, 106.4, 40, 118, 'exp')
S.gliss('vln1', 103.65, 106.3, 'A4', 'A5', 70, scale='chrom', dur_mult=1.05)
S.gliss('vc', 103.65, 106.3, 'A2', 'A3', 70, scale='chrom', dur_mult=1.05)
S.mel('bsn', Sec(103.6, 100), 0, 'G2:.5 G2:.5 G2:.5 G2:.5 G2:.5 G2:.5 G2:.25 G2:.25 G2:.25 G2:.25', vel=70)

# H. KICK (106.46) -> the ball rockets up -> STAR HIT (108.54) -> the fall -> chase -> PLOP (123.79)
hit(106.46, ['Eb3', 'G3', 'Bb3', 'Eb4'], vel=126, timp='Eb2', low='Eb1')
S.n('perc', 106.46, 3, 49, 120)
S.n('perc', 106.46, 1, 35, 124)
S.n('taiko', 106.46, 1, 'C3', 120)
dyn(['vln1f', 'vln2f'], 106.4, 108.5, 70, 120, 'exp')
S.gliss('vln1f', 106.6, 108.45, 'Bb4', 'Eb7', 70)
S.gliss('vln2f', 106.62, 108.45, 'G4', 'Bb6', 62)
S.gliss('picc', 107.0, 108.45, 'Bb5', 'Eb7', 66)
dyn(['trem'], 106.5, 108.5, 70, 110)
for p in ('Eb5', 'Bb5', 'Eb6'):
    S.n('trem', 106.55, 1.95, p, 76)
S.roll('perc', 107.2, 108.5, 59, 30, 110)
# the hit: a bright crash and a shattered chime
S.n('perc', 108.54, 4.0, 57, 120)
S.n('perc', 108.54, 4.0, 49, 110)
for i, p in enumerate(('C7', 'F#6', 'B6', 'F7', 'A#6', 'E7')):
    S.n('glock', 108.54 + i * 0.03, 1.5, p, 92 - i * 4)
    S.n('cel', 108.54 + i * 0.035, 1.5, p, 80 - i * 4)
for p, ins in (('Ab3', 'tbn'), ('D4', 'hn'), ('F4', 'hn'), ('B4', 'tpt'), ('D2', 'tuba')):
    S.n(ins, 108.54, 0.9, p, 112)
dyn(['hn', 'tpt', 'tbn', 'tuba'], 108.55, 109.5, 112, 50)
# 108.6 - 117: the fall - tumbling celesta/harp in whole tones, branch bonks
setv(['trem', 'vln1', 'vla', 'vc', 'cb'], 109.4, 40)
_g = _r.Random(21)
wt = ['C', 'D', 'E', 'F#', 'G#', 'A#']
t = 109.0
oc = 7
while t < 115.2:
    p = f'{wt[_g.randrange(6)]}{oc}'
    S.n('cel', t, 0.6, p, 66)
    S.n('harp', t + 0.02, 0.6, p.replace(str(oc), str(oc - 1)), 54)
    t += _g.uniform(0.16, 0.3)
    if _g.random() < 0.18 and oc > 4:
        oc -= 1
for t0, ln in ((111.0, 1.6), (112.6, 1.7), (114.3, 1.0)):
    S.gliss('fl', t0, t0 + ln * 0.9, 'E6', 'G#4', 60, scale=[0, 2, 4, 6, 8, 10], dur_mult=1.1)
for t in (112.6, 114.3, 115.3):                         # branch / ground bonks
    S.n('pizz', t, 0.3, 'C3', 96)
    S.n('timp', t, 0.5, 'C2', 72)
    S.n('perc', t, 0.2, 76, 74)
dyn(['vc', 'cb'], 109.4, 116.5, 30, 96, 'exp')
for p in ('C2', 'C3'):
    S.n('vc' if p == 'C3' else 'cb', 109.4, 7.2, p, 70)
dyn(['trem'], 112.0, 116.6, 30, 100)
for p in ('F#4', 'C5', 'F#5'):
    S.n('trem', 112.0, 4.6, p, 70)
# chase (116.6 - 123.2): D minor galop, 168 bpm
H = Sec(116.6, 168)
setv(['vln1f', 'vln2f', 'vlaf', 'vcf', 'cb', 'hn', 'tpt', 'tbn', 'fl', 'picc'], 116.55, 100)
chase = bars(0, ['Dm', 'Bb', ['Gm', 'C'], 'A7'])
for bar, bt, ln, sym in chase:
    b = bass_of(sym, 38, 50)
    for o in range(int(ln * 2)):
        S.n('vcf', H.t(bar, bt + o * 0.5), 0.17, b if o % 2 == 0 else b + 12, 88)
        S.n('cb', H.t(bar, bt + o * 0.5), 0.17, b - 12 if o % 2 == 0 else b, 80)
    v = voicing(sym, 57, 72, 3)
    for o in (0.5, 1.5, 2.5, 3.5):
        for q in v:
            S.n('vln2f', H.t(bar, bt + o), 0.14, q, 78)
            S.n('hn', H.t(bar, bt + o), 0.14, q - 12, 62)
    S.n('kit', H.t(bar, bt + 1), 0.1, 38, 66)
    S.n('kit', H.t(bar, bt + 3), 0.1, 38, 70)
    S.n('perc', H.t(bar, bt), 0.4, 35, 70)
chase_mel = ['D6:.5 A5:.5 D6:.5 E6:.5 F6:1 E6:.5 D6:.5', 'D6:.5 F6:.5 Bb6:.5 A6:.5 G6:.5 F6:.5 E6:.5 D6:.5',
             'Bb6:1 A6:.5 G6:.5 G6:.5 F6:.5 E6:.5 F6:.5', 'E6:.5 F6:.5 G6:.5 E6:.5 C#6:1 E6:1']
for k, ph in enumerate(chase_mel):
    S.mel('vln1f', H, k, ph, vel=96, legato=0.75, oct=-1)
    S.mel('xylo', H, k, ph, vel=72, oct=0)
    S.mel('fl', H, k, ph, vel=84, legato=0.6)
for k in (1, 3):
    S.mel('tpt', H, k, 'D5:1 r:.5 D5:.5 F5:1 r:1', vel=88)
# bar 7-8 (~122.3-123.8): the Star flies off the beach - everything rises and hangs
S.gliss('vln1f', H.t(4), 123.3, 'A4', 'A6', 90)
dyn(['trem'], 122.9, 123.75, 80, 118, 'exp')
for p in ('A5', 'C#6', 'E6', 'A6'):
    S.n('trem', 122.9, 0.86, p, 90)
S.roll('perc', 122.6, 123.75, 59, 40, 108)
# PLOP (123.79): everything stops. a low harp note, then the light fades out (123.8 - 125.3)
S.n('harp', 123.79, 3.0, 'D2', 96)
S.n('harp', 123.79, 3.0, 'D3', 80)
S.n('timp', 123.79, 1.5, 'D2', 60)
S.n('pizz', 123.79, 0.5, 'D2', 90)
for i, p in enumerate(('A6', 'E6', 'D6', 'A5', 'F5', 'D5')):
    S.n('cel', 123.95 + i * 0.26 * (1 + i * 0.25), 1.4, p, 70 - i * 7)
S.bend('cel', 125.0, 125.9, 0, -90)
S.bend('cel', 126.4, 126.5, -90, 0)


# ======================================================================
# I. THE LOST LIGHT (126 - 153)
# ======================================================================
setv(['vln1', 'vln2', 'vla', 'vc', 'cb'], 125.0, 30)
dyn(['vla', 'vc', 'cb'], 125.0, 127.5, 20, 58)
for p, ins in (('D2', 'cb'), ('D3', 'vc'), ('A3', 'vla'), ('F4', 'vla')):
    S.n(ins, 125.0, 7.2, p, 60)
dyn(['vln1'], 126.0, 128.0, 10, 50)
S.n('vln1', 126.0, 6.0, 'A6', 50)
S.n('harp', 127.0, 2.0, 'D4', 40)
S.n('harp', 127.4, 2.0, 'A4', 38)
S.n('harp', 127.8, 2.0, 'F5', 36)
dyn(['bsn'], 128.4, 132.0, 74, 60)
S.mel('bsn', Sec(128.5, 66), 0, 'A3:1.5 G3:.5 F3:2 E3:1 D3:2', vel=70)     # Garchomp's sorry sigh
# I1 Sobble's lament (132) -> the dive (134.1) -> underwater (136-139)
I = Sec(132.0, 72)
setv(['ob'], 131.9, 90)
dyn(['ob'], 132.0, 134.2, 92, 80)
S.mel('ob', I, 0, 'D5:1 C#5:.5 D5:.5 F5:1.5 E5:.5', vel=86)
strings_pad(I, [(0, 0, 2.5, 'Dm'), (0, 2.5, 1.5, 'Gm/D')], vel=54, lo=53, hi=72)
dyn(['vln2', 'vla'], 132.0, 134.0, 50, 64)
# Greninja springs into action (134.1): horns call, strings surge
dyn(['hn'], 134.0, 135.2, 80, 108)
S.mel('hn', Sec(134.05, 120), 0, 'A3:.5 D4:.5 A4:1.5', vel=96)
S.gliss('vln1f', 134.1, 135.0, 'D4', 'D6', 84, scale=[2, 4, 5, 7, 9, 10, 0])
S.n('taiko', 135.04, 0.5, 'C3', 92)
S.n('timp', 135.04, 0.6, 'D2', 84)
S.n('timp', 135.875, 0.6, 'A1', 70)
# underwater: low ostinato, harp ripples
U = Sec(136.0, 108)
setv(['vcf', 'cb'], 135.9, 80)
for k in range(6):
    S.mel('vcf', U, k * 0.5, 'D3:.5 A2:.5 F3:.5 A2:.5', vel=66 + k * 3, legato=0.6) if False else None
for k in range(5):
    t = U.t(0, k * 1.0)
    for j, p in enumerate(('D3', 'A2', 'F3', 'A2')):
        S.n('vcf', t + j * U.d(0.25), U.d(0.22), p, 64 + k * 4)
    S.n('cb', t, U.d(0.9), 'D2', 60 + k * 4)
for i in range(10):
    S.n('harp', 136.05 + i * 0.28, 0.6, ['D5', 'F5', 'A5', 'E5', 'G5', 'C6', 'A5', 'F5', 'D6', 'A5'][i], 44)
S.n('cel', 137.6, 1.0, 'D6', 40)
# I2 Greninja surfaces holding the Star (139.3) - hope! (Pallet Town in the horns) ... then the light is gone (144)
J = Sec(139.3, 84)
setv(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn'], 139.2, 60)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], 139.3, 141.5, 60, 84)
dyn(['hn'], 140.2, 143.6, 118, 127)
S.mel('hn', J, 0, 'r:1 D5:.5 C5:.5 Bb4:.5 A4:.5 G5:.5 E5:.5', vel=108, oct=-1)
S.mel('hn', J, 1, 'F5:.5 E5:.5 D5:1.5 r:2', vel=108, oct=-1)
S.mel('vln1', J, 0, 'r:1 A5:1 Bb5:1 C6:1', vel=66)
S.mel('vln1', J, 1, 'D6:2 r:2', vel=84)
strings_pad(J, [(0, 0, 2, 'F'), (0, 2, 2, 'Bb'), (1, 0, 2, 'F/A'), (1, 2, 1.0, 'C')], vel=76, lo=55, hi=77)
S.arp('harp', J, [(0, 0, 2, 'F'), (0, 2, 2, 'Bb'), (1, 0, 2, 'F')], step=0.25, vel=56, lo=53, hi=84)
S.n('perc', J.t(1), 2.0, 59, 60)
# 144.0: realisation - the chord sours, the Star motif can't finish
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], 143.6, 146.8, 92, 40)
for p, ins in (('Bb1', 'cb'), ('Bb2', 'vc'), ('F3', 'vla'), ('Db4', 'vln2'), ('F4', 'vln2'), ('Bb4', 'vln1')):
    S.n(ins, 143.9, 3.2, p, 66)
star_motif(144.5, vel=62, notes=('A5', 'D6', 'E6'), shimmer=False)
S.n('cel', 144.5 + 3 * 0.22, 1.2, 'Eb6', 48)
dyn(['ob'], 145.0, 147.0, 70, 50)
S.mel('ob', Sec(145.2, 66), 0, 'Db5:1 C5:1 Bb4:2', vel=70)
# I3 Garchomp's apology - the Pokémon Center theme as comfort (147 - 152.3), D major, 84 bpm
K = Sec(147.0, 100)
setv(['vln1', 'vln2', 'vla', 'vc', 'cb'], 146.9, 50)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], 147.0, 148.6, 40, 66)
center = 'D5:.5 A4:.5 D5:.5 A5:1 G5:1 F#5:.5 E5:.5 C#5:1.5 A4:1 E4:1 D5:2'
S.mel('piano', K, 0, center, vel=70)
S.mel('cel', K, 0, center, vel=46, oct=1)
cprog = [(0, 0, 4, 'D'), (1, 0, 2, 'A/C#'), (1, 2, 2, 'A7'), (2, 0, 2, 'D')]
strings_pad(K, cprog, vel=60, lo=50, hi=72)
for bar, bt, ln, sym in cprog:
    b = bass_of(sym, 38, 50)
    S.n('piano', K.t(bar, bt), K.d(ln), b, 54)
    for j, q in enumerate(voicing(sym, 55, 67, 3)):
        S.n('piano', K.t(bar, bt + 0.5 + j * 0.5), K.d(ln - 0.5 - j * 0.5), q, 44)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], 151.4, 152.6, 66, 10)


# ======================================================================
# The Festival Star theme (original), D major, 16 bars
# ======================================================================
THEME = ['D5:1.5 A4:.5 D5:1 F#5:1', 'B5:3 A5:1', 'G5:1 F#5:1 E5:1 F#5:.5 G5:.5', 'A5:4',
         'D5:1.5 A4:.5 D5:1 F#5:1', 'D6:3 C#6:.5 B5:.5', 'A5:1 G5:1 F#5:1 E5:1', 'D5:4',
         'G5:1.5 F#5:.5 E5:1 G5:1', 'B5:2 A5:1 G5:1', 'F#5:1.5 E5:.5 D5:1 F#5:1', 'A5:3 A5:.5 B5:.5',
         'C6:2 B5:1 A5:1', 'B5:2 A5:1 G5:1', 'F#5:1 A5:1 E5:1.5 D5:.5', 'D5:4']
THEME_H = ['D', 'G', ['Em7', 'A7'], 'D', 'D', 'Bm', ['G', 'A7'], 'D',
           'G', 'Em', 'D/F#', ['Bm', 'A'], 'C', 'G', ['D/A', 'A7'], 'D']


def theme(sec, bar0, idx, mel_ins, vel=90, oct=0, harm=True, pad_vel=76, brass_pad=False, harp=True, bass_ins=('cb', 'vc')):
    for k, i in enumerate(idx):
        for ins in mel_ins:
            o = oct + (ins == 'vc') * -1 + (ins in ('tbn', 'hn')) * -1
            S.mel(ins, sec, bar0 + k, THEME[i], vel=vel, oct=o)
        if harm:
            prog = bars(bar0 + k, [THEME_H[i]])
            S.pad(['vla', 'vln2', 'vln2'], sec, prog, pad_vel, 55, 74, 3)
            for b_ins in bass_ins:
                S.bassline(b_ins, sec, prog, pad_vel, 33 if b_ins == 'cb' else 45, 47 if b_ins == 'cb' else 59)
            if brass_pad:
                S.pad(['tbn', 'hn', 'hn'], sec, prog, pad_vel - 6, 48, 67, 3)
            if harp:
                S.arp('harp', sec, prog, step=0.25, vel=52, lo=50, hi=86)


# ======================================================================
# ACT III - JOURNEY
# ======================================================================
# J. golden hour: Pikachu's sparks can't relight the Star (153 - 162)
setv(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'trem', 'choir', 'oohs'], 152.9, 40)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], 153.0, 154.5, 30, 70)
Jg = Sec(153.0, 60)
strings_pad(Jg, [(0, 0, 1.6, 'Bm'), (0, 1.6, 1.7, 'Gmaj7')], vel=60, lo=54, hi=76)
dyn(['solovn'], 153.2, 156.3, 84, 70)
S.mel('solovn', Sec(153.3, 66), 0, 'B4:1.5 F#4:.5 B4:1 D5:1', vel=74)          # the theme's head, in minor
dyn(['trem'], 156.3, 159.0, 20, 112, 'exp')
for p in ('F#3', 'B3', 'D4', 'F#4', 'B4'):
    S.n('trem', 156.3, 2.74, p, 70)
dyn(['oohs'], 156.3, 159.0, 20, 96, 'exp')
for p in ('F#4', 'B4', 'D5'):
    S.n('oohs', 156.3, 2.74, p, 60)
S.roll('timp', 156.4, 159.0, 'F#2', 20, 100)
S.roll('perc', 157.6, 159.0, 59, 10, 80)
star_motif(157.44, vel=58, notes=('A5', 'D6'), shimmer=False)
star_motif(157.70, vel=66, notes=('A5', 'D6', 'E6'), shimmer=False)
star_motif(158.36, vel=76, notes=('A5', 'D6', 'E6'), shimmer=False)
S.n('glock', 158.36 + 0.48, 0.6, 'A6', 42)                 # ...so close
# 159.04 it dies
dyn(['trem', 'oohs'], 159.0, 159.25, 112, 0)
S.n('cb', 159.05, 2.6, 'B1', 60)
for i, p in enumerate(('E6', 'D6', 'A5')):
    S.n('cel', 159.1 + i * 0.4, 1.2, p, 60 - i * 8)
S.bend('cel', 159.8, 160.8, 0, -100)
S.bend('cel', 161.5, 161.6, -100, 0)
setv(['vc'], 159.5, 84)
dyn(['vc'], 159.6, 162.2, 88, 64)
S.mel('vc', Sec(159.6, 64), 0, 'D4:1 C#4:.5 B3:.5 A#3:1 B3:1.5', vel=80)        # lament
S.n('vla', 159.7, 2.3, 'F#3', 50)
S.n('vln2', 159.7, 2.3, 'D4', 46)
# J2 Dragonite's idea (162 - 168): the fanfare cell, then a rising swell
S.mel('bsn', Sec(162.4, 140), 0, 'D3.:.5 F#3.:.5 A3.:.5 F#3.:.5 B3.:.5 A3.:1', vel=62)  # chatter
dyn(['hn'], 163.1, 165.0, 72, 92)
S.mel('hn', Sec(163.2, 80), 0, 'D4:.5 D4:.5 A4:2', vel=88)
S.mel('hn', Sec(163.2, 80), 0, 'A3:.5 A3:.5 D4:2', vel=78)
S.n('timp', 163.2, 0.3, 'D2', 66)
S.n('timp', 163.575, 0.3, 'D2', 60)
S.n('timp', 163.95, 0.5, 'A2', 70)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], 163.2, 167.8, 50, 100, 'exp')
Jh = Sec(163.2, 75)
strings_pad(Jh, [(0, 0, 2, 'D'), (0, 2, 2, 'Bb'), (1, 0, 1.5, 'C')], vel=72, lo=57, hi=81)
S.gliss('harp', 166.5, 167.7, 'C4', 'C7', 54, scale=[0, 2, 4, 7, 9])

# K1. the distant peak: Charizard asleep (168 - 172)
setv(['hn', 'bsn', 'tbn', 'cb', 'vc', 'trem'], 167.9, 70)
setv(['hn'], 167.95, 124)
dyn(['cb', 'vc'], 167.9, 168.6, 40, 70)
S.n('cb', 168.0, 4.2, 'D1', 48)
S.n('vc', 168.0, 4.2, 'D2', 60)
S.n('pad', 168.0, 4.2, 'D3', 50)
S.n('pad', 168.0, 4.2, 'A3', 46)
CZ = Sec(168.1, 60)
S.mel('hn', CZ, 0, 'D3:1 A3:1 Bb3:1.5 A3:.5', vel=96)        # Charizard's motif
S.mel('bsn', CZ, 0, 'D3:1 A3:1 Bb3:1.5 A3:.5', vel=60, oct=-1)
S.n('timp', 168.1, 1.5, 'D2', 40)

# K2. take-off (172 - 178): the title fanfare becomes the flight ostinato
TK = Sec(172.0, 100)
setv(['vln2f', 'vlaf', 'hn', 'vln1', 'vc', 'cb', 'tbn'], 171.9, 60)
dyn(['vln2f', 'vlaf'], 172.0, 177.9, 60, 116, 'exp')
dyn(['hn', 'vc', 'cb', 'tbn'], 172.5, 177.9, 50, 108, 'exp')
fan = ['A4', 'Bb4', 'A4', 'F#4', 'A4', 'Bb4', 'C5', 'C#5']
for k in range(10):
    bar, bt = k // 2, (k % 2) * 2
    top = fan[k % 8]
    for ins, sh in (('vln2f', 0), ('vlaf', -12)):
        S.n(ins, TK.t(bar, bt) + 0.0, TK.d(0.45), P('D4') + sh + 12, 76 + k * 3)
        S.n(ins, TK.t(bar, bt + 0.5), TK.d(0.45), P('D4') + sh + 12, 70 + k * 3)
        S.n(ins, TK.t(bar, bt + 1), TK.d(0.95), P(top) + sh + 12, 82 + k * 3)
    S.n('timp', TK.t(bar, bt), 0.3, 'D2', 50 + k * 5)
    S.n('timp', TK.t(bar, bt + 0.5), 0.3, 'D2', 44 + k * 5)
S.n('hn', 172.5, 5.5, 'D4', 70)
S.n('hn', 172.5, 5.5, 'A4', 66)
S.n('vc', 172.5, 5.5, 'D3', 70)
S.n('cb', 172.5, 5.5, 'D2', 70)
S.n('tbn', 174.4, 3.6, 'A2', 66)
S.gliss('harp', 173.6, 174.6, 'D3', 'D7', 60)              # lift-off
S.roll('perc', 176.6, 178.0, 59, 20, 100)
S.gliss('vln1', 176.6, 177.9, 'A4', 'A5', 70)
dyn(['vln1'], 176.6, 177.9, 60, 110)

# K3. soaring across the valley (178 - 187): THE FESTIVAL STAR THEME
SO = Sec(178.0, 120)
setv(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tpt', 'tbn'], 177.95, 110)
S.n('perc', 178.0, 3.0, 57, 104)
S.n('perc', 178.0, 1.0, 35, 96)
S.n('timp', 178.0, 1.0, 'D2', 104)
theme(SO, 0, [0, 1, 2, 3], ['vln1', 'hn'], vel=100, pad_vel=86, brass_pad=False)
S.mel('tpt', SO, 2, THEME[2], vel=88)
S.mel('tpt', SO, 3, 'A4:4', vel=84)
S.mel('vc', SO, 0, 'r:2 D4:1 C#4:1 B3:3 C#4:1 B3:1 A3:1 G3:1 A3:1 F#3:4', vel=84)   # countermelody
for b in range(4):
    S.n('timp', SO.t(b), 0.6, 'D2' if b != 1 else 'G2', 80)
    S.n('timp', SO.t(b, 2), 0.4, 'A2' if b != 1 else 'D2', 66)
S.n('perc', SO.t(2), 2.0, 57, 70)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tpt'], 185.0, 187.4, 110, 40)
S.gliss('harp', 186.0, 187.0, 'A6', 'D3', 56)

# K4. the ledge: Charizard snoring; Dragonite lands softly (187 - 195)
setv(['bsn', 'vla', 'vc', 'cb', 'vln1'], 187.3, 50)
LD = Sec(187.4, 60)
for k in range(3):                                  # snore: in... out
    t = 187.6 + k * 2.4
    S.n('bsn', t, 1.0, 'D2', 50)
    S.n('bsn', t + 1.1, 1.0, 'C2', 44)
    S.bend('bsn', t + 1.1, t + 2.0, 0, -80)
    S.bend('bsn', t + 2.05, t + 2.1, -80, 0)
dyn(['vla', 'vc', 'cb'], 187.4, 189.0, 30, 56)
for p, ins in (('D2', 'cb'), ('A2', 'vc'), ('F3', 'vla')):
    S.n(ins, 187.4, 7.6, p, 56)
S.gliss('harp', 189.2, 191.5, 'D6', 'D4', 46, scale=[2, 4, 5, 7, 9])
S.n('pizz', 191.6, 0.4, 'D2', 70)
S.n('timp', 191.65, 0.6, 'D2', 44)
dyn(['vln1'], 192.4, 194.9, 20, 46)
S.n('vln1', 192.4, 2.6, 'A6', 46)

# K5. tiptoe... poke... SNORT (195 - 202)
TT = Sec(195.0, 120)
S.mel('vlnpizz', TT, 0, 'D5:.5 r:.5 F5:.5 r:.5 A5:.5 r:.5 G#5:.5 r:.5', vel=70)
S.mel('pizz', TT, 0, 'D3:.5 r:.5 A2:.5 r:.5 D3:.5 r:.5 A2:.5 r:.5', vel=72)
S.mel('bsn', TT, 0, 'D3.:.5 r:.5 r:.5 F3.:.5 r:.5 r:.5 E3.:.5 Eb3.:.5', vel=60)
S.mel('vlnpizz', TT, 1, 'A5:.5 r:.5', vel=64)
S.n('xylo', 198.0, 0.3, 'A6', 72)                    # poke!
S.n('vlnpizz', 198.0, 0.2, 'A6', 70)
S.n('cb', 198.3, 0.5, 'D1', 50)                      # an eye opens
S.n('timp', 198.3, 0.6, 'D1' if False else 'D2', 40)
setv(['tbn', 'tuba'], 198.7, 110)
for p, ins in (('D2', 'tbn'), ('A2', 'tbn'), ('D1', 'tuba')):
    S.n(ins, 198.82, 0.75, p, 110)                   # SNORT
S.bend('tbn', 198.9, 199.55, 0, -150)
S.bend('tbn', 199.7, 199.75, -150, 0)
S.n('timp', 198.82, 0.6, 'D2', 92)
S.n('perc', 198.82, 0.5, 35, 80)
S.gliss('fl', 198.85, 199.4, 'A6', 'A5', 70)   # Pikachu jumps
dyn(['trem'], 199.6, 201.9, 30, 50)
for p in ('D3', 'Eb3'):
    S.n('trem', 199.6, 2.3, p, 50)

# K6. the promise (202 - 209): a plea... the dragon's gaze softens... it nods, wings spread
setv(['ob', 'vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tbn'], 201.95, 60)
dyn(['ob'], 202.4, 205.8, 80, 70)
S.mel('ob', Sec(202.4, 72), 0, 'A4:1 D5:1 E5:.5 F5:1.5', vel=78)           # the Star motif, in minor
PR = Sec(202.4, 72)
strings_pad(PR, [(0, 0, 1.7, 'Dm'), (0, 1.7, 2.3, 'Bb')], vel=56, lo=53, hi=72)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], 205.6, 208.9, 56, 112, 'exp')
for t, sym, ln in ((205.75, 'Bb', 0.6), (206.35, 'F/A', 0.65), (207.0, 'Gm7', 1.0), (208.0, 'A7sus4', 0.5), (208.5, 'A7', 0.5)):
    v = voicing(sym, 55, 79, 4)
    for ins, p in zip(['vla', 'vln2', 'vln2', 'vln1'], v):
        S.n(ins, t, ln + 0.05, p, 76)
    S.n('cb', t, ln + 0.05, bass_of(sym, 33, 47), 76)
    S.n('vc', t, ln + 0.05, bass_of(sym, 45, 59), 76)
dyn(['hn'], 206.2, 208.9, 84, 110)
S.mel('hn', Sec(206.2, 90), 0, 'Bb3:1 F4:1 G4:1.5 F4:.5', vel=94)           # Charizard's motif, now noble
S.mel('tbn', Sec(206.2, 90), 0, 'Bb2:1 F3:1 G3:1.5 F3:.5', vel=84)
S.n('cel', 205.8, 1.2, 'D6', 56)
S.n('cel', 205.95, 1.2, 'F6', 52)
S.roll('perc', 207.4, 209.0, 59, 20, 96)
S.roll('timp', 207.6, 209.0, 'A1', 30, 100)

# K7. homeward at dusk (209 - 217): the theme's soaring second half
DU = Sec(209.0, 120)
setv(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tpt', 'tbn'], 208.95, 108)
S.n('perc', 209.0, 3.0, 57, 96)
theme(DU, 0, [12, 13, 14, 15], ['vln1', 'hn'], vel=98, pad_vel=84, brass_pad=True)
S.mel('tpt', DU, 0, THEME[12], vel=86)
S.mel('fl', DU, 1, THEME[13], vel=70, oct=1)
for b in range(4):
    S.n('timp', DU.t(b), 0.6, ['C2', 'G2', 'A2', 'D2'][b], 84 - b * 6)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tpt', 'tbn'], 214.6, 216.9, 104, 6)


# ======================================================================
# ACT IV - FESTIVAL NIGHT
# ======================================================================
# L. night vigil (217 - 227): a lullaby among the fireflies, then wingbeats - they're back!
NV = Sec(217.0, 66)
setv(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'fl', 'cl', 'trem'], 216.95, 40)
dyn(['vln2', 'vla', 'vc', 'cb'], 217.0, 218.5, 20, 52)
nprog = [(0, 0, 2, 'C'), (0, 2, 2, 'F/C'), (1, 0, 2, 'C'), (1, 2, 2, 'G7/B')]
strings_pad(NV, nprog, vel=50, lo=52, hi=72)
S.arp('harp', NV, nprog, step=1.0, vel=36, lo=48, hi=72)
lull = 'r:1 G5:.5 F#5:.5 G5:.5 E5:1.5 D5:.5 E5:.5 F5:1 G5:1 F5:.5 E5:.5'
S.mel('cel', NV, 0, lull, vel=60)
S.mel('fl', NV, 0, lull, vel=56, oct=-1)
dyn(['fl'], 217.0, 221.0, 60, 50)
# 221.2 they look up: wings in the dark
dyn(['trem'], 221.2, 224.0, 20, 104, 'exp')
for p in ('G3', 'D4', 'G4', 'B4'):
    S.n('trem', 221.2, 2.9, p, 66)
dyn(['hn'], 222.4, 224.0, 70, 100)
S.mel('hn', Sec(222.5, 100), 0, 'G3:.5 G3:.5 D4:1 G3:.5 G3:.5 Eb4:1', vel=86)
S.roll('timp', 222.6, 224.05, 'G2', 20, 90)
# 224.1 joy!
setv(['vln1', 'vln2', 'vla', 'vc', 'cb'], 224.05, 96)
JY = Sec(224.1, 100)
jprog = [(0, 0, 2, 'F'), (0, 2, 2, 'G')]
strings_pad(JY, jprog, vel=82, lo=55, hi=81)
S.mel('vln1', JY, 0, 'A5:1 C6:1 B5:1 D6:1', vel=88)
S.mel('hn', JY, 0, 'F4:2 G4:2', vel=84)
S.gliss('harp', 224.1, 224.8, 'F3', 'F6', 58, scale=[5, 7, 9, 0, 2])
S.n('perc', 224.1, 2.0, 57, 70)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn'], 225.6, 227.0, 96, 40)

# M. the rekindling (227 - 241)
setv(['trem', 'oohs', 'choir'], 226.9, 30)
dyn(['trem'], 227.0, 228.8, 30, 60)
for p in ('A3', 'E4', 'A4'):
    S.n('trem', 227.0, 4.3, p, 60)
dyn(['oohs'], 227.0, 228.8, 20, 60)
S.n('oohs', 227.0, 4.3, 'E4', 56)
S.n('oohs', 227.0, 4.3, 'A4', 56)
# fire! everything climbs toward the ignition at 231.29
dyn(['trem', 'oohs', 'choir'], 228.8, 231.25, 60, 127, 'exp')
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tbn', 'tpt'], 228.8, 231.25, 50, 120, 'exp')
setv(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tbn', 'tpt'], 228.7, 50)
rise = [(228.8, 'F#m'), (229.35, 'G'), (229.85, 'A'), (230.3, 'Bm'), (230.7, 'C'), (231.0, 'A7sus4')]
prev = None
for k, (t, sym) in enumerate(rise):
    t1 = rise[k + 1][0] if k + 1 < len(rise) else 231.29
    v = voicing(sym, 55 + k, 81 + k, 4, prev)
    prev = v
    for ins, p in zip(['vla', 'vln2', 'vln2', 'vln1'], v):
        S.n(ins, t, t1 - t + 0.03, p, 84)
    for ins, p in zip(['tbn', 'hn', 'hn'], voicing(sym, 50, 67, 3)):
        S.n(ins, t, t1 - t + 0.03, p, 80)
    b = bass_of(sym, 33, 47)
    S.n('cb', t, t1 - t + 0.03, b, 84)
    S.n('vc', t, t1 - t + 0.03, b + 12, 84)
    S.n('choir', t, t1 - t + 0.03, v[-1] - 12, 76)
    S.n('choir', t, t1 - t + 0.03, v[-2] - 12, 76)
S.roll('timp', 228.9, 231.27, 'A1', 30, 124)
S.roll('perc', 229.5, 231.27, 59, 20, 118)
S.gliss('picc', 230.4, 231.2, 'A5', 'A6', 70)
# IGNITION 231.29: tutti D major + the healing jingle in the bells
T0 = 231.29
setv(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tbn', 'tpt', 'choir'], T0 - 0.01, 124)
for ins, ps in (('tpt', ('A4', 'D5', 'F#5')), ('hn', ('D4', 'F#4', 'A4', 'D5')), ('tbn', ('D3', 'A3')), ('tuba', ('D2',)),
                ('vln1', ('D6', 'F#6')), ('vln2', ('A5', 'D5')), ('vla', ('F#4', 'A4')), ('vc', ('D3', 'A3')), ('cb', ('D2',)),
                ('choir', ('D4', 'F#4', 'A4', 'D5'))):
    for p in ps:
        S.n(ins, T0, 2.6, p, 112)
S.n('perc', T0, 4.0, 57, 124)
S.n('perc', T0, 4.0, 49, 116)
S.n('perc', T0, 1.0, 35, 120)
S.n('timp', T0, 1.2, 'D2', 124)
S.gliss('harp', T0 + 0.02, T0 + 0.9, 'D3', 'D7', 76)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tbn', 'tpt', 'choir'], T0 + 0.4, T0 + 2.6, 124, 84)
HEAL = Sec(T0 + 0.25, 120)
for ins, v, o in (('bells', 96, 0), ('glock', 84, 0), ('cel', 90, 0), ('cel', 80, -1)):
    S.mel(ins, HEAL, 0, 'A5:1 A5:1 A5:.5 F#5:.5 D6:1.5', vel=v, oct=o)
for i in range(18):                                     # sparkles
    S.n('glock', T0 + 2.6 + i * 0.09, 0.4, ['A6', 'D7', 'E7', 'F#7', 'A7', 'E7'][i % 6], 56 - i)
# the theme, broad (233.6 ->), then tender on the happy faces (236 ->)
BR = Sec(233.6, 96)
setv(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn'], 233.55, 92)
theme(BR, 0, [0, 1, 2], ['vln1', 'hn'], vel=90, pad_vel=74)
dyn(['hn'], 235.6, 237.2, 92, 30)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], 235.8, 237.0, 92, 66)
S.mel('cl', BR, 1, 'D5:2 C#5:1 D5:1', vel=60)
S.mel('fl', BR, 2, 'B5:1 A5:1 G5:1 A5:1', vel=62)
star_motif(236.8, vel=66, notes=('D6', 'F#6', 'A6'))     # Sobble's happy tears
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb'], 239.6, 241.0, 66, 56)

# N. Dragonite carries the Star home; the lanterns (241 - 256)
setv(['vln1', 'vln2', 'vla', 'vc', 'cb', 'choir', 'hn', 'tbn', 'tpt'], 240.95, 56)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb', 'choir', 'hn'], 241.0, 246.35, 56, 120, 'exp')
up = [(241.0, 'D'), (242.1, 'Em'), (243.2, 'F#m'), (244.25, 'G'), (245.3, 'A7sus4'), (245.9, 'A7')]
prev = None
for k, (t, sym) in enumerate(up):
    t1 = up[k + 1][0] if k + 1 < len(up) else 246.42
    v = voicing(sym, 57 + 2 * k, 81 + 2 * k, 4, prev)
    prev = v
    for ins, p in zip(['vla', 'vln2', 'vln2', 'vln1'], v):
        S.n(ins, t, t1 - t + 0.03, p, 80)
    b = bass_of(sym, 33, 47)
    S.n('cb', t, t1 - t + 0.03, b, 80)
    S.n('vc', t, t1 - t + 0.03, b + 12, 80)
    for p in v[1:3]:
        S.n('choir', t, t1 - t + 0.03, p - 12, 72)
    S.arp('harp', Sec(t, 150), [(0, 0, (t1 - t) / 0.4, sym)], step=0.5, vel=54, lo=50 + 2 * k, hi=86, shape='up')
S.mel('hn', Sec(241.0, 100), 0, 'A3:2 D4:2 E4:2 F#4:2 G4:1.5', vel=84)
S.roll('timp', 244.6, 246.4, 'A1', 30, 118)
S.roll('perc', 245.2, 246.4, 59, 20, 110)
# 246.42 the Star is home: crash, bells, the lanterns cascade, the theme in triumph
T1 = 246.42
S.n('perc', T1, 4.0, 57, 124)
S.n('perc', T1, 4.0, 49, 118)
S.n('perc', T1, 1.0, 35, 118)
S.n('timp', T1, 1.0, 'D2', 120)
for i, p in enumerate(('D6', 'F#6', 'A6', 'D7', 'F#7', 'A7')):
    S.n('bells', T1 + i * 0.06, 2.0, p, 80)
_g = _r.Random(33)
lan = ['D6', 'E6', 'F#6', 'A6', 'B6', 'D7', 'E7', 'F#7', 'A7']
for i in range(24):                                   # lantern cascade 246.5 - 247.6
    S.n('glock', 246.5 + i * 0.047, 0.5, lan[min(8, i * 9 // 24)], 60 + _g.randint(0, 16))
    S.n('cel', 246.52 + i * 0.047, 0.6, lan[min(8, i * 9 // 24)], 50)
TR = Sec(T1, 96)
setv(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tpt', 'tbn', 'choir'], T1 - 0.01, 116)
theme(TR, 0, [0, 1, 6, 7], ['vln1', 'hn', 'tpt'], vel=104, pad_vel=92, brass_pad=True)
S.mel('choir', TR, 0, 'D5:4 D5:4 B4:2 C#5:2 A4:4', vel=84)
S.mel('vc', TR, 0, 'r:2 D4:1 C#4:1 B3:2 D4:2 E4:1 D4:1 C#4:2 A3:4', vel=86)
for b in range(4):
    S.n('timp', TR.t(b), 0.6, ['D2', 'G2', 'A2', 'D2'][b], 96)
    S.n('timp', TR.t(b, 2), 0.4, ['A2', 'D2', 'A2', 'A2'][b], 80)
    S.n('perc', TR.t(b), 1.5, 57 if b % 2 == 0 else 49, 84)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tpt', 'tbn', 'choir'], 254.0, 256.3, 116, 70)

# O. the festival dance (256.42 - 269.5): a jig on Route 1 and Pallet Town, 6/8
DJ = Sec(256.42, 330, meter=6)
setv(['fiddle', 'fl', 'cl', 'accord', 'vln1f', 'vln2f'], 256.3, 104)
jig = ['D5:1 E5:1 F#5:1 F#5:2 F#5:1', 'D5:1 E5:1 F#5:1 F#5:2 G5:1', 'A5:2 F#5:1 D5:2 F#5:1', 'E5:3 E5:2 r:1',
       'C#5:1 D5:1 E5:1 E5:2 E5:1', 'C#5:1 D5:1 E5:1 E5:2 F#5:1', 'G5:2 E5:1 C#5:2 E5:1', 'D5:3 A4:2 r:1',
       'A5:1 G5:1 F#5:1 E5:2 D6:1', 'B5:1 C#6:1 B5:1 A5:3', 'G5:1 A5:1 B5:1 A5:1 F#5:1 E5:1', 'D5:3 D6:2 r:1']
jh = ['D', 'D', 'D', 'A', 'A', 'A', 'A7', 'D', 'D', 'G', ['Em', 'A7'], 'D']
for k, ph in enumerate(jig):
    S.mel('fiddle', DJ, k, ph, vel=92, legato=0.85)
    S.mel('fl', DJ, k, ph, vel=60, legato=0.7, oct=1 if k >= 8 else 0)
    if 4 <= k < 8:
        S.mel('cl', DJ, k, ph, vel=66, oct=-1)
    if k >= 8:
        S.mel('xylo', DJ, k, ph, vel=64, oct=1)
for bar, bt, ln, sym in bars(0, jh, beats=6):
    b = bass_of(sym, 38, 50)
    v = voicing(sym, 57, 69, 3)
    for e in range(int(ln)):
        pos = bt + e
        if pos % 3 == 0:
            S.n('pizz', DJ.t(bar, pos), 0.2, b if pos % 6 == 0 else b + 7 if b + 7 < 57 else b - 5, 90)
            S.n('kit', DJ.t(bar, pos), 0.1, 54, 58 if pos % 6 == 0 else 46)       # tambourine
            S.n('perc', DJ.t(bar, pos), 0.2, 45 if pos % 6 == 0 else 41, 70)      # low tom "bodhran"
        else:
            for q in v:
                S.n('accord', DJ.t(bar, pos), DJ.d(0.8), q, 64)
                S.n('vlnpizz', DJ.t(bar, pos), 0.15, q + 12, 50) if pos % 3 == 2 else None
for t in (260.6, 262.9, 265.0):                     # spins & hops
    S.gliss('harp', t, t + 0.75, 'D5', 'D7', 56)
S.n('perc', DJ.t(8), 1.5, 57, 70)

# P. fireworks, the friends together, the end (269.5 - 300) - the R/B ending theme, in D
S.gliss('vln1f', 269.3, 269.95, 'D5', 'D6', 76)
S.roll('perc', 269.3, 270.0, 59, 30, 96)
FW = Sec(270.0, 100)
setv(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tpt', 'tbn', 'choir', 'fl', 'cl', 'ob'], 269.95, 108)
end1 = 'F#5:1.5 F#5:.25 G5:.25 A5:1 F#5:1 C6:1 B5:1 A5:1 G5:1'
end2 = 'F#5:1.5 D5:.5 A5:2 D5:1.5 A4:.5 F#5:2'
end3 = 'G5:1.5 E5:.5 C6:2 C5:1.5 G4:.5 E5:2'
eprog = bars(0, ['D', 'C', 'D', 'D', 'D', 'C', 'D', ['D', 'A/C#'], 'C', ['C', 'A7sus4']])
# 270 - 279.6 majestic (bars 0-3)
S.mel('vln1', FW, 0, end1, vel=100)
S.mel('hn', FW, 0, end1, vel=96, oct=-1)
S.mel('tpt', FW, 0, end1, vel=84)
S.mel('vln1', FW, 2, end2, vel=100)
S.mel('hn', FW, 2, end2, vel=96, oct=-1)
S.mel('tpt', FW, 2, end2, vel=82)
S.pad(['vla', 'vln2', 'vln2'], FW, eprog[:4], 84, 55, 74, 3)
S.pad(['tbn', 'hn', 'hn'], FW, eprog[:4], 74, 48, 64, 3)
S.bassline('cb', FW, eprog[:4], 88, 33, 47)
S.bassline('vc', FW, eprog[:4], 84, 45, 59)
S.arp('harp', FW, eprog[:4], step=0.5, vel=54, lo=50, hi=86)
for b in range(4):
    S.n('timp', FW.t(b), 0.6, 'D2' if eprog[b][3] == 'D' else 'C2', 84)
S.n('perc', 271.875, 2.0, 49, 92)                    # first burst
S.n('perc', 274.21, 2.0, 57, 84)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tpt', 'tbn'], 278.0, 279.6, 108, 64)
# 279.6 - 284.4 side by side, watching: tender (woodwinds, harp)
S.mel('fl', FW, 4, end1, vel=74)
setv(['cl'], 279.4, 56)
S.mel('cl', FW, 4, end1, vel=60, oct=-1)
S.mel('ob', FW, 5, 'r:4 E5:1 D5:1 C5:1 B4:1', vel=56)
setv(['vln1'], 279.5, 60)
S.pad(['vla', 'vln2', 'vln1'], FW, eprog[4:6], 60, 55, 76, 3)
S.bassline('vc', FW, eprog[4:6], 60, 45, 59)
S.bassline('cb', FW, eprog[4:6], 56, 33, 47)
S.arp('harp', FW, eprog[4:6], step=0.25, vel=46, lo=55, hi=86)
star_motif(281.4, vel=52)
# 284.4 - 289.2 crane up and away: building again
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'choir'], 284.3, 289.0, 64, 112)
S.mel('vln1', FW, 6, end2, vel=96)
S.mel('fl', FW, 6, end2, vel=80, oct=1)
S.mel('hn', FW, 6, end2, vel=88, oct=-1)
S.pad(['vla', 'vln2', 'vln2'], FW, eprog[6:8], 80, 55, 74, 3)
S.pad(['choir', 'choir', 'choir'], FW, eprog[6:8], 70, 55, 72, 3)
S.bassline('cb', FW, eprog[6:8], 84, 33, 47)
S.bassline('vc', FW, eprog[6:8], 80, 45, 59)
S.arp('harp', FW, eprog[6:8], step=0.5, vel=52, lo=50, hi=86)
# 289.2 - 294.0 the grand last phrase (bVII), then a broad cadence to THE END at 295.4
setv(['tpt', 'tbn', 'tuba'], 289.1, 104)
S.mel('vln1', FW, 8, end3, vel=104)
S.mel('hn', FW, 8, end3, vel=100, oct=-1)
S.mel('tpt', FW, 8, end3, vel=90)
S.pad(['vla', 'vln2', 'vln2'], FW, eprog[8:], 90, 55, 76, 3)
S.pad(['tbn', 'hn', 'hn'], FW, eprog[8:], 80, 48, 64, 3)
S.pad(['choir', 'choir', 'choir'], FW, eprog[8:], 80, 55, 72, 3)
S.bassline('cb', FW, eprog[8:], 92, 33, 47)
S.bassline('vc', FW, eprog[8:], 88, 45, 59)
S.bassline('tuba', FW, eprog[8:], 76, 28, 40)
S.arp('harp', FW, eprog[8:], step=0.25, vel=56, lo=50, hi=88)
S.n('timp', FW.t(8), 0.8, 'C2', 96)
S.roll('timp', 293.4, 295.38, 'A1', 40, 120)
S.roll('perc', 294.0, 295.38, 59, 30, 110)
S.mel('vln1', Sec(294.0, 70), 0, 'D6:.75 C#6:.75', vel=100)
S.mel('tpt', Sec(294.0, 70), 0, 'D5:.75 C#5:.75', vel=92)
# THE END - D major, held, with the Star motif and a last harp sweep
TE = 295.4
setv(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tpt', 'tbn', 'tuba', 'choir'], TE - 0.01, 118)
for ins, ps in (('tpt', ('F#4', 'A4', 'D5')), ('hn', ('D4', 'F#4', 'A4')), ('tbn', ('D3', 'A3')), ('tuba', ('D2',)),
                ('vln1', ('D6', 'A5')), ('vln2', ('F#5', 'D5')), ('vla', ('A4', 'F#4')), ('vc', ('D3', 'A3')),
                ('cb', ('D2',)), ('choir', ('D4', 'F#4', 'A4', 'D5'))):
    for p in ps:
        S.n(ins, TE, 4.4, p, 108)
S.n('perc', TE, 4.4, 57, 112)
S.n('perc', TE, 4.4, 49, 100)
S.n('timp', TE, 1.4, 'D2', 116)
S.gliss('harp', TE + 0.05, TE + 1.1, 'D3', 'D7', 70)
dyn(['vln1', 'vln2', 'vla', 'vc', 'cb', 'hn', 'tpt', 'tbn', 'tuba', 'choir'], TE + 0.5, 299.8, 118, 0, 'log')
star_motif(TE + 1.3, vel=74)
S.n('bells', TE + 1.3, 3.0, 'D6', 60)


if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'stems')
    files = S.write_midis(out)
    tot = sum(len(v) for v in S.notes.values())
    print('instruments', len(files), 'notes', tot)
