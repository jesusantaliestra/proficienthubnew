import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

interface ExamSection {
  id: string;
  name: string;
  icon: string;
  color: string;
  duration: number;
  questions: number;
}

const ExamStartScreen: React.FC<{ route: any; navigation: any }> = ({ route, navigation }) => {
  const { theme } = useTheme();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  
  const examType = route?.params?.examType || user?.examType || 'ielts';

  const examInfo: Record<string, { name: string; color: string; sections: ExamSection[] }> = {
    ielts: {
      name: 'IELTS',
      color: '#EF4444',
      sections: [
        { id: 'reading', name: 'Reading', icon: 'book', color: '#3B82F6', duration: 60, questions: 40 },
        { id: 'listening', name: 'Listening', icon: 'headset', color: '#8B5CF6', duration: 30, questions: 40 },
        { id: 'writing', name: 'Writing', icon: 'create', color: '#10B981', duration: 60, questions: 2 },
        { id: 'speaking', name: 'Speaking', icon: 'mic', color: '#F59E0B', duration: 15, questions: 3 },
      ]
    },
    'ielts-academic': {
      name: 'IELTS Academic',
      color: '#EF4444',
      sections: [
        { id: 'reading', name: 'Academic Reading', icon: 'book', color: '#3B82F6', duration: 60, questions: 40 },
        { id: 'listening', name: 'Listening', icon: 'headset', color: '#8B5CF6', duration: 30, questions: 40 },
        { id: 'writing', name: 'Academic Writing', icon: 'create', color: '#10B981', duration: 60, questions: 2 },
        { id: 'speaking', name: 'Speaking', icon: 'mic', color: '#F59E0B', duration: 15, questions: 3 },
      ]
    },
    'ielts-general': {
      name: 'IELTS General',
      color: '#F87171',
      sections: [
        { id: 'reading', name: 'General Reading', icon: 'book', color: '#3B82F6', duration: 60, questions: 40 },
        { id: 'listening', name: 'Listening', icon: 'headset', color: '#8B5CF6', duration: 30, questions: 40 },
        { id: 'writing', name: 'General Writing', icon: 'create', color: '#10B981', duration: 60, questions: 2 },
        { id: 'speaking', name: 'Speaking', icon: 'mic', color: '#F59E0B', duration: 15, questions: 3 },
      ]
    },
    toefl: {
      name: 'TOEFL',
      color: '#3B82F6',
      sections: [
        { id: 'reading', name: 'Reading', icon: 'book', color: '#3B82F6', duration: 54, questions: 30 },
        { id: 'listening', name: 'Listening', icon: 'headset', color: '#8B5CF6', duration: 41, questions: 28 },
        { id: 'writing', name: 'Writing', icon: 'create', color: '#10B981', duration: 50, questions: 2 },
        { id: 'speaking', name: 'Speaking', icon: 'mic', color: '#F59E0B', duration: 17, questions: 4 },
      ]
    },
    cambridge: {
      name: 'Cambridge',
      color: '#8B5CF6',
      sections: [
        { id: 'reading', name: 'Reading & Use of English', icon: 'book', color: '#3B82F6', duration: 90, questions: 56 },
        { id: 'listening', name: 'Listening', icon: 'headset', color: '#8B5CF6', duration: 40, questions: 30 },
        { id: 'writing', name: 'Writing', icon: 'create', color: '#10B981', duration: 90, questions: 2 },
        { id: 'speaking', name: 'Speaking', icon: 'mic', color: '#F59E0B', duration: 14, questions: 4 },
      ]
    },
    'pte-academic': {
      name: 'PTE Academic',
      color: '#F97316',
      sections: [
        { id: 'speaking_writing', name: 'Speaking & Writing', icon: 'mic', color: '#F59E0B', duration: 77, questions: 25 },
        { id: 'reading', name: 'Reading', icon: 'book', color: '#3B82F6', duration: 32, questions: 15 },
        { id: 'listening', name: 'Listening', icon: 'headset', color: '#8B5CF6', duration: 45, questions: 15 },
      ]
    },
    'pte-core': {
      name: 'PTE Core',
      color: '#FB923C',
      sections: [
        { id: 'speaking_writing', name: 'Speaking & Writing', icon: 'mic', color: '#F59E0B', duration: 54, questions: 20 },
        { id: 'reading', name: 'Reading', icon: 'book', color: '#3B82F6', duration: 29, questions: 15 },
        { id: 'listening', name: 'Listening', icon: 'headset', color: '#8B5CF6', duration: 30, questions: 12 },
      ]
    },
    pte: {
      name: 'PTE Academic',
      color: '#F97316',
      sections: [
        { id: 'speaking_writing', name: 'Speaking & Writing', icon: 'mic', color: '#F59E0B', duration: 77, questions: 25 },
        { id: 'reading', name: 'Reading', icon: 'book', color: '#3B82F6', duration: 32, questions: 15 },
        { id: 'listening', name: 'Listening', icon: 'headset', color: '#8B5CF6', duration: 45, questions: 15 },
      ]
    }
  };

  const exam = examInfo[examType] || examInfo['ielts-academic'];

  const startExam = async (sectionId: string) => {
    setLoading(true);
    try {
      // Navigate to exam simulator
      Alert.alert(
        'Iniciar Examen',
        `¿Estás listo para comenzar la sección de ${exam.sections.find(s => s.id === sectionId)?.name}?`,
        [
          { text: 'Cancelar', style: 'cancel' },
          { 
            text: 'Comenzar', 
            onPress: () => {
              // In a real app, navigate to ExamSimulatorScreen
              Alert.alert('¡Próximamente!', 'El simulador de examen estará disponible pronto.');
            }
          }
        ]
      );
    } finally {
      setLoading(false);
    }
  };

  const startFullExam = () => {
    Alert.alert(
      'Examen Completo',
      `¿Deseas realizar el examen completo de ${exam.name}? Esto tomará aproximadamente ${exam.sections.reduce((acc, s) => acc + s.duration, 0)} minutos.`,
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Comenzar', onPress: () => Alert.alert('¡Próximamente!', 'El examen completo estará disponible pronto.') }
      ]
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={[styles.examHeader, { backgroundColor: exam.color }]}>
          <View style={styles.examHeaderContent}>
            <Text style={styles.examName}>{exam.name}</Text>
            <Text style={styles.examSubtitle}>Simulador de Examen</Text>
          </View>
          <View style={styles.examBadge}>
            <Ionicons name="school" size={32} color="#FFFFFF" />
          </View>
        </View>

        {/* Full Exam Button */}
        <TouchableOpacity 
          style={[styles.fullExamButton, { backgroundColor: theme.colors.primary }]}
          onPress={startFullExam}
        >
          <View style={styles.fullExamContent}>
            <Ionicons name="play-circle" size={28} color="#FFFFFF" />
            <View style={styles.fullExamText}>
              <Text style={styles.fullExamTitle}>Examen Completo</Text>
              <Text style={styles.fullExamDuration}>
                ~{exam.sections.reduce((acc, s) => acc + s.duration, 0)} minutos
              </Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#FFFFFF" />
        </TouchableOpacity>

        {/* Sections */}
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>Practicar por Sección</Text>
        
        {exam.sections.map(section => (
          <TouchableOpacity
            key={section.id}
            style={[styles.sectionCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}
            onPress={() => startExam(section.id)}
          >
            <View style={[styles.sectionIcon, { backgroundColor: section.color + '20' }]}>
              <Ionicons name={section.icon as any} size={24} color={section.color} />
            </View>
            <View style={styles.sectionInfo}>
              <Text style={[styles.sectionName, { color: theme.colors.text }]}>{section.name}</Text>
              <View style={styles.sectionMeta}>
                <Ionicons name="time-outline" size={14} color={theme.colors.textSecondary} />
                <Text style={[styles.sectionMetaText, { color: theme.colors.textSecondary }]}>
                  {section.duration} min
                </Text>
                <Ionicons name="help-circle-outline" size={14} color={theme.colors.textSecondary} style={{ marginLeft: 12 }} />
                <Text style={[styles.sectionMetaText, { color: theme.colors.textSecondary }]}>
                  {section.questions} preguntas
                </Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={24} color={theme.colors.textSecondary} />
          </TouchableOpacity>
        ))}

        {/* Tips Card */}
        <View style={[styles.tipsCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
          <View style={styles.tipsHeader}>
            <Ionicons name="bulb" size={24} color="#F59E0B" />
            <Text style={[styles.tipsTitle, { color: theme.colors.text }]}>Consejos</Text>
          </View>
          <Text style={[styles.tipsText, { color: theme.colors.textSecondary }]}>
            • Practica en un ambiente tranquilo{'\n'}
            • Usa auriculares para las secciones de audio{'\n'}
            • Respeta los tiempos límite{'\n'}
            • Revisa tus respuestas antes de enviar
          </Text>
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
  examHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 24,
    borderRadius: 20,
    marginBottom: 20,
  },
  examHeaderContent: {},
  examName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  examSubtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 4,
  },
  examBadge: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  fullExamButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    borderRadius: 16,
    marginBottom: 24,
  },
  fullExamContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  fullExamText: {
    marginLeft: 12,
  },
  fullExamTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  fullExamDuration: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.8)',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  sectionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 12,
  },
  sectionIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sectionInfo: {
    flex: 1,
    marginLeft: 16,
  },
  sectionName: {
    fontSize: 16,
    fontWeight: '600',
  },
  sectionMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  sectionMetaText: {
    fontSize: 12,
    marginLeft: 4,
  },
  tipsCard: {
    padding: 20,
    borderRadius: 16,
    borderWidth: 1,
    marginTop: 12,
  },
  tipsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  tipsText: {
    fontSize: 14,
    lineHeight: 22,
  },
});

export default ExamStartScreen;
