import math, os, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 14
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

INK = (52, 44, 66)
CREAM = (255, 246, 234)
PAL = [(255, 138, 128), (129, 212, 180), (130, 190, 235), (255, 214, 102), (190, 160, 235), (255, 171, 118)]
BGS = [(255, 214, 190), (200, 234, 222), (205, 225, 245), (255, 233, 178), (255, 214, 190)]
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F = lambda s: ImageFont.truetype(FB, s)
f_huge, f_big, f_mid, f_small = F(170), F(110), F(76), F(58)
f_t = F(90)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo3(t): return 1 - (1 - clamp(t)) ** 3
def bounce(t):
    t = clamp(t); n1, d1 = 7.5625, 2.75
    if t < 1 / d1: return n1 * t * t
    if t < 2 / d1: t -= 1.5 / d1; return n1 * t * t + .75
    if t < 2.5 / d1: t -= 2.25 / d1; return n1 * t * t + .9375
    t -= 2.625 / d1; return n1 * t * t + .984375
def eob(t, s=1.70158):
    t = clamp(t); return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2

def tcenter(img, txt, font, cy, fill, alpha=1.0, cx=W / 2):
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0, 0), txt, font=font)
    x = cx - (bb[2] - bb[0]) / 2 - bb[0]; y = cy - (bb[3] - bb[1]) / 2 - bb[1]
    if alpha >= .999:
        d.text((x, y), txt, font=font, fill=fill)
    elif alpha > 0:
        L = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(L).text((x, y), txt, font=font, fill=fill + (int(255 * alpha),))
        img.paste(L, (0, 0), L)

def rrect(d, cx, cy, w, h, col, r=26, ang=0):
    if ang == 0:
        d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=r, fill=col)
        d.rounded_rectangle((cx - w / 2 + 14, cy - h / 2 + 14, cx + w / 2 - 14, cy - h / 2 + 36), radius=10, fill=tuple(min(255, v + 28) for v in col))
    else:
        a = math.radians(ang); c, s = math.cos(a), math.sin(a)
        pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
        d.polygon([(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts], fill=col)

# ---- scenes ----
T = [0, 2.4, 5.6, 8.8, 12.0, 14.0]
titles = ["", "1. Rakenna linnake", "2. Tasapainorata", "3. Torni kasaan, torni kumoon"]

def scene_of(t):
    for i in range(5):
        if T[i] <= t < T[i + 1]: return i
    return 4

def draw_scene(img, i, lt):
    d = ImageDraw.Draw(img)
    cx = W / 2
    if i == 0:
        words = ["Sadepäivä?", "Ei hätää."]
        for k, wd in enumerate(words):
            p = eob((lt - 0.2 - k * 0.55) / 0.6)
            tcenter(img, wd, f_huge if k == 0 else f_big, 640 + k * 190 + (1 - p) * 300, INK, alpha=clamp(p * 1.4))
        p = bounce((lt - 1.3) / 0.8)
        if p > 0:
            w, h = 620 * p, 120 * p
            d.rounded_rectangle((cx - w / 2, 1180 - h / 2, cx + w / 2, 1180 + h / 2), radius=60, fill=INK)
            if p > .95: tcenter(img, "3 leikki-ideaa", f_mid, 1180, CREAM)
        for k in range(5):
            rrect(d, 170 + k * 185, 1560 + math.sin(lt * 4 + k) * 14, 130, 130, PAL[k], 30)
    else:
        n = i
        # title text
        p = eob(lt / 0.55)
        tx = titles[n]
        if n == 3:
            tcenter(img, "3. Torni kasaan,", f_t, 330 + (1 - p) * -200, INK, alpha=clamp(p * 1.5))
            tcenter(img, "torni kumoon", f_t, 460 + (1 - p) * -200, INK, alpha=clamp(p * 1.5))
        else:
            tcenter(img, tx, f_t, 380 + (1 - p) * -200, INK, alpha=clamp(p * 1.5))
        gy = 1480  # ground
        d.rounded_rectangle((120, gy, W - 120, gy + 40), radius=20, fill=tuple(int(v * .62) for v in BGS[n]))
        if n == 1:
            # fort wall of blocks building, flag on top
            cols = 5; bw = 150
            x0 = cx - cols * bw / 2 + bw / 2
            order = [(0, 0), (4, 0), (1, 0), (3, 0), (2, 0), (0, 1), (4, 1), (1, 1), (3, 1), (2, 1)]
            for k, (cc, rr) in enumerate(order):
                s0 = 0.5 + k * 0.22
                pp = bounce((lt - s0) / 0.55)
                if lt < s0: continue
                tx_ = x0 + cc * bw; ty = gy - bw / 2 - rr * (bw + 6)
                y = ty - (1 - pp) * 900
                rrect(d, tx_, y, bw - 6, bw, PAL[(cc + rr * 2) % 6], 22)
            fp = clamp((lt - 2.7) / 0.3)
            if fp > 0:
                px = cx; py = gy - 2 * (bw + 6) - 20
                d.line((px, py, px, py - 190), fill=INK, width=10)
                wv = math.sin(lt * 9) * 14
                d.polygon([(px, py - 190), (px + 130, py - 160 + wv), (px, py - 120)], fill=(255, 138, 128))
        elif n == 2:
            # plank on roll wobbling with a ball
            ang = math.sin(lt * 2.6) * 11 * eo3(lt / 0.8)
            rc = (cx, gy - 70)
            d.ellipse((rc[0] - 70, rc[1] - 70, rc[0] + 70, rc[1] + 70), fill=(214, 170, 120))
            d.ellipse((rc[0] - 28, rc[1] - 28, rc[0] + 28, rc[1] + 28), fill=(190, 145, 98))
            a = math.radians(ang)
            pcx, pcy = cx, gy - 140 - 24
            rrect(d, pcx, pcy, 720, 48, (255, 171, 118), 24, ang)
            # ball rolls along plank
            bx = math.sin(lt * 2.6 - 0.9) * 280
            bxw = pcx + bx * math.cos(a) - (-48 / 2 - 38) * math.sin(a)
            byw = pcy + bx * math.sin(a) + (-48 / 2 - 38) * math.cos(a)
            d.ellipse((bxw - 38, byw - 38, bxw + 38, byw + 38), fill=(130, 190, 235))
            d.ellipse((bxw - 18, byw - 22, bxw - 4, byw - 8), fill=(205, 230, 250))
        else:
            # tower builds then topples
            bw = 150
            nblk = 5
            for k in range(nblk):
                s0 = 0.5 + k * 0.32
                if lt < s0: continue
                ty = gy - bw / 2 - k * (bw + 4)
                col = PAL[k % 6]
                if lt < 2.55:
                    y = ty - (1 - bounce((lt - s0) / 0.5)) * 900
                    rrect(d, cx + math.sin(k * 1.7) * 6, y, bw, bw, col, 24)
                else:
                    tt = lt - 2.55
                    dirn = 1 if k % 2 == 0 else -1
                    vx = dirn * (80 + k * 55)
                    x = cx + vx * tt * 1.6
                    y = ty + 0.5 * 2300 * tt * tt * (0.4 + 0.1 * k)
                    y = min(y, gy - bw / 2 + 0)
                    if y >= gy - bw / 2 - 1: x = cx + dirn * (200 + k * 70 + 30 * math.sin(k))
                    ang = dirn * min(tt, .9) * (60 + k * 12)
                    rrect(d, x, y, bw, bw, col, 24, ang)
    return

def circle_wipe(img, prev_bg, new_bg, lt, dur=0.5):
    pass

def bg_for(i): return BGS[i]

N = FPS * DUR
for fi in range(N):
    t = fi / FPS
    i = scene_of(t)
    lt = t - T[i]
    if i == 4:
        img = Image.new("RGB", (W, H), BGS[4])
        d = ImageDraw.Draw(img)
        p = eob(lt / 0.6)
        tcenter(img, "Lisää leikki-ideoita", f_mid, 640 + (1 - p) * 250, INK, alpha=clamp(p * 1.4))
        tcenter(img, "ja leluja lapsille", f_mid, 740 + (1 - p) * 250, INK, alpha=clamp(p * 1.4))
        u = bounce((lt - 0.9) / 0.7)
        if u > 0:
            w, h = 600 * u, 130 * u
            d.rounded_rectangle((W / 2 - w / 2, 1000 - h / 2, W / 2 + w / 2, 1000 + h / 2), radius=65, fill=INK)
            if u > .95: tcenter(img, "hellurei.fi", f_big if False else F(78), 1000, CREAM)
        for k in range(6):
            pp = bounce((lt - 0.2 - k * 0.15) / 0.6)
            if pp > 0:
                y = 1480 - (1 - pp) * 700
                rrect(d, 160 + k * 152, y + math.sin(lt * 4 + k) * 8, 120, 120, PAL[k], 28)
    else:
        prev = BGS[i - 1] if i > 0 else BGS[0]
        img = Image.new("RGB", (W, H), prev if (i > 0 and lt < 0.5) else BGS[i])
        d = ImageDraw.Draw(img)
        if i > 0 and lt < 0.5:
            r = eo3(lt / 0.5) * 1500
            d.ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=BGS[i])
        draw_scene(img, i, lt)
    img.save(f"{OUT}/f{fi:04d}.png")

# ---- audio: original synthesized jingle (no copyrighted material) ----
SR = 44100
n = int(SR * DUR)
aud = np.zeros(n, dtype=np.float32)
def note(freq, start, dur, amp=0.25, kind="mar"):
    s = int(start * SR); L = int(dur * SR)
    if s >= n: return
    L = min(L, n - s)
    tt = np.arange(L) / SR
    env = np.exp(-tt * (5.5 if kind == "mar" else 2.2)) * np.minimum(1, tt * 400)
    w = np.sin(2 * np.pi * freq * tt) + 0.35 * np.sin(2 * np.pi * freq * 2 * tt) * np.exp(-tt * 9) + 0.15 * np.sin(2 * np.pi * freq * 3.01 * tt) * np.exp(-tt * 14)
    aud[s:s + L] += (amp * env * w).astype(np.float32)
C = {"C4": 261.63, "D4": 293.66, "E4": 329.63, "G4": 392.0, "A4": 440.0, "C5": 523.25, "D5": 587.33, "E5": 659.25, "G5": 783.99, "A3": 220.0, "G3": 196.0, "F3": 174.61, "C3": 130.81, "F4": 349.23}
beat = 0.5
mel = ["E4", "G4", "A4", "G4", "E4", "D4", "C4", "D4", "E4", "G4", "C5", "A4", "G4", "E4", "D4", "E4",
       "G4", "A4", "C5", "D5", "C5", "A4", "G4", "E4", "C5", "G4", "A4", "G4", "E4", "G4", "C5", "C5"]
for k, nm in enumerate(mel):
    note(C[nm], 0.2 + k * beat, 0.9, 0.22)
bass = ["C3", "C3", "F3", "G3"]
for k in range(28):
    note(C[bass[(k // 2) % 4]], 0.2 + k * beat, 0.45, 0.20, "bass")
# pop sounds at scene transitions
for tr in T[1:5]:
    note(880, tr, 0.25, 0.18); note(1320, tr + 0.06, 0.25, 0.12)
# fade in/out
fade = np.minimum(1, np.arange(n) / (SR * 0.3)) * np.minimum(1, (n - np.arange(n)) / (SR * 1.2))
aud *= fade.astype(np.float32)
aud = np.clip(aud / max(1e-6, np.abs(aud).max()) * 0.8, -1, 1)
pcm = (aud * 32767).astype(np.int16)
with wave.open(os.path.join(OUT, "audio.wav"), "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())
print("done")
