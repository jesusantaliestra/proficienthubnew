import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Bot, Send, Mic, MicOff, Volume2, VolumeX, Loader2,
  MessageSquare, ChevronLeft, Settings, Play, Pause,
  BookOpen, Lightbulb, Target, CheckCircle, GraduationCap,
  Trophy, Calendar, Coins, History, Plus, Sparkles
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Agent icons mapping
const AgentIcons = {
  official_tutor: GraduationCap,
  mock_coach: Trophy,
  planner: Calendar
};

export default function AITutorMultiAgent() {
  const navigate = useNavigate();
  const { examType = 'ielts' } = useParams();
  const { user } = useAuth();
  
  // Agent state
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [credits, setCredits] = useState({ remaining_credits: 0, total_credits: 0 });
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  
  // Voice state
  const [voiceMode, setVoiceMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState('nova');
  
  // Mock Coach state
  const [mockCoachSession, setMockCoachSession] = useState(null);
  const [currentAttempt, setCurrentAttempt] = useState(0);
  
  // Sessions history
  const [sessions, setSessions] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);

  const examInfo = {
    toefl: { name: 'TOEFL', color: 'bg-blue-500' },
    ielts: { name: 'IELTS', color: 'bg-red-500' },
    cambridge: { name: 'Cambridge', color: 'bg-purple-500' },
    trinity: { name: 'Trinity', color: 'bg-pink-500' },
    toeic: { name: 'TOEIC', color: 'bg-indigo-500' },
    celpip: { name: 'CELPIP', color: 'bg-cyan-500' },
    pte: { name: 'PTE', color: 'bg-orange-500' },
    oet: { name: 'OET', color: 'bg-green-500' }
  };

  useEffect(() => {
    fetchAgents();
    fetchCredits();
    fetchSessions();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchAgents = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/ai-agents/available`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAgents(response.data.agents || []);
      // Select first agent by default
      if (response.data.agents?.length > 0 && !selectedAgent) {
        selectAgent(response.data.agents[0]);
      }
    } catch (error) {
      console.error('Error fetching agents:', error);
      toast.error('Error al cargar los agentes');
    }
  };

  const fetchCredits = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/ai-agents/credits`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCredits(response.data);
    } catch (error) {
      console.error('Error fetching credits:', error);
    }
  };

  const fetchSessions = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/ai-agents/sessions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  };

  const selectAgent = (agent) => {
    setSelectedAgent(agent);
    setSessionId(null);
    setMessages([{
      role: 'assistant',
      content: getWelcomeMessage(agent),
      timestamp: new Date()
    }]);
    setMockCoachSession(null);
    setCurrentAttempt(0);
  };

  const getWelcomeMessage = (agent) => {
    const agentMessages = {
      official_tutor: `¡Hola! Soy tu **${agent.name_es}** para ${examInfo[examType]?.name || 'tu examen'}. 

Puedo ayudarte con:
• **Estrategias de examen** - Tips para cada sección
• **Práctica guiada** - Feedback instantáneo
• **Gramática y vocabulario** - Explicaciones claras
• **Preparación de Speaking** - Activa el modo voz

¿En qué puedo ayudarte hoy?`,
      
      mock_coach: `¡Bienvenido al entrenamiento! Soy tu **${agent.name_es}**.

Mi método es especial:
• Te daré preguntas de práctica reales
• Tienes **5 intentos** por pregunta
• Te daré pistas después de cada intento incorrecto
• Solo revelo la respuesta después del 5º intento

¿Listo para practicar? Escribe "empezar" para comenzar con una pregunta.`,
      
      planner: `¡Hola! Soy tu **${agent.name_es}** personal.

Voy a crear un plan de estudio personalizado para ti. Necesito saber:
• ¿Cuándo es tu examen?
• ¿Cuántas horas puedes estudiar por día/semana?
• ¿Cuáles son tus áreas más débiles?
• ¿Cuál es tu nivel actual?

Cuéntame sobre tu situación y crearemos juntos el plan perfecto.`
    };
    
    return agentMessages[agent.id] || `¡Hola! Soy ${agent.name_es}. ¿En qué puedo ayudarte?`;
  };

  const sendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim() || isLoading || !selectedAgent) return;

    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');
      
      // Check for Mock Coach special commands
      if (selectedAgent.id === 'mock_coach' && 
          (messageText.toLowerCase() === 'empezar' || messageText.toLowerCase() === 'start')) {
        await startMockQuestion();
        setIsLoading(false);
        return;
      }
      
      // Check answer for Mock Coach
      if (selectedAgent.id === 'mock_coach' && mockCoachSession) {
        await checkMockAnswer(messageText);
        setIsLoading(false);
        return;
      }
      
      // Regular agent interaction
      const response = await axios.post(
        `${API_URL}/ai-agents/interact`,
        {
          agent_type: selectedAgent.id,
          message: messageText,
          exam_type: examType,
          session_id: sessionId,
          voice_enabled: voiceMode && selectedAgent.voice_enabled,
          voice_id: selectedVoice,
          context: mockCoachSession ? { attempt_count: currentAttempt } : null
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (!response.data.success) {
        if (response.data.error === 'insufficient_credits') {
          toast.error('Sin créditos suficientes');
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: '❌ **Sin créditos suficientes**\n\nNecesitas más créditos para continuar usando el tutor IA. Contacta a tu institución o compra más créditos.',
            timestamp: new Date(),
            error: true
          }]);
          setIsLoading(false);
          return;
        }
      }

      // Update session ID
      if (response.data.session_id && !sessionId) {
        setSessionId(response.data.session_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        audio: response.data.audio_base64,
        timestamp: new Date(),
        creditsUsed: response.data.credits_consumed
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Update credits
      fetchCredits();

      // Auto-play audio if available
      if (response.data.audio_base64) {
        playAudio(response.data.audio_base64);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Error al comunicarse con el tutor');
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Estoy teniendo problemas de conexión. Por favor, intenta de nuevo.',
        timestamp: new Date(),
        error: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const startMockQuestion = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/ai-agents/mock-coach/start-question?exam_type=${examType}&section=reading`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setMockCoachSession(response.data.session_id);
      setCurrentAttempt(0);

      const questionMessage = {
        role: 'assistant',
        content: `📝 **Nueva Pregunta de Práctica**

${response.data.passage ? `**Pasaje:**\n${response.data.passage}\n\n` : ''}**Pregunta:**
${response.data.question}

Tienes **${response.data.max_attempts} intentos**. ¡Buena suerte! 🍀`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, questionMessage]);

    } catch (error) {
      console.error('Error starting mock question:', error);
      toast.error('Error al cargar la pregunta');
    }
  };

  const checkMockAnswer = async (answer) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/ai-agents/mock-coach/check-answer?session_id=${mockCoachSession}&answer=${encodeURIComponent(answer)}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setCurrentAttempt(prev => prev + 1);

      let responseContent = '';

      if (response.data.correct) {
        responseContent = `✅ **¡CORRECTO!** 🎉

${response.data.message}

Has usado ${response.data.attempts_used} intento(s).

Escribe "empezar" para otra pregunta.`;
        setMockCoachSession(null);
        setCurrentAttempt(0);
      } else if (response.data.max_attempts_reached) {
        responseContent = `❌ **Intentos agotados**

${response.data.explanation}

**Respuesta correcta:** ${response.data.correct_answer}

Escribe "empezar" para otra pregunta.`;
        setMockCoachSession(null);
        setCurrentAttempt(0);
      } else {
        responseContent = `❌ **Intento ${5 - response.data.attempts_remaining}/5 incorrecto**

💡 **Pista:** ${response.data.hint}

Te quedan **${response.data.attempts_remaining} intentos**. ¡Sigue intentando!`;
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: responseContent,
        timestamp: new Date()
      }]);

    } catch (error) {
      console.error('Error checking answer:', error);
      toast.error('Error al verificar la respuesta');
    }
  };

  const playAudio = (base64Audio) => {
    try {
      const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);
      audioRef.current = audio;
      audio.onplay = () => setIsPlaying(true);
      audio.onended = () => setIsPlaying(false);
      audio.play();
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(track => track.stop());
        await transcribeAndSend(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      toast.error('No se pudo acceder al micrófono');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAndSend = async (audioBlob) => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'voice_message.webm');
      
      const response = await axios.post(
        `${API_URL}/voice/speech-to-text`,
        formData,
        { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' } }
      );

      if (response.data.text) {
        await sendMessage(response.data.text);
      } else {
        toast.error('No se pudo transcribir el audio');
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error transcribing:', error);
      toast.error('Error al procesar el mensaje de voz');
      setIsLoading(false);
    }
  };

  const loadSession = async (session) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/ai-agents/history/${session._id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Find and select the agent
      const agent = agents.find(a => a.id === session.agent_type);
      if (agent) {
        setSelectedAgent(agent);
      }

      setSessionId(session._id);
      
      // Convert history to messages
      const historyMessages = response.data.history.map(h => ([
        { role: 'user', content: h.user_message, timestamp: new Date(h.created_at) },
        { role: 'assistant', content: h.agent_response, timestamp: new Date(h.created_at) }
      ])).flat();

      setMessages(historyMessages);
      setShowHistory(false);

    } catch (error) {
      console.error('Error loading session:', error);
      toast.error('Error al cargar la sesión');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Left Sidebar - Agent Selection */}
      <aside className="w-80 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
              <ChevronLeft className="w-4 h-4 mr-1" />
              Volver
            </Button>
            <Badge className={`${examInfo[examType]?.color} text-white`}>
              {examInfo[examType]?.name}
            </Badge>
          </div>
          
          {/* Credits Display */}
          <Card className="bg-gradient-to-r from-amber-50 to-yellow-50 border-amber-200">
            <CardContent className="p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Coins className="w-5 h-5 text-amber-600" />
                  <span className="font-semibold text-amber-800">Créditos IA</span>
                </div>
                <span className="text-xl font-bold text-amber-600">
                  {credits.remaining_credits}
                </span>
              </div>
              <Progress 
                value={(credits.remaining_credits / Math.max(credits.total_credits, 1)) * 100} 
                className="mt-2 h-2"
              />
            </CardContent>
          </Card>
        </div>

        {/* Agent Selection */}
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="text-sm font-semibold text-gray-500 mb-3">AGENTES DISPONIBLES</h3>
          <div className="space-y-2">
            {agents.map((agent) => {
              const IconComponent = AgentIcons[agent.id] || Bot;
              const isSelected = selectedAgent?.id === agent.id;
              
              return (
                <button
                  key={agent.id}
                  onClick={() => selectAgent(agent)}
                  className={`w-full p-3 rounded-xl text-left transition-all ${
                    isSelected 
                      ? 'bg-[#58CC02] text-white shadow-lg' 
                      : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                  }`}
                  data-testid={`agent-select-${agent.id}`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      isSelected ? 'bg-white/20' : 'bg-white'
                    }`}>
                      <IconComponent className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-[#58CC02]'}`} />
                    </div>
                    <div>
                      <div className="font-semibold">{agent.name_es}</div>
                      <div className={`text-xs ${isSelected ? 'text-white/80' : 'text-gray-500'}`}>
                        {agent.credits_per_message} crédito{agent.credits_per_message > 1 ? 's' : ''}/mensaje
                      </div>
                    </div>
                  </div>
                  {agent.voice_enabled && (
                    <div className="mt-2 flex items-center gap-1 text-xs">
                      <Volume2 className="w-3 h-3" />
                      <span>Voz disponible</span>
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Session History */}
          <div className="mt-6">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="flex items-center gap-2 text-sm font-semibold text-gray-500 mb-3 hover:text-gray-700"
            >
              <History className="w-4 h-4" />
              HISTORIAL DE SESIONES
            </button>
            
            {showHistory && (
              <div className="space-y-2">
                {sessions.slice(0, 5).map((session, idx) => (
                  <button
                    key={idx}
                    onClick={() => loadSession(session)}
                    className="w-full p-2 rounded-lg bg-gray-50 hover:bg-gray-100 text-left text-sm"
                  >
                    <div className="flex items-center gap-2">
                      <span>{session.agent_icon}</span>
                      <span className="font-medium truncate">{session.first_message?.slice(0, 30)}...</span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {session.message_count} mensajes
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* New Chat Button */}
        <div className="p-4 border-t border-gray-200">
          <Button 
            className="w-full bg-[#58CC02] hover:bg-[#46A302]"
            onClick={() => selectedAgent && selectAgent(selectedAgent)}
          >
            <Plus className="w-4 h-4 mr-2" />
            Nueva Conversación
          </Button>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col">
        {/* Chat Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {selectedAgent && (
                <>
                  <div className="w-10 h-10 rounded-xl bg-[#58CC02] flex items-center justify-center">
                    {React.createElement(AgentIcons[selectedAgent.id] || Bot, { 
                      className: "w-5 h-5 text-white" 
                    })}
                  </div>
                  <div>
                    <h1 className="font-bold text-gray-900">{selectedAgent.name_es}</h1>
                    <p className="text-xs text-gray-500">{selectedAgent.description}</p>
                  </div>
                </>
              )}
            </div>

            {/* Voice Controls */}
            {selectedAgent?.voice_enabled && (
              <div className="flex items-center gap-3">
                <Button
                  variant={voiceMode ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setVoiceMode(!voiceMode)}
                  className={voiceMode ? 'bg-[#58CC02] hover:bg-[#46A302]' : ''}
                  data-testid="voice-toggle"
                >
                  {voiceMode ? <Volume2 className="w-4 h-4 mr-2" /> : <VolumeX className="w-4 h-4 mr-2" />}
                  {voiceMode ? 'Voz On' : 'Voz Off'}
                </Button>

                {voiceMode && (
                  <select
                    value={selectedVoice}
                    onChange={(e) => setSelectedVoice(e.target.value)}
                    className="text-sm border rounded-lg px-2 py-1"
                  >
                    <option value="nova">Nova (Femenina)</option>
                    <option value="echo">Echo (Masculina)</option>
                    <option value="alloy">Alloy (Neutral)</option>
                    <option value="fable">Fable (Expresiva)</option>
                  </select>
                )}
              </div>
            )}
          </div>

          {/* Mock Coach Progress */}
          {selectedAgent?.id === 'mock_coach' && mockCoachSession && (
            <div className="mt-3 p-3 bg-amber-50 rounded-lg">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-amber-800">Pregunta en progreso</span>
                <span className="text-amber-600">Intento {currentAttempt}/5</span>
              </div>
              <Progress value={(currentAttempt / 5) * 100} className="mt-2 h-2" />
            </div>
          )}
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-[#58CC02] text-white'
                      : message.error
                        ? 'bg-red-100 text-red-800'
                        : 'bg-white border border-gray-200 text-gray-800'
                  }`}
                >
                  <div className="prose prose-sm max-w-none whitespace-pre-wrap">
                    {message.content.split('\n').map((line, i) => (
                      <p key={i} className="mb-1 last:mb-0">
                        {line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                          .split(/(<strong>.*?<\/strong>)/)
                          .map((part, j) => 
                            part.startsWith('<strong>') 
                              ? <strong key={j}>{part.replace(/<\/?strong>/g, '')}</strong>
                              : part
                          )}
                      </p>
                    ))}
                  </div>
                  
                  {/* Audio playback */}
                  {message.audio && message.role === 'assistant' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="mt-2 text-gray-500"
                      onClick={() => isPlaying ? stopAudio() : playAudio(message.audio)}
                    >
                      {isPlaying ? <Pause className="w-4 h-4 mr-1" /> : <Play className="w-4 h-4 mr-1" />}
                      {isPlaying ? 'Detener' : 'Reproducir Audio'}
                    </Button>
                  )}

                  {/* Credits indicator */}
                  {message.creditsUsed && message.role === 'assistant' && (
                    <div className="mt-2 text-xs text-gray-400 flex items-center gap-1">
                      <Coins className="w-3 h-3" />
                      {message.creditsUsed} crédito{message.creditsUsed > 1 ? 's' : ''} usado{message.creditsUsed > 1 ? 's' : ''}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
                  <div className="flex items-center gap-2 text-gray-500">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Pensando...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Quick Actions for each agent */}
        {messages.length <= 2 && selectedAgent && (
          <div className="px-6 pb-4">
            <div className="max-w-3xl mx-auto">
              <p className="text-sm text-gray-500 mb-3">Acciones rápidas:</p>
              <div className="flex flex-wrap gap-2">
                {selectedAgent.id === 'official_tutor' && (
                  <>
                    <QuickButton onClick={() => sendMessage("¿Cuál es la mejor estrategia para el reading?")} label="Reading Tips" icon={BookOpen} />
                    <QuickButton onClick={() => sendMessage("Dame una pregunta de práctica de writing")} label="Writing Practice" icon={Target} />
                    <QuickButton onClick={() => sendMessage("¿Cómo puedo mejorar mi speaking?")} label="Speaking Help" icon={Mic} />
                  </>
                )}
                {selectedAgent.id === 'mock_coach' && (
                  <>
                    <QuickButton onClick={() => sendMessage("empezar")} label="Empezar Práctica" icon={Play} />
                  </>
                )}
                {selectedAgent.id === 'planner' && (
                  <>
                    <QuickButton onClick={() => sendMessage("Mi examen es en 2 meses, tengo 2 horas diarias para estudiar")} label="Plan 2 meses" icon={Calendar} />
                    <QuickButton onClick={() => sendMessage("Necesito un plan intensivo de 2 semanas")} label="Plan intensivo" icon={Sparkles} />
                  </>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="max-w-3xl mx-auto flex items-center gap-3">
            {voiceMode && selectedAgent?.voice_enabled && (
              <Button
                variant={isRecording ? 'destructive' : 'outline'}
                size="icon"
                className={isRecording ? 'animate-pulse' : ''}
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isLoading}
                data-testid="record-button"
              >
                {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </Button>
            )}
            
            <Input
              placeholder={isRecording ? "Grabando..." : "Escribe tu mensaje..."}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              disabled={isLoading || isRecording}
              className="flex-1"
              data-testid="message-input"
            />
            
            <Button
              className="bg-[#58CC02] hover:bg-[#46A302]"
              onClick={() => sendMessage()}
              disabled={!inputMessage.trim() || isLoading}
              data-testid="send-button"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          
          {isRecording && (
            <p className="text-center text-sm text-red-500 mt-2 animate-pulse">
              🎤 Grabando... Click en el micrófono para detener
            </p>
          )}
        </div>
      </main>
    </div>
  );
}

// Quick action button component
function QuickButton({ onClick, label, icon: Icon }) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-full text-sm hover:border-[#58CC02] hover:bg-green-50 transition-all"
    >
      <Icon className="w-4 h-4 text-[#58CC02]" />
      {label}
    </button>
  );
}
