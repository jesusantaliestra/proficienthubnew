import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';

const examSections = [
  { id: 'reading', name: 'Reading', icon: 'book', color: '#3B82F6' },
  { id: 'writing', name: 'Writing', icon: 'create', color: '#10B981' },
  { id: 'listening', name: 'Listening', icon: 'headset', color: '#8B5CF6' },
  { id: 'speaking', name: 'Speaking', icon: 'mic', color: '#F59E0B' },
];

const ExamsScreen: React.FC = () => {
  const { theme } = useTheme();
  const { user } = useAuth();

  const ExamCard = ({ section }: { section: typeof examSections[0] }) => (
    <TouchableOpacity style={[styles.examCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
      <View style={[styles.examIcon, { backgroundColor: section.color + '20' }]}>
        <Ionicons name={section.icon as any} size={32} color={section.color} />
      </View>
      <Text style={[styles.examTitle, { color: theme.colors.text }]}>{section.name}</Text>
      <Text style={[styles.examSubtitle, { color: theme.colors.textSecondary }]}>Practice tests available</Text>
      <View style={styles.examActions}>
        <TouchableOpacity style={[styles.examBtn, { backgroundColor: section.color }]}>
          <Text style={styles.examBtnText}>Start Test</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: theme.colors.text }]}>Practice Exams</Text>
        <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
          {user?.examType?.toUpperCase() || 'IELTS'} Preparation
        </Text>
      </View>

      {/* Full Mock Test */}
      <TouchableOpacity style={[styles.mockTestCard, { backgroundColor: theme.colors.primary }]}>
        <View style={styles.mockTestContent}>
          <Ionicons name="document-text" size={40} color="#FFFFFF" />
          <View style={styles.mockTestText}>
            <Text style={styles.mockTestTitle}>Full Mock Test</Text>
            <Text style={styles.mockTestSubtitle}>Complete exam simulation (3 hours)</Text>
          </View>
        </View>
        <View style={styles.mockTestBadge}>
          <Text style={styles.mockTestBadgeText}>RECOMMENDED</Text>
        </View>
      </TouchableOpacity>

      {/* Section Tests */}
      <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>Practice by Section</Text>
      <ScrollView contentContainerStyle={styles.examGrid}>
        {examSections.map((section) => (
          <ExamCard key={section.id} section={section} />
        ))}
      </ScrollView>

      {/* Credits Info */}
      <View style={[styles.creditsCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
        <Ionicons name="wallet" size={24} color={theme.colors.primary} />
        <Text style={[styles.creditsText, { color: theme.colors.text }]}>
          You have <Text style={{ fontWeight: 'bold', color: theme.colors.primary }}>{user?.credits || 0}</Text> credits remaining
        </Text>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
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
  mockTestCard: {
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
  },
  mockTestContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  mockTestText: {
    marginLeft: 16,
    flex: 1,
  },
  mockTestTitle: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: 'bold',
  },
  mockTestSubtitle: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 14,
    marginTop: 4,
  },
  mockTestBadge: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 12,
  },
  mockTestBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: 'bold',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  examGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -6,
  },
  examCard: {
    width: '48%',
    margin: '1%',
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
  },
  examIcon: {
    width: 56,
    height: 56,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  examTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  examSubtitle: {
    fontSize: 12,
    marginTop: 4,
  },
  examActions: {
    marginTop: 12,
  },
  examBtn: {
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
  examBtnText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  creditsCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginTop: 24,
  },
  creditsText: {
    marginLeft: 12,
    fontSize: 14,
  },
});

export default ExamsScreen;