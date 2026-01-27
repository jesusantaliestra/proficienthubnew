import React from 'react';
import { View, Text, ScrollView, StyleSheet, Dimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';

const { width } = Dimensions.get('window');

const ProgressScreen: React.FC = () => {
  const { theme } = useTheme();
  const { user } = useAuth();

  const skillProgress = [
    { name: 'Reading', score: 78, color: '#3B82F6' },
    { name: 'Writing', score: 65, color: '#10B981' },
    { name: 'Listening', score: 82, color: '#8B5CF6' },
    { name: 'Speaking', score: 70, color: '#F59E0B' },
  ];

  const recentExams = [
    { date: 'Jan 25', type: 'Full Mock', score: 72 },
    { date: 'Jan 22', type: 'Reading', score: 78 },
    { date: 'Jan 20', type: 'Writing', score: 65 },
    { date: 'Jan 18', type: 'Listening', score: 82 },
  ];

  const ProgressBar = ({ skill }: { skill: typeof skillProgress[0] }) => (
    <View style={styles.progressItem}>
      <View style={styles.progressHeader}>
        <Text style={[styles.progressLabel, { color: theme.colors.text }]}>{skill.name}</Text>
        <Text style={[styles.progressValue, { color: skill.color }]}>{skill.score}%</Text>
      </View>
      <View style={[styles.progressBarBg, { backgroundColor: theme.colors.border }]}>
        <View style={[styles.progressBarFill, { width: `${skill.score}%`, backgroundColor: skill.color }]} />
      </View>
    </View>
  );

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.colors.text }]}>Your Progress</Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            {user?.examType?.toUpperCase() || 'IELTS'} Preparation
          </Text>
        </View>

        {/* Overall Score Card */}
        <View style={[styles.scoreCard, { backgroundColor: theme.colors.primary }]}>
          <View style={styles.scoreCircle}>
            <Text style={styles.scoreValue}>74</Text>
            <Text style={styles.scoreLabel}>Overall</Text>
          </View>
          <View style={styles.scoreInfo}>
            <Text style={styles.scoreTitle}>Predicted Band Score</Text>
            <Text style={styles.scoreSubtitle}>Based on your practice tests</Text>
            <View style={styles.targetBadge}>
              <Ionicons name="flag" size={14} color="#FFFFFF" />
              <Text style={styles.targetText}>Target: 7.5</Text>
            </View>
          </View>
        </View>

        {/* Skills Breakdown */}
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>Skills Breakdown</Text>
        <View style={[styles.skillsCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
          {skillProgress.map((skill) => (
            <ProgressBar key={skill.name} skill={skill} />
          ))}
        </View>

        {/* Recent Exams */}
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>Recent Exams</Text>
        <View style={[styles.examsCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
          {recentExams.map((exam, index) => (
            <View key={index} style={[styles.examItem, index < recentExams.length - 1 && styles.examItemBorder]}>
              <View>
                <Text style={[styles.examType, { color: theme.colors.text }]}>{exam.type}</Text>
                <Text style={[styles.examDate, { color: theme.colors.textSecondary }]}>{exam.date}</Text>
              </View>
              <View style={[styles.examScore, { backgroundColor: theme.colors.primary + '20' }]}>
                <Text style={[styles.examScoreText, { color: theme.colors.primary }]}>{exam.score}%</Text>
              </View>
            </View>
          ))}
        </View>

        {/* Tips */}
        <View style={[styles.tipsCard, { backgroundColor: '#FEF3C7' }]}>
          <Ionicons name="bulb" size={24} color="#F59E0B" />
          <View style={styles.tipsContent}>
            <Text style={styles.tipsTitle}>Improvement Tip</Text>
            <Text style={styles.tipsText}>Focus on Writing Task 2. Your essay structure could use more practice.</Text>
          </View>
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
  scoreCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderRadius: 16,
    marginBottom: 24,
  },
  scoreCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scoreValue: {
    color: '#FFFFFF',
    fontSize: 28,
    fontWeight: 'bold',
  },
  scoreLabel: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 12,
  },
  scoreInfo: {
    marginLeft: 20,
    flex: 1,
  },
  scoreTitle: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  scoreSubtitle: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 12,
    marginTop: 4,
  },
  targetBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginTop: 12,
    gap: 6,
  },
  targetText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  skillsCard: {
    padding: 20,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 24,
  },
  progressItem: {
    marginBottom: 16,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  progressLabel: {
    fontWeight: '600',
  },
  progressValue: {
    fontWeight: 'bold',
  },
  progressBarBg: {
    height: 8,
    borderRadius: 4,
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  examsCard: {
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 24,
    overflow: 'hidden',
  },
  examItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  examItemBorder: {
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  examType: {
    fontWeight: '600',
  },
  examDate: {
    fontSize: 12,
    marginTop: 2,
  },
  examScore: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  examScoreText: {
    fontWeight: 'bold',
  },
  tipsCard: {
    flexDirection: 'row',
    padding: 16,
    borderRadius: 12,
  },
  tipsContent: {
    marginLeft: 12,
    flex: 1,
  },
  tipsTitle: {
    fontWeight: 'bold',
    color: '#92400E',
  },
  tipsText: {
    color: '#92400E',
    fontSize: 14,
    marginTop: 4,
  },
});

export default ProgressScreen;