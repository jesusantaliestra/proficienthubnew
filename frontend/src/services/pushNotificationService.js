/**
 * Push Notifications Service for Capacitor
 * Handles native push notifications for iOS and Android
 */

import { PushNotifications } from '@capacitor/push-notifications';
import { Preferences } from '@capacitor/preferences';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

class PushNotificationService {
  constructor() {
    this.initialized = false;
    this.token = null;
  }

  /**
   * Check if push notifications are supported
   */
  isSupported() {
    return window.Capacitor?.isNativePlatform?.() || false;
  }

  /**
   * Initialize push notifications
   */
  async initialize() {
    if (!this.isSupported()) {
      console.log('Push notifications not supported on this platform');
      return false;
    }

    try {
      // Request permission
      const permStatus = await PushNotifications.checkPermissions();
      
      if (permStatus.receive === 'prompt') {
        const permission = await PushNotifications.requestPermissions();
        if (permission.receive !== 'granted') {
          console.log('Push notification permission denied');
          return false;
        }
      } else if (permStatus.receive !== 'granted') {
        console.log('Push notification permission not granted');
        return false;
      }

      // Register for push notifications
      await PushNotifications.register();

      // Set up listeners
      this.setupListeners();
      
      this.initialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize push notifications:', error);
      return false;
    }
  }

  /**
   * Set up push notification event listeners
   */
  setupListeners() {
    // On registration success
    PushNotifications.addListener('registration', async (token) => {
      console.log('Push registration success, token:', token.value);
      this.token = token.value;
      
      // Store token locally
      await Preferences.set({
        key: 'push_token',
        value: token.value
      });

      // Register token with backend
      await this.registerTokenWithBackend(token.value);
    });

    // On registration error
    PushNotifications.addListener('registrationError', (error) => {
      console.error('Push registration error:', error.error);
    });

    // On notification received (app in foreground)
    PushNotifications.addListener('pushNotificationReceived', (notification) => {
      console.log('Push notification received:', notification);
      
      // Show custom in-app notification or update UI
      this.handleForegroundNotification(notification);
    });

    // On notification action performed (user tapped notification)
    PushNotifications.addListener('pushNotificationActionPerformed', (notification) => {
      console.log('Push notification action performed:', notification);
      
      // Navigate to appropriate screen based on notification data
      this.handleNotificationAction(notification);
    });
  }

  /**
   * Register push token with backend
   * @param {string} pushToken - Device push token
   */
  async registerTokenWithBackend(pushToken) {
    try {
      const authToken = localStorage.getItem('token');
      if (!authToken) {
        console.log('No auth token, skipping push token registration');
        return;
      }

      const platform = window.Capacitor?.getPlatform?.() || 'unknown';
      
      await axios.post(
        `${API_URL}/api/notifications/register-token`,
        {
          token: pushToken,
          device_info: {
            platform: platform,
            timestamp: new Date().toISOString()
          }
        },
        {
          headers: { Authorization: `Bearer ${authToken}` }
        }
      );

      console.log('Push token registered with backend');
    } catch (error) {
      console.error('Failed to register push token:', error);
    }
  }

  /**
   * Handle notification received while app is in foreground
   * @param {object} notification - Push notification data
   */
  handleForegroundNotification(notification) {
    // You can show a custom in-app notification here
    // or trigger a toast/alert
    const event = new CustomEvent('pushNotification', {
      detail: notification
    });
    window.dispatchEvent(event);
  }

  /**
   * Handle user action on notification (tap)
   * @param {object} notification - Push notification action data
   */
  handleNotificationAction(notification) {
    const data = notification.notification?.data || {};
    
    // Navigate based on notification type
    if (data.type === 'exam_reminder') {
      window.location.href = `/exam/${data.exam_type}`;
    } else if (data.type === 'live_class') {
      window.location.href = `/live-classes`;
    } else if (data.type === 'progress_report') {
      window.location.href = `/dashboard`;
    } else {
      // Default: go to dashboard
      window.location.href = '/dashboard';
    }
  }

  /**
   * Get stored push token
   */
  async getToken() {
    if (this.token) return this.token;
    
    const { value } = await Preferences.get({ key: 'push_token' });
    this.token = value;
    return value;
  }

  /**
   * Clear push token (on logout)
   */
  async clearToken() {
    await Preferences.remove({ key: 'push_token' });
    this.token = null;
    this.initialized = false;
  }

  /**
   * Check if notifications are enabled
   */
  async areNotificationsEnabled() {
    if (!this.isSupported()) return false;
    
    const permStatus = await PushNotifications.checkPermissions();
    return permStatus.receive === 'granted';
  }
}

// Singleton instance
const pushNotificationService = new PushNotificationService();
export default pushNotificationService;
