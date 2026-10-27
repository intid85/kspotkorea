# K-Spot Korea (`kspotkorea.co.kr`) — Korea Filming Locations Interactive Guide

**Live Production URL:** [https://kspotkorea.co.kr](https://kspotkorea.co.kr)  
**GitHub Repository:** [`intid85/kspotkorea`](https://github.com/intid85/kspotkorea) (`main` branch → GitHub Pages)  
**Local Box Workspace Path:** `/workspace/kspot-map/`

---

## 1. Project Overview & Hosting Architecture
- **Domain & DNS:** `kspotkorea.co.kr` and `www.kspotkorea.co.kr` (registered via Gabia DNS with GitHub Pages `A` records `185.199.108.153`–`111.153` and `CNAME` → `intid85.github.io`).
- **Deployment Pipeline:** Static single-page web application deployed from the root of the `main` branch on `intid85/kspotkorea` via GitHub Pages (`CNAME` file set to `kspotkorea.co.kr`).
- **Triggering Instant Redeploy:** After pushing to `main`, run:
  ```bash
  gh api -X POST repos/intid85/kspotkorea/pages/builds
  ```
- **Core Files in Repository:**
  - `index.html` — Complete application UI, Tailwind CSS configuration, Kakao Maps SDK + OSM fallback engine, filter state machine, and travel monetization hub.
  - `data/spots.json` — Curated, English/Korean bilingual 102-spot verified filming locations dataset with coordinates, scene descriptions, photo tips, subway directions, and curated images.
  - `README.md` & `HANDOFF.md` — Architecture & agent continuation documentation.
  - `sitemap.xml`, `robots.txt`, `CNAME` — SEO and custom domain configuration.

---

## 2. Map Architecture (Official Kakao Maps JS SDK + Global English OSM Fallback)
- **Primary Engine (`mapEngine === "KAKAO"`):**
  - Uses the **Official Kakao Maps JavaScript SDK v2** (`https://dapi.kakao.com/v2/maps/sdk.js?appkey=...&autoload=false`).
  - **Kakao Developers App Info:** App ID `1608117` (`플랜트맵`), which holds the grandfathered free **300,000 calls/day** Web Map quota.
  - **Registered Web Platform Domains:**
    - `https://kspotkorea.co.kr`
    - `https://www.kspotkorea.co.kr`
    - `https://intid85.github.io`
    - `http://localhost:8080`
    - `http://127.0.0.1:8080`
  - **Features:**
    - Street/building/alleyway zoom (`level: 1` closest building detail to `level: 13` full country view) with `scrollwheel: true`.
    - Layer toggles: **🗺️ Kakao Roadmap** (`kakao.maps.MapTypeId.ROADMAP`), **🛰️ Kakao Skyview** (`kakao.maps.MapTypeId.HYBRID`), and **🌐 Global English Map (OSM)** (`setMapLayer('OSM')`).
    - Color-coded circular numbered pins rendered via `kakao.maps.CustomOverlay` (`clickable: true`):
      - **K-Drama:** Rose (`#F43F5E`), numbered `#1` to `#61` (`spot.themeNum`)
      - **K-Pop:** Purple (`#9333EA`), numbered `#1` to `#22` (`spot.themeNum`)
      - **K-Movie:** Amber (`#F59E0B`), numbered `#1` to `#19` (`spot.themeNum`)
    - **Auto-Relayout (`ResizeObserver`):** `initMap()` attaches a `ResizeObserver` on `#korea-map` and `renderSelectedSpotPanel()` invokes `kakaoMap.relayout()` (and `leafletMap.invalidateSize()`) inside `requestAnimationFrame` + `setTimeout(..., 120)` so `#korea-map` always fills 100% of the stretched flex column height alongside `#selected-spot-panel` with zero grey gap.

---

## 3. Dataset Structure & Expanding Filming Spots
- **Active Curated Dataset (`data/spots.json`):**
  - Contains **102 verified iconic spots** across **21+ flagship works** (*Goblin*, *Crash Landing on You*, *Itaewon Class*, *Lovely Runner*, *Queen of Tears*, *Squid Game*, *When the Camellia Blooms*, *Hometown Cha-Cha-Cha*, *Our Beloved Summer*, *Extraordinary Attorney Woo*, *Mr. Sunshine*, *Reply 1988*, *Kingdom*, *Twenty-Five Twenty-One*, *The Glory*, *My Demon*, *King the Land*, *BTS*, *BLACKPINK*, *SEVENTEEN*, *NewJeans*, *Stray Kids*, *TWICE*, *Parasite*, *Oldboy*, *Train to Busan*, *Decision to Leave*, *Past Lives*, *Architecture 101*, *The Handmaiden*).
  - **Theme Numbering Fields:** Each spot object in `data/spots.json` has:
    - `id`: Global numeric ID (`1`–`102`)
    - `category`: `"K-Drama"` | `"K-Pop"` | `"K-Movie"`
    - `themeNum`: Category-specific sequential number (`1–61` for K-Drama, `1–22` for K-Pop, `1–19` for K-Movie)
    - `themeTotal`: Total count in that category (`61`, `22`, or `19`)
    - `name`, `nameKr`, `primaryWork`, `works` (array), `region`, `city`, `lat`, `lng`, `addressKr`, `addressEn`, `subway`, `hours`, `sceneEn`, `photoTip`, `image`, `fallbackImage`
- **Raw Master Dataset for Future Expansion (on Local Box):**
  - `/workspace/kspot-map/data/kcisa_filming_locations_utf8.csv` — **15,034 rows** of official Korean Cultural Information Service Agency (KCISA) media filming location records (`미디어유형`, `제목`, `장소명`, `장소설명`, `주소`, `위도`, `경도`, etc.).
  - To add new spots: append new items to `data/spots.json`, recalculate `themeNum` and `themeTotal` per category, and push to `main`.

---

## 4. UI State Machine & Travel Monetization Engine
1. **Hero Banner Auto-Rotator:**
   - 5-slide visual showcase (`startHeroAutoRotate()`) with a 5-second crossfade interval (`HERO_SLIDES`), pause-on-hover, dot indicators, and a 1-click jump button that filters by that work and focuses the exact spot on the map.
2. **Two-Way Filter Sync (`setCategory` ↔ `setWork`):**
   - Clicking any child work chip (e.g. `Itaewon Class`, `BTS`, `Parasite`) when another top category tab is active automatically switches `activeCategory` / `currentCategory` to match that work's category (`K-Drama`, `K-Pop`, `K-Movie`), updates the top tab styling, fits the map bounds (`kakao.maps.LatLngBounds`) to the matching pins, and loads the first matching spot into `#selected-spot-panel`.
   - Clicking a top category tab (`All Spots`, `K-Drama`, `K-Pop`, `K-Movie`) automatically resets `activeWork = "ALL"` / `currentWork = "all"` if the active work has no spots in that category.
3. **Right-Side Selected Pin Card (`#selected-spot-panel`) & Dwell-Time Engine:**
   - Clicking any numbered pin on the map (`onPinClick(spotId)`) smoothly pans the map, highlights the active pin, opens a floating summary card with `🔍 Zoom Close` (Kakao Level `3`), and renders the full spot guide in `#selected-spot-panel`.
   - Includes **Around This Spot · Trip Planner**:
     - **🏨 Stay Near This Spot:** `Agoda Deals`, `Booking.com`, `Trip.com Hotels`
     - **🎟️ Tours & Activities:** `Klook Passes & Day Tours`, `GetYourGuide`
     - **🍜 Nearby Eats & Cafes:** Curated area dining tips + 1-click `Nearby Food on Map` (`https://map.kakao.com/link/search/...`), `Naver Eats`, and `Google Maps`
     - **📍 Closest K-Spots to Visit Next:** Top 3 nearest filming spots computed in real time by Haversine distance (`km`).
4. **Centralized Affiliate Configuration (`AFFILIATE_CONFIG` in `index.html`):**
   - Located near line 510 of `index.html`:
     ```js
     const AFFILIATE_CONFIG = {
       agodaCid: '',             // e.g. '1922888' — Agoda Partner CID
       bookingAid: '',           // e.g. '2311236' — Booking.com Affiliate AID
       tripAllianceId: '',       // e.g. '38821'   — Trip.com Alliance ID
       klookAid: '',             // e.g. '41092'   — Klook Affiliate ID
       getYourGuidePartnerId: '' // e.g. 'ABCD123' — GetYourGuide Partner ID
     };
     ```
   - Entering partner IDs in `AFFILIATE_CONFIG` automatically activates affiliate tracking parameters across all 102+ cards and the right-side map panel.
