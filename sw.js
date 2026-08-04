/* JMR Lifting Solutions & Engineering — Service Worker
   Strategy:
   - Precache: shell (HTML index, CSS, JS, logo)
   - Runtime cache:
     * Same-origin static assets (images, fonts, PDFs) → cache-first, network fallback
     * HTML navigations → network-first (fresh content), cache fallback for offline
     * Google Fonts → stale-while-revalidate
   - Third-party (Uploadcare, Formspree, GA, GSAP CDN) → network only, never cached
*/

const VERSION = 'jmr-v12-scope';
const SHELL_CACHE = `jmr-shell-${VERSION}`;
const RUNTIME_CACHE = `jmr-runtime-${VERSION}`;
const FONT_CACHE = `jmr-fonts-${VERSION}`;

const SHELL_ASSETS = [
  '/',
  '/index.html',
  '/services.html',
  '/tools.html',
  '/ai-lift-plan.html',
  '/company.html',
  '/contact.html',
  '/crane-lift-plan.html',
  '/404.html',
  '/css/style.css',
  '/css/landing.css',
  '/js/main.js',
  '/assets/svg/favicon.svg',
  '/assets/icons/icon-192.png',
  '/assets/icons/icon-512.png',
  '/manifest.json'
];

const CACHEABLE_ORIGINS = [
  self.location.origin,
  'https://fonts.googleapis.com',
  'https://fonts.gstatic.com'
];

const NEVER_CACHE_HOSTS = [
  'formspree.io',
  'formsubmit.co',
  'uploadcare.com',
  'ucarecdn.com',
  'googletagmanager.com',
  'google-analytics.com',
  'www.google-analytics.com',
  'analytics.google.com'
];

// ---- INSTALL ----
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(SHELL_CACHE).then(cache => {
      // Add each shell asset individually so one 404 doesn't nuke the whole precache
      return Promise.all(
        SHELL_ASSETS.map(url =>
          cache.add(url).catch(err => console.warn('[SW] precache skip', url, err.message))
        )
      );
    })
  );
});

// ---- ACTIVATE ----
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => !k.endsWith(VERSION))
          .map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// ---- FETCH ----
self.addEventListener('fetch', event => {
  const req = event.request;

  // Only handle GET
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Never cache/intercept sensitive third-party endpoints
  if (NEVER_CACHE_HOSTS.some(h => url.hostname.includes(h))) return;

  // Only handle allowed origins
  if (!CACHEABLE_ORIGINS.includes(url.origin)) return;

  // Google Fonts → stale-while-revalidate
  if (url.origin === 'https://fonts.googleapis.com' || url.origin === 'https://fonts.gstatic.com') {
    event.respondWith(staleWhileRevalidate(req, FONT_CACHE));
    return;
  }

  // HTML navigations → network-first
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(networkFirst(req, RUNTIME_CACHE));
    return;
  }

  // Everything else same-origin → cache-first with runtime cache
  event.respondWith(cacheFirst(req, RUNTIME_CACHE));
});

// ---- Strategies ----
async function networkFirst(req, cacheName) {
  const cache = await caches.open(cacheName);
  try {
    const fresh = await fetch(req);
    if (fresh && fresh.ok) cache.put(req, fresh.clone());
    return fresh;
  } catch (err) {
    const cached = await cache.match(req);
    if (cached) return cached;
    // Offline fallback for navigations
    const offline = await caches.match('/index.html');
    if (offline) return offline;
    return new Response('Offline — please reconnect.', {
      status: 503,
      headers: {'Content-Type': 'text/plain'}
    });
  }
}

async function cacheFirst(req, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  if (cached) return cached;
  try {
    const fresh = await fetch(req);
    if (fresh && fresh.ok) cache.put(req, fresh.clone());
    return fresh;
  } catch (err) {
    return new Response('', {status: 504});
  }
}

async function staleWhileRevalidate(req, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  const fetchPromise = fetch(req).then(fresh => {
    if (fresh && fresh.ok) cache.put(req, fresh.clone());
    return fresh;
  }).catch(() => cached);
  return cached || fetchPromise;
}

// ---- Message channel (for skipWaiting from client) ----
self.addEventListener('message', event => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});
