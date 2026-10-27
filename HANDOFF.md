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
