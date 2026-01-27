import { useState, useEffect, useCallback } from 'react';
import NetInfo, { NetInfoState } from '@react-native-community/netinfo';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface UseOfflineReturn {
  isOnline: boolean;
  isOfflineMode: boolean;
  toggleOfflineMode: () => void;
  saveForOffline: (key: string, data: any) => Promise<void>;
  getOfflineData: <T>(key: string) => Promise<T | null>;
  clearOfflineData: (key?: string) => Promise<void>;
  syncPendingActions: () => Promise<void>;
  queueAction: (action: OfflineAction) => Promise<void>;
}

interface OfflineAction {
  id: string;
  type: string;
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: any;
  timestamp: number;
}

const OFFLINE_PREFIX = '@proficienthub_offline_';
const PENDING_ACTIONS_KEY = '@proficienthub_pending_actions';

export const useOffline = (): UseOfflineReturn => {
  const [isOnline, setIsOnline] = useState(true);
  const [isOfflineMode, setIsOfflineMode] = useState(false);

  useEffect(() => {
    // Check initial network state
    NetInfo.fetch().then((state: NetInfoState) => {
      setIsOnline(state.isConnected ?? true);
    });

    // Subscribe to network changes
    const unsubscribe = NetInfo.addEventListener((state: NetInfoState) => {
      setIsOnline(state.isConnected ?? true);
    });

    // Load offline mode preference
    AsyncStorage.getItem('@proficienthub_offline_mode').then((value) => {
      if (value === 'true') {
        setIsOfflineMode(true);
      }
    });

    return () => unsubscribe();
  }, []);

  const toggleOfflineMode = useCallback(async () => {
    const newMode = !isOfflineMode;
    setIsOfflineMode(newMode);
    await AsyncStorage.setItem('@proficienthub_offline_mode', String(newMode));
  }, [isOfflineMode]);

  const saveForOffline = useCallback(async (key: string, data: any) => {
    try {
      const storageKey = `${OFFLINE_PREFIX}${key}`;
      await AsyncStorage.setItem(storageKey, JSON.stringify({
        data,
        timestamp: Date.now(),
      }));
    } catch (error) {
      console.error('Error saving offline data:', error);
    }
  }, []);

  const getOfflineData = useCallback(async <T>(key: string): Promise<T | null> => {
    try {
      const storageKey = `${OFFLINE_PREFIX}${key}`;
      const item = await AsyncStorage.getItem(storageKey);
      if (item) {
        const { data } = JSON.parse(item);
        return data as T;
      }
      return null;
    } catch (error) {
      console.error('Error getting offline data:', error);
      return null;
    }
  }, []);

  const clearOfflineData = useCallback(async (key?: string) => {
    try {
      if (key) {
        await AsyncStorage.removeItem(`${OFFLINE_PREFIX}${key}`);
      } else {
        const allKeys = await AsyncStorage.getAllKeys();
        const offlineKeys = allKeys.filter(k => k.startsWith(OFFLINE_PREFIX));
        await AsyncStorage.multiRemove(offlineKeys);
      }
    } catch (error) {
      console.error('Error clearing offline data:', error);
    }
  }, []);

  const queueAction = useCallback(async (action: OfflineAction) => {
    try {
      const existing = await AsyncStorage.getItem(PENDING_ACTIONS_KEY);
      const actions: OfflineAction[] = existing ? JSON.parse(existing) : [];
      actions.push(action);
      await AsyncStorage.setItem(PENDING_ACTIONS_KEY, JSON.stringify(actions));
    } catch (error) {
      console.error('Error queuing offline action:', error);
    }
  }, []);

  const syncPendingActions = useCallback(async () => {
    if (!isOnline) return;

    try {
      const existing = await AsyncStorage.getItem(PENDING_ACTIONS_KEY);
      if (!existing) return;

      const actions: OfflineAction[] = JSON.parse(existing);
      const failedActions: OfflineAction[] = [];

      for (const action of actions) {
        try {
          // Here you would actually make the API call
          // const response = await api[action.method.toLowerCase()](action.endpoint, action.data);
          console.log('Syncing action:', action.type);
        } catch (error) {
          console.error('Failed to sync action:', action.id, error);
          failedActions.push(action);
        }
      }

      // Save failed actions for retry
      if (failedActions.length > 0) {
        await AsyncStorage.setItem(PENDING_ACTIONS_KEY, JSON.stringify(failedActions));
      } else {
        await AsyncStorage.removeItem(PENDING_ACTIONS_KEY);
      }
    } catch (error) {
      console.error('Error syncing pending actions:', error);
    }
  }, [isOnline]);

  // Auto-sync when coming back online
  useEffect(() => {
    if (isOnline && !isOfflineMode) {
      syncPendingActions();
    }
  }, [isOnline, isOfflineMode, syncPendingActions]);

  return {
    isOnline,
    isOfflineMode,
    toggleOfflineMode,
    saveForOffline,
    getOfflineData,
    clearOfflineData,
    syncPendingActions,
    queueAction,
  };
};
