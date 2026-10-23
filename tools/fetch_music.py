#!/usr/bin/env python3
"""Download CC0 (public domain) music from OpenGameArt into music/cc0/ and write music/catalog.json.
Runs on GitHub Actions (the Claude workspace cannot reach the site). Only pages that say CC0 are kept.
Handles direct audio files and zip packs. Log: music/fetch_log.txt"""
import json, os, re, subprocess, time, urllib.request, html, zipfile, io
UA = {'User-Agent': 'Mozilla/5.0 hellurei-content-bot'}
OUT = 'music/cc0'; os.makedirs(OUT, exist_ok=True)
cat = json.load(open('music/catalog.json')) if os.path.exists('music/catalog.json') else []
have = {c['source'] for c in cat}; LOG = []
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
def dur(p):
    try: return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode().strip())
    except Exception: return 0
pages = []
for pg in range(0, 8):
    u = f'https://opengameart.org/art-search-advanced?keys=&field_art_type_tid%5B%5D=12&field_art_licenses_tid%5B%5D=4&sort_by=count&sort_order=DESC&page={pg}'
    try: t = get(u).decode('utf8', 'ignore')
    except Exception as e: LOG.append(f'list fail {pg} {e}'); break
    pages += re.findall(r'href="(/content/[a-z0-9\-_]+)"', t); time.sleep(1)
pages = [p for p in dict.fromkeys(pages) if p not in ('/content/faq',) and 'challenge' not in p]; LOG.append(f'candidates {len(pages)}')
def add(raw, name, title, auth, src):
    d = dur(raw)
    if d < 40 or d > 400: LOG.append(f'length {name} {d}'); return
    mp3 = f'{OUT}/{name}.mp3'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-vn', '-ac', '2', '-ar', '44100', '-b:a', '128k', mp3])
    if os.path.exists(mp3): cat.append({'file': mp3, 'title': title, 'author': auth, 'source': src, 'license': 'CC0', 'seconds': round(d, 1)}); LOG.append(f'ok {title} {round(d)}')
for p in pages:
    if len(cat) >= 40: break
    src = 'https://opengameart.org' + p
    if src in have: continue
    try: t = get(src).decode('utf8', 'ignore')
    except Exception as e: LOG.append(f'skip {p} {e}'); continue
    if 'creativecommons.org/publicdomain/zero' not in t and 'CC0' not in t: LOG.append(f'not CC0 {p}'); continue
    title = html.unescape((re.search(r'<title>(.*?)\|', t, re.S) or [0, p])[1]).strip()
    auth = (re.search(r'/users/[^"]+"[^>]*>([^<]+)<', t) or [0, '?'])[1]
    files = [('https://opengameart.org' + x if x.startswith('/') else x) for x in re.findall(r'(?:href|src)="((?:https?://opengameart\.org)?/sites/default/files/[^"?]+?\.(?:mp3|ogg|wav|zip))(?:\?[^"]*)?"', t, re.I)]
    if not files: LOG.append(f'no file {p}'); continue
    base = re.sub(r'[^a-z0-9]+', '-', p.split('/')[-1])[:40]
    try:
        for k, f in enumerate([x for x in files if not x.lower().endswith('.zip')][:1] or files[:1]):
            data = get(f.replace(' ', '%20'))
            if f.lower().endswith('.zip'):
                z = zipfile.ZipFile(io.BytesIO(data)); n = 0
                for nm in z.namelist():
                    if nm.lower().endswith(('.mp3', '.ogg', '.wav')) and n < 3 and len(cat) < 40:
                        raw = f'{OUT}/tmp_{n}.src'; open(raw, 'wb').write(z.read(nm)); add(raw, f'{base}-{n}', f'{title} / {os.path.basename(nm)}', auth, src); os.remove(raw); n += 1
            else:
                raw = f'{OUT}/tmp.src'; open(raw, 'wb').write(data); add(raw, base, title, auth, src); os.remove(raw)
    except Exception as e: LOG.append(f'fail {p} {e}')
    time.sleep(1)
open('music/fetch_log.txt', 'w').write('\n'.join(LOG))
json.dump(cat, open('music/catalog.json', 'w'), ensure_ascii=False, indent=1)
