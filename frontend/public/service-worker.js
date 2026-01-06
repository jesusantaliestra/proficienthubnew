// Service Worker for ProficientHub - Offline Support
const CACHE_NAME = 'proficienthub-v1';
const DYNAMIC_CACHE = 'proficienthub-dynamic-v1';

// Resources to cache on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
];

// API endpoints that can be cached for offline
const CACHEABLE_API_PATHS = [
  '/api/exams/types',
  '/api/pricing/plans',
  '/api/voice/available-voices'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== DYNAMIC_CACHE)
          .map((name) => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome-extension and other non-http requests
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // API requests - Network first, then cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // Static assets - Cache first, then network
  event.respondWith(cacheFirstStrategy(request));
});

// Cache first strategy - good for static assets
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    // Return cached version and update cache in background
    updateCache(request);
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // Return offline page if available
    const offlineResponse = await caches.match('/offline.html');
    return offlineResponse || new Response('Offline - Please check your connection', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// Network first strategy - good for API calls
async function networkFirstStrategy(request) {
  const url = new URL(request.url);
  const isCacheable = CACHEABLE_API_PATHS.some(path => url.pathname.includes(path));

  try {
    const networkResponse = await fetch(request);
    
    // Cache successful API responses
    if (networkResponse.ok && isCacheable) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache for:', request.url);
    
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return error response for API calls
    return new Response(JSON.stringify({ 
      error: 'Offline', 
      message: 'This feature is not available offline',
      offline: true 
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Update cache in background
async function updateCache(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse);
    }
  } catch (error) {
    // Silently fail - we already have cached version
  }
}

// Handle messages from the main app
self.addEventListener('message', (event) => {
  if (event.data.type === 'CACHE_EXAM_DATA') {
    // Cache exam data for offline use
    cacheExamData(event.data.examType);
  }
  
  if (event.data.type === 'CACHE_LIBRARY_ITEM') {
    // Cache library item for offline use
    cacheLibraryItem(event.data.itemUrl);
  }
  
  if (event.data.type === 'CLEAR_CACHE') {
    clearAllCaches();
  }
});

// Cache exam data for offline practice
async function cacheExamData(examType) {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    const endpoints = [
      `/api/exams/${examType}/practice?section=reading`,
      `/api/exams/${examType}/practice?section=writing`,
      `/api/exams/${examType}/speaking-prompts`,
      `/api/exams/${examType}/writing-tasks`
    ];
    
    for (const endpoint of endpoints) {
      try {
        const response = await fetch(endpoint);
        if (response.ok) {
          await cache.put(endpoint, response);
        }
      } catch (e) {
        console.log('[SW] Could not cache:', endpoint);
      }
    }
    
    // Notify the app that caching is complete
    self.clients.matchAll().then(clients => {
      clients.forEach(client => {
        client.postMessage({ type: 'EXAM_CACHED', examType });
      });
    });
  } catch (error) {
    console.error('[SW] Error caching exam data:', error);
  }
}

// Cache library item (PDF, audio, video)
async function cacheLibraryItem(itemUrl) {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    const response = await fetch(itemUrl);
    
    if (response.ok) {
      await cache.put(itemUrl, response);
      
      self.clients.matchAll().then(clients => {
        clients.forEach(client => {
          client.postMessage({ type: 'LIBRARY_ITEM_CACHED', itemUrl });
        });
      });
    }
  } catch (error) {
    console.error('[SW] Error caching library item:', error);
  }
}

// Clear all caches
async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(cacheNames.map(name => caches.delete(name)));
  
  self.clients.matchAll().then(clients => {
    clients.forEach(client => {
      client.postMessage({ type: 'CACHE_CLEARED' });
    });
  });
}

// Background sync for offline submissions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-exam-submissions') {
    event.waitUntil(syncExamSubmissions());
  }
});

async function syncExamSubmissions() {
  // This would sync any exam submissions made while offline
  // Implementation depends on IndexedDB storage of pending submissions
  console.log('[SW] Syncing exam submissions...');
}

console.log('[SW] Service Worker loaded');
