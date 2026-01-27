import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, FlatList } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { offlineStorage, OfflineContent } from '../services/offlineStorage';

const MaterialsScreen: React.FC = () => {
  const { theme } = useTheme();
  const [activeTab, setActiveTab] = useState('library');
  const [offlineContent, setOfflineContent] = useState<OfflineContent[]>([]);

  useEffect(() => {
    loadOfflineContent();
  }, []);

  const loadOfflineContent = async () => {
    const content = await offlineStorage.getAllOfflineContent();
    setOfflineContent(content);
  };

  const materials = [
    { id: '1', title: 'IELTS Reading Strategies', type: 'pdf', icon: 'document-text', size: '2.4 MB' },
    { id: '2', title: 'Academic Vocabulary List', type: 'flashcards', icon: 'albums', size: '500 cards' },
    { id: '3', title: 'Listening Practice Audio', type: 'audio', icon: 'headset', size: '45 min' },
    { id: '4', title: 'Writing Task 2 Templates', type: 'pdf', icon: 'document-text', size: '1.8 MB' },
    { id: '5', title: 'Speaking Part 2 Topics', type: 'flashcards', icon: 'albums', size: '120 cards' },
  ];

  const MaterialItem = ({ item }: { item: typeof materials[0] }) => (
    <TouchableOpacity style={[styles.materialCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
      <View style={[styles.materialIcon, { backgroundColor: theme.colors.primary + '20' }]}>
        <Ionicons name={item.icon as any} size={24} color={theme.colors.primary} />
      </View>
      <View style={styles.materialContent}>
        <Text style={[styles.materialTitle, { color: theme.colors.text }]}>{item.title}</Text>
        <Text style={[styles.materialMeta, { color: theme.colors.textSecondary }]}>{item.type} • {item.size}</Text>
      </View>
      <TouchableOpacity style={styles.downloadBtn}>
        <Ionicons name="download-outline" size={24} color={theme.colors.primary} />
      </TouchableOpacity>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: theme.colors.text }]}>Study Materials</Text>
      </View>

      {/* Tabs */}
      <View style={[styles.tabBar, { backgroundColor: theme.colors.surface }]}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'library' && { backgroundColor: theme.colors.primary }]}
          onPress={() => setActiveTab('library')}
        >
          <Ionicons name="library" size={20} color={activeTab === 'library' ? '#FFF' : theme.colors.textSecondary} />
          <Text style={[styles.tabText, { color: activeTab === 'library' ? '#FFF' : theme.colors.textSecondary }]}>Library</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'offline' && { backgroundColor: theme.colors.primary }]}
          onPress={() => setActiveTab('offline')}
        >
          <Ionicons name="cloud-offline" size={20} color={activeTab === 'offline' ? '#FFF' : theme.colors.textSecondary} />
          <Text style={[styles.tabText, { color: activeTab === 'offline' ? '#FFF' : theme.colors.textSecondary }]}>
            Offline ({offlineContent.length})
          </Text>
        </TouchableOpacity>
      </View>

      {activeTab === 'library' ? (
        <FlatList
          data={materials}
          renderItem={({ item }) => <MaterialItem item={item} />}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
        />
      ) : (
        <View style={styles.offlineContainer}>
          {offlineContent.length > 0 ? (
            <FlatList
              data={offlineContent}
              renderItem={({ item }) => (
                <TouchableOpacity style={[styles.materialCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                  <View style={[styles.materialIcon, { backgroundColor: '#10B98120' }]}>
                    <Ionicons name="checkmark-circle" size={24} color="#10B981" />
                  </View>
                  <View style={styles.materialContent}>
                    <Text style={[styles.materialTitle, { color: theme.colors.text }]}>{item.title}</Text>
                    <Text style={[styles.materialMeta, { color: theme.colors.textSecondary }]}>Available offline</Text>
                  </View>
                  <TouchableOpacity>
                    <Ionicons name="trash-outline" size={24} color={theme.colors.accent} />
                  </TouchableOpacity>
                </TouchableOpacity>
              )}
              keyExtractor={(item) => item.id}
              contentContainerStyle={styles.listContent}
            />
          ) : (
            <View style={styles.emptyState}>
              <Ionicons name="cloud-offline" size={64} color={theme.colors.textSecondary} />
              <Text style={[styles.emptyTitle, { color: theme.colors.text }]}>No Offline Content</Text>
              <Text style={[styles.emptySubtitle, { color: theme.colors.textSecondary }]}>
                Download materials to access them without internet
              </Text>
            </View>
          )}
        </View>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
  },
  tabBar: {
    flexDirection: 'row',
    marginHorizontal: 20,
    borderRadius: 12,
    padding: 4,
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    gap: 8,
  },
  tabText: {
    fontWeight: '600',
  },
  listContent: {
    padding: 20,
  },
  materialCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 12,
  },
  materialIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  materialContent: {
    flex: 1,
    marginLeft: 16,
  },
  materialTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  materialMeta: {
    fontSize: 12,
    marginTop: 2,
  },
  downloadBtn: {
    padding: 8,
  },
  offlineContainer: {
    flex: 1,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 16,
  },
  emptySubtitle: {
    fontSize: 14,
    textAlign: 'center',
    marginTop: 8,
  },
});

export default MaterialsScreen;