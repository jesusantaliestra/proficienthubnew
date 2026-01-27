import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

interface Agent {
  id: string;
  name: string;
  name_es: string;
  description: string;
  icon: string;
  credits_per_message: number;
  voice_enabled: boolean;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  creditsUsed?: number;
}

interface Credits {
  remaining_credits: number;
  total_credits: number;
  used_credits: number;
}

const AITutorScreen: React.FC = () => {
  const { theme } = useTheme();
  const { user } = useAuth();
  
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [credits, setCredits] = useState<Credits>({ remaining_credits: 0, total_credits: 0, used_credits: 0 });
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  const scrollViewRef = useRef<ScrollView>(null);
  const examType = user?.examType || 'ielts';

  useEffect(() => {
    fetchAgents();
    fetchCredits();
  }, []);

  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const fetchAgents = async () => {
    try {
      const response = await api.get('/ai-agents/available');
      setAgents(response.data.agents || []);
      if (response.data.agents?.length > 0) {
        selectAgent(response.data.agents[0]);
      }
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  const fetchCredits = async () => {
    try {
      const response = await api.get('/ai-agents/credits');
      setCredits(response.data);
    } catch (error) {
      console.error('Error fetching credits:', error);
    }
  };

  const selectAgent = (agent: Agent) => {
    setSelectedAgent(agent);
    setSessionId(null);
    setMessages([{
      role: 'assistant',
      content: getWelcomeMessage(agent),
      timestamp: new Date()
    }]);
  };

  const getWelcomeMessage = (agent: Agent): string => {
    const agentMessages: Record<string, string> = {
      official_tutor: `¡Hola! Soy tu ${agent.name_es} para ${examType.toUpperCase()}.\n\n• Estrategias de examen\n• Práctica guiada\n• Gramática y vocabulario\n\n¿En qué puedo ayudarte?`,
      mock_coach: `¡Bienvenido! Soy tu ${agent.name_es}.\n\nMi método:\n• Preguntas de práctica reales\n• 5 intentos por pregunta\n• Pistas después de cada error\n\nEscribe "empezar" para comenzar.`,
      planner: `¡Hola! Soy tu ${agent.name_es}.\n\nCrearemos un plan personalizado. Cuéntame:\n• ¿Cuándo es tu examen?\n• ¿Horas disponibles?\n• ¿Áreas débiles?`
    };
    return agentMessages[agent.id] || `¡Hola! Soy ${agent.name_es}. ¿En qué puedo ayudarte?`;
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading || !selectedAgent) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await api.post('/ai-agents/interact', {
        agent_type: selectedAgent.id,
        message: inputMessage,
        exam_type: examType,
        session_id: sessionId,
        voice_enabled: false
      });

      if (!response.data.success) {
        if (response.data.error === 'insufficient_credits') {
          Alert.alert('Sin Créditos', 'No tienes créditos suficientes para continuar.');
          return;
        }
      }

      if (response.data.session_id && !sessionId) {
        setSessionId(response.data.session_id);
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        creditsUsed: response.data.credits_consumed
      }]);

      fetchCredits();

    } catch (error: any) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Error de conexión. Por favor, intenta de nuevo.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const AgentIcon = ({ agentId }: { agentId: string }) => {
    const icons: Record<string, string> = {
      official_tutor: 'school',
      mock_coach: 'trophy',
      planner: 'calendar'
    };
    return <Ionicons name={(icons[agentId] || 'chatbubbles') as any} size={20} color="#FFFFFF" />;
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Header */}
      <View style={[styles.header, { backgroundColor: theme.colors.surface, borderBottomColor: theme.colors.border }]}>
        <View style={styles.headerLeft}>
          {selectedAgent && (
            <>
              <View style={[styles.agentIconHeader, { backgroundColor: theme.colors.primary }]}>
                <AgentIcon agentId={selectedAgent.id} />
              </View>
              <View>
                <Text style={[styles.headerTitle, { color: theme.colors.text }]}>{selectedAgent.name_es}</Text>
                <Text style={[styles.headerSubtitle, { color: theme.colors.textSecondary }]}>{examType.toUpperCase()}</Text>
              </View>
            </>
          )}
        </View>
        <View style={[styles.creditsBox, { backgroundColor: '#FEF3C7' }]}>
          <Ionicons name="wallet" size={16} color="#D97706" />
          <Text style={styles.creditsText}>{credits.remaining_credits}</Text>
        </View>
      </View>

      {/* Agent Selector */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.agentSelector}>
        {agents.map(agent => (
          <TouchableOpacity
            key={agent.id}
            onPress={() => selectAgent(agent)}
            style={[
              styles.agentChip,
              { 
                backgroundColor: selectedAgent?.id === agent.id ? theme.colors.primary : theme.colors.surface,
                borderColor: theme.colors.border
              }
            ]}
          >
            <AgentIcon agentId={agent.id} />
            <Text style={[
              styles.agentChipText, 
              { color: selectedAgent?.id === agent.id ? '#FFFFFF' : theme.colors.text }
            ]}>
              {agent.name_es}
            </Text>
            <Text style={[
              styles.agentCredits,
              { color: selectedAgent?.id === agent.id ? 'rgba(255,255,255,0.8)' : theme.colors.textSecondary }
            ]}>
              {agent.credits_per_message}cr
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Messages */}
      <ScrollView 
        ref={scrollViewRef}
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}
      >
        {messages.map((message, idx) => (
          <View 
            key={idx} 
            style={[
              styles.messageBubble,
              message.role === 'user' 
                ? [styles.userMessage, { backgroundColor: theme.colors.primary }]
                : [styles.assistantMessage, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]
            ]}
          >
            <Text style={[
              styles.messageText,
              { color: message.role === 'user' ? '#FFFFFF' : theme.colors.text }
            ]}>
              {message.content}
            </Text>
            {message.creditsUsed && (
              <Text style={styles.creditsUsed}>-{message.creditsUsed} crédito(s)</Text>
            )}
          </View>
        ))}
        {isLoading && (
          <View style={[styles.assistantMessage, styles.messageBubble, { backgroundColor: theme.colors.surface }]}>
            <ActivityIndicator size="small" color={theme.colors.primary} />
            <Text style={[styles.loadingText, { color: theme.colors.textSecondary }]}>Pensando...</Text>
          </View>
        )}
      </ScrollView>

      {/* Input */}
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <View style={[styles.inputContainer, { backgroundColor: theme.colors.surface, borderTopColor: theme.colors.border }]}>
          <TextInput
            style={[styles.input, { backgroundColor: theme.colors.background, color: theme.colors.text }]}
            placeholder="Escribe tu mensaje..."
            placeholderTextColor={theme.colors.textSecondary}
            value={inputMessage}
            onChangeText={setInputMessage}
            multiline
            maxLength={1000}
          />
          <TouchableOpacity
            style={[styles.sendButton, { backgroundColor: theme.colors.primary, opacity: inputMessage.trim() ? 1 : 0.5 }]}
            onPress={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
          >
            <Ionicons name="send" size={20} color="#FFFFFF" />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  agentIconHeader: {
    width: 40,
    height: 40,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  headerTitle: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  headerSubtitle: {
    fontSize: 12,
  },
  creditsBox: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  creditsText: {
    marginLeft: 4,
    fontWeight: 'bold',
    color: '#D97706',
  },
  agentSelector: {
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  agentChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 24,
    marginRight: 8,
    borderWidth: 1,
  },
  agentChipText: {
    marginLeft: 8,
    fontWeight: '600',
  },
  agentCredits: {
    marginLeft: 4,
    fontSize: 12,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
  },
  messageBubble: {
    maxWidth: '85%',
    padding: 14,
    borderRadius: 18,
    marginBottom: 12,
  },
  userMessage: {
    alignSelf: 'flex-end',
    borderBottomRightRadius: 4,
  },
  assistantMessage: {
    alignSelf: 'flex-start',
    borderBottomLeftRadius: 4,
    borderWidth: 1,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 22,
  },
  creditsUsed: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.7)',
    marginTop: 6,
    textAlign: 'right',
  },
  loadingText: {
    marginLeft: 8,
    fontSize: 14,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 12,
    borderTopWidth: 1,
  },
  input: {
    flex: 1,
    minHeight: 44,
    maxHeight: 100,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 22,
    fontSize: 15,
    marginRight: 8,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default AITutorScreen;
