"""Download hellurei.fi product images (public storefront) and build contact sheets.

Output:
  shopify/manifest.json              handle, title, images[{n, src, w, h, alt}]
  shopify/sheets/<handle>.jpg        contact sheet, thumbnails numbered 1..N (same n as in manifest)
Run by GitHub Actions; no secrets needed.
"""
import json, os, sys, time, urllib.request
from PIL import Image, ImageDraw, ImageFont

BASE = "https://hellurei.fi"
OUT = "shopify"
os.makedirs(f"{OUT}/sheets", exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (compatible; hellurei-content-bot)"}

def get(url, tries=3):
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception as e:
            if k == tries - 1:
                raise
            time.sleep(2)

products = []
page = 1
while True:
    data = json.loads(get(f"{BASE}/products.json?limit=250&page={page}"))
    items = data.get("products", [])
    if not items:
        break
    products += items
    page += 1
print("products", len(products))

manifest = []
font = ImageFont.load_default(size=28) if "size" in ImageFont.load_default.__code__.co_varnames else ImageFont.load_default()
for p in products:
    imgs = p.get("images", [])
    entry = {"handle": p["handle"], "title": p["title"], "product_type": p.get("product_type", ""),
             "images": [{"n": i + 1, "src": im["src"], "w": im.get("width"), "h": im.get("height"), "alt": im.get("alt")} for i, im in enumerate(imgs)]}
    manifest.append(entry)
    if not imgs:
        continue
    path = f"{OUT}/sheets/{p['handle']}.jpg"
    if os.path.exists(path):
        continue
    thumbs = []
    for i, im in enumerate(imgs[:12]):
        try:
            u = im["src"] + ("&" if "?" in im["src"] else "?") + "width=360"
            t = Image.open(__import__("io").BytesIO(get(u))).convert("RGB")
            t.thumbnail((360, 360))
            c = Image.new("RGB", (360, 360), (255, 255, 255))
            c.paste(t, ((360 - t.width) // 2, (360 - t.height) // 2))
            d = ImageDraw.Draw(c)
            d.rectangle((0, 0, 52, 44), fill=(0, 0, 0))
            d.text((10, 6), str(i + 1), fill=(255, 255, 255), font=font)
            thumbs.append(c)
        except Exception as e:
            print("skip", p["handle"], i + 1, e, file=sys.stderr)
    if not thumbs:
        continue
    cols = 4
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 360, rows * 360), (230, 230, 230))
    for k, c in enumerate(thumbs):
        sheet.paste(c, ((k % cols) * 360, (k // cols) * 360))
    sheet.save(path, quality=70)

json.dump(manifest, open(f"{OUT}/manifest.json", "w"), ensure_ascii=False, indent=1)
print("done")
