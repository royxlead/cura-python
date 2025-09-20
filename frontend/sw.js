/**
 * Cura AI Service Worker
 * Provides offline functionality, caching, and background sync
 */

const CACHE_NAME = 'cura-ai-v2.0.0';
const STATIC_CACHE = 'cura-static-v2.0.0';
const DYNAMIC_CACHE = 'cura-dynamic-v2.0.0';

// Files to cache for offline functionality
const STATIC_FILES = [
    '/',
    '/index.html',
    '/app.css',
    '/app.js',
    '/favicon.svg',
    '/manifest.json',
    // Only cache these if they exist
    // '/icons/icon-72x72.svg',
    // '/icons/icon-96x96.svg',
    // '/icons/icon-128x128.svg',
    // '/icons/icon-144x144.svg',
    // '/icons/icon-152x152.svg',
    // '/icons/icon-192x192.svg',
    // '/icons/icon-384x384.svg',
    // '/icons/icon-512x512.svg',
    // Add other static assets
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap',
    'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap',
    'https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200'
];

// API endpoints that should be cached
const CACHEABLE_APIS = [
    '/auth/profile',
    '/medical/body-systems',
    '/medical/severity-levels',
    '/medical/symptoms/database',
    '/medical/drugs/database'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(async (cache) => {
                console.log('Service Worker: Caching static files');
                
                // Cache files individually to handle failures gracefully
                const cachePromises = STATIC_FILES.map(async (file) => {
                    try {
                        await cache.add(file);
                        console.log('Service Worker: Cached', file);
                    } catch (error) {
                        console.warn('Service Worker: Failed to cache', file, error);
                        // Continue with other files even if one fails
                    }
                });
                
                await Promise.all(cachePromises);
                console.log('Service Worker: Static files cached (with possible failures)');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Service Worker: Failed to open cache', error);
                // Still skip waiting to not block the installation
                return self.skipWaiting();
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Service Worker: Deleting old cache', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker: Activated successfully');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve cached content or fetch from network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Ignore non-http(s) schemes (e.g., chrome-extension) and non-GET requests
    if (request.method !== 'GET') {
        return; // let the browser handle it
    }
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
        return; // do not intercept browser/extension requests
    }

    // Only handle same-origin requests during fetch to prevent caching issues
    // Cross-origin assets (e.g., Google Fonts) are pre-cached during install via cache.addAll
    if (url.origin !== self.location.origin) {
        return; // skip interception for cross-origin at runtime
    }

    // Handle different types of requests
    if (isStaticFile(request.url)) {
        // Static files - cache first strategy
        event.respondWith(cacheFirst(request));
    } else if (isCacheableAPI(request.url)) {
        // API requests - network first with cache fallback
        event.respondWith(networkFirstWithCache(request));
    } else if (isAPIRequest(request.url)) {
        // Other API requests - network only with offline fallback
        event.respondWith(networkOnlyWithOfflineFallback(request));
    } else {
        // Default strategy
        event.respondWith(networkFirstWithCache(request));
    }
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
    console.log('Service Worker: Background sync triggered', event.tag);
    
    if (event.tag === 'chat-message-sync') {
        event.waitUntil(syncChatMessages());
    } else if (event.tag === 'symptom-assessment-sync') {
        event.waitUntil(syncSymptomAssessments());
    } else if (event.tag === 'drug-interaction-sync') {
        event.waitUntil(syncDrugInteractions());
    }
});

// Push notifications
self.addEventListener('push', (event) => {
    console.log('Service Worker: Push received', event.data?.text());
    
    if (event.data) {
        const data = event.data.json();
        
        const options = {
            body: data.body || 'You have a new message from Cura AI',
            icon: '/icons/icon-192x192.png',
            badge: '/icons/icon-72x72.png',
            image: data.image,
            data: data.data,
            actions: [
                {
                    action: 'open',
                    title: 'Open Cura',
                    icon: '/icons/open-action.png'
                },
                {
                    action: 'dismiss',
                    title: 'Dismiss',
                    icon: '/icons/dismiss-action.png'
                }
            ],
            tag: data.tag || 'cura-notification',
            renotify: true,
            requireInteraction: data.urgent || false,
            timestamp: Date.now(),
            vibrate: data.urgent ? [200, 100, 200, 100, 200] : [100, 50, 100]
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title || 'Cura AI', options)
        );
    }
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('Service Worker: Notification clicked', event.action);
    
    event.notification.close();
    
    if (event.action === 'open' || !event.action) {
        event.waitUntil(
            clients.matchAll({ type: 'window', includeUncontrolled: true })
                .then((clientList) => {
                    // Check if app is already open
                    for (const client of clientList) {
                        if (client.url.includes(self.location.origin) && 'focus' in client) {
                            return client.focus();
                        }
                    }
                    
                    // Open new window if app is not open
                    if (clients.openWindow) {
                        const url = event.notification.data?.url || '/';
                        return clients.openWindow(url);
                    }
                })
        );
    }
});

// Message handling from main thread
self.addEventListener('message', (event) => {
    const { type, payload } = event.data;
    
    switch (type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
            
        case 'CACHE_CHAT_MESSAGE':
            cacheChatMessage(payload);
            break;
            
        case 'QUEUE_OFFLINE_ACTION':
            queueOfflineAction(payload);
            break;
            
        case 'GET_CACHE_STATUS':
            getCacheStatus().then(status => {
                event.ports[0].postMessage({ type: 'CACHE_STATUS', payload: status });
            });
            break;
    }
});

// Caching strategies
async function cacheFirst(request) {
    try {
        // Guard: only cache http(s) requests
        const url = new URL(request.url);
        if (url.protocol !== 'http:' && url.protocol !== 'https:') {
            return fetch(request);
        }
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        const cache = await caches.open(STATIC_CACHE);
        cache.put(request, networkResponse.clone());
        
        return networkResponse;
    } catch (error) {
        console.error('Cache first strategy failed:', error);
        return new Response('Offline - content not available', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

async function networkFirstWithCache(request) {
    try {
        // Guard: only cache http(s) requests
        const url = new URL(request.url);
        if (url.protocol !== 'http:' && url.protocol !== 'https:') {
            return fetch(request);
        }
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('Network failed, trying cache:', error);
        
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        return createOfflineResponse(request);
    }
}

async function networkOnlyWithOfflineFallback(request) {
    try {
        return await fetch(request);
    } catch (error) {
        console.log('Network request failed:', error);
        return createOfflineResponse(request);
    }
}

function createOfflineResponse(request) {
    const url = new URL(request.url);
    
    if (url.pathname.includes('/api/')) {
        return new Response(
            JSON.stringify({
                error: 'Offline',
                message: 'This feature requires an internet connection. Your request will be synced when you\'re back online.',
                offline: true
            }),
            {
                status: 503,
                statusText: 'Service Unavailable',
                headers: { 'Content-Type': 'application/json' }
            }
        );
    }
    
    return new Response('You are offline. Please check your internet connection.', {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'text/plain' }
    });
}

// Utility functions
function isStaticFile(url) {
    return STATIC_FILES.some(file => url.includes(file)) ||
           url.includes('.css') ||
           url.includes('.js') ||
           url.includes('.png') ||
           url.includes('.jpg') ||
           url.includes('.ico') ||
           url.includes('.woff') ||
           url.includes('.woff2');
}

function isCacheableAPI(url) {
    return CACHEABLE_APIS.some(api => url.includes(api));
}

function isAPIRequest(url) {
    return url.includes('/api/') || 
           url.includes('/auth/') || 
           url.includes('/chat/') || 
           url.includes('/medical/');
}

// Offline sync functions
async function syncChatMessages() {
    try {
        const db = await openIndexedDB();
        const messages = await getOfflineMessages(db);
        
        for (const message of messages) {
            try {
                const response = await fetch('/chat/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${message.token}`
                    },
                    body: JSON.stringify({
                        content: message.content,
                        conversation_id: message.conversation_id
                    })
                });
                
                if (response.ok) {
                    await removeOfflineMessage(db, message.id);
                    console.log('Synced offline message:', message.id);
                }
            } catch (error) {
                console.error('Failed to sync message:', error);
            }
        }
    } catch (error) {
        console.error('Sync chat messages failed:', error);
    }
}

async function syncSymptomAssessments() {
    try {
        const db = await openIndexedDB();
        const assessments = await getOfflineAssessments(db);
        
        for (const assessment of assessments) {
            try {
                const response = await fetch('/medical/symptom-check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${assessment.token}`
                    },
                    body: JSON.stringify(assessment.data)
                });
                
                if (response.ok) {
                    await removeOfflineAssessment(db, assessment.id);
                    console.log('Synced offline assessment:', assessment.id);
                }
            } catch (error) {
                console.error('Failed to sync assessment:', error);
            }
        }
    } catch (error) {
        console.error('Sync symptom assessments failed:', error);
    }
}

async function syncDrugInteractions() {
    try {
        const db = await openIndexedDB();
        const interactions = await getOfflineDrugChecks(db);
        
        for (const interaction of interactions) {
            try {
                const response = await fetch('/medical/drug-interactions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${interaction.token}`
                    },
                    body: JSON.stringify(interaction.data)
                });
                
                if (response.ok) {
                    await removeOfflineDrugCheck(db, interaction.id);
                    console.log('Synced offline drug check:', interaction.id);
                }
            } catch (error) {
                console.error('Failed to sync drug check:', error);
            }
        }
    } catch (error) {
        console.error('Sync drug interactions failed:', error);
    }
}

// IndexedDB helper functions
function openIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('CuraOfflineDB', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            if (!db.objectStoreNames.contains('messages')) {
                db.createObjectStore('messages', { keyPath: 'id', autoIncrement: true });
            }
            
            if (!db.objectStoreNames.contains('assessments')) {
                db.createObjectStore('assessments', { keyPath: 'id', autoIncrement: true });
            }
            
            if (!db.objectStoreNames.contains('drugChecks')) {
                db.createObjectStore('drugChecks', { keyPath: 'id', autoIncrement: true });
            }
            
            if (!db.objectStoreNames.contains('cache')) {
                db.createObjectStore('cache', { keyPath: 'key' });
            }
        };
    });
}

async function getOfflineMessages(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['messages'], 'readonly');
        const store = transaction.objectStore('messages');
        const request = store.getAll();
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

async function removeOfflineMessage(db, id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['messages'], 'readwrite');
        const store = transaction.objectStore('messages');
        const request = store.delete(id);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve();
    });
}

async function getOfflineAssessments(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['assessments'], 'readonly');
        const store = transaction.objectStore('assessments');
        const request = store.getAll();
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

async function removeOfflineAssessment(db, id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['assessments'], 'readwrite');
        const store = transaction.objectStore('assessments');
        const request = store.delete(id);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve();
    });
}

async function getOfflineDrugChecks(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['drugChecks'], 'readonly');
        const store = transaction.objectStore('drugChecks');
        const request = store.getAll();
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

async function removeOfflineDrugCheck(db, id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['drugChecks'], 'readwrite');
        const store = transaction.objectStore('drugChecks');
        const request = store.delete(id);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve();
    });
}

async function cacheChatMessage(message) {
    try {
        const db = await openIndexedDB();
        const transaction = db.transaction(['messages'], 'readwrite');
        const store = transaction.objectStore('messages');
        
        await store.add({
            content: message.content,
            conversation_id: message.conversation_id,
            token: message.token,
            timestamp: Date.now()
        });
        
        console.log('Message cached for offline sync');
    } catch (error) {
        console.error('Failed to cache message:', error);
    }
}

async function queueOfflineAction(action) {
    try {
        const db = await openIndexedDB();
        const storeName = action.type === 'symptom' ? 'assessments' : 'drugChecks';
        const transaction = db.transaction([storeName], 'readwrite');
        const store = transaction.objectStore(storeName);
        
        await store.add({
            data: action.data,
            token: action.token,
            timestamp: Date.now()
        });
        
        console.log('Action queued for offline sync:', action.type);
        
        // Register background sync
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            const registration = await navigator.serviceWorker.ready;
            const syncTag = action.type === 'symptom' ? 'symptom-assessment-sync' : 'drug-interaction-sync';
            await registration.sync.register(syncTag);
        }
    } catch (error) {
        console.error('Failed to queue offline action:', error);
    }
}

async function getCacheStatus() {
    try {
        const staticCache = await caches.open(STATIC_CACHE);
        const dynamicCache = await caches.open(DYNAMIC_CACHE);
        
        const staticKeys = await staticCache.keys();
        const dynamicKeys = await dynamicCache.keys();
        
        return {
            staticFilesCount: staticKeys.length,
            dynamicFilesCount: dynamicKeys.length,
            totalSize: await calculateCacheSize(staticCache, dynamicCache),
            lastUpdated: Date.now()
        };
    } catch (error) {
        console.error('Failed to get cache status:', error);
        return null;
    }
}

async function calculateCacheSize(staticCache, dynamicCache) {
    let totalSize = 0;
    
    const staticKeys = await staticCache.keys();
    const dynamicKeys = await dynamicCache.keys();
    
    for (const request of [...staticKeys, ...dynamicKeys]) {
        try {
            const response = await staticCache.match(request) || await dynamicCache.match(request);
            if (response) {
                const blob = await response.blob();
                totalSize += blob.size;
            }
        } catch (error) {
            console.error('Error calculating cache size for:', request.url);
        }
    }
    
    return totalSize;
}

console.log('Cura AI Service Worker loaded successfully');