import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

interface LiveClass {
  id: string;
  title: string;
  instructor: string;
  scheduled_time: string;
  duration_minutes: number;
  join_url: string;
  status: 'upcoming' | 'live' | 'completed';
}

const LiveClassesScreen: React.FC = () => {
  const { theme } = useTheme();
  const { user } = useAuth();
  const [classes, setClasses] = useState<LiveClass[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'upcoming' | 'past'>('upcoming');

  useEffect(() => {
    fetchClasses();
  }, []);

  const fetchClasses = async () => {
    try {
      const response = await api.get('/student/upcoming-classes');
      setClasses(response.data.classes || []);
    } catch (error) {
      console.error('Error fetching classes:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchClasses();
    setRefreshing(false);
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric', month: 'short' });
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'live': return '#EF4444';
      case 'upcoming': return '#F59E0B';
      case 'completed': return '#10B981';
      default: return theme.colors.textSecondary;
    }
  };

  const ClassCard = ({ item }: { item: LiveClass }) => (
    <View style={[styles.classCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
      <View style={styles.classHeader}>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) + '20' }]}>
          <View style={[styles.statusDot, { backgroundColor: getStatusColor(item.status) }]} />
          <Text style={[styles.statusText, { color: getStatusColor(item.status) }]}>
            {item.status === 'live' ? '🔴 EN VIVO' : item.status === 'upcoming' ? 'Próxima' : 'Completada'}
          </Text>
        </View>
        <Text style={[styles.duration, { color: theme.colors.textSecondary }]}>{item.duration_minutes} min</Text>
      </View>
      
      <Text style={[styles.classTitle, { color: theme.colors.text }]}>{item.title}</Text>
      <Text style={[styles.instructor, { color: theme.colors.textSecondary }]}>👨‍🏫 {item.instructor}</Text>
      
      <View style={styles.classFooter}>
        <View style={styles.dateTime}>
          <Ionicons name="calendar-outline" size={16} color={theme.colors.textSecondary} />
          <Text style={[styles.dateText, { color: theme.colors.text }]}>{formatDate(item.scheduled_time)}</Text>
          <Ionicons name="time-outline" size={16} color={theme.colors.textSecondary} style={{ marginLeft: 12 }} />
          <Text style={[styles.dateText, { color: theme.colors.text }]}>{formatTime(item.scheduled_time)}</Text>
        </View>
        
        {(item.status === 'live' || item.status === 'upcoming') && (
          <TouchableOpacity 
            style={[styles.joinButton, { backgroundColor: item.status === 'live' ? '#EF4444' : theme.colors.primary }]}
          >
            <Ionicons name="videocam" size={18} color="#FFFFFF" />
            <Text style={styles.joinText}>{item.status === 'live' ? 'Unirse' : 'Recordar'}</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  const upcomingClasses = classes.filter(c => c.status === 'upcoming' || c.status === 'live');
  const pastClasses = classes.filter(c => c.status === 'completed');

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={[styles.title, { color: theme.colors.text }]}>Clases en Vivo</Text>
        <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
          {upcomingClasses.length} clases programadas
        </Text>
      </View>

      {/* Tabs */}
      <View style={[styles.tabs, { backgroundColor: theme.colors.surface }]}>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'upcoming' && { backgroundColor: theme.colors.primary }]}
          onPress={() => setActiveTab('upcoming')}
        >
          <Text style={[styles.tabText, { color: activeTab === 'upcoming' ? '#FFFFFF' : theme.colors.text }]}>
            Próximas
          </Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'past' && { backgroundColor: theme.colors.primary }]}
          onPress={() => setActiveTab('past')}
        >
          <Text style={[styles.tabText, { color: activeTab === 'past' ? '#FFFFFF' : theme.colors.text }]}>
            Pasadas
          </Text>
        </TouchableOpacity>
      </View>

      {/* Classes List */}
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={theme.colors.primary} />}
      >
        {(activeTab === 'upcoming' ? upcomingClasses : pastClasses).length > 0 ? (
          (activeTab === 'upcoming' ? upcomingClasses : pastClasses).map(item => (
            <ClassCard key={item.id} item={item} />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Ionicons name="videocam-off-outline" size={64} color={theme.colors.textSecondary} />
            <Text style={[styles.emptyText, { color: theme.colors.textSecondary }]}>
              {activeTab === 'upcoming' ? 'No hay clases programadas' : 'No hay clases pasadas'}
            </Text>
          </View>
        )}
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
  header: {
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
  },
  subtitle: {
    fontSize: 14,
    marginTop: 4,
  },
  tabs: {
    flexDirection: 'row',
    marginHorizontal: 20,
    padding: 4,
    borderRadius: 12,
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 10,
  },
  tabText: {
    fontWeight: '600',
  },
  scrollContent: {
    padding: 20,
  },
  classCard: {
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 12,
  },
  classHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  duration: {
    fontSize: 12,
  },
  classTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  instructor: {
    fontSize: 14,
    marginBottom: 12,
  },
  classFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  dateTime: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dateText: {
    fontSize: 13,
    marginLeft: 4,
  },
  joinButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  joinText: {
    color: '#FFFFFF',
    fontWeight: '600',
    marginLeft: 6,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    marginTop: 16,
    fontSize: 16,
  },
});

export default LiveClassesScreen;
