"""Original synthesized soundtrack, locked to the video's cut list. Own work = no copyright problems.
make_music(out_wav, duration, bpm, cuts, hits_big, end_t, seed, style=None, groove_from=None)
Styles: bouncy | dreamy | funk | chill  (random from seed if None).  Returns the style name."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kinetic'))
from audio_lib import Mix, note as n, chord, scale
NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
def nm(root, semis): return NAMES[(NAMES.index(root) + semis) % 12]
STYLES = {
    'bouncy': dict(prog=[(0, ''), (9, 'm'), (5, ''), (7, '')], arp='pluck', step=.25, drums=True, swing=0, scale='pentatonic'),
    'dreamy': dict(prog=[(0, 'maj7'), (4, 'm7'), (5, 'maj7'), (7, '')], arp='bell', step=.5, drums=True, swing=0, scale='lydian'),
    'funk':   dict(prog=[(2, 'm7'), (7, '7'), (0, 'maj7'), (9, '7')], arp='pluck', step=.25, drums=True, swing=.12, scale='dorian'),
    'chill':  dict(prog=[(0, 'maj9'), (9, 'm7'), (2, 'm7'), (7, '7')], arp='pluck', step=.5, drums=True, swing=.2, scale='pentatonic'),
}
def make_music(out, duration, bpm, cuts, big_hits, end_t, seed=1, style=None, groove_from=None, only_fx=False):
    rnd = random.Random(seed); style = style or rnd.choice(list(STYLES)); S = STYLES[style]
    key = rnd.choice(['C', 'D', 'F', 'G', 'A', 'Eb']); beat = 60 / bpm
    m = Mix(duration=duration, bpm=bpm, seed=seed)
    g0 = groove_from if groove_from is not None else (cuts[3] if len(cuts) > 3 else 1.5)
    # impact on every cut
    for i, c in enumerate(cuts):
        early = c < g0
        m.boom(c, .26 if c not in big_hits else .5)
        m.bell(c, n([0, 4, 7, 12, 9, 14][i % 6] + {'C': 0, 'D': 2, 'F': 5, 'G': 7, 'A': 9, 'Eb': 3}[key]), .16 if early else .11, 1.0)
        if not early: m.whoosh(c, .45, .12)
        if early: m.clap(c, .05)
    if g0 > 0: m.riser(g0, min(.6, g0), .1)
    if not only_fx:
        t = g0; k = 0
        while t < end_t:
            d, q = S['prog'][(k // 1) % 4]; bar_t0 = t
            name = nm(key, d) + q; fr = chord(name, 3)
            t1 = min(t + 4 * beat, duration)
            m.pad(fr, t, t1, amp=.05)
            hi = chord(name, 4, bass=False); hi = hi + [hi[0] * 2, hi[1] * 2]
            m.arp(t, t1, hi, step=S['step'] * beat * 2, amp=.09, voice=S['arp'], order=rnd.choice(['up', 'up', 'down']))
            if style == 'chill': m.chord_hit(t, chord(name, 4), voice='piano', amp=.06, dur=2.0)
            for j in range(4):
                tt = t + j * beat
                if tt >= end_t or tt >= duration: break
                m.kick(tt, .2 if style != 'dreamy' else .15)
                if j % 2 == 1: m.clap(tt, .07)
                m.hat(tt + beat / 2 + (S['swing'] * beat / 2), .03)
                m.bass(tt, chord(name, 2, bass=False)[0], amp=.12)
            t += 4 * beat; k += 1
        # sparkle melody over the middle
        sc = scale(key, S['scale'], 5, n=10)
        mt = g0 + 2 * beat
        while mt < end_t - 4 * beat:
            m.bell(mt, sc[rnd.randrange(len(sc))], .07, .9); mt += beat * rnd.choice([1, 1.5, 2])
        # build-up and landing on the end card
        m.riser(end_t, min(1.2, 2 * beat), .16)
        for q in (-1, -.5, -.25): m.snare(end_t + q * beat * 1.0, .07)
        m.chord_hit(end_t, chord(key, 4) + [n(12)], voice='piano', amp=.09, dur=2.5); m.sub(end_t, chord(key, 2, bass=False)[0], .3, 1.2)
        tt = end_t + beat
        sc2 = scale(key, S['scale'], 5, n=8)
        while tt < duration - .5:
            m.kick(tt, .17); m.bell(tt + beat / 2, sc2[rnd.randrange(len(sc2))], .08, 1.2); tt += beat
    m.render(out)
    return style
