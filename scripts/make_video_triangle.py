"""Product video: foldable Montessori climbing triangle with ramp (hellurei.fi).
Usage: python make_video_triangle.py <picks_img_dir> <out_dir>
Facts used (from the product page): 8 rungs per side, two slopes, folds flat, ramp 35x104 cm,
from 12 months with adult supervision, Baltic birch plywood, EN 71, made in Latvia.
"""
import math, os, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

IMG, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
W, H, FPS, DUR = 1080, 1920, 30, 18
INK = (52, 44, 66); CREAM = (255, 246, 234)
PAL = [(255, 138, 128), (129, 212, 180), (130, 190, 235), (255, 214, 102), (190, 160, 235), (255, 171, 118)]
BGS = [(255, 233, 178), (205, 225, 245), (200, 234, 222), (255, 214, 190), (255, 246, 234)]
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F = lambda s: ImageFont.truetype(FB, s)
f_t, f_m, f_s, f_x = F(84), F(66), F(48), F(40)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo3(t): return 1 - (1 - clamp(t)) ** 3
def eob(t, s=1.70158):
    t = clamp(t); return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2

def photo(name):
    return Image.open(os.path.join(IMG, name)).convert("RGB")

PH = {k: photo(f"triangle_{k}.jpg") for k in (1, 3, 4, 5, 6)}

def cover(im, w, h, zoom, panx, pany):
    s = max(w / im.width, h / im.height) * zoom
    nw, nh = int(im.width * s), int(im.height * s)
    r = im.resize((nw, nh), Image.LANCZOS)
    x0 = int((nw - w) * (0.5 + panx)); y0 = int((nh - h) * (0.5 + pany))
    x0 = max(0, min(nw - w, x0)); y0 = max(0, min(nh - h, y0))
    return r.crop((x0, y0, x0 + w, y0 + h))

def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width, im.height), radius=r, fill=255)
    out = Image.new("RGBA", im.size); out.paste(im, (0, 0)); out.putalpha(m); return out

def tcenter(img, txt, font, cy, fill, alpha=1.0, cx=W / 2):
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0, 0), txt, font=font)
    x = cx - (bb[2] - bb[0]) / 2 - bb[0]; y = cy - (bb[3] - bb[1]) / 2 - bb[1]
    if alpha >= .999: d.text((x, y), txt, font=font, fill=fill)
    elif alpha > 0:
        L = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(L).text((x, y), txt, font=font, fill=fill + (int(255 * alpha),)); img.paste(L, (0, 0), L)

# (start, photo, pan, title lines, callout text, icon)
SC = [
    (0.0, 3, (0.0, 0.0), ["Kiipeilykolmio", "luiskalla"], "Montessori-henkinen kiipeily kotona", None),
    (4.0, 5, (0.1, 0.0), ["8 tankoa", "joka puolella"], "Ote ja jalkavoima kehittyvät", "rungs"),
    (8.0, 6, (-0.1, 0.0), ["Kaksi", "kaltevuutta"], "Luiska liu'ulle tai kiipeämiseen", "slope"),
    (12.0, 4, (0.0, 0.0), ["Taittuu", "litteäksi"], "Pois tieltä leikin jälkeen", "fold"),
    (15.5, 1, (0.0, 0.0), ["Hellurei"], "Hae: Montessori-kiipeilykolmio luiskalla", None),
]
END = 18.0

def scene_idx(t):
    for i in range(len(SC) - 1, -1, -1):
        if t >= SC[i][0]: return i

def icon(d, kind, cx, cy, lt):
    if kind == "rungs":
        for k in range(8):
            p = clamp((lt - 0.5 - k * 0.12) / 0.3)
            y = cy + 44 - k * 12.5
            d.rounded_rectangle((cx - 52 * p, y - 3, cx + 52 * p, y + 3), radius=3, fill=PAL[k % 6])
    elif kind == "slope":
        p = eo3((lt - 0.4) / 0.6)
        d.polygon([(cx - 70, cy + 45), (cx + 70, cy + 45), (cx + 70, cy + 45 - 35 * p)], fill=PAL[2])
        d.line((cx - 70, cy + 45, cx + 70, cy + 45 - 80 * p), fill=PAL[0], width=7)
    elif kind == "fold":
        p = eo3((lt - 0.5) / 1.4)
        a = math.radians(55 * (1 - p))
        base = (cx, cy + 40)
        L = 80
        d.line((cx - L * math.cos(a), cy + 40 - L * math.sin(a), *base), fill=PAL[3], width=12)
        d.line((cx + L * math.cos(a), cy + 40 - L * math.sin(a), *base), fill=PAL[1], width=12)

def draw(t):
    i = scene_idx(t)
    st, pk, pan, title, call, ic = SC[i]
    lt = t - st
    nxt = SC[i + 1][0] if i + 1 < len(SC) else END
    dur = nxt - st
    img = Image.new("RGB", (W, H), BGS[i])
    d = ImageDraw.Draw(img)
    # colour wipe at scene start
    if i > 0 and lt < 0.45:
        prev = BGS[i - 1]
        img = Image.new("RGB", (W, H), prev); d = ImageDraw.Draw(img)
        r = eo3(lt / 0.45) * 1600
        d.ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=BGS[i])
    # title
    p = eob((lt - 0.05) / 0.55)
    for k, line in enumerate(title):
        tcenter(img, line, f_t, 190 + k * 100 + (1 - p) * -160, INK, alpha=clamp(p * 1.5))
    # photo card with Ken Burns
    if i < 4:
        cw, ch = 940, 940
        zoom = 1.0 + 0.10 * (lt / dur)
        card = cover(PH[pk], cw, ch, zoom, pan[0] + 0.15 * (lt / dur), pan[1])
        cp = eob((lt - 0.15) / 0.6)
        card = rounded(card, 48)
        y = 520 + (1 - cp) * 700
        sh = Image.new("RGBA", (cw + 40, ch + 40), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((20, 30, cw + 20, ch + 30), radius=52, fill=(0, 0, 0, 40))
        img.paste(sh, (int(W / 2 - cw / 2 - 20), int(y - 20)), sh)
        img.paste(card, (int(W / 2 - cw / 2), int(y)), card)
        d = ImageDraw.Draw(img)
        # callout pill under the card
        bp = eob((lt - 0.9) / 0.6)
        if bp > 0:
            w = 940 * clamp(bp); h = 170
            cy = 1560
            d.rounded_rectangle((W / 2 - w / 2, cy - h / 2, W / 2 + w / 2, cy + h / 2), radius=40, fill=INK)
            if bp > 0.9:
                if ic:
                    icon(d, ic, 190, cy - 10, lt)
                    tcenter(img, call, f_x, cy, CREAM, cx=W / 2 + 110)
                else:
                    tcenter(img, call, f_s, cy, CREAM)
    else:
        # end card: studio photo + url pill
        cw, ch = 760, 760
        zoom = 1.0 + 0.04 * (lt / dur)
        card = rounded(cover(PH[1], cw, ch, zoom, 0, 0), 48)
        cp = eob((lt - 0.2) / 0.6)
        img.paste(card, (int(W / 2 - cw / 2), int(430 + (1 - cp) * 800)), card)
        d = ImageDraw.Draw(img)
        tcenter(img, call, f_x, 1330, INK, alpha=clamp((lt - 0.8) * 3))
        u = eob((lt - 1.1) / 0.6)
        if u > 0:
            w, h = 560 * clamp(u), 130
            d.rounded_rectangle((W / 2 - w / 2, 1510 - h / 2, W / 2 + w / 2, 1510 + h / 2), radius=65, fill=INK)
            if u > .9: tcenter(img, "hellurei.fi", F(76), 1510, CREAM)
        tcenter(img, "Sopii 12 kk:sta alkaen aikuisen valvonnassa", F(34), 1650, INK, alpha=clamp((lt - 1.4) * 3))
        for k in range(6):
            pp = eob((lt - 0.3 - k * 0.1) / 0.5)
            d.rounded_rectangle((70 + k * 168, 1790 + (1 - pp) * 200, 70 + k * 168 + 110, 1790 + (1 - pp) * 200 + 110), radius=26, fill=PAL[k])
    return img

for fi in range(int(FPS * DUR)):
    draw(fi / FPS).save(f"{OUT}/f{fi:04d}.png")

# ---- original synthesized music (no copyrighted material) ----
SR = 44100; n = int(SR * DUR)
aud = np.zeros(n, dtype=np.float32)
def note(freq, start, dur, amp=0.22, kind="mar"):
    s = int(start * SR)
    if s >= n: return
    L = min(int(dur * SR), n - s); tt = np.arange(L) / SR
    env = np.exp(-tt * (6 if kind == "mar" else 2.4)) * np.minimum(1, tt * 400)
    w = np.sin(2 * np.pi * freq * tt) + .33 * np.sin(2 * np.pi * freq * 2 * tt) * np.exp(-tt * 9) + .12 * np.sin(2 * np.pi * freq * 3.01 * tt) * np.exp(-tt * 14)
    aud[s:s + L] += (amp * env * w).astype(np.float32)
N = {"C3": 130.81, "F3": 174.61, "G3": 196.0, "A3": 220.0, "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.0, "A4": 440.0, "C5": 523.25, "D5": 587.33, "E5": 659.25}
beat = 0.375
mel = ["G4", "E4", "G4", "A4", "G4", "E4", "D4", "E4", "C4", "E4", "G4", "C5", "A4", "G4", "E4", "G4",
       "A4", "C5", "D5", "C5", "A4", "G4", "E4", "D4", "E4", "G4", "A4", "G4", "E4", "D4", "C4", "C4",
       "G4", "E4", "G4", "A4", "G4", "E4", "D4", "E4", "C5", "A4", "G4", "E4", "D4", "E4", "C4", "C4"]
for k, nm in enumerate(mel): note(N[nm], 0.15 + k * beat, 0.8)
bass = ["C3", "C3", "F3", "G3"]
for k in range(48): note(N[bass[(k // 4) % 4]], 0.15 + k * beat * 2 / 2 * 1, 0.4, 0.17, "bass") if k % 2 == 0 else None
for s in SC[1:]: note(880, s[0], .22, .17); note(1320, s[0] + .06, .22, .11)
fade = np.minimum(1, np.arange(n) / (SR * .3)) * np.minimum(1, (n - np.arange(n)) / (SR * 1.4))
aud *= fade.astype(np.float32); aud = np.clip(aud / max(1e-6, np.abs(aud).max()) * .8, -1, 1)
with wave.open(os.path.join(OUT, "audio.wav"), "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((aud * 32767).astype(np.int16).tobytes())
print("done")
