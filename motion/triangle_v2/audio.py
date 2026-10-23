from audio_lib import Mix, note as n, chord, scale
DUR, BPM = 15, 120
B = .5
m = Mix(duration=DUR, bpm=BPM)
CH = ['C','Am','F','G','C','Am','F','G']
cuts = [0,.5,1,1.5,4,6,8,10,12]
# intro word hits: rising bells + boom
for i,(t,s) in enumerate([(0,0),(.5,4),(1,7)]):
    m.boom(t,.28); m.bell(t,n(s),.2,.9); m.bell(t,n(s+12),.1,.7); m.clap(t+.0,.05)
m.riser(1.5,.5,.1)
# main groove from 1.5
for k,name in enumerate(CH):
    t0=1.5+k*2
    if t0>=15: break
    t1=min(t0+2,15)
    fr=chord(name,3)
    m.pad(fr,t0,t1,amp=.05)
    pent=chord(name,4,bass=False)
    m.arp(t0,t1,pent+[pent[0]*2,pent[1]*2],step=.25,amp=.09,voice='pluck',order='up')
t=1.5
while t<12.0:
    m.kick(t,.22)
    if int((t-1.5)/.5)%2==1: m.clap(t,.07)
    m.hat(t+.25,.03)
    m.bass(t,chord(CH[int((t-1.5)//2)%8],2,bass=False)[0],amp=.12)
    t+=.5
# cut accents
for c in cuts[3:]:
    m.whoosh(c,.45,.12); m.boom(c,.22 if c<12 else .5); m.bell(c,n(12),.12,1.0)
# melody sparkle in rung/slope/fold/grid scenes
mel=scale('C','pentatonic',5,n=10)
for i,tt in enumerate([4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5]):
    m.bell(tt+.25,mel[[0,2,4,2,5,4,2,1][i]],.08,.8)
# riser into the end card, big hit and tail
m.riser(12.0,1.0,.16); m.snare(11.5,.06); m.snare(11.75,.07); m.snare(11.875,.08)
m.chord_hit(12.0,chord('C',4)+[n(12)],voice='piano',amp=.09,dur=2.5); m.sub(12.0,n(-33),.3,1.2)
for i,tt in enumerate([12.5,13.0,13.5,14.0]):
    m.kick(tt,.18); m.bell(tt+.25,mel[[4,5,6,7][i]],.08,1.2)
m.render('audio.wav')
