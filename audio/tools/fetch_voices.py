# Rebuild audio/cries/extra/ from the sources listed in audio/cries/extra/INDEX.md.
# Each row names the target file, the original file inside a game rip, and where the rip lives.
# Clips are converted to 48 kHz stereo WAV, trimmed of silence (-55 dB) and peak-normalised to -1 dBFS.
#   python3 audio/tools/fetch_voices.py [--only pikachu] [--keep-zips]
import os, re, sys, io, zipfile, subprocess, urllib.request, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRA = os.path.join(HERE, '..', 'cries', 'extra')
CACHE = os.path.join(HERE, '..', 'cries', '_zips')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36'


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    return urllib.request.urlopen(req, timeout=120).read()


def rip_zip(page):
    """sounds.spriters-resource.com asset page -> local path of its zip (cached)"""
    os.makedirs(CACHE, exist_ok=True)
    aid = page.rstrip('/').split('/')[-1]
    dst = os.path.join(CACHE, aid + '.zip')
    if not os.path.exists(dst):
        html = get(page).decode('utf-8', 'ignore')
        m = re.search(r'href="(/media/assets/[^"]+\.zip[^"]*)"', html)
        if not m:
            raise RuntimeError('no download link on ' + page)
        print('  downloading', page)
        open(dst, 'wb').write(get('https://sounds.spriters-resource.com' + m.group(1)))
    return dst


def convert(raw, out):
    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(raw[0])[1] or '.bin', delete=False) as f:
        f.write(raw[1])
        src = f.name
    try:
        trim = ('silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.005,areverse,'
                'silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.005,areverse')
        tmp = out + '.tmp.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', trim, '-ar', '48000', '-ac', '2', tmp], check=True)
        # peak-normalise to -1 dBFS with plain gain
        vol = subprocess.run(['ffmpeg', '-v', 'info', '-i', tmp, '-af', 'volumedetect', '-f', 'null', '-'],
                             capture_output=True, text=True).stderr
        mx = float(re.search(r'max_volume:\s*(-?[\d.]+) dB', vol).group(1))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', f'volume={-1.0 - mx}dB', '-c:a', 'pcm_s16le', out],
                       check=True)
        os.remove(tmp)
    finally:
        os.remove(src)


def main():
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    rows = []
    for line in open(os.path.join(EXTRA, 'INDEX.md'), encoding='utf-8'):
        c = [x.strip() for x in line.split('|')]
        if len(c) >= 7 and c[1].startswith('`') and '/' in c[1]:
            rows.append((c[1].strip('`'), c[4].strip('`'), c[5]))
    ok = fail = 0
    for target, orig, src in rows:
        if only and not target.startswith(only):
            continue
        out = os.path.join(EXTRA, target)
        if os.path.exists(out):
            ok += 1
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        try:
            if src.endswith('.ogg') or 'raw.githubusercontent' in src:
                raw = (src, get(src))
            else:
                z = zipfile.ZipFile(rip_zip(src))
                names = [n for n in z.namelist() if os.path.basename(n).lower() == orig.lower()]
                if not names:
                    raise RuntimeError(f'{orig} not found in {src}')
                raw = (names[0], z.read(names[0]))
            convert(raw, out)
            ok += 1
        except Exception as e:
            print('  FAILED', target, '-', e)
            fail += 1
    if '--keep-zips' not in sys.argv and os.path.isdir(CACHE):
        for f in os.listdir(CACHE):
            os.remove(os.path.join(CACHE, f))
        os.rmdir(CACHE)
    print(f'voice clips ready: {ok}, failed: {fail}')


if __name__ == '__main__':
    main()
