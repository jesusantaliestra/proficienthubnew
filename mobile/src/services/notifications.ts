import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configure notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

// Notification types
export type NotificationType = 
  | 'class_reminder'
  | 'study_reminder'
  | 'badge_earned'
  | 'tutor_response'
  | 'streak_warning'
  | 'exam_result'
  | 'new_content';

export interface PushNotificationData {
  type: NotificationType;
  title: string;
  body: string;
  data?: Record<string, any>;
}

class NotificationService {
  private expoPushToken: string | null = null;

  async initialize(): Promise<string | null> {
    try {
      // Check if device can receive push notifications
      if (!Device.isDevice) {
        console.log('Push notifications require a physical device');
        return null;
      }

      // Request permissions
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.log('Push notification permission not granted');
        return null;
      }

      // Get Expo push token
      const projectId = Constants.expoConfig?.extra?.eas?.projectId;
      const token = (await Notifications.getExpoPushTokenAsync({ projectId })).data;
      
      this.expoPushToken = token;
      await AsyncStorage.setItem('pushToken', token);

      // Configure Android channel
      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('default', {
          name: 'ProficientHub',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#58CC02',
        });

        await Notifications.setNotificationChannelAsync('reminders', {
          name: 'Study Reminders',
          importance: Notifications.AndroidImportance.HIGH,
          vibrationPattern: [0, 250],
        });

        await Notifications.setNotificationChannelAsync('classes', {
          name: 'Live Classes',
          importance: Notifications.AndroidImportance.MAX,
          sound: 'default',
        });
      }

      console.log('Push token:', token);
      return token;

    } catch (error) {
      console.error('Error initializing notifications:', error);
      return null;
    }
  }

  getToken(): string | null {
    return this.expoPushToken;
  }

  // Schedule a local notification
  async scheduleLocalNotification(
    notification: PushNotificationData,
    trigger: Notifications.NotificationTriggerInput
  ): Promise<string> {
    const identifier = await Notifications.scheduleNotificationAsync({
      content: {
        title: notification.title,
        body: notification.body,
        data: { type: notification.type, ...notification.data },
        sound: true,
      },
      trigger,
    });
    return identifier;
  }

  // Schedule study reminder
  async scheduleStudyReminder(hour: number = 18, minute: number = 0): Promise<void> {
    // Cancel existing study reminders
    await this.cancelNotificationsByType('study_reminder');

    await this.scheduleLocalNotification(
      {
        type: 'study_reminder',
        title: '📚 Time to Study!',
        body: "Don't break your streak! Practice for at least 15 minutes today.",
      },
      {
        hour,
        minute,
        repeats: true,
      }
    );
  }

  // Schedule class reminder (30 minutes before)
  async scheduleClassReminder(classId: string, className: string, classTime: Date): Promise<void> {
    const reminderTime = new Date(classTime.getTime() - 30 * 60 * 1000);

    if (reminderTime > new Date()) {
      await this.scheduleLocalNotification(
        {
          type: 'class_reminder',
          title: '🎥 Live Class Starting Soon',
          body: `"${className}" starts in 30 minutes`,
          data: { classId },
        },
        {
          date: reminderTime,
        }
      );
    }
  }

  // Schedule streak warning (if user hasn't practiced today by 8pm)
  async scheduleStreakWarning(): Promise<void> {
    const now = new Date();
    const warningTime = new Date(now);
    warningTime.setHours(20, 0, 0, 0);

    if (warningTime > now) {
      await this.scheduleLocalNotification(
        {
          type: 'streak_warning',
          title: '🔥 Streak at Risk!',
          body: 'Practice now to keep your streak alive!',
        },
        {
          date: warningTime,
        }
      );
    }
  }

  // Send immediate notification for badge earned
  async notifyBadgeEarned(badgeName: string, badgeIcon: string): Promise<void> {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: `${badgeIcon} Badge Earned!`,
        body: `Congratulations! You earned the "${badgeName}" badge!`,
        data: { type: 'badge_earned', badgeName },
      },
      trigger: null, // Immediate
    });
  }

  // Send notification for AI tutor response
  async notifyTutorResponse(agentName: string, preview: string): Promise<void> {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: `🤖 ${agentName} replied`,
        body: preview.length > 100 ? preview.substring(0, 100) + '...' : preview,
        data: { type: 'tutor_response' },
      },
      trigger: null,
    });
  }

  // Cancel notifications by type
  async cancelNotificationsByType(type: NotificationType): Promise<void> {
    const scheduled = await Notifications.getAllScheduledNotificationsAsync();
    
    for (const notification of scheduled) {
      if (notification.content.data?.type === type) {
        await Notifications.cancelScheduledNotificationAsync(notification.identifier);
      }
    }
  }

  // Cancel all notifications
  async cancelAllNotifications(): Promise<void> {
    await Notifications.cancelAllScheduledNotificationsAsync();
  }

  // Get all scheduled notifications
  async getScheduledNotifications(): Promise<Notifications.NotificationRequest[]> {
    return await Notifications.getAllScheduledNotificationsAsync();
  }

  // Add notification listener
  addNotificationReceivedListener(
    callback: (notification: Notifications.Notification) => void
  ): Notifications.Subscription {
    return Notifications.addNotificationReceivedListener(callback);
  }

  // Add response listener (when user taps notification)
  addNotificationResponseListener(
    callback: (response: Notifications.NotificationResponse) => void
  ): Notifications.Subscription {
    return Notifications.addNotificationResponseReceivedListener(callback);
  }

  // Get badge count
  async getBadgeCount(): Promise<number> {
    return await Notifications.getBadgeCountAsync();
  }

  // Set badge count
  async setBadgeCount(count: number): Promise<void> {
    await Notifications.setBadgeCountAsync(count);
  }
}

export const notificationService = new NotificationService();
export default notificationService;
