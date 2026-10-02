# search / fetch BBC Sound Effects (RemArc licence: personal, educational, research use)
import json, sys, os, urllib.request
API = 'https://sound-effects-api.bbcrewind.co.uk/api/sfx/search'
def search(q, n=8):
    body = json.dumps({'criteria': {'from': 0, 'size': n, 'query': q}}).encode()
    r = urllib.request.Request(API, body, {'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(r))['results']
def fetch(i, dst):
    if not os.path.exists(dst):
        urllib.request.urlretrieve(f'https://sound-effects-media.bbcrewind.co.uk/wav/{i}.wav', dst)
if __name__ == '__main__':
    if sys.argv[1] == 'get':
        fetch(sys.argv[2], sys.argv[3])
    else:
        for q in sys.argv[1:]:
            print('##', q)
            for x in search(q):
                print(f"  {x['id']:>10} {x['duration']/1000:7.1f}s  {x['description'][:110]}")
