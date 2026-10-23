import math, os, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 10
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SS = 1  # no supersampling to keep it fast

BG = (255, 244, 230)
PAL = [(255, 138, 128), (129, 212, 180), (130, 190, 235), (255, 214, 102), (190, 160, 235), (255, 171, 118)]
INK = (60, 52, 70)
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_title = ImageFont.truetype(FONT_B, 150)
f_tag = ImageFont.truetype(FONT_B, 58)
f_url = ImageFont.truetype(FONT_B, 70)

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ease_out_bounce(t):
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

S = 210
# pyramid 3-2-1, targets (cx, cy)
base_y = 1400
targets = [
    (330, base_y), (540, base_y), (750, base_y),
    (435, base_y - S - 12), (645, base_y - S - 12),
    (540, base_y - 2 * (S + 12)),
]
order = [0, 1, 2, 3, 4, 5]

def text_center(d, txt, font, cy, fill, alpha=1.0, img=None):
    bbox = d.textbbox((0, 0), txt, font=font)
    w = bbox[2] - bbox[0]
    x = (W - w) / 2 - bbox[0]
    y = cy - (bbox[3] - bbox[1]) / 2 - bbox[1]
    if alpha >= 0.999:
        d.text((x, y), txt, font=font, fill=fill)
    else:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.text((x, y), txt, font=font, fill=fill + (int(255 * alpha),))
        img.paste(layer, (0, 0), layer)

for i in range(FPS * DUR):
    t = i / FPS
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # soft background circles drifting
    for k, (cx, cy, r, c) in enumerate([(160, 300, 220, (255, 230, 205)), (930, 700, 260, (250, 236, 215)), (200, 1650, 240, (255, 230, 205))]):
        dy = math.sin(t * 0.8 + k) * 18
        d.ellipse((cx - r, cy - r + dy, cx + r, cy + r + dy), fill=c)

    # blocks drop in
    for n, idx in enumerate(order):
        start = 0.25 + n * 0.45
        p = clamp((t - start) / 0.9)
        tx, ty = targets[idx]
        if t < start:
            continue
        y = ty - (1 - ease_out_bounce(p)) * 1500
        bob = 0
        if t > 6.0:
            bob = math.sin((t - 6.0) * 2.4 + n) * 6
        col = PAL[idx % len(PAL)]
        d.rounded_rectangle((tx - S / 2, y - S / 2 + bob, tx + S / 2, y + S / 2 + bob), radius=34, fill=col)
        # little highlight and dots like toy blocks
        d.rounded_rectangle((tx - S / 2 + 18, y - S / 2 + 18 + bob, tx + S / 2 - 18, y - S / 2 + 46 + bob), radius=14, fill=tuple(min(255, v + 28) for v in col))
        for dx in (-40, 40):
            d.ellipse((tx + dx - 11, y + 20 + bob, tx + dx + 11, y + 42 + bob), fill=tuple(int(v * 0.75) for v in col))

    # title
    tp = clamp((t - 3.4) / 0.8)
    if tp > 0:
        yoff = (1 - ease_out_cubic(tp)) * 80
        text_center(d, "Hellurei", f_title, 420 + yoff, INK, alpha=tp, img=img)
        d = ImageDraw.Draw(img)

    # tagline
    gp = clamp((t - 5.6) / 0.8)
    if gp > 0:
        yoff = (1 - ease_out_cubic(gp)) * 50
        text_center(d, "Huolella valittuja", f_tag, 640 + yoff, INK, alpha=gp, img=img)
        text_center(d, "tuotteita lapsille", f_tag, 720 + yoff, INK, alpha=gp, img=img)
        d = ImageDraw.Draw(img)

    # url pill
    up = clamp((t - 7.9) / 0.7)
    if up > 0:
        sc = ease_out_bounce(up)
        w, h = 520 * sc, 120 * sc
        cx, cy = W / 2, 1640
        d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=60, fill=INK)
        if up > 0.9:
            text_center(d, "hellurei.fi", f_url, cy, (255, 244, 230))

    img.save(f"{OUT}/f{i:04d}.png")
print("done")
