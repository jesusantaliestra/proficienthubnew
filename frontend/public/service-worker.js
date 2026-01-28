/* Service Worker for Offline Content - ProficientHub v2 */
const CACHE_NAME = 'proficienthub-v2';
const STATIC_CACHE = 'static-v2';
const CONTENT_CACHE = 'content-v2';

// Static assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
];

// API routes to cache for offline
const CACHEABLE_API_ROUTES = [
  '/api/exams/types',
  '/api/pricing/public',
  '/api/institution/branding'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('Service Worker v2: Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .catch((error) => {
        console.log('Service Worker: Cache failed', error);
      })
  );
  self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker v2: Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (!cache.includes('v2')) {
            console.log('Service Worker: Clearing old cache', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') return;
  
  // Skip chrome-extension and other non-http requests
  if (!url.protocol.startsWith('http')) return;
  
  // API requests - network first, cache fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }
  
  // Static assets - cache first
  if (request.destination === 'style' || 
      request.destination === 'script' || 
      request.destination === 'image') {
    event.respondWith(cacheFirstStrategy(request));
    return;
  }
  
  // HTML pages - network first
  event.respondWith(networkFirstStrategy(request));
});

// Network first strategy
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // Network failed, try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback for navigation
    if (request.mode === 'navigate') {
      return new Response(
        '<!DOCTYPE html><html><head><title>Offline</title></head><body><h1>You are offline</h1><p>Please check your connection.</p></body></html>',
        { headers: { 'Content-Type': 'text/html' }, status: 503 }
      );
    }
    
    throw error;
  }
}

// Cache first strategy
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    const cache = await caches.open(STATIC_CACHE);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    return new Response('Not found', { status: 404 });
  }
}

// Handle messages from client
self.addEventListener('message', (event) => {
  const { type, data } = event.data || {};
  
  switch (type) {
    case 'CACHE_CONTENT':
      cacheContent(data.urls).then(() => {
        event.ports[0]?.postMessage({ success: true });
      });
      break;
      
    case 'CACHE_OFFLINE_MATERIALS':
      cacheOfflineMaterials(data.manifest).then((result) => {
        event.ports[0]?.postMessage(result);
      });
      break;
      
    case 'GET_CACHE_STATUS':
      getCacheStatus().then(status => {
        event.ports[0]?.postMessage(status);
      });
      break;
      
    case 'CLEAR_CACHE':
      clearCache().then(() => {
        event.ports[0]?.postMessage({ success: true });
      });
      break;
  }
});

// Cache specific content URLs
async function cacheContent(urls) {
  const cache = await caches.open(CONTENT_CACHE);
  const results = [];
  
  for (const url of urls) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        await cache.put(url, response);
        results.push({ url, success: true });
      } else {
        results.push({ url, success: false, error: response.statusText });
      }
    } catch (error) {
      results.push({ url, success: false, error: error.message });
    }
  }
  
  // Notify all clients
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage({ type: 'CACHE_PROGRESS', results });
  });
  
  return results;
}

// Cache offline materials from manifest
async function cacheOfflineMaterials(manifest) {
  const cache = await caches.open(CONTENT_CACHE);
  let cached = 0;
  let failed = 0;
  
  // Cache exam questions
  if (manifest.exams) {
    for (const exam of manifest.exams) {
      try {
        const url = `/api/exams/${exam.type}/full/${exam.number}`;
        const response = await fetch(url, {
          headers: { 'Authorization': `Bearer ${manifest.token}` }
        });
        if (response.ok) {
          await cache.put(url, response);
          cached++;
        } else {
          failed++;
        }
      } catch {
        failed++;
      }
    }
  }
  
  // Cache library materials
  if (manifest.materials) {
    for (const material of manifest.materials) {
      try {
        const response = await fetch(material.url);
        if (response.ok) {
          await cache.put(material.url, response);
          cached++;
        } else {
          failed++;
        }
      } catch {
        failed++;
      }
    }
  }
  
  return { cached, failed, total: (manifest.exams?.length || 0) + (manifest.materials?.length || 0) };
}

// Get cache status
async function getCacheStatus() {
  const cacheNames = await caches.keys();
  const status = { caches: {}, totalSize: 0 };
  
  for (const name of cacheNames) {
    const cache = await caches.open(name);
    const keys = await cache.keys();
    status.caches[name] = {
      items: keys.length,
      urls: keys.map(k => k.url).slice(0, 10) // First 10 URLs
    };
  }
  
  return status;
}

// Clear all caches
async function clearCache() {
  const cacheNames = await caches.keys();
  await Promise.all(cacheNames.map(name => caches.delete(name)));
  console.log('All caches cleared');
}

// Background sync
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-exam-progress') {
    event.waitUntil(syncExamProgress());
  }
  if (event.tag === 'sync-offline-results') {
    event.waitUntil(syncOfflineResults());
  }
});

async function syncExamProgress() {
  console.log('Syncing exam progress...');
  // Implementation: Get from IndexedDB and send to server
}

async function syncOfflineResults() {
  console.log('Syncing offline results...');
  // Implementation: Get from IndexedDB and send to server
}

console.log('Service Worker v2: Loaded');
