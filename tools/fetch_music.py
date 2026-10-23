#!/usr/bin/env python3
"""Download CC0 (public domain) music from OpenGameArt into music/cc0/ and write music/catalog.json.
Run on GitHub Actions (the Claude workspace cannot reach the site). Only tracks whose page says CC0 are kept."""
import json, os, re, subprocess, sys, time, urllib.request, html
UA = {'User-Agent': 'Mozilla/5.0 hellurei-content-bot'}
OUT = 'music/cc0'; os.makedirs(OUT, exist_ok=True)
cat = json.load(open('music/catalog.json')) if os.path.exists('music/catalog.json') else []
have = {c['source'] for c in cat}
def get(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40); return r.read()
def dur(p):
    try: return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode().strip())
    except Exception: return 0
pages = []
for pg in range(0, 6):
    u = f'https://opengameart.org/art-search-advanced?keys=&field_art_type_tid%5B%5D=12&field_art_licenses_tid%5B%5D=4&sort_by=count&sort_order=DESC&page={pg}'
    try: t = get(u).decode('utf8', 'ignore')
    except Exception as e: print('list fail', pg, e); break
    pages += re.findall(r'href="(/content/[a-z0-9\-_]+)"', t); time.sleep(1)
pages = list(dict.fromkeys(pages)); print('candidates', len(pages))
for p in pages:
    if len(cat) >= 60: break
    src = 'https://opengameart.org' + p
    if src in have: continue
    try: t = get(src).decode('utf8', 'ignore')
    except Exception as e: print('skip', p, e); continue
    if not re.search(r'CC0', t): print('not CC0', p); continue
    title = html.unescape((re.search(r'<title>(.*?)\|', t, re.S) or [0, p])[1]).strip()
    auth = (re.search(r'/users/[^"]+"[^>]*>([^<]+)<', t) or [0, '?'])[1]
    files = re.findall(r'href="(https://opengameart.org/sites/default/files/[^"]+\.(?:mp3|ogg|wav))"', t)
    if not files: print('no file', p); continue
    f = sorted(files, key=lambda x: (not x.endswith('.mp3'), len(x)))[0]; name = re.sub(r'[^a-z0-9]+', '-', p.split('/')[-1])[:50]
    raw = f'{OUT}/{name}.src'; mp3 = f'{OUT}/{name}.mp3'
    try: open(raw, 'wb').write(get(f.replace(' ', '%20')))
    except Exception as e: print('dl fail', p, e); continue
    d = dur(raw)
    if d < 40 or d > 400: os.remove(raw); print('length', p, d); continue
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-ac', '2', '-ar', '44100', '-b:a', '160k', mp3]); os.remove(raw)
    cat.append({'file': mp3, 'title': title, 'author': auth, 'source': src, 'license': 'CC0', 'seconds': round(d, 1)}); print('ok', title, round(d)); time.sleep(1)
json.dump(cat, open('music/catalog.json', 'w'), ensure_ascii=False, indent=1)
