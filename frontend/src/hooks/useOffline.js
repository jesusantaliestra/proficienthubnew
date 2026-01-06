import { useState, useEffect, useCallback } from 'react';

export function useOffline() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isServiceWorkerReady, setIsServiceWorkerReady] = useState(false);
  const [cachedExams, setCachedExams] = useState([]);
  const [cachedLibraryItems, setCachedLibraryItems] = useState([]);

  useEffect(() => {
    // Online/offline listeners
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Register service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/service-worker.js')
        .then((registration) => {
          console.log('Service Worker registered:', registration.scope);
          setIsServiceWorkerReady(true);
        })
        .catch((error) => {
          console.error('Service Worker registration failed:', error);
        });

      // Listen for messages from service worker
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data.type === 'EXAM_CACHED') {
          setCachedExams(prev => [...new Set([...prev, event.data.examType])]);
        }
        if (event.data.type === 'LIBRARY_ITEM_CACHED') {
          setCachedLibraryItems(prev => [...new Set([...prev, event.data.itemUrl])]);
        }
        if (event.data.type === 'CACHE_CLEARED') {
          setCachedExams([]);
          setCachedLibraryItems([]);
        }
      });
    }

    // Load cached items from localStorage
    const storedExams = localStorage.getItem('cachedExams');
    const storedItems = localStorage.getItem('cachedLibraryItems');
    if (storedExams) setCachedExams(JSON.parse(storedExams));
    if (storedItems) setCachedLibraryItems(JSON.parse(storedItems));

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Save cached items to localStorage
  useEffect(() => {
    localStorage.setItem('cachedExams', JSON.stringify(cachedExams));
  }, [cachedExams]);

  useEffect(() => {
    localStorage.setItem('cachedLibraryItems', JSON.stringify(cachedLibraryItems));
  }, [cachedLibraryItems]);

  // Cache exam for offline use
  const cacheExam = useCallback((examType) => {
    if (navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({
        type: 'CACHE_EXAM_DATA',
        examType
      });
    }
  }, []);

  // Cache library item for offline use
  const cacheLibraryItem = useCallback((itemUrl) => {
    if (navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({
        type: 'CACHE_LIBRARY_ITEM',
        itemUrl
      });
    }
  }, []);

  // Clear all offline cache
  const clearCache = useCallback(() => {
    if (navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({
        type: 'CLEAR_CACHE'
      });
    }
  }, []);

  // Check if an exam is cached
  const isExamCached = useCallback((examType) => {
    return cachedExams.includes(examType);
  }, [cachedExams]);

  // Check if a library item is cached
  const isLibraryItemCached = useCallback((itemUrl) => {
    return cachedLibraryItems.includes(itemUrl);
  }, [cachedLibraryItems]);

  return {
    isOnline,
    isServiceWorkerReady,
    cachedExams,
    cachedLibraryItems,
    cacheExam,
    cacheLibraryItem,
    clearCache,
    isExamCached,
    isLibraryItemCached
  };
}

// Offline indicator component
export function OfflineIndicator() {
  const { isOnline } = useOffline();

  if (isOnline) return null;

  return (
    <div className="fixed bottom-4 left-4 bg-yellow-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 z-50">
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3" 
        />
      </svg>
      <span className="font-medium">You're offline</span>
    </div>
  );
}

export default useOffline;
