/**
 * Offline Content Service
 * Manages downloading and caching content for offline use
 */

import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

class OfflineContentService {
  constructor() {
    this.dbName = 'proficienthub-offline';
    this.dbVersion = 1;
    this.db = null;
  }

  /**
   * Initialize IndexedDB for offline storage
   */
  async initDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Store for exam content
        if (!db.objectStoreNames.contains('exams')) {
          db.createObjectStore('exams', { keyPath: 'id' });
        }
        
        // Store for materials
        if (!db.objectStoreNames.contains('materials')) {
          db.createObjectStore('materials', { keyPath: 'id' });
        }
        
        // Store for offline exam results
        if (!db.objectStoreNames.contains('pendingResults')) {
          db.createObjectStore('pendingResults', { keyPath: 'id', autoIncrement: true });
        }
        
        // Store for vocabulary/flashcards
        if (!db.objectStoreNames.contains('vocabulary')) {
          db.createObjectStore('vocabulary', { keyPath: 'id' });
        }
        
        // Store for download progress
        if (!db.objectStoreNames.contains('downloadStatus')) {
          db.createObjectStore('downloadStatus', { keyPath: 'type' });
        }
      };
    });
  }

  /**
   * Get offline content manifest from server
   */
  async getManifest() {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    try {
      const response = await axios.get(`${API_URL}/api/user/offline-manifest`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get offline manifest:', error);
      return null;
    }
  }

  /**
   * Download and cache exam content for offline use
   */
  async downloadExamContent(examType, examNumbers = [1, 2, 3]) {
    if (!this.db) await this.initDB();
    
    const token = localStorage.getItem('token');
    const results = { success: 0, failed: 0, errors: [] };
    
    for (const num of examNumbers) {
      try {
        const response = await axios.get(
          `${API_URL}/api/exams/${examType}/full/${num}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        
        const examData = {
          id: `${examType}-${num}`,
          examType,
          examNumber: num,
          data: response.data,
          downloadedAt: new Date().toISOString()
        };
        
        await this.saveToStore('exams', examData);
        results.success++;
        
        // Dispatch progress event
        window.dispatchEvent(new CustomEvent('offlineProgress', {
          detail: { type: 'exam', examType, examNumber: num, status: 'success' }
        }));
      } catch (error) {
        results.failed++;
        results.errors.push({ examType, examNumber: num, error: error.message });
      }
    }
    
    await this.updateDownloadStatus('exams', { lastDownload: new Date().toISOString(), ...results });
    return results;
  }

  /**
   * Download library materials
   */
  async downloadMaterials(materialIds) {
    if (!this.db) await this.initDB();
    
    const token = localStorage.getItem('token');
    const results = { success: 0, failed: 0 };
    
    for (const id of materialIds) {
      try {
        const response = await axios.get(
          `${API_URL}/api/library/items/${id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        
        const material = {
          id,
          ...response.data,
          downloadedAt: new Date().toISOString()
        };
        
        await this.saveToStore('materials', material);
        results.success++;
      } catch (error) {
        results.failed++;
      }
    }
    
    await this.updateDownloadStatus('materials', { lastDownload: new Date().toISOString(), ...results });
    return results;
  }

  /**
   * Download vocabulary/flashcards
   */
  async downloadVocabulary() {
    if (!this.db) await this.initDB();
    
    const token = localStorage.getItem('token');
    
    try {
      const response = await axios.get(
        `${API_URL}/api/library/vocabulary`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      for (const item of response.data.items || []) {
        await this.saveToStore('vocabulary', {
          id: item.id,
          ...item,
          downloadedAt: new Date().toISOString()
        });
      }
      
      await this.updateDownloadStatus('vocabulary', {
        lastDownload: new Date().toISOString(),
        count: response.data.items?.length || 0
      });
      
      return { success: true, count: response.data.items?.length || 0 };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Get cached exam content
   */
  async getOfflineExam(examType, examNumber) {
    if (!this.db) await this.initDB();
    
    const id = `${examType}-${examNumber}`;
    return this.getFromStore('exams', id);
  }

  /**
   * Get all cached exams
   */
  async getAllOfflineExams() {
    if (!this.db) await this.initDB();
    return this.getAllFromStore('exams');
  }

  /**
   * Get cached material
   */
  async getOfflineMaterial(id) {
    if (!this.db) await this.initDB();
    return this.getFromStore('materials', id);
  }

  /**
   * Get all cached vocabulary
   */
  async getOfflineVocabulary() {
    if (!this.db) await this.initDB();
    return this.getAllFromStore('vocabulary');
  }

  /**
   * Save exam result for later sync
   */
  async savePendingResult(result) {
    if (!this.db) await this.initDB();
    
    const pendingResult = {
      ...result,
      savedAt: new Date().toISOString(),
      synced: false
    };
    
    await this.saveToStore('pendingResults', pendingResult);
    
    // Request background sync if available
    if ('serviceWorker' in navigator && 'sync' in window.SyncManager) {
      const registration = await navigator.serviceWorker.ready;
      await registration.sync.register('sync-offline-results');
    }
    
    return pendingResult;
  }

  /**
   * Get pending results that need sync
   */
  async getPendingResults() {
    if (!this.db) await this.initDB();
    return this.getAllFromStore('pendingResults');
  }

  /**
   * Sync pending results with server
   */
  async syncPendingResults() {
    if (!navigator.onLine) return { synced: 0, error: 'Offline' };
    
    const pending = await this.getPendingResults();
    const token = localStorage.getItem('token');
    let synced = 0;
    
    for (const result of pending) {
      if (result.synced) continue;
      
      try {
        await axios.post(
          `${API_URL}/api/exams/attempt`,
          result,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        
        // Mark as synced
        result.synced = true;
        result.syncedAt = new Date().toISOString();
        await this.saveToStore('pendingResults', result);
        synced++;
      } catch (error) {
        console.error('Failed to sync result:', error);
      }
    }
    
    return { synced, total: pending.length };
  }

  /**
   * Get download status for a content type
   */
  async getDownloadStatus(type) {
    if (!this.db) await this.initDB();
    return this.getFromStore('downloadStatus', type);
  }

  /**
   * Update download status
   */
  async updateDownloadStatus(type, status) {
    if (!this.db) await this.initDB();
    await this.saveToStore('downloadStatus', { type, ...status });
  }

  /**
   * Get total offline storage usage
   */
  async getStorageUsage() {
    if (!this.db) await this.initDB();
    
    const exams = await this.getAllFromStore('exams');
    const materials = await this.getAllFromStore('materials');
    const vocabulary = await this.getAllFromStore('vocabulary');
    
    return {
      exams: exams.length,
      materials: materials.length,
      vocabulary: vocabulary.length,
      estimatedSize: JSON.stringify({ exams, materials, vocabulary }).length
    };
  }

  /**
   * Clear all offline content
   */
  async clearAllContent() {
    if (!this.db) await this.initDB();
    
    await this.clearStore('exams');
    await this.clearStore('materials');
    await this.clearStore('vocabulary');
    
    // Also clear service worker cache
    if ('serviceWorker' in navigator) {
      const registration = await navigator.serviceWorker.ready;
      registration.active?.postMessage({ type: 'CLEAR_CACHE' });
    }
    
    return { success: true };
  }

  // IndexedDB helpers
  saveToStore(storeName, data) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(data);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  getFromStore(storeName, key) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(key);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  getAllFromStore(storeName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  }

  clearStore(storeName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.clear();
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Check if app is running offline
   */
  isOffline() {
    return !navigator.onLine;
  }

  /**
   * Listen for online/offline status changes
   */
  onStatusChange(callback) {
    window.addEventListener('online', () => callback(true));
    window.addEventListener('offline', () => callback(false));
  }
}

// Singleton instance
const offlineContentService = new OfflineContentService();
export default offlineContentService;
