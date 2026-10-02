import mido, sys
NN = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']
def nm(n): return f"{NN[n%12]}{n//12-1}"
m = mido.MidiFile(sys.argv[1]); tpb = m.ticks_per_beat
maxbeats = float(sys.argv[2]) if len(sys.argv) > 2 else 32
print(sys.argv[1], 'tpb', tpb, 'tracks', len(m.tracks))
for i, tr in enumerate(m.tracks):
    t = 0; notes = []; on = {}; prog = None; ch = None
    for msg in tr:
        t += msg.time
        if msg.type == 'program_change': prog = msg.program
        if msg.type == 'set_tempo' and t == 0: print('  tempo', mido.tempo2bpm(msg.tempo))
        if msg.type == 'note_on' and msg.velocity > 0:
            on[(msg.channel, msg.note)] = t; ch = msg.channel
        elif msg.type in ('note_off', 'note_on') and (msg.channel, getattr(msg,'note',None)) in on:
            s = on.pop((msg.channel, msg.note)); notes.append((s, t - s, msg.note))
    notes.sort()
    if not notes: continue
    notes = [n for n in notes if n[0] / tpb < maxbeats]
    print(f' track {i} ch {ch} prog {prog} n={len(notes)}')
    print('   ' + ' '.join(f"{nm(p)}@{s/tpb:g}:{d/tpb:.2g}" for s, d, p in notes[:90]))
