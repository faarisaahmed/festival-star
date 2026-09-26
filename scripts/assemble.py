import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + '/'
# Encode each shot, then join into the final movie with fades at act breaks.
import os, re, subprocess, sys
src = open(ROOT + 'scripts/shots.py').read()
shots = sorted((m.group(1), int(m.group(2))) for m in re.finditer(r"@shot\('(\w+)', (\d+)", src) if m.group(1) != 'test')
# fade to/from black around act boundaries and at the very start/end
FADE_OUT = {'s11_bigfriends': 12, 's23_sorry': 18, 's32_dusk': 18, 's41_finale': 36}
FADE_IN = {'s01_aerial': 30, 's12_game_a': 10, 's24_sparks': 16, 's33_return': 18}
kind = sys.argv[1] if len(sys.argv) > 1 else 'final'
os.makedirs(ROOT + 'tmp/enc', exist_ok=True)
parts = []
for name, secs in shots:
    d = ROOT + f'frames/{kind}/{name}/'
    if not os.path.isdir(d) or not os.listdir(d):
        print('missing', name)
        continue
    n = secs * 24
    vf = []
    if name in FADE_IN:
        vf.append(f'fade=t=in:st=0:d={FADE_IN[name] / 24:.3f}')
    if name in FADE_OUT:
        vf.append(f'fade=t=out:st={(n - FADE_OUT[name]) / 24:.3f}:d={FADE_OUT[name] / 24:.3f}')
    out = ROOT + f'tmp/enc/{name}.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-start_number', '1', '-i', d + '%04d.jpg']
    if vf:
        cmd += ['-vf', ','.join(vf)]
    cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', out]
    subprocess.run(cmd, check=True)
    parts.append(out)
    print('encoded', name)
lst = ROOT + 'tmp/enc/list.txt'
open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
final = ROOT + ('The_Festival_Star.mp4' if kind == 'final' else f'preview_{kind}.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', final], check=True)
print('WROTE', final)
