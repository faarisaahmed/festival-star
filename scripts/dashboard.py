import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + '/'
# Live render dashboard:  python3 scripts/dashboard.py  ->  http://localhost:8765
import http.server, json, os, re, time, urllib.parse, subprocess

FINAL = ROOT + 'frames/final/'
PORT = 8765
ACTS = [('s01', 'Act I · Morning'), ('s12', 'Act II · The Game'), ('s24', 'Act III · The Journey'), ('s33', 'Act IV · Festival Night')]


def shots():
    src = open(ROOT + 'scripts/shots.py').read()
    out = []
    for m in re.finditer(r"@shot\('(\w+)', (\d+), '(\w+)'[^)]*\)\ndef \w+\(S\):\n\s+\"\"\"(.*?)\"\"\"", src, re.S):
        if m.group(1) == 'test':
            continue
        out.append(dict(name=m.group(1), secs=int(m.group(2)), light=m.group(3), desc=' '.join(m.group(4).split())))
    return sorted(out, key=lambda s: s['name'])


def status():
    sh = shots()
    all_times = []
    total = done = 0
    current = None
    for s in sh:
        n = s['secs'] * 24
        d = FINAL + s['name']
        files = []
        if os.path.isdir(d):
            for f in os.listdir(d):
                p = os.path.join(d, f)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                if st.st_size > 0:
                    files.append((f, st.st_mtime))
        files.sort()
        s['frames'] = n
        s['done'] = min(len(files), n)
        s['latest'] = files[-1][0] if files else None
        all_times += [t for _, t in files]
        total += n
        done += s['done']
        if current is None and s['done'] < n and os.path.isdir(d):
            current = s['name']
    all_times.sort()
    rate = None
    if len(all_times) >= 3:
        recent = all_times[-40:]
        rate = (recent[-1] - recent[0]) / (len(recent) - 1)
    last_t = all_times[-1] if all_times else None
    running = subprocess.run(['pgrep', '-f', 'render_all.sh'], capture_output=True).returncode == 0
    latest = None
    for s in sh:
        if s['latest']:
            p = FINAL + s['name'] + '/' + s['latest']
            t = os.stat(p).st_mtime
            if latest is None or t > latest[2]:
                latest = (s['name'], s['latest'], t)
    return dict(shots=sh, total=total, done=done, rate=rate, eta=(total - done) * rate if rate else None,
                started=all_times[0] if all_times else None, last=last_t, now=time.time(), running=running,
                current=current, latest=latest[:2] if latest else None, acts=ACTS,
                movie=os.path.exists(ROOT + 'The_Festival_Star.mp4'))


PAGE = r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Festival Star · Render</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#0d0f14;--panel:#151922;--line:#232938;--text:#e8eaf0;--mute:#8a93a6;--gold:#ffc94d;--gold2:#ff8a3d;--ok:#5ee3a1}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(1200px 600px at 70% -10%,#2a1f10 0%,transparent 60%),var(--bg);color:var(--text);font:14px/1.5 Inter,system-ui,sans-serif;min-height:100vh}
.wrap{max-width:1280px;margin:0 auto;padding:28px 20px 60px}
header{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:22px}
h1{font:600 34px/1.1 Fraunces,serif;margin:0;letter-spacing:.3px}h1 span{color:var(--gold)}
.sub{color:var(--mute);margin-top:6px}
.pill{display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border-radius:999px;background:var(--panel);border:1px solid var(--line);font-weight:500}
.dot{width:9px;height:9px;border-radius:50%;background:var(--ok);box-shadow:0 0 0 0 rgba(94,227,161,.6);animation:p 1.8s infinite}
.dot.off{background:#ff5d6c;animation:none}@keyframes p{70%{box-shadow:0 0 0 10px rgba(94,227,161,0)}100%{box-shadow:0 0 0 0 rgba(94,227,161,0)}}
.grid{display:grid;grid-template-columns:1.6fr 1fr;gap:18px}@media(max-width:900px){.grid{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px}
.hero img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px;background:#000;display:block}
.cap{display:flex;justify-content:space-between;color:var(--mute);margin-top:10px;font-size:13px;gap:10px}
.big{font:600 56px/1 Fraunces,serif}.big small{font-size:22px;color:var(--mute)}
.bar{height:12px;background:#0a0c10;border-radius:999px;overflow:hidden;border:1px solid var(--line);margin:14px 0 18px}
.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--gold2),var(--gold));border-radius:999px;transition:width .8s}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:12px}.stat{background:#10131a;border:1px solid var(--line);border-radius:12px;padding:12px}
.stat b{display:block;font-size:20px;font-weight:600}.stat span{color:var(--mute);font-size:12px;text-transform:uppercase;letter-spacing:.08em}
.now{margin-top:14px;padding:12px;border-radius:12px;background:linear-gradient(135deg,rgba(255,201,77,.12),rgba(255,138,61,.06));border:1px solid rgba(255,201,77,.25)}
.now .t{font-weight:600}.now .d{color:var(--mute);font-size:13px}
.strip{display:flex;height:34px;border-radius:10px;overflow:hidden;border:1px solid var(--line);margin:18px 0 6px}
.strip div{position:relative;border-right:1px solid #0d0f14;background:#10131a}.strip div i{position:absolute;inset:0 auto 0 0;background:linear-gradient(180deg,var(--gold),var(--gold2))}
.strip div.cur{outline:2px solid var(--gold);outline-offset:-2px;z-index:1}
.acts{display:flex;color:var(--mute);font-size:12px}.acts div{border-left:1px solid var(--line);padding-left:6px;white-space:nowrap;overflow:hidden}
h2{font:600 20px Fraunces,serif;margin:28px 0 12px}
.shots{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.shot{background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.shot.cur{border-color:var(--gold);box-shadow:0 0 0 1px var(--gold)}
.th{aspect-ratio:16/9;background:#0a0c10 center/cover no-repeat;position:relative}
.th .badge{position:absolute;top:8px;left:8px;background:rgba(0,0,0,.65);padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600}
.th .lt{position:absolute;top:8px;right:8px;background:rgba(0,0,0,.65);padding:2px 8px;border-radius:999px;font-size:11px;color:var(--gold)}
.sb{padding:10px 12px}.sb .n{font-weight:600;font-size:13px}.sb .d{color:var(--mute);font-size:12px;height:36px;overflow:hidden}
.mini{height:4px;background:#0a0c10;border-radius:4px;margin-top:8px;overflow:hidden}.mini i{display:block;height:100%;background:var(--gold)}
.done .mini i{background:var(--ok)}
.movie{margin-top:14px;display:none}.movie a{color:var(--gold)}
</style></head><body><div class="wrap">
<header><div><h1>The <span>Festival Star</span></h1><div class="sub">Live render · 1920×1080 · 24 fps · EEVEE</div></div>
<div class="pill"><span class="dot" id="dot"></span><span id="state">connecting…</span></div></header>
<div class="grid">
 <div class="card hero"><img id="latest" alt="latest frame"><div class="cap"><span id="lcap">—</span><span id="lage"></span></div></div>
 <div class="card">
  <div class="big" id="pct">0<small>%</small></div>
  <div class="bar"><i id="bar" style="width:0"></i></div>
  <div class="stats">
   <div class="stat"><span>Frames</span><b id="frames">–</b></div>
   <div class="stat"><span>Seconds / frame</span><b id="rate">–</b></div>
   <div class="stat"><span>Time left</span><b id="left">–</b></div>
   <div class="stat"><span>Finishes around</span><b id="eta">–</b></div>
   <div class="stat"><span>Elapsed</span><b id="elapsed">–</b></div>
   <div class="stat"><span>Movie rendered</span><b id="mins">–</b></div>
  </div>
  <div class="now"><div class="t" id="nowt">—</div><div class="d" id="nowd"></div></div>
  <div class="movie" id="movie">🎬 Movie assembled: <a href="/movie">The_Festival_Star.mp4</a></div>
 </div>
</div>
<div class="strip" id="strip"></div><div class="acts" id="acts"></div>
<h2>Shots</h2><div class="shots" id="shots"></div>
</div>
<script>
const $=id=>document.getElementById(id);
const fmt=s=>{if(s==null)return'–';s=Math.max(0,s);const h=Math.floor(s/3600),m=Math.floor(s%3600/60);return h?`${h}h ${m}m`:`${m}m ${Math.floor(s%60)}s`};
const light={dawn:'🌅',morning:'☀️',noon:'☀️',afternoon:'🌤',golden:'🌇',sunset:'🌇',dusk:'🌆',night:'🌙'};
let lastLatest='';
async function tick(){
 let d;try{d=await (await fetch('/api/status')).json()}catch(e){$('state').textContent='dashboard offline';$('dot').className='dot off';return}
 const pct=d.total?d.done/d.total*100:0;
 $('pct').innerHTML=pct.toFixed(1)+'<small>%</small>';$('bar').style.width=pct+'%';
 $('frames').textContent=`${d.done.toLocaleString()} / ${d.total.toLocaleString()}`;
 $('rate').textContent=d.rate?d.rate.toFixed(1)+' s':'–';
 $('left').textContent=d.eta!=null?fmt(d.eta):'–';
 $('eta').textContent=d.eta!=null?new Date((d.now+d.eta)*1000).toLocaleString([], {weekday:'short',hour:'numeric',minute:'2-digit'}):'–';
 $('elapsed').textContent=d.started?fmt(d.now-d.started):'–';
 $('mins').textContent=`${(d.done/24/60).toFixed(2)} of ${(d.total/24/60).toFixed(0)} min`;
 const stalled=d.last&&d.now-d.last>300;
 $('state').textContent=d.done>=d.total?'All frames rendered':(!d.running?'Renderer not running':stalled?'Working (long frame)…':'Rendering');
 $('dot').className='dot'+(d.running||d.done>=d.total?'':' off');
 $('movie').style.display=d.movie?'block':'none';
 const cur=d.shots.find(s=>s.name===d.current);
 $('nowt').textContent=cur?`Now: ${cur.name}  (${cur.done}/${cur.frames})`:'—';$('nowd').textContent=cur?cur.desc:'';
 if(d.latest){const u=`/frame/${d.latest[0]}/${d.latest[1]}`;if(u!==lastLatest){$('latest').src=u;lastLatest=u}
  $('lcap').textContent=`${d.latest[0]} · frame ${parseInt(d.latest[1])}`;$('lage').textContent=d.last?`${Math.round(d.now-d.last)}s ago`:''}
 $('strip').innerHTML=d.shots.map(s=>`<div title="${s.name}: ${s.done}/${s.frames}" class="${s.name===d.current?'cur':''}" style="flex:${s.frames}"><i style="width:${s.done/s.frames*100}%"></i></div>`).join('');
 const total=d.total;let acc=0,starts={};d.shots.forEach(s=>{d.acts.forEach(a=>{if(s.name.startsWith(a[0]))starts[a[1]]=acc});acc+=s.frames});
 const names=d.acts.map(a=>a[1]);$('acts').innerHTML=names.map((n,i)=>{const a=starts[n]||0,b=i+1<names.length?starts[names[i+1]]:total;return`<div style="flex:${b-a}">${n}</div>`}).join('');
 $('shots').innerHTML=d.shots.map(s=>{const img=s.latest?`background-image:url('/frame/${s.name}/${s.latest}?t=${s.done}')`:'';
  const cls=(s.name===d.current?' cur':'')+(s.done>=s.frames?' done':'');
  return`<div class="shot${cls}"><div class="th" style="${img}"><span class="badge">${s.done>=s.frames?'✓ done':s.done?`${Math.round(s.done/s.frames*100)}%`:'queued'}</span><span class="lt">${light[s.light]||''} ${s.secs}s</span></div>
  <div class="sb"><div class="n">${s.name.replace(/^s(\d+b?)_/,'$1 · ').replace(/_/g,' ')}</div><div class="d">${s.desc}</div><div class="mini"><i style="width:${s.done/s.frames*100}%"></i></div></div></div>`}).join('');
}
tick();setInterval(tick,5000);
</script></body></html>'''


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path).path
        if u == '/':
            return self.send(200, PAGE.encode(), 'text/html; charset=utf-8')
        if u == '/api/status':
            return self.send(200, json.dumps(status()).encode(), 'application/json')
        if u.startswith('/frame/'):
            parts = u.split('/')
            if len(parts) == 4 and re.fullmatch(r'\w+', parts[2]) and re.fullmatch(r'\d+\.jpg', parts[3]):
                p = FINAL + parts[2] + '/' + parts[3]
                if os.path.isfile(p):
                    return self.send(200, open(p, 'rb').read(), 'image/jpeg')
            return self.send(404, b'', 'text/plain')
        if u == '/movie' and os.path.exists(ROOT + 'The_Festival_Star.mp4'):
            return self.send(200, open(ROOT + 'The_Festival_Star.mp4', 'rb').read(), 'video/mp4')
        self.send(404, b'not found', 'text/plain')


if __name__ == '__main__':
    print(f'Dashboard: http://localhost:{PORT}')
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
