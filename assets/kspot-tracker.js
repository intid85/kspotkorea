/*!
 * K-Spot Korea (kspotkorea.co.kr) — Invisible Pageview Tracker (Abacus: kspot-korea-2026)
 * - 100% invisible to normal visitors
 * - Tracks daily (day__YYYY-MM-DD__<slug> and day__YYYY-MM-DD__all_site) + cumulative (total__<slug> and total__all_site) in KST (UTC+9)
 * - Owner-only admin bar available via ?admin=9616
 */
(function () {
  'use strict';

  var NAMESPACE = 'kspot-korea-2026';
  var API_BASE = 'https://abacus.jasoncameron.dev';

  function fnv1aHex8(str) {
    var h = 0x811c9dc5;
    var bytes = new TextEncoder().encode(str);
    for (var i = 0; i < bytes.length; i++) {
      h ^= bytes[i];
      h = Math.imul(h, 0x01000193) >>> 0;
    }
    return h.toString(16).padStart(8, '0');
  }

  function shortSlug(slug) {
    var clean = String(slug || '')
      .toLowerCase()
      .replace(/[^a-z0-9_-]+/g, '-')
      .replace(/^-+|-+$/g, '') || 'home';
    if (clean.length <= 44) return clean;
    return clean.slice(0, 35) + '_' + fnv1aHex8(clean);
  }

  function getKstDateString(offsetDays) {
    var offset = (typeof offsetDays === 'number' ? offsetDays : 0) * 86400000;
    var kstMs = Date.now() + (9 * 3600000) + offset;
    return new Date(kstMs).toISOString().slice(0, 10);
  }

  function detectPageInfo() {
    var path = (window.location.pathname || '/').replace(/\/+$/, '') || '/';
    var lower = path.toLowerCase();
    var postMatch = lower.match(/\/blog\/([^\/]+?)(?:\.html)?$/i);
    if (postMatch && postMatch[1]) {
      var name = postMatch[1].replace(/\.html$/i, '').replace(/^\/+|\/+$/g, '') || 'post';
      return { slug: name, isBlogArticle: name !== 'index' };
    }
    if (lower === '/' || lower === '/index.html' || /\/kspotkorea(?:\/index\.html)?$/i.test(lower)) {
      return { slug: 'home', isBlogArticle: false };
    }
    var seg = lower.split('/').pop().replace(/\.html$/i, '') || 'home';
    return { slug: seg, isBlogArticle: false };
  }

  function shouldTrack(params) {
    if (params.get('force_track') === '1') return true;
    if (params.get('notrack') === '1') return false;
    if (params.get('admin') === '9616') return false;
    if (typeof navigator !== 'undefined' && navigator.webdriver) return false;
    var ua = (typeof navigator !== 'undefined' && navigator.userAgent) ? navigator.userAgent : '';
    if (/bot|crawl|spider|slurp|headless|lighthouse|pagespeed|gtmetrix|pingdom|python|curl|wget|playwright|puppeteer/i.test(ua)) {
      return false;
    }
    var host = (window.location.hostname || '').toLowerCase();
    if (!host || host === 'localhost' || host === '127.0.0.1' || window.location.protocol === 'file:') {
      return false;
    }
    return true;
  }

  function hitKey(key) {
    try {
      fetch(API_BASE + '/hit/' + NAMESPACE + '/' + encodeURIComponent(key), {
        method: 'GET',
        mode: 'cors',
        keepalive: true,
        cache: 'no-store'
      }).catch(function () {});
    } catch (e) {}
  }

  function init() {
    var params;
    try {
      params = new URLSearchParams(window.location.search || '');
    } catch (e) {
      params = { get: function () { return null; } };
    }
    if (!shouldTrack(params)) return;

    var info = detectPageInfo();
    var today = getKstDateString(0);
    var sKey = shortSlug(info.slug);

    var dedupeKey = 'kspot_pv_' + today + '_' + sKey;
    if (params.get('force_track') !== '1') {
      try {
        var lastTs = parseInt(sessionStorage.getItem(dedupeKey) || '0', 10);
        if (lastTs && (Date.now() - lastTs) < 60000) return;
        sessionStorage.setItem(dedupeKey, String(Date.now()));
      } catch (e) {}
    }

    hitKey('day__' + today + '__' + sKey);
    hitKey('total__' + sKey);
    hitKey('day__' + today + '__all_site');
    hitKey('total__all_site');
  }

  window.KSpotTracker = {
    namespace: NAMESPACE,
    shortSlug: shortSlug,
    getKstDateString: getKstDateString
  };

  init();
})();
