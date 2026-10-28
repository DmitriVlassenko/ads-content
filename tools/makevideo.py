#!/usr/bin/env python3
"""Build one Hellurei motion-graphics video from a spec.
  python3 tools/makevideo.py specs/<id>.json [--preview] [--stills]   -> videos/<id>.mp4
See CLAUDE.md for the spec format. Randomness (palette, variants, bpm, music style) comes from spec.seed."""
import json, os, random, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from musicgen import make_music
PALS = [  # ink, paper, 5 accents
 ([44, 34, 74], [255, 247, 232], [[255, 107, 90], [255, 205, 70], [90, 170, 235], [120, 214, 176], [255, 160, 200]]),
 ([20, 40, 70], [250, 244, 232], [[255, 122, 48], [255, 208, 60], [30, 190, 170], [70, 130, 255], [255, 140, 170]]),
 ([24, 58, 50], [255, 248, 235], [[240, 84, 60], [255, 214, 90], [120, 200, 240], [190, 224, 80], [190, 160, 240]]),
 ([40, 28, 40], [255, 240, 225], [[230, 60, 140], [255, 184, 0], [0, 190, 220], [60, 200, 120], [255, 120, 100]]),
 ([60, 50, 90], [255, 252, 245], [[255, 170, 140], [250, 226, 120], [150, 210, 250], [150, 225, 190], [200, 170, 245]]),
]
BEATS = {'strobe': 1, 'hero': 5, 'counter': 4, 'card': 4, 'fold': 4, 'grid': 4, 'text': 3, 'end': 6}
def main():
    a = sys.argv[1:]; spec_path = os.path.abspath(a[0]); mode = 'render'
    if '--preview' in a: mode = 'preview'
    if '--stills' in a: mode = 'stills'
    sp = json.load(open(spec_path)); vid = sp['id']; seed = int(sp.get('seed', 1)); rnd = random.Random(seed)
    ink, paper, cols = PALS[sp.get('palette', rnd.randrange(len(PALS)))]
    cols = cols[:]; rnd.shuffle(cols) if sp.get('shuffle_colors', True) else None
    bpm = sp.get('bpm') or rnd.choice([104, 108, 112, 116, 120, 124, 128]); beat = 60 / bpm
    # expand scenes (strobe words become one scene each), assign times on the beat grid
    scenes = []
    for s in sp['scenes']:
        if s['type'] == 'strobe':
            for w in s['words']: scenes.append({'type': 'strobe', 'words': [w], 'beats': s.get('beats', 1)})
        else: scenes.append(dict(s))
    t = 0.0
    for s in scenes:
        s['v'] = rnd.randrange(6); b = s.get('beats', BEATS[s['type']]); s['a'] = round(t, 3); t += b * beat; s['b'] = round(t, 3)
    scenes[-1]['b'] = round(scenes[-1]['b'] + .01, 3)
    dur = round(t, 2); end_t = scenes[-1]['a']
    hits = [[s['a'], 1.4 if s['type'] == 'end' else 1.2 if (i == 3 and s['type'] == 'hero') else 1] + ([22] if s['type'] == 'end' else []) for i, s in enumerate(scenes)]
    for s in scenes:
        if s['type'] not in ('strobe', 'end') and (s['b'] - s['a']) > 3.5 * beat: hits.append([round(s['a'] + 2 * beat, 3), .5])
    hits.sort()
    P = os.path.join(REPO, 'build', vid); shutil.rmtree(P, ignore_errors=True); os.makedirs(P + '/img')
    photos = {}
    for k, src in sp['photos'].items():
        src = src if os.path.isabs(src) else os.path.join(REPO, src); dst = f'img/{k}.jpg'; shutil.copy(src, os.path.join(P, dst)); photos[k] = dst
    SPEC = {'pal': {'ink': ink, 'paper': paper, 'c': cols}, 'photos': photos, 'scenes': scenes, 'duration': dur, 'hits': hits, 'seed': seed}
    html = open(os.path.join(HERE, 'template.html')).read().replace('/*SPEC*/', 'const SPEC=' + json.dumps(SPEC) + ';')
    open(P + '/index.html', 'w').write(html); shutil.copy(os.path.join(HERE, 'kinetic/engine.js'), P)
    cuts = [s['a'] for s in scenes]; first_groove = next((s['a'] for s in scenes if s['type'] not in ('strobe',)), 0)
    m = sp.get('music', {}); wav = P + '/audio.wav'
    if m.get('file'):
        make_music(P + '/fx.wav', dur, bpm, cuts, [end_t], end_t, seed, groove_from=first_groove, only_fx=True)
        f = m['file'] if os.path.isabs(m['file']) else os.path.join(REPO, m['file']); ss = m.get('start', 0)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(ss), '-t', str(dur), '-i', f, '-i', P + '/fx.wav', '-filter_complex',
                        f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.8,afade=t=in:d=0.3,afade=t=out:st={dur-1.2}:d=1.2[a];[a][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.95', '-ac', '2', '-ar', '48000', wav], check=True)
        style = 'file:' + os.path.basename(f)
    else: style = make_music(wav, dur, bpm, cuts, [end_t], end_t, seed, m.get('style'), groove_from=first_groove)
    cov = next((s for s in scenes if s['type'] in ('hero','card','counter','grid')), scenes[0]); cover_ms = int((cov['a'] + 1.0) * 1000)
    open(P + '/cover_ms.txt', 'w').write(str(cover_ms)); print('COVER thumbnailOffset ms:', cover_ms)
    print(f'video {vid}: {dur}s, {len(scenes)} scenes, bpm {bpm}, music {style}, palette ok')
    B = os.path.join(HERE, 'kinetic/build.py')
    if mode == 'stills': subprocess.run([sys.executable, B, P, 'stills'], check=True); print('sheet:', P + '/stills_sheet.jpg'); return
    if mode == 'preview': subprocess.run([sys.executable, B, P, 'preview'], check=True); return
    subprocess.run([sys.executable, B, P, 'render', '--max-mb', '20'], check=True)
    os.makedirs(REPO + '/videos', exist_ok=True); shutil.copy(P + '/out.mp4', f'{REPO}/videos/{vid}.mp4'); shutil.copy(P + '/qa_sheet.jpg', f'{REPO}/build/{vid}_qa_sheet.jpg')
    print('DONE videos/%s.mp4  (Buffer thumbnailOffset = %d ms)' % (vid, cover_ms))
main()
