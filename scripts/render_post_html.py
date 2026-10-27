#!/usr/bin/env python3
"""Render a hand-written post JSON (data/drafts/*.json) into blog/<slug>.html,
prepend it to data/blog-posts.json and add it to sitemap.xml.
Usage: python3 scripts/render_post_html.py data/drafts/<file>.json
Draft JSON fields: slug,title,subtitle,region,district,districtKr,date,readTime,wordCount,
heroImage,featuredWorks,relatedSpotIds,summary,spotHighlights[{name,work,addressKr,subway}],
sections[{heading,html}],faq[{q,a}]"""
import html, json, os, sys, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
from publish_daily_blog import BASE_DIR, POSTS_JSON, BLOG_DIR, update_sitemap

E = html.escape
ADS = '''
        <div class="my-6 rounded-2xl border border-slate-200 bg-slate-50/70 p-4 text-center" data-adsense-slot="blog-in-article">
          <div class="text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1">Advertisement</div>
          <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-XXXXXXXXXXXXXXXX" data-ad-slot="1234567890" data-ad-format="auto" data-full-width-responsive="true"></ins>
        </div>'''

def render(post, others):
    url = f"https://kspotkorea.co.kr/blog/{post['slug']}.html"
    q = urllib.parse.quote_plus(post['district'])
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": post['title'], "description": post['subtitle'], "image": post['heroImage'],
         "datePublished": post['date'], "dateModified": post['date'],
         "author": {"@type": "Organization", "name": "K-Spot Korea Editorial Team", "url": "https://kspotkorea.co.kr/"},
         "publisher": {"@type": "Organization", "name": "K-Spot Korea", "url": "https://kspotkorea.co.kr/"},
         "mainEntityOfPage": url},
        *[{"@type": "TouristAttraction", "name": s['name'], "description": f"Filming location: {s['work']}",
           "address": {"@type": "PostalAddress", "streetAddress": s['addressKr'], "addressLocality": post['district'], "addressCountry": "KR"}}
          for s in post['spotHighlights']],
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f['q'], "acceptedAnswer": {"@type": "Answer", "text": f['a']}} for f in post['faq']]}]}
    spots = ''.join(f'''
        <div class="rounded-xl bg-slate-50 border border-slate-200 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span class="inline-block text-[11px] font-mono font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">{E(s['work'])}</span>
            <h3 class="font-display font-bold text-base text-slate-900 mt-1">{E(s['name'])}</h3>
            <p class="text-xs font-mono text-slate-600 mt-0.5">📍 {E(s['addressKr'])} · 🚇 {E(s['subway'])}</p>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <a href="https://map.naver.com/p/search/{urllib.parse.quote(s['addressKr'])}" target="_blank" rel="noopener" class="px-3 py-1.5 rounded-lg bg-[#03C75A] text-white text-xs font-bold">🟢 Naver Map</a>
            <a href="https://map.kakao.com/link/search/{urllib.parse.quote(s['addressKr'])}" target="_blank" rel="noopener" class="px-3 py-1.5 rounded-lg bg-[#FEE500] text-slate-900 text-xs font-bold">🟡 KakaoMap</a>
          </div>
        </div>''' for s in post['spotHighlights'])
    body = ''
    for i, s in enumerate(post['sections']):
        h = s['html'].replace('<p>', '<p class="text-slate-700 leading-relaxed mb-4 text-base">').replace('<h3>', '<h3 class="font-display font-bold text-lg text-slate-900 mt-5 mb-2">')
        body += f'''
        <section class="mb-8">
          <h2 class="font-display font-bold text-xl sm:text-2xl text-slate-900 mb-3">{E(s['heading'])}</h2>
          {h}{ADS if i in (1, 3) else ''}
        </section>'''
    faq = ''.join(f'<details class="p-4 rounded-xl bg-white border border-slate-200"><summary class="font-bold text-slate-900 cursor-pointer">{E(f["q"])}</summary><p class="mt-2 text-slate-700 text-sm leading-relaxed">{E(f["a"])}</p></details>' for f in post['faq'])
    more = ''.join(f'<a href="./{o["slug"]}.html" class="block p-3 rounded-xl border border-slate-200 hover:border-rose-400 bg-white transition"><div class="text-[11px] font-mono text-rose-600 font-bold">{E(o["region"])} · {E(o["date"])}</div><div class="font-display font-bold text-sm text-slate-900 mt-0.5">{E(o["title"])}</div></a>' for o in others[:3])
    return f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{E(post['title'])} | K-Spot Korea Travel Blog</title>
  <meta name="description" content="{E(post['subtitle'])}" />
  <link rel="canonical" href="{url}" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{E(post['title'])}" />
  <meta property="og:description" content="{E(post['subtitle'])}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{post['heroImage']}" />
  <!-- Travelpayouts Monetization Script -->
  <script data-noptimize="1" data-cfasync="false" data-wpfc-render="false" src="https://emrldtp.cc/NTkxMjc3.js?t=591277" async></script>
  <!-- Google AdSense Configuration -->
  <script>window.ADSENSE_CLIENT_ID = "ca-pub-XXXXXXXXXXXXXXXX";</script>
  <script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
  </script>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: #F8FAFC; color: #0F172A; }}
    .font-display {{ font-family: 'Outfit', sans-serif; }}
    .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
  </style>
</head>
<body class="antialiased">
  <header class="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-xl">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 py-3.5 flex items-center justify-between gap-3">
      <a href="https://kspotkorea.co.kr/" class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-xl bg-rose-500 text-white font-display font-extrabold flex items-center justify-center">K</div>
        <div>
          <span class="font-display font-extrabold text-base text-slate-900">K-SPOT KOREA</span>
          <span class="text-[11px] font-mono text-rose-600 ml-1.5">DAILY REGIONAL GUIDE</span>
        </div>
      </a>
      <div class="flex items-center gap-2">
        <a href="https://kspotkorea.co.kr/#travel-blog" class="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs font-bold text-slate-700">← All Blog Guides</a>
        <a href="https://kspotkorea.co.kr/#interactive-map" class="px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-xs font-bold text-white shadow-xs">🗺️ Open Interactive Map</a>
      </div>
    </div>
  </header>

  <main class="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
    <article class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="relative h-64 sm:h-80 bg-slate-900">
        <img src="{post['heroImage']}" alt="Seoul street at night, illustrating {E(post['district'])}" class="w-full h-full object-cover opacity-90" />
        <div class="absolute inset-0 bg-gradient-to-t from-slate-950/85 via-slate-950/35 to-transparent"></div>
        <div class="absolute bottom-5 left-5 right-5 text-white">
          <div class="flex flex-wrap items-center gap-2 text-xs font-mono mb-2">
            <span class="px-2.5 py-0.5 rounded-full bg-rose-600 text-white font-bold">📍 {E(post['region'])} · {E(post['district'])}</span>
            <span class="px-2.5 py-0.5 rounded-full bg-white/20 backdrop-blur-md">📅 Published {post['date']}</span>
            <span class="px-2.5 py-0.5 rounded-full bg-white/20 backdrop-blur-md">⏱️ {post['readTime']}</span>
          </div>
          <h1 class="font-display font-extrabold text-2xl sm:text-3xl lg:text-4xl leading-tight">{E(post['title'])}</h1>
        </div>
      </div>

      <div class="p-6 sm:p-10">
        <p class="text-lg font-medium text-slate-700 border-l-4 border-rose-500 pl-4 mb-8 leading-relaxed">{E(post['summary'])}</p>

        <div class="mb-8 space-y-3">
          <h2 class="font-display font-bold text-lg text-slate-900">🎬 Featured Filming Spots in This Article</h2>{spots}
        </div>
{body}
        <section class="mb-8">
          <h2 class="font-display font-bold text-xl sm:text-2xl text-slate-900 mb-3">Frequently Asked Questions</h2>
          <div class="space-y-2.5">{faq}</div>
        </section>

        <!-- Travel Planner Affiliate Box -->
        <div class="rounded-2xl bg-slate-900 text-white p-6 space-y-4 my-8">
          <div class="flex items-center justify-between">
            <h3 class="font-display font-bold text-lg text-amber-300">✨ Plan Your Trip to {E(post['district'])}</h3>
            <span class="text-xs font-mono text-slate-300">Hotels &amp; Tours</span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">Compare hotels near these filming spots or book Seoul day tours and passes:</p>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            <a href="https://www.agoda.com/search?text={q}" target="_blank" rel="noopener sponsored" class="py-2.5 px-3 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs text-center">🏨 Agoda Hotels</a>
            <a href="https://www.booking.com/searchresults.html?ss={q}" target="_blank" rel="noopener sponsored" class="py-2.5 px-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs text-center">🛏️ Booking.com</a>
            <a href="https://www.klook.com/en-US/search/result/?query={q}" target="_blank" rel="noopener sponsored" class="py-2.5 px-3 rounded-xl bg-orange-500 hover:bg-orange-400 text-white font-bold text-xs text-center">🎟️ Klook Day Tours</a>
            <a href="https://kspotkorea.co.kr/?region={urllib.parse.quote_plus(post['region'])}#interactive-map" class="py-2.5 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs text-center">🗺️ View Pins on Map</a>
          </div>
        </div>

        <!-- Traveler Tips & Q&A Widget -->
        <section class="rounded-2xl bg-slate-50 border border-slate-200 p-6 my-8 space-y-4">
          <h3 class="font-display font-bold text-lg text-slate-900">💬 Traveler Tips &amp; Q&amp;A ({E(post['district'])})</h3>
          <div id="reviews-list" class="space-y-3 text-xs sm:text-sm text-slate-700">
            <p id="no-tips" class="text-slate-500">No traveler tips yet. Been here? Share a subway exit, cafe, or photo tip below.</p>
          </div>
          <form onsubmit="event.preventDefault(); addVisitorTip();" class="pt-2 space-y-2.5">
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <input id="tip-name" type="text" required placeholder="Your Name / Country" class="px-3 py-2 rounded-xl border border-slate-300 bg-white text-xs" />
              <input id="tip-text" type="text" required placeholder="Your tip or question..." class="sm:col-span-2 px-3 py-2 rounded-xl border border-slate-300 bg-white text-xs" />
            </div>
            <button type="submit" class="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition">Post Tip</button>
          </form>
        </section>

        <p class="text-xs text-slate-500 leading-relaxed">Source: Korea Culture Information Service Agency (KCISA) public filming-location dataset (한국문화정보원 미디어 촬영지 공공데이터). Businesses may have changed since the data was recorded; confirm hours on Naver Map or KakaoMap before visiting.</p>

        <div class="border-t border-slate-200 pt-6 mt-8">
          <h3 class="font-display font-bold text-base text-slate-900 mb-3">📚 More K-Spot Korea Regional Filming Guides</h3>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">{more}</div>
        </div>
      </div>
    </article>
  </main>

  <footer class="border-t border-slate-200 bg-white py-8 text-center text-xs text-slate-500 space-y-2">
    <p>© 2026 K-Spot Korea (<a href="https://kspotkorea.co.kr" class="text-rose-600 font-semibold">kspotkorea.co.kr</a>) · Powered by KCISA Public Cultural Filming Dataset &amp; Official Kakao Maps SDK.</p>
    <p class="flex flex-wrap items-center justify-center gap-3 font-mono text-[11px]">
      <a href="https://kspotkorea.co.kr/about-privacy-disclaimer.html#about" class="hover:text-slate-900 underline">About Us &amp; Editorial Policy</a><span>·</span>
      <a href="https://kspotkorea.co.kr/about-privacy-disclaimer.html#privacy" class="hover:text-slate-900 underline">Privacy Policy (AdSense)</a><span>·</span>
      <a href="https://kspotkorea.co.kr/about-privacy-disclaimer.html#terms" class="hover:text-slate-900 underline">Terms &amp; Disclaimer</a><span>·</span>
      <a href="mailto:duckcheonkorea@gmail.com" class="hover:text-slate-900 underline">Contact: duckcheonkorea@gmail.com</a>
    </p>
  </footer>
  <script>
    function addVisitorTip() {{
      const name = document.getElementById('tip-name').value.trim();
      const text = document.getElementById('tip-text').value.trim();
      if (!name || !text) return;
      const empty = document.getElementById('no-tips'); if (empty) empty.remove();
      const div = document.createElement('div');
      div.className = 'p-3.5 rounded-xl bg-rose-50/60 border border-rose-200';
      const b = document.createElement('div'); b.className = 'font-bold text-slate-900'; b.textContent = name;
      const p = document.createElement('p'); p.className = 'mt-1 text-slate-700'; p.textContent = text;
      div.append(b, p);
      document.getElementById('reviews-list').prepend(div);
      document.getElementById('tip-name').value = '';
      document.getElementById('tip-text').value = '';
    }}
  </script>
</body>
</html>
'''

def main():
    post = json.load(open(sys.argv[1], encoding='utf-8'))
    posts = json.load(open(POSTS_JSON, encoding='utf-8')) if os.path.exists(POSTS_JSON) else []
    posts = [p for p in posts if p['slug'] != post['slug']]
    others = list(posts)
    os.makedirs(BLOG_DIR, exist_ok=True)
    with open(os.path.join(BLOG_DIR, post['slug'] + '.html'), 'w', encoding='utf-8') as f:
        f.write(render(post, others))
    entry = {k: v for k, v in post.items() if k not in ('faq',)}
    entry['sections'] = [{"heading": s['heading'], "paragraphs": [x for x in __import__('re').sub('<h3>.*?</h3>', '', s['html']).replace('</p>', '').split('<p>') if x.strip()]} for s in post['sections']]
    posts.insert(0, entry)
    json.dump(posts, open(POSTS_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    update_sitemap(posts)
    print('published', post['slug'], len(posts))

if __name__ == '__main__':
    main()
