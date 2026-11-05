# HANDOFF GUIDE FOR FUTURE AGENTS (`K-Spot Korea` / `kspotkorea.co.kr`)

If you are a new agent session picking up work on **K-Spot Korea (`https://kspotkorea.co.kr`)**, read this file first so you have 100% context without needing to rediscover anything.

---

## 1. Where Everything Lives
- **Live Website:** `https://kspotkorea.co.kr` (also `https://www.kspotkorea.co.kr` and `https://intid85.github.io/kspotkorea/`)
- **GitHub Repo:** `https://github.com/intid85/kspotkorea` (branch: `main`)
- **Local Workspace Directory on Box:** `/workspace/kspot-map/`
  - `/workspace/kspot-map/index.html` — Main single-page app
  - `/workspace/kspot-map/data/spots.json` — Curated 102 filming spots JSON
  - `/workspace/kspot-map/data/kcisa_filming_locations_utf8.csv` — 15,034-row raw Korean government (KCISA) filming location CSV for future expansion
  - `/workspace/kspot-map/kakao_app_key.txt` — Active 32-char Kakao Maps JavaScript SDK key (from Kakao Developers App ID `1608117` `플랜트맵`, which has the 300,000/day free Web Map quota)
- **Local Git Clone on Box:** `/tmp/kspotkorea-repo/` (or clone `https://github.com/intid85/kspotkorea.git` fresh anytime using `gh`).

---

## 2. How to Deploy Changes to Production (`https://kspotkorea.co.kr`)
1. Edit files in `/workspace/kspot-map/` (primarily `index.html` and `data/spots.json`).
2. Copy updated files into the git repository and push to `main`:
   ```bash
   cp /workspace/kspot-map/index.html /workspace/kspot-map/README.md /workspace/kspot-map/HANDOFF.md /tmp/kspotkorea-repo/
   cp /workspace/kspot-map/data/spots.json /tmp/kspotkorea-repo/data/spots.json
   cd /tmp/kspotkorea-repo
   git add -A
   git commit -m "Describe your update"
   git push origin main
   gh api -X POST repos/intid85/kspotkorea/pages/builds
   ```
3. Check build status with:
   ```bash
   gh api repos/intid85/kspotkorea/pages/builds/latest --jq '{status: .status, commit: .commit}'
   ```

---

## 3. Critical Technical Details to Preserve
1. **Kakao Maps SDK & ResizeObserver (`#korea-map`):**
   - `index.html` loads `https://dapi.kakao.com/v2/maps/sdk.js?appkey=...&autoload=false`.
   - Never remove the `ResizeObserver` on `#korea-map` or the `kakaoMap.relayout()` calls at the end of `renderSelectedSpotPanel()`. Because `#selected-spot-panel` changes height dynamically (750–820px), `#korea-map` stretches via CSS Flexbox; calling `kakaoMap.relayout()` prevents any grey blank area at the bottom of the map.
2. **Playwright Screenshot Capture inside the Linux Box:**
   - When capturing screenshots of `http://localhost:8080` or `https://kspotkorea.co.kr` using headless Chromium inside the box, Chromium's egress proxy breaks direct requests to `mts.kakaocdn.net` (`ERR_BLOCKED_BY_ORB` / `AkamaiGHost 400`), whereas `curl` succeeds with `200 OK image/png`.
   - Always attach a `page.route('**://mts.kakaocdn.net/**', ...)` handler in Playwright that fetches the tile via `execFileSync('curl', ['-s', route.request().url(), '-H', 'Referer: https://kspotkorea.co.kr/'])` and fulfills with `contentType: 'image/png'`.
3. **Child Work Chip ↔ Top Category Tab Auto-Sync:**
   - In `setWork(work)`, selecting a work chip automatically switches `activeCategory` / `currentCategory` to match that work's category (`K-Drama`, `K-Pop`, `K-Movie`) and updates the top category buttons.
   - In `setCategory(cat)`, switching top category resets `activeWork = "ALL"` / `currentWork = "all"` if the work does not belong to `cat`.
4. **Affiliate Monetization (`AFFILIATE_CONFIG`):**
   - When the user provides their Agoda CID, Booking.com AID, Trip.com Alliance ID, Klook AID, or GetYourGuide Partner ID, simply populate `AFFILIATE_CONFIG` in `index.html` and push to `main`.

---

## 7. Daily Public-Data Regional Blog & AdSense Pipeline (`[t628u]`)
- **JSON Feed**: `/workspace/kspot-map/data/blog-posts.json`
- **Standalone Static HTML Articles**: `/workspace/kspot-map/blog/<slug>.html` (indexed in `/workspace/kspot-map/sitemap.xml`)
- **Daily Generator Script**: `/workspace/kspot-map/scripts/publish_daily_blog.py`
  - Reads `/workspace/kspot-map/data/kcisa_filming_locations_utf8.csv` (15,034 public filming records), picks the next unposted Korean city/district cluster, generates a rich English regional travel guide, prepends it to `data/blog-posts.json`, and updates `sitemap.xml`.

## 8. Google Search Console, Travelpayouts & Google AdSense Setup
- **Google Search Console Verification File**: `/workspace/kspot-map/googlefb9a5ed5e8203036.html` (`https://kspotkorea.co.kr/googlefb9a5ed5e8203036.html`)
- **Robots & Sitemap**: `/workspace/kspot-map/robots.txt` (`https://kspotkorea.co.kr/robots.txt`) and `/workspace/kspot-map/sitemap.xml` (`https://kspotkorea.co.kr/sitemap.xml`)
- **Travelpayouts Script**: `<script data-noptimize="1" data-cfasync="false" data-wpfc-render="false" src="https://emrldtp.cc/NTkxMjc3.js?t=591277" async></script>` included in `<head>` of `index.html`, `about-privacy-disclaimer.html`, and all `/blog/*.html` pages.
- **Google AdSense Ready**:
  - Legal & Editorial Policies Page: `/workspace/kspot-map/about-privacy-disclaimer.html` (`About Us & Editorial Policy`, `Privacy Policy` with Google AdSense DoubleClick DART cookie disclosure, `Terms & Travel Disclaimer`, and `Contact: duckcheonkorea@gmail.com`) linked in the footer of every page.
  - AdSense Publisher ID placeholder (`window.ADSENSE_CLIENT_ID = "ca-pub-XXXXXXXXXXXXXXXX"`) and `<ins class="adsbygoogle" ...>` containers on `index.html` and inside each `/blog/*.html` article.

## 9. Daily Post Workflow (since 2026-10-28)
- Write the day's post as a draft JSON in `data/drafts/YYYY-MM-DD-<area>.json` (fields documented at the top of `scripts/render_post_html.py`).
- Run `python3 scripts/render_post_html.py data/drafts/<file>.json` to build `blog/<slug>.html`, prepend to `data/blog-posts.json`, and add the URL to `sitemap.xml`.
- Covered so far: Jongno/Bukchon, Suwon Haenggung-dong, Gangneung/Jumunjin, Itaewon/Yongsan, Mapo-gu (Hongdae/Yeonnam/Mangwon), Gangnam-gu (Apgujeong/Cheongdam/COEX), Jung-gu (Deoksugung/Myeongdong/Seoullo/DDP, 2026-11-01), Yeongdeungpo-gu (Yeouido/Han River bridges/Seonyudo/Mullae, 2026-11-02), Paju (Book City/Heyri/Byeokchoji/Imjingak, 2026-11-03), Goyang (Ilsan Lake Park/Jeongbalsan/KINTEX/Haengjusanseong, 2026-11-04), Incheon Jung-gu (Chinatown/Songwol-dong/Jayu Park/Incheon Art Platform/Wolmido + airport & Paradise City, 2026-11-05), Seocho-gu (Banpo Bridge/Jamsu Bridge/Some Sevit/Seorae Island, Seoul court district, GT Tower/Boutique Monaco, Seoul Arts Center, Yangjae, 2026-11-06; draft data/drafts/2026-11-06-seocho.json). Next candidates by KCISA record count: Jeju-si (270), Seodaemun-gu (224), Songpa-gu (203), Seongnam (202). Incheon Dong-gu (Hanmi Bookstore from Goblin, Baedari book street) could be a later small add-on.
- SEO block: after rendering, run `upgrade_html_file()` from `/workspace/kp/seo_upgrade_helper.py` on the new post only (set its TODAY/TODAY_ISO to the post date first) to add robots max-image-preview, BreadcrumbList JSON-LD, h2 ids + TOC and the related-guides aside.
- Hero alt text: set `heroAlt` in the draft JSON (render_post_html.py uses it; the old default said "Seoul street at night"). After the SEO helper, check: hero <figure> img has fetchpriority=high and no loading=lazy, twitter:image exists, BlogPosting JSON-LD image lists all photos.
- The SEO helper adds loading="lazy" to the in-article hero <figure> img (because the header img counts as #1) and does not add twitter:image or list all photos in BlogPosting image: fix these three by hand after running it (done this way for Goyang, Incheon and Seocho). Call it via import with sys.dont_write_bytecode=True and set h.TODAY / h.TODAY_ISO; revert scripts/__pycache__/*.pyc if render touches it (it is tracked).
- The traveler-tips widget starts empty; do not seed it with invented reviews.

## Blog photo rule (2026-11-03)
- Commons tip: query `action=query&prop=imageinfo|categories&iiprop=url|size|extmetadata&iiurlwidth=1600` to get author/license/categories and a ready thumbnail; Seoul court buildings have few Commons photos (Seocho post used `File:Supreme Court of Korea (2020).jpg`, Seoul Institute CC BY 4.0, captioned as the court district next to the Seoul Central District Court).
- Real photos of the actual place only: KTO/공공누리 (credit source), Wikimedia Commons CC (credit author + license link; get metadata via commons API), Unsplash/Pexels. Never drama/MV screenshots or unlicensed images; verify the photo shows the named place.
- Save to assets/blog/<slug>/, ~1200px wide, JPG/WebP <300KB. Use <figure> + descriptive alt + width/height + loading=lazy (except hero) + <figcaption> credit/license. Hero = og:image/twitter:image + JSON-LD image + heroImage in data/blog-posts.json.
