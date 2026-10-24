# Hellurei social media: operating manual (read this first, every run)

Same content is in AGENTS.md. If you change one, copy it to the other.
Owner: Dmitri (dmitrivlassenko@gmail.com), non-marketer, wants Claude to run the accounts autonomously and tell him what he must do.

## 1. Business
- hellurei.fi = Hellurei Play Oy, Finnish online toy shop on Shopify, ~279 products, dropshipping via Hertwill. Brands: leg&go, IGLU, Little Lights, Feber, STEP'n'FOLD and more.
- Main market Finland. Finnish is mandatory. Swedish about 1 post in 6 on Instagram, English on some Pinterest pins.
- Accounts (all business, handle hellurei_play_oy): Instagram, TikTok, Pinterest. No Facebook.
- Instagram/TikTok profile link must be https://hellurei.fi (owner was asked to set it).

## 2. Tools and ids
- Buffer (free plan, via MCP connector; the API key is NOT usable): organizationId 6a836f8146c6a1a35bad3476 (NOT the account id 6a836f8146c6a1a35bad3474).
  Channels: Instagram 6a836fefccaf649a67c4dfce, TikTok 6a837007ccaf649a67c4e03a, Pinterest 6a83703eccaf649a67c4e128.
  Pinterest boards: "Lasten huonekalut, lelut & Montessori" 1082693635359170154; "Products" 1082693635359159074.
  Limits: 10 queued posts per channel (refills as posts publish), 100 requests/15 min, 250/day, 3000/month. Use few calls: list_posts once, then create.
  Timezone Europe/Helsinki: UTC+3 until Sun 25.10.2026, UTC+2 after. Build dueAt from get_account currentTime.
- Shopify connector: live product data (title, FI translation, description, media).
- This repo (DmitriVlassenko/ads-content, public, branch main) is the media host. Pushed files are reachable by Buffer at
  https://raw.githubusercontent.com/DmitriVlassenko/ads-content/main/<path>  (VERIFIED: video posts work this way).
  The Claude workspace itself cannot open raw.githubusercontent.com, cdn.shopify.com or hellurei.fi (egress allowlist), but git push/pull works. GitHub Actions can reach everything.
- Add repo to a session: mcp__claude-code-remote__add_repo owner DmitriVlassenko repo ads-content access push, then clone, then register_repo_root.

## 3. Product images (you must LOOK at them)
- shopify/manifest.json: all products {handle,title,product_type,images[{n,src,w,h,alt}]} (n is 1-based, order of the public products.json).
- shopify/sheets/<handle>.jpg: numbered contact sheet of that product's images. Open with Read to see them. Image 1 is usually a plain studio shot (looks like an ad). Prefer lifestyle shots (children playing, rooms). The owner dislikes white-background ad images; mix at most one studio shot per carousel. File names and alt texts are unreliable, always look at the sheet.
- Full resolution: add lines `name url` to picks/<anything>.txt (url = the src from manifest) and push. The workflow fetch-picks.yml downloads them to picks/img/<name>.jpg (1400 px) and commits. git pull, then Read them. (Takes ~1 min; check with `git fetch` and FETCH_HEAD.)
- To refresh the manifest after catalog changes run workflow "fetch-images" (workflow_dispatch) or push a change to scripts/fetch_products.py.
- Buffer media rules: Shopify image URLs must carry &width=1080. TikTok images max 2,073,600 pixels. Instagram carousel images must have aspect ratio 4:5 to 1.91:1 (portrait 2:3 FAILS on Instagram). Pinterest wants portrait (2:3), needs boardServiceId, title and url (https://hellurei.fi/products/<handle>). Instagram/TikTok captions cannot hold clickable links: say "hae <tuotteen nimi> hellurei.fi-sivulta, linkki profiilissa".

## 4. Content rules (hard)
- Real small-shop human voice: short, warm, concrete, hook or question, vary openers and structure, no emoji walls, no checkmark lists every time. Never the same caption on two platforms. Instagram = conversational + 5-6 hashtags; TikTok = short punchy; Pinterest = keyword-rich title + plain description + product URL.
- Facts ONLY from live Shopify data. Never invent: no shipping promises/free shipping, discounts, urgency, reviews/testimonials, personal anecdotes ("our favourite"), age/safety claims beyond the product page, prices unless checked live. Mention made-to-order if true.
- About 1/3 of posts are NOT plain product ads: brand stories (verified facts), play/parenting tips grounded in product facts, seasonal hooks (autumn evenings, Independence Day 6.12., Christmas, rainy-day play), text cards, videos. Pick products randomly across the whole catalogue; never repeat a product within 14 days; never the same product on all platforms the same day.
- Cadence: Instagram 1/day, TikTok 1/day, Pinterest 1-2/day. Times about 12:00 and 19:00-20:30 Helsinki. Avoid nights.
- No other people's content or brand footage without written permission. No claims you cannot verify.

## 5. Video system (the owner loves the quality: keep it)
Quality bar = videos/hellurei_triangle_v2.mp4 (approved, published 23.10.2026): vertical 1080x1920, 15 s, beat-synced cuts, smooth camera moves, motion blur, stamped kinetic type, animated graphics, real product photos, sound locked to every cut, end card with hellurei.fi.
Bad examples the owner rejected (never do again): static slideshow with Pillow, slow zooms with jitter, generic loop music, 10-second block animation.

How to make a video:
1. Pick a random product (Shopify) and 4-5 LIFESTYLE photos (sheets + picks, see section 3). Write facts from the product page only.
2. Write specs/<id>.json (see examples: specs/test_gen.json). Then run: `python3 tools/makevideo.py specs/<id>.json` (add --stills to check a contact sheet first, --preview for a fast draft). Output: videos/<id>.mp4 and build/<id>_qa_sheet.jpg. Needs node, playwright (npm i -g playwright; do not run playwright install if Chromium exists), ffmpeg, numpy, Pillow. ~3-4 min render on 2 cores.
3. ALWAYS look at the stills sheet (Read) before rendering and at the qa sheet after. Fix overflowing text, low contrast, wrong photos (a "photo" of a different colour/product).
4. Randomise on purpose so videos differ: palette (spec.palette 0-4 or random from seed), seed, scene order and count (3-8 scenes), different hero/counter/card/fold/grid/text scene mix, bpm and music style (bouncy/dreamy/funk/chill, or a CC0 file). Never reuse the exact same scene sequence twice in a row. Change copy tone each time.
Spec format: {id, seed, palette?, bpm?, photos{key: path}, scenes[], music{style?|file?,start?}}.
Scene types: strobe{words[]} (one slam word per beat, use 2-3 at the start), hero{photo,l1,l2?,sub?,icon?:false} (full-bleed photo with wipe, drawn triangle icon unless icon:false: set icon:false for non-climbing products), counter{photo,n,word,l2?,foot?} (a big number counting up, n<=8), card{photo,t1,t2?,foot?,graphic?:'slope'} (photo card + big words; 'slope' only for ramps), fold{photo,t1,t2,foot?} (frame folding flat; only for foldable products), grid{photos[4],l1,l2} (photo grid with banner), text{lines[2-3],photo?} (pure kinetic type), end{photo,search,note} (always last; brand + hellurei.fi pill). `beats` overrides scene length. Add new scene types to tools/template.html when a product needs a new diagram (keep them pure functions of time, see tools/kinetic/engine.js). Texts in Finnish, short, facts only.
Music: tools/musicgen.py synthesises original music (own work, no licence trouble). music/ holds a CC0 library (music/catalog.json lists title/author/source/licence; use music{file:"music/cc0/x.mp3",start:seconds}); the generator mixes cut sounds over it. CC0 means no attribution needed; never use anything not in the catalogue. Trending/licensed sounds cannot be attached through Buffer; only the owner can add them inside the app (TikTok "notification" posting). Do not use copyrighted songs.
Owner approval rule: the owner approves only the FIRST video of each new kind. The motion-graphics kind (this system) is approved. A genuinely new kind (e.g. talking head, screen recording, different aspect, AI footage) needs approval first (render, send to the owner, wait).
Publishing a video: commit+push the mp4 to videos/, then Buffer create_post with assets [{video:{url:raw url}}]. Instagram metadata {instagram:{type:"reel",shouldShareToFeed:true}}; TikTok metadata {tiktok:{title}}; ALWAYS set the cover: assets [{video:{url, metadata:{thumbnailOffset:<ms>}}}] using the 'thumbnailOffset' printed by makevideo.py (a frame about 1 s into the first photo scene). Our first frames are plain colour slams, so without an offset Instagram shows an empty thumbnail (happened with the first video; sent posts cannot be changed through Buffer, the owner must change the cover in the app). Buffer has no custom cover-image upload for videos, only this offset. Pinterest video pins not tested. Raw URLs only work after the push has completed.

## 6. Routine for a scheduled run
1. Clone/pull this repo, read this file and LOG.md. 2. get_account; list_posts scheduled+sent+error for each channel (find errors, fix with edit_post). 3. Fill each queue up to 10 (IG 1/day, TikTok 1/day, Pinterest 1-2/day) over the next days; at least 2 of every 7 Instagram/TikTok posts should be videos made with the system above (alternate product videos with brand/tip/seasonal ones). 4. Append every created post to LOG.md (date, platform, product/topic, Buffer id). 5. git commit + push. 6. Report: what was queued per channel, failures/fixes, what the owner should do.
Order matters: build videos and push them BEFORE creating Buffer posts that point to them.

## 7. Open items for the owner (mention when relevant, do not nag)
- Set Instagram and TikTok profile links to https://hellurei.fi.
- Revoke the old Buffer API key (it was pasted in chat).
- Check Feber balance bike images in Shopify (appear mislabeled "recycled-eco-playhouse-duplicate").
- Ask Hertwill for EAN/GTIN export and a media pack (lifestyle photos/videos).
- Earlier SEO tasks: native FI/SV text review, homepage SEO paste, Search Console baseline.

## 8. Lessons learned
- Buffer queue holds max 10 per channel on free plan; shareNow publishes instantly (used for first posts).
- A portrait 2:3 image broke an Instagram carousel; always check ratios.
- Image selection by file name was wrong several times; look at contact sheets.
- Do not claim "our favourite", discounts, shipping. A first caption did, and it was removed.
- The workspace network is allowlisted; if a download fails, do it in a GitHub Actions workflow in this repo instead of retrying.
- Videos: render with sub-pixel transforms (canvas drawImage float coordinates), never integer-cropped Pillow frames (causes shaking).

## 9. Music library status (24.10.2026)
music/catalog.json holds 40 CC0 tracks from OpenGameArt (73 MB), mostly game music (dark, ambient, battle). Only a few fit a cheerful kids' shop: "Bossa Nova" (Joth), "Next to You" (Joth), "Enchanted Tiki 86" (cynicmusic), "Town Theme RPG" (cynicmusic), "Snowfall" (Kistol, calm/Christmas), "4 Chiptunes (Adventure)" (Juhani Junkala), "Awake! (Megawall-10)" (cynicmusic). Do not use dark, creepy, battle or ambient horror tracks. The built-in synthesizer (tools/musicgen.py) is the default and matches the approved video; use a CC0 file only when it clearly fits. Extend the library by editing tools/fetch_music.py (push triggers the workflow; it runs ~25 min).

## 10. Research note (24.10.2026, r/ClaudeAI thread "how are people making those graphic motion videos")
- Consensus: the good clips are code-rendered (HTML/canvas or Remotion + headless browser + ffmpeg), not generative video. That is exactly our pipeline. Remotion/HyperFrames/Three.js/Blender are alternatives; our pipeline is enough for photo-based product videos.
- Things others add that we do not have yet: (1) reference clips: ask the owner for example videos he likes, split with `ffmpeg -vf fps=1,scale=360:-1,tile=4x6` into a contact sheet and Read it, then copy pacing/type/layout; (2) paid generated assets via an OpenRouter key (voice-over, music, images, a second model as critic), about $3 per video; needs the owner's key and budget, not set up; (3) a storyboard per video before building, and a critic pass on the rendered sheets.
- SAFE ZONES: Instagram/TikTok UI covers roughly the bottom 20% and the right edge. Keep important text between y=250 and y=1500 (of 1920), x<=960. Our end-card note lines (y 1570-1650) and foot texts (y 1855) are partly inside the unsafe zone: keep them short or move them up when you edit tools/template.html.
- The first 5 s need a hook: the strobe words are our hook; make them a curiosity/benefit word, not a brand name.
