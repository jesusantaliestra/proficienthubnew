import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useWhiteLabel } from '../contexts/WhiteLabelContext';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

interface Stats {
  credits: number;
  examsCompleted: number;
  avgScore: number;
  streak: number;
}

const HomeScreen: React.FC = () => {
  const { theme } = useTheme();
  const { config } = useWhiteLabel();
  const { user } = useAuth();
  const [stats, setStats] = useState<Stats>({ credits: 0, examsCompleted: 0, avgScore: 0, streak: 0 });
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboard = async () => {
    try {
      const response = await api.get('/student/dashboard');
      if (response.data) {
        setStats({
          credits: response.data.credits || user?.credits || 0,
          examsCompleted: response.data.total_exams || 0,
          avgScore: response.data.average_score || 0,
          streak: response.data.streak || 0,
        });
      }
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchDashboard();
    setRefreshing(false);
  };

  const StatCard = ({ icon, label, value, color }: { icon: string; label: string; value: string | number; color: string }) => (
    <View style={[styles.statCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
      <View style={[styles.statIcon, { backgroundColor: color + '20' }]}>
        <Ionicons name={icon as any} size={24} color={color} />
      </View>
      <Text style={[styles.statValue, { color: theme.colors.text }]}>{value}</Text>
      <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>{label}</Text>
    </View>
  );

  const QuickAction = ({ icon, label, onPress, color }: { icon: string; label: string; onPress: () => void; color: string }) => (
    <TouchableOpacity style={[styles.quickAction, { backgroundColor: color }]} onPress={onPress}>
      <Ionicons name={icon as any} size={28} color="#FFFFFF" />
      <Text style={styles.quickActionText}>{label}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={theme.colors.primary} />}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={[styles.greeting, { color: theme.colors.textSecondary }]}>Welcome back,</Text>
            <Text style={[styles.userName, { color: theme.colors.text }]}>{user?.name || 'Student'}</Text>
          </View>
          <TouchableOpacity style={[styles.notificationBtn, { backgroundColor: theme.colors.surface }]}>
            <Ionicons name="notifications-outline" size={24} color={theme.colors.text} />
          </TouchableOpacity>
        </View>

        {/* Current Exam Badge */}
        <View style={[styles.examBadge, { backgroundColor: theme.colors.primary }]}>
          <Ionicons name="school" size={24} color="#FFFFFF" />
          <View style={styles.examBadgeText}>
            <Text style={styles.examBadgeLabel}>Currently Preparing</Text>
            <Text style={styles.examBadgeValue}>{user?.examType?.toUpperCase() || 'IELTS'}</Text>
          </View>
          <TouchableOpacity style={styles.examBadgeBtn}>
            <Text style={styles.examBadgeBtnText}>Change</Text>
          </TouchableOpacity>
        </View>

        {/* Stats Grid */}
        <View style={styles.statsGrid}>
          <StatCard icon="wallet-outline" label="Credits" value={stats.credits} color={theme.colors.primary} />
          <StatCard icon="document-text-outline" label="Exams Done" value={stats.examsCompleted} color={theme.colors.secondary} />
          <StatCard icon="trophy-outline" label="Avg Score" value={`${stats.avgScore}%`} color="#F59E0B" />
          <StatCard icon="flame-outline" label="Day Streak" value={stats.streak} color="#EF4444" />
        </View>

        {/* Quick Actions */}
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>Quick Actions</Text>
        <View style={styles.quickActionsGrid}>
          <QuickAction icon="play-circle" label="Start Mock Exam" onPress={() => {}} color={theme.colors.primary} />
          <QuickAction icon="mic" label="Speaking Practice" onPress={() => {}} color={theme.colors.secondary} />
          <QuickAction icon="create" label="Writing Test" onPress={() => {}} color={theme.colors.accent} />
          <QuickAction icon="chatbubbles" label="AI Tutor" onPress={() => {}} color="#8B5CF6" />
        </View>

        {/* Recent Activity */}
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>Continue Learning</Text>
        <View style={[styles.activityCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
          <View style={styles.activityIcon}>
            <Ionicons name="book" size={32} color={theme.colors.primary} />
          </View>
          <View style={styles.activityContent}>
            <Text style={[styles.activityTitle, { color: theme.colors.text }]}>Reading Section Practice</Text>
            <Text style={[styles.activitySubtitle, { color: theme.colors.textSecondary }]}>3 passages remaining</Text>
            <View style={styles.progressBar}>
              <View style={[styles.progressFill, { width: '65%', backgroundColor: theme.colors.primary }]} />
            </View>
          </View>
          <TouchableOpacity style={[styles.continueBtn, { backgroundColor: theme.colors.primary }]}>
            <Ionicons name="arrow-forward" size={20} color="#FFFFFF" />
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  greeting: {
    fontSize: 14,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  notificationBtn: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  examBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
    marginBottom: 24,
  },
  examBadgeText: {
    flex: 1,
    marginLeft: 12,
  },
  examBadgeLabel: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 12,
  },
  examBadgeValue: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: 'bold',
  },
  examBadgeBtn: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  examBadgeBtnText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -6,
    marginBottom: 24,
  },
  statCard: {
    width: '48%',
    margin: '1%',
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
  },
  statIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
  },
  statLabel: {
    fontSize: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -6,
    marginBottom: 24,
  },
  quickAction: {
    width: '48%',
    margin: '1%',
    padding: 20,
    borderRadius: 16,
    alignItems: 'center',
  },
  quickActionText: {
    color: '#FFFFFF',
    fontWeight: '600',
    marginTop: 8,
    textAlign: 'center',
  },
  activityCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
  },
  activityIcon: {
    width: 56,
    height: 56,
    borderRadius: 12,
    backgroundColor: '#58CC0220',
    justifyContent: 'center',
    alignItems: 'center',
  },
  activityContent: {
    flex: 1,
    marginLeft: 16,
  },
  activityTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  activitySubtitle: {
    fontSize: 12,
    marginTop: 2,
  },
  progressBar: {
    height: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 3,
    marginTop: 8,
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
  continueBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default HomeScreen;