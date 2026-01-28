import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { api } from '../services/api';
import notificationService from '../services/notifications';

interface NotificationSettings {
  study_reminders: boolean;
  class_reminders: boolean;
  streak_warnings: boolean;
  badge_notifications: boolean;
  tutor_responses: boolean;
  marketing: boolean;
  reminder_time: string;
}

const NotificationSettingsScreen: React.FC = () => {
  const { theme } = useTheme();
  const [settings, setSettings] = useState<NotificationSettings>({
    study_reminders: true,
    class_reminders: true,
    streak_warnings: true,
    badge_notifications: true,
    tutor_responses: true,
    marketing: false,
    reminder_time: '18:00',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [pushToken, setPushToken] = useState<string | null>(null);

  useEffect(() => {
    initializeNotifications();
    fetchSettings();
  }, []);

  const initializeNotifications = async () => {
    const token = await notificationService.initialize();
    setPushToken(token);

    if (token) {
      // Register token with backend
      try {
        await api.post('/notifications/register-token', {
          token,
          device_type: 'mobile',
        });
      } catch (error) {
        console.error('Failed to register push token:', error);
      }
    }
  };

  const fetchSettings = async () => {
    try {
      const response = await api.get('/notifications/settings');
      setSettings(prev => ({ ...prev, ...response.data }));
    } catch (error) {
      console.error('Failed to fetch notification settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateSetting = async (key: keyof NotificationSettings, value: boolean) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    
    try {
      await api.post('/notifications/settings', { [key]: value });
      
      // Update local notifications based on setting
      if (key === 'study_reminders') {
        if (value) {
          const [hour, minute] = settings.reminder_time.split(':').map(Number);
          await notificationService.scheduleStudyReminder(hour, minute);
        } else {
          await notificationService.cancelNotificationsByType('study_reminder');
        }
      }
      
      if (key === 'streak_warnings') {
        if (value) {
          await notificationService.scheduleStreakWarning();
        } else {
          await notificationService.cancelNotificationsByType('streak_warning');
        }
      }
    } catch (error) {
      console.error('Failed to update setting:', error);
      // Revert on error
      setSettings(prev => ({ ...prev, [key]: !value }));
    }
  };

  const testNotification = async () => {
    try {
      await notificationService.notifyBadgeEarned('Test Badge', '🧪');
      Alert.alert('Success', 'Test notification sent!');
    } catch (error) {
      Alert.alert('Error', 'Failed to send test notification');
    }
  };

  const notificationItems = [
    {
      key: 'study_reminders',
      title: 'Study Reminders',
      description: 'Daily reminder to practice',
      icon: 'book',
    },
    {
      key: 'class_reminders',
      title: 'Class Reminders',
      description: '30 minutes before live classes',
      icon: 'videocam',
    },
    {
      key: 'streak_warnings',
      title: 'Streak Warnings',
      description: 'Alert when streak is at risk',
      icon: 'flame',
    },
    {
      key: 'badge_notifications',
      title: 'Badge Notifications',
      description: 'When you earn achievements',
      icon: 'medal',
    },
    {
      key: 'tutor_responses',
      title: 'AI Tutor Responses',
      description: 'When tutor replies to you',
      icon: 'chatbubbles',
    },
    {
      key: 'marketing',
      title: 'News & Updates',
      description: 'New features and promotions',
      icon: 'newspaper',
    },
  ];

  if (loading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: theme.colors.background }]}>
        <Text style={{ color: theme.colors.text }}>Loading...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.colors.text }]}>Notification Settings</Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            Control how you receive notifications
          </Text>
        </View>

        {/* Push Status */}
        <View style={[styles.statusCard, { backgroundColor: pushToken ? '#D1FAE5' : '#FEE2E2' }]}>
          <Ionicons 
            name={pushToken ? 'checkmark-circle' : 'alert-circle'} 
            size={24} 
            color={pushToken ? '#059669' : '#DC2626'} 
          />
          <View style={styles.statusText}>
            <Text style={[styles.statusTitle, { color: pushToken ? '#059669' : '#DC2626' }]}>
              {pushToken ? 'Push Notifications Enabled' : 'Push Notifications Disabled'}
            </Text>
            <Text style={styles.statusDescription}>
              {pushToken 
                ? 'You will receive notifications on this device' 
                : 'Enable notifications in your device settings'}
            </Text>
          </View>
        </View>

        {/* Notification Options */}
        <View style={[styles.section, { backgroundColor: theme.colors.surface }]}>
          {notificationItems.map((item, index) => (
            <View 
              key={item.key}
              style={[
                styles.settingItem,
                index < notificationItems.length - 1 && { borderBottomWidth: 1, borderBottomColor: theme.colors.border }
              ]}
            >
              <View style={styles.settingLeft}>
                <View style={[styles.iconBox, { backgroundColor: theme.colors.background }]}>
                  <Ionicons name={item.icon as any} size={20} color={theme.colors.primary} />
                </View>
                <View style={styles.settingInfo}>
                  <Text style={[styles.settingTitle, { color: theme.colors.text }]}>{item.title}</Text>
                  <Text style={[styles.settingDescription, { color: theme.colors.textSecondary }]}>
                    {item.description}
                  </Text>
                </View>
              </View>
              <Switch
                value={settings[item.key as keyof NotificationSettings] as boolean}
                onValueChange={(value) => updateSetting(item.key as keyof NotificationSettings, value)}
                trackColor={{ false: '#E5E7EB', true: '#BBF7D0' }}
                thumbColor={settings[item.key as keyof NotificationSettings] ? '#58CC02' : '#9CA3AF'}
              />
            </View>
          ))}
        </View>

        {/* Reminder Time */}
        <View style={[styles.section, { backgroundColor: theme.colors.surface }]}>
          <View style={styles.settingItem}>
            <View style={styles.settingLeft}>
              <View style={[styles.iconBox, { backgroundColor: theme.colors.background }]}>
                <Ionicons name="time" size={20} color={theme.colors.primary} />
              </View>
              <View style={styles.settingInfo}>
                <Text style={[styles.settingTitle, { color: theme.colors.text }]}>Reminder Time</Text>
                <Text style={[styles.settingDescription, { color: theme.colors.textSecondary }]}>
                  Daily study reminder time
                </Text>
              </View>
            </View>
            <Text style={[styles.timeText, { color: theme.colors.primary }]}>
              {settings.reminder_time}
            </Text>
          </View>
        </View>

        {/* Test Button */}
        <TouchableOpacity 
          style={[styles.testButton, { backgroundColor: theme.colors.surface }]}
          onPress={testNotification}
        >
          <Ionicons name="notifications-outline" size={20} color={theme.colors.primary} />
          <Text style={[styles.testButtonText, { color: theme.colors.text }]}>
            Send Test Notification
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollContent: {
    padding: 20,
  },
  header: {
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
  },
  subtitle: {
    fontSize: 14,
    marginTop: 4,
  },
  statusCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
    marginBottom: 20,
  },
  statusText: {
    marginLeft: 12,
    flex: 1,
  },
  statusTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  statusDescription: {
    fontSize: 13,
    color: '#6B7280',
    marginTop: 2,
  },
  section: {
    borderRadius: 16,
    marginBottom: 16,
    overflow: 'hidden',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  iconBox: {
    width: 40,
    height: 40,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  settingInfo: {
    marginLeft: 12,
    flex: 1,
  },
  settingTitle: {
    fontSize: 15,
    fontWeight: '600',
  },
  settingDescription: {
    fontSize: 12,
    marginTop: 2,
  },
  timeText: {
    fontSize: 16,
    fontWeight: '600',
  },
  testButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 16,
    gap: 8,
  },
  testButtonText: {
    fontSize: 15,
    fontWeight: '600',
  },
});

export default NotificationSettingsScreen;
