import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system';

const OFFLINE_DATA_KEY = 'offline_data';
const DOWNLOADED_CONTENT_DIR = FileSystem.documentDirectory + 'downloads/';

export interface OfflineContent {
  id: string;
  type: 'material' | 'flashcard' | 'video' | 'exam';
  title: string;
  data: any;
  downloadedAt: string;
  fileUri?: string;
}

export const offlineStorage = {
  // Save data for offline access
  async saveForOffline(content: OfflineContent): Promise<void> {
    try {
      const existingData = await this.getAllOfflineContent();
      const index = existingData.findIndex(c => c.id === content.id);
      
      if (index >= 0) {
        existingData[index] = content;
      } else {
        existingData.push(content);
      }
      
      await AsyncStorage.setItem(OFFLINE_DATA_KEY, JSON.stringify(existingData));
    } catch (error) {
      console.error('Failed to save offline content:', error);
      throw error;
    }
  },

  // Get all offline content
  async getAllOfflineContent(): Promise<OfflineContent[]> {
    try {
      const data = await AsyncStorage.getItem(OFFLINE_DATA_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Failed to get offline content:', error);
      return [];
    }
  },

  // Get specific offline content
  async getOfflineContent(id: string): Promise<OfflineContent | null> {
    const allContent = await this.getAllOfflineContent();
    return allContent.find(c => c.id === id) || null;
  },

  // Download file for offline access
  async downloadFile(url: string, filename: string): Promise<string> {
    try {
      // Ensure directory exists
      const dirInfo = await FileSystem.getInfoAsync(DOWNLOADED_CONTENT_DIR);
      if (!dirInfo.exists) {
        await FileSystem.makeDirectoryAsync(DOWNLOADED_CONTENT_DIR, { intermediates: true });
      }

      const fileUri = DOWNLOADED_CONTENT_DIR + filename;
      const downloadResult = await FileSystem.downloadAsync(url, fileUri);
      
      return downloadResult.uri;
    } catch (error) {
      console.error('Failed to download file:', error);
      throw error;
    }
  },

  // Delete offline content
  async deleteOfflineContent(id: string): Promise<void> {
    try {
      const allContent = await this.getAllOfflineContent();
      const content = allContent.find(c => c.id === id);
      
      // Delete file if exists
      if (content?.fileUri) {
        const fileInfo = await FileSystem.getInfoAsync(content.fileUri);
        if (fileInfo.exists) {
          await FileSystem.deleteAsync(content.fileUri);
        }
      }
      
      // Remove from storage
      const filtered = allContent.filter(c => c.id !== id);
      await AsyncStorage.setItem(OFFLINE_DATA_KEY, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to delete offline content:', error);
      throw error;
    }
  },

  // Get storage info
  async getStorageInfo(): Promise<{ usedSpace: number; itemCount: number }> {
    try {
      const allContent = await this.getAllOfflineContent();
      let totalSize = 0;
      
      for (const content of allContent) {
        if (content.fileUri) {
          const fileInfo = await FileSystem.getInfoAsync(content.fileUri);
          if (fileInfo.exists && 'size' in fileInfo) {
            totalSize += fileInfo.size;
          }
        }
      }
      
      return {
        usedSpace: totalSize,
        itemCount: allContent.length,
      };
    } catch (error) {
      console.error('Failed to get storage info:', error);
      return { usedSpace: 0, itemCount: 0 };
    }
  },

  // Clear all offline data
  async clearAllOfflineData(): Promise<void> {
    try {
      await AsyncStorage.removeItem(OFFLINE_DATA_KEY);
      
      const dirInfo = await FileSystem.getInfoAsync(DOWNLOADED_CONTENT_DIR);
      if (dirInfo.exists) {
        await FileSystem.deleteAsync(DOWNLOADED_CONTENT_DIR, { idempotent: true });
      }
    } catch (error) {
      console.error('Failed to clear offline data:', error);
      throw error;
    }
  },
};